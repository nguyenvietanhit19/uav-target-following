# Ghi chú kiến thức: bài toán drone bám theo mục tiêu

> Trang mục lục. Tài liệu chi tiết nằm trong `docs/`; chỉ chứa những phần đã học.
> Mỗi công thức đều có ví dụ số kèm theo. Những chỗ từng hỏi lại được giải thích kỹ ở mục **"Hỏi và đáp"** của từng phần.
> Có thể sửa trực tiếp file này trong VS Code và đẩy lên Git.

## Mục lục

**Tài liệu đã học** (có thể sửa trực tiếp trong VS Code):

| File | Nội dung |
|---|---|
| [docs/01_he_toa_do_yaw_offboard.md](docs/01_he_toa_do_yaw_offboard.md) | NED, body frame, yaw, yaw rate, offboard mode |
| [docs/02_script_va_thi_nghiem.md](docs/02_script_va_thi_nghiem.md) | Script MAVSDK, kết quả thí nghiệm A và B, vì sao thiếu quãng đường |
| [docs/03_dieu_khien_yaw_tu_anh.md](docs/03_dieu_khien_yaw_tu_anh.md) | `tâm_box_x`, sai số chuẩn hóa, `K_YAW` |
| [docs/04_bang_thuat_ngu.md](docs/04_bang_thuat_ngu.md) | Bảng thuật ngữ đã học |

**Chưa học:** các chủ đề do claude.ai liệt kê sẵn (toán phụ trợ, thị giác, Kalman, đám đông) nằm ở [docs/chua_hoc/](docs/chua_hoc/README.md). Sẽ chuyển sang bảng trên khi học xong.

**Đang học tiếp:** bộ điều khiển P (chưa có file, sẽ viết khi bắt đầu).

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

## 2. Lộ trình học

| Bước | Nội dung | Mục tiêu kiểm tra | Trạng thái |
|---|---|---|---|
| 1 | Hệ tọa độ + offboard (script `buoc3_offboard.py`) | Bay tiến 1 m/s trong 3 giây và xem đi đúng hướng | Đã xong A, B; còn C |
| 2 | Bộ điều khiển P bám theo điểm ảo di chuyển | Drone bám điểm ảo, giữ khoảng cách khoảng 5 m | Chưa làm |
| 3 | Lấy hình từ camera trong Gazebo (OpenCV) | Hiển thị được video từ drone | Chưa làm |
| 4 | Phát hiện người (YOLO) | Lấy bounding box, nối với bước 2 (sai số giữa tâm box và tâm ảnh) | Chưa làm |
| 5 | Tracking, Re-ID, Kalman, xử lý đám đông | Đo số lần ID switch trên mỗi video | Chưa làm |

**Vì sao không nên học Re-ID hay Kalman trước:** hai phần đó giải quyết vấn đề nâng cao (đám đông, che khuất). Khi chưa có drone bám được một người đơn giản thì chưa có gì để cải thiện và cũng không kiểm chứng được chúng có hiệu quả hay không.

---

## 3. Việc còn dở và câu hỏi mở

- [ ] **Chạy thí nghiệm C** (xoay 30 độ/giây trong 3 giây). Kỳ vọng: vị trí gần như không đổi, mũi xoay thêm khoảng +90°. Dán kết quả vào ghi chú này.
- [ ] **Kiểm chứng nguyên nhân thiếu quãng đường** ([file 02](docs/02_script_va_thi_nghiem.md), mục 2.4): đọc ô Real Time Factor trong Gazebo, và/hoặc thêm đoạn in vận tốc thực tế mỗi 0,5 giây vào `buoc3_offboard.py`. Hoặc thử `so_giay = 6` và xem quãng đường có gần 6 m hay chỉ khoảng 4 m.
- [ ] **Khởi động lại sim** giữa các thí nghiệm để vị trí bắt đầu lại từ (0, 0), dễ so sánh hơn.
- [ ] **Thử B với yaw = 180°** để thấy rõ hướng bay tách khỏi hướng mũi (drone bay lùi).
- [ ] Sau đó sang bước 2 của lộ trình: bộ điều khiển P bám theo điểm ảo.


## Ghi chú của riêng bạn

<!-- Sửa trực tiếp ở đây trong VS Code -->
