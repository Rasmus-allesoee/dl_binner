"""No-data-download tests for acquisition, preservation, progress and real DAGs.

Native mapper execution remains a UCloud check. The pinned Snakemake engine runs
a complete tiny fixture DAG to test rule wiring and extended benchmark capture.
"""

import contextlib
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import e001_multisample as multi
import e001_preprocess as prep


class MultiSampleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def item(self, data=b"archive"):
        return {"url": "https://example.invalid/archive", "etag": '"fixture"',
                "bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "sample": 1}

    def response(self, data, size=None, etag='"fixture"'):
        response = io.BytesIO(data)
        response.status = 200
        response.headers = {"Content-Length": str(len(data) if size is None else size), "ETag": etag}
        return response

    def test_download_checksums_and_no_overwrite(self):
        dest = self.root / "source.tar.gz"
        with patch.object(multi.urllib.request, "urlopen", return_value=self.response(b"archive")):
            record = multi.download(self.item(), dest)
        self.assertEqual(record["sha256"], hashlib.sha256(b"archive").hexdigest())
        self.assertTrue(record["publisher_md5_verified"])
        with self.assertRaisesRegex(ValueError, "destination exists"):
            multi.download(self.item(), dest)

    def test_download_failures_preserve_partial(self):
        for name, data, message in (("truncated", b"ar", "Truncated"), ("digest", b"wrong!!", "MD5"), ("oversize", b"archive!", "byte count")):
            with self.subTest(name=name):
                dest = self.root / (name + ".tar.gz")
                with patch.object(multi.urllib.request, "urlopen", return_value=self.response(data, size=7)):
                    with self.assertRaisesRegex(ValueError, message):
                        multi.download(self.item(), dest)
                self.assertFalse(dest.exists())
                self.assertTrue(dest.with_suffix(".gz.partial").exists())

    def test_changed_headers_stop_before_payload(self):
        dest = self.root / "source.tar.gz"
        with patch.object(multi.urllib.request, "urlopen", return_value=self.response(b"archive", etag='"changed"')):
            with self.assertRaisesRegex(ValueError, "ETag"):
                multi.download(self.item(), dest)
        self.assertFalse(list(self.root.glob("*.partial")))

    def test_general_extraction_full_stream_and_sample_identity(self):
        member = "2017.12.04_18.45.54_sample_9/reads/anonymous_reads.fq"
        data = "".join(f"@S9R{i}/{m}\n{'A'*150}\n+\n{'I'*150}\n" for i in range(3) for m in (1, 2)).encode()
        archive = self.root / "reads.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            info = tarfile.TarInfo(member)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        result = prep.extract(archive, self.root / "reads.fq", None, member, sample=9)
        self.assertEqual(result["pairs"], 3)
        with self.assertRaisesRegex(ValueError, "different sample"):
            prep.extract(archive, self.root / "wrong.fq", None, member, sample=1)
        with self.assertRaisesRegex(ValueError, "resource bound"):
            prep.extract(archive, self.root / "limited.fq", None, member, max_pairs=2)

    def test_live_progress_preserves_native_logs(self):
        folder = self.root / "sample_1/logs"
        folder.mkdir(parents=True)
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture), multi.progress(self.root, interval=0.01, heartbeat=0.02):
            (folder / "map.log").write_text("START mapping\n")
            time.sleep(0.05)
        self.assertIn("START mapping", capture.getvalue())
        self.assertIn("RUNNING", capture.getvalue())
        self.assertEqual((folder / "map.log").read_text(), "START mapping\n")
        self.assertIn("START mapping", (self.root / "progress.log").read_text())

    def test_no_implicit_acquisition_or_small_allocation(self):
        with self.assertRaisesRegex(ValueError, "Explicit"):
            multi.run(self.root, self.root, 4, 12, False)
        with self.assertRaisesRegex(ValueError, "3 vCPU"):
            multi.run(self.root, self.root, 2, 6, True)
        self.assertFalse(list(self.root.glob("multisample-*")))

    def test_total_and_sample_resource_limits_are_separate(self):
        plan = multi.resource_plan(8, 24, 4, 10, 2)
        self.assertEqual(plan["sample_vcpus"], 4)
        self.assertEqual(plan["memory_budget_mb"], 23000)
        for args in ((4, 24, 4, 10, 2), (8, 20, 4, 10, 2), (8, 24, 4, 10, 3)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                multi.resource_plan(*args)

    def test_failed_prerequisite_packages_evidence(self):
        with patch.object(multi.shutil, "disk_usage", return_value=SimpleNamespace(free=0)), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(multi.run(self.root, self.root, 4, 12, True), 1)
        archive = next(self.root.glob("*-return.tar.gz"))
        with tarfile.open(archive) as tar:
            self.assertTrue(any(m.name.endswith("failure.json") for m in tar))
        self.assertTrue(Path(str(archive) + ".sha256").exists())

    def make_executable(self, path, body):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env python3\n" + body)
        path.chmod(0o755)
        return path

    def test_mapping_version_probes_are_ordered_and_recorded(self):
        mapping = self.root / "envs/mapping/bin/python"
        mapping.parent.mkdir(parents=True)
        self.make_executable(mapping.parent / "strobealign", "import sys; print('strobealign 0.17.0'); print('native note', file=sys.stderr)\n")
        self.make_executable(mapping.parent / "samtools", "print('samtools 1.24')\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            versions = multi.verify_mapping_versions(mapping, dict(os.environ), self.root)
        self.assertEqual(versions, {"strobealign": "0.17.0", "samtools": "1.24"})
        labels = ("strobealign-version", "samtools-version")
        for label in labels:
            record = json.loads((self.root / (label + ".command.json")).read_text())
            self.assertEqual(record["returncode"], 0)
            self.assertEqual(record["timeout_seconds"], 30)
            self.assertTrue((self.root / (label + ".stdout")).is_file())
            self.assertTrue((self.root / (label + ".stderr")).is_file())
        self.assertIn("native note", (self.root / "strobealign-version.stderr").read_text())
        events = [line for line in output.getvalue().splitlines() if line.startswith(("START:", "PASS:"))]
        self.assertEqual(events, [event for label in labels for event in ("START: " + label, "PASS: " + label)])

    def test_snakemake_version_comes_from_recorded_workflow_lock(self):
        inventory = self.root / "workflow-lock.stdout"
        inventory.write_text("pip==25.1.1\nsnakemake==9.13.7\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(multi.verify_snakemake_version(self.root), "9.13.7")
        self.assertIn("PASS: snakemake-version (9.13.7, from workflow-lock)", output.getvalue())
        inventory.write_text("snakemake==9.14.0\n")
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors), self.assertRaisesRegex(ValueError, "snakemake==9.13.7"):
            multi.verify_snakemake_version(self.root)
        self.assertIn("FAIL: snakemake-version", errors.getvalue())

    def test_failed_version_probe_records_return_code_and_stops_order(self):
        mapping = self.root / "envs/mapping/bin/python"
        mapping.parent.mkdir(parents=True)
        self.make_executable(mapping.parent / "strobealign", "import sys; print('broken version'); print('probe failed', file=sys.stderr); sys.exit(7)\n")
        self.make_executable(mapping.parent / "samtools", "print('samtools 1.24')\n")
        errors = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors), \
             self.assertRaisesRegex(RuntimeError, "strobealign-version failed with return code 7"):
            multi.verify_mapping_versions(mapping, dict(os.environ), self.root)
        record = json.loads((self.root / "strobealign-version.command.json").read_text())
        self.assertEqual(record["returncode"], 7)
        self.assertIn("probe failed", (self.root / "strobealign-version.stderr").read_text())
        self.assertIn("FAIL: strobealign-version", errors.getvalue())
        self.assertFalse((self.root / "samtools-version.command.json").exists())

    def test_changed_version_is_reported_and_stops_order(self):
        mapping = self.root / "envs/mapping/bin/python"
        mapping.parent.mkdir(parents=True)
        self.make_executable(mapping.parent / "strobealign", "print('strobealign 0.18.0')\n")
        self.make_executable(mapping.parent / "samtools", "print('samtools 1.24')\n")
        errors = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors), \
             self.assertRaisesRegex(ValueError, "expected '0.17.0', observed '0.18.0'"):
            multi.verify_mapping_versions(mapping, dict(os.environ), self.root)
        self.assertIn("FAIL: strobealign-version", errors.getvalue())
        self.assertFalse((self.root / "samtools-version.command.json").exists())

    def test_hung_version_probe_times_out_kills_and_records(self):
        mapping = self.root / "envs/mapping/bin/python"
        mapping.parent.mkdir(parents=True)
        self.make_executable(mapping.parent / "strobealign", "import sys,time; print('starting', flush=True); print('still working', file=sys.stderr, flush=True); time.sleep(10)\n")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()), \
             self.assertRaisesRegex(subprocess.TimeoutExpired, "strobealign-version"):
            multi.verify_mapping_versions(mapping, dict(os.environ), self.root, timeout_seconds=1.5)
        record = json.loads((self.root / "strobealign-version.command.json").read_text())
        self.assertTrue(record["timed_out"])
        self.assertLess(record["returncode"], 0)
        self.assertEqual(record["timeout_seconds"], 1.5)
        self.assertIn("starting", (self.root / "strobealign-version.stdout").read_text())
        self.assertIn("still working", (self.root / "strobealign-version.stderr").read_text())
        self.assertFalse((self.root / "samtools-version.command.json").exists())

    def test_complete_driver_order_seeds_and_repeat_preservation(self):
        (self.root / "SOURCE_COMMIT").write_text("a"*40)
        (self.root / "envs/workflow/bin").mkdir(parents=True)
        calls = []
        original_sha = multi.sha
        def fake_invoke(args, env, stage, label, limit):
            calls.append((label, args, limit))
            versions = {"strobealign-version": "strobealign 0.17.0\n",
                        "samtools-version": "samtools 1.24\n", "snakemake-startup": "9.13.7\n"}
            if label in versions:
                (stage / (label + ".stdout")).write_text(versions[label])
            elif label == "workflow-lock":
                (stage / "workflow-lock.stdout").write_text("snakemake==9.13.7\n")
        with patch.object(multi, "CODE", self.root), \
             patch.object(multi, "accepted_sample0", return_value={"sample": 0}), \
             patch.object(multi, "sha", side_effect=lambda p: "14870c27bc9467b5897bd1b65b347d7d5e2733d8bbe48c0085cb708194966fe1" if Path(p).name == "canonical.fna" else original_sha(p)), \
             patch.object(multi.shutil, "disk_usage", return_value=SimpleNamespace(free=400*10**9)), \
             patch.object(multi, "invoke", side_effect=fake_invoke), \
             patch.object(multi, "aggregate") as aggregate, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(multi.run(self.root, self.root, 4, 12, True), 0)
            self.assertEqual(multi.run(self.root, self.root, 8, 24, True, 4, 10, 2), 0)
        self.assertEqual([c[0] for c in calls], ["mapping-environment", "strobealign-version", "samtools-version",
                                                  "workflow-lock", "snakemake-startup", "dag", "workflow"]*2)
        self.assertEqual([c[2] for c in calls if c[0].endswith("-version")], [30]*4)
        self.assertIn("--benchmark-extended", calls[-1][1])
        cfg = aggregate.call_args.args[0]
        self.assertEqual(cfg["samples"], [1, 2, 3, 4, 5, 9, 10, 11, 12])
        nine = json.loads(Path(cfg["sample_configs"]["9"]).read_text())
        self.assertEqual(nine["sample_index"], 6)
        self.assertEqual(nine["vcpus"], 4)
        self.assertEqual(cfg["vcpus"], 8)
        self.assertEqual(cfg["max_concurrent_samples"], 2)
        self.assertEqual(len(list(self.root.glob("*-return.tar.gz"))), 2)

    def test_packaging_failure_cannot_report_success(self):
        output = io.StringIO()
        with patch.object(multi.shutil, "disk_usage", return_value=SimpleNamespace(free=0)), \
             patch.object(multi.tarfile, "open", side_effect=OSError("fixture packaging error")), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(multi.run(self.root, self.root, 4, 12, True), 1)
        self.assertNotIn("RETURN:", output.getvalue())
        record = json.loads(next(self.root.glob("multisample-*/status.json")).read_text())
        self.assertTrue(record["packaging_failed"])
        self.assertEqual(record["exit_code"], 1)

    def test_snapshot_inventory_gate_and_local_interpreter(self):
        (self.root / "SOURCE_COMMIT").write_text("a" * 40)
        original_sha = multi.sha
        expected = json.loads((multi.EXPERIMENT / "sample0-preprocess-observed.json").read_text())["member_sha256"]["workflow-lock.stdout"]
        prefix = self.root / "local-workflow"
        for matched in (False, True):
            calls = []
            def digest(path):
                if Path(path).name == "workflow-lock.stdout":
                    return expected if matched else "wrong"
                if Path(path).name == "canonical.fna":
                    return "14870c27bc9467b5897bd1b65b347d7d5e2733d8bbe48c0085cb708194966fe1"
                return original_sha(path)
            with patch.object(multi, "CODE", self.root), \
                 patch.object(multi, "accepted_sample0", return_value={"sample": 0}), \
                 patch.object(multi, "stage_runtime", return_value=prefix), \
                 patch.object(multi, "verify_mapping_versions"), patch.object(multi, "workflow_preflight"), \
                 patch.object(multi, "sha", side_effect=digest), \
                 patch.object(multi, "invoke", side_effect=lambda a, e, s, label, limit: calls.append((label, a))), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                result = multi.run(self.root, self.root, 4, 12, False,
                                   startup_only=True, workflow_snapshot=self.root / "snapshot.tar.gz")
            self.assertEqual(result, 0 if matched else 1)
            self.assertEqual("dag" in [label for label, argv in calls], matched)
            for label, argv in calls:
                if label in ("workflow-prefix", "dag"):
                    self.assertEqual(argv[0], prefix / "bin/python")

    def test_startup_only_never_acquires_or_aggregates(self):
        (self.root / "SOURCE_COMMIT").write_text("a" * 40)
        calls = []
        original_sha = multi.sha
        with patch.object(multi, "CODE", self.root), \
             patch.object(multi, "accepted_sample0", return_value={"sample": 0}), \
             patch.object(multi, "sha", side_effect=lambda p: "14870c27bc9467b5897bd1b65b347d7d5e2733d8bbe48c0085cb708194966fe1" if Path(p).name == "canonical.fna" else original_sha(p)), \
             patch.object(multi, "verify_mapping_versions"), patch.object(multi, "workflow_preflight"), \
             patch.object(multi, "invoke", side_effect=lambda a, e, s, label, limit: calls.append(label)), \
             patch.object(multi, "aggregate") as aggregate, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(multi.run(self.root, self.root, 4, 12, False, startup_only=True), 0)
        self.assertEqual(calls, ["mapping-environment", "dag"])
        aggregate.assert_not_called()
        self.assertTrue(json.loads(next(self.root.glob("multisample-*/status.json")).read_text())["startup_only"])

    def test_accepted_sample0_reuse_and_changed_record_rejected(self):
        folder = self.root / "sample0-accepted"
        folder.mkdir()
        records = {"runtime.json": {"stage": str(folder)}, "status.json": {"exit_code": 0},
                   "reads.json": {"pairs": 5}, "preprocessing-summary.json": {"sample": 0},
                   "C0/qc.json": {"bytes": 7}, "CT/qc.json": {"bytes": 7}}
        for name, record in records.items():
            p = folder / name
            p.parent.mkdir(exist_ok=True)
            p.write_text(json.dumps(record))
        for condition in ("C0", "CT"):
            (folder / condition / "mapped.bam").write_bytes(b"fixture")
            (folder / condition / "mapped.bam.bai").touch()
        self.assertEqual(multi.accepted_sample0(self.root, {"records": records})["sample"], 0)
        (folder / "C0/qc.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "record changed"):
            multi.accepted_sample0(self.root, {"records": records})

    def test_shared_worker_uses_sample_readgroup_and_ordered_seed(self):
        from e001lib import native, smoke
        reference = self.root / "ref.fna"
        reference.write_text(">fixture\nAAAA\n")
        cfg = self.root / "runtime.json"
        cfg.write_text(json.dumps({"stage": str(self.root), "root": str(self.root), "sample": 9, "sample_index": 6,
            "reference": str(reference), "reference_sha256": multi.sha(reference), "vcpus": 4}))
        commands = []
        def pipeline(argv, out):
            commands.extend(argv)
            (self.root / "C0/mapped.bam").write_bytes(b"full")
        def invoke(argv, env, out, label, timeout):
            if label == "thin":
                commands.append(argv)
                (self.root / "CT/mapped.bam").write_bytes(b"thin")
        with patch.object(native, "pipeline", side_effect=pipeline), \
             patch.object(prep, "invoke", side_effect=invoke), \
             patch.object(prep.subprocess, "check_output", side_effect=lambda argv, **kw: "strobealign 0.17.0" if argv[0] == "strobealign" else "samtools 1.24"), \
             patch.object(smoke, "bam_inventory", side_effect=[{"records": 100}, {"records": 10}]), \
             patch.dict(prep.os.environ), contextlib.redirect_stdout(io.StringIO()):
            prep.worker("map", cfg)
            prep.worker("thin", cfg)
        self.assertIn("E001-sample9", commands[0])
        self.assertEqual(commands[-1][commands[-1].index("--subsample-seed") + 1], "1006")
        self.assertEqual(json.loads((self.root / "preprocessing-summary.json").read_text())["sample"], 9)

    def test_aggregate_preserves_order_and_rejects_wrong_seed(self):
        folder = self.root / "sample_9"
        folder.mkdir()
        path = folder / "runtime.json"
        path.write_text(json.dumps({"stage": str(folder), "sample_index": 6}))
        summary = {"sample": 9, "thinning_seed": 1006, "C0": {"records": 10}, "CT": {"records": 1}}
        (folder / "preprocessing-summary.json").write_text(json.dumps(summary))
        (folder / "reads.json").write_text(json.dumps({"pairs": 5}))
        config = {"sample0": {"sample": 0}, "samples": [9], "sample_configs": {"9": str(path)},
                  "stage": str(self.root), "source_commit": "a"*40, "reference": "reference", "reference_sha256": "a"*64}
        multi.aggregate(config)
        self.assertEqual([s["sample"] for s in json.loads((self.root / "bam-manifest.json").read_text())["samples"]], [0, 9])
        summary["thinning_seed"] = 1009
        (folder / "preprocessing-summary.json").write_text(json.dumps(summary))
        with self.assertRaisesRegex(ValueError, "seed"):
            multi.aggregate(config)

    def test_real_snakemake_execution_and_extended_benchmarks(self):
        executable = Path(os.environ.get("E001_TEST_SNAKEMAKE", str(REPO / "artifacts/e001-snakemake-test-env/bin/snakemake")))
        if not executable.exists():
            self.skipTest("Pinned workflow environment unavailable")
        helper = self.root / "fixture_worker.py"
        # Test real engine wiring without native tools, internet or research data.
        helper.write_text('''import argparse,json,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--config');p.add_argument('--sample');a=p.parse_args()
c=json.loads(Path(a.config).read_text()); d=Path(c['stage'])/('sample_'+a.sample);d.mkdir(exist_ok=True)
start=time.time()
if c.get('max_concurrent_samples',1)>1:time.sleep(1.5 if a.worker=='map' else 0.1)
names={'download':['source.tar.gz','acquisition.json'],'extract':['reads.fq','reads.json'],'map':['C0/mapped.bam','C0/mapped.bam.bai','C0/qc.json'],'thin':['CT/mapped.bam','CT/mapped.bam.bai','CT/qc.json','preprocessing-summary.json']}[a.worker]
with (Path(c['stage'])/'order.txt').open('a') as f:f.write(a.sample+':'+a.worker+'\\n')
for name in names:
 out=d/name;out.parent.mkdir(exist_ok=True);out.write_text('fixture')
(d/(a.worker+'-events.json')).write_text(json.dumps({'start':start,'end':time.time(),'sample':a.sample,'mode':a.worker}))
print('completed',a.sample,a.worker)
''')
        reference = self.root / "ref.fna"
        reference.write_text(">fixture\nACGT\n")
        runtime = self.root / "runtime.json"
        runtime.write_text(json.dumps({"stage": str(self.root), "samples": [1, 9], "reference": str(reference), "vcpus": 4,
            "mapping_python": sys.executable, "helper": str(helper), "runtime_config": str(runtime)}))
        command = [str(executable), "--snakefile", str(REPO / "workflows/e001-preprocess/multisample.smk"),
                   "--directory", str(self.root), "--configfile", str(runtime), "--cores", "4", "--executor", "local", "--benchmark-extended"]
        command = [str(a) for a in multi.workflow_command(executable, "snakemake", command[1:], 0)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / "order.txt").read_text().splitlines(),
                         [f"{s}:{m}" for s in (1, 9) for m in ("download", "extract", "map", "thin")])
        benches = list(self.root.glob("sample_*/benchmarks/*.tsv"))
        self.assertEqual(len(benches), 8)
        with benches[0].open() as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(rows), 1)
        self.assertTrue({"s", "max_rss", "rule_name", "cpu_time", "threads"}.issubset(rows[0]))
        second = subprocess.run(command, capture_output=True, text=True, timeout=120)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("Nothing to be done", second.stdout + second.stderr)

        parallel = self.root / "parallel"
        parallel.mkdir()
        runtime = parallel / "runtime.json"
        runtime.write_text(json.dumps({"stage": str(parallel), "samples": [1, 2, 3, 4, 5, 9],
            "reference": str(reference), "vcpus": 8, "sample_vcpus": 4, "sample_ram_gb": 10,
            "max_concurrent_samples": 2, "mapping_python": sys.executable, "helper": str(helper), "runtime_config": str(runtime)}))
        command = [str(executable), "--snakefile", str(REPO / "workflows/e001-preprocess/multisample.smk"),
                   "--directory", str(parallel), "--configfile", str(runtime), "--cores", "8", "--executor", "local",
                   "--resources", "mem_mb=23000", "download_slots=1", "--benchmark-extended"]
        command = [str(a) for a in multi.workflow_command(executable, "snakemake", command[1:], 0)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        events = [json.loads(p.read_text()) for p in parallel.glob("sample_*/*-events.json")]
        def peak(mode):
            points = sorted((e[k], delta) for e in events if e["mode"] == mode
                            for k, delta in (("start", 1), ("end", -1)))
            active = maximum = 0
            for _, delta in points:
                active += delta
                maximum = max(maximum, active)
            return maximum
        self.assertEqual(peak("download"), 1)
        self.assertEqual(peak("map"), 2)
        for prior, following in ((1, 3), (2, 4), (3, 5), (4, 9)):
            finish = next(e["end"] for e in events if e["sample"] == str(prior) and e["mode"] == "thin")
            start = next(e["start"] for e in events if e["sample"] == str(following) and e["mode"] == "download")
            self.assertGreaterEqual(start, finish)
        with (parallel / "sample_9/benchmarks/map.tsv").open() as handle:
            row = next(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(int(row["threads"]), 4)


if __name__ == "__main__":
    unittest.main()
