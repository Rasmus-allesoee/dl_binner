"""Secondary sequence-truth bin summaries; never used by grouping or selection.

Completeness is a duplicate-safe provided-reference union, not marker breadth.
Impurity includes unconfirmed DNA, so in conservative truth it is an upper
bound on contamination rather than a measured contaminant fraction. No RNA
screening, MIMAG HQ certification, near-complete tier or primary-rule change.
"""
from collections import Counter, defaultdict
import math


def union_bp(intervals):
    """Return bp in half-open interval unions, refusing malformed coordinates."""
    total = 0; end = -1
    for a, b in sorted(intervals):
        if type(a) is not int or type(b) is not int or not 0 <= a < b:
            raise ValueError('Malformed secondary reference interval')
        total += max(0, b-max(a, end)); end = max(end, b)
    return total


def quality_tier(completeness, impurity):
    """Use exclusive secondary numerical tiers, with explicit strict HQ edges."""
    if any(type(v) not in (int,float) or not math.isfinite(v) or not 0 <= v <= 1 for v in (completeness,impurity)):
        raise ValueError('Invalid secondary quality fraction')
    if completeness > .90 and impurity < .05: return 'threshold_based_HQ'
    if completeness >= .50 and impurity < .10: return 'threshold_based_MQ'
    if completeness < .50 and impurity < .10: return 'threshold_based_LQ'
    return 'high_impurity_or_unresolved'


def summarize(rows, assignments, references, genome_lengths, targets):
    """Stream admitted query support into all-bin sequence quality diagnostics.

    Rows use length, id, confirmed_query_bp and source_intervals. All assigned
    DNA enters bin purity. Non-target dominant origins remain reported and
    separate from target tier counts. All supplied genome denominators must
    match full reference lengths. Unknown support is never silently excluded.
    """
    expected = Counter()
    for ref in references.values(): expected[ref['genome']] += ref['length']
    if any(expected[g] != n or n <= 0 for g, n in genome_lengths.items()) or not set(targets) <= set(genome_lengths):
        raise ValueError('Secondary full-reference denominator differs')
    sizes = Counter(); support = defaultdict(Counter); loci = defaultdict(list); seen = set()
    for r in rows:
        q = r['id']; n = r['length']
        if q in seen or q not in assignments or type(n) is not int or n < 0:
            raise ValueError('Secondary complete query axis differs')
        seen.add(q); counts = r['confirmed_query_bp']
        if any(g not in expected or type(v) is not int or v < 0 for g, v in counts.items()) or sum(counts.values()) > n:
            raise ValueError('Secondary support exceeds query or unknown genome')
        for ref, spans in r['source_intervals'].items():
            if ref not in references or any(b > references[ref]['length'] for a, b in spans):
                raise ValueError('Secondary reference coordinate escaped')
            union_bp(spans)
        b = assignments[q]
        if b is None: continue
        if not isinstance(b, (str, int)) or isinstance(b, bool) or (isinstance(b, int) and b < 0):
            raise ValueError('Secondary malformed bin label')
        sizes[b] += n; support[b].update(counts)
        for ref, spans in r['source_intervals'].items(): loci[b, ref].extend(spans)
    if seen != set(assignments): raise ValueError('Secondary extra/missing query')
    recovered = defaultdict(Counter)
    for (b, ref), spans in loci.items(): recovered[b][references[ref]['genome']] += union_bp(spans)
    result = []; counts = Counter(); large_counts = Counter()
    for b in sorted(sizes, key=str):
        n = sizes[b]; candidates = support[b]
        dominant = min(candidates, key=lambda g: (-candidates[g], g)) if candidates else None
        own = candidates[dominant] if dominant is not None else 0
        denominator = expected.get(dominant)
        complete = recovered[b][dominant]/denominator if denominator else None
        if complete is not None and not 0 <= complete <= 1:
            raise ValueError('Secondary reference union exceeds denominator')
        purity = own/n if n else 0.; impurity = 1-purity
        tier = quality_tier(complete, impurity) if complete is not None else 'high_impurity_or_unresolved'
        is_target = dominant in targets
        counts[tier] += 1
        if n >= 200000: large_counts[tier] += 1
        result.append(dict(bin_id=b, bp=n, dominant_origin=dominant, target=is_target,
            full_reference_bp=denominator, source_union_bp=recovered[b][dominant] if dominant else 0,
            completeness=complete, confirmed_purity=purity, impurity_upper_bound=impurity,
            confirmed_other_origin_bp=sum(candidates.values())-own,
            confirmed_other_origin_fraction=(sum(candidates.values())-own)/n if n else 0.,
            unconfirmed_bp=n-sum(candidates.values()), unresolved_fraction=(n-sum(candidates.values()))/n if n else 0., tier=tier))
    target_counts = Counter(x['tier'] for x in result if x['target'])
    return dict(bins=result, counts=dict(counts), target_counts=dict(target_counts),
        at_least_200kb_counts=dict(large_counts), assigned_bp=sum(sizes.values()),
        query_count=len(seen), primary_rule_changed=False, rRNA_tRNA_screened=False,
        numerical_units='fractions in [0,1], not percentages',
        label='Secondary sequence-truth threshold-based tiers, not formal MIMAG HQ',
        semantics='full-reference union completeness; 1-confirmed/all-bin purity includes unresolved DNA and is a contamination upper bound; origin oracle is not uniqueness',
        thresholds='HQ completeness>90%, impurity<5%; else MQ completeness>=50%, impurity<10%; else LQ completeness<50%, impurity<10%; else unresolved/high impurity')
