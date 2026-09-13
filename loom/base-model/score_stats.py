#!/usr/bin/env python
"""Significance testing for the graded simulacrum self-awareness sweep.

Reads a scores JSON of the form {"persona": [0,1,0,3,...], ...} where each
value is a 0-3 rating from CLASSIFIER.md amendment 2, and reports whether
persona identity explains any variance.

  ./score_stats.py scores.json
"""
import json
import sys
from collections import Counter

import numpy as np
from scipy import stats

scores = json.load(open(sys.argv[1]))
personas = list(scores)

print(f"{'persona':10} {'n':>4} {'mean':>6} {'0':>4} {'1':>4} {'2':>4} {'3':>4} {'>=2':>6}")
print("-" * 52)
groups = []
aware = []
for p in personas:
    v = scores[p]
    groups.append(v)
    c = Counter(v)
    n = len(v)
    ge2 = sum(1 for x in v if x >= 2)
    aware.append((ge2, n - ge2))
    print(f"{p:10} {n:>4} {np.mean(v):>6.2f} "
          f"{c[0]:>4} {c[1]:>4} {c[2]:>4} {c[3]:>4} {ge2:>3}/{n}")

print()
H, p_kw = stats.kruskal(*groups)
print(f"Kruskal-Wallis across {len(personas)} personas: H = {H:.3f}, p = {p_kw:.3f}")

table = np.array(aware).T
if table.min() < 5:
    _, p_fis = stats.fisher_exact(table[:, :2]) if table.shape[1] == 2 else (None, None)
    chi2, p_chi, _, _ = stats.chi2_contingency(table)
    print(f"Rate of self-awareness (score >= 2), chi-square: "
          f"chi2 = {chi2:.3f}, p = {p_chi:.3f}  (low cell counts; treat as approximate)")
else:
    chi2, p_chi, _, _ = stats.chi2_contingency(table)
    print(f"Rate of self-awareness (score >= 2), chi-square: chi2 = {chi2:.3f}, p = {p_chi:.3f}")

allv = [x for v in scores.values() for x in v]
n_all = len(allv)
n3 = sum(1 for x in allv if x == 3)
n2 = sum(1 for x in allv if x >= 2)
print()
print(f"Pooled: n = {n_all}, mean = {np.mean(allv):.2f}")
print(f"  hypostasis (3):        {n3}/{n_all} = {100*n3/n_all:.1f}%")
print(f"  self-aware (>=2):      {n2}/{n_all} = {100*n2/n_all:.1f}%")
lo, hi = stats.binomtest(n2, n_all).proportion_ci(confidence_level=0.95)
print(f"  95% CI on >=2 rate:    [{100*lo:.1f}%, {100*hi:.1f}%]")

if "_eerie_baseline" in scores:
    pass
print()
print("Comparison against the eerie-seed baseline (Arago, n=20, 18 of 20 at >=2):")
tbl = np.array([[n2, n_all - n2], [18, 2]])
odds, p_b = stats.fisher_exact(tbl)
print(f"  neutral pooled vs eerie: Fisher exact p = {p_b:.3e}")
