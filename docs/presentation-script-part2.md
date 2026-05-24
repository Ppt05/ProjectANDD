# KỊCH BẢN THUYẾT TRÌNH CHI TIẾT — PHẦN 2
# Slide 15–22: Cải tiến + An ninh di động + Kết luận
# Tiếp nối từ `presentation-script-part1.md`

---

# ═══════════════════════
# SLIDE 15 — HẠN CHẾ (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Trước khi trình bày cải tiến, hãy hiểu tại sao cần cải tiến.

**Hạn chế 1 của NDSD:** Thuật toán chỉ dùng thông tin **1-hop** — tức chỉ xét bậc của láng giềng trực tiếp. Hai node có thể có cùng NDS nhưng cấu trúc xung quanh khác hoàn toàn. Ví dụ: node A và B cùng có 3 bạn bậc [5, 3, 1], nhưng bạn của bạn — tức 2-hop — hoàn toàn khác. NDSD không phân biệt được.

**Hạn chế 2 của Local Search:** Thuật toán chỉ chấp nhận swap khi qualF tăng nghiêm ngặt. Nếu rơi vào **local optimum** — tức không swap nào cải thiện — thuật toán dừng sớm, dù nghiệm chưa tối ưu toàn cục.

Hai hạn chế này càng nghiêm trọng khi **noise cao** (ε ≥ 10%)."

> ⚠️ **Lưu ý:** Từ slide này trở đi là **phần cải tiến của nhóm — không có trong bài báo gốc**.

**[DẪN]:** "Nhóm đề xuất 2 cải tiến tương ứng: ENDSD giải quyết hạn chế 1, ILS giải quyết hạn chế 2."

---

# ═══════════════════════
# SLIDE 16 — ENDSD (⏱️ 2.5 phút)
# ═══════════════════════

**[NÓI]:**
"Cải tiến đầu tiên: **ENDSD** — Extended Neighbor Degree Sequence Difference.

Ý tưởng: thay vì chỉ nhìn 1-hop, ta mở rộng sang **2-hop** — tức bạn của bạn. Fingerprint mới gồm 2 phần:
- Phần 1: NDS 1-hop giống NDSD gốc
- Phần 2: NDS 2-hop nhân với trọng số α = 0.5

Tại sao α = 0.5? Vì 2-hop bị ảnh hưởng bởi noise nhiều hơn 1-hop — mỗi cạnh sai ở 1-hop sẽ lan ra 2-hop. Nên ta giảm trọng số để tránh nhiễu.

Kết quả: fingerprint phong phú hơn → phân biệt node tốt hơn → Hungarian cho matching chính xác hơn, đặc biệt ở mức noise cao."

**[DẪN]:** "Cải tiến thứ hai giải quyết vấn đề local optimum."

---

# ═══════════════════════
# SLIDE 17 — ILS (⏱️ 2.5 phút)
# ═══════════════════════

**[NÓI]:**
"Cải tiến thứ hai: **ILS** — Iterated Local Search.

Vấn đề: Local Search gốc dừng khi không swap nào cải thiện — nhưng nghiệm có thể chưa tối ưu toàn cục.

Giải pháp: sau khi Local Search bị kẹt, ta **xáo trộn** nghiệm bằng cách swap ngẫu nhiên k=3 cặp node — gọi là perturbation — rồi chạy lại Local Search từ vị trí mới. Lặp lại R=4 lần, giữ nghiệm tốt nhất.

Hình dung như đang leo núi: Local Search leo đến đỉnh gần nhất rồi dừng. ILS thì nhảy sang ngọn núi khác và leo lại — có thể tìm được đỉnh cao hơn.

Kết quả: ILS khám phá nhiều vùng trong không gian nghiệm → tìm được nghiệm tốt hơn Local Search thuần túy."

**[DẪN]:** "Kết quả cải tiến so với baseline như thế nào?"

---

# ═══════════════════════
# SLIDE 18 — KẾT QUẢ CẢI TIẾN (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Bảng này so sánh Baseline (NDSD + LS) với Improved (ENDSD + ILS) trên mô hình BA:

- Ở ε = 0%: cả hai đều gần 100% — không cần cải tiến.
- Ở ε = 10%: Baseline đạt 80%, Improved đạt 87% — cải thiện 7 điểm.
- Ở ε = 15-20%: cải thiện lên đến **9 điểm phần trăm**.

Xu hướng rõ ràng: cải tiến **nhiều nhất ở mức noise cao**. Điều này hợp lý vì:
- ENDSD tạo fingerprint phong phú hơn → NDSD ban đầu chính xác hơn
- ILS thoát local optimum → tìm nghiệm tốt hơn

Trên biểu đồ, vùng màu đỏ giữa hai đường chính là phần cải tiến."

**[DẪN]:** "Giờ hãy liên hệ tất cả những điều này với an ninh di động."

---

# ═══════════════════════
# SLIDE 19 — THREAT MODEL (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Bài toán phi ẩn danh hóa có tác động trực tiếp đến an ninh di động.

Kịch bản: Kẻ tấn công có mạng xã hội công khai — ví dụ Facebook. Nạn nhân tham gia một ứng dụng ẩn danh — ví dụ forum darknet. Bằng thuật toán NDSD + Local Search, kẻ tấn công khớp cấu trúc hai mạng và biết ai là ai trên app ẩn danh.

Trên thiết bị di động, có nhiều nguồn đồ thị:
- **Danh bạ + lịch sử cuộc gọi** → đồ thị liên lạc
- **Bluetooth / WiFi proximity** → đồ thị thiết bị gần nhau
- **Metadata ứng dụng** — dù nội dung được mã hóa, pattern ai liên lạc ai vẫn bị lộ

Cross-referencing nhiều đồ thị càng làm tăng hiệu quả tấn công."

**[DẪN]:** "Vậy phòng thủ như thế nào?"

---

# ═══════════════════════
# SLIDE 20 — PHÒNG THỦ (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Từ kết quả bài báo, ta rút ra được mức noise cần thiết để phòng thủ:

**Edge perturbation:** Thêm/xóa cạnh ngẫu nhiên. Từ thực nghiệm: cần ε > 10-15% để accuracy giảm đáng kể. Nhưng ε quá cao sẽ làm hỏng utility của dữ liệu.

**Differential Privacy:** Thêm noise có kiểm soát, đảm bảo privacy bounds toán học. Đây là hướng mạnh nhất nhưng phức tạp.

**K-anonymity cho đồ thị:** Đảm bảo mỗi node có ít nhất k nodes 'giống hệt' về cấu trúc. Khó áp dụng trong thực tế.

**Tối thiểu hóa dữ liệu:** Nguyên tắc đơn giản — không chia sẻ cấu trúc đồ thị nếu không cần thiết.

**Bài học lớn nhất:** Ẩn danh hóa — tức xóa tên — là **chưa đủ**. Cấu trúc đồ thị bản thân nó đã chứa đủ thông tin để re-identify."

**[DẪN]:** "Tóm lại những gì nhóm đã trình bày."

---

# ═══════════════════════
# SLIDE 21 — KẾT LUẬN (⏱️ 1.5 phút)
# ═══════════════════════

**[NÓI]:**
"Tổng kết 3 điểm chính:

**Một:** Bài báo đề xuất pipeline NDSD + Local Search hiệu quả cao trên mạng scale-free. Chịu được noise lên đến 10%. Có phân tích formal — Theorem 1 chứng minh O(n²) iterations.

**Hai:** Nhóm đề xuất cải tiến ENDSD (2-hop fingerprint) và ILS (Iterated Local Search), nâng accuracy thêm 7-9 điểm ở mức noise cao.

**Ba:** Bài toán này có tác động trực tiếp đến an ninh di động. Metadata trên thiết bị tạo ra nhiều loại đồ thị, và thuật toán de-anonymization có thể khai thác chúng.

Hướng phát triển: mở rộng sang mạng lớn, kết hợp thông tin thuộc tính node, và tìm mức noise tối thiểu bảo vệ privacy."

**[DẪN]:** "Cuối cùng, tài liệu tham khảo."

---

# ═══════════════════════
# SLIDE 22 — TLTK (⏱️ 30s)
# ═══════════════════════

**[NÓI]:**
"Đây là danh sách tài liệu tham khảo chính. Bài báo gốc của Caragiannis và Tsitsoka 2019 là nguồn chính. Các tham khảo khác bao gồm công trình tiên phong của Narayanan 2009, ý tưởng NDS từ Babai 1980, và các mô hình đồ thị.

Cảm ơn thầy/cô và các bạn đã lắng nghe. Nhóm sẵn sàng trả lời câu hỏi."

---

## TỔNG THỜI GIAN PHẦN 2: ~15 phút

| Nhóm slide | Thời gian |
|-----------|-----------|
| Cải tiến (15-18) | ~9 phút |
| An ninh DĐ (19-20) | ~4 phút |
| Kết luận (21-22) | ~2 phút |

## TỔNG THỜI GIAN TOÀN BÀI: ~41 phút

---

## PHỤ LỤC: CÂU HỎI DỰ ĐOÁN + TRẢ LỜI

### Q1: "Tại sao không dùng graph isomorphism algorithms (nauty/VF2) thay vì NDSD?"
**A:** Graph isomorphism chỉ hoạt động khi hai đồ thị giống **hoàn toàn**. Trong bài toán này, H là noisy subgraph — có node bị xóa, cạnh bị đổi — nên cần phiên bản tối ưu hóa (maximize edge matches), không phải decision version.

### Q2: "Tại sao qualF chứ không phải score toàn cục?"
**A:** qualF(u) tính **per-node** — cho phép đánh giá cục bộ. Khi swap u₁ và u₂, chỉ cần tính lại qualF cho 2 node đó (O(Δ)) thay vì score toàn cục (O(m)). Đây là thiết kế thông minh giúp mỗi swap check rất nhanh.

### Q3: "ENDSD alpha = 0.5 — tại sao không tune?"
**A:** alpha = 0.5 là giá trị hợp lý mặc định. 2-hop bị noise nhiều hơn 1-hop nên cần trọng số thấp hơn. Có thể tune nhưng kết quả không nhạy cảm lắm với alpha trong khoảng [0.3, 0.7].

### Q4: "ILS với R=4, k=3 — tối ưu chưa?"
**A:** R=4 và k=3 là cân bằng giữa chất lượng và thời gian chạy. R lớn hơn → tốt hơn nhưng chậm hơn. k=3 đủ để thoát local optimum mà không phá hỏng nghiệm.

### Q5: "Bài báo này liên quan gì đến an ninh di động?"
**A:** Thiết bị di động tạo nhiều loại đồ thị (contact, proximity, metadata). Kẻ tấn công có thể dùng thuật toán này để re-identify người dùng trên ứng dụng ẩn danh. Đây là mối đe dọa thực tế.

### Q6: "Có thể áp dụng cho mạng có hướng (directed graph) không?"
**A:** Bài báo chỉ xét đồ thị vô hướng. Mở rộng sang directed graph cần sửa NDS (chia thành in-degree sequence và out-degree sequence) và sửa adjF. Đây là hướng phát triển.
