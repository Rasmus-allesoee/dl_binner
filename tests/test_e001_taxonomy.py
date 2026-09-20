"""Historical taxonomy validation and complete owner-driver integration."""

import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import unittest

import test_e001_resume as resume_fixture
from test_e001_resume import sha
from e001lib.records import ContractError, domains_from_nodes
from e001lib.taxonomy import prepare


class TaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.fixture = resume_fixture.ResumeTests()
        self.fixture.setUp()
        self.root, self.code = self.fixture.root, self.fixture.code
        self.archive = self.root / "taxonomy.tar.gz"
        nodes = b"1\t|\t1\t|\tno rank\t|\n2\t|\t1\t|\tsuperkingdom\t|\n"
        with tarfile.open(self.archive, "w:gz") as archive:
            member = tarfile.TarInfo("nodes.dmp")
            member.size = len(nodes)
            archive.addfile(member, io.BytesIO(nodes))
        self.mapping = self.root / "inventory/per_bodysite/gastro_bam/gsa_pooled_mapping_fixed.tsv"
        self.policy = self.code / "experiments/E001-coverage-thinning/taxonomy-policy.json"
        self.policy.write_text(json.dumps({
            "archive_sha256": sha(self.archive), "mapping_sha256": sha(self.mapping),
            "members": {"nodes.dmp": {"size": len(nodes), "sha256": hashlib.sha256(nodes).hexdigest()}},
            "taxid_count": 1, "genome_domains": {"bacteria": 1},
            "invariant_outputs": {}, "expected_population": {"eligible_genomes": 1}}))
        cfg_path = self.code / "experiments/E001-coverage-thinning/config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg.update(min_genome_bp=2000, min_genomes=1, min_short_queries=0, min_short_query_genomes=0)
        cfg_path.write_text(json.dumps(cfg))

    def tearDown(self):
        self.fixture.tearDown()

    def execute(self):
        import subprocess
        return subprocess.run([sys.executable, "-I", str(self.code / "scripts/e001_inventory_resume.py"),
                               str(self.root), "--convert", "--taxonomy", str(self.archive)],
                              capture_output=True, text=True)

    def test_taxonomy_driver_repeated_and_input_invariance(self):
        first = self.execute()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        report = json.loads(next(self.root.glob("inventory-resume-*/input/inventory.json")).read_text())
        self.assertEqual(report["status"], "validated")
        policy = json.loads(self.policy.read_text())
        policy["invariant_outputs"] = {n: report["outputs"][n] for n in ("canonical.fna", "truth.tsv")}
        self.policy.write_text(json.dumps(policy))
        second = self.execute()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        for path in self.root.glob("*-return.tar.gz"):
            with tarfile.open(path) as archive:
                self.assertTrue(any(n.endswith("taxonomy/coverage.json") for n in archive.getnames()))
                self.assertFalse(any(n.endswith("nodes.dmp") for n in archive.getnames()))
        policy["invariant_outputs"]["canonical.fna"] = "0" * 64
        self.policy.write_text(json.dumps(policy))
        failed = self.execute()
        self.assertEqual(failed.returncode, 1)
        self.assertIn("Taxonomy changed input", failed.stderr)

    def test_bad_archive_packaged_without_conversion(self):
        with self.archive.open("ab") as handle:
            handle.write(b"changed")
        result = self.execute()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Taxonomy archive checksum mismatch", result.stderr)
        self.assertFalse(list(self.root.glob("inventory-resume-*/input")))
        self.assertEqual(len(list(self.root.glob("*-return.tar.gz"))), 1)

    def test_wrong_member_and_missing_member_fail(self):
        policy = json.loads(self.policy.read_text())
        policy["members"]["nodes.dmp"]["sha256"] = "0" * 64
        self.policy.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ContractError, "member checksum"):
            prepare(self.archive, self.policy, self.mapping, self.root / "wrong")
        policy["members"]["nodes.dmp"]["sha256"] = hashlib.sha256(
            (self.root / "wrong/nodes.dmp").read_bytes()).hexdigest()
        policy["members"]["missing"] = {"size": 0, "sha256": "0" * 64}
        self.policy.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ContractError, "Missing taxonomy member"):
            prepare(self.archive, self.policy, self.mapping, self.root / "missing")

    def test_unknown_cycle_duplicate_and_missing_root(self):
        path = self.root / "nodes.dmp"
        path.write_text("1|1|no rank|\n3|4|species|\n4|3|species|\n5|2|species|\n")
        self.assertEqual(domains_from_nodes(["3", "5", "2", "99"], path),
                         {"3": "unknown", "5": "unknown", "2": "unknown", "99": "unknown"})
        with path.open("a") as handle:
            handle.write("3|1|species|\n")
        with self.assertRaisesRegex(ContractError, "duplicate taxonomy"):
            domains_from_nodes(["3"], path)

    def test_mapping_and_coverage_mismatch(self):
        policy = json.loads(self.policy.read_text())
        policy["mapping_sha256"] = "0" * 64
        self.policy.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ContractError, "mapping checksum"):
            prepare(self.archive, self.policy, self.mapping, self.root / "bad-mapping")
        self.assertFalse((self.root / "bad-mapping").exists())
        policy["mapping_sha256"] = sha(self.mapping)
        policy["genome_domains"] = {"archaea": 1}
        self.policy.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ContractError, "coverage differs"):
            prepare(self.archive, self.policy, self.mapping, self.root / "bad-coverage")

    def test_duplicate_members_rejected(self):
        with tarfile.open(self.archive, "w:gz") as archive:
            for _ in range(2):
                member = tarfile.TarInfo("nodes.dmp")
                member.size = 0
                archive.addfile(member, io.BytesIO(b""))
        policy = json.loads(self.policy.read_text())
        policy["archive_sha256"] = sha(self.archive)
        policy["members"]["nodes.dmp"] = {"size": 0, "sha256": hashlib.sha256(b"").hexdigest()}
        self.policy.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ContractError, "duplicate taxonomy member"):
            prepare(self.archive, self.policy, self.mapping, self.root / "duplicate")


if __name__ == "__main__":
    unittest.main()
