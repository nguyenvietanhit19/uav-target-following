# 03. Điều khiển yaw từ ảnh

> [Về mục lục chính](../kien_thuc_drone_bam_muc_tieu.md) · Trước: [02](02_script_va_thi_nghiem.md)

## 1. Từ pixel đến yaw rate: `tâm_box_x`, sai số chuẩn hóa, `K_YAW`

Mục này giải thích chi tiết phần "giữ mục tiêu ở giữa khung hình" bằng cách xoay mũi drone. Chuỗi tính toán đầy đủ:

```
Ảnh từ camera
   ↓  (YOLO tìm người, trả về khung bao quanh)
Tâm khung theo trục x            →  tâm_box_x          (ví dụ 480 px)
   ↓  (trừ đi tâm ảnh)
Sai số thô                       →  480 - 320 = 160 px
   ↓  (chia cho nửa độ rộng ảnh)
Sai số chuẩn hóa                 →  160 / 320 = 0,5
   ↓  (nhân với hệ số K_YAW)
yaw_rate                         →  40 * 0,5 = 20 độ/giây
   ↓
VelocityBodyYawspeed(tiến, 0, 0, yaw_rate)
```

### 1.1. Tọa độ trong ảnh và pixel

**Pixel** là một điểm ảnh, ô vuông nhỏ nhất của ảnh. Ảnh rộng 640 px nghĩa là mỗi hàng có 640 điểm ảnh.

Tọa độ trong ảnh khác với đồ thị toán học: gốc (0, 0) nằm ở **góc trên-trái**, trục x chạy sang **phải**, trục y chạy **xuống dưới**.

```
(0,0) ──────────────────────────────→ x
  │   x = 0        x = 320        x = 640
  │   mép trái     tâm ảnh        mép phải
  ↓
  y
```

Với ảnh rộng 640 px thì **tâm ảnh theo trục x** nằm ở 640 / 2 = **320**.

### 1.2. `tâm_box_x` là gì

**`tâm_box_x` là tọa độ x (đơn vị pixel) của điểm chính giữa khung chữ nhật bao quanh người.**

Khi YOLO phát hiện một người, nó vẽ một khung chữ nhật quanh người đó (bounding box, tức khung chữ nhật bao quanh vật thể). Khung thường được mô tả bằng hai góc: góc trên-trái và góc dưới-phải.

```
(0,0) ────────────────────────→ x
  │      x1                x2
  │      ┌────────────────┐ ← y1 (cạnh trên)
  │      │      người     │
  │      │       🚶       │
  │      └────────────────┘ ← y2 (cạnh dưới)
  ↓
  y
```

- `x1`, `x2`: tọa độ x của cạnh trái và cạnh phải của khung.
- `y1`, `y2`: tọa độ y của cạnh trên và cạnh dưới.

Tâm theo trục x nằm giữa hai cạnh trái và phải, tức là trung bình cộng:

```
tâm_box_x = (x1 + x2) / 2
```

**Ví dụ:** ảnh rộng 640 px, YOLO báo khung người có x1 = 400 và x2 = 560.
- Cộng: 400 + 560 = 960
- Chia 2: 960 / 2 = **480**
- Kiểm tra: khung rộng 560 - 400 = 160 px, nửa khung là 80 px, nên điểm giữa = 400 + 80 = 480. Khớp.

Với việc xoay trái phải, chỉ cần `tâm_box_x`. Chiều cao khung (y2 - y1) để sau, dùng ước lượng khoảng cách tới người (người càng gần thì khung càng to; phần ước lượng khoảng cách chưa học, xem [kho chưa học](chua_hoc/thi_giac_phat_hien_theo_doi.md)).

*Lưu ý chưa kiểm chứng:* một số thư viện trả khung dạng `(x1, y1, x2, y2)`, số khác trả `(x_tâm, y_tâm, rộng, cao)` (khi đó tâm đã có sẵn). Dự án chưa cài YOLO (bước 4 của lộ trình), nên đến lúc đó cần xem tài liệu thư viện đã cài để biết đúng dạng, không đoán.

### 1.3. Sai số và sai số thô

Bạn muốn người luôn nằm **giữa** khung hình, nên **sai số là người đang lệch khỏi giữa bao xa**. Sai số thô tính thẳng bằng pixel:

```
sai_số_thô = tâm_box_x - tâm_ảnh_x
```

**Ví dụ:** tâm_box_x = 480, tâm ảnh = 320 → sai số thô = 480 - 320 = **+160 px**.

Quy ước dấu: **dương là người lệch phải, âm là lệch trái**, khớp với quy ước yaw rate (dương xoay phải).

### 1.4. Sai số chuẩn hóa là gì và vì sao cần

Con số 160 px **không có ý nghĩa cố định**, vì nó phụ thuộc ảnh to hay nhỏ. Ví dụ hai trường hợp người đứng **cùng một chỗ** trong khung hình (cách tâm bằng một nửa đoạn từ tâm ra mép phải):

| Ảnh | Tâm ảnh | Người ở | Sai số thô |
|---|---|---|---|
| rộng 640 px | 320 | x = 480 | 160 px |
| rộng 1280 px | 640 | x = 960 | 320 px |

Cùng một vị trí tương đối mà số pixel khác nhau gấp đôi. Nếu dùng thẳng pixel thì mỗi lần đổi camera hoặc độ phân giải lại phải chọn lại toàn bộ hệ số điều khiển.

**Chuẩn hóa** là đổi về một thước đo chung, không phụ thuộc kích thước ảnh, bằng cách chia sai số thô cho **nửa độ rộng ảnh** (khoảng cách từ tâm ra mép):

```
sai_số_chuẩn_hóa = (tâm_box_x - tâm_ảnh_x) / (độ_rộng_ảnh / 2)
```

- `tâm_box_x - tâm_ảnh_x`: sai số thô (pixel).
- `độ_rộng_ảnh / 2`: khoảng cách từ tâm ảnh ra mép ảnh (pixel).
- Kết quả không có đơn vị (pixel chia pixel).

**Tính lại hai trường hợp trên:**
- Ảnh 640: (480 - 320) / (640 / 2) = 160 / 320 = **0,5**
- Ảnh 1280: (960 - 640) / (1280 / 2) = 320 / 640 = **0,5**

Hai kết quả bằng nhau, đúng như trực giác (người đứng cùng chỗ trong khung hình).

**Cách đọc con số.** Sai số chuẩn hóa nằm trong khoảng **-1 đến +1** (khi tâm khung nằm trong ảnh) và cho biết "người lệch được bao nhiêu phần của đoạn từ tâm ra mép":

| Giá trị | Ý nghĩa | Ví dụ với ảnh 640 px (tâm_box_x) |
|---|---|---|
| 0 | Người ở chính giữa ảnh | 320 |
| +0,5 | Nửa đường từ tâm ra mép phải | 480 |
| +1 | Sát mép phải | 640 |
| -1 | Sát mép trái | 0 |
| -0,25 | Một phần tư đường từ tâm ra mép trái | 240 |

Kiểm tra dòng cuối: (240 - 320) / 320 = -80 / 320 = -0,25.

### 1.5. `K_YAW` là gì

Sau khi có sai số chuẩn hóa, bước cuối là đổi nó thành tốc độ xoay:

```
yaw_rate = K_YAW * sai_số_chuẩn_hóa
```

- `yaw_rate`: tốc độ xoay mũi gửi cho drone (độ/giây; dương xoay phải, xem mục 2.4 của [file 01](01_he_toa_do_yaw_offboard.md)).
- `sai_số_chuẩn_hóa`: số từ -1 đến +1 vừa tính ở trên.
- `K_YAW`: **hệ số do bạn tự chọn**, đơn vị độ/giây.

**Ý nghĩa của K_YAW:** nếu người ở sát mép ảnh (sai số chuẩn hóa = ±1) thì drone xoay `K_YAW` độ/giây. Vì sai số chuẩn hóa chỉ nằm trong -1 đến +1 nên `K_YAW` cũng chính là **tốc độ xoay lớn nhất** có thể xảy ra. (K_YAW là một hệ số tỉ lệ, cùng họ với hệ số Kp của bộ điều khiển P sẽ học sau.)

**Ví dụ: cùng một vị trí người (x = 480, sai số chuẩn hóa = 0,5), đổi K_YAW:**

| K_YAW | Tính | yaw_rate | Cảm giác |
|---|---|---|---|
| 20 | 20 * 0,5 | **10 °/s** | Xoay chậm, êm, nhưng có thể theo không kịp khi người đi nhanh |
| 40 | 40 * 0,5 | **20 °/s** | Vừa phải |
| 90 | 90 * 0,5 | **45 °/s** | Xoay gấp, dễ vọt qua giữa rồi lắc qua lắc lại |

**Ví dụ: cùng K_YAW = 40, đổi vị trí người (ảnh 640 px):**

| tâm_box_x | Sai số thô | Chuẩn hóa | yaw_rate | Ý nghĩa |
|---|---|---|---|---|
| 640 | 640 - 320 = 320 | 320 / 320 = 1 | 40 * 1 = **+40°/s** | Sát mép phải, xoay phải hết cỡ |
| 480 | 160 | 0,5 | 40 * 0,5 = **+20°/s** | Lệch phải nhiều |
| 360 | 40 | 40 / 320 = 0,125 | 40 * 0,125 = **+5°/s** | Lệch phải ít, xoay chậm |
| 320 | 0 | 0 | **0°/s** | Ở giữa, không xoay |
| 100 | 100 - 320 = -220 | -220 / 320 = -0,6875 | 40 * (-0,6875) = **-27,5°/s** | Lệch trái, xoay trái |
| 0 | -320 | -1 | **-40°/s** | Sát mép trái, xoay trái hết cỡ |

Drone xoay thì người dịch về giữa ảnh, sai số giảm, yaw rate giảm theo, về 0 thì dừng xoay.

**Ví dụ đời thường:** bạn ngồi ghế xoay và bạn A đứng lệch bên phải. K_YAW nhỏ giống người ngồi lười: lệch phải chút thì đạp chân nhẹ, A có thể đã đi mất trước khi bạn xoay kịp. K_YAW lớn giống người cuống: thấy A lệch một chút là đạp ghế mạnh, ghế vọt qua mặt A rồi phải đạp ngược lại.

### 1.6. Hỏi và đáp

**Hỏi: `tâm_box_x` là gì?**

Là tọa độ x của điểm giữa khung bao quanh người, tính bằng pixel, bằng `(x1 + x2) / 2`. Xem 1.2.

**Hỏi: Sai số chuẩn hóa là gì, sao không dùng luôn số pixel?**

Là sai số thô chia cho nửa độ rộng ảnh, ra số từ -1 đến +1. Dùng pixel thì cùng một vị trí tương đối cho số khác nhau ở mỗi độ phân giải (160 px ở ảnh 640, 320 px ở ảnh 1280); chuẩn hóa cho cùng kết quả 0,5 ở cả hai, nên đổi camera không phải chọn lại hệ số. Xem 1.4.

**Hỏi: `K_YAW` là gì?**

Là hệ số bạn tự chọn, cho biết khi người ở sát mép ảnh thì drone xoay bao nhiêu độ/giây. Càng lớn thì drone phản ứng càng mạnh. Xem 1.5.

**Hỏi: Nên chọn `K_YAW` bằng bao nhiêu?**

Chưa có đáp án chắc chắn, vì chưa thử trên sim (mức [GT]). Hướng làm: bắt đầu nhỏ (ví dụ 20) rồi tăng dần đến khi drone theo kịp người mà không lắc qua lắc lại. Trong sim, RTF thấp làm vòng điều khiển trễ hơn nên giá trị tốt có thể nhỏ hơn dự kiến.

### 1.7. Lưu ý

- **Chưa kiểm chứng trên sim:** cách chuẩn hóa và việc chọn K_YAW là thiết kế đề xuất (mức [GT]), chưa viết code hay chạy thử.
- **Camera nhìn xuống:** các ví dụ giả định camera nhìn về phía trước. Camera đang dùng trong Gazebo là `gz_x500_mono_cam_down` (nhìn xuống), nên đến bước 3 và 4 phải xét lại: dùng model camera hướng trước, hoặc đổi cách tính sai số (ví dụ dịch ngang thay vì xoay).
