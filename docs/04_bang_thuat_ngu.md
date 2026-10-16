# 04. Bảng thuật ngữ (phần đã học)

> [Về mục lục chính](../kien_thuc_drone_bam_muc_tieu.md) · Thuật ngữ chưa học nằm ở [kho chưa học](chua_hoc/thuat_ngu.md)

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
| Bounding box | Khung chữ nhật bao quanh vật thể trong ảnh |
| Pixel | Điểm ảnh, ô nhỏ nhất của ảnh (ảnh rộng 640 px = 640 điểm mỗi hàng) |
| `tâm_box_x` | Tọa độ x (pixel) của điểm giữa khung bao người, bằng `(x1 + x2) / 2` |
| Sai số chuẩn hóa | Sai số pixel chia cho nửa độ rộng ảnh, ra số từ -1 đến +1, không phụ thuộc độ phân giải |
| `K_YAW` | Hệ số đổi sai số chuẩn hóa thành yaw rate (độ/giây); cũng là tốc độ xoay tối đa |
| Bộ điều khiển P | Bộ điều khiển có lệnh tỉ lệ thuận với sai số: `u = Kp × e` |
| Vòng phản hồi (feedback loop) | Vừa đo vừa chỉnh liên tục: đo vị trí, tính sai số, ra lệnh, đo lại |
| Sai số (error, `e`) | Mục tiêu trừ giá trị hiện tại: `e = r - y` |
| `Kp` | Hệ số khuếch đại của bộ P; "mỗi 1 m sai số thì lệnh bao nhiêu m/s"; đơn vị 1/giây |
| Chu kỳ `Δt` | Khoảng thời gian giữa hai lần tính (0,1 giây nếu 10 lần/giây) |
| Hệ số `1 - Kp × Δt` | Tỉ lệ sai số còn lại sau mỗi lần tính; âm thì drone vọt qua đích |
| Overshoot (vọt lố) | Drone đi quá đích rồi phải quay lại |
| Sai số xác lập | Độ lệch còn lại khi hệ đã ổn định; P thuần với mục tiêu đang chạy là `vận_tốc_mục_tiêu / Kp` |
| Feedforward | Cộng sẵn vận tốc của mục tiêu vào lệnh: `u = v_mục_tiêu + Kp × e` |
| PID | Bộ điều khiển có thêm I (sai số tích lũy) và D (tốc độ đổi của sai số) |
| `Δbắc`, `Δđông` | Hiệu vị trí mục tiêu trừ vị trí drone theo trục Bắc và trục Đông (m) |
| Khoảng cách ngang | Độ dài đường bay thẳng trên mặt phẳng ngang: `√(Δbắc² + Δđông²)` (Pytago) |
| Khoảng cách xiên (3D) | Khoảng cách tính cả độ cao: `√(khoảng_cách_ngang² + độ_cao²)` |
| Hướng (vector đơn vị) | Cặp `(Δbắc / khoảng cách; Δđông / khoảng cách)`, chỉ hướng đi, độ dài bằng 1 |
| Khoảng cách thực (`gap`) | Mục tiêu đang cách drone bao xa |
| Khoảng cách giữ (`d_giữ`, `KHOANG_CACH_GIU`) | Khoảng cách bạn muốn giữ với mục tiêu; sai số là `e = gap - d_giữ` |
