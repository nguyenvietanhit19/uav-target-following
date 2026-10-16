# 05. Bộ điều khiển P

> [Về mục lục chính](../kien_thuc_drone_bam_muc_tieu.md) · Trước: [03. Điều khiển yaw từ ảnh](03_dieu_khien_yaw_tu_anh.md) · Thuật ngữ: [04](04_bang_thuat_ngu.md)
>
> Mọi số trong file này tính theo **mô hình lý tưởng** (drone đạt đúng vận tốc lệnh, số đo luôn mới nhất, trừ khi có ghi rõ là có độ trễ). Tất cả bảng đã được kiểm chứng bằng code (mục 13). **Chưa thử trên sim**: giá trị Kp tốt cho drone của bạn phải đo bằng thí nghiệm ở `buoc4_p_controller.py`.

## Mục lục

- [1. Bộ điều khiển P là gì](#1-bộ-điều-khiển-p-là-gì)
  - [1.1. Vì sao cần điều khiển](#11-vì-sao-cần-điều-khiển)
  - [1.2. Các đại lượng](#12-các-đại-lượng)
  - [1.3. Hai công thức](#13-hai-công-thức)
  - [1.4. Hỏi và đáp: bộ P này do mình setup chứ không phải PX4 có sẵn à?](#14-hỏi-và-đáp-bộ-p-này-do-mình-setup-chứ-không-phải-px4-có-sẵn-à)
- [2. Các ví dụ đời thường](#2-các-ví-dụ-đời-thường)
  - [2.1. Rót nước vào ly](#21-rót-nước-vào-ly)
  - [2.2. Lái xe vào vạch dừng](#22-lái-xe-vào-vạch-dừng)
  - [2.3. Vặn vòi nước tắm (có độ trễ)](#23-vặn-vòi-nước-tắm-có-độ-trễ)
  - [2.4. Xe giữ khoảng cách với xe phía trước](#24-xe-giữ-khoảng-cách-với-xe-phía-trước)
  - [2.5. Ngồi trên ghế xoay](#25-ngồi-trên-ghế-xoay)
- [3. Ví dụ với drone: đích ở 8 m](#3-ví-dụ-với-drone-đích-ở-8-m)
  - [3.1. Chu kỳ Δt = 1 giây (tính mỗi giây một lần, để dễ đọc)](#31-chu-kỳ-δt--1-giây-tính-mỗi-giây-một-lần-để-dễ-đọc)
  - [3.2. Chu kỳ Δt = 0,1 giây (tính 10 lần/giây, như thực tế)](#32-chu-kỳ-δt--01-giây-tính-10-lầngiây-như-thực-tế)
  - [3.3. So sánh hai chu kỳ](#33-so-sánh-hai-chu-kỳ)
  - [3.4. Hỏi và đáp](#34-hỏi-và-đáp)
- [4. Kp là gì](#4-kp-là-gì)
  - [4.1. Định nghĩa](#41-định-nghĩa)
  - [4.2. Hỏi và đáp: Kp đơn vị 1/giây thì "1" ở đây là gì?](#42-hỏi-và-đáp-kp-đơn-vị-1giây-thì-1-ở-đây-là-gì)
  - [4.3. Chọn Kp: so sánh sáu giá trị](#43-chọn-kp-so-sánh-sáu-giá-trị)
  - [4.4. Hỏi và đáp: Kp khác gì K_YAW?](#44-hỏi-và-đáp-kp-khác-gì-k_yaw)
- [5. Hệ số (1 - Kp × Δt): vì sao sai số còn lại một tỉ lệ cố định](#5-hệ-số-1---kp--δt-vì-sao-sai-số-còn-lại-một-tỉ-lệ-cố-định)
  - [5.1. Hỏi và đáp: 0,95 là gì và vì sao có?](#51-hỏi-và-đáp-095-là-gì-và-vì-sao-có)
  - [5.2. Hệ số này cho biết điều gì](#52-hệ-số-này-cho-biết-điều-gì)
- [6. Giới hạn vận tốc](#6-giới-hạn-vận-tốc)
- [7. Hạn chế của P](#7-hạn-chế-của-p)
  - [7.1. Độ trễ làm P dao động](#71-độ-trễ-làm-p-dao-động)
  - [7.2. P thuần luôn tụt lại sau mục tiêu đang di chuyển](#72-p-thuần-luôn-tụt-lại-sau-mục-tiêu-đang-di-chuyển)
  - [7.3. Feedforward: cộng sẵn vận tốc của mục tiêu](#73-feedforward-cộng-sẵn-vận-tốc-của-mục-tiêu)
- [8. Giữ khoảng cách mong muốn với mục tiêu](#8-giữ-khoảng-cách-mong-muốn-với-mục-tiêu)
  - [8.1. Sai số khi có khoảng cách giữ](#81-sai-số-khi-có-khoảng-cách-giữ)
  - [8.2. Chỉ dùng P thuần, bắt đầu đúng khoảng cách (gap = 3 m)](#82-chỉ-dùng-p-thuần-bắt-đầu-đúng-khoảng-cách-gap--3-m)
  - [8.3. P cộng feedforward, bắt đầu đúng khoảng cách](#83-p-cộng-feedforward-bắt-đầu-đúng-khoảng-cách)
  - [8.4. Bắt đầu ở xa (gap = 10 m, tức e = 7)](#84-bắt-đầu-ở-xa-gap--10-m-tức-e--7)
  - [8.5. Khi quá gần](#85-khi-quá-gần)
  - [8.6. Hỏi và đáp](#86-hỏi-và-đáp)
  - [8.7. Tóm tắt mục 8](#87-tóm-tắt-mục-8)
- [9. Từ một chiều sang hai chiều và độ cao](#9-từ-một-chiều-sang-hai-chiều-và-độ-cao)
  - [9.1. Δbắc và Δđông là gì](#91-δbắc-và-δđông-là-gì)
  - [9.2. Khoảng cách ngang: đường chữ L và đường bay thẳng](#92-khoảng-cách-ngang-đường-chữ-l-và-đường-bay-thẳng)
  - [9.3. Công thức Pytago](#93-công-thức-pytago)
  - [9.4. Khoảng cách ngang, khoảng cách xiên và vì sao tách riêng độ cao](#94-khoảng-cách-ngang-khoảng-cách-xiên-và-vì-sao-tách-riêng-độ-cao)
  - [9.5. Điều khiển ngang hai chiều](#95-điều-khiển-ngang-hai-chiều)
  - [9.6. Điều khiển độ cao (trục D)](#96-điều-khiển-độ-cao-trục-d)
  - [9.7. Hỏi và đáp](#97-hỏi-và-đáp)
  - [9.8. Tóm tắt mục 9](#98-tóm-tắt-mục-9)
- [10. Tổng quan về PID (mức [GT])](#10-tổng-quan-về-pid-mức-gt)
- [11. Bảng tra: câu hỏi đã hỏi nằm ở đâu](#11-bảng-tra-câu-hỏi-đã-hỏi-nằm-ở-đâu)
- [12. Bài tập tự kiểm tra](#12-bài-tập-tự-kiểm-tra)
- [13. Tự kiểm chứng bằng code](#13-tự-kiểm-chứng-bằng-code)
- [14. Tóm tắt](#14-tóm-tắt)

## 1. Bộ điều khiển P là gì

### 1.1. Vì sao cần điều khiển

Bạn muốn drone đến một chỗ, hoặc giữ cách người 5 m. Bạn không thể ra một lệnh rồi mặc kệ, vì gió, độ trễ và sai số làm drone không đến đúng chỗ. Cách làm là **vừa đo vừa chỉnh liên tục**, gọi là **vòng phản hồi** (feedback loop):

```
        ┌──────────── đo vị trí hiện tại ←──────────────┐
        ↓                                               │
 mong muốn → [so sánh] → sai số → [bộ điều khiển P] → lệnh → drone bay → vị trí mới
```

Bộ điều khiển P là cách đơn giản nhất để đổi "sai số" thành "lệnh": **sai số càng lớn thì lệnh càng mạnh, sai số càng nhỏ thì lệnh càng nhẹ**. Chữ P là **Proportional** (tỉ lệ thuận): sai số gấp đôi thì lệnh gấp đôi.

### 1.2. Các đại lượng

| Đại lượng | Tên gọi | Ý nghĩa | Đơn vị | Ai quyết định |
|---|---|---|---|---|
| r | Mục tiêu (setpoint) | Chỗ bạn muốn đến (ví dụ 10 m) | m | Bạn |
| y | Giá trị đo (phản hồi, feedback) | Chỗ drone đang ở thật sự | m | Đo từ drone (telemetry) |
| e | Sai số (error) | Còn thiếu bao xa | m | Tính ra |
| Kp | Hệ số khuếch đại (gain) | "Mỗi 1 m sai số thì phản ứng bao nhiêu" | 1/giây | Bạn chọn |
| u | Lệnh | Vận tốc gửi cho drone | m/s | Tính ra |
| Δt | Chu kỳ | Khoảng thời gian giữa hai lần tính (0,1 giây nếu tính 10 lần/giây) | giây | Bạn chọn |

### 1.3. Hai công thức

```
e = r - y          (sai số = mong muốn trừ hiện tại)
u = Kp × e         (lệnh tỉ lệ thuận với sai số)
```

Sau mỗi lần tính, drone bay với vận tốc u trong khoảng Δt, nên vị trí mới là:

```
y_mới = y + u × Δt
```

**Ví dụ số:** đích r = 10 m, drone đang ở y = 4 m, Kp = 0,5, Δt = 1 giây.
- Sai số: e = 10 - 4 = **6** m
- Lệnh: u = 0,5 × 6 = **3** m/s
- Vị trí mới: y = 4 + 3 × 1 = **7** m

### 1.4. Hỏi và đáp: bộ P này do mình setup chứ không phải PX4 có sẵn à?

**Đúng, bộ P này do bạn tự viết, nhưng PX4 cũng có các bộ điều khiển riêng ở tầng thấp hơn.** Hai bên chồng lên nhau thành nhiều lớp:

```
Lớp ngoài (bạn viết, chạy trên máy tính, ~10 lần/giây)
  "Mục tiêu cách 4 m" → bộ P của bạn → "bay 2 m/s"
                                   │  set_velocity_ned
                                   ▼
Lớp trong (PX4 có sẵn, chạy trên flight controller, hàng trăm lần/giây)
  "muốn 2 m/s" → bộ điều khiển vận tốc → "nghiêng thân 5°"
               → bộ điều khiển tư thế   → "tốc độ 4 động cơ"
```

Theo ví dụ chiếc taxi (xem [file 01](01_he_toa_do_yaw_offboard.md), mục 3.2), bạn là hành khách và PX4 là tài xế: bạn nói "đi nhanh hơn một chút, người kia còn cách xa" (hướng đi và tốc độ), tài xế lo đạp ga, đánh lái và giữ xe không đổ.

**Vì sao vẫn phải tự viết lớp ngoài:** PX4 không biết "mục tiêu" là gì, nó chỉ nhận setpoint từ bạn. Sai số đến từ chương trình của bạn: ở bước 2 là vị trí điểm ảo trừ vị trí drone, ở bước 4 là tâm bounding box trừ tâm ảnh. PX4 không có hai giá trị này.

**Một lựa chọn khác:** PX4 nhận cả setpoint vị trí (`set_position_ned`), khi đó P bên trong PX4 làm hết. Không dùng vì bạn không kiểm soát được cách drone tiến tới (tốc độ tối đa, feedforward cho mục tiêu di chuyển), ở bước camera bạn cũng chỉ có sai số pixel chứ không có tọa độ, và mục tiêu học của bạn là hiểu vòng điều khiển.

*Chưa kiểm chứng:* chi tiết bên trong PX4 (từng tầng dùng P hay PID, tên tham số). Mình nói theo hiểu biết chung, chưa mở tài liệu hay log để xác nhận.

## 2. Các ví dụ đời thường

### 2.1. Rót nước vào ly

Ly cần đầy đến vạch 200 ml. Bạn rót theo quy tắc: mỗi giây rót bằng **một nửa phần còn thiếu**. Ở đây r = 200, Kp = 0,5, Δt = 1 giây.

| Giây | Đang có (y) | Còn thiếu (e = 200 - y) | Rót thêm (0,5 × e) | Sau giây này |
|---|---|---|---|---|
| 1 | 0 | 200 | 100 | 100 |
| 2 | 100 | 100 | 50 | 150 |
| 3 | 150 | 50 | 25 | 175 |
| 4 | 175 | 25 | 12,5 | 187,5 |

Lúc đầu nước chảy mạnh, gần đầy thì chỉ nhỏ giọt, và ly không bao giờ tràn. Đó là P với Kp vừa phải.

### 2.2. Lái xe vào vạch dừng

Còn xa vạch thì nhấn ga mạnh, còn gần thì nhả dần. Hai kiểu lái:
- **Người cẩn thận (Kp nhỏ):** còn cách vạch 10 m đã nhả gần hết ga. Tới vạch chậm nhưng êm.
- **Người nóng vội (Kp lớn):** còn cách vạch 10 m vẫn giữ ga mạnh, đến sát mới phanh gấp. Tới nhanh nhưng dễ trượt qua vạch rồi phải lùi lại.

Cả hai dùng cùng quy tắc "càng xa vạch càng nhấn ga". Chỉ khác ở **mức nhấn ga ứng với mỗi mét còn lại**, và con số đó chính là Kp.

### 2.3. Vặn vòi nước tắm (có độ trễ)

Nước nóng chảy từ bình tới vòi mất vài giây. Bạn thấy nước còn lạnh nên vặn nóng mạnh, nhưng vì độ trễ, nước nóng đổ về cùng lúc khiến nước thành quá nóng. Bạn lại vặn lạnh mạnh, rồi lại quá lạnh. Bạn dao động nóng lạnh vì **phản ứng quá mạnh trong khi thông tin về kết quả đến chậm**. Điều này cũng xảy ra với drone khi Kp lớn và có độ trễ (mục 7.1).

### 2.4. Xe giữ khoảng cách với xe phía trước

Đây là ví dụ gần nhất với bài bám người. Xe của bạn muốn giữ khoảng cách cố định với xe phía trước (cruise control thích ứng). Nếu chỉ dùng P, xe bạn sẽ **luôn tụt lại một đoạn** khi xe trước đang chạy, vì phải có sai số thì mới có lệnh (mục 7.2). Biết trước tốc độ xe trước rồi cộng sẵn vào lệnh mới giữ đúng khoảng cách, và đó là feedforward (mục 7.3).

### 2.5. Ngồi trên ghế xoay

Bạn muốn luôn nhìn thẳng vào bạn A đang đi qua lại. A lệch phải thì đạp ghế xoay phải, lệch càng nhiều thì đạp càng gấp. Đây là P áp dụng cho yaw, giải thích kỹ ở [file 01](01_he_toa_do_yaw_offboard.md) (mục 2.6) và [file 03](03_dieu_khien_yaw_tu_anh.md).

## 3. Ví dụ với drone: đích ở 8 m

**Điều kiện chung:** drone ở y = 0 m, đích r = 8 m. Công thức mỗi bước: `e = 8 - y`, `u = Kp × e`, `y_mới = y + u × Δt`.

### 3.1. Chu kỳ Δt = 1 giây (tính mỗi giây một lần, để dễ đọc)

**Kp = 0,5**

| Bước | Giây | y | e = 8 - y | u = 0,5 × e | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 8 | 4 | 4 |
| 1 | 1 | 4 | 4 | 2 | 6 |
| 2 | 2 | 6 | 2 | 1 | 7 |
| 3 | 3 | 7 | 1 | 0,5 | 7,5 |
| 4 | 4 | 7,5 | 0,5 | 0,25 | 7,75 |
| 5 | 5 | 7,75 | 0,25 | 0,125 | 7,875 |

Mỗi giây sai số giảm một nửa, nên drone tiến nhanh rồi chậm dần khi gần đích, không vọt qua.

**Kp = 1,5**

| Bước | Giây | y | e = 8 - y | u = 1,5 × e | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 8 | 12 | 12 |
| 1 | 1 | 12 | -4 | -6 | 6 |
| 2 | 2 | 6 | 2 | 3 | 9 |
| 3 | 3 | 9 | -1 | -1,5 | 7,5 |
| 4 | 4 | 7,5 | 0,5 | 0,75 | 8,25 |
| 5 | 5 | 8,25 | -0,25 | -0,375 | 7,875 |

Cách đọc:
- **Bước 0:** sai số 8 m mà lệnh tới 12 m/s, nên drone bay một mạch tới 12 m, **vọt qua đích 4 m**.
- **Bước 1:** drone ở 12 m, đích ở 8 m nên sai số **âm** (-4). Lệnh cũng âm (-6 m/s), nghĩa là bay lùi, và lùi quá tay về 6 m, tức là qua đích về phía bên kia.
- Cứ thế drone đi tới đi lui quanh đích, mỗi lần lệch **bằng một nửa lần trước** (sai số: 8 → -4 → 2 → -1 → 0,5 → -0,25). Dao động **tắt dần**, drone cuối cùng dừng ở 8 m nhưng đi qua đích nhiều lần.

**Kp = 2**

| Bước | Giây | y | e = 8 - y | u = 2 × e | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 8 | 16 | 16 |
| 1 | 1 | 16 | -8 | -16 | 0 |
| 2 | 2 | 0 | 8 | 16 | 16 |
| 3 | 3 | 16 | -8 | -16 | 0 |
| 4 | 4 | 0 | 8 | 16 | 16 |
| 5 | 5 | 16 | -8 | -16 | 0 |

Drone **bay 0 → 16 → 0 → 16 mãi mãi**, không bao giờ dừng ở 8 m. Mỗi lần vọt qua đích đúng bằng khoảng cách ban đầu nên dao động không tắt dần.

### 3.2. Chu kỳ Δt = 0,1 giây (tính 10 lần/giây, như thực tế)

Mỗi lần tính drone chỉ đi một đoạn nhỏ: `y_mới = y + u × 0,1`. Ví dụ lệnh 4 m/s trong 0,1 giây thì đi thêm 4 × 0,1 = 0,4 m.

**Kp = 0,5** (4 bước đầu)

| Bước | Giây | y | e = 8 - y | u = 0,5 × e | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 8 | 4 | 0,4 |
| 1 | 0,1 | 0,4 | 7,6 | 3,8 | 0,78 |
| 2 | 0,2 | 0,78 | 7,22 | 3,61 | 1,141 |
| 3 | 0,3 | 1,141 | 6,859 | 3,4295 | 1,484 |

**Kp = 1,5** (4 bước đầu)

| Bước | Giây | y | e = 8 - y | u = 1,5 × e | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 8 | 12 | 1,2 |
| 1 | 0,1 | 1,2 | 6,8 | 10,2 | 2,22 |
| 2 | 0,2 | 2,22 | 5,78 | 8,67 | 3,087 |
| 3 | 0,3 | 3,087 | 4,913 | 7,3695 | 3,824 |

**Kp = 2** (4 bước đầu)

| Bước | Giây | y | e = 8 - y | u = 2 × e | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 8 | 16 | 1,6 |
| 1 | 0,1 | 1,6 | 6,4 | 12,8 | 2,88 |
| 2 | 0,2 | 2,88 | 5,12 | 10,24 | 3,904 |
| 3 | 0,3 | 3,904 | 4,096 | 8,192 | 4,7232 |

**Vị trí y sau mỗi giây (10 bước tính), đích 8 m:**

| Sau | Kp = 0,5 | Kp = 1,5 | Kp = 2 |
|---|---|---|---|
| 1 giây | 3,21 | 6,43 | 7,14 |
| 2 giây | 5,13 | 7,69 | 7,91 |
| 3 giây | 6,28 | 7,94 | 7,99 |
| 4 giây | 6,97 | 7,99 | 8,00 |
| 5 giây | 7,38 | 8,00 | 8,00 |

Thời gian đến được 90% quãng đường (tới 7,2 m): Kp = 0,5 mất khoảng **4,5 giây**, Kp = 1,5 mất khoảng **1,5 giây**, Kp = 2 mất khoảng **1,1 giây**.

### 3.3. So sánh hai chu kỳ

**Δt = 1 giây**, vị trí y sau mỗi giây:

| Giây | Kp = 0,5 | Kp = 1,5 | Kp = 2 |
|---|---|---|---|
| 1 | 4 | 12 | 16 |
| 2 | 6 | 6 | 0 |
| 3 | 7 | 9 | 16 |
| 4 | 7,5 | 7,5 | 0 |

Điều rút ra:

1. **Với Δt = 0,1, Kp = 1,5 và 2 không còn dao động hay vọt qua đích**, trong khi Δt = 1 thì có. Cái làm dao động không phải riêng Kp mà là **Kp nhân với chu kỳ** (Kp × Δt, xem mục 5).
2. **Kp lớn hơn thì đến đích nhanh hơn**, và với Δt = 0,1 thì không phải đánh đổi bằng dao động.
3. **Tính nhiều lần mỗi giây thì chịu được Kp lớn hơn.** Với Δt = 0,1, Kp = 10 mới nằm sát ranh giới (đến đích ngay trong 1 bước). Kp = 15 mới bắt đầu vọt qua (12 → 6 → 9 → 7,5 → 8,25, giống hệt bảng Kp = 1,5 ở Δt = 1), và Kp = 20 thì dao động mãi (16 → 0 → 16 → 0).
4. **Nhưng đây là mô hình lý tưởng.** Drone thật cần thời gian tăng tốc và số đo bị trễ, nên ranh giới thực tế phụ thuộc độ trễ (mục 7.1), không chỉ chu kỳ gửi lệnh.

### 3.4. Hỏi và đáp

**Hỏi: Làm ví dụ ở phần Δt = 1 với Kp = 1,5 và 2.** Xem mục 3.1.

**Hỏi: Lấy ví dụ với Δt = 0,1.** Xem mục 3.2 và so sánh ở 3.3.

## 4. Kp là gì

### 4.1. Định nghĩa

**Kp là một con số bạn tự chọn, cho biết "sai số 1 m thì phản ứng mạnh bao nhiêu".** Chữ K là hệ số (gain, độ khuếch đại), chữ p là Proportional (tỉ lệ), tức hệ số tỉ lệ của bộ điều khiển P.

Ví dụ đèn đỏ (mục 2.2): hai người lái dùng cùng quy tắc "càng xa vạch càng nhấn ga", chỉ khác mức nhấn ga ứng với mỗi mét còn lại. Con số đó là Kp.

**Ví dụ số:** drone còn cách đích 6 m (e = 6).

| Kp | Tính | Vận tốc lệnh |
|---|---|---|
| 0,2 | 0,2 × 6 | **1,2 m/s** (nhẹ nhàng) |
| 0,5 | 0,5 × 6 | **3 m/s** |
| 1,0 | 1,0 × 6 | **6 m/s** (mạnh tay) |

Cùng một sai số 6 m, Kp lớn gấp 5 lần thì lệnh mạnh gấp 5 lần.

### 4.2. Hỏi và đáp: Kp đơn vị 1/giây thì "1" ở đây là gì?

Số 1 không có ý nghĩa riêng. **"1/giây" đọc là "trên giây" hay "mỗi giây"**, giống như "km/h" đọc là "ki-lô-mét trên giờ". Nó xuất hiện vì các đơn vị triệt tiêu nhau:

```
u  =  Kp  ×  e
m/s   ?      m

Muốn vế phải ra m/s thì Kp phải là (m/s) chia m = 1/s   (mét ở trên và dưới triệt tiêu)
```

Kp trả lời câu hỏi: "**mỗi mét** sai số thì ra lệnh **bao nhiêu mét/giây**".

**Cách hiểu dễ hơn:** Kp × Δt là phần sai số bị xóa trong mỗi lần tính:

| Chu kỳ Δt | Kp × Δt (với Kp = 0,5) | Ý nghĩa |
|---|---|---|
| 1 giây (như các bảng ví dụ) | 0,5 × 1 = 0,5 | Mỗi lần tính xóa **một nửa** sai số |
| 0,1 giây (10 lần/giây, như thực tế) | 0,5 × 0,1 = 0,05 | Mỗi lần tính xóa **5%** sai số |

Ở trường hợp thứ hai, mỗi giây tính 10 lần, sai số còn lại sau 1 giây là 0,95¹⁰ ≈ 0,60, tức xóa được khoảng **40% mỗi giây**. Các bảng dùng Δt = 1 giây chỉ để dễ đọc, drone thật tính nhiều lần nhỏ hơn.

Còn một cách hình dung nữa: `1 / Kp` là thời gian khoảng để xóa được khoảng 63% sai số. Với Kp = 0,5 thì khoảng 2 giây. Kp càng lớn thì phản ứng càng nhanh.

### 4.3. Chọn Kp: so sánh sáu giá trị

Đích 10 m, Δt = 1 giây. Vị trí sau mỗi bước:

| Kp | Bước 1 | Bước 2 | Bước 3 | Bước 4 | Nhận xét |
|---|---|---|---|---|---|
| 0,2 | 2 | 3,6 | 4,88 | 5,9 | Quá chậm, chưa đến nơi |
| 0,5 | 5 | 7,5 | 8,75 | 9,4 | Êm, tiến dần tới đích |
| 1,0 | 10 | 10 | 10 | 10 | Đến ngay trong một bước |
| 1,5 | **15** | 7,5 | 11,25 | 9,4 | Vọt qua đích rồi dao động tắt dần |
| 2,0 | **20** | 0 | 20 | 0 | Dao động mãi, không ổn định |
| 2,5 | 25 | -12,5 | 43,75 | -40,6 | Dao động ngày càng lớn (mất kiểm soát) |

| | Kp nhỏ | Kp lớn |
|---|---|---|
| Đến đích | Chậm | Nhanh |
| Vọt qua đích, dao động | Ít | Nhiều (khi có độ trễ hoặc Δt lớn) |
| Tụt lại sau mục tiêu đang chạy | Nhiều | Ít |

### 4.4. Hỏi và đáp: Kp khác gì K_YAW?

**Giống nhau:** cả hai đều là **hệ số P**, cùng làm một việc là đổi sai số thành lệnh (`lệnh = hệ số × sai số`). K_YAW chính là một Kp được dùng cho yaw.

**Khác nhau** ở loại sai số đưa vào và loại lệnh đưa ra, từ đó ra đơn vị khác:

| | Kp (bay tới điểm) | K_YAW (xoay theo người) |
|---|---|---|
| Sai số đưa vào | Mét (khoảng cách còn lại) | Số **không đơn vị** từ -1 đến +1 (sai số chuẩn hóa) |
| Lệnh đưa ra | Vận tốc, m/s | Tốc độ xoay, độ/giây |
| Đơn vị của hệ số | 1/giây | **độ/giây** |
| Ý nghĩa | "Mỗi 1 m sai số → bao nhiêu m/s" | "Người sát mép ảnh (±1) → bao nhiêu độ/giây" |

K_YAW có đơn vị độ/giây vì sai số chuẩn hóa không có đơn vị (pixel chia pixel); lệnh là độ/giây thì hệ số mang luôn đơn vị đó. Vì vậy K_YAW cũng là **tốc độ xoay lớn nhất** có thể xảy ra.

**Ví dụ nối hai khái niệm.** Nếu tính sai số theo **góc**: người lệch 30° so với hướng mũi, dùng Kp thông thường:

```
yaw_rate = Kp × sai_số_góc = 0,5 /s × 30° = 15 °/s
```

Kp vẫn có đơn vị 1/giây, vì (°/s) chia ° = 1/s. K_YAW là cách làm này khi sai số đã chuẩn hóa. Nếu nửa góc nhìn của camera là 45° (FOV ngang 90°, giả định để minh họa) thì sai số chuẩn hóa = 1 ứng với khoảng 45°. Khi đó, **xấp xỉ**:

```
K_YAW ≈ Kp × 45° = 0,5 /s × 45° = 22,5 °/s
```

Kiểm tra: người ở sai số chuẩn hóa 0,5 thì `yaw_rate = 22,5 × 0,5 = 11,25 °/s`. Tính theo góc: người lệch khoảng 22,5° nên `0,5 × 22,5 = 11,25 °/s`. Hai cách ra cùng số.

*Lưu ý:* cách xấp xỉ này coi pixel và góc tỉ lệ tuyến tính, còn thực tế camera có quan hệ chính xác hơn (mô hình lỗ kim, chưa học). Dùng để hiểu mối liên hệ thì đủ, còn K_YAW thực tế nên chọn bằng thí nghiệm.

## 5. Hệ số (1 - Kp × Δt): vì sao sai số còn lại một tỉ lệ cố định

### 5.1. Hỏi và đáp: 0,95 là gì và vì sao có?

**Hỏi:** "Mỗi bước sai số chỉ giảm 5% (Kp × Δt = 0,5 × 0,1 = 0,05), nên ở bước 1 sai số còn 8 × 0,95 = 7,6." 0,95 là gì và vì sao có?

**0,95 là tỉ lệ sai số còn lại sau mỗi lần tính.** Dẫn ra bằng số cụ thể: bước 0, drone ở y = 0, đích r = 8, Kp = 0,5, Δt = 0,1.

1. Sai số: e = 8 - 0 = **8**
2. Lệnh: u = 0,5 × 8 = **4** m/s
3. Drone đi trong 0,1 giây: 4 × 0,1 = **0,4** m, nên y mới = 0,4
4. Sai số mới: e = 8 - 0,4 = **7,6**

Sai số giảm từ 8 xuống 7,6, bớt đi **0,4**, đúng bằng đoạn drone vừa đi. Đoạn vừa đi chiếm bao nhiêu phần của sai số? 0,4 / 8 = 0,05 = 5%, và 0,05 chính là **Kp × Δt** = 0,5 × 0,1. Vậy sai số còn lại: 8 × (1 - 0,05) = 8 × **0,95** = 7,6.

**Dẫn ra bằng chữ (công thức tổng quát):**

```
sai số mới = r - y_mới
           = r - (y + u × Δt)
           = r - y - Kp × e × Δt        (vì u = Kp × e)
           = e - Kp × Δt × e            (vì r - y chính là e)
           = e × (1 - Kp × Δt)
```

Vậy:

```
sai_số_mới = sai_số_cũ × (1 - Kp × Δt)
```

- `Kp × Δt`: phần sai số bị xóa trong mỗi lần tính (0,05 = 5%).
- `1 - Kp × Δt`: phần sai số **còn lại** (0,95 = 95%).

Kiểm tra với bảng ở mục 3.2 (Kp = 0,5, Δt = 0,1):

| Bước | Sai số | Tính |
|---|---|---|
| 0 | 8 | |
| 1 | 7,6 | 8 × 0,95 |
| 2 | 7,22 | 7,6 × 0,95 |
| 3 | 6,859 | 7,22 × 0,95 |

Khớp với cột e của bảng. Cũng giống tiền lãi giảm dần: mỗi lần trả 5% số dư, số dư còn 95% của lần trước.

### 5.2. Hệ số này cho biết điều gì

Cùng một công thức, đổi Kp và Δt thì đổi hệ số `1 - Kp × Δt`. Tính cho tất cả các trường hợp đã làm (sai số đầu là 8):

| Kp | Δt | Kp × Δt | Hệ số 1 - Kp × Δt | Sai số: 8 → |
|---|---|---|---|---|
| 0,5 | 1 | 0,5 | **0,5** | 4 |
| 1,5 | 1 | 1,5 | **-0,5** | -4 |
| 2 | 1 | 2 | **-1** | -8 |
| 0,5 | 0,1 | 0,05 | **0,95** | 7,6 |
| 1,5 | 0,1 | 0,15 | **0,85** | 6,8 |
| 2 | 0,1 | 0,2 | **0,8** | 6,4 |

Mỗi dòng khớp với bước đầu tiên của các bảng ở mục 3.1 và 3.2. Bốn vùng hành vi:

| Kp × Δt | Hệ số | Hành vi |
|---|---|---|
| nhỏ hơn hoặc bằng 1 | từ 0 đến 1 | Sai số nhỏ dần, giữ nguyên dấu: **không vọt qua đích** |
| từ 1 đến 2 | từ -1 đến 0 | Sai số đổi dấu mỗi bước nhưng nhỏ dần: vọt qua đích, **dao động tắt dần** |
| bằng 2 | -1 | Sai số đổi dấu, giữ nguyên độ lớn: **dao động mãi** |
| lớn hơn 2 | nhỏ hơn -1 | Sai số đổi dấu và lớn dần: **mất kiểm soát** |

Hệ số bằng 0 (Kp × Δt = 1) nghĩa là sai số về 0 ngay trong một bước (Kp = 1, Δt = 1 ở mục 4.3). **Đây là nguồn gốc quy tắc "Kp × Δt ≤ 1 thì không vọt qua đích"**: nó chỉ là điều kiện để hệ số không âm.

*Chú ý:* quy tắc này chỉ đúng cho mô hình lý tưởng ở đây. Khi có độ trễ (mục 7.1) thì ranh giới thấp hơn.

## 6. Giới hạn vận tốc

Sai số lớn thì lệnh có thể phi thực tế. Mục tiêu cách 40 m, Kp = 0,5 thì u = 0,5 × 40 = 20 m/s. Vì vậy ta chặn lại bằng một hằng số đặt ở đầu file, `VAN_TOC_TOI_DA`:

```
u = Kp × e
nếu u >  VAN_TOC_TOI_DA  thì  u =  VAN_TOC_TOI_DA
nếu u < -VAN_TOC_TOI_DA  thì  u = -VAN_TOC_TOI_DA
```

Với VAN_TOC_TOI_DA = 3 m/s: u = 20 bị chặn xuống **3 m/s**. Sai số 4 m thì u = 2 m/s, dưới giới hạn nên giữ nguyên. Chặn cả hai chiều vì drone cũng có thể phải bay lùi.

**Chặn vận tốc không chữa được dao động.** Kp = 2, Δt = 1, đích 8 m, VAN_TOC_TOI_DA = 3 m/s:

| Giây | y | e | u = 2 × e | u sau khi chặn | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 8 | 16 | **3** | 3 |
| 1 | 3 | 5 | 10 | **3** | 6 |
| 2 | 6 | 2 | 4 | **3** | 9 |
| 3 | 9 | -1 | -2 | -2 | 7 |
| 4 | 7 | 1 | 2 | 2 | 9 |
| 5 | 9 | -1 | -2 | -2 | 7 |

Lúc đầu drone không phóng quá mạnh, nhưng khi tới gần đích thì sai số nhỏ, lệnh không còn bị chặn, và drone vẫn dao động giữa 7 và 9 m. Nguyên nhân (Kp quá lớn) vẫn còn.

## 7. Hạn chế của P

### 7.1. Độ trễ làm P dao động

**Ví dụ thực tế: lái xe đồ chơi qua màn hình bị trễ 1 giây.** Bạn điều khiển một chiếc xe đồ chơi bằng cách nhìn video truyền về, và video luôn **cũ 1 giây**. Vạch đích cách xe 10 m. Quy tắc của bạn: mỗi giây ra lệnh vận tốc bằng **một nửa khoảng cách còn lại** mà bạn thấy trên màn hình.

- **Giây 0:** xe ở 0 m, màn hình cũng hiện 0 m. Còn 10 m nên bạn ra lệnh 5 m/s. Xe chạy tới 5 m.
- **Giây 1:** xe thật đã ở 5 m, nhưng màn hình vẫn hiện hình cũ (0 m). Bạn lại thấy "còn 10 m", nên lại ra lệnh 5 m/s. Xe chạy tới 10 m, **đã chạm vạch đích**.
- **Giây 2:** xe thật ở 10 m, nhưng màn hình mới chỉ hiện 5 m. Bạn thấy "còn 5 m", ra lệnh 2,5 m/s. Xe chạy tiếp tới 12,5 m, **vượt qua vạch**.
- **Giây 3:** màn hình hiện xe ở 10 m (đúng vạch) nên bạn ra lệnh dừng, nhưng xe thật đã ở 12,5 m.
- **Giây 4 trở đi:** màn hình cuối cùng cho bạn thấy xe ở 12,5 m, quá vạch 2,5 m, bạn mới ra lệnh lùi.

Cùng một quy tắc "nửa khoảng cách còn lại" mà khi nhìn đúng thời gian thực thì xe tiến êm tới vạch. Vì nhìn hình cũ nên bạn cứ đẩy xe tiếp trong khi nó đã đến nơi. Giờ xem bảng số và công thức tương ứng.

Số đo vị trí bạn dùng luôn **cũ đi** (telemetry báo chậm, gói tin truyền mất thời gian; lúc đầu bạn ghi nhận telemetry khoảng 1 lần/giây, nhưng sau khi đặt tần số thì thí nghiệm bài 4 đo được 10 lần/giây).

**Ví dụ 1: số đo cũ một nhịp (Δt = 1), đích 10 m, Kp = 0,5.** Sai số tính từ vị trí của **giây trước**:

| Giây | y lúc này | y cũ dùng | e = 10 - y cũ | u = 0,5 × e | y mới |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 10 | 5 | 5 |
| 1 | 5 | 0 | 10 | 5 | 10 |
| 2 | 10 | 5 | 5 | 2,5 | **12,5** |
| 3 | 12,5 | 10 | 0 | 0 | 12,5 |
| 4 | 12,5 | 12,5 | -2,5 | -1,25 | 11,25 |
| 5 | 11,25 | 12,5 | -2,5 | -1,25 | 10 |
| 6 | 10 | 11,25 | -1,25 | -0,625 | 9,375 |
| 7 | 9,375 | 10 | 0 | 0 | 9,375 |

Cùng Kp = 0,5 (vốn không vọt qua đích khi không có độ trễ), giờ drone vọt lên **12,5 m**. Lý do: ở giây 1, drone đã ở 5 m nhưng bạn vẫn "thấy" nó ở 0 m, nên tiếp tục đẩy 5 m/s như thể nó chưa đi đâu.

**Ví dụ 2: số đo cũ 1 giây, tính 10 lần/giây (Δt = 0,1), đích 8 m.** Giả định số đo luôn cũ đúng 1 giây (10 bước). Vị trí y theo thời gian:

| Giây | Kp = 0,5 | Kp = 1,5 | Kp = 2 |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0,5 | 2 | 6 | 8 |
| 1 | 4 | 12 | 16 |
| 1,5 | 5,8 | 16,2 | 20,8 |
| 2 | 7,1 | 15,9 | 17,6 |
| 2,5 | 7,91 | 11,37 | 7,04 |
| 3 | 8,32 | 5,04 | -5,12 |
| 3,5 | 8,45 | 0,26 | -10,94 |
| 4 | 8,43 | -0,37 | -4,93 |
| 4,5 | 8,33 | 3,47 | 11,33 |
| 5 | 8,22 | 9,75 | 28,87 |
| 5,5 | 8,12 | 15,11 | 35,85 |
| 6 | 8,05 | 16,67 | 25,12 |
| 6,5 | 8 | 13,59 | 0,2 |
| 7 | 7,98 | 7,51 | -24,81 |
| 7,5 | 7,97 | 1,68 | -32,65 |
| 8 | 7,98 | -0,78 | -14,14 |

- **Kp = 0,5:** vọt nhẹ lên tối đa khoảng 8,46 rồi ổn định ở 8. Chấp nhận được.
- **Kp = 1,5:** dao động lớn, biên độ gần như không tắt (đỉnh 16,2 rồi 16,67): drone đang lắc qua lắc lại trong khoảng từ khoảng 0 đến 16 m quanh đích 8 m.
- **Kp = 2:** dao động ngày càng lớn (đỉnh 20,8 rồi 35,85), mất kiểm soát.

Cùng Kp = 1,5 và 2 nhưng khi không có độ trễ (mục 3.2) thì êm hoàn toàn. Vậy **độ trễ là thủ phạm**, và **độ trễ càng lớn thì Kp phải càng nhỏ**. Đây cũng là lý do nếu sim chạy chậm hơn thời gian thật (RTF thấp) thì vòng điều khiển trễ hơn, nên Kp tốt trong sim có thể nhỏ hơn dự kiến.

*Chưa kiểm chứng:* mức trễ thật của hệ thống bạn (bao nhiêu giây) chưa đo. Ví dụ 2 chỉ là minh họa với trễ giả định 1 giây.

### 7.2. P thuần luôn tụt lại sau mục tiêu đang di chuyển

**Ví dụ thực tế: đi bộ đuổi theo một người bạn.** Bạn đang đi bộ phía sau một người bạn và dùng quy tắc: **tốc độ của bạn bằng một nửa khoảng cách tới bạn ấy** (m/s). Bạn ấy đi đều 2 m/s.

- Lúc đầu bạn đứng ngay sau lưng bạn ấy (khoảng cách 0), nên quy tắc cho tốc độ 0. Bạn ấy đi xa dần, khoảng cách tăng lên.
- Khi cách 2 m thì bạn bước 1 m/s, vẫn chậm hơn bạn ấy (2 m/s) nên khoảng cách vẫn tăng.
- Khi cách 3 m, bạn bước 1,5 m/s, vẫn chậm hơn, khoảng cách vẫn tăng.
- Chỉ khi **cách 4 m** thì bạn mới bước 0,5 × 4 = 2 m/s, đúng bằng bạn ấy. Từ đó khoảng cách đứng yên ở 4 m và không bao giờ thu nhỏ lại.

Bạn sẽ **luôn tụt lại sau 4 m**, vì quy tắc chỉ bước nhanh khi đã có khoảng cách, mà muốn bước 2 m/s thì phải đang cách đủ xa. Muốn bước nhanh hơn thì phải tụt xa hơn nữa. Giờ xem bảng số và công thức tương ứng.

Mục tiêu đi tới 2 m/s. Drone dùng `u = Kp × e`. Giả sử drone đạt đúng vận tốc lệnh, và drone bắt đầu ngay sau lưng mục tiêu (sai số = 0). Mỗi lần tính:

```
sai_số_mới = sai_số_cũ + (vận_tốc_mục_tiêu - u) × Δt
```

**Công thức này nói gì.** Nó trả lời câu hỏi: sau một khoảng thời gian Δt, khoảng cách giữa drone và mục tiêu thay đổi bao nhiêu? Ở đây "sai số" là **khoảng cách mục tiêu cách drone**. Vì mục tiêu đang chạy, khoảng cách bị kéo bởi hai chuyển động cùng lúc: mục tiêu chạy **đi xa**, drone chạy **đuổi theo lại gần**. Khoảng cách thay đổi bằng hiệu của hai chuyển động đó.

| Đại lượng | Ý nghĩa | Ví dụ |
|---|---|---|
| sai_số_cũ | Khoảng cách mục tiêu cách drone lúc đầu | 3 m |
| vận_tốc_mục_tiêu | Mục tiêu chạy nhanh cỡ nào | 2 m/s |
| u | Vận tốc lệnh, tức drone chạy nhanh cỡ nào (u = Kp × sai số) | 1,5 m/s |
| Δt | Thời gian trôi qua | 1 giây |
| sai_số_mới | Khoảng cách sau Δt | cần tính |

**Ví dụ số bằng vị trí cụ thể.** Mục tiêu đang ở 10 m, drone ở 7 m, nên sai số = 10 - 7 = **3 m**. Mục tiêu chạy 2 m/s, drone chạy 1,5 m/s, Δt = 1 giây.

1. Mục tiêu đi thêm 2 × 1 = 2 m, nên ở 10 + 2 = **12 m**.
2. Drone đi thêm 1,5 × 1 = 1,5 m, nên ở 7 + 1,5 = **8,5 m**.
3. Sai số mới = 12 - 8,5 = **3,5 m**.

Tính bằng công thức: 3 + (2 - 1,5) × 1 = 3 + 0,5 = **3,5 m**. Khớp.

**Vì sao công thức có dạng đó (dẫn bằng chữ):**

```
sai_số_mới = vị_trí_mục_tiêu_mới - vị_trí_drone_mới
           = (vị_trí_mục_tiêu + v_mục_tiêu × Δt) - (vị_trí_drone + u × Δt)
           = (vị_trí_mục_tiêu - vị_trí_drone) + (v_mục_tiêu × Δt - u × Δt)
           = sai_số_cũ + (v_mục_tiêu - u) × Δt
```

Dòng thứ ba chỉ gom nhóm: phần trong ngoặc đầu chính là sai số cũ, phần còn lại là chênh lệch quãng đường hai bên đã đi.

**Cách đọc dấu của `(vận_tốc_mục_tiêu - u)`:**

| Trường hợp | Phần `(v_mục_tiêu - u)` | Khoảng cách |
|---|---|---|
| Mục tiêu nhanh hơn drone (2 so với 1,5) | dương (+0,5) | **Giãn ra** |
| Drone nhanh hơn mục tiêu (ví dụ u = 3) | âm (2 - 3 = -1) | **Thu hẹp lại** |
| Hai bên bằng nhau (u = 2) | 0 | **Giữ nguyên** |

Giống đi bộ đuổi theo bạn: bạn ấy đi nhanh hơn thì cách xa dần, bạn đi nhanh hơn thì cách ngắn dần, bằng nhau thì giữ nguyên khoảng cách.

**Liên hệ với công thức ở mục 5.** Ở các phần trước, đích **đứng yên** (vận_tốc_mục_tiêu = 0). Thay vào công thức này: `sai_số_mới = sai_số_cũ + (0 - u) × Δt = sai_số_cũ - u × Δt`, tức sai số chỉ giảm đúng đoạn drone vừa đi (ví dụ 8 - 4 × 0,1 = 7,6 ở mục 5.1). Công thức mới chỉ thêm phần `v_mục_tiêu` vì lúc này đích cũng đang chạy.

**Dùng vào bảng bên dưới** (mục tiêu 2 m/s, Kp = 0,5, Δt = 1). Dòng giây 1: sai số = 2, u = 0,5 × 2 = 1, nên `sai_số_mới = 2 + (2 - 1) × 1 = 3`. Mục tiêu nhanh hơn drone 1 m/s nên mỗi giây khoảng cách giãn thêm 1 m. Đến khi sai số = 4 thì u = 0,5 × 4 = 2, bằng tốc độ mục tiêu, phần `(2 - 2) = 0` nên khoảng cách không đổi nữa. Đó là kết quả 4 m của bảng.

**Kp = 0,5, Δt = 1:**

| Giây | Sai số | u = 0,5 × sai số | Sai số mới = sai số + (2 - u) × 1 |
|---|---|---|---|
| 0 | 0 | 0 | 2 |
| 1 | 2 | 1 | 3 |
| 2 | 3 | 1,5 | 3,5 |
| 3 | 3,5 | 1,75 | 3,75 |
| 4 | 3,75 | 1,875 | 3,875 |
| 5 | 3,875 | 1,9375 | 3,9375 |

Sai số tiến dần tới **4 m**. Với Δt = 0,1 thì kết quả cuối vẫn là 4 m (chỉ đến chậm hơn): sai số sau 1, 2, 3, 4, 5, 6 giây lần lượt là 1,6, 2,57, 3,14, 3,49, 3,69, 3,82.

**Lý do:** để drone đi bằng tốc độ mục tiêu thì lệnh phải là 2 m/s, mà lệnh bằng Kp × sai số nên sai số = 2 / 0,5 = **4 m**. Tổng quát:

```
sai_số_tồn_dư = vận_tốc_mục_tiêu / Kp
```

Gọi là **sai số xác lập** (steady-state error, độ lệch còn lại mà P thuần không xóa được). Với Δt = 0,1:

| Kp | Sai số tồn dư = 2 / Kp |
|---|---|
| 0,5 | 4 m |
| 1,5 | 1,33 m |
| 2 | 1 m |

Tăng Kp thì bớt tụt lại, nhưng tăng Kp thì dễ dao động khi có độ trễ (mục 7.1). Hai điều này kéo nhau.

### 7.3. Feedforward: cộng sẵn vận tốc của mục tiêu

**Ví dụ thực tế: vẫn đuổi theo người bạn đi 2 m/s, nhưng lần này bạn biết sẵn bạn ấy đi nhanh cỡ nào.** Bạn bước **sẵn 2 m/s** (theo bạn ấy) rồi mới cộng thêm một phần nhỏ để chỉnh khoảng cách: nếu bạn ấy cách xa hơn mong muốn thì bước nhanh thêm một chút, gần quá thì chậm lại một chút. Nhờ vậy bạn không cần "tụt lại" mới đủ nhanh, và khoảng cách thu về đúng mức mong muốn.

Giống người đi xe máy chạy theo xe trước: biết xe trước đang chạy 40 km/h thì giữ ga ở mức đó trước, rồi mới tăng giảm nhẹ theo khoảng cách. Dưới đây là công thức.

```
u = vận_tốc_mục_tiêu + Kp × e
```

Ví dụ: mục tiêu đi 2 m/s, sai số 4 m, Kp = 0,5 thì u = 2 + 0,5 × 4 = **4 m/s**. Drone đi nhanh hơn mục tiêu để bắt kịp, và khi sai số về 0 thì u = 2 m/s, đúng bằng tốc độ mục tiêu. Bắt đầu từ sai số 4 m, Δt = 1:

| Giây | Sai số | u = 2 + 0,5 × sai số | Sai số mới = sai số + 2 - u |
|---|---|---|---|
| 0 | 4 | 4 | 2 |
| 1 | 2 | 3 | 1 |
| 2 | 1 | 2,5 | 0,5 |
| 3 | 0,5 | 2,25 | 0,25 |
| 4 | 0,25 | 2,125 | 0,125 |

Sai số về 0. Feedforward làm phần việc "bắt kịp tốc độ mục tiêu" mà không cần Kp lớn, nên phá thế giằng co ở mục 7.2. Ví dụ đời thường (mục 2.4): xe trước chạy 10 m/s, chỉ dùng P với Kp = 0,5 thì xe bạn luôn cách xa hơn mong muốn `10 / 0,5 = 20 m`. Biết tốc độ xe trước rồi cộng sẵn vào lệnh thì khoảng cách giữ đúng.

Ở mục 7.2 và 7.3, ta coi như drone muốn đến đúng chỗ của mục tiêu (khoảng cách muốn giữ bằng 0). Mục 8 mở rộng cho khoảng cách giữ bất kỳ, như bài toán thật của bạn.

## 8. Giữ khoảng cách mong muốn với mục tiêu

Ở mục 7.2 và 7.3, drone muốn đến **đúng chỗ của mục tiêu**. Bài toán thật của bạn khác: giữ **một khoảng cách cố định** phía sau mục tiêu (hằng số `KHOANG_CACH_GIU`, ví dụ 5 m). Mục này làm lại bài với khoảng cách giữ bất kỳ.

**Điểm mấu chốt: chỉ có định nghĩa "sai số" thay đổi, các công thức còn lại giữ nguyên.**

Để dễ hiểu, xét trên một đường thẳng: mục tiêu đi phía trước, drone đi phía sau. Số liệu dùng trong cả mục:

| Ký hiệu | Giá trị | Nghĩa |
|---|---|---|
| `d_giữ` | **3 m** | Khoảng cách bạn muốn giữ với mục tiêu |
| `v_mt` | **2 m/s** | Vận tốc của mục tiêu |
| Kp | 0,5 /s | Hệ số P |
| Δt | 1 giây | Chu kỳ tính |

(Vì sao chọn `d_giữ` = 3 m mà không phải 2 m: xem mục 8.6.)

### 8.1. Sai số khi có khoảng cách giữ

| Khái niệm | Ý nghĩa | Ví dụ |
|---|---|---|
| Khoảng cách thực (`gap`) | Mục tiêu đang cách drone bao xa | 6 m |
| Khoảng cách giữ (`d_giữ`) | Khoảng cách bạn **muốn** giữ | 3 m |

Sai số là **chênh lệch giữa hai cái đó**:

```
e = gap - d_giữ        (khoảng cách thực trừ khoảng cách muốn giữ)
```

- Xa hơn 3 m thì `e > 0`: drone phải đuổi theo.
- Đúng 3 m thì `e = 0`: giữ nguyên.
- Gần hơn 3 m thì `e < 0`: drone phải chậm lại.

Khi `d_giữ = 0` (mục 7.2, 7.3) thì `e = gap`, đúng như các ví dụ trước. Lệnh vẫn là `u = Kp × e`.

**Ví dụ số:** mục tiêu ở 10 m, drone ở 4 m.
- gap = 10 - 4 = 6 m
- e = 6 - 3 = **3** m
- u = Kp × e = 0,5 × 3 = **1,5** m/s

**Công thức cập nhật sai số không đổi** so với mục 7.2, vì `d_giữ` là hằng số nên bị triệt tiêu:

```
e_mới = gap_mới - d_giữ
      = (gap + (v_mt - u) × Δt) - d_giữ
      = e + (v_mt - u) × Δt
```

(Dòng thứ hai là công thức khoảng cách thay đổi đã giải thích ở mục 7.2.) Kiểm tra bằng ví dụ trên, Δt = 1, mục tiêu chạy 2 m/s, drone chạy 1,5 m/s: mục tiêu từ 10 m lên 12 m, drone từ 4 m lên 5,5 m, gap mới = 12 - 5,5 = 6,5 m, nên e mới = 6,5 - 3 = **3,5**. Bằng công thức: 3 + (2 - 1,5) × 1 = **3,5**. Khớp.

### 8.2. Chỉ dùng P thuần, bắt đầu đúng khoảng cách (gap = 3 m)

Công thức: `u = Kp × e`.

| Giây | gap | e = gap - 3 | u = 0,5 × e | e mới = e + (2 - u) × 1 |
|---|---|---|---|---|
| 0 | 3 | 0 | 0 | 2 |
| 1 | 5 | 2 | 1 | 3 |
| 2 | 6 | 3 | 1,5 | 3,5 |
| 3 | 6,5 | 3,5 | 1,75 | 3,75 |
| 4 | 6,75 | 3,75 | 1,875 | 3,875 |
| 5 | 6,875 | 3,875 | 1,9375 | 3,9375 |

Dòng đầu: drone đứng đúng 3 m nên `e = 0` và lệnh = 0. Nhưng mục tiêu vẫn chạy 2 m/s nên khoảng cách giãn ra.

**Kết quả ổn định:** `e_tồn_dư = v_mt / Kp = 2 / 0,5 = 4`, nên `gap = d_giữ + e_tồn_dư = 3 + 4 =` **7 m**. Bạn muốn giữ 3 m nhưng thực tế bị tụt ra 7 m.

### 8.3. P cộng feedforward, bắt đầu đúng khoảng cách

Công thức: `u = v_mt + Kp × e`.

| Giây | gap | e | u = 2 + 0,5 × e | e mới |
|---|---|---|---|---|
| 0 | 3 | 0 | 2 | 0 |
| 1 | 3 | 0 | 2 | 0 |
| 2 | 3 | 0 | 2 | 0 |

Drone chạy cùng tốc độ mục tiêu nên giữ **đúng 3 m**.

### 8.4. Bắt đầu ở xa (gap = 10 m, tức e = 7)

| Giây | P thuần: gap | P thuần: u | Có feedforward: gap | Có feedforward: u |
|---|---|---|---|---|
| 0 | 10 | 3,5 | 10 | 5,5 |
| 1 | 8,5 | 2,75 | 6,5 | 3,75 |
| 2 | 7,75 | 2,375 | 4,75 | 2,875 |
| 3 | 7,375 | 2,1875 | 3,875 | 2,4375 |
| 4 | 7,1875 | 2,09375 | 3,4375 | 2,21875 |
| 5 | 7,09375 | 2,0469 | 3,21875 | 2,1094 |

- **P thuần:** gap giảm dần và tiến tới **7 m**, không về 3 m.
- **Có feedforward:** gap tiến về **3 m** (còn 3,22 m ở giây 5, tiếp tục giảm).

**Ví dụ đời thường:** bạn đi bộ theo một người bạn và muốn đi cách bạn ấy 3 m. Chỉ dùng quy tắc "bước nhanh theo khoảng cách dư ra" thì bạn tụt lại 7 m. Biết bạn ấy đi 2 m/s thì bạn bước sẵn 2 m/s rồi chỉnh thêm, và giữ đúng 3 m.

### 8.5. Khi quá gần

Mục tiêu đứng yên (`v_mt = 0`), gap = 1,5 m (gần hơn 3 m): `e = 1,5 - 3 = -1,5`, `u = 0,5 × (-1,5) =` **-0,75 m/s**. Lệnh âm nghĩa là drone **lùi ra** để giữ 3 m. Khi viết code cần quyết định có cho drone lùi không và lùi tối đa bao nhiêu (giới hạn bằng `VAN_TOC_TOI_DA`, mục 6).

### 8.6. Hỏi và đáp

**Hỏi: Ví dụ bài toán bây giờ không phải giữ khoảng cách 0 nữa mà giữ khoảng cách với mục tiêu, ví dụ 2 m, thì sao?**

Chỉ đổi định nghĩa sai số thành `e = gap - d_giữ`, các công thức còn lại giữ nguyên. Xem mục 8.1 đến 8.5.

**Hỏi: Vì sao làm lại ví dụ với giữ 3 m?**

Vì vận tốc mục tiêu cũng là 2 m/s, nên ở bản đầu (giữ 2 m) có quá nhiều số 2 (khoảng cách giữ, vận tốc mục tiêu, các phép chia) và dễ nhầm số nào là đại lượng nào. Đổi `d_giữ` thành 3 m thì mỗi số có một vai trò riêng, dễ theo dõi hơn.

### 8.7. Tóm tắt mục 8

- Chỉ đổi định nghĩa sai số: `e = gap - d_giữ`, các công thức còn lại giữ nguyên.
- P thuần với mục tiêu chạy: `gap = d_giữ + v_mt / Kp = 3 + 4 = 7 m`, lệch khỏi mong muốn.
- Feedforward đưa gap về `d_giữ = 3 m`.

## 9. Từ một chiều sang hai chiều và độ cao

Các mục 3 đến 8 chỉ xét **một chiều trên một đường thẳng nằm ngang**: mục tiêu phía trước, drone phía sau. Bài toán thật có thêm hai điều: mục tiêu nằm bất kỳ trên mặt đất (hai chiều Bắc và Đông), và drone bay cao hơn mục tiêu. Mục này mở rộng từng bước.

### 9.1. Δbắc và Δđông là gì

Chữ Δ (đọc là "delta") nghĩa là **hiệu**, tức độ chênh giữa hai vị trí:

```
Δbắc  = bắc_của_mục_tiêu  - bắc_của_drone      (mục tiêu ở phía Bắc nhiều hơn drone bao nhiêu mét)
Δđông = đông_của_mục_tiêu - đông_của_drone     (mục tiêu ở phía Đông nhiều hơn drone bao nhiêu mét)
```

**Ví dụ:** drone ở (bắc 2 m, đông 1 m), mục tiêu ở (bắc 11 m, đông 13 m).
- Δbắc = 11 - 2 = **9** m
- Δđông = 13 - 1 = **12** m

Vậy mục tiêu nằm cách drone 9 m về phía Bắc và 12 m về phía Đông.

### 9.2. Khoảng cách ngang: đường chữ L và đường bay thẳng

Hãy coi mặt đất là bản đồ ô vuông nhìn từ trên xuống: mũi tên đi **lên** là hướng Bắc, đi **sang phải** là hướng Đông. Dùng số nhỏ cho dễ vẽ (3 ô Bắc, 4 ô Đông):

```
Bắc ↑
      ·  ·  ·  ·  M          M = mục tiêu
      ·  ·  ·  ·  ·          (3 ô lên, 4 ô sang phải)
      ·  ·  ·  ·  ·
      D  ·  ·  ·  ·  → Đông  D = drone
```

Có hai cách đi từ D tới M:

- **Đi theo đường chữ L** (như đi trong thành phố, chỉ rẽ ở ngã tư): đi 4 ô sang phải rồi 3 ô lên, tổng 4 + 3 = **7** ô.
- **Bay thẳng** (như chim bay): đường chéo từ D tới M, ngắn hơn đường chữ L.

**Khoảng cách ngang là độ dài đường bay thẳng**, tức đường chéo đó. Nó không phải 7.

```
          M
         /|
        / |  3 ô (Δbắc)
       /  |
      D───┘
        4 ô (Δđông)
```

D, góc vuông ở dưới M và M tạo thành một **tam giác vuông**: hai cạnh ngắn là Δbắc (3) và Δđông (4), cạnh dài nhất (cạnh huyền) là đường bay thẳng.

### 9.3. Công thức Pytago

Với tam giác vuông, độ dài cạnh huyền tính bằng:

```
khoảng_cách_ngang = √(Δbắc² + Δđông²)
```

- `Δbắc`, `Δđông`: hai cạnh ngắn (m), xem mục 9.1.
- `²` nghĩa là bình phương (nhân số đó với chính nó).
- `√` là căn bậc hai (số nào nhân với chính nó ra kết quả bên trong).
- Kết quả là độ dài cạnh huyền, tức khoảng cách ngang (m).

**Ví dụ nhỏ (3 và 4):**
1. Bình phương hai cạnh: 3² = 9, 4² = 16.
2. Cộng lại: 9 + 16 = 25.
3. Lấy căn bậc hai: √25 = **5** ô.

Đường chéo dài 5 ô, ngắn hơn đường chữ L (7 ô). Hợp lý vì đi thẳng luôn ngắn hơn đi vòng.

**Ví dụ của bài (9 và 12):**
1. 9² = 81, 12² = 144.
2. 81 + 144 = 225.
3. √225 = **15** m.

Đường chữ L dài 9 + 12 = 21 m, nhưng bay thẳng chỉ 15 m.

**Vì sao bình phương rồi lấy căn.** Kiểm chứng bằng ví dụ 3-4-5: xếp các ô vuông trên ba cạnh của tam giác. Ô vuông trên cạnh 3 có 3 × 3 = 9 ô nhỏ, trên cạnh 4 có 4 × 4 = 16 ô nhỏ, trên cạnh huyền có 5 × 5 = 25 ô nhỏ. Quả thật 9 + 16 = 25. Đó là điều Pytago nói: diện tích hình vuông trên cạnh huyền bằng tổng diện tích hai hình vuông còn lại. Lấy căn bậc hai là đổi diện tích ngược về độ dài cạnh.

**Dấu âm không làm hỏng công thức.** Nếu mục tiêu ở phía Nam và phía Tây của drone thì Δbắc và Δđông âm. Ví dụ Δbắc = -9, Δđông = -12: (-9)² = 81 (bình phương một số âm ra số dương), (-12)² = 144, 81 + 144 = 225, √225 = **15** m. Vẫn là 15 m, đúng thực tế vì khoảng cách là độ dài, không thể âm.

### 9.4. Khoảng cách ngang, khoảng cách xiên và vì sao tách riêng độ cao

Drone bay ở độ cao H còn người đứng trên mặt đất, nên có hai loại khoảng cách:

| Khái niệm | Công thức | Ví dụ (người cách 15 m ngang, drone cao 10 m) |
|---|---|---|
| Khoảng cách ngang | `√(Δbắc² + Δđông²)` | √(9² + 12²) = √225 = **15 m** |
| Khoảng cách xiên (3D) | `√(khoảng_cách_ngang² + độ_cao²)` | √(15² + 10²) = √325 ≈ **18,03 m** |

**Bộ P dùng khoảng cách ngang** (15 m). Khoảng cách xiên chỉ liên quan khi ước lượng khoảng cách từ kích thước khung trong ảnh (phần chưa học), vì camera thấy khoảng cách xiên chứ không thấy khoảng cách ngang.

Vì sao **tách** thành hai phần mà không dùng một khoảng cách 3D duy nhất:

| Phần | Điều khiển cái gì | Ví dụ |
|---|---|---|
| Chiều ngang (Bắc và Đông) | Giữ **khoảng cách ngang** với người | Giữ cách người 5 m trên mặt phẳng ngang |
| Chiều cao (trục D) | Giữ **độ cao cố định** so với mặt đất | Luôn bay ở 10 m |

Nếu dùng khoảng cách 3D làm sai số, bộ P sẽ kéo drone **hạ thấp xuống** để rút ngắn khoảng cách, tiến sát đầu người. Điều đó nguy hiểm. Độ cao nên là một hằng số bạn chọn, không phải kết quả của việc bám.

### 9.5. Điều khiển ngang hai chiều

**Ý chính: bài hai chiều chính là bài một chiều, chỉ là drone chạy dọc theo đường nối nó với mục tiêu.**

**Bước 0: nhắc lại bài một chiều.** Mục tiêu ở ngay phía Bắc, cách 15 m, muốn giữ 5 m, Kp = 0,5. Sai số e = 15 - 5 = **10** m, lệnh u = 0,5 × 10 = **5** m/s về phía Bắc. Bây giờ mục tiêu lệch sang Đông, nên chỉ có **hướng bay** phải chéo.

**Bước 1: xác định mục tiêu ở đâu.** Cho drone đứng ở gốc (0; 0). Mục tiêu ở **(9 m Bắc; 12 m Đông)**. Khoảng cách ngang = √(9² + 12²) = **15** m, cũng là 15 m như bài một chiều.

```
Bắc ↑
 9 ·            M  (9 Bắc, 12 Đông)
   ·         /
   ·      /       cách 15 m theo đường thẳng
   ·   /
 0 D · · · · · · · → Đông
   0           12
```

**Bước 2: tính sai số.** Muốn giữ 5 m thì drone chỉ cần tiến lại gần cho còn cách mục tiêu 5 m. Sai số = 15 - 5 = **10** m, đúng bằng bài một chiều. Nhưng 10 m này phải đi theo đường chéo về phía mục tiêu.

**Bước 3: đổi sai số thành hai con số (Bắc; Đông).** PX4 nhận lệnh vận tốc theo hai trục Bắc và Đông (dạng NED), nên phải tách đường chéo thành hai thành phần.

Đường chéo dài 15 m, trong đó 9 m là phần Bắc, 12 m là phần Đông. Vậy phần Bắc chiếm 9 / 15 = **0,6** đường chéo, phần Đông chiếm 12 / 15 = **0,8** đường chéo. Cặp (0,6; 0,8) gọi là **hướng** (chỉ cho biết hướng đi, độ dài quy về 1). Kiểm tra: √(0,6² + 0,8²) = √(0,36 + 0,64) = √1 = 1.

```
hướng = (Δbắc / khoảng_cách_ngang ; Δđông / khoảng_cách_ngang)
u_bắc  = tốc_độ × (Δbắc / khoảng_cách_ngang)
u_đông = tốc_độ × (Δđông / khoảng_cách_ngang)
```

Với tốc độ u = 0,5 × 10 = **5** m/s (như bài một chiều):
- u_bắc = 5 × 0,6 = **3** m/s
- u_đông = 5 × 0,8 = **4** m/s

Kiểm tra: tốc độ tổng √(3² + 4²) = 5 m/s, đúng bằng 5.

**Bước 4: theo dõi vài giây** (Δt = 1 giây, mục tiêu đứng yên ở (9; 12)):

| Giây | Drone ở | Mục tiêu cách (Bắc; Đông) | Khoảng cách ngang | Sai số = khoảng cách - 5 | Tốc độ = 0,5 × sai số | Lệnh (Bắc; Đông) | Drone sau 1 giây |
|---|---|---|---|---|---|---|---|
| 0 | (0; 0) | (9; 12) | 15 | 10 | 5 | (3; 4) | (3; 4) |
| 1 | (3; 4) | (6; 8) | 10 | 5 | 2,5 | (1,5; 2) | (4,5; 6) |
| 2 | (4,5; 6) | (4,5; 6) | 7,5 | 2,5 | 1,25 | (0,75; 1) | (5,25; 7) |

Cột sai số đi **10 → 5 → 2,5**, mỗi giây giảm một nửa, đúng như bảng một chiều với Kp = 0,5 (mục 3.1). Cách tính cột "Lệnh" ở mỗi dòng cũng vậy: ví dụ giây 1, hướng = (6 / 10; 8 / 10) = (0,6; 0,8), nên lệnh = 2,5 × (0,6; 0,8) = (1,5; 2).

**Cách nhìn thứ hai cho cùng kết quả: P cho từng trục.** Thay vì tính tốc độ rồi chia hướng, ta tính **vị trí mong muốn** rồi áp P riêng cho trục Bắc và trục Đông:

1. Vị trí mong muốn là điểm cách mục tiêu 5 m trên đường nối tới drone: mục tiêu (9; 12) trừ 5 × (0,6; 0,8) = (9 - 3; 12 - 4) = **(6; 8)**.
2. Sai số theo từng trục (vị trí mong muốn trừ vị trí drone): Bắc = 6 - 0 = **6**, Đông = 8 - 0 = **8**.
3. P cho từng trục: u_bắc = 0,5 × 6 = **3**, u_đông = 0,5 × 8 = **4**.

Ra cùng (3; 4). Cách này có ưu điểm là mỗi trục là một bài một chiều độc lập: trục Bắc có sai số 6 và lệnh 3, trục Đông có sai số 8 và lệnh 4.

| Bài một chiều | Bài hai chiều |
|---|---|
| Sai số: 1 con số | Sai số: 1 cặp số (Bắc; Đông) |
| Lệnh: `u = Kp × e` | Lệnh: `u_bắc = Kp × e_bắc` và `u_đông = Kp × e_đông` |
| Mục tiêu nằm trên 1 đường | Mục tiêu nằm bất kỳ trên mặt phẳng |

**Trường hợp đặc biệt cho thấy chúng thống nhất:** nếu mục tiêu nằm đúng phía Bắc (Δbắc = 15, Δđông = 0), vị trí mong muốn là (10; 0), sai số là (10; 0), lệnh là (5; 0). Đó là bài một chiều ban đầu.

### 9.6. Điều khiển độ cao (trục D)

Nhớ trục D của NED dương là xuống, nên bay lên là D âm. Độ cao dùng một P riêng:

```
e_D = D_mong_muốn - D_hiện_tại
u_D = Kp_cao × e_D
```

- `D_mong_muốn`: độ cao muốn giữ, ghi theo trục D (bay ở 10 m thì D = -10).
- `D_hiện_tại`: độ cao drone đang có, ghi theo trục D.
- `u_D`: vận tốc theo trục D (m/s); dương là đi xuống, âm là đi lên.

**Ví dụ số:** muốn bay ở 10 m (D = -10), drone đang ở 8 m (D = -8), Kp_cao = 0,5.
- Sai số: e_D = -10 - (-8) = **-2** m
- Lệnh: u_D = 0,5 × (-2) = **-1** m/s

`u_D` âm nghĩa là D giảm, tức drone **bay lên** 1 m/s cho tới khi đạt 10 m. Đúng chiều. `Kp_cao` có thể khác Kp ngang, vì độ cao thường cần chỉnh nhẹ nhàng hơn.

### 9.7. Hỏi và đáp

**Hỏi: Với bài toán theo dõi mục tiêu thì khoảng cách được tính như thế nào, vì độ cao của drone không bằng với mục tiêu? Các ví dụ bộ P chỉ lấy khoảng cách theo chiều ngang thôi đúng không?**

Đúng, các ví dụ ở mục 3 đến 8 chỉ xét một chiều ngang trên một đường thẳng. Bài thật tách thành hai phần: giữ **khoảng cách ngang** (Pytago, mục 9.3) bằng P, và giữ **độ cao cố định** bằng một P riêng cho trục D (mục 9.6). Không dùng khoảng cách xiên (3D) làm sai số để drone không bị kéo xuống sát người (mục 9.4).

**Hỏi: Tôi chưa hình dung khoảng cách ngang được tính bằng `√(Δbắc² + Δđông²)` là như nào.**

Xem mục 9.1 đến 9.3: Δbắc và Δđông là hai cạnh của một tam giác vuông trên bản đồ nhìn từ trên xuống, khoảng cách ngang là cạnh huyền (đường bay thẳng, ngắn hơn đường chữ L). Ví dụ 3-4-5 và 9-12-15.

**Hỏi: Tôi chưa hiểu phần "từ một chiều sang hai chiều".**

Xem mục 9.5. Hai chiều chính là bài một chiều mà drone chạy dọc theo đường nối với mục tiêu: sai số vẫn là khoảng cách trừ khoảng cách giữ, chỉ thêm bước chia lệnh thành (Bắc; Đông). Cách nhìn "P cho từng trục" cho cùng kết quả.

### 9.8. Tóm tắt mục 9

- Khoảng cách ngang = `√(Δbắc² + Δđông²)`, không phải Δbắc + Δđông (đó là đường chữ L).
- Điều khiển ngang: sai số = khoảng cách ngang - khoảng cách giữ; tốc độ = Kp × sai số; chia theo hướng (Δbắc / khoảng cách; Δđông / khoảng cách). Hoặc áp P cho từng trục từ vị trí mong muốn.
- Điều khiển độ cao: P riêng cho trục D, nhớ bay lên là D âm.
- **Chưa kiểm chứng trên sim.** Cách tách ngang và cao là thiết kế phổ biến mình đề xuất, chưa thử. Cách ước lượng khoảng cách ngang từ ảnh (cần góc nghiêng camera, kích thước khung) chưa học.

## 10. Tổng quan về PID *(mức [GT])*

P là một trong ba thành phần của bộ điều khiển **PID**:

| Thành phần | Nhìn vào | Ví dụ đời thường |
|---|---|---|
| P (Proportional) | Sai số **hiện tại** | Còn cách vạch càng xa thì càng nhấn ga |
| I (Integral, tích phân) | Sai số **tích lũy từ trước** | Gió đẩy lùi mãi thì dần dần nhấn ga mạnh hơn cho tới khi hết lùi |
| D (Derivative, đạo hàm) | **Tốc độ thay đổi** của sai số | Thấy vạch lao tới nhanh thì phanh sớm để không vọt lố |

Với bài bám điểm ảo, P cộng feedforward là đủ để bắt đầu. I và D sẽ học khi cần.

## 11. Bảng tra: câu hỏi đã hỏi nằm ở đâu

| Câu hỏi | Xem |
|---|---|
| Bộ điều khiển P là gì | Mục 1 |
| Bộ P này do mình setup chứ không phải PX4 có sẵn à | Mục 1.4 |
| Ví dụ thực tế dễ hiểu | Mục 2 |
| Kp là gì | Mục 4.1 |
| Kp đơn vị 1/giây thì "1" là gì | Mục 4.2 |
| Kp khác gì K_YAW | Mục 4.4 |
| Ví dụ phần drone với Kp = 1,5 và 2 | Mục 3.1 |
| Ví dụ với Δt = 0,1 | Mục 3.2 |
| 0,95 là gì và vì sao có | Mục 5.1 |
| Độ trễ làm dao động, P tụt lại sau mục tiêu | Mục 7 |
| Công thức `sai_số_mới = sai_số_cũ + (vận_tốc_mục_tiêu - u) × Δt` nghĩa là gì | Mục 7.2 |
| Giữ khoảng cách với mục tiêu (không phải 0) thì sao | Mục 8 |
| Vì sao ví dụ dùng khoảng cách giữ 3 m | Mục 8.6 |
| Khoảng cách tính thế nào khi độ cao drone khác mục tiêu; ví dụ chỉ theo chiều ngang đúng không | Mục 9.4 và 9.7 |
| Khoảng cách ngang `√(Δbắc² + Δđông²)` là như nào | Mục 9.1 đến 9.3 |
| Từ một chiều sang hai chiều | Mục 9.5 |

## 12. Bài tập tự kiểm tra

**Bài 1 (Δt = 1):** drone ở 0 m, đích ở 20 m, Kp = 0,25, Δt = 1 giây. Tính vị trí sau 2 bước.

**Đáp án:** bước 1: e = 20, u = 0,25 × 20 = 5, y = 5. Bước 2: e = 15, u = 0,25 × 15 = 3,75, y = 5 + 3,75 = **8,75 m**.

**Bài 2 (Δt = 0,1):** đích 8 m, Kp = 0,5, Δt = 0,1. Sai số còn lại sau 3 bước là bao nhiêu? (Gợi ý: dùng hệ số ở mục 5.)

**Đáp án:** hệ số = 1 - 0,5 × 0,1 = 0,95. Sau 3 bước: 8 × 0,95 × 0,95 × 0,95 = **6,859** (khớp bảng ở mục 3.2).

**Bài 3 (giữ khoảng cách, mục 8):** mục tiêu đi 2 m/s, đang cách drone 9 m, muốn giữ 3 m, Kp = 0,5, có feedforward. Tính vận tốc lệnh.

**Đáp án:** sai số e = 9 - 3 = 6. Lệnh u = v_mt + Kp × e = 2 + 0,5 × 6 = 2 + 3 = **5 m/s**.

**Bài 4 (hai chiều, mục 9):** mục tiêu đứng yên, nằm cách drone 6 m về Bắc và 8 m về Đông. Muốn giữ 4 m ngang, Kp = 0,5. Tính lệnh (Bắc; Đông).

**Đáp án:** khoảng cách ngang = √(6² + 8²) = √100 = 10 m. Sai số = 10 - 4 = 6. Tốc độ = 0,5 × 6 = 3 m/s. Hướng = (6 / 10; 8 / 10) = (0,6; 0,8). Lệnh = 3 × (0,6; 0,8) = **(1,8; 2,4) m/s**.

## 13. Tự kiểm chứng bằng code

Đoạn code mô phỏng lý tưởng dùng để sinh các bảng trong file này (viết theo quy ước tên tiếng Việt không dấu của dự án). Chạy được bằng Python thuần, không cần sim:

```python
def mo_phong(kp, dich, dt, so_buoc):
    """Mô phỏng lý tưởng: drone đạt đúng vận tốc lệnh, số đo luôn mới nhất."""
    vi_tri = 0.0
    for _ in range(so_buoc):
        sai_so = dich - vi_tri
        van_toc_lenh = kp * sai_so
        vi_tri = vi_tri + van_toc_lenh * dt
    return vi_tri

print(mo_phong(0.5, 8, 1.0, 3))              # kỳ vọng 7 (bảng mục 3.1, sau 3 bước)
print(round(mo_phong(0.5, 8, 0.1, 10), 4))   # kỳ vọng 3,2101 (bảng mục 3.2, sau 1 giây)
```

Đã chạy: kết quả 7,0 và 3,2101, khớp hai bảng nêu trên.

Đoạn thứ hai kiểm chứng mục 8 (giữ khoảng cách mong muốn khi mục tiêu đang chạy):

```python
def mo_phong_giu_khoang_cach(kp, v_muc_tieu, khoang_cach_giu, khoang_cach_dau, dt, so_buoc, dung_feedforward):
    """Mô phỏng lý tưởng: drone đi sau mục tiêu trên một đường thẳng, trả về khoảng cách thực cuối cùng."""
    vi_tri_muc_tieu = khoang_cach_dau
    vi_tri_drone = 0.0
    for _ in range(so_buoc):
        khoang_cach_thuc = vi_tri_muc_tieu - vi_tri_drone
        sai_so = khoang_cach_thuc - khoang_cach_giu
        van_toc_lenh = kp * sai_so
        if dung_feedforward:
            van_toc_lenh = van_toc_lenh + v_muc_tieu
        vi_tri_muc_tieu = vi_tri_muc_tieu + v_muc_tieu * dt
        vi_tri_drone = vi_tri_drone + van_toc_lenh * dt
    return vi_tri_muc_tieu - vi_tri_drone

print(round(mo_phong_giu_khoang_cach(0.5, 2, 3, 3, 1.0, 60, False), 3))  # kỳ vọng 7 (P thuần, mục 8.2)
print(round(mo_phong_giu_khoang_cach(0.5, 2, 3, 3, 1.0, 60, True), 3))   # kỳ vọng 3 (có feedforward, mục 8.3)
print(round(mo_phong_giu_khoang_cach(0.5, 2, 3, 10, 1.0, 5, False), 5))  # kỳ vọng 7,09375 (mục 8.4, giây 5)
print(round(mo_phong_giu_khoang_cach(0.5, 2, 3, 10, 1.0, 5, True), 5))   # kỳ vọng 3,21875 (mục 8.4, giây 5)
```

Đã chạy: kết quả 7,0, 3,0, 7,09375 và 3,21875, khớp các bảng ở mục 8.

Đoạn thứ ba kiểm chứng mục 9 (điều khiển hai chiều, mục tiêu đứng yên):

```python
import math

def mo_phong_2d(kp, khoang_cach_giu, mt_bac, mt_dong, dt, so_buoc):
    """Mô phỏng lý tưởng 2 chiều: mục tiêu đứng yên, drone bắt đầu ở gốc (0; 0). Trả về (bắc, đông) của drone.
    Chưa xử lý trường hợp khoang_cach = 0 (chia cho 0); khi viết code thật phải xử lý."""
    bac = 0.0
    dong = 0.0
    for _ in range(so_buoc):
        d_bac = mt_bac - bac
        d_dong = mt_dong - dong
        khoang_cach = math.sqrt(d_bac ** 2 + d_dong ** 2)
        sai_so = khoang_cach - khoang_cach_giu
        toc_do = kp * sai_so
        bac = bac + toc_do * (d_bac / khoang_cach) * dt
        dong = dong + toc_do * (d_dong / khoang_cach) * dt
    return bac, dong

print(mo_phong_2d(0.5, 5, 9, 12, 1.0, 3))   # kỳ vọng (5,25; 7,0) (bảng mục 9.5, sau 3 giây)
```

Đã chạy: kết quả (5,25; 7,0), khớp bảng ở mục 9.5.

## 14. Tóm tắt

- **P:** `u = Kp × e`, sai số càng lớn thì lệnh càng mạnh. Kp do bạn chọn.
- **Kp** có đơn vị 1/giây; **Kp × Δt** là phần sai số xóa mỗi lần tính; **1 - Kp × Δt** là phần còn lại.
- **Kp × Δt ≤ 1** thì không vọt qua đích; từ 1 đến 2 thì dao động tắt dần; từ 2 trở lên thì dao động mãi hoặc mất kiểm soát (mô hình lý tưởng).
- **Độ trễ** làm ranh giới thấp hơn nhiều, nên Kp thực tế nên bắt đầu nhỏ (0,2 đến 0,5).
- **Giới hạn vận tốc** chặn lệnh phi thực tế nhưng không chữa được dao động.
- **P thuần** tụt lại sau mục tiêu đang chạy (sai số tồn dư = vận_tốc_mục_tiêu / Kp); thêm **feedforward** để sửa.
- **Giữ khoảng cách mong muốn:** sai số là `e = khoảng_cách_thực - khoảng_cách_giữ`; các công thức còn lại giữ nguyên. P thuần làm khoảng cách thực lệch thành `khoảng_cách_giữ + vận_tốc_mục_tiêu / Kp` (ví dụ 3 + 4 = 7 m), feedforward đưa về đúng khoảng cách giữ.
- **Hai chiều và độ cao:** khoảng cách ngang là `√(Δbắc² + Δđông²)` (Pytago), không phải Δbắc + Δđông. Điều khiển ngang bằng P cho từng trục (hoặc tốc độ nhân với hướng), điều khiển độ cao bằng một P riêng cho trục D, không dùng khoảng cách xiên (3D) làm sai số.
- **K_YAW** là một Kp cho yaw, đơn vị độ/giây.

**Chưa kiểm chứng trên sim:** mọi giá trị Kp tốt và mức độ trễ thực của hệ thống. Việc này làm ở bước viết `buoc4_p_controller.py`.
