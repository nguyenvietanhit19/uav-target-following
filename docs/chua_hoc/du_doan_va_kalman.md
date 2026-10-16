# Dự đoán quỹ đạo và Kalman filter

> **Chưa học.** Nội dung này do claude.ai soạn sẵn, người học chưa tìm hiểu. Khi dạy, hãy giải thích lại từ đầu theo cách người học đang quen (thuật ngữ giải thích ngay lần đầu, ví dụ số từng bước). Học xong và đã hỏi lại thì chuyển sang thư mục `docs/` và bổ sung phần Hỏi và đáp.
> [Về kho chưa học](README.md)

## 1. Dự đoán quỹ đạo và Kalman filter

### 1.1. Hỏi và đáp: dự đoán quỹ đạo có phải dựa vào vector chuyển động không?

Đúng, nhưng vector chuyển động mới chỉ là phần đơn giản nhất. Dự đoán quỹ đạo là dùng **vị trí và vận tốc hiện tại** để đoán vị trí ở khung hình tiếp theo.

### 1.2. Mô hình vận tốc không đổi

```
p_dự_đoán = p_hiện_tại + v * Δt
```

(`p` là vị trí, `v` là vận tốc, `Δt` là thời gian giữa hai khung hình.)

**Ví dụ:** người ở x = 300 px, di chuyển sang phải 60 px/giây, camera 30 khung/giây nên Δt = 1/30 giây.
- p_dự_đoán = 300 + 60 * (1/30) = 300 + 2 = **302 px**

Vận tốc tính từ hai vị trí gần nhất: khung trước x = 298, khung này x = 300 → v = (300 - 298) / (1/30) = **60 px/giây**.

### 1.3. Vì sao cần Kalman filter chứ không chỉ cộng vector

Hai điểm yếu của cộng vector thô:

- **Đo đạc nhiễu:** box rung nhẹ từng khung, vận tốc tính từ hai khung gần nhau dao động mạnh. Ví dụ box nhảy từ 298 sang 303 (nhiễu) cho v = 5 / (1/30) = **150 px/giây**, sai hẳn so với thực tế 60.
- **Mất dấu tạm thời:** khi bị che không có phép đo mới, cộng vector thô sẽ lệch dần.

**Kalman filter** giữ một ước lượng (vị trí và vận tốc) cùng với **độ không chắc chắn** của nó. Mỗi khung hình làm hai bước:

1. **Dự đoán:** dùng `p + v * Δt`, độ không chắc chắn tăng lên.
2. **Cập nhật:** khi có phép đo mới, trộn phép đo với dự đoán theo tỉ lệ tùy bên nào đáng tin hơn (đo nhiễu nhiều thì tin dự đoán hơn, và ngược lại).

Kết quả: vận tốc mượt hơn nhiều.

### 1.4. Hai lưu ý

- Giả định vận tốc không đổi chỉ đúng trong thời gian ngắn. Người rẽ đột ngột hay dừng lại thì dự đoán lệch; khi mất dấu lâu, vùng tìm kiếm phải mở rộng dần (đây là lý do Kalman cho độ không chắc chắn tăng theo thời gian).
- Drone cũng đang bay và xoay nên vị trí trong ảnh đổi kể cả khi người đứng yên. Cách tốt là dự đoán trong **hệ tọa độ thế giới** (dùng vị trí và hướng của drone từ PX4) rồi chiếu ngược vào ảnh. Bài thử đầu tiên có thể dự đoán thẳng trong pixel, nhưng nên biết giới hạn này.
