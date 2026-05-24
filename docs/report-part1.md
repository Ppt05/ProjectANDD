# BÁO CÁO MIDTERM — MÔN AN NINH DI ĐỘNG
# Đề tài: Phi Ẩn Danh Hóa Mạng Xã Hội Sử Dụng Thông Tin Cấu Trúc
# Bài báo: "Deanonymizing Social Networks Using Structural Information" — IJCAI-2019
# Tác giả bài báo: Ioannis Caragiannis & Evi Tsitsoka — Đại học Patras, Hy Lạp

---

**Môn học:** An Ninh Di Động
**Giảng viên:** TS. Lê Thị Hợi
**Nhóm:** [Điền tên nhóm]
**Thành viên:** [Điền tên các thành viên]

---

# MỤC LỤC

1. Giới thiệu
2. Cơ sở lý thuyết
3. Thuật toán đề xuất trong bài báo
4. Mô hình đồ thị thực nghiệm
5. Thực nghiệm và kết quả *(Phần 2)*
6. Đề xuất cải tiến *(Phần 2)*
7. Liên hệ an ninh di động *(Phần 2)*
8. Kết luận *(Phần 2)*
9. Tài liệu tham khảo *(Phần 2)*

---

## 1. GIỚI THIỆU

### 1.1 Bối cảnh

Trong kỷ nguyên số, các mạng xã hội (Facebook, Twitter, LinkedIn) lưu trữ lượng thông tin khổng lồ về quan hệ giữa người dùng. Để bảo vệ quyền riêng tư, các tổ chức thường **ẩn danh hóa** (anonymize) dữ liệu trước khi chia sẻ cho bên thứ ba — tức là xóa đi các thông tin định danh trực tiếp như tên, ID, email.

Tuy nhiên, việc xóa nhãn danh tính **không đồng nghĩa** với việc bảo vệ quyền riêng tư. Lý do: **cấu trúc quan hệ** (topology) giữa các node trong mạng vẫn được giữ nguyên, và bản thân cấu trúc này chứa đủ thông tin để khôi phục lại danh tính.

### 1.2 Tiền đề nghiên cứu

Nghiên cứu về phi ẩn danh hóa mạng xã hội trở nên phổ biến từ công trình tiên phong của **Narayanan và Shmatikov (2009)** tại hội nghị IEEE S&P. Họ chứng minh rằng việc ẩn danh hóa dữ liệu mạng xã hội thông thường có thể bị **vi phạm nghiêm trọng** bằng cách khai thác cấu trúc đồ thị.

Một hướng nghiên cứu khác là của **Backstrom et al. (2007)**, giả định kẻ tấn công có thể sửa đổi mạng trước khi nó được phát hành (sybil attack). Cách tiếp cận của bài báo này **khác hoàn toàn** — không cần sybil nodes, không cần seed nodes, chỉ dùng **thông tin cấu trúc thuần túy**.

Về mặt lý thuyết, bài toán liên quan mật thiết đến **Graph Isomorphism** — bài toán đã nhận được nhiều sự chú ý nhờ kết quả đột phá của **Babai (2016)** đạt thời gian quasi-polynomial. Tuy nhiên, trong thực tế, hai mạng xã hội không bao giờ giống nhau hoàn toàn, nên cần giải **phiên bản tối ưu hóa** của graph isomorphism.

### 1.3 Câu hỏi nghiên cứu

> **"Liệu có thể khôi phục danh tính người dùng trong mạng ẩn danh chỉ bằng cấu trúc đồ thị, khi mạng bị nhiễu (xóa node, thay đổi cạnh)?"**

Bài báo trả lời câu hỏi này bằng hai thuật toán:
1. **NDSD** — khai thác ý tưởng từ Babai et al. (1980) về dãy bậc láng giềng
2. **Local Search** — cải thiện kết quả bằng hoán đổi cục bộ, với phân tích formal về thời gian chạy

---

## 2. CƠ SỞ LÝ THUYẾT

### 2.1 Định nghĩa bài toán

Cho hai đồ thị:
- **G**: Đồ thị có danh tính (eponymous social network) — n node được đánh số [1..n]
- **H**: Đồ thị ẩn danh (anonymous social network) — n' node, với n' ≤ n

Định nghĩa hàm **pseudobijection** `F: V(G) → V(H) ∪ {0}`:
- Mỗi node u ∈ V(G) được ánh xạ đến **một node duy nhất** trong V(H) hoặc **dummy node 0**
- Với mỗi node v ∈ V(H), **tồn tại đúng một** node u ∈ V(G) sao cho F(u) = v
- Có `n - n'` nodes của G được ánh xạ đến dummy node 0 (nodes đã bị xóa khỏi H)

### 2.2 Quá trình tạo đồ thị ẩn danh

Đồ thị H được tạo từ G qua 3 bước:
1. **Bước 1:** Áp dụng một hoán vị (permutation) lên các node của G
2. **Bước 2:** Xóa một số node (node noise δ — tỷ lệ nodes bị xóa)
3. **Bước 3:** Thay đổi một số cạnh (edge noise ε — xác suất mỗi cặp node bị đổi trạng thái cạnh)

Quá trình này định nghĩa một pseudobijection thực sự **F*: V(G) → V(H) ∪ {0}** (ground truth).

### 2.3 Hàm mục tiêu

Mục tiêu của bài toán là: cho G và H, tìm pseudobijection F **khôi phục F* chính xác nhất**. Performance được đo bằng:

```
Performance(F) = Σ_{u∈V(G)} 𝟙{F*(u) ≠ 0 và F(u) = F*(u)}
```

Tức là: đếm số node u mà:
- u **có mặt** trong H (F*(u) ≠ 0)
- Thuật toán khớp **đúng** u (F(u) = F*(u))

### 2.4 Ký hiệu

| Ký hiệu | Định nghĩa |
|----------|-----------|
| V(G), E(G) | Tập node và tập cạnh của đồ thị G |
| n = \|V(G)\|, n' = \|V(H)\| | Số node của G và H |
| F: V(G) → V(H) ∪ {0} | Pseudobijection |
| F* | Pseudobijection ground truth |
| deg_u | **Neighbor Degree Sequence (NDS)** của node u — dãy bậc các láng giềng, sắp giảm dần |
| diff(u,v) | Khoảng cách L1 giữa hai NDS (Equation 1 trong paper) |
| adjF(u,v) | = 1 nếu (u,v) ∈ E(G) **và** (F(u),F(v)) ∈ E(H); = 0 nếu ngược lại |
| qualF(u) | = Σ_{v∈N_G(u)} adjF(u,v) — **chất lượng** node u trong mapping F |
| Φ(F) | = Σ_{u∈V(G)} qualF(u) — **tổng chất lượng** toàn cục |
| δ | Node noise — tỷ lệ node bị xóa (0 ≤ δ ≤ 0.20) |
| ε | Edge noise — xác suất đổi trạng thái cạnh (0 ≤ ε ≤ 0.10) |

### 2.5 Độ khó tính toán

Khi δ = 0 và ε = 0, bài toán trở thành **Graph Isomorphism** — bài toán nổi tiếng trong lý thuyết độ phức tạp. Babai (2016) đã chứng minh Graph Isomorphism nằm trong thời gian quasi-polynomial (`exp(polylog(n))`). Trong thực tế, bài toán này được giải hiệu quả bởi các công cụ như nauty (McKay và Piperno, 2014).

Tuy nhiên, phiên bản tối ưu hóa (maximize edge matches) là **NP-khó** trong trường hợp tổng quát. Do đó, bài báo thiết kế các **heuristic hiệu quả** thay vì thuật toán chính xác.

---

## 3. THUẬT TOÁN ĐỀ XUẤT TRONG BÀI BÁO

### 3.0 Khái niệm nền tảng: Pseudobijection và Dummy Nodes

Bài báo định nghĩa ánh xạ **F: V(G) → V(H) ∪ {0}** gọi là **pseudobijection**:
- Mỗi node u ∈ V(G) được ánh xạ đến một node **duy nhất** trong V(H) hoặc **dummy node 0**
- Với mỗi node v ∈ V(H), tồn tại **đúng một** u ∈ V(G) sao cho F(u) = v
- Chính xác `n - n'` node của G sẽ ánh xạ đến 0

**Ý nghĩa thực tế:** Nếu |V(G)| = 5 và |V(H)| = 4, ta thêm **1 dummy node** vào H. Khi tìm matching, node G nào khớp với dummy → node đó đã bị xóa khỏi H.

### 3.1 Thuật toán NDSD (Neighbor Degree Sequence Difference)

#### 3.1.1 Ý tưởng cốt lõi — NDS từ Babai et al. (1980)

Babai et al. (1980) quan sát rằng với đồ thị Erdős-Rényi G_{n,1/2}, **dãy bậc các láng giềng** (Neighbor Degree Sequence) của mỗi node là **duy nhất với xác suất cao**. Tính chất này mở rộng cho các giá trị p khác (Bollobás 2001, Czajka và Pandurangan 2008).

**Neighbor Degree Sequence (NDS)** của node u:
```
deg_u = (d₁, d₂, ..., d_k)  với d₁ ≥ d₂ ≥ ... ≥ d_k
```
Trong đó d_i là bậc (degree) của láng giềng thứ i của u, sắp xếp **giảm dần**.

#### 3.1.2 Khoảng cách diff (Equation 1)

Cho hai node u ∈ V(G) và v ∈ V(H), khoảng cách NDS được định nghĩa:

```
diff(u, v) = Σ_{i=1}^{max(|deg_u|, |deg_v|)} |deg_u(i) - deg_v(i)|    (Eq. 1)
```

Nếu hai dãy có độ dài khác nhau, dãy ngắn hơn được đệm thêm số 0.

#### 3.1.3 Quy trình NDSD

1. **Tính NDS** cho mỗi node trong G và H
2. **Thêm dummy nodes:** Thêm `n - n'` dummy nodes vào H. Mỗi dummy node có deg = [] (dãy rỗng), nên diff(u, dummy) = Σ deg_u(i)
3. **Xây cost matrix:** Ma trận C kích thước n×n, với C[u][v] = diff(u, v)
4. **Hungarian Algorithm:** Tìm perfect matching tối thiểu hóa tổng cost
5. **Kết quả:** Node G khớp với dummy → F(u) = 0; khớp với v ∈ V(H) → F(u) = v

#### 3.1.4 Ví dụ minh họa (dựa trên Figure 1 của bài báo)

Giả sử G có 5 nodes {1,2,3,4,5} và H có 4 nodes {a,b,c,d}:
- Ta thêm **1 dummy node e** vào H → H' = {a,b,c,d,e}
- Tính diff cho mọi cặp (u∈G, v∈H') → ma trận 5×5
- Hungarian tìm matching tối ưu
- Nếu node 2 khớp với dummy e → F(2) = 0 (node 2 đã bị xóa khỏi H)

#### 3.1.5 Độ phức tạp

| Bước | Phức tạp |
|------|----------|
| Tính NDS cho n nodes | O(n × Δ) ≈ O(n²) |
| Tính diff cho n² cặp | O(n² × Δ) ≈ O(n³) |
| Hungarian Algorithm | O(n³) |
| **Tổng** | **O(n³)** |

*Ghi chú: Bài báo ghi O(n⁴) vì xét worst-case khi Δ ≈ n.*

### 3.2 Thuật toán Local Search (Algorithm 1)

#### 3.2.1 Ý tưởng

Sau khi NDSD cho kết quả ban đầu F₀, Local Search **cải thiện** bằng cách thử hoán đổi (swap) từng cặp node. Nếu swap cải thiện chất lượng → chấp nhận.

#### 3.2.2 Các hàm đánh giá

**adjF(u, v):** Kiểm tra cạnh có được bảo toàn qua mapping F hay không
```
adjF(u, v) = 1  nếu (u,v) ∈ E(G) VÀ (F(u), F(v)) ∈ E(H)
           = 0  nếu ngược lại
```

**qualF(u):** Chất lượng ánh xạ của node u — đếm số láng giềng trong G mà cạnh được bảo toàn trong H
```
qualF(u) = Σ_{v ∈ N_G(u)} adjF(u, v)
```

**Φ(F):** Tổng chất lượng toàn cục
```
Φ(F) = Σ_{u ∈ V(G)} qualF(u)
```

#### 3.2.3 Algorithm 1 — Pseudocode chính xác từ bài báo

```
Algorithm 1: Local Search
─────────────────────────
Input: Đồ thị G, H; pseudobijection ban đầu F₀
F ← F₀

repeat
  improved ← false
  for each u₁ ∈ V(G) do
    for each u₂ ∈ V(G), u₂ ≠ u₁ do
      Đặt F' = F nhưng swap: F'(u₁) = F(u₂), F'(u₂) = F(u₁)
      
      if qualF'(u₁) + qualF'(u₂) > qualF(u₁) + qualF(u₂) then
        F ← F'
        improved ← true
      end if
    end for
  end for
until improved = false

Output: Pseudobijection F
```

**Điều kiện swap:** Chấp nhận nếu **tổng chất lượng hai node** sau swap **tăng nghiêm ngặt**:
```
qualF'(u₁) + qualF'(u₂) > qualF(u₁) + qualF(u₂)
```

#### 3.2.4 Theorem 1 — Giới hạn số iterations

> **Theorem 1 (Caragiannis & Tsitsoka, 2019):**
> Algorithm 1 thực hiện tối đa **O(n²)** swap operations.

**Chứng minh (sketch):**
- Mỗi swap được chấp nhận làm **Φ(F) tăng nghiêm ngặt** ít nhất 1 đơn vị
- Φ(F) ≤ 2|E(G)| (vì mỗi cạnh đóng góp tối đa 2 vào Φ — mỗi đầu 1)
- |E(G)| ≤ n(n-1)/2 = O(n²)
- Vậy số lần swap ≤ O(n²) ∎

#### 3.2.5 Độ phức tạp

| Thành phần | Phức tạp |
|------------|----------|
| Mỗi iteration: scan O(n²) cặp | O(n²) |
| Mỗi swap check: tính qualF' | O(Δ) — xét láng giềng |
| Số iterations tối đa (Theorem 1) | O(n²) |
| **Tổng** | **O(n⁴ × Δ) ≈ O(n⁵)** |

### 3.3 Pipeline kết hợp: NDSD → Local Search

```
Input: G (eponymous), H (anonymous)
         │
         ▼
┌─────────────────────┐
│ Bước 1: NDSD        │  Tính NDS, cost matrix, Hungarian
│ Kết quả: F₀         │  Matching ban đầu (O(n⁴))
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Bước 2: Local Search│  Swap cặp node nếu qualF tăng
│ Cải tiến: F₀ → F    │  Lặp đến convergence (O(n⁵))
└────────┬────────────┘
         │
         ▼
Output: F — pseudobijection tối ưu
```

**Tại sao kết hợp?**
- NDSD cho kết quả khá tốt nhưng có sai số do nhiễu
- Local Search bắt đầu từ nghiệm tốt (F₀ từ NDSD) → sửa sai hiệu quả
- Nếu bắt đầu từ nghiệm ngẫu nhiên → Local Search bị kẹt local optimum

---

## 4. MÔ HÌNH ĐỒ THỊ THỰC NGHIỆM

Bài báo thực nghiệm trên cả **mạng xã hội thật** và **đồ thị ngẫu nhiên**.

### 4.1 Mạng xã hội thật

| Mạng | Nguồn | Số nodes | Mô tả |
|------|-------|----------|-------|
| ego-Facebook | SNAP (Leskovec & Krevl, 2014) | 4,039 | Mạng bạn bè Facebook |
| Amherst41 | Network Repository (Rossi & Ahmed, 2015) | 2,235 | Mạng sinh viên Amherst College |
| Wellesley22 | Network Repository | 2,970 | Mạng sinh viên Wellesley College |

### 4.2 Mô hình đồ thị ngẫu nhiên

| Mô hình | Đặc trưng | Phù hợp MXH? |
|---------|-----------|--------------|
| **Erdős-Rényi (ER)** | Mỗi cạnh xuất hiện với xác suất p; phân phối bậc đồng đều | ❌ Không — thiếu hub, thiếu clustering |
| **Watts-Strogatz (WS)** | Small-world: đường kính nhỏ, clustering cao | ❌ Không — phân phối bậc đồng đều |
| **Barabási-Albert (BA)** | Scale-free: "rich-get-richer", phân phối bậc power-law | ✅ Có — mô phỏng tốt hub/influencer |
| **Holme-Kim (HK)** | BA + clustering cao (triad formation) | ✅ Có — BA + "bạn chung" |

**Tại sao BA và HK phù hợp?**
- Mạng xã hội thật có **phân phối bậc power-law** (nhiều người ít bạn, ít người nhiều bạn)
- BA tạo ra tính chất này qua cơ chế **preferential attachment** (Barabási & Albert, 1999)
- HK bổ sung **clustering** (Holme & Kim, 2002) — trong MXH thật, "bạn của bạn thường cũng là bạn"

**Tại sao ER và WS không phù hợp?**
- ER: Phân phối bậc Poisson → tất cả nodes "giống nhau" → NDS không phân biệt được
- WS: Bậc gần đồng đều → cùng vấn đề

*→ Tiếp tục Chương 5-9 trong `report-part2.md`*
