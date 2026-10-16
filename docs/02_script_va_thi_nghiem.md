# 02. Script MAVSDK và kết quả thí nghiệm

> [Về mục lục chính](../kien_thuc_drone_bam_muc_tieu.md) · Trước: [01](01_he_toa_do_yaw_offboard.md) · Tiếp: [03](03_dieu_khien_yaw_tu_anh.md)

## 1. Viết script MAVSDK (gói `mavsdk_grpc`)

### 1.1. Môi trường đang dùng

- Chạy trên Windows, script nằm trong thư mục `scripts/` của repo, dùng môi trường ảo `.venv` ở thư mục gốc của repo (cài từ `requirements.txt`).
- MAVSDK 4.x có API mới làm hỏng script cũ nên đã chuyển sang gói **`mavsdk_grpc`**.
- Kết nối tới sim qua `udpin://0.0.0.0:14540` (QGroundControl dùng cổng 14550 nên hai bên không giành nhau).

### 1.2. Import

```python
from mavsdk_grpc import System
from mavsdk_grpc.offboard import OffboardError, VelocityBodyYawspeed, VelocityNedYaw
```

### 1.3. Hai kiểu lệnh vận tốc

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

### 1.4. Khung chương trình

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

### 1.5. Đọc dữ liệu từ drone

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

### 1.6. Cấu trúc file `buoc3_offboard.py`

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

## 2. Kết quả thí nghiệm A và B

### 2.1. Thí nghiệm A: tiến 1 m/s trong 3 giây (body frame)

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
- **Quãng đường** là khoảng cách thẳng từ chỗ bắt đầu đến chỗ dừng (Pytago, giải thích ở [file 05](05_bo_dieu_khien_p.md), mục 9.3): √(0,12² + 2,01²) = √4,0545 ≈ **2,01 m**.
- **Thay đổi** = vị trí sau - vị trí trước. Đông: 2,01 - 0 = +2,01 m. Bắc: -0,11 m (trôi nhẹ về Nam).
  - Vì sao -0,11 mà không phải -0,12: do làm tròn khi in (ví dụ vị trí "trước" thực ra là -0,004, in ra thành -0,00).
- **Mũi xoay thêm** = `(yaw_sau - yaw_trước + 180) % 360 - 180` = (92,0 - 95,9 + 180) % 360 - 180 = 176,1 - 180 = **-3,9°** (in -3,8° vì số thực chưa làm tròn). Dấu âm = xoay nhẹ sang trái.

**Kiểm tra hướng đi khớp lý thuyết:** yaw ban đầu 95,9°, tiến 1 m/s.

- north = 1 * cos(95,9°) = 1 * (-0,103) = **-0,10 m/s**
- east = 1 * sin(95,9°) = 1 * 0,995 = **+0,99 m/s**
- Trong 3 giây, công thức dự đoán north ≈ -0,31 m và east ≈ +2,99 m. Đo được -0,12 và +2,01: cùng dấu, cùng hướng, chỉ độ lớn nhỏ hơn.

Hướng bay thực tế ([kho chưa học](chua_hoc/toan_phu_tro.md), mục 1.2): bearing = atan2(2,01; -0,12) ≈ **93,4°**, gần như trùng hướng mũi (92 đến 96°). Vậy drone đi đúng theo hướng mũi như lệnh "tiến" trong body frame.

### 2.2. Thí nghiệm B: bay về Bắc 1 m/s, mũi hướng Đông (NED)

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

### 2.3. So sánh A và B

| | A (tiến theo mũi) | B (bay Bắc, mũi Đông) |
|---|---|---|
| Đi được sau khi gửi lệnh | 1,44 m | 1,47 m |
| Đi được sau khi dừng hẳn | 2,01 m | 2,06 m |
| Đi thêm lúc phanh | 0,57 m | 0,59 m |
| So với kỳ vọng 3 m | 67% | 69% |

Hai thí nghiệm dùng hai hệ tọa độ khác nhau mà kết quả gần như trùng nhau. Vậy "thiếu quãng đường" **không do hệ tọa độ**.

### 2.4. Vì sao chỉ đi được khoảng 2 m thay vì 3 m

Có hai nguyên nhân có thể cùng góp phần (chưa kiểm chứng xong, xem phần "Việc còn dở" ở [mục lục chính](../kien_thuc_drone_bam_muc_tieu.md)):

1. **Thời gian sim chạy chậm hơn thời gian thật (real-time factor, RTF).**
   - RTF là hệ số: thời gian sim / thời gian thật. Gazebo trên máy bạn chỉ chạy khoảng 50 đến 60%.
   - Script dùng `asyncio.sleep` đếm theo **thời gian thật**, nhưng drone bay theo **thời gian sim**.
   - Công thức: `thời_gian_sim = thời_gian_thật * RTF`.
   - **Ví dụ:** RTF = 0,6, gửi lệnh 3 giây thật → thời gian sim = 3 * 0,6 = 1,8 giây → quãng đường = 1 * 1,8 = **1,8 m**.
   - Đo được 2,01 m (A) và 2,06 m (B), tỉ lệ 0,67 và 0,69, nằm trong khoảng RTF 0,6 đến 0,7. Khớp khá tốt.
2. **Drone tăng tốc từ từ (ramp).** PX4 làm mượt lệnh vận tốc nên không đạt ngay 1 m/s. Ví dụ nếu mất 1,5 giây để lên tới 1 m/s thì đi được 1 * (3 - 0,75) = 2,25 m.

**Cách phân biệt:** in vận tốc thực tế của drone mỗi 0,5 giây. Vận tốc đo bằng m/s của thế giới ảo nên không phụ thuộc RTF. Nếu vận tốc lên gần 1,0 m/s rồi ổn định thì drone bay đúng lệnh và thiếu quãng đường là do RTF. Nếu chỉ lên khoảng 0,6 m/s thì drone thật sự chậm hơn lệnh. Cách đơn giản khác: nhìn ô Real Time Factor ở góc dưới cửa sổ Gazebo.

**Ý nghĩa cho bài bám người:** tần số camera, tần số gửi lệnh đều chạy theo thời gian thật nên trong sim RTF thấp sẽ khiến vòng điều khiển phản ứng chậm hơn bạn nghĩ. Trên drone thật RTF luôn bằng 1.
