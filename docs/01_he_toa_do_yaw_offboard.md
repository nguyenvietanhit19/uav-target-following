# 01. Hệ tọa độ, yaw và offboard mode

> [Về mục lục chính](../kien_thuc_drone_bam_muc_tieu.md) · Tiếp theo: [02. Script và thí nghiệm](02_script_va_thi_nghiem.md)

## 1. Hệ tọa độ: NED và body frame

### 1.1. NED (North - East - Down)

PX4 mô tả vị trí và vận tốc bằng 3 trục gắn với mặt đất:

| Trục | Dương nghĩa là |
|---|---|
| N (North) | hướng **Bắc** |
| E (East) | hướng **Đông** |
| D (Down) | hướng **xuống đất** |

**Trục D hay gây nhầm nhất:** bay lên là D **âm**.

Ví dụ: drone ở độ cao 10 m so với điểm cất cánh thì D = -10. Muốn bay lên với tốc độ 2 m/s thì đặt vận tốc D = -2.

(Gazebo lại hay dùng ENU - East, North, Up - nên khi nối PX4 với Gazebo rất dễ nhầm dấu và thứ tự trục.)

### 1.2. Body frame (hệ tọa độ gắn trên thân drone)

| Trục | Hướng |
|---|---|
| Forward | hướng mũi drone |
| Right | bên phải drone |
| Down | xuống dưới thân drone |

Body frame tiện cho bài bám người: "tiến 1 m/s" luôn là hướng mũi drone, dù mũi đang quay về đâu. Drone tự đổi sang NED giúp bạn.

### 1.3. Công thức đổi từ body frame sang NED

```
north = forward * cos(yaw) - right * sin(yaw)
east  = forward * sin(yaw) + right * cos(yaw)
```

**Ví dụ 1:** yaw = 90° (mũi hướng Đông), forward = 2 m/s, right = 0.
- north = 2 * cos 90° - 0 = 2 * 0 = **0**
- east = 2 * sin 90° + 0 = 2 * 1 = **2**
- Vậy drone bay thẳng về phía Đông 2 m/s, đúng hướng mũi.

**Ví dụ 2:** yaw = 90°, forward = 0, right = 1 m/s.
- north = 0 - 1 * sin 90° = **-1** (về phía Nam)
- east = 0 + 1 * cos 90° = **0**
- Bên phải của người đang nhìn về Đông là hướng Nam. Kết quả đúng.

**Ví dụ 3:** yaw = 45°, forward = 2 m/s, right = 0.
- north = 2 * cos 45° ≈ 2 * 0,707 = **1,41**
- east = 2 * sin 45° ≈ 2 * 0,707 = **1,41**
- Drone bay về Đông Bắc, đúng hướng mũi.

Công thức đúng với mọi yaw.

### 1.4. Hỏi và đáp

**Hỏi: Nếu ban đầu mũi không hướng về Bắc thì sao?**

Không sao. Xem mục 2.3.

---

## 2. Yaw và yaw rate

### 2.1. Yaw là gì

**Yaw là hướng mũi drone đang nhìn về**, đo bằng góc như la bàn, nhìn từ trên xuống:

```
                 Bắc (0°)
                    ↑
 Tây (270°)  ←      ✛      →  Đông (90°)
                    ↓
                 Nam (180°)
```

- Mũi chỉ Bắc: yaw = 0°
- Mũi chỉ Đông: yaw = 90° (xoay sang phải, cùng chiều kim đồng hồ)
- Mũi chỉ Nam: yaw = 180°
- Mũi chỉ Tây: yaw = 270°

Cách nhớ: đứng yên một chỗ, mặt nhìn về hướng Bắc, rồi xoay người sang phải dần dần. Góc đã xoay là yaw.

### 2.2. Hai điều dễ nhầm

1. **Yaw là hướng mũi, không phải hướng bay.** Drone có thể mũi nhìn về Đông nhưng đang bay lùi hoặc bay ngang. Giống bạn nhìn về phía trước nhưng bước sang bên.
2. **Vì sao yaw quan trọng với bài bám người:** camera gắn ở mũi drone, mũi quay đi đâu camera nhìn về đó. Muốn người luôn ở giữa khung hình, phải xoay mũi theo người, tức là điều khiển yaw.

### 2.3. Hỏi và đáp: ban đầu mũi không hướng về Bắc thì sao?

**Yaw luôn đo so với hướng Bắc**, không phải so với hướng ban đầu của drone. Bắc là mốc cố định, giống kim la bàn luôn chỉ Bắc dù bạn đứng quay mặt về đâu.

Drone biết yaw hiện tại nhờ **la bàn (magnetometer)** bên trong, nên yaw ban đầu có thể là giá trị bất kỳ.

**Ví dụ thật từ thí nghiệm của bạn:** lúc bắt đầu, hướng mũi drone là **95,9°**, tức là gần hướng Đông chứ không phải Bắc. Khi bạn ra lệnh "tiến" trong body frame, drone bay về phía Đông (xem mục 2 của [file 02](02_script_va_thi_nghiem.md)).

Quan trọng: **lượng xoay không phụ thuộc yaw ban đầu**, chỉ có hướng cuối cùng thì phụ thuộc.

### 2.4. Yaw rate (tốc độ xoay)

- **Yaw** là góc đang đứng (ví dụ 90°).
- **Yaw rate** là mình đang xoay nhanh cỡ nào, đo bằng độ/giây.
- Giống kim đồng hồ: vị trí kim là yaw, kim chạy nhanh hay chậm là yaw rate.

```
yaw_mới = yaw_cũ + yaw_rate * thời_gian
```

**Ví dụ 1:** yaw = 0° (mũi Bắc), yaw rate = 30 độ/giây trong 3 giây.
- yaw_mới = 0 + 30 * 3 = **90°** (mũi xoay sang Đông)

**Ví dụ 2 (yaw ban đầu không phải 0):** yaw = 45°, yaw rate = 30 độ/giây trong 3 giây.
- yaw_mới = 45 + 30 * 3 = **135°**
- Mũi vẫn xoay thêm đúng 90°, chỉ hướng cuối khác.

**Ví dụ 3 (vượt 360°):** yaw = 350°, xoay thêm 30°.
- 350 + 30 = 380, rồi 380 % 360 = **20°** (`%` là phép chia lấy phần dư: 380 chia 360 được 1, dư 20; chi tiết ở [kho chưa học](chua_hoc/toan_phu_tro.md))

**Dấu của yaw rate:**
- Dương: xoay sang **phải** (cùng chiều kim đồng hồ).
- Âm: xoay sang **trái**.

**Ví dụ 4:** yaw rate = -30 độ/giây trong 3 giây, bắt đầu từ 90°.
- yaw_mới = 90 + (-30 * 3) = **0°** (mũi quay từ Đông về Bắc)

### 2.5. Hai kiểu lệnh xử lý yaw khác nhau

| Kiểu lệnh | Ý nghĩa của yaw | Cần biết yaw ban đầu không |
|---|---|---|
| Body frame + yaw rate (`VelocityBodyYawspeed`) | "Xoay thêm 30 độ/giây" | **Không** |
| NED + yaw tuyệt đối (`VelocityNedYaw`) | "Hãy quay mũi về hướng 90°" | Không (drone tự tính phải xoay bao nhiêu) |

**Ví dụ NED + yaw tuyệt đối:** mũi đang ở 45°, lệnh yaw = 90° thì drone xoay thêm 90 - 45 = **45°** sang phải. Mũi đang ở 200°, lệnh yaw = 90° thì drone xoay ngược lại 200 - 90 = **110°** sang trái.

Với bài bám người sẽ dùng kiểu **body frame + yaw rate**, vì chỉ cần nói "người lệch phải thì xoay phải".

### 2.6. Ví dụ cho kiểu body frame + yaw rate

Lệnh có dạng `VelocityBodyYawspeed(tiến, phải, xuống, yaw_rate)`. Ba số đầu là vận tốc theo thân drone (m/s), số cuối là yaw rate (độ/giây; dương xoay phải, âm xoay trái). Lệnh này chỉ nói "xoay nhanh cỡ này", không nói "quay về hướng nào", nên không cần biết yaw ban đầu.

**Ví dụ 1: chỉ xoay tại chỗ.** Lệnh `(0, 0, 0, 30)` trong 3 giây, theo `yaw_mới = yaw_cũ + yaw_rate * thời_gian`:

| Mũi ban đầu | Tính | Mũi lúc sau | Lượng xoay |
|---|---|---|---|
| 45° | 45 + 30 * 3 | **135°** | +90° |
| 200° | 200 + 30 * 3 | **290°** | +90° |
| 350° | 350 + 30 * 3 = 440, rồi 440 % 360 | **80°** | +90° |

Yaw ban đầu là bao nhiêu thì lượng xoay vẫn là 90°. Đây cũng là thí nghiệm C. Xoay trái: yaw_rate = -30 trong 3 giây từ 200° thì 200 + (-30 * 3) = **110°**.

**Ví dụ 2: vừa tiến vừa xoay (bay vòng cung).** Lệnh `(1, 0, 0, 30)`: tiến 1 m/s và xoay phải 30°/giây liên tục, drone bay thành vòng tròn.

1. Đổi sang radian/giây (radian là đơn vị góc, 360° = 2π): 30 * π / 180 ≈ 0,524 rad/s.
2. Bán kính = vận tốc / tốc độ xoay = 1 / 0,524 ≈ **1,91 m**.
3. Kiểm tra: một vòng xoay hết 360 / 30 = 12 giây; chu vi 2π * 1,91 ≈ 12,0 m; ở 1 m/s đi 12 m mất 12 giây. Khớp.

**Ví dụ 3: đổi sai số pixel thành yaw rate (bài bám người).**

```
sai_số_chuẩn_hóa = (tâm_box_x - tâm_ảnh_x) / (độ_rộng_ảnh / 2)
yaw_rate = K_YAW * sai_số_chuẩn_hóa
```

- `tâm_box_x`: tọa độ ngang (pixel) tâm bounding box quanh người.
- `tâm_ảnh_x`: tâm ảnh = độ rộng ảnh / 2.
- `sai_số_chuẩn_hóa`: chia cho nửa độ rộng ảnh để ra số từ -1 đến +1, không phụ thuộc độ phân giải.
- `K_YAW`: hệ số tự chọn (độ/giây khi lệch hết cỡ).

Ảnh rộng 640 px (tâm ảnh = 320), K_YAW = 40:

| Tâm box (px) | Sai số px | Chuẩn hóa | yaw_rate | Ý nghĩa |
|---|---|---|---|---|
| 480 | 480 - 320 = 160 | 160 / 320 = 0,5 | 40 * 0,5 = **+20°/s** | Lệch phải nhiều, xoay phải nhanh |
| 360 | 40 | 0,125 | 40 * 0,125 = **+5°/s** | Lệch phải ít, xoay phải chậm |
| 320 | 0 | 0 | **0°/s** | Ở giữa, không xoay |
| 100 | 100 - 320 = -220 | -220 / 320 = -0,6875 | 40 * (-0,6875) = **-27,5°/s** | Lệch trái, xoay trái |

Drone xoay thì người dịch về giữa ảnh, sai số giảm, yaw rate giảm theo, về 0 thì dừng xoay. Đây là bộ điều khiển P áp dụng cho yaw. *(Mức [GT]: K_YAW tốt chưa kiểm chứng trên sim, nên chọn nhỏ vì có độ trễ.)* Giải thích chi tiết từng đại lượng (`tâm_box_x`, sai số chuẩn hóa, `K_YAW`) ở [file 03](03_dieu_khien_yaw_tu_anh.md).

**Ví dụ đời thường: ngồi trên ghế xoay.** Bạn là drone, hướng mặt là mũi, mắt là camera.

- **Yaw tuyệt đối (NED):** "hãy nhìn về phía cửa sổ". Bạn phải tự tính cửa sổ nằm ở đâu rồi quay đúng góc.
- **Yaw rate (body frame):** "xoay phải chậm chậm". Bạn chỉ đạp ghế xoay phải, không cần biết mình đang nhìn đâu.

Muốn luôn nhìn thẳng vào bạn A đang đi qua lại trong phòng, bạn dùng quy tắc: A lệch phải thì đạp ghế xoay phải, lệch trái thì xoay trái, ngay trước mặt thì đứng yên, và A lệch càng xa thì xoay càng gấp.

| Trên ghế xoay | Trong code |
|---|---|
| Tốc độ đạp ghế | `yaw_rate` (độ/giây) |
| Đạp sang phải / trái | `yaw_rate` dương / âm |
| A lệch bao xa trong tầm nhìn | sai số tâm box so với tâm ảnh |
| "Lệch nhiều thì xoay mạnh" | `yaw_rate = K_YAW * sai_số` |

Thêm chuyển động: đạp xe tiến đều mà tay lái hơi nghiêng phải thì xe chạy đường cong sang phải (chính là ví dụ 2). Nghiêng nhiều và chạy chậm thì vòng nhỏ, nghiêng ít và chạy nhanh thì vòng rộng.

**Lưu ý:** ví dụ 3 giả định camera nhìn về phía trước, còn camera đang dùng trong Gazebo là `gz_x500_mono_cam_down` (nhìn xuống). Đến bước 3 và 4 phải xét lại (dùng model camera hướng trước hoặc đổi cách tính sai số).

---

## 3. Offboard mode

### 3.1. Offboard là gì

**Offboard là chế độ mà chương trình của bạn trực tiếp lái drone theo thời gian thực**, thay vì để PX4 tự quyết định.

### 3.2. Ví dụ chiếc taxi

PX4 là tài xế, bạn là hành khách.

- **Mission mode:** bạn đưa tài xế một tuyến đường có sẵn ("qua điểm A, rồi B, rồi về"). Tài xế tự lái hết. Đây là cách bạn đã làm với `tha_phao_muc1.plan`.
- **Offboard mode:** bạn ngồi ghế sau nói liên tục "đi thẳng chậm lại... rẽ trái một chút... nhanh lên chút". Tài xế vẫn cầm vô lăng và giữ xe không đổ, nhưng **hướng đi và tốc độ do bạn quyết từng giây**.

### 3.3. Vì sao bài bám người bắt buộc dùng offboard

Mission mode cần biết trước các điểm đến. Nhưng người đi đâu thì không ai biết trước. Chỉ có chương trình của bạn, nhìn qua camera, biết người đang ở đâu ngay lúc này. Nên chương trình phải nói với drone liên tục "người đang lệch phải, hãy dịch phải".

### 3.4. Ai làm việc gì

```
Script của bạn   →  "bay tiến 1 m/s"  →   PX4   →   tốc độ từng động cơ
(quyết định đi đâu)                      (giữ thăng bằng, lo chi tiết)
```

Offboard **không** có nghĩa là bạn điều khiển từng động cơ. Bạn chỉ nói **vận tốc mong muốn**; PX4 tự tính 4 động cơ cần quay nhanh chậm thế nào để đạt vận tốc đó mà vẫn cân bằng.

### 3.5. Ba luật bắt buộc

1. **Phải gửi một lệnh vận tốc trước khi bật offboard**, nếu không PX4 từ chối chuyển chế độ. Thường gửi lệnh "đứng yên" `(0, 0, 0, 0)` làm lệnh đầu. Lý do: lúc đó PX4 chưa biết phải làm gì nếu bạn "giao vô lăng"; lệnh đứng yên là cách nói "cứ giữ nguyên, rồi tôi sẽ chỉ đường sau".
2. **Phải gửi liên tục.** Nếu PX4 không nhận lệnh mới trong khoảng nửa giây, nó tự thoát offboard (cơ chế an toàn, failsafe) và chuyển sang hover hoặc hạ cánh.
3. **Phải đang bay (đã cất cánh) trước khi vào offboard**, để drone không bị giật dưới đất.

### 3.6. Tần suất gửi lệnh

```
tần_suất = 1 / chu_kỳ_gửi
```

**Ví dụ:** gửi mỗi 0,05 giây thì tần suất = 1 / 0,05 = **20 lần/giây**. An toàn vì 0,05 giây nhỏ hơn nhiều so với ngưỡng 0,5 giây. Nếu script bị treo, sau 0,5 giây drone tự dừng, không bay mất.

Trong script bài 3, chu kỳ gửi là 0,1 giây, tức 10 lần/giây.

### 3.7. Hỏi và đáp: offboard có phải là gửi xung liên tục không?

Gần đúng, nhưng cần chỉnh một chữ: bạn gửi liên tục **lệnh vận tốc** (gọi là **setpoint**, giá trị mục tiêu mong muốn), không phải xung điều khiển động cơ.

- Nội dung mỗi lần gửi là câu như "bay tiến 1 m/s, không xoay".
- PX4 nhận câu đó rồi tự tính tốc độ 4 động cơ.
- Tín hiệu xung PWM kiểu điều khiển servo/ESC là tầng thấp bên dưới do PX4 lo, bạn không phải đụng tới.

Ví dụ bay tiến 3 giây (mỗi dòng là một lần gửi):

| Thời điểm | Script gửi | Drone làm |
|---|---|---|
| 0,00 s | tiến 1 m/s | bắt đầu tăng tốc |
| 0,05 s | tiến 1 m/s | tiếp tục |
| 0,10 s | tiến 1 m/s | tiếp tục |
| ... | ... | ... |
| 3,00 s | đứng yên | dừng lại |

Lệnh có thể giống nhau mỗi lần (thí nghiệm A) hoặc khác nhau từng lần (bám người, vì người dịch chuyển nên sai số đổi liên tục).

### 3.8. Tóm tắt 4 bước

1. Cất cánh bình thường.
2. Gửi một lệnh đứng yên.
3. Bật offboard (từ đây script cầm lái).
4. Gửi lệnh vận tốc; hết việc thì gửi đứng yên rồi thoát offboard để PX4 lái lại.

### 3.9. Công thức quãng đường (để kiểm tra thí nghiệm)

```
quãng_đường = vận_tốc * thời_gian
```

**Ví dụ:** tiến 1 m/s trong 3 giây thì đi được 1 * 3 = **3 m**.
