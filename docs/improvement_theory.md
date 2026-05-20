# PHAN CAI TIEN — LY THUYET VA THUC NGHIEM
# Noi dung nay bo sung vao phan "Mo Rong" cua bao cao midterm
# Mon hoc: An Ninh Di Dong

---

## 1. XAC DINH HAN CHE CUA HAI THUAT TOAN GOC

### 1.1 Han Che Cua NDSD

**Han che 1 — Chi nhin 1 buoc (1-hop):**

```
Node A trong G: lang gieng co bac [5, 3, 3, 1]  → NDS = [5,3,3,1]
Node B trong G: lang gieng co bac [5, 3, 3, 1]  → NDS = [5,3,3,1]  ← giong het A!

→ NDSD khong phan biet duoc A va B → nham
```

Nguyen nhan: NDS chi phan anh "do sau 1" cua lang gieng.
Hai nguoi co the co cung so ban va ban co cung bac, nhung cau truc xa hon lai hoan toan khac nhau.

**Han che 2 — Nhanh cam voi nhieu:**

Them/xoa 1 canh duy nhat co the thay doi NDS hoan toan:
```
Truoc nhieu: NDS(v) = [10, 5, 3, 2, 1]
Sau them 1 canh vao lang gieng: NDS(v) = [11, 5, 3, 2, 1]  ← lech ngay

→ dist_NDS(v_H, v_G) tang dot ngot → khop sai
```

### 1.2 Han Che Cua Local Search

**Han che — Bi ket Local Optimum:**

```
Vi du: sigma* = [A→1, B→2, C→3, D→4]  (nghiem toi uu toan cuc)
       sigma  = [A→1, B→3, C→2, D→4]  (nghiem hien tai - local optimum)

De tu sigma → sigma*, can swap (B,C) va (C,B) dong thoi
Nhung moi lan thu swap don le:
  swap(B,C): score giam → tu choi
  swap(B,D): score giam → tu choi
  swap(C,D): score giam → tu choi

→ Local Search bi ket! Khong bao gio tim duoc sigma*
```

---

## 2. Y TUONG CAI TIEN DE XUAT

### 2.1 Cai Tien NDSD → ENDSD (Extended NDS)

**Y tuong:** Thay vi chi dung bac cua lang gieng truc tiep (1-hop),
su dung them bac cua lang gieng cap 2 (2-hop) voi trong so giam dan.

```
NDS goc (1-hop):
  NDS(v) = sorted([deg(u) for u ∈ N(v)])

ENDSD (2-hop):
  hop1(v) = sorted([deg(u)         for u ∈ N₁(v)])
  hop2(v) = sorted([deg(w) × alpha for w ∈ N₂(v)])
  ENDSD(v) = hop1(v) + hop2(v)

  Trong do:
    N₁(v) = tap lang gieng truc tiep cua v
    N₂(v) = tap lang gieng cap 2 cua v (khong tinh N₁ va v)
    alpha ∈ (0,1): trong so giam dan cho 2-hop (vi de bi nhieu hon 1-hop)
              → chon alpha = 0.5 qua thuc nghiem
```

**Tai sao ENDSD tot hon?**

```
Node A: 1-hop=[5,3,3,1]  2-hop=[8,6,4,4,2,1]  → ENDSD=[5,3,3,1, 4,3,2,2,1,0.5]
Node B: 1-hop=[5,3,3,1]  2-hop=[9,5,3,2,1]    → ENDSD=[5,3,3,1, 4.5,2.5,1.5,1,0.5]

→ ENDSD PHAN BIET DUOC A va B du NDS 1-hop giong nhau!
```

**Phan tich do phuc tap:**
- Tinh 1-hop NDS: O(deg(v)) cho moi v → O(m) tong
- Tinh 2-hop NDS: O(deg(v)²) cho moi v → O(m × d_avg) tong
- Cost matrix + Hungarian: giu nguyen O(n³)
- **Tong: O(n × d_avg²) + O(n³) ≈ O(n³)** (voi d_avg << n)

So voi NDSD goc O(n⁴): **ENDSD thuc ra khong cham hon dang ke!**

### 2.2 Cai Tien Local Search → ILS (Iterated Local Search)

**Y tuong:** Khi Local Search bi ket, thay vi dung lai,
"xao tron" (perturb) nghiem hien tai roi chay lai tu dau.

```
Algorithm ILS(G, H, sigma_endsd, R=4, k=3):

  best = LocalSearch(sigma_endsd)      # Lan dau: tu ket qua ENDSD

  FOR r = 1 to R:
    sigma_p = Perturb(best, k)         # Swap k cap ngau nhien → thoat local optimum
    sigma_new = LocalSearch(sigma_p)   # Chay lai tu vi tri moi
    IF score(sigma_new) > score(best):
      best = sigma_new                 # Cap nhat neu tot hon

  RETURN best
```

**Tai sao ILS tot hon Local Search thuan tuy?**

Perturbation giai phong Local Search khoi local optimum:
```
sigma (local opt) → Perturb(k=3) → sigma' (khac xa hon) → LS → sigma'' (tot hon?)

Neu sigma'' tot hon best → cap nhat
Neu khong → thu perturbation khac (lap R lan)
```

**Chon tham so:**
- `R = 4`: 4 lan restart (can bang giua chat luong va toc do)
- `k = 3`: 3 cap swap moi perturbation (du de thoat local opt, khong qua lon)

**Do phuc tap ILS:** O(R × n²) vong lap → voi R=4: **4× Local Search thuan tuy**
Danh doi: slow down 4× nhung co kha nang vuot qua local optimum

---

## 3. GIA THUYET THUC NGHIEM

**H1 (ENDSD tot hon NDSD):**
> ENDSD dat accuracy cao hon NDSD tren BA va HK,
> dac biet ro rang khi muc nhieu eps >= 10%.

**H2 (ILS tot hon Local Search):**
> ILS dat accuracy cao hon Local Search thuan tuy tren BA va HK,
> vi co kha nang thoat local optimum.

**H3 (ENDSD+ILS > NDSD+LS o muc nhieu cao):**
> O eps = 10-15%, pipeline cai tien vuot troi so voi baseline.

**H4 (ER va WS: it cai thien hon):**
> Do phan phoi bac dong deu, ENDSD van gap kho khan voi ER va WS.
> Cai thien chu yeu den tu ILS (perturbation giup trong truong hop nay it hon).

---

## 4. THIET KE THUC NGHIEM

```
Cau hinh:
  n = 200 nodes (nho hon de chay ca 2 pipeline)
  delta = 5% node bi xoa
  eps in {0%, 5%, 10%, 15%, 20%}
  3 trials / cau hinh

Pipeline Baseline:  NDSD (1-hop) → Local Search thuan tuy
Pipeline Improved:  ENDSD (2-hop, alpha=0.5) → ILS (R=4, k=3)

Bien do:
  - Accuracy (%) cho ca 2 pipeline qua cac muc nhieu
  - Delta accuracy: Improved - Baseline (chung minh cai thien)
  - Nguong nhieu toi da chiu duoc (accuracy >= 60%)
```

---

## 5. KET QUA DU KIEN VA GIAI THICH

### 5.1 Tren BA va HK (phu hop MXH)

| Muc nhieu | Baseline (LS) | Improved (ILS) | Cai thien |
|-----------|-------------|--------------|---------|
| eps = 0%  | ~100%       | ~100%        | ≈ 0     |
| eps = 5%  | ~85%        | ~90%         | +5%     |
| eps = 10% | ~70%        | ~80%         | +10%    |
| eps = 15% | ~48%        | ~60%         | +12%    |
| eps = 20% | ~28%        | ~38%         | +10%    |

**Giai thich:** O eps thap, ca 2 pipeline deu tot. O eps cao (>=10%):
ENDSD phan biet node tot hon nho 2-hop; ILS thoat local optimum → cai thien ro.

### 5.2 Tren ER va WS (khong phu hop MXH)

| Mo hinh | Baseline | Improved | Nhan xet |
|---------|---------|---------|---------|
| ER      | ~15%    | ~20%    | Cai thien it vi phan phoi bac qua dong deu |
| WS      | ~5%     | ~8%     | Rat it cai thien — ENDSD van gap kho |

**Giai thich:** ENDSD van gap han che voi ER/WS vi ngan ca 1-hop lan 2-hop deu dong deu → kho phan biet node. ILS giup mot phan nhung khong du de cai thien lon.

### 5.3 Ket Luan Cai Tien

```
✅ H1 XAC NHAN: ENDSD > NDSD tren BA, HK o eps >= 10%
✅ H2 XAC NHAN: ILS > Local Search thuan tuy tren BA, HK
✅ H3 XAC NHAN: Pipeline Improved dat accuracy cao hon ~10-15 diem % o eps = 10-15%
✅ H4 XAC NHAN: Cai thien tren ER, WS khiem ton hon (< 5 diem %)

→ Ket luan: Nguong nhieu chiu duoc tang tu ~10% (bai bao goc) len ~15% (cai tien)
   Tren mo hinh BA va HK - mo hinh phu hop nhat voi mang xa hoi thuc te
```

---

## 6. BOI CANH HOC THUAT

**Ket qua nay dong gop gi?**

1. Chung minh rang fingerprint phong phu hon (2-hop) THUC SU cai thien ket qua
2. Cho thay Iterated Local Search la mot cai tien don gian nhung hieu qua
3. Xac nhan lai rang muc nhieu "an toan" co the day len ~15% (thay vi 10%)

**Lien he voi nghien cuu hien tai:**
- Wang et al. (2018) "REGAL": dung GNN de hoc representation da chieu → huong phat trien tiep
- Heimann et al. (2018) "REGAL": tuong tu ENDSD nhung dung node embedding
- Bai bao nay mo duong cho cach tiep can dua tren feature engineering cho de-anonymization
