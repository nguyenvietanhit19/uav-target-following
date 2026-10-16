# Thị giác máy tính: phát hiện và theo dõi

> **Chưa học.** Nội dung này do claude.ai soạn sẵn, người học chưa tìm hiểu. Khi dạy, hãy giải thích lại từ đầu theo cách người học đang quen (thuật ngữ giải thích ngay lần đầu, ví dụ số từng bước). Học xong và đã hỏi lại thì chuyển sang thư mục `docs/` và bổ sung phần Hỏi và đáp.
> [Về kho chưa học](README.md)

## 1. Thị giác máy tính: phát hiện và theo dõi

### 1.1. Object detection (phát hiện vật thể)

Tìm khung chữ nhật (**bounding box**) bao quanh mục tiêu trong ảnh, ví dụ bằng **YOLO**. Mỗi khung hình được xử lý độc lập, không nhớ khung trước.

### 1.2. Object tracking (theo dõi qua các khung hình)

Giữ nguyên "danh tính" mục tiêu từ khung này sang khung khác. Các thuật toán hay gặp:

| Thuật toán | Đặc điểm |
|---|---|
| KCF, CSRT | nhẹ, chạy trực tiếp trên ảnh |
| SORT, ByteTrack | kết hợp detection với tracking, chủ yếu dựa vào chuyển động và IoU |
| DeepSORT, StrongSORT, BoT-SORT | thêm nhận diện ngoại hình (Re-ID), chống nhảy ID tốt hơn |

**Vì sao cần tracking:** detection có thể bỏ sót vài khung hình; tracking giúp mục tiêu không bị "mất dấu" ngay lúc đó.

**IoU** (intersection over union) là độ chồng lấn giữa hai khung: diện tích phần giao chia diện tích phần hợp. Càng gần 1 càng trùng nhau.

### 1.3. Mô hình camera và ước lượng vị trí

- **Pinhole camera model** (mô hình lỗ kim): cách một điểm 3D chiếu thành pixel 2D.
- **FOV** (field of view) là góc nhìn; **intrinsics** là thông số trong của camera (như tiêu cự).
- Từ pixel suy ra góc lệch của mục tiêu so với trục camera.
- Từ kích thước bounding box ước lượng khoảng cách: box càng to thì mục tiêu càng gần.

### 1.4. Visual servoing (kết hợp tất cả)

Dùng ảnh để điều khiển trực tiếp: giữ mục tiêu ở giữa khung hình (điều khiển yaw hoặc dịch ngang) và giữ khoảng cách không đổi (điều khiển tiến/lùi theo kích thước box).
