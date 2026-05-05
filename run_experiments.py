"""
Misty Moon Treasure Hunt - Experiment Runner
4 algorithms (DFS/BFS/A*/GA) x 3 densities x 4 guard counts x 30 reps
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from scipy.stats import f_oneway, ttest_ind
from itertools import product
import os, time

from game import Game

ALGORITHMS = ["DFS", "BFS", "A*", "GA"]
WALL_DENSITIES = [0.15, 0.25, 0.35]
GUARD_COUNTS = [0, 2, 4, 6]
REPETITIONS = 30
MAX_STEPS = 500
OUTPUT_DIR = "results"

def run_all():
    results = []
    conditions = list(product(ALGORITHMS, WALL_DENSITIES, GUARD_COUNTS))
    total = len(conditions) * REPETITIONS
    done = 0
    print(f"Running {total} experiments ({len(conditions)} conditions x {REPETITIONS} reps)")
    print("=" * 70)
    for algo, wd, gc in conditions:
        print(f"  {algo:4s} | walls={wd:.0%} | guards={gc} ...", end=" ", flush=True)
        t0 = time.time()
        for rep in range(REPETITIONS):
            seed = rep * 1000 + int(wd * 100) + gc
            g = Game(algo, wd, gc, seed=seed, visual=False, max_steps=MAX_STEPS)
            m = g.run_headless()
            m["wall_density"] = wd
            m["num_guards"] = gc
            m["repetition"] = rep
            results.append(m)
            done += 1
        print(f"done ({time.time()-t0:.1f}s)")
    print(f"\nAll {done} experiments completed.")
    return pd.DataFrame(results)

def analyze(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, "raw_results.csv"), index=False)

    summary = df.groupby(["algorithm", "wall_density", "num_guards"]).agg(
        path_mean=("path_length", "mean"), path_std=("path_length", "std"),
        nodes_mean=("nodes_explored", "mean"), nodes_std=("nodes_explored", "std"),
        time_mean=("compute_time", "mean"),
        replan_mean=("replan_count", "mean"),
        pred_replan_mean=("predictive_replans", "mean"),
        evade_mean=("evade_count", "mean"),
        success=("found_treasure", "mean"),
    ).reset_index()
    summary.to_csv(os.path.join(OUTPUT_DIR, "summary_stats.csv"), index=False)
    print("\n" + summary.to_string())

    colors = ['#4FC3F7', '#81C784', '#FFB74D', '#CE93D8']

    # Box plots
    for metric, ylabel, title in [
        ("path_length", "Path Length", "Path Length by Algorithm"),
        ("nodes_explored", "Nodes Explored", "Search Efficiency by Algorithm"),
        ("replan_count", "Replan Count", "Replanning Frequency"),
        ("evade_count", "Evade Count", "Emergency Evades by Algorithm"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 5))
        data = [df[df["algorithm"] == a][metric] for a in ALGORITHMS]
        bp = ax.boxplot(data, labels=ALGORITHMS, patch_artist=True,
                        medianprops=dict(color='red', linewidth=2))
        for patch, c in zip(bp['boxes'], colors):
            patch.set_facecolor(c)
        ax.set_ylabel(ylabel); ax.set_title(title); ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"boxplot_{metric}.png"), dpi=150)
        plt.close()

    # Success rate grouped bar
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(GUARD_COUNTS)); bw = 0.2
    for i, algo in enumerate(ALGORITHMS):
        rates = [df[(df["algorithm"] == algo) & (df["num_guards"] == gc)]["found_treasure"].mean()
                 for gc in GUARD_COUNTS]
        ax.bar(x + i * bw, rates, bw, label=algo, color=colors[i])
    ax.set_xlabel("Number of Guards"); ax.set_ylabel("Success Rate")
    ax.set_title("Success Rate by Algorithm and Guard Count")
    ax.set_xticks(x + bw * 1.5); ax.set_xticklabels(GUARD_COUNTS)
    ax.legend(); ax.set_ylim(0, 1.05); ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "success_rate.png"), dpi=150)
    plt.close()

    # Path length vs wall density
    fig, ax = plt.subplots(figsize=(9, 5))
    ok = df[df["found_treasure"] == True]
    for algo, c in zip(ALGORITHMS, colors):
        means = [ok[(ok["algorithm"] == algo) & (ok["wall_density"] == wd)]["path_length"].mean()
                 for wd in WALL_DENSITIES]
        stds = [ok[(ok["algorithm"] == algo) & (ok["wall_density"] == wd)]["path_length"].std()
                for wd in WALL_DENSITIES]
        ax.errorbar(WALL_DENSITIES, means, yerr=stds, marker='o', label=algo, color=c, capsize=5, lw=2)
    ax.set_xlabel("Wall Density"); ax.set_ylabel("Path Length")
    ax.set_title("Path Length vs Wall Density (successful runs)"); ax.legend(); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "path_vs_density.png"), dpi=150)
    plt.close()

    # Heatmap: predictive replans
    fig, ax = plt.subplots(figsize=(9, 5))
    hm = np.zeros((len(ALGORITHMS), len(GUARD_COUNTS)))
    for i, a in enumerate(ALGORITHMS):
        for j, gc in enumerate(GUARD_COUNTS):
            hm[i][j] = df[(df["algorithm"] == a) & (df["num_guards"] == gc)]["predictive_replans"].mean()
    im = ax.imshow(hm, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(len(GUARD_COUNTS))); ax.set_xticklabels(GUARD_COUNTS)
    ax.set_yticks(range(len(ALGORITHMS))); ax.set_yticklabels(ALGORITHMS)
    ax.set_xlabel("Guards"); ax.set_ylabel("Algorithm"); ax.set_title("Avg Predictive Replans")
    for i in range(len(ALGORITHMS)):
        for j in range(len(GUARD_COUNTS)):
            ax.text(j, i, f"{hm[i][j]:.1f}", ha="center", va="center", fontsize=11)
    plt.colorbar(im); plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "heatmap_pred_replan.png"), dpi=150)
    plt.close()

    # Subsumption behavior comparison: evade vs replan stacked bar
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(ALGORITHMS))
    evades = [df[df["algorithm"] == a]["evade_count"].mean() for a in ALGORITHMS]
    replans = [df[df["algorithm"] == a]["replan_count"].mean() for a in ALGORITHMS]
    pred = [df[df["algorithm"] == a]["predictive_replans"].mean() for a in ALGORITHMS]
    ax.bar(x, evades, 0.5, label="Emergency Evades", color='#EF5350')
    ax.bar(x, pred, 0.5, bottom=evades, label="Predictive Replans", color='#FFA726')
    ax.set_xticks(x); ax.set_xticklabels(ALGORITHMS)
    ax.set_ylabel("Count"); ax.set_title("Subsumption Layer Activations by Algorithm")
    ax.legend(); ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "subsumption_activations.png"), dpi=150)
    plt.close()

    # Stats
    print("\n" + "=" * 50 + "\nSTATISTICAL TESTS\n" + "=" * 50)
    if len(ok) > 0:
        groups = [ok[ok["algorithm"] == a]["path_length"] for a in ALGORITHMS]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) >= 2:
            f, p = f_oneway(*groups)
            print(f"\nANOVA path_length: F={f:.4f}, p={p:.6f} {'***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'}")
    print("\nPairwise t-tests (path_length):")
    for i in range(len(ALGORITHMS)):
        for j in range(i + 1, len(ALGORITHMS)):
            a1 = ok[ok["algorithm"] == ALGORITHMS[i]]["path_length"]
            a2 = ok[ok["algorithm"] == ALGORITHMS[j]]["path_length"]
            if len(a1) > 1 and len(a2) > 1:
                t, p = ttest_ind(a1, a2)
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
                print(f"  {ALGORITHMS[i]:4s} vs {ALGORITHMS[j]:4s}: t={t:8.3f} p={p:.6f} {sig}")
    print(f"\nAll figures saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    print("=" * 70)
    print("  MISTY MOON TREASURE HUNT - EXPERIMENT RUNNER")
    print("  4 Algorithms | Predictive Replanning | Subsumption Architecture")
    print("=" * 70)
    df = run_all()
    analyze(df)
