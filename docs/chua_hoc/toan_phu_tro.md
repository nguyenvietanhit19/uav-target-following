# Toán phụ trợ: Pytago, atan2, phép chia lấy dư

> **Chưa học.** Nội dung này do claude.ai soạn sẵn, người học chưa tìm hiểu. Khi dạy, hãy giải thích lại từ đầu theo cách người học đang quen (thuật ngữ giải thích ngay lần đầu, ví dụ số từng bước). Học xong và đã hỏi lại thì chuyển sang thư mục `docs/` và bổ sung phần Hỏi và đáp.
> [Về kho chưa học](README.md)

## 1. Toán phụ trợ: Pytago, atan2, phép chia lấy dư `%`

### 1.1. Khoảng cách trên mặt phẳng (Pytago)

> **Đã học** phần Pytago (khoảng cách ngang `√(Δbắc² + Δđông²)`): xem [file 05](../05_bo_dieu_khien_p.md), mục 9.1 đến 9.3. Mục này giữ lại để tham khảo.

```
khoảng_cách = √(Δbắc² + Δđông²)
```

**Ví dụ:** bắc = -3, đông = +4 → √(3² + 4²) = √25 = **5 m**.

### 1.2. Hướng và bearing (atan2)

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

### 1.3. Phép `%` (chia lấy phần dư, modulo)

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

### 1.4. Công thức góc xoay `(a - b + 180) % 360 - 180`

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
