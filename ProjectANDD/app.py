# -*- coding: utf-8 -*-
"""
Flask Web Demo — Phi Ẩn Danh Hóa Mạng Xã Hội
Bài báo: "Deanonymizing Social Networks Using Structural Information" (IJCAI-2019)
Môn học: An Ninh Di Động
"""

import json
import random
import time

import networkx as nx
import numpy as np
from flask import Flask, jsonify, render_template, request
from scipy.optimize import linear_sum_assignment

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# CORE ALGORITHMS (từ experiment.py)
# ─────────────────────────────────────────────────────────────

def generate_graph(model: str, n: int) -> nx.Graph:
    if model == "BA":
        return nx.barabasi_albert_graph(n, m=2, seed=42)
    elif model == "ER":
        return nx.erdos_renyi_graph(n, p=0.08, seed=42)
    elif model == "WS":
        return nx.watts_strogatz_graph(n, k=4, p=0.1, seed=42)
    elif model == "HK":
        return nx.powerlaw_cluster_graph(n, m=2, p=0.5, seed=42)
    else:
        raise ValueError(f"Model not supported: {model}")


def create_noisy_subgraph(G: nx.Graph, delta: float, epsilon: float, seed: int = 0):
    rng = random.Random(seed)
    nodes_G = list(G.nodes())

    n_remove = int(len(nodes_G) * delta)
    removed = set(rng.sample(nodes_G, n_remove)) if n_remove > 0 else set()
    kept_nodes = [v for v in nodes_G if v not in removed]

    H_original = G.subgraph(kept_nodes).copy()
    H_noisy = H_original.copy()

    all_pairs = [(u, v) for u in kept_nodes for v in kept_nodes if u < v]
    for u, v in all_pairs:
        if rng.random() < epsilon:
            if H_noisy.has_edge(u, v):
                H_noisy.remove_edge(u, v)
            else:
                H_noisy.add_edge(u, v)

    node_to_anon = {v: i for i, v in enumerate(kept_nodes)}
    H = nx.relabel_nodes(H_noisy, node_to_anon)
    true_map = {i: v for i, v in enumerate(kept_nodes)}

    return H, true_map


def neighbor_degree_sequence(graph: nx.Graph, node) -> list:
    return sorted([graph.degree(nb) for nb in graph.neighbors(node)], reverse=True)


def nds_distance(seq_a: list, seq_b: list) -> float:
    max_len = max(len(seq_a), len(seq_b), 1)
    a = seq_a + [0] * (max_len - len(seq_a))
    b = seq_b + [0] * (max_len - len(seq_b))
    return sum(abs(x - y) for x, y in zip(a, b))


def ndsd_algorithm(G: nx.Graph, H: nx.Graph, true_map: dict) -> dict:
    nodes_H = list(H.nodes())
    nodes_G = list(true_map.values())

    nds_H = {v: neighbor_degree_sequence(H, v) for v in nodes_H}
    nds_G = {v: neighbor_degree_sequence(G, v) for v in nodes_G}

    n = len(nodes_H)
    m = len(nodes_G)
    cost_matrix = np.zeros((n, m))
    for i, h in enumerate(nodes_H):
        for j, g in enumerate(nodes_G):
            cost_matrix[i, j] = nds_distance(nds_H[h], nds_G[g])

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    predicted_map = {nodes_H[i]: nodes_G[j] for i, j in zip(row_ind, col_ind)}
    return predicted_map


def edge_overlap_score(G: nx.Graph, H: nx.Graph, mapping: dict) -> int:
    score = 0
    for u, v in H.edges():
        if G.has_edge(mapping.get(u, -1), mapping.get(v, -1)):
            score += 1
    return score


def local_search_algorithm(G: nx.Graph, H: nx.Graph, initial_map: dict, max_iter: int = None) -> dict:
    mapping = dict(initial_map)
    nodes_H = list(H.nodes())
    n = len(nodes_H)

    if max_iter is None:
        max_iter = n

    current_score = edge_overlap_score(G, H, mapping)

    for _ in range(max_iter):
        improved = False
        for i in range(n):
            for j in range(i + 1, n):
                u, v = nodes_H[i], nodes_H[j]
                mapping[u], mapping[v] = mapping[v], mapping[u]
                new_score = edge_overlap_score(G, H, mapping)
                if new_score > current_score:
                    current_score = new_score
                    improved = True
                else:
                    mapping[u], mapping[v] = mapping[v], mapping[u]
        if not improved:
            break

    return mapping


def compute_accuracy(predicted_map: dict, true_map: dict) -> float:
    if not true_map:
        return 0.0
    correct = sum(1 for h in true_map if predicted_map.get(h) == true_map[h])
    return correct / len(true_map)


def graph_to_json(G, layout=None, node_labels=None):
    """Convert NetworkX graph to JSON for D3.js visualization."""
    if layout is None:
        layout = nx.spring_layout(G, seed=42, k=2.0)

    nodes = []
    for node in G.nodes():
        x, y = layout[node]
        label = node_labels.get(node, str(node)) if node_labels else str(node)
        nodes.append({
            "id": int(node),
            "label": label,
            "degree": G.degree(node),
            "x": float(x),
            "y": float(y),
        })

    edges = []
    for u, v in G.edges():
        edges.append({"source": int(u), "target": int(v)})

    return {"nodes": nodes, "edges": edges}


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate graph G and anonymous graph H."""
    data = request.json
    model = data.get("model", "BA")
    n = int(data.get("n", 20))
    epsilon = float(data.get("epsilon", 0.0))
    delta = float(data.get("delta", 0.05))

    n = max(8, min(n, 40))  # Limit for web demo

    G = generate_graph(model, n)
    H, true_map = create_noisy_subgraph(G, delta=delta, epsilon=epsilon, seed=7)

    # Compute layout for G
    layout_G = nx.spring_layout(G, seed=42, k=1.5)

    # Compute layout for H (use similar positions as G for visual mapping)
    layout_H = {}
    nodes_H = list(H.nodes())
    for h_node in nodes_H:
        g_node = true_map[h_node]
        if g_node in layout_G:
            # Add small jitter
            jitter_x = random.uniform(-0.05, 0.05)
            jitter_y = random.uniform(-0.05, 0.05)
            layout_H[h_node] = (layout_G[g_node][0] + jitter_x, layout_G[g_node][1] + jitter_y)
        else:
            layout_H[h_node] = (random.uniform(-1, 1), random.uniform(-1, 1))

    # Random shuffle of layout_H to hide identity
    shuffled_positions = list(layout_H.values())
    random.shuffle(shuffled_positions)
    layout_H_shuffled = {node: pos for node, pos in zip(nodes_H, shuffled_positions)}

    g_json = graph_to_json(G, layout_G)
    h_json = graph_to_json(H, layout_H_shuffled)

    # Store true_map for later use (encode as string keys)
    true_map_str = {str(k): v for k, v in true_map.items()}

    return jsonify({
        "G": g_json,
        "H": h_json,
        "true_map": true_map_str,
        "model": model,
        "n_G": G.number_of_nodes(),
        "n_H": H.number_of_nodes(),
        "e_G": G.number_of_edges(),
        "e_H": H.number_of_edges(),
        "epsilon": epsilon,
        "delta": delta,
    })


@app.route("/api/run_ndsd", methods=["POST"])
def api_run_ndsd():
    """Run NDSD algorithm only (Step 2). Returns mapping for Local Search input."""
    data = request.json
    model = data.get("model", "BA")
    n = int(data.get("n", 20))
    epsilon = float(data.get("epsilon", 0.0))
    delta = float(data.get("delta", 0.05))

    n = max(8, min(n, 40))

    G = generate_graph(model, n)
    H, true_map = create_noisy_subgraph(G, delta=delta, epsilon=epsilon, seed=7)

    t0 = time.time()
    pred_ndsd = ndsd_algorithm(G, H, true_map)
    t_ndsd = time.time() - t0

    acc_ndsd = compute_accuracy(pred_ndsd, true_map)
    ndsd_correct = {str(h): (pred_ndsd.get(h) == true_map[h]) for h in true_map}
    ndsd_mapping = {str(k): int(v) for k, v in pred_ndsd.items()}
    true_map_result = {str(k): int(v) for k, v in true_map.items()}

    return jsonify({
        "acc_ndsd": round(acc_ndsd * 100, 1),
        "t_ndsd": round(t_ndsd, 2),
        "ndsd_correct": ndsd_correct,
        "ndsd_mapping": ndsd_mapping,
        "true_map": true_map_result,
        # Echo back params so Local Search endpoint can rebuild graphs
        "model": model,
        "n": n,
        "epsilon": epsilon,
        "delta": delta,
    })


@app.route("/api/run_local_search", methods=["POST"])
def api_run_local_search():
    """Run Local Search on top of a given NDSD mapping (Step 3)."""
    data = request.json
    model = data.get("model", "BA")
    n = int(data.get("n", 20))
    epsilon = float(data.get("epsilon", 0.0))
    delta = float(data.get("delta", 0.05))
    # ndsd_mapping: {str(h_node): g_node} sent from frontend
    ndsd_mapping_raw = data.get("ndsd_mapping", {})

    n = max(8, min(n, 40))

    G = generate_graph(model, n)
    H, true_map = create_noisy_subgraph(G, delta=delta, epsilon=epsilon, seed=7)

    # Reconstruct mapping with correct types
    initial_map = {int(k): int(v) for k, v in ndsd_mapping_raw.items()}

    t1 = time.time()
    pred_ls = local_search_algorithm(G, H, initial_map, max_iter=n)
    t_ls = time.time() - t1

    acc_ls = compute_accuracy(pred_ls, true_map)
    ls_correct = {str(h): (pred_ls.get(h) == true_map[h]) for h in true_map}
    ls_mapping = {str(k): int(v) for k, v in pred_ls.items()}
    true_map_result = {str(k): int(v) for k, v in true_map.items()}

    return jsonify({
        "acc_ls": round(acc_ls * 100, 1),
        "t_ls": round(t_ls, 2),
        "ls_correct": ls_correct,
        "ls_mapping": ls_mapping,
        "true_map": true_map_result,
    })


@app.route("/api/accuracy_curve", methods=["POST"])
def api_accuracy_curve():
    """Compute accuracy at multiple noise levels for chart."""
    data = request.json
    model = data.get("model", "BA")
    n = int(data.get("n", 25))
    n = max(8, min(n, 30))

    noise_levels = [0.0, 0.05, 0.10, 0.15, 0.20]

    G = generate_graph(model, n)

    ndsd_accs = []
    ls_accs = []

    for eps in noise_levels:
        H, true_map = create_noisy_subgraph(G, delta=0.05, epsilon=eps, seed=7)
        pred_ndsd = ndsd_algorithm(G, H, true_map)
        acc_ndsd = compute_accuracy(pred_ndsd, true_map)
        pred_ls = local_search_algorithm(G, H, pred_ndsd, max_iter=n)
        acc_ls = compute_accuracy(pred_ls, true_map)
        ndsd_accs.append(round(acc_ndsd * 100, 1))
        ls_accs.append(round(acc_ls * 100, 1))

    return jsonify({
        "noise_levels": [int(e * 100) for e in noise_levels],
        "ndsd": ndsd_accs,
        "ls": ls_accs,
        "model": model,
    })


@app.route("/api/game_check", methods=["POST"])
def api_game_check():
    """Check user's guesses in game mode."""
    data = request.json
    user_guesses = data.get("guesses", {})  # {str(h_node): int(g_node)}
    true_map = data.get("true_map", {})     # {str(h_node): int(g_node)}

    correct = 0
    total = len(true_map)
    results = {}

    for h_str, g_guess in user_guesses.items():
        actual = true_map.get(h_str)
        is_correct = (int(g_guess) == int(actual)) if actual is not None else False
        results[h_str] = {
            "guess": int(g_guess),
            "actual": int(actual) if actual is not None else -1,
            "correct": is_correct,
        }
        if is_correct:
            correct += 1

    score = round(correct / total * 100, 1) if total > 0 else 0

    return jsonify({
        "score": score,
        "correct": correct,
        "total": total,
        "results": results,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5050, host="0.0.0.0")
