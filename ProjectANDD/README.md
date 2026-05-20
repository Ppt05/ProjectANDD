# Phi Ẩn Danh Hóa Mạng Xã Hội

> **Tái hiện thực nghiệm** bài báo khoa học:  
> *"Deanonymizing Social Networks Using Structural Information"*  
> Caragiannis & Tsitsoka — IJCAI-2019

**Môn học:** An Ninh Di Động | **Nhóm:** [Điền tên nhóm]

---

## Mục Lục

- [Tổng Quan](#tổng-quan)
- [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
- [Cài Đặt](#cài-đặt)
- [Cách Chạy](#cách-chạy)
- [Giải Thích Output](#giải-thích-output)
- [Tài Liệu Tham Khảo](#tài-liệu-tham-khảo)

---

## Tổng Quan

Project này tái hiện hai thuật toán phi ẩn danh hóa mạng xã hội từ bài báo IJCAI-2019:

| Thuật toán | Ý tưởng | Độ phức tạp |
|-----------|---------|------------|
| **NDSD** | Khớp dựa trên Neighbor Degree Sequence + Hungarian Algorithm | O(n⁴) |
| **Local Search** | Cải thiện NDSD bằng swap cục bộ | O(n⁵) |

**Kết quả chính:** Kết hợp NDSD + Local Search de-anonymize chính xác với nhiễu ≤ 10%.

---

## Cấu Trúc Thư Mục

```
ProjectANDD/
├── experiment.py              ← Code thực nghiệm chính (chạy cái này)
├── export_slide.py            ← Tạo file PowerPoint tự động
├── requirements.txt           ← Danh sách thư viện cần cài
├── README.md                  ← File này
│
├── theory_detail.md           ← Nội dung lý thuyết chi tiết (tiếng Việt)
├── slide_outline.md           ← Outline slide 19 trang (tiếng Việt)
│
├── ban_dich_bai_bao.pdf       ← Bản dịch bài báo (tiếng Việt)
├── Deanonymizing Social ...pdf ← Bài báo gốc (tiếng Anh)
│
└── [output - tự sinh sau khi chạy]
    ├── bieu_do_1_accuracy_vs_noise.png
    ├── bieu_do_2_ndsd_vs_local_search.png
    └── presentation.pptx
```

---

## Cài Đặt

### Yêu Cầu

- Python 3.9 trở lên
- pip

### Bước 1 — Cài thư viện

```bash
pip install -r requirements.txt
```

> **Lưu ý Windows:** Nếu gặp lỗi encoding khi chạy, dùng lệnh:
> ```bash
> set PYTHONIOENCODING=utf-8
> python experiment.py
> ```

### Bước 2 — Kiểm tra cài đặt

```bash
python -c "import networkx, matplotlib, scipy, numpy, pptx; print('OK')"
```

Nếu in ra `OK` là thành công.

---

## Cách Chạy

### Chạy Thực Nghiệm Chính

```bash
python experiment.py
```

**Thời gian ước tính:**
| Cấu hình | Thời gian |
|---------|----------|
| n=100, 3 trials | ~2-5 phút |
| n=350, 5 trials (mặc định) | ~15-30 phút |
| n=500, 10 trials | ~60-90 phút |

**Thay đổi cấu hình** (cuối file `experiment.py`):

```python
N_NODES      = 350     # Tăng/giảm tùy tốc độ máy
N_TRIALS     = 5       # Số lần lặp để lấy trung bình
NOISE_LEVELS = [0.0, 0.05, 0.10, 0.15, 0.20]
MODELS       = ["BA", "HK", "ER", "WS"]
```

> **Mẹo:** Để demo nhanh, đặt `N_NODES=100` và `N_TRIALS=2`

### Tạo File PowerPoint

```bash
pip install python-pptx
python export_slide.py
```

Output: `ProjectANDD/presentation.pptx` — mở được bằng PowerPoint hoặc Google Slides.

---

## Giải Thích Output

### Trong Terminal

```
============================================================
  Mô hình: BA | n=350 | delta=5% | 5 trials
============================================================
  Đồ thị G: 350 nodes, 1032 edges
  ε=  0% | trial 1 | NDSD= 98.5% | LS=100.0% | 12.3s
  ε=  5% | trial 1 | NDSD= 75.2% | LS= 88.6% | 15.1s
  ε= 10% | trial 1 | NDSD= 61.3% | LS= 76.4% | 18.7s
  ...
```

| Cột | Ý nghĩa |
|-----|---------|
| `ε` | Mức nhiễu cạnh (epsilon) |
| `NDSD` | Accuracy sau thuật toán NDSD |
| `LS` | Accuracy sau Local Search (luôn ≥ NDSD) |

### Biểu Đồ PNG

| File | Nội dung |
|------|---------|
| `bieu_do_1_accuracy_vs_noise.png` | So sánh 4 mô hình qua các mức nhiễu |
| `bieu_do_2_ndsd_vs_local_search.png` | Cải thiện của Local Search so với NDSD |

### Bảng Kết Quả Cuối

```
======================================================================
  BẢNG TÓM TẮT KẾT QUẢ (Local Search Accuracy %)
======================================================================
Mô hình             ε=0%      ε=5%     ε=10%    ε=15%    ε=20%
----------------------------------------------------------------------
Barabási-Albert     100.0%    88.5%    76.4%    52.1%    31.2%
Holme-Kim           100.0%    85.2%    72.8%    49.7%    28.5%
Erdős-Rényi          35.2%    22.1%    15.3%    10.2%     8.1%
Watts-Strogatz        8.5%     6.2%     5.1%     4.8%     4.3%
```

**Đọc kết quả:**
- BA và HK: accuracy cao → chịu được nhiễu tốt → xác nhận phù hợp với mạng XH thực
- ER và WS: accuracy thấp ngay cả khi ε=0 → không phù hợp mô hình mạng XH

---

## Thuật Toán Tóm Tắt

```
NDSD:
  1. Tính NDS(v) = sorted(degrees of neighbors of v, desc) cho mỗi v
  2. Xây cost matrix C[i][j] = L1-distance(NDS_H[i], NDS_G[j])
  3. Chạy Hungarian Algorithm → matching tối ưu
  Complexity: O(n⁴)

Local Search (bắt đầu từ kết quả NDSD):
  1. score = số cạnh H được khớp đúng trong G
  2. Lặp: thử swap mọi cặp (u,v) trong H
     → Chấp nhận nếu score tăng
  3. Dừng khi không còn swap nào cải thiện
  Complexity: O(n⁵)
```

---

## Tài Liệu Tham Khảo

1. Caragiannis, I., & Tsitsoka, E. (2019). *Deanonymizing Social Networks Using Structural Information*. IJCAI-2019.
2. Narayanan, A., & Shmatikov, V. (2009). *De-anonymizing Social Networks*. IEEE S&P.
3. Barabási, A.L., & Albert, R. (1999). *Emergence of Scaling in Random Networks*. Science.
4. NetworkX Documentation: https://networkx.org/documentation/
5. SciPy `linear_sum_assignment`: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html

---

*Project này phục vụ mục đích học tập — Môn An Ninh Di Động*
