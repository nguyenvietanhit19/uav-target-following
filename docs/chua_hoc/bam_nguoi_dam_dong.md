# Bám người trong đám đông và hai người giống hệt nhau

> **Chưa học.** Nội dung này do claude.ai soạn sẵn, người học chưa tìm hiểu. Khi dạy, hãy giải thích lại từ đầu theo cách người học đang quen (thuật ngữ giải thích ngay lần đầu, ví dụ số từng bước). Học xong và đã hỏi lại thì chuyển sang thư mục `docs/` và bổ sung phần Hỏi và đáp.
> [Về kho chưa học](README.md)

## 1. Bám người trong đám đông (chống nhảy ID)

### 1.1. Vấn đề

**ID switch** (nhảy mã định danh): tracker đang gán "ID 7" cho người cần theo, nhưng khi hai người giao nhau hoặc che nhau, nó gán nhầm ID 7 sang người bên cạnh. Chỉ dùng vị trí trong ảnh thì gần như chắc chắn bị nhảy trong đám đông. Giải pháp là kết hợp nhiều lớp phòng thủ.

### 1.2. Lớp 1: nhận diện bằng ngoại hình (Re-ID)

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

### 1.3. Lớp 2: dự đoán chuyển động và gating

Dùng Kalman filter dự đoán người đó sẽ ở đâu ở khung hình tiếp theo. **Gating** (đặt cổng lọc): người nào nằm quá xa vị trí dự đoán thì loại luôn, không cần xét ngoại hình. Tránh trường hợp người giống áo nhưng đứng cách xa vẫn bị chọn nhầm.

### 1.4. Lớp 3: gộp thành một chi phí để chọn

```
cost = λ * (1 - cos) + (1 - λ) * d_motion
```

`d_motion` là khoảng cách tới vị trí dự đoán đã chuẩn hóa về 0 đến 1; `λ` là trọng số ưu tiên ngoại hình. Cost càng thấp càng đúng.

**Ví dụ λ = 0,7:**
- Ứng viên A: cos = 0,96, d_motion = 0,4 → cost = 0,7 * 0,04 + 0,3 * 0,4 = 0,028 + 0,12 = **0,148**
- Ứng viên B: cos = 0,30, d_motion = 0,1 → cost = 0,7 * 0,70 + 0,3 * 0,1 = 0,49 + 0,03 = **0,52**

B đứng gần vị trí dự đoán hơn nhưng trông khác hẳn, nên A vẫn thắng. Khi có nhiều người, thuật toán **Hungarian** (ghép cặp tối ưu) ghép sao cho tổng chi phí nhỏ nhất. Đây là cách DeepSORT, StrongSORT, BoT-SORT hoạt động.

### 1.5. Lớp 4: xử lý lúc bị che khuất - thà mất mục tiêu còn hơn bám nhầm

- **Đặt ngưỡng:** chỉ nhận ứng viên nếu cos lớn hơn một ngưỡng cao (ví dụ 0,8). Không ai đạt ngưỡng thì coi như mất dấu.
- **Khi mất dấu:** ngừng cập nhật mẫu ngoại hình, để Kalman tiếp tục dự đoán, tìm lại trong vùng rộng dần quanh vị trí cuối cùng.
- **Chỉ nhận lại** khi có ứng viên vượt ngưỡng trong nhiều khung liên tiếp (ví dụ 5 khung), tránh nhận nhầm do một khung ngẫu nhiên.
- **Lệnh bay an toàn:** lúc mất dấu cho drone giảm tốc rồi hover (đứng yên) thay vì lao theo người gần nhất.

### 1.6. Lớp 5: cập nhật mẫu ngoại hình rất chậm (EMA)

Ngoại hình đổi theo góc nhìn và ánh sáng nên mẫu cần cập nhật, nhưng phải chậm và chỉ khi chắc chắn. **EMA** (exponential moving average, trung bình trượt có trọng số):

```
f_mới = α * f_hiện_tại + (1 - α) * f_cũ
```

**Ví dụ (một thành phần của vector):** f_cũ = 0,8, f_hiện_tại = 0,4, α = 0,1.
- f_mới = 0,1 * 0,4 + 0,9 * 0,8 = 0,04 + 0,72 = **0,76**

Mẫu chỉ nhích nhẹ, nên nếu một khung bị nhầm sang người khác thì mẫu không bị "nhiễm" ngay. Chỉ cập nhật khi cos cao và mục tiêu không bị che.

### 1.7. Mẹo bổ sung

- Camera trên **gimbal** (giá đỡ xoay ổn định) giúp ảnh ổn định.
- Dùng nhiều đặc trưng: Re-ID toàn thân, biểu đồ màu áo/quần, tỉ lệ khung chiều cao/rộng.
- Cảm biến phụ (nếu được phép): GPS từ điện thoại người đó, hoặc thẻ UWB.
- ByteTrack rất tốt trong đám đông nhưng chủ yếu dựa vào chuyển động và IoU, nên một mình nó vẫn hay nhảy ID. Nên dùng bản có Re-ID.

---

## 2. Hai người mặc giống hệt nhau

### 2.1. Thực tế thẳng thắn

**Chỉ dựa vào ngoại hình thì không thể phân biệt được**, vì hai embedding gần như trùng nhau (cos ≈ 0,95 với cả hai người). Hệ thống phải dựa vào nguồn thông tin khác, và quan trọng hơn là biết khi nào mình không chắc để dừng lại.

### 2.2. Dựa vào chuyển động và tính liên tục

- Khi hai người ở xa nhau, Kalman filter vẫn theo đúng người. Rủi ro chỉ xảy ra **lúc họ giao nhau hoặc che nhau**.
- Giữ **quỹ đạo** của mục tiêu: hướng đi, tốc độ, gia tốc. Người đi thẳng 1,2 m/s khó lẫn với người đứng yên hay đi ngược chiều.
- Sau giao nhau, nếu có hai ứng viên đều khớp ngoại hình, chọn người **khớp quỹ đạo dự đoán hơn**. Nếu hai người đi song song cùng vận tốc thì cách này cũng hết tác dụng.

### 2.3. Phát hiện tình huống mơ hồ (ambiguity)

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

### 2.4. Tìm đặc điểm phân biệt nhỏ hơn

- Dáng đi, chiều cao, vóc người (gait recognition cần video dài nên ít dùng thực tế).
- Phụ kiện: balo, mũ, giày, túi. Nếu kiểm soát được kịch bản, yêu cầu mục tiêu mang một vật đặc trưng (mũ màu rực).
- Khuôn mặt: chính xác nhất nhưng chỉ dùng được khi nhìn thấy mặt (gần, góc phù hợp). Cần cân nhắc quyền riêng tư.

### 2.5. Thêm cảm biến định danh bên ngoài (đáng tin nhất)

| Phương án | Độ chính xác | Ghi chú |
|---|---|---|
| GPS điện thoại/thiết bị đeo | khoảng 3 đến 5 m | hai người đứng sát nhau vẫn khó phân biệt |
| UWB (ultra-wideband, băng siêu rộng) | khoảng 10 đến 30 cm | thẻ nhỏ người đó mang, phân biệt được hai người đứng cạnh nhau |
| AprilTag (mã vuông giống QR) gắn trên lưng áo | đọc được là biết chắc ID | đơn giản và rẻ, dùng tốt khi thử nghiệm |

### 2.6. Thiết kế hành vi theo mức độ chắc chắn

| Trạng thái | Điều kiện | Hành động của drone |
|---|---|---|
| Chắc chắn | cos cao, tỉ số mơ hồ thấp | Bám bình thường |
| Mơ hồ | Hai ứng viên giống nhau | Giảm tốc, giữ khoảng cách, chờ |
| Mất dấu | Không ai đạt ngưỡng | Hover và tìm lại |

Khi ra khỏi vùng mơ hồ (hai người tách nhau), dùng quỹ đạo và vị trí liên tục để nối lại danh tính rồi mới tiếp tục bám.

### 2.7. Kết luận thực tế

- Nếu chỉ có camera và hai người giống hệt nhau đi sát nhau liên tục, **không có giải pháp nào đảm bảo 100%**. Đó là giới hạn của bài toán, không phải lỗi thuật toán.
- Tốt nhất là kết hợp: quỹ đạo + phát hiện mơ hồ + hành vi thận trọng, rồi thêm AprilTag hoặc UWB nếu cần độ tin cậy cao.
- Với đồ án hoặc demo, nên bắt đầu bằng **AprilTag trên lưng áo** vì dễ làm trong Gazebo và cho kết quả chắc chắn để kiểm chứng phần còn lại.
