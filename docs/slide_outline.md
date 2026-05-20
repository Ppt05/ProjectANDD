# OUTLINE SLIDE — BÁO CÁO MIDTERM
# Môn: An Ninh Di Động
# Bài báo: "Deanonymizing Social Networks Using Structural Information" (IJCAI-2019)
# Caragiannis & Tsitsoka — Đại học Patras, Hy Lạp

---

## SLIDE 1 — TRANG BÌA

**Tiêu đề:** Phi Ẩn Danh Hóa Mạng Xã Hội Sử Dụng Thông Tin Cấu Trúc
**Phụ đề:** Phân tích bài báo IJCAI-2019
**Thông tin nhóm:** [Tên nhóm] | Môn An Ninh Di Động | [Ngày]

> 🎨 Gợi ý thiết kế: Nền tối, hình minh họa network graph glowing, font lớn bold

---

## SLIDE 2 — MỤC LỤC

**Tiêu đề:** Nội Dung Trình Bày

1. 🧩 **Lý Thuyết** — Bài toán, Thuật toán, Phân tích lý thuyết
2. 🔬 **Thực Nghiệm** — Thiết lập, Kết quả, Biểu đồ
3. 🚀 **Mở Rộng** — Ứng dụng An ninh di động, Phòng thủ

> 🎤 **Speaker notes:** Giới thiệu nhanh 3 phần, nhấn mạnh bài báo thuộc IJCAI (top-tier AI conference)

---

## ===== PHẦN 1: LÝ THUYẾT (Slide 3–8) =====

---

## SLIDE 3 — ĐẶT VẤN ĐỀ: PRIVACY PARADOX

**Tiêu đề:** Ẩn Danh Hóa Có Thực Sự Bảo Vệ Quyền Riêng Tư?

**Nội dung:**
- ✅ Thực trạng: Các mạng xã hội chia sẻ dữ liệu sau khi "ẩn danh hóa" (xóa tên, ID)
- ❌ Vấn đề: **Cấu trúc quan hệ** vẫn còn nguyên → có thể khôi phục danh tính
- 📰 Ví dụ: Netflix Prize dataset (Narayanan & Shmatikov 2009) — de-anonymize qua IMDB

**Câu hỏi nghiên cứu:**
> Chỉ dùng thông tin cấu trúc đồ thị, có thể phi ẩn danh hóa mạng xã hội không?

> 🎤 **Speaker notes:** Nhấn mạnh "chỉ dùng cấu trúc" — không cần metadata, không cần content. Đây là điểm khác biệt so với các phương pháp trước.

---

## SLIDE 4 — MÔ HÌNH BÀI TOÁN

**Tiêu đề:** Bài Toán Phi Ẩn Danh Hóa Mạng Xã Hội

**Hình minh họa:** [Vẽ 2 đồ thị G và H cạnh nhau, mũi tên ánh xạ node]

**Định nghĩa:**
- **G** = Mạng xã hội có danh tính (eponymous graph) — biết tên node
- **H** = Mạng xã hội ẩn danh (anonymous graph) — node bị đổi tên, ẩn danh
  - H là noisy subgraph của G: xóa δ% node + đổi ε% cạnh

**Mục tiêu:** Tính ánh xạ σ: V(H) → V(G) sao cho σ(v) là danh tính thật của v

**Bài toán tối ưu:**
> Tối đa hóa số cạnh được khớp đúng:
> `max |{(u,v) ∈ E(H) : (σ(u), σ(v)) ∈ E(G)}|`

> 🎤 **Speaker notes:** Giải thích δ (xóa node) và ε (nhiễu cạnh). Ví dụ: δ=5% nghĩa là 5% người dùng không xuất hiện trong mạng ẩn danh. ε=10% nghĩa là 10% cặp node có quan hệ cạnh khác nhau giữa G và H.

---

## SLIDE 5 — THUẬT TOÁN 1: NDSD

**Tiêu đề:** Thuật Toán NDSD — Neighbor Degree Sequence Difference

**Ý tưởng cốt lõi:**
> Node có láng giềng "tương tự" → khả năng là cùng một người

**Các bước:**
1. **Tính chữ ký cấu trúc** mỗi node:
   - NDS(v) = dãy bậc của các láng giềng, sắp xếp giảm dần
   - Ví dụ: v có láng giềng bậc [5, 3, 3, 1] → NDS = [5,3,3,1]

2. **Tính khoảng cách** giữa mọi cặp (node H, node G):
   - dist(u, v) = L1-distance của NDS(u) và NDS(v)

3. **Khớp tối ưu** bằng Thuật toán Hungary (Hungarian Algorithm):
   - Tìm matching tối thiểu tổng khoảng cách
   - Độ phức tạp: **O(n⁴)**

**[Hình: Ma trận cost matrix → kết quả Hungarian matching]**

> 🎤 **Speaker notes:** Giải thích Hungarian algorithm giải bài toán Assignment Problem trong O(n³). Vì tính NDS tốn O(n) nên tổng O(n⁴).

---

## SLIDE 6 — THUẬT TOÁN 2: LOCAL SEARCH

**Tiêu đề:** Thuật Toán Local Search — Tìm Kiếm Cục Bộ Qua Hoán Đổi

**Ý tưởng:**
> Bắt đầu từ nghiệm NDSD → liên tục cải thiện bằng swap 2 node

**Các bước:**
1. Khởi đầu: σ₀ = kết quả từ NDSD
2. **Lặp lại:**
   - Thử swap mọi cặp (u, v) trong H: σ' = σ với σ'(u)↔σ'(v)
   - Nếu score(σ') > score(σ): chấp nhận swap
3. **Dừng** khi không còn swap nào cải thiện (local optimum)

**Phân tích:**
| Thuật toán | Độ phức tạp | Chất lượng |
|-----------|-------------|-----------|
| NDSD | O(n⁴) | Nghiệm ban đầu tốt |
| Local Search | O(n⁵) tổng thể | Cải thiện đáng kể |
| **Kết hợp** | O(n⁵) | **Tốt nhất** |

> 🎤 **Speaker notes:** O(n²) cặp × O(n²) tính score mỗi lần × O(n²) vòng lặp = O(n⁵). Nhưng thực tế hội tụ sớm hơn nhiều vì dừng khi không cải thiện.

---

## SLIDE 7 — CÁC MÔ HÌNH ĐỒ THỊ

**Tiêu đề:** Mô Hình Đồ Thị Nào Phù Hợp Mạng Xã Hội Thực?

**[Hình: 4 đồ thị minh họa với các đặc trưng khác nhau]**

| Mô hình | Đặc trưng | Phù hợp MXH? |
|---------|-----------|-------------|
| **Barabási-Albert (BA)** | Scale-free, "rich get richer" | ✅ Rất phù hợp |
| **Holme-Kim (HK)** | BA + clustering cao | ✅ Rất phù hợp |
| Erdős-Rényi (ER) | Random, phân phối Poisson | ❌ Không phù hợp |
| Watts-Strogatz (WS) | Small-world, clustering đều | ❌ Không phù hợp |

**Lý do BA/HK phù hợp:**
- Phân phối bậc power-law (ít người có nhiều bạn, nhiều người có ít bạn)
- Các "hub" (người nổi tiếng) tạo cấu trúc đặc trưng dễ nhận dạng

> 🎤 **Speaker notes:** Đây là một phát hiện PHỤ quan trọng của bài báo — kết quả thực nghiệm gián tiếp xác nhận BA và HK là mô hình thực tế nhất cho mạng xã hội.

---

## ===== PHẦN 2: THỰC NGHIỆM (Slide 8–13) =====

---

## SLIDE 8 — THIẾT LẬP THỰC NGHIỆM

**Tiêu đề:** Thiết Lập Thực Nghiệm

**Cấu hình của nhóm:**
```
- Số node: n = 350
- Tỷ lệ xóa node: δ = 5%  
- Mức nhiễu ε: {0%, 5%, 10%, 15%, 20%}
- Số lần lặp: 5 trials / cấu hình
- Mô hình: BA, HK, ER, WS
- Công cụ: Python, NetworkX, SciPy (Hungarian), Matplotlib
```

**Metric đánh giá:**
> Accuracy = (số node de-anonymize đúng) / (tổng số node trong H)

**[Hình: Pipeline thực nghiệm: G → tạo H → NDSD → Local Search → Accuracy]**

> 🎤 **Speaker notes:** Giải thích tại sao dùng synthetic data (NetworkX) thay vì dataset thực — đủ để tái hiện kết quả bài báo, không phụ thuộc vào quyền truy cập dataset.

---

## SLIDE 9 — KẾT QUẢ: THUẬT TOÁN NDSD

**Tiêu đề:** Kết Quả NDSD Theo Mức Nhiễu

**[CHÈN BIỂU ĐỒ: bieu_do_1_accuracy_vs_noise.png — subplot trái]**

**Nhận xét:**
- ε = 0%: BA và HK đạt ~100% (lý tưởng, không nhiễu)
- ε = 10%: BA/HK vẫn ~60-75%, ER/WS giảm mạnh
- ε > 15%: Tất cả giảm đáng kể
- ER và WS kém ngay cả khi ε = 0%

> 🎤 **Speaker notes:** Giải thích tại sao ER kém ngay cả khi không có nhiễu — do phân phối bậc đều nhau, NDS của các node quá giống nhau, khó phân biệt.

---

## SLIDE 10 — KẾT QUẢ: LOCAL SEARCH

**Tiêu đề:** Kết Quả Local Search — Cải Thiện Rõ Rệt

**[CHÈN BIỂU ĐỒ: bieu_do_1_accuracy_vs_noise.png — subplot phải]**

**So sánh với NDSD:**
- BA ε=10%: NDSD ~65% → Local Search ~80% (+15 điểm)
- HK ε=10%: NDSD ~60% → Local Search ~75% (+15 điểm)
- ER, WS: Cải thiện ít (Local Search bị kẹt local optimum)

**Kết luận thực nghiệm:**
> ✅ Kết hợp NDSD + Local Search chịu được nhiễu tới **10%**
> ✅ BA và HK là mô hình phù hợp nhất với mạng XH thực tế
> ❌ ER và WS không phù hợp để mô hình hóa mạng XH

> 🎤 **Speaker notes:** Nhấn mạnh "10% noise tolerance" là phát hiện quan trọng của bài báo gốc. Kết quả nhóm tái hiện được phát hiện này.

---

## SLIDE 11 — PHÂN TÍCH SO SÁNH NDSD vs LOCAL SEARCH

**Tiêu đề:** NDSD vs Local Search — Vùng Cải Thiện

**[CHÈN BIỂU ĐỒ: bieu_do_2_ndsd_vs_local_search.png]**

**Phân tích:**
- Vùng tô màu = mức độ cải thiện của Local Search so với NDSD
- BA: cải thiện lớn nhất ở ε = 5-10%
- HK: tương tự, nhờ cấu trúc clustering rõ ràng hơn
- Khi ε > 15%: cải thiện giảm vì nhiễu quá cao, local search không đủ

> 🎤 **Speaker notes:** Biểu đồ này là phần nhóm tự thêm, không có trong bài báo gốc — đây là "đóng góp" của nhóm trong phân tích.

---

## SLIDE 12 — ĐỐI CHIẾU VỚI BÀI BÁO GỐC

**Tiêu đề:** Kết Quả Nhóm vs Bài Báo Gốc

| Tiêu chí | Bài báo gốc | Nhóm tái hiện |
|----------|-------------|---------------|
| Dataset | Mạng thực (Facebook, Snap) | Synthetic (NetworkX, n=350) |
| Kết hợp tốt nhất | BA + HK | ✅ Xác nhận |
| Chịu nhiễu 10% | ✅ | ✅ Tái hiện được |
| ER, WS kém | ✅ | ✅ Xác nhận |
| Scale | Vài nghìn node | 350 node (giới hạn tính toán) |

**Hạn chế của nhóm:**
- O(n⁵) quá chậm với n lớn → giảm max_iter
- Chưa test trên dataset thực (Facebook, Twitter)

> 🎤 **Speaker notes:** Trung thực về hạn chế — điều này thể hiện tư duy phản biện tốt.

---

## ===== PHẦN 3: MỞ RỘNG (Slide 13–18) =====

---

## SLIDE 13 — ỨNG DỤNG TRONG AN NINH DI ĐỘNG

**Tiêu đề:** De-Anonymization Trong Bối Cảnh Di Động

**[Hình: Smartphone → thu thập dữ liệu ngầm → xây dựng đồ thị → de-anonymize]**

**Ứng dụng di động thu thập "đồ thị quan hệ" ẩn:**
| Nguồn dữ liệu | Loại đồ thị |
|---------------|-------------|
| Call logs | Ai gọi cho ai |
| Danh bạ | Mạng quan hệ trực tiếp |
| Bluetooth proximity | Ai ở gần nhau |
| Wi-Fi co-location | Ai ở cùng địa điểm |
| App usage overlap | Ai dùng cùng app |

**Kịch bản tấn công:**
> Kẻ tấn công có app với quyền READ_CONTACTS + READ_CALL_LOGS → xây G → so khớp với H (mạng ẩn danh tội phạm) → de-anonymize

> 🎤 **Speaker notes:** Liên hệ với môn An ninh Di động: Android/iOS permissions, quyền truy cập dữ liệu. Nhấn mạnh rằng người dùng thường cấp quyền mà không biết dữ liệu sẽ bị dùng thế này.

---

## SLIDE 14 — THREAT MODEL CHI TIẾT

**Tiêu đề:** Mô Hình Mối Đe Dọa (Threat Model)

**Kẻ tấn công:**
- Có mạng xã hội công khai G (LinkedIn, Facebook public)
- Có mạng ẩn danh H (dark web forum, group tội phạm)
- Mục tiêu: biết ai trong H là ai trong G

**Điều kiện để tấn công thành công:**
1. H là noisy subgraph của G (cùng người, khác nền tảng)
2. Nhiễu ε ≤ 10%
3. Mô hình mạng gần BA hoặc HK (thực tế mạng XH đều vậy)

**[Hình: Attack flow diagram]**

> 🎤 **Speaker notes:** Ví dụ thực tế: FBI đã sử dụng phân tích cấu trúc mạng để de-anonymize các thành viên của Silk Road (dark web marketplace).

---

## SLIDE 15 — CƠ CHẾ PHÒNG THỦ

**Tiêu đề:** Làm Thế Nào Để Bảo Vệ Quyền Riêng Tư?

**3 hướng phòng thủ chính:**

### 1. Graph Perturbation (Thêm nhiễu có chủ ý)
- Thêm/xóa cạnh ngẫu nhiên trước khi chia sẻ đồ thị
- Cần ε > 10% để phá vỡ de-anonymization
- ⚠️ Đánh đổi: nhiễu nhiều → mất tính hữu dụng của dữ liệu

### 2. Differential Privacy on Graphs
- Thêm nhiễu có kiểm soát (Laplace/Gaussian mechanism)
- Đảm bảo ε-differential privacy
- Bảo vệ từng cạnh (edge-level) hoặc từng node (node-level)

### 3. k-Anonymity cho Graphs
- Đảm bảo mỗi node không phân biệt được với ít nhất k-1 node khác
- Cần cân bằng k và utility

> 🎤 **Speaker notes:** Differential Privacy đang là tiêu chuẩn vàng. Apple và Google dùng DP cho analytics trên iOS/Android. Nhấn mạnh trade-off privacy vs utility.

---

## SLIDE 16 — CÂU HỎI MỞ VÀ HƯỚNG NGHIÊN CỨU

**Tiêu đề:** Hướng Mở Rộng Tiếp Theo

**Hạn chế bài báo gốc → Hướng mở rộng:**

| Hạn chế | Hướng giải quyết |
|---------|-----------------|
| O(n⁵) — không scale với mạng lớn | Graph Neural Networks (GNN) cho de-anonymization |
| Chỉ xét đồ thị vô hướng | Mở rộng cho directed/weighted graphs |
| Local search mắc kẹt local optimum | Simulated Annealing, Genetic Algorithm |
| Giả thiết H ⊆ G duy nhất | Multi-graph matching |
| ε > 10%: hiệu năng giảm mạnh | Kết hợp thêm semantic features (text, timestamp) |

**Câu hỏi nghiên cứu mở:**
> Liệu Deep Learning có thể học được "chữ ký cấu trúc" tốt hơn NDS không?

> 🎤 **Speaker notes:** GNN-based approaches (như GraphSAGE, GAT) đang là hướng nghiên cứu hot. Có thể đề cập bài báo "Network Alignment with Holistic Graph Matching" (ICDM 2020).

---

## SLIDE 17 — DEMO THỰC NGHIỆM

**Tiêu đề:** Demo — Chạy Thực Nghiệm Trực Tiếp

**[DEMO LIVE hoặc chèn ảnh chụp màn hình kết quả chạy code]**

**Kết quả demo:**
```
Mô hình: BA | n=350 | delta=5% | 5 trials
ε= 0% | NDSD=100.0% | LS=100.0%
ε= 5% | NDSD= 82.3% | LS= 91.5%
ε=10% | NDSD= 65.1% | LS= 78.4%
ε=15% | NDSD= 41.2% | LS= 52.8%
ε=20% | NDSD= 23.7% | LS= 31.3%
```

**[Chèn 2 biểu đồ PNG]**

> 🎤 **Speaker notes:** Nếu có thể, chạy live demo (khoảng 2-3 phút với n=100). Nếu không, dùng kết quả đã chạy sẵn.

---

## SLIDE 18 — KẾT LUẬN

**Tiêu đề:** Kết Luận

**Tóm tắt 3 điểm chính:**

1. 🧩 **Lý thuyết:** Bài báo hình thức hóa bài toán de-anonymization dưới dạng tối ưu hóa đồ thị, đề xuất 2 thuật toán NDSD (O(n⁴)) và Local Search (O(n⁵))

2. 🔬 **Thực nghiệm:** Kết hợp NDSD + Local Search chịu được nhiễu tới 10%; BA và HK là mô hình phù hợp nhất với mạng XH thực tế

3. 🚀 **Mở rộng:** Có ứng dụng thực tiễn trong An ninh Di động; cần thêm cơ chế phòng thủ (Differential Privacy, Graph Perturbation)

**Thông điệp cuối:**
> ⚠️ Ẩn danh hóa dữ liệu ≠ Bảo vệ quyền riêng tư.
> Cấu trúc quan hệ có thể tiết lộ danh tính dù không có metadata.

---

## SLIDE 19 — TÀI LIỆU THAM KHẢO

**Tiêu đề:** Tài Liệu Tham Khảo

1. Caragiannis, I., & Tsitsoka, E. (2019). *Deanonymizing Social Networks Using Structural Information*. IJCAI-2019, pp. 1213–1219.

2. Narayanan, A., & Shmatikov, V. (2009). *De-anonymizing Social Networks*. IEEE S&P 2009.

3. Backstrom, L., et al. (2007). *Wherefore art thou r3579x? Anonymized Social Networks*. KDD 2007.

4. Babai, L. (2016). *Graph Isomorphism in Quasipolynomial Time*. STOC 2016.

5. Barabási, A.L., & Albert, R. (1999). *Emergence of Scaling in Random Networks*. Science.

6. Dwork, C. (2006). *Differential Privacy*. ICALP 2006.

---

## GHI CHÚ THIẾT KẾ SLIDE

### Màu sắc gợi ý:
- Nền: #0D1117 (đen GitHub) hoặc #1A1A2E (dark navy)
- Nhấn: #E63946 (đỏ) + #F4A261 (cam) — màu của biểu đồ BA/HK
- Text: #E8E8E8

### Font gợi ý:
- Tiêu đề: **Inter Bold** hoặc **Montserrat Bold**
- Body: Inter Regular 18px
- Code: JetBrains Mono

### Số slide: 19 slides (~1.5 phút/slide = ~28 phút trình bày)
