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
