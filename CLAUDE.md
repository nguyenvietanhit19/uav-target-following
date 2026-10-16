# CLAUDE.md - Ngữ cảnh dự án UAV - iVista

> File này giúp Claude Code hiểu **tôi là ai, dự án đang ở đâu, tôi đã nắm được gì và chưa nắm gì**.
> Tổng hợp ngày 2026-10-14 từ ghi chú dự án và các buổi trao đổi trước. Có thể đã cũ nếu dự án tiến triển thêm; khi thấy mâu thuẫn với thực tế trong thư mục, hãy tin thực tế và nhắc tôi cập nhật file này.
> Đặt file này ở thư mục gốc của repo để Claude Code tự đọc.

---

## 0. Đọc phần này trước: cách làm việc với tôi

**Tôi là ai (phần liên quan tới dự án):** sinh viên năm cuối ngành Công nghệ thông tin (tên gọi: Bi), đang thực tập tại công ty iVista. Nền tảng chính là **lập trình backend** (Python/Flask, thiết kế REST API, xác thực JWT, SQL Server, Git/GitHub). Mục tiêu nghề nghiệp hướng về AI.

**Mức độ về UAV/drone: người mới hoàn toàn** (complete beginner). Tôi đang học từ nền móng. Đừng giả định tôi biết sẵn thuật ngữ về bay, điều khiển hay thị giác máy tính.

### Quy tắc trả lời (bắt buộc)

1. **Trả lời bằng tiếng Việt**, giữ nguyên tên kỹ thuật tiếng Anh (offboard, yaw, setpoint...).
2. **Giải thích thuật ngữ ngay tại lần đầu xuất hiện**, trong cùng câu hoặc trong ngoặc, không để tôi phải hỏi lại. Ví dụ: "yaw (góc xoay mũi drone quanh trục thẳng đứng)".
3. **Mỗi công thức phải có:**
   - giải thích từng đại lượng trong công thức, và
   - **một ví dụ số tính từng bước ngay sau công thức** để đọc lại là hiểu.
4. Dùng ví dụ đời thường khi cần (ví dụ chiếc taxi cho offboard, đồng hồ cho phép chia lấy dư). Tôi hiểu nhanh nhất qua ví dụ cụ thể.
5. Khi tôi hỏi lại một chỗ, **giải thích lại bằng cách khác** (hình vẽ ASCII, ví dụ số khác) chứ đừng lặp nguyên văn.
6. Nói rõ **điều gì đã kiểm chứng và điều gì chỉ là giả thuyết**. Nếu không chắc tên hàm/API, hãy kiểm tra trong thư viện đã cài thay vì đoán.
7. Không tự ý làm quá phạm vi yêu cầu. Mỗi lần ưu tiên một bước nhỏ chạy được, rồi dừng cho tôi chạy thử.

### Quy ước viết code (theo các script có sẵn)

- **Comment và docstring bằng tiếng Việt**, có đủ dấu.
- **Tên biến/hàm bằng tiếng Việt không dấu**, kiểu `snake_case` (ví dụ `DIA_CHI_KET_NOI`, `DO_CAO_CAT_CANH`, `gui_lenh_lien_tuc`, `doc_huong_mui`).
- Hằng số cấu hình đặt **ở đầu file, viết hoa**, để tôi dễ sửa và so sánh (ví dụ Kp, vận tốc tối đa, khoảng cách giữ).
- Script in tiến trình theo kiểu đánh số: `print("1) Đang chờ kết nối...")`, `print("   -> Đã kết nối!")`.
- Cuối mỗi script thí nghiệm **in kết quả đo được kèm giá trị kỳ vọng** để tôi đối chiếu.
- Mỗi script có docstring đầu file ghi rõ: làm gì, chạy trên đâu, điều kiện cần (sim đang chạy...).
- Dùng `asyncio`; điểm vào là `asyncio.run(main())`.
- Import gói MAVSDK theo mẫu chịu được cả hai phiên bản (dùng trong bài 2):

```python
try:
    from mavsdk_grpc import System          # tên mới của thư viện
except ImportError:
    from mavsdk import System               # tên cũ (mavsdk<4)
```

(Các script bài 1 và bài 3 import thẳng `from mavsdk_grpc import System`.)

---

## 1. Tổng quan dự án

- Công ty đang tự phát triển một **UAV 4 cánh quạt (quadcopter)**, gồm cả **lớp companion computer** (máy tính gắn trên drone để chạy phần "thông minh" như camera, AI), không chỉ bộ điều khiển bay (flight controller).
- **Nhiệm vụ sếp giao cho tôi** (ghi theo cách tôi diễn đạt, không phải nguyên văn của sếp): nghiên cứu **payload** (ví dụ gimbal giữ camera) và **cơ cấu mang và thả hàng** để drone bay tới một tọa độ rồi thả vật (ví dụ thả phao cứu sinh xuống một vị trí).
- Tôi muốn **hiểu nền tảng trước** thay vì sa vào chi tiết cụ thể (như khối lượng hàng).
- **Các kịch bản cần nghiên cứu:**
  1. Bay tới một tọa độ và thả hàng (phao cứu sinh, hàng hóa).
  2. Bay tới một vị trí, chụp một tấm ảnh rồi quay về.
- **Chủ đề học mới nhất:** bài toán **drone bám theo mục tiêu (target following)**, ví dụ bám theo một người, kể cả khi người đó đi vào đám đông.

---

## 2. Môi trường phát triển

### 2.1. Phần cứng

- Laptop: **Asus TUF Gaming F15 FX507ZE**, Windows, RAM 16 GB.
- GPU: **NVIDIA GeForce RTX 3050 Ti Laptop**.
- Ổ C chỉ còn khoảng 20 GB trống; **ưu tiên cài vào ổ D**. Dữ liệu Docker (khoảng 35 GB) vẫn nằm trên ổ C; thử dời sang D từng lỗi "Failed to apply settings" và đã hoãn.

### 2.2. Phần mềm

| Thành phần | Chi tiết |
|---|---|
| Hệ điều hành | Windows (PowerShell), có WSL2 + Ubuntu (user `nvanh`) |
| Docker | Docker Desktop, đã bật tích hợp WSL cho Ubuntu |
| Python | 3.12 trên Windows, dùng môi trường ảo `.venv` |
| Thư viện điều khiển | **`mavsdk_grpc`** (không dùng `mavsdk` 4.x, vì API mới làm hỏng script cũ) |
| Trạm mặt đất | QGroundControl (QGC) 5.1.4 cho Windows |
| Mô phỏng | PX4 SITL qua Docker + Gazebo |

### 2.3. Cách các phần kết nối với nhau

```
Windows (script Python + QGC)  <--- MAVLink qua UDP --->  Container Docker (PX4 + Gazebo)
                                                          chạy trong WSL2/docker-desktop
```

- Script Python chạy **trên Windows**, kết nối tới PX4 trong container qua `udpin://0.0.0.0:14540`.
- **QGC dùng cổng 14550**, script dùng **14540**, nên hai bên không giành nhau.
- Hai hình thức mô phỏng đã dùng:
  1. **Docker SITL/SIH** (image `px4io/px4-sitl:latest`) + QGC. Lệnh Docker dùng `--rm`, nên **tham số và log bị mất khi tắt sim**.
  2. **Gazebo 3D** (image `px4io/px4-sitl-gazebo`, model `gz_x500`, container tên `px4-gazebo`), chạy từ WSL2 Ubuntu với WSLg, kết nối QGC trên Windows.
- Khởi động sim 3D bằng `~/phao/chay_gpu.sh` (render GPU qua WSL D3D12). **Real-time factor (RTF) đạt khoảng 60%** với model có camera (trước đó khoảng 40-50% khi render bằng CPU).
- Nếu cửa sổ Gazebo không tự mở: `docker exec -it px4-gazebo gz sim -g -v 4` (khi đó camera không còn tự bám theo drone).
- **Không bấm nút reset của Gazebo** (drone biến mất); hãy khởi động lại sim.

### 2.4. Cấu trúc file đang có

Đã chuyển hết vào repo này (trước đây nằm ở `D:\Intern iVista\UAV\mavsdk`). Script nằm trong thư mục `scripts/`:

| File | Nội dung |
|---|---|
| `scripts/buoc1_cat_canh.py` | Bài 1: kết nối, cất cánh 10 m, hạ cánh |
| `scripts/buoc2_tha_phao_tu_dong.py` | Bài 2: bay plan thả phao và tự nhả móc khi tới lệnh Gripper Action |
| `scripts/tha_phao_muc1.plan` | Plan QGC cho mission thả phao (đặt cạnh script để bài 2 đọc được; chạy bài 2 từ trong thư mục `scripts/`) |
| `scripts/buoc3_offboard.py` | Bài 3: thí nghiệm offboard A/B/C (lệnh vận tốc) |
| `scripts/buoc4_p_controller.py` | Bài 4: bộ điều khiển P bám mục tiêu ảo đi thẳng |
| `kien_thuc_drone_bam_muc_tieu.md` và `docs/` | Ghi chú kiến thức (mục lục ở file gốc, chi tiết trong `docs/`) |
| `requirements.txt` | Các gói Python cần cài vào `.venv` |

Trong WSL Ubuntu: `~/phao/model.sdf` (mô hình phao), `~/phao/chay_gpu.sh` (script chạy sim).
Plan gốc còn lưu ở `Documents\QGroundControl\Missions`.

### 2.5. Cách chạy script

```powershell
# Lần đầu: tạo môi trường ảo trong repo và cài gói
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Chạy script từ thư mục gốc của repo
(.venv) PS D:\Intern iVista\UAV\uav-target-following> python scripts\buoc3_offboard.py A

# Riêng bài 2 (đọc file plan theo thư mục đang đứng) phải chạy từ trong scripts/
(.venv) PS D:\Intern iVista\UAV\uav-target-following\scripts> python buoc2_tha_phao_tu_dong.py
```

Điều kiện: **sim đang chạy** và QGC đang mở. Nên **khởi động lại sim giữa các lần thí nghiệm** để vị trí bắt đầu lại từ (0, 0) và dễ so sánh.

---

## 3. Bản đồ kiến thức: tôi đã nắm gì, ở mức nào

Quy ước mức độ:

- **[TH]** Đã thực hành trên sim, chạy được.
- **[LT]** Đã học lý thuyết, đã hỏi lại và hiểu (có ví dụ số), chưa tự cài đặt.
- **[GT]** Mới được giải thích một lượt, chưa thực hành, cần củng cố.
- **[--]** Chưa học.

### 3.1. Nền tảng UAV và công cụ

| Chủ đề | Mức | Ghi chú |
|---|---|---|
| Hướng quadcopter + companion computer, payload, cơ cấu thả hàng | [LT] | Tìm hiểu ở mức tổng quan để làm báo cáo cho sếp |
| Tải trọng tối đa: lực nâng (thrust), thời gian bay theo pin, dòng điện | [LT] | Có phần công thức kèm ví dụ trong báo cáo cho sếp |
| PX4 SITL qua Docker + QGC (Takeoff, Go to location, nút Gripper) | [TH] | Từng đặt Home sang Việt Nam trong khi drone ở Zurich nên bị "Safe Recovery" |
| Lập kế hoạch mission thủ công trong QGC (Plan) | [TH] | Xem 3.2 |
| Đọc log trên review.px4.io (Flight Review) | [TH] | Xem 3.2 |
| Gazebo 3D qua WSL2 + Docker, kết nối QGC | [TH] | Model `gz_x500` bay thành công |
| Camera hướng xuống `gz_x500_mono_cam_down`, xem ảnh trong Image Display | [TH] | Xác nhận bằng cách đặt hình khối trên mặt đất |
| Gắn phao nhìn thấy được, thả bằng DetachableJoint (`/phao/tha`) | [TH] | Thả thủ công bằng `gz topic` đã thành công |
| Điều khiển tay bằng joystick ảo của QGC | [TH] | Từng đâm vào vật cản và lật drone |
| MAVSDK Python: kết nối, cất cánh, hạ cánh (bài 1) | [TH] | |
| MAVSDK Python: nạp plan, nhả phao tự động (bài 2) | [TH] | Lần đầu lỗi `FAILED_TO_OPEN_QGC_PLAN` vì thiếu file plan cạnh script |
| Gimbal, chụp ảnh tự động, phần cứng thật | [--] | Cố ý để sau, tôi chọn làm track MAVSDK trước |

### 3.2. Mission thả phao mức 1 (đã làm xong)

- Plan `tha_phao_muc1`: Takeoff 20 m → Waypoint 20 m phía trên hồ Irchelpark (cách khoảng 120 m) → Waypoint cùng chỗ ở 5 m, Hold 5 s → **Gripper Action (Release, id 1)** → Return To Launch.
- Mặc định: Alt Frame Rel, độ cao waypoint 20, Flight Speed 5 m/s đã tick.
- Tên mục trong QGC 5.1.4: menu Q → Fly / Plan / Analyze / Configure. Tham số nằm trong Configure; plan mới phải chọn "No Template"; nút chuyển lớp (Mission/Fence/Rally) ở góc trên phải bản đồ; lệnh "Gripper Action" nằm dưới "Advanced"; Log Download nằm trong Analyze.
- Tham số quan sát được: không có `PD_GRIPPER_EN`; `PD_GRIPPER_TYPE` = Binary Grab/Release; `PD_GRIPPER_TO` = 1 s; `SDLOG_MODE` = ghi từ lúc khởi động đến khi disarm.
- Log lần đầu nặng khoảng 530 MB nên không tải lên được; bay lại trong cùng phiên sim thì log nhỏ và tải được.
- Kết quả bay: 2 phút 26 giây, quãng đường 395,5 m, chênh cao tối đa 32 m, tốc độ ngang tối đa 18,3 km/h.
- Đọc log hiểu được: điểm Takeoff đặt cách Home khoảng 33 m nên drone vòng qua đó; lúc Return bay lên khoảng 30 m; vận tốc gần 0 trong 5 giây Hold trước khi nhả; có **dao động ở setpoint Z chỉ ở chặng đi, không có chặng về (chưa giải thích được)**; hiểu trục Z dương là xuống và quan hệ giữa vận tốc Z với đồ thị độ cao.
- Ý tưởng thí nghiệm chưa làm: bỏ waypoint 5 m để xem dao động có biến mất không.

### 3.3. Lý thuyết bám mục tiêu (đã học, đã hỏi lại, đều có ví dụ số)

Chi tiết đầy đủ nằm trong `kien_thuc_drone_bam_muc_tieu.md`. Tóm tắt trạng thái:

| Chủ đề | Mức | Điểm cốt lõi và chỗ tôi từng hỏi lại |
|---|---|---|
| Chuỗi 3 khâu: nhìn thấy → biết ở đâu → bay theo | [LT] | Nên học theo thứ tự ngược: điều khiển bay trước, thị giác sau |
| Hệ tọa độ NED (D dương là xuống, bay lên D âm) và body frame | [LT] | Công thức đổi body → NED có ví dụ yaw 90° và 45° |
| Yaw (hướng mũi so với Bắc), yaw rate (độ/giây; dương = xoay phải) | [LT] | Từng hỏi "mũi không hướng Bắc ban đầu thì sao" → yaw luôn đo so với Bắc, lượng xoay không phụ thuộc yaw ban đầu |
| Offboard mode: script lái bằng lệnh vận tốc | [LT]+[TH] | Từng hỏi "có phải gửi xung liên tục không" → gửi **setpoint vận tốc**, không phải xung động cơ; PX4 lo phần động cơ |
| Ba luật offboard: gửi lệnh trước khi bật; gửi liên tục (dưới 0,5 s); phải đã cất cánh | [LT]+[TH] | Ví dụ chiếc taxi giúp tôi hiểu |
| Phân tích số liệu thí nghiệm: Pytago, bearing, atan2 | [LT] | Từng hỏi "âm càng nhỏ, dương càng lớn thì sao" |
| Phép chia lấy dư `%` và công thức góc xoay `(a - b + 180) % 360 - 180` | [LT] | Từng hỏi `%` là gì; hiểu bằng ví dụ đồng hồ và trường hợp vượt qua hướng Bắc (359° → 1°) |
| Real-time factor (RTF) làm sim chạy chậm hơn thời gian thật | [LT] | Giả thuyết giải thích quãng đường thiếu; **chưa kiểm chứng** |
| Phát hiện vật thể (YOLO), bounding box, IoU | [LT] | |
| Theo dõi (KCF/CSRT, SORT, ByteTrack, DeepSORT/StrongSORT/BoT-SORT) | [LT] | ByteTrack dựa chủ yếu vào chuyển động nên vẫn hay nhảy ID |
| Mô hình camera lỗ kim, FOV, intrinsics, ước lượng khoảng cách từ kích thước box | [LT] | |
| Dự đoán quỹ đạo `p + v·Δt` và Kalman filter | [LT] | Từng hỏi "có phải dựa vào vector chuyển động không" → đúng, nhưng cần Kalman vì đo nhiễu và mất dấu |
| Chống nhảy ID: Re-ID, embedding, cosine similarity, gallery | [LT] | Có ví dụ cos = 0,96 và 0 |
| Gating, hàm chi phí `λ·(1-cos) + (1-λ)·d_motion`, thuật toán Hungarian | [LT] | Ví dụ A cost 0,148 thắng B cost 0,52 |
| Xử lý che khuất: ngưỡng cos, nhiều khung liên tiếp mới nhận lại, hover khi mất dấu | [LT] | Nguyên tắc: **thà mất mục tiêu còn hơn bám nhầm** |
| Cập nhật mẫu ngoại hình bằng EMA (α nhỏ, đóng băng khi mơ hồ) | [LT] | Ví dụ 0,8 → 0,76 |
| Hai người mặc giống hệt: tỉ số mơ hồ, 3 trạng thái (chắc chắn/mơ hồ/mất dấu), cảm biến phụ (GPS, UWB, AprilTag) | [LT] | Kết luận: chỉ dùng camera thì không có giải pháp đảm bảo 100%; khuyên dùng AprilTag để thử nghiệm |
| Bộ điều khiển P: `vận_tốc = Kp × sai_số`, chọn Kp, overshoot, giới hạn vận tốc | [GT] | Mới được giải thích, chưa viết code |
| Feedforward cho mục tiêu di chuyển; ý niệm về I và D (PID) | [GT] | `vận_tốc_lệnh = vận_tốc_mục_tiêu + Kp × sai_số` |
| Sai số điều khiển từ pixel → yaw rate để giữ người giữa khung hình | [GT] | |
| Lấy ảnh camera Gazebo vào Python (OpenCV) | [--] | Bước 3 trong lộ trình |
| Chạy YOLO để lấy bounding box người | [--] | Bước 4 |
| Cài đặt tracking, Re-ID (OSNet), Kalman filter bằng code | [--] | Bước 5 |

---

## 4. Thí nghiệm offboard đã làm (bài 3)

### 4.1. Cấu trúc `buoc3_offboard.py`

Chạy: `python buoc3_offboard.py A` (hoặc `B`, `C`). Mỗi lần: kết nối → chờ GPS/Home → cất cánh 10 m (chờ đạt ít nhất 90% độ cao) → chờ 3 giây → đo trước → vào offboard → gửi lệnh liên tục → đo sau → thoát offboard → in kết quả → hạ cánh.

Hằng số: `DIA_CHI_KET_NOI = "udpin://0.0.0.0:14540"`, `DO_CAO_CAT_CANH = 10`, `CHU_KY_GUI = 0.1` (10 lần/giây).

Các hàm chính: `ket_noi_va_cat_canh`, `vao_offboard` (gửi lệnh đứng yên rồi `offboard.start()`), `gui_lenh_lien_tuc(ham_gui, lenh, so_giay)`, `thoat_offboard` (gửi đứng yên 2 giây rồi `offboard.stop()`), `doc_vi_tri` (bắc, đông so với Home), `doc_huong_mui`, `doc_do_cao`, và `thi_nghiem_A/B/C`.

### 4.2. API đã kiểm tra trong gói `mavsdk_grpc`

```python
from mavsdk_grpc import System
from mavsdk_grpc.offboard import OffboardError, VelocityBodyYawspeed, VelocityNedYaw

VelocityBodyYawspeed(forward_m_s, right_m_s, down_m_s, yawspeed_deg_s)
VelocityNedYaw(north_m_s, east_m_s, down_m_s, yaw_deg)

await drone.offboard.set_velocity_body(...)
await drone.offboard.set_velocity_ned(...)
await drone.offboard.start()   # có thể ném OffboardError
await drone.offboard.stop()

drone.telemetry.position_velocity_ned()   # .position.north_m / east_m / down_m, .velocity
drone.telemetry.heading()                 # .heading_deg
drone.telemetry.position()                # .relative_altitude_m
```

Các lớp khác có trong module offboard (chưa dùng): `PositionNedYaw`, `Attitude`, `AttitudeRate`, `AccelerationNed`, và các hàm `set_position_ned`, `set_attitude`, `set_attitude_rate`, `set_acceleration_ned`, `set_position_velocity_ned`.

### 4.3. Kết quả đo

| Thí nghiệm | Lệnh | Đi được (sau khi dừng hẳn) | Kỳ vọng | Hướng mũi |
|---|---|---|---|---|
| A | Body `(1, 0, 0, 0)` trong 3 giây | **2,01 m** (đông +2,01; bắc -0,11) | 3 m theo hướng mũi | 95,9° → 92,0° |
| B | NED `(1, 0, 0, yaw=90)` trong 3 giây | **2,06 m** về Bắc (đông -0,02) | 3 m về Bắc | 92,6° → 89,9° |
| C | Body `(0, 0, 0, 30)` trong 3 giây | **chưa chạy** | vị trí gần như không đổi, mũi xoay khoảng +90° | |

Điều rút ra:

- A: yaw ban đầu của drone là **95,9° chứ không phải 0°**, nên "tiến" đã đi về phía Đông. Hướng bay (bearing) ≈ 93,4°, khớp hướng mũi.
- B: hướng bay 359,4° (gần Bắc) trong khi mũi hướng Đông, tức hướng bay tách khỏi hướng mũi. Hạn chế: mũi vốn đã gần 90° nên không thấy mũi xoay rõ; muốn thấy rõ thì thử yaw = 180°.
- Cả hai chỉ đạt khoảng 67-69% quãng đường kỳ vọng. Vì hai hệ tọa độ cho kết quả gần như nhau, nguyên nhân **không phải hệ tọa độ**.
- **Giả thuyết chính:** RTF khoảng 0,6 khiến 3 giây thật chỉ tương ứng khoảng 1,8 giây sim (`thời_gian_sim = thời_gian_thật × RTF`). Giả thuyết phụ: drone tăng tốc từ từ (ramp) và telemetry báo trễ. **Chưa kiểm chứng.**

---

## 5. Việc đang dở

- [ ] Chạy thí nghiệm C và ghi lại kết quả.
- [ ] Kiểm chứng nguyên nhân thiếu quãng đường: đọc ô Real Time Factor trong Gazebo và/hoặc in vận tốc thực tế mỗi 0,5 giây; hoặc thử `so_giay = 6`.
- [ ] Thử B với yaw = 180°.
- [ ] Viết `buoc4_p_controller.py` (xem 6).
- [ ] Đặt tên repo (đang cân nhắc `uav-target-following`) và đẩy ghi chú + script lên Git. Lưu ý: dự án thuộc công ty, cần chắc chắn được phép công khai nếu để public, và thêm `.venv/`, `__pycache__/` vào `.gitignore`.
- [ ] (Đề tài cũ) Thử bỏ waypoint 5 m để xem dao động Z ở chặng đi có biến mất không.

---

## 6. Bước tiếp theo đề xuất cho Claude Code

**Bước 2 trong lộ trình: bộ điều khiển P cho drone bám theo một điểm ảo di chuyển** (chưa dùng camera).

Yêu cầu cho `buoc4_p_controller.py`:

1. Tạo **mục tiêu ảo** trong code, chuyển động theo đường thẳng hoặc hình tròn (tôi chọn được bằng một hằng số).
2. Mỗi chu kỳ (10 lần/giây): đọc vị trí drone → tính sai số so với "vị trí mong muốn = vị trí mục tiêu - khoảng cách giữ" → `vận_tốc_lệnh = vận_tốc_mục_tiêu + Kp × sai_số` → **giới hạn vận tốc tối đa** → gửi bằng `set_velocity_ned`.
3. **Các tham số đặt ở đầu file:** `KP`, `VAN_TOC_TOI_DA`, `KHOANG_CACH_GIU` (khoảng 5 m), tốc độ và dạng quỹ đạo mục tiêu.
4. In sai số mỗi 0,5 giây; cuối bài in sai số trung bình để so sánh các giá trị Kp (ví dụ 0,2 / 0,5 / 1,0).
5. Nhớ rằng **RTF thấp làm vòng điều khiển trễ hơn**, nên Kp tốt trong sim có thể phải nhỏ hơn dự kiến. Nên ghi vào docstring.
6. Luôn tuân thủ 3 luật offboard và có đoạn thoát offboard an toàn (gửi đứng yên rồi `stop()`, rồi hạ cánh).

**Lộ trình sau đó:**

| Bước | Nội dung | Trạng thái |
|---|---|---|
| 1 | Hệ tọa độ + offboard | Xong A, B; còn C |
| 2 | Bộ điều khiển P bám điểm ảo | Kế tiếp |
| 3 | Lấy hình từ camera trong Gazebo (OpenCV) | Chưa |
| 4 | Phát hiện người (YOLO), nối vào bước 2 bằng sai số tâm box - tâm ảnh | Chưa |
| 5 | Tracking, Re-ID, Kalman, xử lý đám đông và nhảy ID | Chưa |

Lý do giữ thứ tự này: chưa bay bám được một điểm đơn giản thì chưa có nền để đo xem Re-ID hay Kalman cải thiện được bao nhiêu.

---

## 7. Lưu ý và cạm bẫy đã gặp

- **Yaw ban đầu của drone trong sim không phải 0°** (đo được khoảng 92-96°). Đừng giả định mũi hướng Bắc.
- **Trục D của NED dương là xuống:** bay lên là D âm; dễ nhầm với Gazebo (ENU, Z dương là lên).
- **Telemetry cập nhật chậm** (khoảng 1 lần/giây), nên số đo "ngay sau khi gửi lệnh" có thể cũ; số đo sau khi drone đứng yên đáng tin hơn.
- **Lệnh vận tốc có độ trễ:** drone không đạt vận tốc ngay.
- **Sim chạy chậm hơn thời gian thật** (RTF khoảng 50-60%): `asyncio.sleep` đếm theo thời gian thật còn drone bay theo thời gian sim. Trên drone thật RTF luôn bằng 1.
- `--rm` trong lệnh Docker nghĩa là tắt sim thì mất tham số và log.
- Log đầy đủ rất nặng (hàng trăm MB); muốn tải lên Flight Review cần log nhỏ.
- Đừng đặt Home ở xa vị trí sim (từng gây "Safe Recovery").
- File `.plan` phải nằm cạnh script khi chạy bài 2.
- Chỉ làm việc trên **simulator**; hiện chưa có drone thật.

---

## 8. Nguồn tham khảo của tôi

- Báo cáo chi tiết cho sếp (có công thức tải trọng tối đa): https://claude.ai/code/artifact/8aa51239-14f2-4cf0-b9a8-9c06e1f5ba7e
- Giải thích kiến trúc Windows/WSL2/Docker/PX4/Gazebo/QGC/MAVLink (hình ví dụ ngôi nhà): https://claude.ai/code/artifact/90b66fee-f70f-4499-832a-3ba2cb0c90d7
- Log mission thả phao trên Flight Review: https://review.px4.io/plot_app?log=d3085b1a-b659-4600-a50b-a585e00d71a2
- Ghi chú kiến thức bám mục tiêu: `kien_thuc_drone_bam_muc_tieu.md`

