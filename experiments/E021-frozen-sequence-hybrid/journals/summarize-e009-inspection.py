#!/usr/bin/env python3
"""Summarize verified E021 E009 receipts; never fit, infer or rescore a baseline.

Run from the repository root after scripts/e021_review.py succeeds. Inputs are
the retained October 25 inspection and E019's accepted target table. Outputs are
compact maintained comparison/inspection records and a complete 156-target table.
Prices are refreshed Catalog rates, not an invoice. Raw evidence stays ignored.
"""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path


REPO = Path.cwd()
EXP = REPO / "experiments/E021-frozen-sequence-hybrid"
BASE = REPO / "artifacts/e021-portable-admission/20261024T183844Z"
R = BASE / "inspection-20261025T1320Z"


def read(path):
    """Read an existing JSON receipt without changing its provenance."""
    return json.loads(path.read_text())


def binding(path):
    """Bind a retained file by repository-relative locator, byte count and SHA256."""
    return dict(path=str(path.relative_to(REPO)), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, value):
    """Write only a derived maintained summary, never an input receipt."""
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def transitions(left, right):
    """Compare already evaluated exact recovered bp on identical full denominators."""
    assert left.keys() == right.keys()
    changes = [right[k] - left[k] for k in left]
    return dict(gained=sum(x > 0 for x in changes), lost=sum(x < 0 for x in changes),
                unchanged=sum(x == 0 for x in changes), delta_bp=sum(changes))


def main():
    """Require completion/reader/watcher proofs and summarize the admitted new review."""
    review_path = R / "local-review-attempt2/diagnostics-E009-hybrid/review.json"
    review = read(review_path)
    baseline_path = REPO / "experiments/E019-window-context/comparison-review.json"
    full_baseline = read(baseline_path)
    baseline = full_baseline["units"]["E009-context"]
    complete = read(R / "recovery-completion.json")
    proof = read(R / "native-preservation-proof.json")
    target = read(R / "local-review/verified/evidence/gates/E009-scoped-target.json")
    assert review["status"] == "SUCCESS"
    assert complete["status"] == "SUCCESS_E009_ONLY_COMPLETE"
    assert complete["scoped_science_completed"] and not complete["science_completed"]
    assert complete["scientific_fits_completed"] == 1 and not complete["oral_executed"]
    assert len(complete["stages"]) == 10
    assert all(s["status"] == "SUCCESS" and s["resources"]["exit_code"] == 0
               for s in complete["stages"])
    assert [s["stage"] for s in complete["stages"] if s["kind"] == "science"] == [
        "train", "embed", "group", "refine", "export", "graph-proof"]
    assert target["status"] == "PASS_E009_ONLY_COMPLETE"
    assert proof["consumer-admission.json"]["consumer_admitted"]
    assert proof["consumer-admission.json"]["old_receivers_unchanged"]
    superv = read(R / "local-review/verified/evidence/logs/supervision.json")
    watcher = read(R / "recovery-watchdog-exit.json")
    assert superv["boot_id"] == watcher["boot_id"]
    assert superv["process"] == watcher["expected_process"] and watcher["shutdown"]
    assert read(R / "final-original-CPU.json")["status"] == "TERMINATED"
    retirement = read(R / "GPU-retirement-verified.json")
    assert not retirement["remaining_instances"] and not retirement["remaining_temporary_disks"]

    table_path = REPO / "experiments/E019-window-context/comparison-targets.tsv"
    with table_path.open() as f:
        previous = {x["genome"]: x for x in csv.DictReader(f, delimiter="\t")
                    if x["dataset"] == "E009_conservative_v2"}
    arms = {a: {x["genome"]: x for x in review["arms"][a]["diagnostics"]["recovery"]}
            for a in ["pre", "old", "post"]}
    assert len(previous) == 156 and all(x.keys() == previous.keys() for x in arms.values())
    rows = []
    for genome, old in previous.items():
        ref = int(old["reference_bp"])
        assert all(a[genome]["reference_bp"] == ref for a in arms.values())
        rows.append(dict(dataset="E009_conservative_v2", genome=genome, reference_bp=ref,
                         **{f"E019_{a}_bp": int(old[f"E019_{a}_bp"]) for a in arms},
                         **{f"E021_{a}_bp": arms[a][genome]["recovered_bp"] for a in arms},
                         delta_vs_E019_post_bp=arms["post"][genome]["recovered_bp"] - int(old["E019_post_bp"])))
    assert sum(x["reference_bp"] for x in rows) == 554661890
    with (EXP / "comparison-targets.tsv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    old_bp = {x["genome"]: x["E019_post_bp"] for x in rows}
    new_bp = {x["genome"]: x["E021_post_bp"] for x in rows}
    delta = transitions(old_bp, new_bp)
    ref_total = sum(x["reference_bp"] for x in rows)
    assert abs(sum(new_bp.values()) / ref_total - review["arms"]["post"]["diagnostics"]["recovery_summary"]["bp_weighted_R95"]) < 1e-15
    summary = dict(
        record="E021 E009-only completed independent review", status="MODIFY_SCOPED_HYBRID",
        reviewed_UTC=dt.datetime.now(dt.timezone.utc).isoformat(),
        scope="One full E009 ten-depth development fit; oral/skin unrun, no baseline fit/rescore",
        scientific_candidate="f136b2c5f6195ae91a0566f23d84c8c6c9f69bf9",
        operational_execution_source=complete["source"],
        source_proof="Execution snapshot matches the original 115 source/input bindings and 43 installed package members. Later documentation edits do not rewrite those locks.",
        evidence=dict(new_review=binding(review_path), baseline=binding(baseline_path),
                      baseline_targets=binding(table_path), protocol=binding(EXP / "protocol.json"),
                      scoped_protocol=binding(EXP / "E009-only-scope.json")),
        full_reference=dict(targets=156, bp=ref_total, N_quarantine_fraction=0.033034),
        arms={}, paired_vs_E019=delta,
        target_gains=sorted([x for x in rows if x["delta_vs_E019_post_bp"] > 0], key=lambda x: -x["delta_vs_E019_post_bp"]),
        target_losses=sorted([x for x in rows if x["delta_vs_E019_post_bp"] < 0], key=lambda x: x["delta_vs_E019_post_bp"]),
        threshold_transitions={str(q): [x for x in rows if
              (x["E019_post_bp"] >= q * x["reference_bp"]) != (x["E021_post_bp"] >= q * x["reference_bp"])] for q in [0.5, 0.9]},
        paired_refinement={f"{a}_to_{b}": transitions(
            {k: v["recovered_bp"] for k, v in arms[a].items()},
            {k: v["recovered_bp"] for k, v in arms[b].items()})
            for a, b in [("pre", "old"), ("old", "post"), ("pre", "post")]},
        preserved_E019_arms={a: baseline["arms"][a]["recovery"] for a in arms},
        raw_learned_geometry={k: v for k, v in review["raw_learned_geometry"].items() if k != "queries"},
        preserved_E019_raw_learned_geometry=baseline["raw_learned_geometry"],
        preserved_E019_post_geometry=baseline["arms"]["post"]["geometry"],
        preserved_E019_post_lineage_geometry=baseline["arms"]["post"]["geometry_by_lineage"],
        preserved_E019_post_B3=baseline["arms"]["post"]["grouping"],
        preserved_context=full_baseline["preserved_context"],
        training={k: v for k, v in review["checkpoint"].items() if k not in ["transform", "history"]},
        geometry_history=review["checkpoint"]["history"],
        native_neighbor_proof={k: v for k, v in review["native_graph_review"]["geometry"].items() if k != "queries"},
        choices=review["choices"], refinement=review["refinement"], token_contract=review["token_contract"],
        portability=review["portability"],
        limitations=[
            "One seed/assembly, E009 ten-depth development evidence only; oral and skin E021 outputs do not exist. Original joint KEEP is unmet.",
            "Complete historical DNABERT-S pretraining inventory is unavailable; no unseen-genome or pretraining-independent claim. This uncertainty is distinct from benchmark labels entering training.",
            "Retained MetaBAT2/dev3 values are rounded native whole-tool context. Eligibility differs; no matched-cutoff or isolated-component claim and no old rescore.",
            "All full-reference denominators and N-quarantined/unsupported/ambiguous/unknown/non-target DNA remain; R95 is not the fraction of genomes recovered or a product-wide quality verdict.",
        ],
        disposition=dict(original_joint_KEEP="UNMET: oral unrun; E009 >=90% count also falls 7 to 6",
                         E009_R95_delta=delta["delta_bp"] / ref_total,
                         practical_gain_threshold_passed=delta["delta_bp"] / ref_total >= 0.005,
                         high_recovery_no_loss_passed=False,
                         original_thresholds_changed=False, scoped="MODIFY; no product-default promotion"),
        interpretation=[
            "Valid bundle gain is concentrated: ASV406.4 contributes 3.112 Mb; net gain is 2.838 Mb over 156 full references. It crosses 90%, but ASV150.14 and ASV300.2 fall below 90%.",
            "Bacterial all-native 5NN improves slightly while bacterial restricted grouping precision/recall fall. Neither whole-pool geometry nor R95 establishes uniform cellular improvement.",
            "E013 selects two split alternatives without changing target recovery. Old destructive refinement scores higher here, but selecting it after truth would violate the frozen policy.",
            "No demonstrated axis/source/view/reader/reload/geometry/graph/export failure explains the mixed outcome. These contracts do not prove biological or algorithmic optimality.",
            "E021 is one seed, one inspected development assembly and a learning bundle. Added branch initialization and training changes prevent an isolated causal GLM claim.",
        ],
        next_decision=dict(
            recommendation="Implement a reliable marker-informed cross-contig learning block locally; prepare one separately priced comparison using retained CPU-readable features/caches, without new GPU extraction.",
            reason="Self-positive crop learning offers no explicit same-genome link between different contigs. Recovery remains fragmented and gains are narrow despite noncollapsed embeddings; audited marker reliability can add a different biological constraint before more model capacity.",
            safety="Repeated family alone is not a cannot-link: preserve E011/E012 locus/panel/replicon/duplication failures, use label-free reliability/context and abstain when insufficient. Truth diagnoses/evaluates only.",
            alternatives="A matched zero-GLM control can isolate attribution but does not directly close recovery; reserve for a design-changing uncertainty. Larger GLM/context models or full oral extraction are not justified by this one mixed gain. More grouping threshold tuning risks the two development communities.",
            scope="Local design/source checks, implementation and tiny engineering only in the next prompt; no community fit, scoring, cloud job, DNA acquisition or retention extension without separate authorization.",
        ),
        confirmation_limits=[
            "Frozen skin choice remains unscored: 610 full targets/one zero origin; 313 inventories exactly match oral-observed genomes. It is not unseen-genome evidence.",
            "Source/genome/replicon/molecule/host/circular taxonomy joins, competitive unique-versus-origin ambiguity/near/pretraining overlap limitations remain explicit. Named provided-origin oracle only, no unique-support claim.",
            "No measured pooled-GSA contig depth or assembly errors; no oral/skin hybrid transfer evidence. Freeze candidate/comparator/protocol and admit evaluator, resources, cost and retention before confirmation; no new acquisition now.",
        ],
    )
    for arm, value in review["arms"].items():
        diag = value["diagnostics"]
        summary["arms"][arm] = dict(recovery=diag["recovery_summary"],
            diagnostics={k: v for k, v in diag.items() if k != "recovery"},
            populations=value["populations"], accounting=review["contracts"][arm],
            bins=len(value["grouping"]["bins"]),
            clean_marker_by_status=value["grouping"]["clean_marker_by_status"])
    assert summary["paired_refinement"]["pre_to_post"]["delta_bp"] == 0
    write(EXP / "comparison-review.json", summary)

    # Fresh Catalog prices are ordinary on-demand; no promotional/free-tier offsets.
    prices = read(R / "current-prices.json")
    def rate(description):
        sku = next(x for x in prices["skus"] if x["description"] == description)
        info = sku["pricingInfo"][-1]
        rates = info["pricingExpression"]["tieredRates"]
        amounts = [int(x["unitPrice"].get("units", 0)) + x["unitPrice"].get("nanos", 0) / 1e9 for x in rates]
        return max(amounts) / info["currencyConversionRate"]
    e2 = 8 * rate("E2 Instance Core running in Americas") + 32 * rate("E2 Instance Ram running in Americas") + rate("External IP Charge on a Standard VM")
    gpu = 8 * rate("G2 Instance Core running in Americas") + 32 * rate("G2 Instance Ram running in Americas") + rate("Nvidia L4 GPU running in Americas") + rate("External IP Charge on a Standard VM")
    pd = rate("Balanced PD Capacity"); std = rate("Storage PD Capacity")
    allowed = read(R / "remaining-original-allowance.json")
    start = read(R / "recovery-start.json")["start_epoch"]
    state = read(R / "final-original-CPU.json")
    stop = dt.datetime.fromisoformat(state["last_stop"]).timestamp()
    recovery_seconds = stop - start
    assert recovery_seconds + allowed["E009_consumer_elapsed_running_seconds"] < 4 * 3600
    retire = read(R / "GPU-retirement-before.json")
    retired_epoch = dt.datetime.fromisoformat(retirement["UTC"]).timestamp()
    temp_cost = sum(int(x["sizeGb"]) * pd / 744 * (retired_epoch - dt.datetime.fromisoformat(x["creationTimestamp"]).timestamp()) / 3600 for x in retire["disks"])
    common = read(BASE / "common-clock.json")
    original_month = 300 * pd + 30 * std
    original_attributed = original_month / 744 * (stop - common["first_VM_start_epoch"]) / 3600
    transports = []
    for path in sorted(BASE.glob("transport-*.json")) + sorted((BASE / "continuation-v6").glob("transport-*.json")):
        d = read(path)
        if "started_epoch" not in d:
            continue
        stream = d.get("stream") or d.get("sender", {}).get("stream")
        assert stream is not None
        transports.append(dict(path=str(path.relative_to(REPO)), status=d["status"], bytes=stream["bytes"]))
    wire = sum(x["bytes"] for x in transports)
    archives = list((BASE / "native-returns").glob("*.tar.gz")) + list(R.glob("*e021-evidence.tar.gz")) + [BASE / "gpu-admission-v3-evidence.tar.gz"]
    exports = sum(p.stat().st_size for p in archives)
    components = dict(GPU_allocation_including_idle_IP=allowed["GPU_running_seconds"] / 3600 * gpu,
                      CPU_allocation_including_recovery_idle_IP=(allowed["CPU_running_seconds"] + recovery_seconds) / 3600 * e2,
                      temporary_disks_through_verified_deletion=temp_cost,
                      original_disks_attribution_overlaps_existing_8_USD_approval=original_attributed,
                      all_transport_wire_conservative_WAN=wire / 1024**3 * .12,
                      all_downloaded_scientific_archives_conservative_WAN=exports / 1024**3 * .12)
    ledger = dict(record="E021 allocation-priced estimate, not an invoice", price_receipt=binding(R / "current-prices.json"),
                  fresh_credit_receipt=binding(R / "financial-gate.json"),
                  Welcome_DKK=1808.22, balance_percent=92, expires="2027-01-12", delayed_usage="unknown, not zero", delayed_reserve_USD=35,
                  credit_only=True, real_money_authorized=False, original_ceiling_USD=45,
                  ordinary_first_party_coverage="Verified live retained-credit paid-upgrade scope; no Marketplace, vWS, commitment or new services",
                  provider_allocation=dict(GPU_seconds=allowed["GPU_running_seconds"], CPU_seconds=allowed["CPU_running_seconds"] + recovery_seconds,
                                           recovery_seconds=recovery_seconds, total_consumer_seconds=allowed["E009_consumer_elapsed_running_seconds"] + recovery_seconds,
                                           common_first_start=common["first_VM_start_epoch"], common_deadline=common["deadline_epoch"]),
                  hourly_USD=dict(E2_8_32_with_IP=e2, G2_8_32_L4_with_IP=gpu),
                  transport_ledgers=transports, total_wire_bytes=wire, charged_export_bytes=exports,
                  components_USD=components, priced_subtotal_USD=sum(components.values()),
                  small_GCS_storage_ops_control_and_unrecorded_minor_network_allowance_USD=.10,
                  additional_unmetered_safety_reserve_USD=1.50,
                  bounded_total_with_reserves_USD=sum(components.values()) + 1.60,
                  recovery_compute_IP_USD=recovery_seconds / 3600 * e2,
                  stopped_original_disks_USD_per_month=original_month,
                  retention="2026-10-28 00:00 Europe/Copenhagen (CET); original $8 interval ~ $7.63, no extension",
                  caveat="All wire is conservatively priced as paid $0.12/GiB outbound, even Mac-origin bytes. No free offsets or credit-delta invoice attribution; Catalog FX used. 744-hour month convention; original-disk attribution is not an additional storage invoice.")
    assert ledger["bounded_total_with_reserves_USD"] < 45
    write(EXP / "cost-review.json", ledger)
    archive = read(R / "recovery-archive-verification.json")
    stage_summaries = [dict(name=s["name"], kind=s["kind"], status=s["status"], **{k:s["resources"][k] for k in ["exit_code", "wall_seconds", "peak_sampled_rss_bytes", "sampled_cpu_seconds"]}) for s in complete["stages"]]
    inspection = dict(record="E021 E009-only verified completion and cleanup", status="COMPLETED_VERIFIED_MODIFY",
        phase="portable-20261024T190419Z", CPU_phase="cpu-E009-recovery-v7", scientific_candidate=summary["scientific_candidate"],
        execution_source=complete["source"], final_CPU=state, GPU_retirement=retirement,
        final_provider_STATE_independent=True, scoped_status=complete["status"], scoped_science_completed=True,
        legacy_two_community_science_completed=False, actual_fits=1, oral_executed=False, skin_executed=False,
        stages=stage_summaries, guard_errors=complete["guard_errors"],
        archive={k:v for k,v in archive.items() if k != "omitted_retained_on_disk"},
        omitted_native_files=len(archive["omitted_retained_on_disk"]),
        omitted_native_bytes=sum(v["bytes"] for v in archive["omitted_retained_on_disk"].values()),
        uploads=complete["return"]["uploads"],
        completion_binding=binding(R / "recovery-completion.json"), watcher_binding=binding(R / "recovery-watchdog-exit.json"),
        consumer_proof_binding=binding(R / "native-preservation-proof.json"),
        watchdog=dict(boot_id=watcher["boot_id"], process=watcher["expected_process"], decision=watcher["decision"], shutdown=watcher["shutdown"], normal_exit_and_crash_tests_passed=True),
        original_failure=dict(status="FAILED_BEFORE_CPU_SCIENCE", cause="Ready task file exposed empty JSON before serialization; deterministic regression reproduces race; later IAP4003 follows CPU shutdown",
                              preserved_old_receivers_pending=True, failure_journals_preserved=True,
                              repair="Exclusive atomic publication, preloaded commands before arm; restored bytes/hardlinks with no recopy/reinstall/extraction/tiny replay"),
        terminal_storage_snapshot=read(R / "local-review/verified/evidence/usage.json"),
        local_review=binding(R / "local-review-attempt2/diagnostics.resources.json"),
        local_review_failed_attempt="First attempt verified archive then sandbox denied ps before diagnostics; retained FAILED receipt. Second used same original one-hour clock and verified extracted bytes, no science replay.",
        retained_bulk="Complete raw GLM bank and inert CUDA runtime archive remain on original CPU work disk; original bank and hardlinked recovery both preserved. Only compact science archive is in GCS/Mac. Omitted arrays/FASTA are not backed up merely by hashes.",
        costs="cost-review.json", comparison="comparison-review.json", full_targets="comparison-targets.tsv",
        evidence_root=str(R.relative_to(REPO)), inspection_backup_record="inspection-backup.json")
    write(EXP / "inspection-observed.json", inspection)
    print(json.dumps(dict(paired=delta, components=components, subtotal=ledger["priced_subtotal_USD"], with_reserves=ledger["bounded_total_with_reserves_USD"], allocation=ledger["provider_allocation"], monthly=original_month), indent=2))


if __name__ == "__main__":
    main()
