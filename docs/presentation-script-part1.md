# KỊCH BẢN THUYẾT TRÌNH CHI TIẾT — PHẦN 1
# Slide 1–14: Mở đầu + Lý thuyết + Thực nghiệm
# Bài báo: "Deanonymizing Social Networks Using Structural Information" (IJCAI-2019)

---

## 📌 HƯỚNG DẪN ĐỌC

| Ký hiệu | Nghĩa |
|----------|-------|
| **[NÓI]** | Lời nói — đọc/diễn khi thuyết trình |
| **[DẪN]** | Câu chuyển tiếp sang slide tiếp |
| **⏱️** | Thời gian gợi ý cho slide |

---

# ═══════════════════════
# SLIDE 1 — BÌA (⏱️ 30s)
# ═══════════════════════

**[NÓI]:**
"Xin chào thầy/cô và các bạn. Hôm nay nhóm chúng tôi sẽ trình bày về bài báo 'Deanonymizing Social Networks Using Structural Information', được công bố tại hội nghị IJCAI năm 2019 bởi hai tác giả Caragiannis và Tsitsoka từ Đại học Patras, Hy Lạp."

---

# ═══════════════════════
# SLIDE 2 — MỤC LỤC (⏱️ 1 phút)
# ═══════════════════════

**[NÓI]:**
"Bài trình bày gồm 4 phần chính:
- Phần 1, chúng tôi giải thích **bài toán** và **hai thuật toán** mà bài báo đề xuất: NDSD và Local Search.
- Phần 2, chúng tôi trình bày **kết quả thực nghiệm** — tái hiện lại bằng Python.
- Phần 3, nhóm **đề xuất cải tiến** ENDSD và ILS — đây là đóng góp riêng, không có trong bài báo gốc.
- Phần 4, chúng tôi liên hệ với **an ninh di động** — vì bài toán này có tác động trực tiếp đến quyền riêng tư trên thiết bị mobile."

**[DẪN]:** "Trước tiên, hãy bắt đầu với câu hỏi: Tại sao ẩn danh hóa lại không an toàn?"

---

# ═══════════════════════
# SLIDE 3 — HOOK (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Hãy tưởng tượng kịch bản sau: Một công ty công nghệ chia sẻ dữ liệu mạng xã hội cho một nhóm nghiên cứu. Họ đã xóa hết tên, email, số điện thoại — tức là đã ẩn danh hóa. Họ tin rằng dữ liệu hoàn toàn an toàn.

Nhưng điều mà bài báo này chứng minh là: chỉ cần **cấu trúc ai-kết-nối-với-ai** — tức là đồ thị quan hệ — ta có thể khôi phục lại danh tính với độ chính xác lên đến gần 100%.

Ý tưởng này không mới. Năm 2009, Narayanan và Shmatikov đã chứng minh điều tương tự tại IEEE S&P. Nhưng bài báo này đi xa hơn: họ **không cần seed nodes**, **không cần thông tin bổ sung** — chỉ thuần túy dùng cấu trúc đồ thị."

**[DẪN]:** "Vậy bài toán chính xác được phát biểu như thế nào? Xem slide tiếp."

---

# ═══════════════════════
# SLIDE 4 — MÔ HÌNH (⏱️ 3 phút)
# ═══════════════════════

**[NÓI]:**
"Bài toán được phát biểu như sau:

Cho hai đồ thị:
- G là mạng xã hội **có danh tính** — ta biết node nào là ai. G có n nodes.
- H là mạng xã hội **ẩn danh** — nodes đã bị xáo trộn, ta không biết ai là ai. H có n' nodes, với n' ≤ n.

H được tạo từ G qua 3 bước: Đầu tiên, hoán vị tất cả nodes. Sau đó, xóa đi δ% nodes — gọi là node noise. Cuối cùng, thay đổi ε% cạnh — gọi là edge noise.

Mục tiêu: tìm hàm F, ánh xạ mỗi node trong G đến một node trong H, hoặc đến **dummy node 0** nếu node đó đã bị xóa. Hàm F này được gọi là **pseudobijection**, ký hiệu:

`F: V(G) → V(H) ∪ {0}`

Đây là ký hiệu trung tâm của bài báo. Ví dụ: nếu G có 5 nodes và H có 4 nodes, thì có 1 node trong G ánh xạ đến dummy 0 — nghĩa là node đó đã bị xóa khỏi H."

**[DẪN]:** "Để đánh giá F tốt hay xấu, bài báo định nghĩa một số ký hiệu quan trọng."

---

# ═══════════════════════
# SLIDE 5 — KÝ HIỆU (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Có 4 ký hiệu quan trọng mà các bạn cần nhớ:

Thứ nhất: **deg_u** — Neighbor Degree Sequence, viết tắt NDS. Đây là dãy bậc của tất cả láng giềng của node u, sắp xếp giảm dần. Ví dụ node u có 3 láng giềng bậc 5, 3, 1 → deg_u = [5, 3, 1].

Thứ hai: **diff(u,v)** — khoảng cách L1 giữa hai NDS. Đây là Equation 1 trong paper. Hai node càng giống nhau thì diff càng nhỏ.

Thứ ba: **adjF(u,v)** — bằng 1 nếu cạnh (u,v) trong G được **bảo toàn** qua mapping F sang H. Nói đơn giản: nếu u và v là bạn trong G, và F(u) với F(v) cũng là bạn trong H → adjF = 1.

Thứ tư: **qualF(u)** — chất lượng ánh xạ node u. Bằng tổng adjF trên tất cả láng giềng. qualF(u) cao nghĩa là phần lớn bạn bè của u trong G đều được khớp đúng trong H."

**[DẪN]:** "Giờ xem thuật toán đầu tiên — NDSD — dùng NDS để tìm matching."

---

# ═══════════════════════
# SLIDE 6 — NDSD (⏱️ 3 phút)
# ═══════════════════════

**[NÓI]:**
"NDSD — Neighbor Degree Sequence Difference — là thuật toán đầu tiên.

Ý tưởng cốt lõi bắt nguồn từ Babai, Erdős và Selkow năm 1980. Họ quan sát rằng trong đồ thị ngẫu nhiên, dãy bậc láng giềng của mỗi node gần như **duy nhất** — tức NDS có thể dùng làm 'chữ ký' cho mỗi node.

Quy trình NDSD gồm 4 bước:
1. Tính NDS cho mỗi node trong G và H
2. Thêm n - n' dummy nodes vào H — mỗi dummy có NDS rỗng
3. Xây ma trận chi phí: C[u][v] = diff(u,v) — khoảng cách L1 giữa NDS
4. Dùng **Hungarian Algorithm** tìm matching tổng chi phí nhỏ nhất

Node G nào khớp với dummy → F(u) = 0, nghĩa là node đó đã bị xóa.

Độ phức tạp: O(n⁴) — do tính NDS là O(n²) và Hungarian cũng O(n³)."

**[DẪN]:** "Xem ví dụ cụ thể từ Figure 1 của bài báo."

---

# ═══════════════════════
# SLIDE 7 — VÍ DỤ (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Đây là ví dụ minh họa dựa trên Figure 1 của bài báo.

G có 5 nodes {1,2,3,4,5}. H có 4 nodes {a,b,c,d}. Vì G nhiều hơn H 1 node, ta thêm 1 dummy node e vào H.

Tính NDS cho từng node, rồi tính diff cho tất cả 25 cặp — ta được ma trận 5×5. Hungarian tìm matching: ví dụ F(1)=a, F(3)=b, F(4)=c, F(5)=d, và F(2)=dummy → node 2 đã bị xóa khỏi H.

Trên slide này các bạn thấy hai đồ thị G và H, với đường nối thể hiện matching."

**[DẪN]:** "NDSD cho kết quả khá tốt, nhưng có sai số. Thuật toán thứ 2 — Local Search — sẽ sửa sai."

---

# ═══════════════════════
# SLIDE 8 — LOCAL SEARCH (⏱️ 3 phút)
# ═══════════════════════

**[NÓI]:**
"Local Search là thuật toán thứ hai — Algorithm 1 trong paper.

Ý tưởng rất đơn giản: bắt đầu từ F₀ do NDSD trả về, rồi thử swap từng cặp node. Nếu swap cải thiện chất lượng → giữ lại.

Cụ thể: với mỗi cặp u₁ và u₂, ta tạo F' bằng cách swap F(u₁) và F(u₂). Rồi kiểm tra điều kiện:

**qualF'(u₁) + qualF'(u₂) > qualF(u₁) + qualF(u₂)**

Tức là: tổng chất lượng hai node **sau swap phải lớn hơn trước swap**. Nếu đúng → chấp nhận.

Điểm quan trọng: bài báo chứng minh **Theorem 1** — số lần swap tối đa là O(n²). Vì sao? Mỗi swap làm Φ(F) — tổng chất lượng toàn cục — tăng nghiêm ngặt ít nhất 1. Mà Φ(F) ≤ 2|E(G)| = O(n²). Nên tổng số swap ≤ O(n²).

Tổng độ phức tạp: O(n⁵) — mỗi iteration scan O(n²) cặp, tối đa O(n²) iterations, mỗi check O(Δ)."

**[DẪN]:** "Hai thuật toán kết hợp thành pipeline — xem tổng quan."

---

# ═══════════════════════
# SLIDE 9 — PIPELINE (⏱️ 1.5 phút)
# ═══════════════════════

**[NÓI]:**
"Pipeline hoàn chỉnh rất đơn giản:
- Bước 1: NDSD cho matching ban đầu F₀ — dùng diff, tức NDS distance
- Bước 2: Local Search cải thiện F₀ thành F — dùng qualF, tức edge preservation

Hai bước bổ sung cho nhau: NDSD nhìn 'giống ai nhất' ở mức cấu trúc tổng thể, còn Local Search kiểm tra 'cạnh nào được bảo toàn' ở mức cục bộ.

Điểm then chốt: Local Search **cần khởi đầu tốt** từ NDSD. Nếu bắt đầu từ matching ngẫu nhiên, Local Search sẽ bị kẹt ở local optimum rất tệ."

**[DẪN]:** "Trước khi xem kết quả, hãy hiểu về các mô hình đồ thị được dùng trong thực nghiệm."

---

# ═══════════════════════
# SLIDE 10 — MÔ HÌNH ĐỒ THỊ (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Bài báo thực nghiệm trên 3 mạng xã hội thật và 4 mô hình đồ thị ngẫu nhiên.

Hai mô hình **phù hợp** mạng xã hội:
- **Barabási-Albert**: tạo đồ thị scale-free với cơ chế 'rich-get-richer' — người nhiều bạn càng dễ có thêm bạn. Phân phối bậc power-law, giống mạng thật.
- **Holme-Kim**: giống BA nhưng thêm clustering — 'bạn của bạn cũng là bạn'.

Hai mô hình **không phù hợp**:
- **Erdős-Rényi**: mỗi cạnh xuất hiện ngẫu nhiên với xác suất p. Tất cả nodes 'giống nhau' → NDS không phân biệt được.
- **Watts-Strogatz**: small-world nhưng bậc đồng đều → cùng vấn đề.

Kết luận quan trọng: hiệu quả thuật toán **phụ thuộc vào cấu trúc mạng**."

**[DẪN]:** "Giờ xem kết quả thực nghiệm cụ thể."

---

# ═══════════════════════
# SLIDE 11 — CẤU HÌNH (⏱️ 1 phút)
# ═══════════════════════

**[NÓI]:**
"Nhóm tái hiện thực nghiệm với 120 nodes, node noise δ = 5%, edge noise từ 0 đến 20%. Mỗi mức noise chạy 3 trials lấy trung bình.

So với bài báo gốc dùng mạng thật hàng ngàn nodes, nhóm dùng quy mô nhỏ hơn để chạy nhanh nhưng vẫn đủ để kiểm chứng xu hướng."

**[DẪN]:** "Kết quả bước 1 — chỉ NDSD."

---

# ═══════════════════════
# SLIDE 12 — KẾT QUẢ NDSD (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Bảng này cho thấy accuracy chỉ với NDSD:

BA đạt khoảng 95% khi không noise, giảm xuống 50% ở ε=10%, và 15% ở ε=20%.
HK tương tự nhưng thấp hơn một chút.

Ngược lại, ER chỉ đạt 15% khi ε=0 và gần 0 khi có noise. WS còn tệ hơn.

Giải thích: BA và HK có phân phối bậc power-law — mỗi node có NDS rất đặc trưng, diff phân biệt tốt. ER và WS có bậc đồng đều — nhiều node cùng NDS → Hungarian khớp sai."

**[DẪN]:** "Khi thêm Local Search, kết quả cải thiện đáng kể."

---

# ═══════════════════════
# SLIDE 13 — KẾT QUẢ PIPELINE (⏱️ 2 phút)
# ═══════════════════════

**[NÓI]:**
"Khi kết hợp NDSD + Local Search:

BA tăng từ 50% lên 80% ở ε=10% — cải thiện 30 điểm phần trăm. HK cũng tương tự.

Nhưng trên ER và WS, cải thiện rất ít — chỉ 3-7 điểm. Lý do: NDSD đã sai quá nhiều → Local Search bắt đầu từ nghiệm quá tệ → bị kẹt ở local optimum.

Kết luận: pipeline NDSD + LS **chịu được noise lên đến 10%** trên mạng scale-free."

**[DẪN]:** "Kết quả này có khớp với bài báo gốc không? Xem đối chiếu."

---

# ═══════════════════════
# SLIDE 14 — ĐỐI CHIẾU (⏱️ 1.5 phút)
# ═══════════════════════

**[NÓI]:**
"Đối chiếu với bài báo gốc — bảng này cho thấy 5 quan sát chính đều **khớp** với kết quả bài báo:
- BA/HK performance cao ✅
- ER/WS performance kém ✅
- Local Search cải thiện đáng kể trên BA/HK ✅
- Chịu nhiễu ε ≤ 10% ✅
- Mạng thật có hành vi giống BA/HK — nhóm chưa thử trên mạng thật nhưng bài báo đã chứng minh qua Figure 3.

**Kết luận:** Tái hiện thành công. Kết quả **nhất quán** với bài báo gốc."

**[DẪN]:** "Tuy nhiên thuật toán gốc có hạn chế. Nhóm đề xuất cải tiến — xem phần tiếp."

---

## TỔNG THỜI GIAN PHẦN 1: ~26 phút

| Nhóm slide | Thời gian |
|-----------|-----------|
| Mở đầu (1-3) | ~3.5 phút |
| Lý thuyết (4-9) | ~14.5 phút |
| Thực nghiệm (10-14) | ~8.5 phút |

*→ Tiếp phần 2 trong `presentation-script-part2.md`*
