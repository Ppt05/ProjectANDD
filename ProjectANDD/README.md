# Phi Ẩn Danh Hóa Mạng Xã Hội (De-anonymizing Social Networks)

> **Tái hiện thực nghiệm** bài báo khoa học:  
> *"Deanonymizing Social Networks Using Structural Information"*  
> Caragiannis & Tsitsoka — IJCAI-2019

**Môn học:** An Ninh Di Động | **Nhóm:** [Điền tên nhóm] | **Thành viên:** [Điền tên các thành viên]

---

## Mục Lục

- [Tổng Quan](#tổng-quan)
- [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
- [Cài Đặt](#cài-đặt)
- [Cách Chạy](#cách-chạy)
  - [1. Chạy Web Demo (Khuyên dùng)](#1-chạy-web-demo-khuyên-dùng)
  - [2. Chạy Thực Nghiệm (CLI)](#2-chạy-thực-nghiệm-cli)
- [Giải Thích Thuật Toán](#giải-thích-thuật-toán)
- [Tài Liệu Tham Khảo](#tài-liệu-tham-khảo)

---

## Tổng Quan

Project này tái hiện hai thuật toán phi ẩn danh hóa mạng xã hội dựa trên cấu trúc đồ thị, được đề xuất trong bài báo IJCAI-2019. 

Hệ thống cho phép nhập một mạng xã hội ẩn danh (không có nhãn/thông tin cá nhân) và đối chiếu nó với một mạng xã hội gốc đã biết danh tính để "lật tẩy" danh tính của người dùng.

| Thuật toán | Ý tưởng | Độ phức tạp |
|-----------|---------|------------|
| **NDSD** | Tính khoảng cách NDS (Neighbor Degree Sequence) và dùng Hungarian Algorithm để tìm matching. | O(n⁴) |
| **Local Search** | Cải thiện kết quả của NDSD bằng cách hoán đổi (swap) vị trí cục bộ để tối ưu matching. | O(n⁵) |

**Kết quả chính:** Kết hợp **NDSD + Local Search** mang lại độ chính xác cực cao (lên đến ~100% khi nhiễu thấp) đối với các mô hình mạng xã hội thực tế (Barabási-Albert, Holme-Kim).

---

## Cấu Trúc Thư Mục

```text
c:\MidTermProject\
├── ProjectANDD/
│   ├── app.py                      ← Ứng dụng Web Flask (Giao diện Demo)
│   ├── experiment_improved.py      ← Code chạy thực nghiệm đa luồng (Nhanh)
│   ├── experiment.py               ← Code chạy thực nghiệm cơ bản
│   ├── requirements.txt            ← Danh sách thư viện Python
│   ├── README.md                   ← File hướng dẫn này
│   └── templates/                  
│       └── index.html              ← Giao diện Web HTML/JS
│
├── docs/                           ← Chứa tài liệu và lý thuyết
│   ├── theory_detail.md            ← Lý thuyết chi tiết các thuật toán (Tiếng Việt)
│   ├── slide_outline.md            ← Dàn ý bài thuyết trình
│   └── PLAN-project-review.md      ← Kế hoạch và tiến độ
│
└── Result demo/                    ← Kết quả thực nghiệm và biểu đồ
    ├── bieu_do_1_accuracy_vs_noise.png
    ├── bieu_do_2_ndsd_vs_local_search.png
    └── ...
```

---

## Cài Đặt

### Yêu Cầu

- **Python 3.9+**

### Các Bước Cài Đặt

1. **Clone mã nguồn (nếu chưa có):**
   ```bash
   git clone https://github.com/Ppt05/ProjectANDD.git
   cd ProjectANDD/ProjectANDD
   ```

2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Kiểm tra xem thư viện đã cài đủ chưa:**
   ```bash
   python -c "import flask, networkx, matplotlib, scipy, numpy; print('Cài đặt thành công!')"
   ```

---

## Cách Chạy

Dự án cung cấp 2 chế độ: **Web Demo** (Trực quan, dễ hiểu) và **Chạy Thực Nghiệm** (Dành cho việc so sánh và lấy số liệu).

### 1. Chạy Web Demo (Khuyên dùng)

Giao diện Web giúp minh họa từng bước hoạt động của thuật toán trực quan qua đồ thị D3.js.

```bash
python app.py
```

- Mở trình duyệt và truy cập: **`http://127.0.0.1:5050`**
- Trên giao diện, bạn có thể:
  1. Bấm **Tạo đồ thị mới** (Chọn mô hình Barabási-Albert, Erdős-Rényi,... với độ nhiễu tùy chỉnh).
  2. Bấm **Bước 2: Chạy NDSD** để xem bước khớp cơ sở.
  3. Bấm **Bước 3: Chạy Local Search** để xem cách thuật toán tối ưu hóa và sửa sai.

### 2. Chạy Thực Nghiệm (CLI)

Chạy file này để tái hiện lại các con số trong bài báo gốc. Quá trình này sẽ tạo ra các biểu đồ lưu vào thư mục `Result demo/`.

Nên sử dụng bản `experiment_improved.py` vì đã được tối ưu hóa chạy đa luồng, nhanh hơn bản gốc.

```bash
python experiment_improved.py
```

**Cấu hình thực nghiệm (Có thể sửa trong file code):**
- `N_NODES`: Số lượng node (ví dụ: 350).
- `N_TRIALS`: Số vòng lặp để lấy trung bình (ví dụ: 5).
- `NOISE_LEVELS`: Mức độ nhiễu thêm vào đồ thị.

> **Lưu ý trên Windows:** Nếu bị lỗi liên quan đến font chữ / Unicode khi in ra terminal, hãy chạy lệnh này trước: `set PYTHONIOENCODING=utf-8`

---

## Giải Thích Thuật Toán

### 1. NDSD (Neighbor Degree Sequence Distance)
Thay vì khớp ngẫu nhiên, thuật toán nhìn vào **"Bạn của bạn có bao nhiêu bạn?"**. 
Mỗi node được mã hóa bằng một chuỗi bậc của các hàng xóm (NDS). Sau đó thuật toán dùng khoảng cách $L_1$ để đo độ lệch giữa các node và dùng **Thuật toán Hungarian** để tìm ra phương án ghép cặp (matching) tối ưu với tổng sai số thấp nhất.

### 2. Local Search (Tìm kiếm cục bộ)
Sau khi có kết quả ghép từ NDSD, chúng ta xem xét từng cặp node. Nếu việc hoán đổi (swap) vị trí ghép của 2 node làm cho đồ thị khớp với nhau tốt hơn (tăng số cạnh giống nhau), thì ta chấp nhận sự hoán đổi này. Quá trình lặp lại cho đến khi không thể hoán đổi để tối ưu thêm được nữa.

> Đọc thêm giải thích toán học chi tiết tại file: `docs/theory_detail.md`

---

## Tài Liệu Tham Khảo

1. **Bài báo chính:** Caragiannis, I., & Tsitsoka, E. (2019). *Deanonymizing Social Networks Using Structural Information*. IJCAI-2019.
2. Narayanan, A., & Shmatikov, V. (2009). *De-anonymizing Social Networks*. IEEE S&P.
3. NetworkX Documentation: https://networkx.org/
4. SciPy `linear_sum_assignment`: scipy.optimize.linear_sum_assignment

---
*Dự án thực hiện cho môn An Ninh Di Động - [Tên trường của bạn]*
