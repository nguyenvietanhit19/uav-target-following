# Ghi chú kiến thức: bài toán drone bám theo mục tiêu

> Tài liệu tổng hợp những gì đã học trong các buổi trước (chưa gồm bộ điều khiển P).
> Mỗi công thức đều có ví dụ số kèm theo. Những chỗ từng hỏi lại được giải thích kỹ ở mục **"Hỏi và đáp"** của từng phần.
> Có thể sửa trực tiếp file này trong VS Code và đẩy lên Git.

## Mục lục

1. [Bức tranh tổng thể](#1-bức-tranh-tổng-thể)
2. [Hệ tọa độ: NED và body frame](#2-hệ-tọa-độ-ned-và-body-frame)
3. [Yaw và yaw rate](#3-yaw-và-yaw-rate)
4. [Offboard mode](#4-offboard-mode)
5. [Viết script MAVSDK (gói `mavsdk_grpc`)](#5-viết-script-mavsdk-gói-mavsdk_grpc)
6. [Kết quả thí nghiệm A và B](#6-kết-quả-thí-nghiệm-a-và-b)
7. [Toán phụ trợ: Pytago, atan2, phép chia lấy dư `%`](#7-toán-phụ-trợ-pytago-atan2-phép-chia-lấy-dư-)
8. [Thị giác máy tính: phát hiện và theo dõi](#8-thị-giác-máy-tính-phát-hiện-và-theo-dõi)
9. [Dự đoán quỹ đạo và Kalman filter](#9-dự-đoán-quỹ-đạo-và-kalman-filter)
10. [Bám người trong đám đông (chống nhảy ID)](#10-bám-người-trong-đám-đông-chống-nhảy-id)
11. [Hai người mặc giống hệt nhau](#11-hai-người-mặc-giống-hệt-nhau)
12. [Lộ trình học](#12-lộ-trình-học)
13. [Bảng thuật ngữ](#13-bảng-thuật-ngữ)
14. [Việc còn dở và câu hỏi mở](#14-việc-còn-dở-và-câu-hỏi-mở)

---

## 1. Bức tranh tổng thể

Bài toán drone bám theo mục tiêu (target following) là một chuỗi ba khâu nối nhau:

```
Nhìn thấy mục tiêu  →  Biết mục tiêu ở đâu  →  Ra lệnh cho drone bay theo
   (thị giác)            (định vị/ước lượng)        (điều khiển)
```

| Khâu | Cần học | Công cụ thường dùng |
|---|---|---|
| Nhìn thấy | Phát hiện vật thể, theo dõi qua các khung hình | YOLO, ByteTrack, DeepSORT |
| Biết ở đâu | Mô hình camera, ước lượng khoảng cách, lọc nhiễu | Pinhole model, Kalman filter |
| Bay theo | Hệ tọa độ, offboard, bộ điều khiển phản hồi | PX4, MAVSDK, PID |

**Thứ tự học nên là từ khâu cuối ngược lại**: học cách điều khiển drone trước (có thể làm ngay vì đã có PX4 SITL + MAVSDK), rồi mới thêm camera và nhận diện. Lý do: nếu nhảy thẳng vào YOLO hay Re-ID mà chưa bay theo nổi một điểm đơn giản, khi drone hành xử lạ sẽ không biết lỗi nằm ở phần nhìn hay phần bay.

---

## 2. Hệ tọa độ: NED và body frame

### 2.1. NED (North - East - Down)

PX4 mô tả vị trí và vận tốc bằng 3 trục gắn với mặt đất:

| Trục | Dương nghĩa là |
|---|---|
| N (North) | hướng **Bắc** |
| E (East) | hướng **Đông** |
| D (Down) | hướng **xuống đất** |

**Trục D hay gây nhầm nhất:** bay lên là D **âm**.

Ví dụ: drone ở độ cao 10 m so với điểm cất cánh thì D = -10. Muốn bay lên với tốc độ 2 m/s thì đặt vận tốc D = -2.

(Gazebo lại hay dùng ENU - East, North, Up - nên khi nối PX4 với Gazebo rất dễ nhầm dấu và thứ tự trục.)

### 2.2. Body frame (hệ tọa độ gắn trên thân drone)

| Trục | Hướng |
|---|---|
| Forward | hướng mũi drone |
| Right | bên phải drone |
| Down | xuống dưới thân drone |

Body frame tiện cho bài bám người: "tiến 1 m/s" luôn là hướng mũi drone, dù mũi đang quay về đâu. Drone tự đổi sang NED giúp bạn.

### 2.3. Công thức đổi từ body frame sang NED

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

### 2.4. Hỏi và đáp

**Hỏi: Nếu ban đầu mũi không hướng về Bắc thì sao?**

Không sao. Xem mục 3.3.

---

## 3. Yaw và yaw rate

### 3.1. Yaw là gì

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

### 3.2. Hai điều dễ nhầm

1. **Yaw là hướng mũi, không phải hướng bay.** Drone có thể mũi nhìn về Đông nhưng đang bay lùi hoặc bay ngang. Giống bạn nhìn về phía trước nhưng bước sang bên.
2. **Vì sao yaw quan trọng với bài bám người:** camera gắn ở mũi drone, mũi quay đi đâu camera nhìn về đó. Muốn người luôn ở giữa khung hình, phải xoay mũi theo người, tức là điều khiển yaw.

### 3.3. Hỏi và đáp: ban đầu mũi không hướng về Bắc thì sao?

**Yaw luôn đo so với hướng Bắc**, không phải so với hướng ban đầu của drone. Bắc là mốc cố định, giống kim la bàn luôn chỉ Bắc dù bạn đứng quay mặt về đâu.

Drone biết yaw hiện tại nhờ **la bàn (magnetometer)** bên trong, nên yaw ban đầu có thể là giá trị bất kỳ.

**Ví dụ thật từ thí nghiệm của bạn:** lúc bắt đầu, hướng mũi drone là **95,9°**, tức là gần hướng Đông chứ không phải Bắc. Khi bạn ra lệnh "tiến" trong body frame, drone bay về phía Đông (xem mục 6).

Quan trọng: **lượng xoay không phụ thuộc yaw ban đầu**, chỉ có hướng cuối cùng thì phụ thuộc.

### 3.4. Yaw rate (tốc độ xoay)

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
- 350 + 30 = 380, rồi 380 % 360 = **20°** (xem phép `%` ở mục 7.3)

**Dấu của yaw rate:**
- Dương: xoay sang **phải** (cùng chiều kim đồng hồ).
- Âm: xoay sang **trái**.

**Ví dụ 4:** yaw rate = -30 độ/giây trong 3 giây, bắt đầu từ 90°.
- yaw_mới = 90 + (-30 * 3) = **0°** (mũi quay từ Đông về Bắc)

### 3.5. Hai kiểu lệnh xử lý yaw khác nhau

| Kiểu lệnh | Ý nghĩa của yaw | Cần biết yaw ban đầu không |
|---|---|---|
| Body frame + yaw rate (`VelocityBodyYawspeed`) | "Xoay thêm 30 độ/giây" | **Không** |
| NED + yaw tuyệt đối (`VelocityNedYaw`) | "Hãy quay mũi về hướng 90°" | Không (drone tự tính phải xoay bao nhiêu) |

**Ví dụ NED + yaw tuyệt đối:** mũi đang ở 45°, lệnh yaw = 90° thì drone xoay thêm 90 - 45 = **45°** sang phải. Mũi đang ở 200°, lệnh yaw = 90° thì drone xoay ngược lại 200 - 90 = **110°** sang trái.

Với bài bám người sẽ dùng kiểu **body frame + yaw rate**, vì chỉ cần nói "người lệch phải thì xoay phải".

---

## 4. Offboard mode

### 4.1. Offboard là gì

**Offboard là chế độ mà chương trình của bạn trực tiếp lái drone theo thời gian thực**, thay vì để PX4 tự quyết định.

### 4.2. Ví dụ chiếc taxi

PX4 là tài xế, bạn là hành khách.

- **Mission mode:** bạn đưa tài xế một tuyến đường có sẵn ("qua điểm A, rồi B, rồi về"). Tài xế tự lái hết. Đây là cách bạn đã làm với `tha_phao_muc1.plan`.
- **Offboard mode:** bạn ngồi ghế sau nói liên tục "đi thẳng chậm lại... rẽ trái một chút... nhanh lên chút". Tài xế vẫn cầm vô lăng và giữ xe không đổ, nhưng **hướng đi và tốc độ do bạn quyết từng giây**.

### 4.3. Vì sao bài bám người bắt buộc dùng offboard

Mission mode cần biết trước các điểm đến. Nhưng người đi đâu thì không ai biết trước. Chỉ có chương trình của bạn, nhìn qua camera, biết người đang ở đâu ngay lúc này. Nên chương trình phải nói với drone liên tục "người đang lệch phải, hãy dịch phải".

### 4.4. Ai làm việc gì

```
Script của bạn   →  "bay tiến 1 m/s"  →   PX4   →   tốc độ từng động cơ
(quyết định đi đâu)                      (giữ thăng bằng, lo chi tiết)
```

Offboard **không** có nghĩa là bạn điều khiển từng động cơ. Bạn chỉ nói **vận tốc mong muốn**; PX4 tự tính 4 động cơ cần quay nhanh chậm thế nào để đạt vận tốc đó mà vẫn cân bằng.

### 4.5. Ba luật bắt buộc

1. **Phải gửi một lệnh vận tốc trước khi bật offboard**, nếu không PX4 từ chối chuyển chế độ. Thường gửi lệnh "đứng yên" `(0, 0, 0, 0)` làm lệnh đầu. Lý do: lúc đó PX4 chưa biết phải làm gì nếu bạn "giao vô lăng"; lệnh đứng yên là cách nói "cứ giữ nguyên, rồi tôi sẽ chỉ đường sau".
2. **Phải gửi liên tục.** Nếu PX4 không nhận lệnh mới trong khoảng nửa giây, nó tự thoát offboard (cơ chế an toàn, failsafe) và chuyển sang hover hoặc hạ cánh.
3. **Phải đang bay (đã cất cánh) trước khi vào offboard**, để drone không bị giật dưới đất.

### 4.6. Tần suất gửi lệnh

```
tần_suất = 1 / chu_kỳ_gửi
```

**Ví dụ:** gửi mỗi 0,05 giây thì tần suất = 1 / 0,05 = **20 lần/giây**. An toàn vì 0,05 giây nhỏ hơn nhiều so với ngưỡng 0,5 giây. Nếu script bị treo, sau 0,5 giây drone tự dừng, không bay mất.

Trong script bài 3, chu kỳ gửi là 0,1 giây, tức 10 lần/giây.

### 4.7. Hỏi và đáp: offboard có phải là gửi xung liên tục không?

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

### 4.8. Tóm tắt 4 bước

1. Cất cánh bình thường.
2. Gửi một lệnh đứng yên.
3. Bật offboard (từ đây script cầm lái).
4. Gửi lệnh vận tốc; hết việc thì gửi đứng yên rồi thoát offboard để PX4 lái lại.

### 4.9. Công thức quãng đường (để kiểm tra thí nghiệm)

```
quãng_đường = vận_tốc * thời_gian
```

**Ví dụ:** tiến 1 m/s trong 3 giây thì đi được 1 * 3 = **3 m**.

---

## 5. Viết script MAVSDK (gói `mavsdk_grpc`)

### 5.1. Môi trường đang dùng

- Chạy trên Windows, thư mục `D:\Intern iVista\UAV\mavsdk` (có venv `.venv`).
- MAVSDK 4.x có API mới làm hỏng script cũ nên đã chuyển sang gói **`mavsdk_grpc`**.
- Kết nối tới sim qua `udpin://0.0.0.0:14540` (QGroundControl dùng cổng 14550 nên hai bên không giành nhau).

### 5.2. Import

```python
from mavsdk_grpc import System
from mavsdk_grpc.offboard import OffboardError, VelocityBodyYawspeed, VelocityNedYaw
```

### 5.3. Hai kiểu lệnh vận tốc

```python
# Body frame: (tiến, phải, xuống, yaw_rate độ/giây)
VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0)

# NED: (bắc, đông, xuống, yaw tuyệt đối độ)
VelocityNedYaw(1.0, 0.0, 0.0, 90.0)
```

Gửi bằng:

```python
await drone.offboard.set_velocity_body(...)   # cho body frame
await drone.offboard.set_velocity_ned(...)    # cho NED
```

### 5.4. Khung chương trình

```python
# (đã cất cánh xong rồi mới tới đây)

# 1. Gửi lệnh "đứng yên" trước (luật 1)
await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

# 2. Bật offboard
await drone.offboard.start()

# 3. Gửi lệnh vận tốc LIÊN TỤC (ví dụ 10 lần/giây trong 3 giây)
for _ in range(30):
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(0.1)

# 4. Dừng lại rồi thoát offboard
await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
await asyncio.sleep(2)
await drone.offboard.stop()
```

### 5.5. Đọc dữ liệu từ drone

```python
# Vị trí so với điểm Home (bắc, đông)
async for pv in drone.telemetry.position_velocity_ned():
    print(pv.position.north_m, pv.position.east_m)
    break

# Hướng mũi (yaw), độ
async for h in drone.telemetry.heading():
    print(h.heading_deg)
    break
```

### 5.6. Cấu trúc file `buoc3_offboard.py`

Chạy bằng `python buoc3_offboard.py A` (hoặc `B`, `C`). Mỗi lần: kết nối, cất cánh 10 m, đo trước, vào offboard, gửi lệnh liên tục, đo sau, thoát offboard, in kết quả, hạ cánh.

| Hàm | Việc làm |
|---|---|
| `ket_noi_va_cat_canh` | kết nối, chờ GPS, cất cánh, chờ đạt khoảng 90% độ cao |
| `vao_offboard` | gửi lệnh đứng yên trước, rồi `offboard.start()` |
| `gui_lenh_lien_tuc` | gửi một lệnh lặp lại mỗi `CHU_KY_GUI` giây |
| `thoat_offboard` | gửi đứng yên 2 giây rồi `offboard.stop()` |

Ba thí nghiệm:

| Thí nghiệm | Lệnh | Kỳ vọng |
|---|---|---|
| A | body `(1, 0, 0, 0)` trong 3 giây | đi khoảng 3 m theo hướng mũi |
| B | NED `(1, 0, 0, yaw=90)` trong 3 giây | đi khoảng 3 m về Bắc, mũi hướng Đông |
| C | body `(0, 0, 0, 30)` trong 3 giây | đứng yên, mũi xoay thêm khoảng 90° |

---

## 6. Kết quả thí nghiệm A và B

### 6.1. Thí nghiệm A: tiến 1 m/s trong 3 giây (body frame)

Số liệu thô:

```
Trước:             hướng mũi 95.9°, vị trí (bắc 0.00, đông 0.00)
Sau khi gửi lệnh:  vị trí (bắc -0.06, đông 1.44), hướng mũi 93.5°
Sau khi dừng hẳn:  vị trí (bắc -0.12, đông 2.01), hướng mũi 92.0°
Quãng đường:       2.01 m
Thay đổi bắc:      -0.11 m, thay đổi đông: +2.01 m
Mũi xoay thêm:     -3.8°
```

**Cách đọc từng dòng:**

- **Bắc, đông** là vị trí so với điểm Home, tính bằng mét. Bắc âm = lệch về phía Nam. Đông dương = đã đi về phía Đông.
- **Hai dòng "Sau khi gửi lệnh" và "Sau khi dừng hẳn"** đo ở hai thời điểm khác nhau. Drone đang chạy thì không dừng ngay mà trượt thêm một đoạn khi phanh: 2,01 - 1,44 = **0,57 m**. (Số ở dòng 1 còn có thể hơi cũ vì telemetry cập nhật chậm.)
- **Quãng đường** là khoảng cách thẳng từ chỗ bắt đầu đến chỗ dừng (Pytago, xem mục 7.1): √(0,12² + 2,01²) = √4,0545 ≈ **2,01 m**.
- **Thay đổi** = vị trí sau - vị trí trước. Đông: 2,01 - 0 = +2,01 m. Bắc: -0,11 m (trôi nhẹ về Nam).
  - Vì sao -0,11 mà không phải -0,12: do làm tròn khi in (ví dụ vị trí "trước" thực ra là -0,004, in ra thành -0,00).
- **Mũi xoay thêm** = `(yaw_sau - yaw_trước + 180) % 360 - 180` = (92,0 - 95,9 + 180) % 360 - 180 = 176,1 - 180 = **-3,9°** (in -3,8° vì số thực chưa làm tròn). Dấu âm = xoay nhẹ sang trái.

**Kiểm tra hướng đi khớp lý thuyết:** yaw ban đầu 95,9°, tiến 1 m/s.

- north = 1 * cos(95,9°) = 1 * (-0,103) = **-0,10 m/s**
- east = 1 * sin(95,9°) = 1 * 0,995 = **+0,99 m/s**
- Trong 3 giây, công thức dự đoán north ≈ -0,31 m và east ≈ +2,99 m. Đo được -0,12 và +2,01: cùng dấu, cùng hướng, chỉ độ lớn nhỏ hơn.

Hướng bay thực tế (mục 7.2): bearing = atan2(2,01; -0,12) ≈ **93,4°**, gần như trùng hướng mũi (92 đến 96°). Vậy drone đi đúng theo hướng mũi như lệnh "tiến" trong body frame.

### 6.2. Thí nghiệm B: bay về Bắc 1 m/s, mũi hướng Đông (NED)

Số liệu thô (lưu ý: chưa khởi động lại sim sau thí nghiệm A nên vị trí "Trước" không phải (0, 0), nhưng script dùng **hiệu** nên vẫn đúng):

```
Trước:             vị trí (bắc -0.14, đông 2.06), hướng mũi 92.6°
Sau khi gửi lệnh:  vị trí (bắc 1.33, đông 2.03), hướng mũi 90.1°
Sau khi dừng hẳn:  vị trí (bắc 1.92, đông 2.04), hướng mũi 89.9°
Quãng đường:       2.06 m
Thay đổi bắc:      +2.06 m, thay đổi đông: -0.02 m
Mũi xoay thêm:     -2.8°
```

- Thay đổi bắc = 1,92 - (-0,14) = **+2,06 m** (đi về Bắc).
- Thay đổi đông = 2,04 - 2,06 = **-0,02 m** (gần như không dịch).
- Hướng mũi tiến về 90° (Đông) đúng như lệnh.
- Hướng bay: bearing = atan2(-0,02; 2,06) ≈ -0,56°, và -0,56 % 360 = **359,4°** (gần đúng Bắc).

**Điểm mấu chốt:** hướng bay 359,4° (Bắc) còn hướng mũi 89,9° (Đông), lệch nhau khoảng 90°. Đó là khác biệt giữa lệnh NED (hướng bay tách khỏi hướng mũi) và lệnh body frame ở thí nghiệm A (bay theo mũi).

**Hạn chế của thí nghiệm B:** mũi drone vốn đã ở 92,6°, gần 90° sẵn, nên lệnh "yaw = 90°" gần như không làm mũi xoay. Muốn thấy rõ hơn, đổi yaw thành 180° (bay về Bắc nhưng mũi quay về Nam, tức drone bay lùi).

### 6.3. So sánh A và B

| | A (tiến theo mũi) | B (bay Bắc, mũi Đông) |
|---|---|---|
| Đi được sau khi gửi lệnh | 1,44 m | 1,47 m |
| Đi được sau khi dừng hẳn | 2,01 m | 2,06 m |
| Đi thêm lúc phanh | 0,57 m | 0,59 m |
| So với kỳ vọng 3 m | 67% | 69% |

Hai thí nghiệm dùng hai hệ tọa độ khác nhau mà kết quả gần như trùng nhau. Vậy "thiếu quãng đường" **không do hệ tọa độ**.

### 6.4. Vì sao chỉ đi được khoảng 2 m thay vì 3 m

Có hai nguyên nhân có thể cùng góp phần (chưa kiểm chứng xong, xem mục 14):

1. **Thời gian sim chạy chậm hơn thời gian thật (real-time factor, RTF).**
   - RTF là hệ số: thời gian sim / thời gian thật. Gazebo trên máy bạn chỉ chạy khoảng 50 đến 60%.
   - Script dùng `asyncio.sleep` đếm theo **thời gian thật**, nhưng drone bay theo **thời gian sim**.
   - Công thức: `thời_gian_sim = thời_gian_thật * RTF`.
   - **Ví dụ:** RTF = 0,6, gửi lệnh 3 giây thật → thời gian sim = 3 * 0,6 = 1,8 giây → quãng đường = 1 * 1,8 = **1,8 m**.
   - Đo được 2,01 m (A) và 2,06 m (B), tỉ lệ 0,67 và 0,69, nằm trong khoảng RTF 0,6 đến 0,7. Khớp khá tốt.
2. **Drone tăng tốc từ từ (ramp).** PX4 làm mượt lệnh vận tốc nên không đạt ngay 1 m/s. Ví dụ nếu mất 1,5 giây để lên tới 1 m/s thì đi được 1 * (3 - 0,75) = 2,25 m.

**Cách phân biệt:** in vận tốc thực tế của drone mỗi 0,5 giây. Vận tốc đo bằng m/s của thế giới ảo nên không phụ thuộc RTF. Nếu vận tốc lên gần 1,0 m/s rồi ổn định thì drone bay đúng lệnh và thiếu quãng đường là do RTF. Nếu chỉ lên khoảng 0,6 m/s thì drone thật sự chậm hơn lệnh. Cách đơn giản khác: nhìn ô Real Time Factor ở góc dưới cửa sổ Gazebo.

**Ý nghĩa cho bài bám người:** tần số camera, tần số gửi lệnh đều chạy theo thời gian thật nên trong sim RTF thấp sẽ khiến vòng điều khiển phản ứng chậm hơn bạn nghĩ. Trên drone thật RTF luôn bằng 1.

---

## 7. Toán phụ trợ: Pytago, atan2, phép chia lấy dư `%`

### 7.1. Khoảng cách trên mặt phẳng (Pytago)

```
khoảng_cách = √(Δbắc² + Δđông²)
```

**Ví dụ:** bắc = -3, đông = +4 → √(3² + 4²) = √25 = **5 m**.

### 7.2. Hướng và bearing (atan2)

**Đọc dấu của vị trí:**

- Bắc càng **âm** → càng xa Home về phía **Nam**. Bắc càng dương → càng xa về phía Bắc.
- Đông càng **dương** → càng xa về phía **Đông**. Đông càng âm → càng xa về phía Tây.

Ghép hai trục:

| Bắc | Đông | Drone ở phía |
|---|---|---|
| dương | dương | Đông Bắc |
| âm | dương | Đông Nam |
| âm | âm | Tây Nam |
| dương | âm | Tây Bắc |

Mức xa thì phụ thuộc độ lớn từng số; hướng thì phụ thuộc **tỉ lệ** giữa hai số.

**Bearing** (hướng la bàn của vector vị trí):

```
bearing = atan2(đông, bắc), đổi sang độ, rồi % 360
```

`atan2` là hàm tính góc từ hai số, cho đúng góc ở cả bốn phía (khác arctang thường vốn dễ nhầm khi số âm). Kết quả theo quy ước la bàn: 0° Bắc, 90° Đông, 180° Nam, 270° Tây.

**Ví dụ 1:** bắc = -3, đông = +4.
- khoảng cách = 5 m
- bearing = atan2(4; -3) = 180° - 53,1° = **126,9°** (giữa Đông 90° và Nam 180° → Đông Nam)

**Ví dụ 2 (số thật của thí nghiệm A):** bắc = -0,12, đông = +2,01.
- bearing = 90° + atan(0,12 / 2,01) = 90° + 3,4° = **93,4°**

Nếu đông rất lớn, bắc nhỏ → bearing tiến sát 90° (thẳng Đông). Nếu bắc âm bằng độ lớn đông → bearing 135° (Đông Nam chính xác).

### 7.3. Phép `%` (chia lấy phần dư, modulo)

`%` **không phải phần trăm**. `a % n` là chia `a` cho `n` rồi lấy phần còn thừa.

**Ví dụ đồng hồ:** đồng hồ chỉ có 12 giờ rồi quay lại. 15 giờ chiều kim chỉ số mấy?
- 15 % 12 = 3 (15 chia 12 được 1, dư 3) → kim chỉ số 3.

Góc cũng quay vòng như vậy, một vòng là 360°. `% 360` đưa một góc bất kỳ về khoảng 0° đến dưới 360°.

```
a % n = a - n * (số lần n "chứa" trọn trong a)
```

| Ví dụ | Tính | Kết quả |
|---|---|---|
| yaw = 380° (xoay hơn một vòng) | 380 - 360 * 1 | **20°** |
| yaw = 720° (hai vòng) | 720 - 360 * 2 | **0°** |
| -178 % 360 (số âm, Python giữ kết quả không âm) | -178 - 360 * (-1) = -178 + 360 | **182** |

### 7.4. Công thức góc xoay `(a - b + 180) % 360 - 180`

Trong script:

```python
goc_xoay = (yaw_sau - yaw_truoc + 180) % 360 - 180
```

Mục đích: ra góc xoay trong khoảng **-180° đến +180°** (xoay trái hoặc phải theo **đường ngắn**).

Ba bước:

1. `% 360` đưa về khoảng 0 đến 360.
2. Nhưng muốn khoảng -180 đến +180, nên cộng `+ 180` **trước** khi lấy dư để mốc "không xoay" nằm giữa khoảng.
3. Rồi trừ `- 180` sau cùng để đưa mốc đó về 0.

**Ví dụ vượt qua hướng Bắc:** yaw trước = 359°, yaw sau = 1°.
- 1 - 359 + 180 = -178
- -178 % 360 = 182
- 182 - 180 = **+2°** (xoay phải 2°)
- Nếu chỉ trừ thẳng 1 - 359 = -358°: sai hoàn toàn (mũi chỉ xoay 2°).

Với bearing thuần 0 đến 360 thì chỉ cần `bearing % 360`.

---

## 8. Thị giác máy tính: phát hiện và theo dõi

### 8.1. Object detection (phát hiện vật thể)

Tìm khung chữ nhật (**bounding box**) bao quanh mục tiêu trong ảnh, ví dụ bằng **YOLO**. Mỗi khung hình được xử lý độc lập, không nhớ khung trước.

### 8.2. Object tracking (theo dõi qua các khung hình)

Giữ nguyên "danh tính" mục tiêu từ khung này sang khung khác. Các thuật toán hay gặp:

| Thuật toán | Đặc điểm |
|---|---|
| KCF, CSRT | nhẹ, chạy trực tiếp trên ảnh |
| SORT, ByteTrack | kết hợp detection với tracking, chủ yếu dựa vào chuyển động và IoU |
| DeepSORT, StrongSORT, BoT-SORT | thêm nhận diện ngoại hình (Re-ID), chống nhảy ID tốt hơn |

**Vì sao cần tracking:** detection có thể bỏ sót vài khung hình; tracking giúp mục tiêu không bị "mất dấu" ngay lúc đó.

**IoU** (intersection over union) là độ chồng lấn giữa hai khung: diện tích phần giao chia diện tích phần hợp. Càng gần 1 càng trùng nhau.

### 8.3. Mô hình camera và ước lượng vị trí

- **Pinhole camera model** (mô hình lỗ kim): cách một điểm 3D chiếu thành pixel 2D.
- **FOV** (field of view) là góc nhìn; **intrinsics** là thông số trong của camera (như tiêu cự).
- Từ pixel suy ra góc lệch của mục tiêu so với trục camera.
- Từ kích thước bounding box ước lượng khoảng cách: box càng to thì mục tiêu càng gần.

### 8.4. Visual servoing (kết hợp tất cả)

Dùng ảnh để điều khiển trực tiếp: giữ mục tiêu ở giữa khung hình (điều khiển yaw hoặc dịch ngang) và giữ khoảng cách không đổi (điều khiển tiến/lùi theo kích thước box).

---

## 9. Dự đoán quỹ đạo và Kalman filter

### 9.1. Hỏi và đáp: dự đoán quỹ đạo có phải dựa vào vector chuyển động không?

Đúng, nhưng vector chuyển động mới chỉ là phần đơn giản nhất. Dự đoán quỹ đạo là dùng **vị trí và vận tốc hiện tại** để đoán vị trí ở khung hình tiếp theo.

### 9.2. Mô hình vận tốc không đổi

```
p_dự_đoán = p_hiện_tại + v * Δt
```

(`p` là vị trí, `v` là vận tốc, `Δt` là thời gian giữa hai khung hình.)

**Ví dụ:** người ở x = 300 px, di chuyển sang phải 60 px/giây, camera 30 khung/giây nên Δt = 1/30 giây.
- p_dự_đoán = 300 + 60 * (1/30) = 300 + 2 = **302 px**

Vận tốc tính từ hai vị trí gần nhất: khung trước x = 298, khung này x = 300 → v = (300 - 298) / (1/30) = **60 px/giây**.

### 9.3. Vì sao cần Kalman filter chứ không chỉ cộng vector

Hai điểm yếu của cộng vector thô:

- **Đo đạc nhiễu:** box rung nhẹ từng khung, vận tốc tính từ hai khung gần nhau dao động mạnh. Ví dụ box nhảy từ 298 sang 303 (nhiễu) cho v = 5 / (1/30) = **150 px/giây**, sai hẳn so với thực tế 60.
- **Mất dấu tạm thời:** khi bị che không có phép đo mới, cộng vector thô sẽ lệch dần.

**Kalman filter** giữ một ước lượng (vị trí và vận tốc) cùng với **độ không chắc chắn** của nó. Mỗi khung hình làm hai bước:

1. **Dự đoán:** dùng `p + v * Δt`, độ không chắc chắn tăng lên.
2. **Cập nhật:** khi có phép đo mới, trộn phép đo với dự đoán theo tỉ lệ tùy bên nào đáng tin hơn (đo nhiễu nhiều thì tin dự đoán hơn, và ngược lại).

Kết quả: vận tốc mượt hơn nhiều.

### 9.4. Hai lưu ý

- Giả định vận tốc không đổi chỉ đúng trong thời gian ngắn. Người rẽ đột ngột hay dừng lại thì dự đoán lệch; khi mất dấu lâu, vùng tìm kiếm phải mở rộng dần (đây là lý do Kalman cho độ không chắc chắn tăng theo thời gian).
- Drone cũng đang bay và xoay nên vị trí trong ảnh đổi kể cả khi người đứng yên. Cách tốt là dự đoán trong **hệ tọa độ thế giới** (dùng vị trí và hướng của drone từ PX4) rồi chiếu ngược vào ảnh. Bài thử đầu tiên có thể dự đoán thẳng trong pixel, nhưng nên biết giới hạn này.

---

## 10. Bám người trong đám đông (chống nhảy ID)

### 10.1. Vấn đề

**ID switch** (nhảy mã định danh): tracker đang gán "ID 7" cho người cần theo, nhưng khi hai người giao nhau hoặc che nhau, nó gán nhầm ID 7 sang người bên cạnh. Chỉ dùng vị trí trong ảnh thì gần như chắc chắn bị nhảy trong đám đông. Giải pháp là kết hợp nhiều lớp phòng thủ.

### 10.2. Lớp 1: nhận diện bằng ngoại hình (Re-ID)

**Re-ID** (re-identification, nhận diện lại): dùng một mạng nơ-ron (ví dụ OSNet) biến ảnh cắt của một người thành một vector số gọi là **embedding** (chứa màu áo, dáng người, quần, giày...). Hai ảnh của cùng một người cho hai vector gần giống nhau.

Đo độ giống bằng **cosine similarity** (từ -1 đến 1, càng gần 1 càng giống):

```
cos(a, b) = (a · b) / (|a| * |b|)
```

**Ví dụ (vector 2 chiều cho dễ tính):** mục tiêu a = (3, 4), ứng viên b = (4, 3).
- a · b = 3*4 + 4*3 = 24
- |a| = 5, |b| = 5
- cos = 24 / 25 = **0,96** (rất giống)

Ứng viên c = (4, -3): a · c = 12 - 12 = 0 → cos = **0** (hoàn toàn khác).

Trước khi bay "khóa mục tiêu": chụp vài ảnh người cần theo (nhiều góc nhìn) và lưu embedding làm mẫu (**gallery**).

### 10.3. Lớp 2: dự đoán chuyển động và gating

Dùng Kalman filter dự đoán người đó sẽ ở đâu ở khung hình tiếp theo. **Gating** (đặt cổng lọc): người nào nằm quá xa vị trí dự đoán thì loại luôn, không cần xét ngoại hình. Tránh trường hợp người giống áo nhưng đứng cách xa vẫn bị chọn nhầm.

### 10.4. Lớp 3: gộp thành một chi phí để chọn

```
cost = λ * (1 - cos) + (1 - λ) * d_motion
```

`d_motion` là khoảng cách tới vị trí dự đoán đã chuẩn hóa về 0 đến 1; `λ` là trọng số ưu tiên ngoại hình. Cost càng thấp càng đúng.

**Ví dụ λ = 0,7:**
- Ứng viên A: cos = 0,96, d_motion = 0,4 → cost = 0,7 * 0,04 + 0,3 * 0,4 = 0,028 + 0,12 = **0,148**
- Ứng viên B: cos = 0,30, d_motion = 0,1 → cost = 0,7 * 0,70 + 0,3 * 0,1 = 0,49 + 0,03 = **0,52**

B đứng gần vị trí dự đoán hơn nhưng trông khác hẳn, nên A vẫn thắng. Khi có nhiều người, thuật toán **Hungarian** (ghép cặp tối ưu) ghép sao cho tổng chi phí nhỏ nhất. Đây là cách DeepSORT, StrongSORT, BoT-SORT hoạt động.

### 10.5. Lớp 4: xử lý lúc bị che khuất - thà mất mục tiêu còn hơn bám nhầm

- **Đặt ngưỡng:** chỉ nhận ứng viên nếu cos lớn hơn một ngưỡng cao (ví dụ 0,8). Không ai đạt ngưỡng thì coi như mất dấu.
- **Khi mất dấu:** ngừng cập nhật mẫu ngoại hình, để Kalman tiếp tục dự đoán, tìm lại trong vùng rộng dần quanh vị trí cuối cùng.
- **Chỉ nhận lại** khi có ứng viên vượt ngưỡng trong nhiều khung liên tiếp (ví dụ 5 khung), tránh nhận nhầm do một khung ngẫu nhiên.
- **Lệnh bay an toàn:** lúc mất dấu cho drone giảm tốc rồi hover (đứng yên) thay vì lao theo người gần nhất.

### 10.6. Lớp 5: cập nhật mẫu ngoại hình rất chậm (EMA)

Ngoại hình đổi theo góc nhìn và ánh sáng nên mẫu cần cập nhật, nhưng phải chậm và chỉ khi chắc chắn. **EMA** (exponential moving average, trung bình trượt có trọng số):

```
f_mới = α * f_hiện_tại + (1 - α) * f_cũ
```

**Ví dụ (một thành phần của vector):** f_cũ = 0,8, f_hiện_tại = 0,4, α = 0,1.
- f_mới = 0,1 * 0,4 + 0,9 * 0,8 = 0,04 + 0,72 = **0,76**

Mẫu chỉ nhích nhẹ, nên nếu một khung bị nhầm sang người khác thì mẫu không bị "nhiễm" ngay. Chỉ cập nhật khi cos cao và mục tiêu không bị che.

### 10.7. Mẹo bổ sung

- Camera trên **gimbal** (giá đỡ xoay ổn định) giúp ảnh ổn định.
- Dùng nhiều đặc trưng: Re-ID toàn thân, biểu đồ màu áo/quần, tỉ lệ khung chiều cao/rộng.
- Cảm biến phụ (nếu được phép): GPS từ điện thoại người đó, hoặc thẻ UWB.
- ByteTrack rất tốt trong đám đông nhưng chủ yếu dựa vào chuyển động và IoU, nên một mình nó vẫn hay nhảy ID. Nên dùng bản có Re-ID.

---

## 11. Hai người mặc giống hệt nhau

### 11.1. Thực tế thẳng thắn

**Chỉ dựa vào ngoại hình thì không thể phân biệt được**, vì hai embedding gần như trùng nhau (cos ≈ 0,95 với cả hai người). Hệ thống phải dựa vào nguồn thông tin khác, và quan trọng hơn là biết khi nào mình không chắc để dừng lại.

### 11.2. Dựa vào chuyển động và tính liên tục

- Khi hai người ở xa nhau, Kalman filter vẫn theo đúng người. Rủi ro chỉ xảy ra **lúc họ giao nhau hoặc che nhau**.
- Giữ **quỹ đạo** của mục tiêu: hướng đi, tốc độ, gia tốc. Người đi thẳng 1,2 m/s khó lẫn với người đứng yên hay đi ngược chiều.
- Sau giao nhau, nếu có hai ứng viên đều khớp ngoại hình, chọn người **khớp quỹ đạo dự đoán hơn**. Nếu hai người đi song song cùng vận tốc thì cách này cũng hết tác dụng.

### 11.3. Phát hiện tình huống mơ hồ (ambiguity)

```
độ_mơ_hồ = cos(ứng viên 2) / cos(ứng viên 1)
```

Tỉ số gần 1 nghĩa là hai người giống nhau ngang nhau, không có căn cứ chọn.

**Ví dụ:**
- A có cos = 0,95, B có cos = 0,93 → tỉ số = 0,93 / 0,95 = **0,98** (rất mơ hồ).
- A có cos = 0,95, B có cos = 0,60 → tỉ số = 0,60 / 0,95 = **0,63** (rõ ràng, chọn A).

Quy tắc: nếu tỉ số vượt ngưỡng (ví dụ > 0,9) và hai người đang ở gần nhau thì:

- **Đóng băng mẫu ngoại hình** (không cập nhật EMA để khỏi nhiễm).
- **Giảm tốc, giữ khoảng cách an toàn**, không bám sát nữa.
- **Không đổi ID mục tiêu** cho đến khi có bằng chứng chắc chắn.

### 11.4. Tìm đặc điểm phân biệt nhỏ hơn

- Dáng đi, chiều cao, vóc người (gait recognition cần video dài nên ít dùng thực tế).
- Phụ kiện: balo, mũ, giày, túi. Nếu kiểm soát được kịch bản, yêu cầu mục tiêu mang một vật đặc trưng (mũ màu rực).
- Khuôn mặt: chính xác nhất nhưng chỉ dùng được khi nhìn thấy mặt (gần, góc phù hợp). Cần cân nhắc quyền riêng tư.

### 11.5. Thêm cảm biến định danh bên ngoài (đáng tin nhất)

| Phương án | Độ chính xác | Ghi chú |
|---|---|---|
| GPS điện thoại/thiết bị đeo | khoảng 3 đến 5 m | hai người đứng sát nhau vẫn khó phân biệt |
| UWB (ultra-wideband, băng siêu rộng) | khoảng 10 đến 30 cm | thẻ nhỏ người đó mang, phân biệt được hai người đứng cạnh nhau |
| AprilTag (mã vuông giống QR) gắn trên lưng áo | đọc được là biết chắc ID | đơn giản và rẻ, dùng tốt khi thử nghiệm |

### 11.6. Thiết kế hành vi theo mức độ chắc chắn

| Trạng thái | Điều kiện | Hành động của drone |
|---|---|---|
| Chắc chắn | cos cao, tỉ số mơ hồ thấp | Bám bình thường |
| Mơ hồ | Hai ứng viên giống nhau | Giảm tốc, giữ khoảng cách, chờ |
| Mất dấu | Không ai đạt ngưỡng | Hover và tìm lại |

Khi ra khỏi vùng mơ hồ (hai người tách nhau), dùng quỹ đạo và vị trí liên tục để nối lại danh tính rồi mới tiếp tục bám.

### 11.7. Kết luận thực tế

- Nếu chỉ có camera và hai người giống hệt nhau đi sát nhau liên tục, **không có giải pháp nào đảm bảo 100%**. Đó là giới hạn của bài toán, không phải lỗi thuật toán.
- Tốt nhất là kết hợp: quỹ đạo + phát hiện mơ hồ + hành vi thận trọng, rồi thêm AprilTag hoặc UWB nếu cần độ tin cậy cao.
- Với đồ án hoặc demo, nên bắt đầu bằng **AprilTag trên lưng áo** vì dễ làm trong Gazebo và cho kết quả chắc chắn để kiểm chứng phần còn lại.

---

## 12. Lộ trình học

| Bước | Nội dung | Mục tiêu kiểm tra | Trạng thái |
|---|---|---|---|
| 1 | Hệ tọa độ + offboard (script `buoc3_offboard.py`) | Bay tiến 1 m/s trong 3 giây và xem đi đúng hướng | Đã xong A, B; còn C |
| 2 | Bộ điều khiển P bám theo điểm ảo di chuyển | Drone bám điểm ảo, giữ khoảng cách khoảng 5 m | Chưa làm |
| 3 | Lấy hình từ camera trong Gazebo (OpenCV) | Hiển thị được video từ drone | Chưa làm |
| 4 | Phát hiện người (YOLO) | Lấy bounding box, nối với bước 2 (sai số giữa tâm box và tâm ảnh) | Chưa làm |
| 5 | Tracking, Re-ID, Kalman, xử lý đám đông | Đo số lần ID switch trên mỗi video | Chưa làm |

**Vì sao không nên học Re-ID hay Kalman trước:** hai phần đó giải quyết vấn đề nâng cao (đám đông, che khuất). Khi chưa có drone bám được một người đơn giản thì chưa có gì để cải thiện và cũng không kiểm chứng được chúng có hiệu quả hay không.

---

## 13. Bảng thuật ngữ

| Thuật ngữ | Giải thích ngắn |
|---|---|
| NED / ENU | Hệ tọa độ Bắc-Đông-Xuống (PX4) / Đông-Bắc-Lên (Gazebo) |
| Body frame | Hệ tọa độ gắn trên thân drone (tiến, phải, xuống) |
| Yaw | Góc hướng mũi drone so với hướng Bắc |
| Yaw rate | Tốc độ xoay mũi, độ/giây |
| Setpoint | Giá trị mục tiêu mong muốn gửi cho drone (ví dụ vận tốc) |
| Offboard mode | Chế độ cho chương trình ngoài gửi lệnh liên tục để lái drone |
| Failsafe | Cơ chế an toàn tự kích hoạt khi mất lệnh/mất kết nối |
| Telemetry | Dữ liệu drone báo về (vị trí, hướng, độ cao...) |
| Home | Điểm cất cánh dùng làm gốc tọa độ |
| RTF (real-time factor) | Tỉ lệ thời gian sim so với thời gian thật |
| Bearing | Hướng la bàn của một vector (0° Bắc, 90° Đông) |
| Modulo `%` | Phép chia lấy phần dư |
| atan2 | Hàm tính góc đúng ở cả bốn phía từ hai số |
| Bounding box | Khung chữ nhật bao quanh vật thể trong ảnh |
| IoU | Độ chồng lấn giữa hai khung (phần giao / phần hợp) |
| Detection | Phát hiện vật thể trong một ảnh |
| Tracking | Theo dõi vật thể qua nhiều khung hình |
| ID switch | Tracker gán nhầm mã định danh sang người khác |
| Re-ID | Nhận diện lại một người bằng ngoại hình |
| Embedding | Vector số đại diện cho ngoại hình một người |
| Cosine similarity | Độ giống giữa hai vector, từ -1 đến 1 |
| Gallery | Tập embedding mẫu của mục tiêu đã khóa |
| Gating | Loại ứng viên quá xa vị trí dự đoán |
| Hungarian | Thuật toán ghép cặp tối ưu theo chi phí |
| EMA | Trung bình trượt có trọng số, dùng để cập nhật mẫu chậm |
| Kalman filter | Bộ lọc làm mượt phép đo và dự đoán vị trí kế tiếp |
| Pinhole model | Mô hình lỗ kim chiếu điểm 3D thành pixel 2D |
| FOV | Góc nhìn của camera |
| Visual servoing | Dùng ảnh để điều khiển trực tiếp chuyển động |
| Gimbal | Giá đỡ camera xoay ổn định |
| UWB | Công nghệ định vị băng siêu rộng, chính xác cỡ 10 đến 30 cm |
| AprilTag | Mã vuông (giống QR) để nhận dạng ID bằng camera |

---

## 14. Việc còn dở và câu hỏi mở

- [ ] **Chạy thí nghiệm C** (xoay 30 độ/giây trong 3 giây). Kỳ vọng: vị trí gần như không đổi, mũi xoay thêm khoảng +90°. Dán kết quả vào ghi chú này.
- [ ] **Kiểm chứng nguyên nhân thiếu quãng đường** (mục 6.4): đọc ô Real Time Factor trong Gazebo, và/hoặc thêm đoạn in vận tốc thực tế mỗi 0,5 giây vào `buoc3_offboard.py`. Hoặc thử `so_giay = 6` và xem quãng đường có gần 6 m hay chỉ khoảng 4 m.
- [ ] **Khởi động lại sim** giữa các thí nghiệm để vị trí bắt đầu lại từ (0, 0), dễ so sánh hơn.
- [ ] **Thử B với yaw = 180°** để thấy rõ hướng bay tách khỏi hướng mũi (drone bay lùi).
- [ ] Sau đó sang bước 2 của lộ trình: bộ điều khiển P bám theo điểm ảo.

### Ghi chú của riêng bạn

<!-- Sửa trực tiếp ở đây trong VS Code -->

