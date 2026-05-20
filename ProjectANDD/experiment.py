# -*- coding: utf-8 -*-
"""
Phi Ẩn Danh Hóa Mạng Xã Hội - Tái Hiện Thực Nghiệm
Bài báo: "Deanonymizing Social Networks Using Structural Information" (IJCAI-2019)
Caragiannis & Tsitsoka, Đại học Patras, Hy Lạp

Môn học: An Ninh Di Động
"""

import random
import time
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.optimize import linear_sum_assignment

# ─────────────────────────────────────────────────────────────
# 1. SINH ĐỒ THỊ VÀ TẠO NOISY SUBGRAPH
# ─────────────────────────────────────────────────────────────

def generate_graph(model: str, n: int) -> nx.Graph:
    """Sinh đồ thị G theo 4 mô hình kinh điển."""
    if model == "BA":          # Barabási-Albert (scale-free)
        return nx.barabasi_albert_graph(n, m=3, seed=42)
    elif model == "ER":        # Erdős-Rényi (random)
        return nx.erdos_renyi_graph(n, p=0.02, seed=42)
    elif model == "WS":        # Watts-Strogatz (small-world)
        return nx.watts_strogatz_graph(n, k=6, p=0.1, seed=42)
    elif model == "HK":        # Holme-Kim (clustering + scale-free)
        return nx.powerlaw_cluster_graph(n, m=3, p=0.5, seed=42)
    else:
        raise ValueError(f"Mô hình không hỗ trợ: {model}")


def create_noisy_subgraph(G: nx.Graph, delta: float, epsilon: float, seed: int = 0):
    """
    Tạo đồ thị H là noisy subgraph của G.

    Args:
        G:       Đồ thị gốc có danh tính
        delta:   Tỷ lệ node bị xóa khỏi H  (0 → 0.2)
        epsilon: Xác suất mỗi cạnh bị đổi   (0 → 0.2)
        seed:    Seed ngẫu nhiên

    Returns:
        H:         Đồ thị ẩn danh (node được đổi tên)
        true_map:  Dict {node_H → node_G} ánh xạ thật (để tính accuracy)
    """
    rng = random.Random(seed)
    nodes_G = list(G.nodes())

    # Bước 1: Xóa delta% node khỏi H
    n_remove = int(len(nodes_G) * delta)
    removed = set(rng.sample(nodes_G, n_remove))
    kept_nodes = [v for v in nodes_G if v not in removed]

    # Bước 2: Lấy subgraph trên các node còn lại
    H_original = G.subgraph(kept_nodes).copy()

    # Bước 3: Thêm nhiễu cạnh (epsilon)
    H_noisy = H_original.copy()
    all_pairs = [(u, v) for u in kept_nodes for v in kept_nodes if u < v]
    for u, v in all_pairs:
        if rng.random() < epsilon:
            if H_noisy.has_edge(u, v):
                H_noisy.remove_edge(u, v)
            else:
                H_noisy.add_edge(u, v)

    # Bước 4: Đổi tên node (ẩn danh hóa) — ánh xạ node_G → node_H (0-indexed)
    node_to_anon = {v: i for i, v in enumerate(kept_nodes)}
    H = nx.relabel_nodes(H_noisy, node_to_anon)

    # true_map: node_H → node_G (để tính accuracy sau de-anonymize)
    true_map = {i: v for i, v in enumerate(kept_nodes)}

    return H, true_map


# ─────────────────────────────────────────────────────────────
# 2. THUẬT TOÁN NDSD (Neighbor Degree Sequence Difference)
# ─────────────────────────────────────────────────────────────

def neighbor_degree_sequence(graph: nx.Graph, node) -> list:
    """
    Trả về chuỗi bậc (degree) của các láng giềng của node,
    sắp xếp giảm dần — đây là "chữ ký cấu trúc" của node.
    """
    return sorted([graph.degree(nb) for nb in graph.neighbors(node)], reverse=True)


def nds_distance(seq_a: list, seq_b: list) -> float:
    """
    Khoảng cách L1 giữa hai chuỗi bậc.
    Pad chuỗi ngắn hơn bằng 0.
    """
    max_len = max(len(seq_a), len(seq_b), 1)
    a = seq_a + [0] * (max_len - len(seq_a))
    b = seq_b + [0] * (max_len - len(seq_b))
    return sum(abs(x - y) for x, y in zip(a, b))


def ndsd_algorithm(G: nx.Graph, H: nx.Graph, true_map: dict) -> dict:
    """
    Thuật toán NDSD: khớp node H → G dựa trên Neighbor Degree Sequence.
    Sử dụng Hungarian Algorithm (linear_sum_assignment) để tìm khớp tối ưu.

    Returns:
        predicted_map: {node_H → node_G}
    """
    nodes_H = list(H.nodes())
    nodes_G = list(true_map.values())  # Các node G tương ứng

    # Tính NDS cho từng node
    nds_H = {v: neighbor_degree_sequence(H, v) for v in nodes_H}
    nds_G = {v: neighbor_degree_sequence(G, v) for v in nodes_G}

    # Xây dựng cost matrix: cost[i][j] = khoảng cách NDS giữa nodes_H[i] và nodes_G[j]
    n = len(nodes_H)
    m = len(nodes_G)
    cost_matrix = np.zeros((n, m))
    for i, h in enumerate(nodes_H):
        for j, g in enumerate(nodes_G):
            cost_matrix[i, j] = nds_distance(nds_H[h], nds_G[g])

    # Hungarian matching
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    predicted_map = {nodes_H[i]: nodes_G[j] for i, j in zip(row_ind, col_ind)}
    return predicted_map


# ─────────────────────────────────────────────────────────────
# 3. THUẬT TOÁN LOCAL SEARCH (Swap-based)
# ─────────────────────────────────────────────────────────────

def edge_overlap_score(G: nx.Graph, H: nx.Graph, mapping: dict) -> int:
    """
    Tính số cạnh trong H được khớp đúng theo mapping.
    Cạnh (u,v) trong H đúng nếu (mapping[u], mapping[v]) tồn tại trong G.
    """
    score = 0
    for u, v in H.edges():
        if G.has_edge(mapping.get(u, -1), mapping.get(v, -1)):
            score += 1
    return score


def local_search_algorithm(G: nx.Graph, H: nx.Graph,
                            initial_map: dict, max_iter: int = None) -> dict:
    """
    Thuật toán Local Search: cải thiện ánh xạ bằng cách swap 2 node trong H.
    Mỗi vòng lặp thử swap tất cả cặp (i,j), chấp nhận nếu score tăng.
    Dừng khi không có swap nào cải thiện (local optimum).

    Args:
        G:           Đồ thị gốc
        H:           Đồ thị ẩn danh
        initial_map: Ánh xạ ban đầu (từ NDSD)
        max_iter:    Giới hạn số vòng lặp (mặc định: n²)
    """
    mapping = dict(initial_map)
    nodes_H = list(H.nodes())
    n = len(nodes_H)

    if max_iter is None:
        max_iter = n * n

    current_score = edge_overlap_score(G, H, mapping)

    for iteration in range(max_iter):
        improved = False

        for i in range(n):
            for j in range(i + 1, n):
                u, v = nodes_H[i], nodes_H[j]
                # Thử swap mapping[u] ↔ mapping[v]
                mapping[u], mapping[v] = mapping[v], mapping[u]
                new_score = edge_overlap_score(G, H, mapping)

                if new_score > current_score:
                    # Chấp nhận swap
                    current_score = new_score
                    improved = True
                else:
                    # Hoàn tác swap
                    mapping[u], mapping[v] = mapping[v], mapping[u]

        if not improved:
            # Đạt local optimum — dừng sớm
            break

    return mapping


# ─────────────────────────────────────────────────────────────
# 4. TÍNH ACCURACY
# ─────────────────────────────────────────────────────────────

def compute_accuracy(predicted_map: dict, true_map: dict) -> float:
    """
    Accuracy = tỷ lệ node trong H được de-anonymize đúng.
    predicted_map: {node_H → node_G_predicted}
    true_map:      {node_H → node_G_true}
    """
    if not true_map:
        return 0.0
    correct = sum(1 for h in true_map if predicted_map.get(h) == true_map[h])
    return correct / len(true_map)


# ─────────────────────────────────────────────────────────────
# 5. CHẠY THỰ NGHIỆM
# ─────────────────────────────────────────────────────────────

def run_experiment(model: str, n: int, noise_levels: list,
                   n_trials: int = 5, delta: float = 0.05) -> dict:
    """
    Chạy thực nghiệm cho một mô hình đồ thị.

    Args:
        model:        Tên mô hình ("BA", "ER", "WS", "HK")
        n:            Số node của G
        noise_levels: Danh sách mức nhiễu epsilon
        n_trials:     Số lần lặp để lấy trung bình
        delta:        Tỷ lệ node bị xóa (cố định 5%)

    Returns:
        Dict kết quả accuracy trung bình cho NDSD và LocalSearch
    """
    print(f"\n{'='*60}")
    print(f"  Mô hình: {model} | n={n} | delta={delta*100:.0f}% | {n_trials} trials")
    print(f"{'='*60}")

    G = generate_graph(model, n)
    print(f"  Đồ thị G: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    results = {"ndsd": [], "local_search": []}

    for eps in noise_levels:
        acc_ndsd_list = []
        acc_ls_list = []

        for trial in range(n_trials):
            H, true_map = create_noisy_subgraph(G, delta=delta, epsilon=eps, seed=trial)

            # NDSD
            t0 = time.time()
            pred_ndsd = ndsd_algorithm(G, H, true_map)
            acc_ndsd = compute_accuracy(pred_ndsd, true_map)
            acc_ndsd_list.append(acc_ndsd)

            # Local Search (khởi động từ NDSD)
            pred_ls = local_search_algorithm(G, H, pred_ndsd, max_iter=n)
            acc_ls = compute_accuracy(pred_ls, true_map)
            acc_ls_list.append(acc_ls)

            t1 = time.time()
            print(f"  ε={eps*100:4.0f}% | trial {trial+1} | "
                  f"NDSD={acc_ndsd*100:5.1f}% | LS={acc_ls*100:5.1f}% | {t1-t0:.1f}s")

        results["ndsd"].append(np.mean(acc_ndsd_list))
        results["local_search"].append(np.mean(acc_ls_list))

    return results


# ─────────────────────────────────────────────────────────────
# 6. VẼ BIỂU ĐỒ
# ─────────────────────────────────────────────────────────────

COLORS = {
    "BA": "#E63946",   # Đỏ — mô hình tốt nhất
    "HK": "#F4A261",   # Cam
    "ER": "#457B9D",   # Xanh dương
    "WS": "#6D6875",   # Tím xám
}

MODEL_LABELS = {
    "BA": "Barabási-Albert",
    "HK": "Holme-Kim",
    "ER": "Erdős-Rényi",
    "WS": "Watts-Strogatz",
}


def plot_accuracy_vs_noise(all_results: dict, noise_levels: list, output_path: str):
    """
    Biểu đồ 1: So sánh accuracy của Local Search qua các mức nhiễu, 4 mô hình.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Phi Ẩn Danh Hóa Mạng Xã Hội — Kết Quả Thực Nghiệm\n"
        "(Deanonymizing Social Networks Using Structural Information, IJCAI-2019)",
        fontsize=13, fontweight="bold", y=1.02
    )

    noise_pct = [e * 100 for e in noise_levels]

    # — Subplot 1: NDSD accuracy —
    ax1 = axes[0]
    for model, res in all_results.items():
        ax1.plot(noise_pct, [v * 100 for v in res["ndsd"]],
                 marker="o", linewidth=2, markersize=7,
                 color=COLORS[model], label=MODEL_LABELS[model])
    ax1.set_title("Thuật Toán NDSD", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Mức Nhiễu ε (%)", fontsize=11)
    ax1.set_ylabel("Accuracy (%)", fontsize=11)
    ax1.set_ylim(0, 105)
    ax1.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=10, color="gray", linestyle="--", alpha=0.5, label="Ngưỡng 10%")

    # — Subplot 2: Local Search accuracy —
    ax2 = axes[1]
    for model, res in all_results.items():
        ax2.plot(noise_pct, [v * 100 for v in res["local_search"]],
                 marker="s", linewidth=2, markersize=7,
                 color=COLORS[model], label=MODEL_LABELS[model])
    ax2.set_title("Thuật Toán Local Search (sau NDSD)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Mức Nhiễu ε (%)", fontsize=11)
    ax2.set_ylabel("Accuracy (%)", fontsize=11)
    ax2.set_ylim(0, 105)
    ax2.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.axvline(x=10, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n[OK] Biểu đồ 1 lưu tại: {output_path}")


def plot_ndsd_vs_ls_comparison(all_results: dict, noise_levels: list, output_path: str):
    """
    Biểu đồ 2: Cải thiện của Local Search so với NDSD — chỉ BA và HK.
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "NDSD vs Local Search — Cải Thiện Accuracy\n"
        "(Chỉ mô hình phù hợp mạng xã hội thực tế)",
        fontsize=13, fontweight="bold", y=1.02
    )

    noise_pct = [e * 100 for e in noise_levels]
    focus_models = ["BA", "HK"]

    for idx, model in enumerate(focus_models):
        ax = axes[idx]
        res = all_results[model]
        ndsd_acc   = [v * 100 for v in res["ndsd"]]
        ls_acc     = [v * 100 for v in res["local_search"]]
        improvement = [ls - nd for ls, nd in zip(ls_acc, ndsd_acc)]

        ax.fill_between(noise_pct, ndsd_acc, ls_acc,
                        alpha=0.25, color=COLORS[model], label="Vùng cải thiện")
        ax.plot(noise_pct, ndsd_acc, "o--", linewidth=2, markersize=7,
                color=COLORS[model], alpha=0.7, label="NDSD")
        ax.plot(noise_pct, ls_acc, "s-", linewidth=2.5, markersize=7,
                color=COLORS[model], label="Local Search")

        ax2 = ax.twinx()
        ax2.bar(noise_pct, improvement, alpha=0.15, color=COLORS[model], width=1.5)
        ax2.set_ylabel("Cải thiện (điểm %)", fontsize=9, color="gray")
        ax2.tick_params(axis="y", labelcolor="gray")
        ax2.set_ylim(0, 30)

        ax.set_title(f"Mô hình {MODEL_LABELS[model]}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Mức Nhiễu ε (%)", fontsize=11)
        ax.set_ylabel("Accuracy (%)", fontsize=11)
        ax.set_ylim(0, 105)
        ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
        ax.legend(fontsize=9, loc="lower left")
        ax.grid(True, alpha=0.3)
        ax.axvline(x=10, color="gray", linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] Biểu đồ 2 lưu tại: {output_path}")


# ─────────────────────────────────────────────────────────────
# 7. MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Cấu hình thực nghiệm
    N_NODES     = 350          # Kích thước đồ thị G (300-500 nodes)
    N_TRIALS    = 5            # Số lần lặp mỗi cấu hình
    DELTA       = 0.05         # Tỷ lệ node bị xóa (5%)
    NOISE_LEVELS = [0.0, 0.05, 0.10, 0.15, 0.20]   # ε ∈ {0%, 5%, 10%, 15%, 20%}
    MODELS      = ["BA", "HK", "ER", "WS"]

    print("=" * 60)
    print("  PHI ẨN DANH HÓA MẠNG XÃ HỘI — THỰC NGHIỆM")
    print("  IJCAI-2019 | Môn: An Ninh Di Động")
    print("=" * 60)

    all_results = {}
    for model in MODELS:
        all_results[model] = run_experiment(
            model=model,
            n=N_NODES,
            noise_levels=NOISE_LEVELS,
            n_trials=N_TRIALS,
            delta=DELTA,
        )

    # Vẽ và lưu biểu đồ
    print("\n[*] Đang vẽ biểu đồ...")
    plot_accuracy_vs_noise(
        all_results, NOISE_LEVELS,
        output_path="ProjectANDD/bieu_do_1_accuracy_vs_noise.png"
    )
    plot_ndsd_vs_ls_comparison(
        all_results, NOISE_LEVELS,
        output_path="ProjectANDD/bieu_do_2_ndsd_vs_local_search.png"
    )

    # In bảng tóm tắt
    print("\n" + "=" * 70)
    print("  BẢNG TÓM TẮT KẾT QUẢ (Local Search Accuracy %)")
    print("=" * 70)
    header = f"{'Mô hình':<20}" + "".join(f"ε={int(e*100)}%{'':<5}" for e in NOISE_LEVELS)
    print(header)
    print("-" * 70)
    for model in MODELS:
        row = f"{MODEL_LABELS[model]:<20}"
        for acc in all_results[model]["local_search"]:
            row += f"{acc*100:6.1f}%    "
        print(row)
    print("=" * 70)
    print("\n[DONE] Thực nghiệm hoàn tất!")
    print("       → Xem biểu đồ tại thư mục ProjectANDD/")
