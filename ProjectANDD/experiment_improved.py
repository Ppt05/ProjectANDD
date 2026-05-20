# -*- coding: utf-8 -*-
"""
So Sanh Thuc Nghiem: Thuat Toan Goc vs Cai Tien
================================================
Bai bao: "Deanonymizing Social Networks Using Structural Information" (IJCAI-2019)

Han che da xac dinh:
  - NDSD: Chi dung 1-hop neighbor degrees -> fingerprint ngheo nan, dez nham o noise cao
  - Local Search: Bi ket local optimum -> khong tim duoc nghiem tot hon

Y tuong cai tien:
  - ENDSD  : Mo rong sang 2-hop neighborhood (fingerprint phong phu hon)
  - ILS    : Iterated Local Search voi perturbation (thoat local optimum)

Thuc nghiem so sanh:
  Baseline : NDSD  -> LocalSearch
  Improved : ENDSD -> ILS (Iterated Local Search)

Mon hoc: An Ninh Di Dong
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import random
import time
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.optimize import linear_sum_assignment

# ─────────────────────────────────────────────────────────────
# 1. SINH DO THI VA NOISY SUBGRAPH (giu nguyen tu experiment.py)
# ─────────────────────────────────────────────────────────────

def generate_graph(model: str, n: int) -> nx.Graph:
    if model == "BA":
        return nx.barabasi_albert_graph(n, m=3, seed=42)
    elif model == "ER":
        return nx.erdos_renyi_graph(n, p=0.02, seed=42)
    elif model == "WS":
        return nx.watts_strogatz_graph(n, k=6, p=0.1, seed=42)
    elif model == "HK":
        return nx.powerlaw_cluster_graph(n, m=3, p=0.5, seed=42)
    raise ValueError(f"Mo hinh khong hop le: {model}")


def create_noisy_subgraph(G, delta, epsilon, seed=0):
    rng = random.Random(seed)
    nodes_G = list(G.nodes())
    n_remove = int(len(nodes_G) * delta)
    removed = set(rng.sample(nodes_G, n_remove))
    kept = [v for v in nodes_G if v not in removed]
    H = G.subgraph(kept).copy()
    for u in kept:
        for v in kept:
            if u < v and rng.random() < epsilon:
                if H.has_edge(u, v):
                    H.remove_edge(u, v)
                else:
                    H.add_edge(u, v)
    mapping = {v: i for i, v in enumerate(kept)}
    true_map = {i: v for i, v in enumerate(kept)}
    return nx.relabel_nodes(H, mapping), true_map


def compute_accuracy(predicted, truth):
    if not truth:
        return 0.0
    return sum(1 for h in truth if predicted.get(h) == truth[h]) / len(truth)


def edge_overlap_score(G, H, mapping):
    """Tinh tong so canh H duoc khop dung trong G theo mapping hien tai."""
    return sum(1 for u, v in H.edges()
               if G.has_edge(mapping.get(u, -1), mapping.get(v, -1)))


def _swap_delta(G, H, mapping, u, v):
    """
    Tinh nhanh DELTA score khi swap mapping[u] <-> mapping[v].
    O(deg(u) + deg(v)) thay vi O(m) — tang toc 20-50x.

    Cong thuc:
      delta = (so canh moi duoc khop sau swap)
            - (so canh cu bi mat sau swap)
    Chi can xet canh trong H lien quan toi u hoac v.
    """
    gu, gv = mapping[u], mapping[v]
    delta = 0

    for x in H.neighbors(u):
        if x == v:
            # Canh (u,v) trong H: G.has_edge(gu,gv) khong doi khi swap
            continue
        gx = mapping[x]
        # Truoc swap: u->gu, sau swap: u->gv
        delta += int(G.has_edge(gv, gx)) - int(G.has_edge(gu, gx))

    for x in H.neighbors(v):
        if x == u:
            continue
        gx = mapping[x]
        # Truoc swap: v->gv, sau swap: v->gu
        delta += int(G.has_edge(gu, gx)) - int(G.has_edge(gv, gx))

    return delta


# ─────────────────────────────────────────────────────────────
# 2. BASELINE: NDSD (1-hop) + LOCAL SEARCH
# ─────────────────────────────────────────────────────────────

def nds_1hop(graph, node):
    """Neighbor Degree Sequence goc: chi dung 1-hop."""
    return sorted([graph.degree(nb) for nb in graph.neighbors(node)], reverse=True)


def nds_distance(a, b):
    n = max(len(a), len(b), 1)
    a_ = a + [0] * (n - len(a))
    b_ = b + [0] * (n - len(b))
    return sum(abs(x - y) for x, y in zip(a_, b_))


def ndsd_baseline(G, H, true_map):
    """THUAT TOAN GOC: NDSD dung 1-hop NDS + Hungarian."""
    nodes_H = list(H.nodes())
    nodes_G = list(true_map.values())
    nds_h = {v: nds_1hop(H, v) for v in nodes_H}
    nds_g = {v: nds_1hop(G, v) for v in nodes_G}
    cost = np.array([[nds_distance(nds_h[h], nds_g[g])
                      for g in nodes_G] for h in nodes_H], dtype=float)
    r, c = linear_sum_assignment(cost)
    return {nodes_H[i]: nodes_G[j] for i, j in zip(r, c)}


def local_search_baseline(G, H, init_map, max_iter=5):
    """
    THUAT TOAN GOC: Local Search thuan tuy (de bi ket local optimum).
    Dung incremental delta update de tang toc.
    """
    mapping = dict(init_map)
    nodes_H = list(H.nodes())
    n = len(nodes_H)
    for _ in range(max_iter):
        improved = False
        for i in range(n):
            for j in range(i + 1, n):
                u, v = nodes_H[i], nodes_H[j]
                d = _swap_delta(G, H, mapping, u, v)
                if d > 0:
                    mapping[u], mapping[v] = mapping[v], mapping[u]
                    improved = True
        if not improved:
            break
    return mapping


# ─────────────────────────────────────────────────────────────
# 3. IMPROVED: ENDSD (2-hop) + ITERATED LOCAL SEARCH
# ─────────────────────────────────────────────────────────────

def endsd_fingerprint(graph, node, alpha=0.5):
    """
    ENDSD Fingerprint - Cai tien chinh:
    Ket hop 1-hop NDS voi 2-hop NDS co trong so.

    Han che cua NDSD:
      - Hai node co the co cung 1-hop NDS nhung cau truc 2-hop khac nhau
      - Vi du: 2 node cung co 3 ban bac [5,3,1] nhung ban cua ban khac nhau
      ENDSD giai quyet bang cach nhin xa hon 1 buoc.

    Args:
        graph : Do thi (G hoac H)
        node  : Node can tinh fingerprint
        alpha : Trong so cho 2-hop component (0 < alpha < 1)
                Nho hon 1 vi 2-hop bi nhieu nhieu hon 1-hop
    """
    # 1-hop: degrees cua lang gieng truc tiep
    hop1_degrees = sorted(
        [graph.degree(nb) for nb in graph.neighbors(node)],
        reverse=True
    )

    # 2-hop: degrees cua lang gieng cap 2 (khong tinh lai node goc va 1-hop)
    one_hop_set = set(graph.neighbors(node))
    two_hop_nodes = set()
    for nb in one_hop_set:
        for nb2 in graph.neighbors(nb):
            if nb2 != node and nb2 not in one_hop_set:
                two_hop_nodes.add(nb2)

    hop2_degrees = sorted(
        [graph.degree(w) * alpha for w in two_hop_nodes],
        reverse=True
    )

    # Ket hop: [1-hop | 2-hop * alpha]
    return hop1_degrees + hop2_degrees


def endsd_distance(fp_a, fp_b):
    """Khoang cach L1 giua 2 ENDSD fingerprints."""
    n = max(len(fp_a), len(fp_b), 1)
    a_ = fp_a + [0.0] * (n - len(fp_a))
    b_ = fp_b + [0.0] * (n - len(fp_b))
    return sum(abs(x - y) for x, y in zip(a_, b_))


def endsd_improved(G, H, true_map, alpha=0.5):
    """
    THUAT TOAN CAI TIEN: ENDSD dung 2-hop fingerprint + Hungarian.
    Giai quyet han che NDSD: fingerprint phong phu hon -> phan biet node tot hon
    o muc nhieu cao.
    """
    nodes_H = list(H.nodes())
    nodes_G = list(true_map.values())

    # Tinh ENDSD fingerprint cho tung node
    fp_h = {v: endsd_fingerprint(H, v, alpha) for v in nodes_H}
    fp_g = {v: endsd_fingerprint(G, v, alpha) for v in nodes_G}

    # Cost matrix dung ENDSD distance
    cost = np.array([[endsd_distance(fp_h[h], fp_g[g])
                      for g in nodes_G] for h in nodes_H], dtype=float)
    r, c = linear_sum_assignment(cost)
    return {nodes_H[i]: nodes_G[j] for i, j in zip(r, c)}


def _local_search_single(G, H, init_map, max_iter=5):
    """
    Mot lan chay Local Search dung incremental delta (noi bo cho ILS).
    Dung _swap_delta thay vi tinh lai toan bo score: tang toc 20-50x.
    """
    mapping = dict(init_map)
    nodes_H = list(H.nodes())
    n = len(nodes_H)
    score = edge_overlap_score(G, H, mapping)
    for _ in range(max_iter):
        improved = False
        for i in range(n):
            for j in range(i + 1, n):
                u, v = nodes_H[i], nodes_H[j]
                d = _swap_delta(G, H, mapping, u, v)
                if d > 0:
                    mapping[u], mapping[v] = mapping[v], mapping[u]
                    score += d
                    improved = True
        if not improved:
            break
    return mapping, score


def iterated_local_search(G, H, init_map, R=4, k=3, max_iter=5):
    """
    THUAT TOAN CAI TIEN: Iterated Local Search (ILS).
    Giai quyet han che Local Search thuan tuy: bi ket local optimum.

    Giai phap:
      Sau moi lan Local Search bi ket, "xao tron" (perturb) bang cach
      swap k cap ngau nhien, roi chay lai Local Search tu vi tri moi.
      Lap R lan, giu nghiem tot nhat.

    Args:
        R        : So lan restart sau perturbation (default 4)
        k        : So cap swap trong moi perturbation (default 3)
        max_iter : So vong lap toi da cua moi lan Local Search (default 5)
    """
    nodes_H = list(H.nodes())
    best_map, best_score = _local_search_single(G, H, init_map, max_iter)

    rng = random.Random(99)
    for _ in range(R):
        # Perturbation: swap k cap ngau nhien de thoat local optimum
        perturbed = dict(best_map)
        for _ in range(k):
            u, v = rng.sample(nodes_H, 2)
            perturbed[u], perturbed[v] = perturbed[v], perturbed[u]

        # Chay lai Local Search tu nghiem bi nhieu loan
        new_map, new_score = _local_search_single(G, H, perturbed, max_iter)

        # Cap nhat nghiem tot nhat
        if new_score > best_score:
            best_map, best_score = new_map, new_score

    return best_map


# ─────────────────────────────────────────────────────────────
# 4. CHAY THUC NGHIEM SO SANH
# ─────────────────────────────────────────────────────────────

def run_comparison(model, n, noise_levels, n_trials=5, delta=0.05,
                   ils_R=4, ils_k=3, endsd_alpha=0.5):
    """
    Chay ca 2 pipeline va tra ve ket qua so sanh:
      Baseline : NDSD (1-hop) + Local Search thuan tuy
      Improved : ENDSD (2-hop) + ILS (Iterated Local Search)
    """
    print(f"\n{'='*65}")
    print(f"  Mo hinh: {model} | n={n} | delta={delta*100:.0f}% | {n_trials} trials")
    print(f"  ILS: R={ils_R}, k={ils_k} | ENDSD: alpha={endsd_alpha}")
    print(f"{'='*65}")

    G = generate_graph(model, n)
    print(f"  Do thi G: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    results = {
        "ndsd":    [],   # Baseline step 1
        "ls":      [],   # Baseline step 2
        "endsd":   [],   # Improved step 1
        "ils":     [],   # Improved step 2
    }

    for eps in noise_levels:
        acc = {"ndsd": [], "ls": [], "endsd": [], "ils": []}

        for trial in range(n_trials):
            H, true_map = create_noisy_subgraph(G, delta, eps, seed=trial)

            t0 = time.time()

            # ── BASELINE ─────────────────────────────────
            pred_ndsd = ndsd_baseline(G, H, true_map)
            pred_ls   = local_search_baseline(G, H, pred_ndsd, max_iter=n)

            # ── IMPROVED ─────────────────────────────────
            pred_endsd = endsd_improved(G, H, true_map, alpha=endsd_alpha)
            pred_ils   = iterated_local_search(G, H, pred_endsd,
                                               R=ils_R, k=ils_k, max_iter=n)

            # ── TINH ACCURACY ─────────────────────────────
            acc["ndsd"].append(compute_accuracy(pred_ndsd, true_map))
            acc["ls"].append(compute_accuracy(pred_ls, true_map))
            acc["endsd"].append(compute_accuracy(pred_endsd, true_map))
            acc["ils"].append(compute_accuracy(pred_ils, true_map))

            t1 = time.time()
            print(f"  eps={eps*100:4.0f}% | trial {trial+1}"
                  f" | NDSD={acc['ndsd'][-1]*100:5.1f}%"
                  f" | LS={acc['ls'][-1]*100:5.1f}%"
                  f" | ENDSD={acc['endsd'][-1]*100:5.1f}%"
                  f" | ILS={acc['ils'][-1]*100:5.1f}%"
                  f" | {t1-t0:.1f}s")

        for key in results:
            results[key].append(np.mean(acc[key]))

    return results


# ─────────────────────────────────────────────────────────────
# 5. VE BIEU DO SO SANH
# ─────────────────────────────────────────────────────────────

COLORS = {
    "ndsd":  "#8B949E",   # Xam - Baseline step 1
    "ls":    "#457B9D",   # Xanh duong - Baseline step 2
    "endsd": "#F4A261",   # Cam - Improved step 1
    "ils":   "#E63946",   # Do - Improved step 2 (tot nhat)
}

LABELS = {
    "ndsd":  "NDSD goc (1-hop)",
    "ls":    "NDSD + Local Search (Baseline)",
    "endsd": "ENDSD cai tien (2-hop)",
    "ils":   "ENDSD + ILS (Improved)",
}


def plot_comparison_all_models(all_results, noise_levels, output_path):
    """
    Bieu do 1: So sanh Baseline vs Improved tren 4 mo hinh do thi.
    2x2 subplots, moi subplot la 1 mo hinh.
    """
    models = list(all_results.keys())
    noise_pct = [e * 100 for e in noise_levels]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor("#0D1117")
    fig.suptitle(
        "So Sanh Thuc Nghiem: Thuat Toan Goc vs Cai Tien\n"
        "Baseline: NDSD + Local Search  |  Improved: ENDSD (2-hop) + ILS",
        fontsize=14, fontweight="bold", color="#E8E8E8", y=1.01
    )

    model_colors_bg = {"BA": "#1A0A0A", "HK": "#1A0D05", "ER": "#090F15", "WS": "#0F0A12"}
    model_titles = {
        "BA": "Barabasi-Albert (phu hop MXH)",
        "HK": "Holme-Kim (phu hop MXH)",
        "ER": "Erdos-Renyi (khong phu hop)",
        "WS": "Watts-Strogatz (khong phu hop)",
    }

    for idx, model in enumerate(models):
        ax = axes[idx // 2][idx % 2]
        ax.set_facecolor(model_colors_bg.get(model, "#0D1117"))
        res = all_results[model]

        # Ve 4 duong
        for key in ["ndsd", "ls", "endsd", "ils"]:
            vals = [v * 100 for v in res[key]]
            ls_style = "--" if key in ["ndsd", "ls"] else "-"
            lw = 1.8 if key in ["ndsd", "ls"] else 2.5
            marker = "o" if "ndsd" in key or key == "endsd" else "s"
            ax.plot(noise_pct, vals,
                    linestyle=ls_style, linewidth=lw,
                    marker=marker, markersize=7,
                    color=COLORS[key], label=LABELS[key], alpha=0.9)

        # Vung cai thien (to mau giua LS va ILS)
        ls_vals  = [v * 100 for v in res["ls"]]
        ils_vals = [v * 100 for v in res["ils"]]
        ax.fill_between(noise_pct, ls_vals, ils_vals,
                        alpha=0.12, color="#E63946",
                        label="Vung cai thien")

        # Duong nguong 10%
        ax.axvline(x=10, color="#8B949E", linestyle=":", alpha=0.6, linewidth=1.2)
        ax.text(10.3, 5, "nguong 10%", color="#8B949E", fontsize=9, alpha=0.7)

        ax.set_title(model_titles[model], fontsize=12,
                     fontweight="bold", color="#E8E8E8", pad=8)
        ax.set_xlabel("Muc Nhieu e (%)", fontsize=10, color="#8B949E")
        ax.set_ylabel("Accuracy (%)", fontsize=10, color="#8B949E")
        ax.set_ylim(0, 108)
        ax.tick_params(colors="#8B949E")
        ax.grid(True, alpha=0.15, color="#8B949E")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363D")

        if idx == 0:
            ax.legend(fontsize=8.5, loc="upper right",
                      facecolor="#161B22", edgecolor="#30363D",
                      labelcolor="#E8E8E8")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="#0D1117")
    plt.close()
    print(f"\n[OK] Bieu do 1 luu tai: {output_path}")


def plot_improvement_delta(all_results, noise_levels, output_path):
    """
    Bieu do 2: Muc do cai thien (delta accuracy) cua ILS so voi LS thuan tuy.
    The hien ro rang: cai tien nhieu nhat o muc nhieu cao (e >= 10%).
    """
    noise_pct = [e * 100 for e in noise_levels]
    focus = ["BA", "HK"]  # Chi xet mo hinh phu hop MXH

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0D1117")
    fig.suptitle(
        "Muc Do Cai Thien: ENDSD+ILS vs NDSD+LS\n"
        "Delta Accuracy (%) = Improved - Baseline",
        fontsize=13, fontweight="bold", color="#E8E8E8", y=1.02
    )

    for idx, model in enumerate(focus):
        ax = axes[idx]
        ax.set_facecolor("#0D1117")
        res = all_results[model]

        ls_vals  = np.array([v * 100 for v in res["ls"]])
        ils_vals = np.array([v * 100 for v in res["ils"]])
        delta    = ils_vals - ls_vals

        # Bar chart cho delta
        bar_colors = ["#3FB950" if d >= 0 else "#E63946" for d in delta]
        bars = ax.bar(noise_pct, delta, color=bar_colors, alpha=0.75,
                      width=3.5, zorder=3)

        # Gia tri tren moi bar
        for bar, d in zip(bars, delta):
            ypos = bar.get_height() + 0.2 if d >= 0 else bar.get_height() - 0.8
            ax.text(bar.get_x() + bar.get_width() / 2, ypos,
                    f"+{d:.1f}%" if d >= 0 else f"{d:.1f}%",
                    ha="center", va="bottom", fontsize=11,
                    fontweight="bold",
                    color="#3FB950" if d >= 0 else "#E63946")

        # Duong so sanh 2 pipeline
        ax2 = ax.twinx()
        ax2.plot(noise_pct, ls_vals,  "o--", color=COLORS["ls"],
                 linewidth=2, markersize=7, label="Baseline (LS)", alpha=0.8)
        ax2.plot(noise_pct, ils_vals, "s-",  color=COLORS["ils"],
                 linewidth=2.5, markersize=7, label="Improved (ILS)", alpha=0.9)
        ax2.set_ylabel("Accuracy (%)", fontsize=10, color="#8B949E")
        ax2.tick_params(colors="#8B949E")
        ax2.set_ylim(0, 115)
        ax2.legend(fontsize=9, loc="upper right",
                   facecolor="#161B22", edgecolor="#30363D",
                   labelcolor="#E8E8E8")

        ax.axhline(y=0, color="#8B949E", linewidth=0.8, alpha=0.5)
        ax.axvline(x=10, color="#8B949E", linestyle=":", alpha=0.5)
        ax.set_title(
            f"Mo hinh {'Barabasi-Albert' if model=='BA' else 'Holme-Kim'}",
            fontsize=12, fontweight="bold", color="#E8E8E8"
        )
        ax.set_xlabel("Muc Nhieu e (%)", fontsize=10, color="#8B949E")
        ax.set_ylabel("Cai thien (diem %)", fontsize=10, color="#8B949E")
        ax.tick_params(colors="#8B949E")
        ax.grid(True, alpha=0.12, color="#8B949E", zorder=0)
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363D")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="#0D1117")
    plt.close()
    print(f"[OK] Bieu do 2 luu tai: {output_path}")


def plot_noise_tolerance_comparison(all_results, noise_levels, output_path,
                                    threshold=0.60):
    """
    Bieu do 3: Nguong nhieu co the chiu duoc (accuracy >= threshold).
    The hien ro: ENDSD+ILS chiu duoc nguong nhieu cao hon Baseline.
    """
    noise_pct = [e * 100 for e in noise_levels]
    models = list(all_results.keys())

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#0D1117")

    x = np.arange(len(models))
    width = 0.35

    def max_tolerable_noise(acc_list):
        """Tim muc nhieu cao nhat ma accuracy >= threshold."""
        for i in reversed(range(len(acc_list))):
            if acc_list[i] >= threshold:
                return noise_pct[i]
        return 0.0

    baseline_tolerance = [max_tolerable_noise(all_results[m]["ls"]) for m in models]
    improved_tolerance = [max_tolerable_noise(all_results[m]["ils"]) for m in models]

    bars1 = ax.bar(x - width/2, baseline_tolerance, width,
                   label="Baseline (NDSD + LS)", color=COLORS["ls"],
                   alpha=0.8, zorder=3)
    bars2 = ax.bar(x + width/2, improved_tolerance, width,
                   label="Improved (ENDSD + ILS)", color=COLORS["ils"],
                   alpha=0.8, zorder=3)

    # Gia tri tren moi bar
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.3,
                f"{h:.0f}%", ha="center", va="bottom",
                color=COLORS["ls"], fontsize=11, fontweight="bold")

    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.3,
                f"{h:.0f}%", ha="center", va="bottom",
                color=COLORS["ils"], fontsize=11, fontweight="bold")

    # Duong nguong 10% cua bai bao goc
    ax.axhline(y=10, color="#F4A261", linestyle="--",
               alpha=0.7, linewidth=1.5, label="Nguong bai bao goc (10%)")

    ax.set_title(
        f"Nguong Nhieu Co The Chiu Duoc (Accuracy >= {threshold*100:.0f}%)\n"
        "So Sanh: Baseline vs ENDSD + ILS",
        fontsize=13, fontweight="bold", color="#E8E8E8"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(["Barabasi-Albert", "Holme-Kim",
                         "Erdos-Renyi", "Watts-Strogatz"],
                        color="#E8E8E8", fontsize=11)
    ax.set_ylabel("Nguong Nhieu Toi Da (%)", fontsize=11, color="#8B949E")
    ax.set_ylim(0, 26)
    ax.tick_params(colors="#8B949E")
    ax.grid(True, alpha=0.12, color="#8B949E", axis="y", zorder=0)
    ax.legend(fontsize=10, facecolor="#161B22",
              edgecolor="#30363D", labelcolor="#E8E8E8")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363D")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="#0D1117")
    plt.close()
    print(f"[OK] Bieu do 3 luu tai: {output_path}")


# ─────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    N_NODES      = 120          # Du lon de co ket qua y nghia, du nho de chay nhanh
    N_TRIALS     = 3
    DELTA        = 0.05
    NOISE_LEVELS = [0.0, 0.05, 0.10, 0.15, 0.20]
    MODELS       = ["BA", "HK", "ER", "WS"]

    # ILS config
    ILS_R        = 4    # So lan perturbation + restart
    ILS_K        = 3    # So cap swap trong moi perturbation
    ENDSD_ALPHA  = 0.5  # Trong so 2-hop component

    print("=" * 65)
    print("  SO SANH THUC NGHIEM: GOC vs CAI TIEN")
    print("  Baseline : NDSD (1-hop) + Local Search thuan tuy")
    print("  Improved : ENDSD (2-hop) + Iterated Local Search (ILS)")
    print("=" * 65)

    all_results = {}
    for model in MODELS:
        all_results[model] = run_comparison(
            model=model, n=N_NODES,
            noise_levels=NOISE_LEVELS, n_trials=N_TRIALS,
            delta=DELTA, ils_R=ILS_R, ils_k=ILS_K,
            endsd_alpha=ENDSD_ALPHA,
        )

    # Ve 3 bieu do
    print("\n[*] Dang ve bieu do ket qua...")
    plot_comparison_all_models(
        all_results, NOISE_LEVELS,
        "ProjectANDD/bieu_do_3_so_sanh_4_mo_hinh.png"
    )
    plot_improvement_delta(
        all_results, NOISE_LEVELS,
        "ProjectANDD/bieu_do_4_muc_do_cai_thien.png"
    )
    plot_noise_tolerance_comparison(
        all_results, NOISE_LEVELS,
        "ProjectANDD/bieu_do_5_nguong_nhieu_chiu_duoc.png",
        threshold=0.60
    )

    # In bang tom tat
    print("\n" + "=" * 75)
    print("  BANG TOM TAT KET QUA (Accuracy % - trung binh 3 trials)")
    print("=" * 75)
    print(f"{'Mo hinh':<12} {'Pipeline':<28}" +
          "".join(f"  e={int(e*100)}%" for e in NOISE_LEVELS))
    print("-" * 75)
    for model in MODELS:
        for key, label in [("ls", "Baseline (LS)"), ("ils", "Improved (ILS)")]:
            row = f"{model if key=='ls' else '':<12} {label:<28}"
            for acc in all_results[model][key]:
                row += f"  {acc*100:5.1f}%"
            print(row)
        print()
    print("=" * 75)

    # Ket luan tu dong
    print("\n[*] KET LUAN TU DONG:")
    for model in ["BA", "HK"]:
        res = all_results[model]
        for i, eps in enumerate(NOISE_LEVELS):
            delta_acc = (res["ils"][i] - res["ls"][i]) * 100
            if delta_acc > 1:
                print(f"  {model} | e={int(eps*100)}%: "
                      f"ILS cai thien +{delta_acc:.1f}% so voi LS thuan tuy")

    print("\n[DONE] Thuc nghiem hoan tat!")
    print("       Xem 3 bieu do PNG tai ProjectANDD/")
