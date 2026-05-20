# NỘI DUNG LÝ THUYẾT CHI TIẾT
# Bài báo: "Deanonymizing Social Networks Using Structural Information" — IJCAI-2019
# Caragiannis & Tsitsoka | Môn: An Ninh Di Động

---

## 1. ĐẶT VẤN ĐỀ VÀ ĐỘNG LỰC NGHIÊN CỨU

### 1.1 Bối Cảnh

Trong kỷ nguyên số, các mạng xã hội (Facebook, Twitter, LinkedIn...) lưu trữ lượng
thông tin khổng lồ về quan hệ giữa người dùng. Để bảo vệ quyền riêng tư, các tổ chức
thường **ẩn danh hóa** dữ liệu trước khi chia sẻ — tức là xóa đi các thông tin định danh
trực tiếp (tên, ID, email) trước khi cung cấp cho nhà nghiên cứu hay đối tác.

**Vấn đề cốt lõi:** Việc xóa danh tính *không đủ* để bảo vệ quyền riêng tư,
vì **cấu trúc quan hệ** (ai kết nối với ai) vẫn còn nguyên và có thể bị khai thác.

### 1.2 Tiền Đề Quan Trọng

Narayanan & Shmatikov (2009) đã chứng minh điều này lần đầu với dataset Netflix:
- Dữ liệu đánh giá phim đã được ẩn danh hóa → vẫn de-anonymize được qua IMDB
- Chỉ cần biết **một vài bộ phim** người dùng đã đánh giá là đủ để nhận dạng

Bài báo IJCAI-2019 này đi xa hơn: **không cần bất kỳ thông tin bên ngoài nào** —
chỉ dùng **cấu trúc đồ thị thuần túy** để de-anonymize.

### 1.3 Câu Hỏi Nghiên Cứu

> Chỉ dùng thông tin cấu trúc (ai kết nối với ai), liệu có thể khôi phục
> danh tính của các node trong một mạng xã hội ẩn danh không?

---

## 2. ĐỊNH NGHĨA BÀI TOÁN HÌNH THỨC

### 2.1 Ký Hiệu

| Ký hiệu | Ý nghĩa |
|---------|---------|
| G = (V, E) | Đồ thị có danh tính (eponymous graph) |
| H = (V', E') | Đồ thị ẩn danh (anonymous graph) |
| n = \|V\| | Số node trong G |
| m = \|V'\| | Số node trong H (m ≤ n) |
| δ ∈ [0,1) | Tỷ lệ node bị xóa khỏi H |
| ε ∈ [0,1) | Xác suất mỗi cạnh bị đổi trạng thái |
| σ: V' → V | Ánh xạ de-anonymization (cần tìm) |
| σ* | Ánh xạ đúng thực sự (ground truth) |

### 2.2 Mô Hình Nhiễu (Noise Model)

H được tạo từ G theo quy trình sau:

```
Bước 1 — Xóa node:
  Chọn ngẫu nhiên δ·n node từ V → xóa khỏi G
  V' = V \ {các node bị xóa}

Bước 2 — Thêm nhiễu cạnh:
  Với mỗi cặp (u,v) ∈ V' × V':
    Với xác suất ε: đổi trạng thái cạnh
      (nếu (u,v) ∈ E → xóa cạnh)
      (nếu (u,v) ∉ E → thêm cạnh)

Bước 3 — Ẩn danh hóa:
  Đổi tên tất cả node trong V' → node ẩn danh
  Kẻ tấn công không biết node nào trong H tương ứng với node nào trong G
```

**Minh họa trực quan:**

```
    G (có danh tính)          H (ẩn danh, sau nhiễu)
    
    Alice ─── Bob             [0] ─── [1]
      |         |               |
    Carol ─── Dave            [2]     [3]
      |                         |
    Eve (bị xóa)              [4] (node mới, nhiễu)
    
    Mục tiêu: tìm σ sao cho σ(0)=Alice, σ(1)=Bob, ...
```

### 2.3 Hàm Mục Tiêu

Bài toán được hình thức hóa là **tối ưu hóa giả toàn ánh** (pseudo-bijection optimization):

```
    max  |{ (u,v) ∈ E(H) : (σ(u), σ(v)) ∈ E(G) }|
   σ: V'→V
   (σ injective)
```

Nói cách khác: tìm ánh xạ 1-1 từ V' → V **tối đa hóa** số cạnh trong H
được "khớp đúng" với cạnh trong G.

### 2.4 Liên Hệ Với Graph Isomorphism

Nếu δ = 0 và ε = 0, bài toán trở thành **Subgraph Isomorphism** — bài toán NP-khó.
Điều này có nghĩa là không thể kỳ vọng thuật toán chính xác 100% trong thời gian đa thức
với nhiễu tổng quát. Vì vậy các tác giả thiết kế **heuristic** thực tế.

---

## 3. THUẬT TOÁN 1: NDSD (Neighbor Degree Sequence Difference)

### 3.1 Trực Giác

**Ý tưởng cốt lõi:** Hai node là cùng một người nếu chúng có "vùng lân cận tương tự".

Trong một mạng xã hội, mỗi người có một tập bạn bè đặc trưng. Thậm chí khi tên bị xóa,
**cấu trúc vùng lân cận** (các bạn của bạn tôi có bao nhiêu bạn?) vẫn là "dấu vân tay"
có thể nhận dạng.

### 3.2 Định Nghĩa: Neighbor Degree Sequence (NDS)

```
Định nghĩa: NDS(v, G) = dãy bậc của các láng giềng của v trong G,
            sắp xếp theo thứ tự GIẢM DẦN.

Ví dụ:
  v có 3 láng giềng: u1 (bậc 5), u2 (bậc 3), u3 (bậc 3)
  → NDS(v, G) = [5, 3, 3]

  v' trong H có 3 láng giềng: w1 (bậc 6), w2 (bậc 3), w3 (bậc 2)
  → NDS(v', H) = [6, 3, 2]
```

### 3.3 Định Nghĩa: Khoảng Cách NDS

```
dist_NDS(u, v) = Σ |NDS(u)[i] - NDS(v)[i]|    (chuẩn L1)
                  i

Pad chuỗi ngắn hơn bằng 0 nếu độ dài khác nhau.

Ví dụ:
  NDS(u) = [5, 3, 3, 0]
  NDS(v) = [6, 3, 2, 0]
  dist = |5-6| + |3-3| + |3-2| + |0-0| = 1 + 0 + 1 + 0 = 2
```

### 3.4 Thuật Toán Hungary (Hungarian Algorithm)

Sau khi tính xong ma trận khoảng cách C[i][j] = dist_NDS(nodes_H[i], nodes_G[j]),
bài toán trở thành **Assignment Problem**:

```
Tìm matching 1-1 tối thiểu tổng chi phí:
   min  Σ C[i][σ(i)]
   σ    i
```

Thuật toán Hungary giải Assignment Problem trong **O(n³)**:
- Augment paths qua bipartite graph
- Tổng độ phức tạp NDSD = O(n²) tính NDS × O(n²) tính C × O(n³) Hungarian = **O(n⁴)**

### 3.5 Pseudocode

```
Algorithm NDSD(G, H):
  Input:  G (eponymous graph), H (anonymous graph)
  Output: σ: V(H) → V(G)

  1. FOR mỗi v ∈ V(H):
       nds_H[v] ← sort([degree_H(u) for u in neighbors_H(v)], desc)

  2. FOR mỗi v ∈ V(G):
       nds_G[v] ← sort([degree_G(u) for u in neighbors_G(v)], desc)

  3. Xây dựng ma trận C (|V(H)| × |V(G)|):
       C[i][j] ← dist_L1(nds_H[nodes_H[i]], nds_G[nodes_G[j]])

  4. σ ← Hungarian_Algorithm(C)

  5. Return σ
```

### 3.6 Phân Tích Lý Thuyết

**Định lý (Babai et al., 1980 — áp dụng):**
Với đồ thị ngẫu nhiên G(n, p) và p = Ω(log n / n), hầu hết các node có NDS phân biệt
→ NDSD cho accuracy cao khi không có nhiễu.

**Giới hạn:** Khi ε tăng, NDS bị nhiễu loạn → dist_NDS kém chính xác hơn.

---

## 4. THUẬT TOÁN 2: LOCAL SEARCH (Tìm Kiếm Cục Bộ)

### 4.1 Trực Giác

NDSD cho một nghiệm ban đầu tốt nhưng không tối ưu. Local Search cải thiện
bằng cách **thử hoán đổi** ánh xạ của 2 node và chấp nhận nếu score tăng.

### 4.2 Hàm Mục Tiêu (Score Function)

```
score(σ, G, H) = |{ (u,v) ∈ E(H) : (σ(u), σ(v)) ∈ E(G) }|
              = số cạnh trong H được de-anonymize đúng
```

### 4.3 Phép Toán Swap

```
Swap(σ, u, v):
  σ_new = σ với σ_new(u) ↔ σ_new(v)
  
  Chấp nhận nếu: score(σ_new) > score(σ)
```

**Tính score sau swap hiệu quả:**
Không cần tính lại toàn bộ — chỉ cần xét các cạnh liên quan đến u và v.

### 4.4 Pseudocode

```
Algorithm LocalSearch(G, H, σ₀):
  Input:  G, H, σ₀ (nghiệm ban đầu từ NDSD)
  Output: σ* (nghiệm cải thiện)

  σ ← σ₀
  current_score ← score(σ, G, H)

  REPEAT:
    improved ← False
    
    FOR mỗi cặp (u, v) ∈ V(H) × V(H), u ≠ v:
      σ' ← Swap(σ, u, v)
      new_score ← score(σ', G, H)
      
      IF new_score > current_score:
        σ ← σ'
        current_score ← new_score
        improved ← True
        BREAK  (hoặc tiếp tục scan hết — first-improvement vs best-improvement)
    
  UNTIL NOT improved  (đạt local optimum)
  
  Return σ
```

### 4.5 Phân Tích Độ Phức Tạp

| Thành phần | Độ phức tạp |
|-----------|------------|
| Số cặp swap mỗi vòng | O(n²) |
| Tính score mỗi swap | O(n) (chỉ xét hàng xóm) |
| Số vòng lặp tối đa | O(n²) (mỗi vòng score tăng ít nhất 1) |
| **Tổng** | **O(n⁵)** |

**Ghi chú thực tế:** Hội tụ thường nhanh hơn nhiều vì:
- Dừng khi không còn swap nào cải thiện
- Thực tế: O(n²) - O(n³) vòng lặp đủ

### 4.6 Kết Hợp NDSD + Local Search

```
Pipeline hoàn chỉnh:
  σ_ndsd  ← NDSD(G, H)                    # Nghiệm ban đầu nhanh
  σ_final ← LocalSearch(G, H, σ_ndsd)     # Cải thiện cục bộ
  
  Return σ_final
```

**Lý do kết hợp hiệu quả:**
- NDSD tránh cho Local Search khởi đầu từ điểm ngẫu nhiên (kém)
- Local Search bù đắp điểm yếu của NDSD (chỉ dùng NDS, bỏ qua cấu trúc toàn cục)
- Hai thuật toán bù trừ điểm yếu nhau

---

## 5. BỐN MÔ HÌNH ĐỒ THỊ — LÝ THUYẾT VÀ SO SÁNH

### 5.1 Erdős-Rényi G(n, p) — Mô Hình Ngẫu Nhiên Thuần Túy

```
Quy tắc tạo:
  - n node
  - Mỗi cặp (u,v): thêm cạnh với xác suất p độc lập

Phân phối bậc: Binomial(n-1, p) ≈ Poisson(λ = (n-1)p)
Đặc trưng: Bậc trung bình gần bằng nhau cho mọi node
           → NDS rất GIỐNG NHAU → NDSD kém!

Phù hợp mạng XH? ❌ KHÔNG
  - Mạng thực có "hub" (người nổi tiếng) — ER không có
  - Mạng thực có clustering cao — ER rất thấp
```

### 5.2 Watts-Strogatz — Mô Hình Small-World

```
Quy tắc tạo:
  - Bắt đầu từ vòng: n node, mỗi node nối k láng giềng gần nhất
  - Rewire: mỗi cạnh được nối lại ngẫu nhiên với xác suất β

Đặc trưng:
  - Clustering coefficient cao (bạn của bạn thường là bạn)
  - Diameter nhỏ (6 degrees of separation)
  - Phân phối bậc: ĐỒNG ĐỀU quanh k (không có hub)

Phù hợp mạng XH? ❌ KHÔNG
  - Thiếu hub → NDSD khó phân biệt node
  - Bậc đồng đều → NDS giống nhau
```

### 5.3 Barabási-Albert — Mô Hình Scale-Free

```
Quy tắc tạo (Preferential Attachment):
  - Bắt đầu với m₀ node
  - Mỗi node mới thêm m cạnh đến các node cũ
  - Xác suất kết nối ∝ bậc hiện tại ("rich get richer")

Phân phối bậc: Power-law P(k) ~ k^(-γ), γ ≈ 3
Đặc trưng:
  - Có ít node "hub" với bậc RẤT CAO
  - Đa số node có bậc thấp
  - Hub tạo "chữ ký" độc đáo cho vùng lân cận

Phù hợp mạng XH? ✅ RẤT PHÙ HỢP
  - Twitter: vài nghìn "influencer" + hàng triệu người theo dõi
  - Facebook: Zuckerberg có hàng triệu friends
  - Power-law đã quan sát trong nhiều mạng thực
```

### 5.4 Holme-Kim — Mô Hình Scale-Free + Clustering

```
Quy tắc tạo (Mở rộng của BA):
  - Sau mỗi bước Preferential Attachment của BA
  - Với xác suất p: thêm "Triangle Closing" step
    (nối node mới với bạn của bạn → tạo tam giác)

Phân phối bậc: Power-law (giống BA)
Clustering: CAO HƠN BA vì có bước Triangle Closing

Phù hợp mạng XH? ✅ RẤT PHÙ HỢP
  - Kết hợp ưu điểm BA (scale-free) + clustering thực tế
  - Mạng tình bạn thực sự có clustering cao ("nhóm bạn")
```

### 5.5 Bảng So Sánh Tổng Hợp

| Đặc trưng | Erdős-Rényi | Watts-Strogatz | Barabási-Albert | Holme-Kim |
|-----------|------------|----------------|-----------------|-----------|
| Phân phối bậc | Poisson | Đều | Power-law | Power-law |
| Hub rõ ràng | ❌ | ❌ | ✅ | ✅ |
| Clustering cao | ❌ | ✅ | ❌ thấp | ✅ |
| Small-world | ✅ | ✅ | ✅ | ✅ |
| Phù hợp MXH | ❌ | ❌ | ✅ | ✅ |
| NDSD accuracy | Thấp | Rất thấp | Cao | Cao |
| LS accuracy | Thấp | Rất thấp | Rất cao | Rất cao |

### 5.6 Tại Sao Hub Quan Trọng Với NDSD?

Hub (node bậc cao) trong BA/HK tạo ra NDS rất đặc trưng:

```
Node A (hub, bậc 50): NDS = [48, 45, 43, 40, ...]   ← UNIQUE
Node B (thường, bậc 3): NDS = [50, 4, 2]             ← Phân biệt được nhờ hub lân cận
Node C (thường, bậc 3): NDS = [3, 2, 1]              ← Khó phân biệt

→ Hub tạo "neo" (anchor) để NDSD tìm đúng → rồi lan ra các node xung quanh
```

---

## 6. PHÂN TÍCH KẾT QUẢ THỰC NGHIỆM

### 6.1 Phát Hiện Chính

| Phát hiện | Giải thích |
|----------|-----------|
| BA + HK chịu được ε ≤ 10% | Hub tạo NDS độc đáo, dễ khớp dù có nhiễu |
| ER + WS kém ngay cả ε = 0% | Phân phối bậc đồng đều → NDS không phân biệt được |
| Local Search cải thiện +10-20% | Tối ưu cục bộ bù đắp sai sót của NDSD |
| Hiệu năng giảm mạnh ε > 10% | Nhiễu quá lớn, cấu trúc bị phá vỡ hoàn toàn |

### 6.2 Kết Luận Kép Của Bài Báo

**Kết luận 1 (De-anonymization):**
> Kết hợp NDSD + Local Search de-anonymize hiệu quả với nhiễu ≤ 10%

**Kết luận 2 (Mô hình đồ thị):**
> Barabási-Albert và Holme-Kim là mô hình phù hợp nhất với mạng XH thực tế

---

## 7. TÓM TẮT CÔNG THỨC QUAN TRỌNG

```
1. NDS(v, G) = sorted([deg(u) for u in N(v)], reverse=True)

2. dist_NDS(u, v) = Σᵢ |NDS(u)[i] - NDS(v)[i]|

3. Bài toán NDSD:
   σ_NDSD = argmin Σᵢ dist_NDS(nodes_H[i], nodes_G[σ(i)])
             σ

4. score(σ, G, H) = |{(u,v) ∈ E(H) : (σ(u), σ(v)) ∈ E(G)}|

5. Điều kiện chấp nhận swap:
   score(Swap(σ, u, v)) > score(σ)

6. Độ phức tạp:
   - NDSD:        O(n⁴)
   - Local Search: O(n⁵)
   - Kết hợp:     O(n⁵)
```
