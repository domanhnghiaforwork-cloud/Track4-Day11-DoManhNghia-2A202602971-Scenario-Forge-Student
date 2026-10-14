MSSV: 202602971

# Lab 11 · Scenario Forge — báo cáo

Mỗi câu: trả lời ngắn, **trích số từ `evidence/`** (ghi tên file và trường, ví dụ `mc.json: crashes = 4`). Grader chạy lại với MSSV của bạn; số không khớp `evidence/` thì mất điểm phần D (RUBRIC), và câu dựa trên số sai khó được điểm đầy đủ. Không cần văn hay: một bảng nhỏ và hai, ba câu giải thích là đủ.

Thị trấn của bạn (`meta.json: _run.town`): A

## 1. Phát lại log có trung thực không? (bước A)

**Trích số từ `evidence/replay.json`:**
- Số kịch bản bị bỏ vì người lái gây va chạm: `dropped_human_crash_logs = 0` (trên tổng số `n_used = 400`).
- Số va chạm khi planner chạy trên log phát lại: `replay.crashes = 112`, phân loại tiếp xúc gồm:
  - `replay.contact.rear = 102`
  - `replay.contact.side = 10`
- Số va chạm trong thế giới phản ứng: `reactive.crashes = 0` (`reactive.contact = {}`).
- Số va chạm xảy ra ở cả hai thế giới: `crash_in_both = 0`.

**Giải thích:**
Phần lớn va chạm khi phát lại là đâm đuôi (`rear`: 102/112, chiếm 91.1%). Đây là **va chạm giả** do phát lại log là mô phỏng vòng lặp mở (open-loop replay): xe bám đuôi phía sau (`tg`) chỉ tua lại hành vi ghi âm từ người lái cũ mà không phản ứng với xe ego. Khi planner tự hành phanh sớm hoặc thận trọng hơn người lái trong dữ liệu thu thập, xe sau trong log vẫn tiếp tục chạy với vận tốc cũ và đâm vào đuôi ego. Trong thế giới phản ứng (`reactive`), mô hình IDM nhận biết ego giảm tốc và phanh theo, giữ khoảng cách an toàn nên không có va chạm nào xảy ra.

**Kịch bản ví dụ (`replay_only`):**
Kịch bản `scenario = 2`: Trong log phát lại, xe ego bị xe sau đâm đuôi (`contact = "rear"`). Trong thế giới phản ứng, xe sau phản ứng kịp thời với cú phanh của ego, đạt thời gian va chạm tối thiểu an toàn `min_ttc_reactive = 2.038 s` mà không hề xảy ra va chạm.

---

## 2. Kịch bản bất khả thi (bước B)

**Các luật trong `is_feasible` và căn cứ vật lý:**
1. Gia tốc ngang chuyển làn $a_{\text{lat}} = (\pi / \text{cutDur})^2 \times 3.5 / 2 \le \mu g$: Giới hạn ma sát ngang lốp - đường. Quỹ đạo chuyển làn cosin 3.5 m nếu diễn ra quá nhanh sẽ đòi hỏi lực bám ngang vượt quá giới hạn ma sát tối đa $\mu g$, khiến xe bị trượt văng/mất lái.
2. Gia tốc phanh sau nhập làn $\text{cutBrake} \le \mu g$: Giới hạn bám dọc khi phanh. Gia tốc phanh không thể vượt quá giới hạn ma sát tiếp xúc giữa lốp xe và mặt đường $\mu g$.
3. Vận tốc người đi bộ $\text{pedV} \le 2.5\text{ m/s}$ ($9\text{ km/h}$): Giới hạn sinh cơ học người đi bộ đô thị. Tốc độ $> 2.5\text{ m/s}$ là chạy nước rút của vận động viên, phi thực tế với người đi bộ qua đường thông thường.
4. Vận tốc xe cắt đầu $0 < \text{cutV} \le 22\text{ m/s}$ ($\approx 79.2\text{ km/h}$): Giới hạn tốc độ lưu thông đô thị hợp lý, loại bỏ kịch bản xe lùi cut-in ($\le 0$) hoặc vượt quá tốc độ cho phép của đường phố.

**Kết quả trong `evidence/hunt.json`:**
- `bus_bypass`: `infeasible = 3`
- `cut_in`: `infeasible = 7`
- `crosswalk_block`: `infeasible = 5`
- `rear_ended`: `infeasible = 14` $\implies$ Cuộc săn `rear_ended` sinh nhiều kịch bản bất khả thi nhất (14 kịch bản).

**Vì sao CEM bị kéo về phía đó:**
Hàm mục tiêu (danger score) của `rear_ended` tăng vọt khi khoảng cách giữa xe sau và xe trước bị triệt tiêu đột ngột. Thuật toán CEM tối ưu hóa điểm số này bằng cách ép tham số về các góc cực đoan (thời gian chuyển làn $\text{cutDur}$ siêu ngắn hoặc phanh $\text{cutBrake}$ cực gắt vượt quá $\mu g$) vì đó là nơi va chạm dễ xảy ra nhất.

**Hậu quả nếu đếm chúng là va chạm:**
Ước lượng xác suất rủi ro sẽ bị **thổi phồng nghiêm trọng** (over-pessimistic bias), báo cáo những vụ tai nạn không bao giờ có thể xảy ra trên đường thật, làm sai lệch quyết định tinh chỉnh an toàn của hệ thống.

---

## 3. Monte Carlo cho bạn biết gì (bước C1)

**Trích số từ `evidence/mc.json`:**
- Số lần chạy: `n = 3000`
- Số va chạm quan sát được: `k = 2` (`crashes = 2`)
- Xác suất ước lượng: $\hat{p} = 2 / 3000 \approx 6.67 \times 10^{-4}$ (`p = 0.0006666666666666667`)
- Khoảng tin cậy Wilson 95%: $[1.83 \times 10^{-4}, 2.43 \times 10^{-3}]$ (`wilson = [0.00018260064736652877, 0.002432658828859943]`).

**Số lần chạy để khoảng tin cậy hẹp lại còn $\pm 20\%$ của $p$:**
Nửa độ rộng khoảng tin cậy $h = 1.96 \sqrt{\frac{p(1-p)}{n}} \approx 1.96 \sqrt{\frac{p}{n}}$.
Để $h = 0.20 p$, ta cần:
$$n \approx \frac{1.96^2}{0.04 \cdot p} \approx \frac{96.04}{p} \approx \frac{96.04}{6.667 \times 10^{-4}} \approx 144,060 \text{ lần chạy}$$
(Cần khoảng **144,000 lần chạy**, gấp 48 lần ngân sách 3,000 hiện tại).

**Kiểu thất bại chưa hề xuất hiện:**
Trong `mc.json: by_mode`, cả 2 va chạm đều thuộc kiểu `bus_bypass` (`bus_bypass = 2`). Ba kiểu thất bại định trước hoàn toàn chưa xuất hiện ($k = 0$):
- `cut_in`: $k = 0$
- `crosswalk_block`: $k = 0$
- `rear_ended`: $k = 0$
(và `other`: $k = 0$).

**Con số đúng cần báo:**
**Tuyệt đối không báo bằng 0**. Với các kiểu có $k = 0$, con số đúng là **cận trên khoảng tin cậy Wilson 95%** khi $k=0$ (hoặc quy tắc Rule of Three $3/n = 3/3000 = 1.0 \times 10^{-3}$):
$$w_{\text{hi}} = \frac{1.96^2}{3000 + 1.96^2} \approx 1.28 \times 10^{-3}$$
Trích từ `mc.json`: `modes.cut_in.hi = 0.00128038`, `modes.crosswalk_block.hi = 0.00128038`, `modes.rear_ended.hi = 0.00128038`.

---

## 4. Importance sampling, ESS và độ suy biến (bước C3)

**Bảng thống kê theo từng kiểu và từng seed (`evidence/estimate.json`):**

| Seed | Kiểu thất bại | `p` | `hits` | `ess` | `top_share` |
|:---:|:---|:---:|:---:|:---:|:---:|
| **0** | `bus_bypass` | $4.48 \times 10^{-4}$ | 34 | 129.0 | 0.183 |
| | `cut_in` | 0.0 (cận trên: $2.50 \times 10^{-2}$) | 0 | 133.2 | 0.000 |
| | `crosswalk_block` | $1.12 \times 10^{-5}$ | 57 | 116.6 | **0.934** |
| | `rear_ended` | 0.0 (cận trên: $2.50 \times 10^{-2}$) | 0 | 119.1 | 0.000 |
| **1** | `bus_bypass` | $1.15 \times 10^{-3}$ | 37 | 108.9 | 0.340 |
| | `cut_in` | 0.0 (cận trên: $2.50 \times 10^{-2}$) | 0 | 123.5 | 0.000 |
| | `crosswalk_block` | $9.15 \times 10^{-6}$ | 68 | 116.8 | **0.913** |
| | `rear_ended` | 0.0 (cận trên: $2.50 \times 10^{-2}$) | 0 | 109.4 | 0.000 |
| **2** | `bus_bypass` | $1.04 \times 10^{-3}$ | 43 | 118.1 | 0.257 |
| | `cut_in` | 0.0 (cận trên: $2.50 \times 10^{-2}$) | 0 | 144.4 | 0.000 |
| | `crosswalk_block` | $6.59 \times 10^{-7}$ | 61 | 108.6 | 0.298 |
| | `rear_ended` | 0.0 (cận trên: $2.50 \times 10^{-2}$) | 0 | 125.0 | 0.000 |

- Tổng xác suất qua 3 seed:
  - Seed 0: `total = 4.59e-04` ($[1.86 \times 10^{-4}, 2.01 \times 10^{-3}]$)
  - Seed 1: `total = 1.16e-03` ($[2.53 \times 10^{-4}, 3.35 \times 10^{-3}]$)
  - Seed 2: `total = 1.04e-03` ($[3.11 \times 10^{-4}, 3.06 \times 10^{-3}]$)
- **Độ đồng thuận:** Ba seed đồng thuận chặt chẽ với nhau (khoảng tin cậy gối lên nhau ở bậc $10^{-4} - 10^{-3}$) và đồng thuận với Monte Carlo ($\hat{p}_{\text{MC}} = 6.67 \times 10^{-4}$ nằm gọn trong khoảng tin cậy của cả 3 seed).
- **Vị trí `top_share` lớn (> 0.5):** Ở kiểu `crosswalk_block` tại Seed 0 (`top_share = 0.934`) và Seed 1 (`top_share = 0.913`).
- **Giải thích độ suy biến:** Đây là hiện tượng suy biến trọng số (weight degeneracy). Khi phân phối đề xuất $q$ rút trúng một mẫu va chạm rơi vào vùng có mật độ tự nhiên $p$ tương đối lớn, tỷ số $w_i = p(x_i)/q(x_i)$ của mẫu đó áp đảo hoàn toàn, chiếm tới hơn 90% tổng trọng số. Khi đó con số ước lượng thực chất bị chi phối bởi trọng số của đúng một mẫu may rủi. Ở Seed 2 không bị mẫu cực đoan này nên `top_share = 0.298` và $p = 6.59 \times 10^{-7}$.
- **So sánh ngân sách:** Ngân sách IS là `estimate.json: budget = 16800` (gồm 9,600 lượt `hunt` và 7,200 lượt `estimate`), chỉ bằng khoảng **1/8.6** so với mức $\approx 144,000$ lượt chạy mà Monte Carlo cần để đạt cùng độ chính xác $\pm 20\%$.
- **Phần `other`:** Lấy từ `mc.json` (`other.k = 0`, `n = 3000`, `other.hi = 0.001279`). Không thể săn `other` bằng CEM vì CEM bắt buộc phải có hàm mục tiêu nguy hiểm liên tục để định hướng tìm kiếm; `other` là tập hợp phần dư không có cấu trúc hình học xác định.

---

## 5. Các kiểu thất bại (bước C2 + 3D)

**Các kiểu tìm thấy:**
1. **`bus_bypass`** (tìm thấy 182 va chạm trong `hunt.json`):
   - **Ảnh 3D:** ![bus_bypass](file:///d:/nghia/vin/TRACK4/day11/Track4-Day11-DoManhNghia-2A202602971-Scenario-Forge-Student/evidence/shots/ch9_bus_bypass.png)
   - **Chuỗi sự kiện:** Xe buýt dừng đỗ che khuất tầm nhìn góc đường; xe phía sau buýt mất kiên nhẫn lách sang làn ngược chiều đúng lúc xe ego tiến tới; do bị thân xe buýt che khuất tầm cảm biến radar/camera nên ego không nhận diện kịp thời xe lấn làn, dẫn đến va chạm trực diện/chéo góc.
2. **`crosswalk_block`** (tìm thấy 16 va chạm `crosswalk_block` trong `hunt.json`):
   - **Ảnh 3D:** ![crosswalk_block](file:///d:/nghia/vin/TRACK4/day11/Track4-Day11-DoManhNghia-2A202602971-Scenario-Forge-Student/evidence/shots/ch9_crosswalk_block.png)
   - **Chuỗi sự kiện:** Xe buýt đỗ chắn ngay sát vạch sang đường; người đi bộ bước ra từ góc khuất đầu xe buýt với vận tốc đi bộ bình thường; xe ego tiến tới mà không giảm tốc phòng ngừa điểm mù, khi cảm biến phát hiện người đi bộ thì cự ly còn lại không đủ cho quãng đường phanh khẩn cấp.

**Kiểu không tìm thấy:**
- `cut_in` (tìm thấy 0 `cut_in`, chỉ ra 10 `bus_bypass` trong `hunt.json`) và `rear_ended` (tìm thấy 0 `rear_ended`, ra 10 `crosswalk_block` và 6 `bus_bypass`).
- **Mức độ tin cậy:** Đáng tin cậy rằng trong điều kiện giao thông tự nhiên của thị trấn A, bộ điều khiển bám làn và giữ khoảng cách thích ứng của ego xử lý tình huống cắt đầu và bám đuôi rất an toàn; tuy nhiên xác suất thực sự không phải bằng 0 mà được chặn trên bởi cận trên zero-hit bound ($2.50 \times 10^{-2}$ trong IS và $1.28 \times 10^{-3}$ trong MC).

**Nếu chỉ chạy MỘT cuộc săn chung cho mọi kiểu:**
Xảy ra hiện tượng **lấn át phương thức (mode collapse)**: Thuật toán CEM sẽ dồn toàn bộ quần thể mẫu vào kiểu thất bại dễ gây va chạm nhất là `bus_bypass`, hoàn toàn bỏ sót các kiểu thất bại hiếm hơn nhưng nghiêm trọng như `crosswalk_block`. Minh chứng: ngay cả khi săn `cut_in`, CEM vẫn bị lệch hướng tìm thấy 10 va chạm `bus_bypass` (`hunt.json: cut_in.found = {"bus_bypass": 10}`). Do đó bắt buộc phải săn riêng từng kiểu với hàm danger score đặc thù.

---

## 6. Sửa planner (bước E + 3D)

**Trích số từ `evidence/fix.json`:**
- Policy được chọn: `{"cutinLat": 3.0}` (`fix.json: chosen.policy = {"cutinLat": 3.0}`).
- **Trên tập TRAIN:**
  - `chosen.fail = 7.4267e-07`
  - `chosen.fail_hi = 1.5583e-06`
- **Trên tập TEST (`test = true`):**
  - Policy được chọn (`chosen_test`):
    - `fail = 7.9110e-07`
    - `fail_hi_seen = 1.3032e-06`
    - `fail_hi` (valid): `0.038827` ($3.88 \times 10^{-2}$)
    - `unseen = ['bus_bypass']`
    - `progress = 214.1 m`, `harsh = 0`
  - Policy gốc (`baseline_test`):
    - `fail = 5.3494e-04` ($5.35 \times 10^{-4}$)
    - `fail_hi_seen = 9.1603e-04`
    - `fail_hi` (valid): `0.002196` ($2.20 \times 10^{-3}$)
    - `unseen = []`
    - `progress = 214.3 m`, `harsh = 0`

**Vì sao `fail_hi` của bản sửa ($3.88 \times 10^{-2}$) lớn hơn `fail` của policy gốc ($5.35 \times 10^{-4}$):**
Trên tập TEST 400 mẫu, bản sửa hoạt động quá tốt nên triệt tiêu toàn bộ va chạm của kiểu `bus_bypass` ($k=0$ hits, trở thành `unseen`). Vì kiểu này chưa từng thấy va chạm trên TEST, hệ thống thống kê bắt buộc phải áp dụng cận trên không va chạm bảo thủ:
$$\text{zero-hit bound} \approx \frac{3}{\beta \cdot n} = \frac{3}{0.2 \times 400} = 0.0375$$
Đây là hình phạt thống kê do kích thước mẫu hữu hạn chứ không phải bản sửa kém đi. Nếu chỉ xét các kiểu đã quan sát va chạm, `fail_hi_seen` của bản sửa chỉ là $1.30 \times 10^{-6}$, giảm hơn **700 lần** so với baseline ($9.16 \times 10^{-4}$).

**Quãng đường và phanh gấp:**
Quãng đường hoàn thành đạt $214.1\text{ m}$ so với $214.3\text{ m}$ của baseline (giảm chưa tới 0.1%, hoàn toàn đạt tiêu chí hao hụt $< 5\%$), số lần phanh gấp `harsh = 0`.

**Ảnh chụp 3D có bóng mờ:**
![fix_ghost](file:///d:/nghia/vin/TRACK4/day11/Track4-Day11-DoManhNghia-2A202602971-Scenario-Forge-Student/evidence/shots/ch9_fix_ghost.png)
*(Bản sửa màu ngọc lam phanh và giữ làn an toàn, trong khi bóng mờ của policy gốc tiếp tục di chuyển và va chạm).*

**Núm chỉnh "nghe thì an toàn hơn" nhưng thực tế làm tăng thất bại:**
Núm giảm tốc độ hành trình quá sâu hoặc tăng khoảng cách an toàn bám đuôi quá xa (`tgGap` quá lớn hoặc `busSpeed` quá thấp). Khi xe ego tự phanh gấp hoặc bò quá chậm trên đường thông thoáng, các phương tiện xung quanh phản ứng lại: xe sau mất kiên nhẫn bấm còi vượt ẩu, hoặc các xe làn bên lách cắt đầu với cự ly hẹp hơn, làm tăng đột biến nguy cơ va chạm cắt đầu và đâm đuôi từ phía sau.

---

## 7. Từ mô phỏng ra đường thật

**Ba giả định nhạy cảm nhất trong `space.py`:**

1. **Hệ số ma sát đường $\mu$ (phân phối rời rạc 0.8 và 0.5):**
   - *Dữ liệu thay thế:* Dữ liệu đo ma sát mặt đường thực tế từ cảm biến chống trượt (ABS/TCS) của xe chạy thương mại và số liệu quan trắc trạm khí tượng thủy văn theo thời gian thực.
   - *Hướng sai lệch:* Nếu trời mưa to đường trơn trượt có $\mu \approx 0.3 - 0.4$, quãng đường phanh thực tế dài hơn nhiều $\implies$ mô phỏng đang đánh giá quá lạc quan, xác suất tai nạn ngoài đời sẽ cao hơn số liệu tính toán.

2. **Tỉ lệ người đi bộ quan sát xe buýt (`pedLook` phân phối nhị thức 0 hoặc 1):**
   - *Dữ liệu thay thế:* Phân tích video camera giao thông đô thị (CCTV) tại các trạm xe buýt bằng mô hình ước lượng tư thế người (pose estimation) để đo góc quay đầu nhìn dòng xe.
   - *Hướng sai lệch:* Ngoài đời người đi bộ thường vội vã hoặc nhìn điện thoại (`pedLook = 0` chiếm tỷ lệ cao hơn), không chủ động dừng lại nhường xe $\implies$ mô phỏng đang đánh giá thấp rủi ro va chạm với người đi bộ.

3. **Thời gian và khoảng cách xe cắt đầu nhập làn (`cutDur` $\in [3, 9]$ s, `cutGap`):**
   - *Dữ liệu thay thế:* Bộ dữ liệu quỹ đạo xe tự nhiên từ camera góc nhìn trên cao (như highD, rounD) hoặc dữ liệu xe tự hành thực địa quy mô lớn (Waymo Open Dataset, nuScenes).
   - *Hướng sai lệch:* Tài xế đô thị thực tế lái xe quyết liệt hơn, thường tạt đầu với khoảng cách ngắn hơn giả định $\implies$ mô phỏng đánh giá thiếu số vụ va chạm chuyển làn bất ngờ.

---

## 8. Giới hạn

**Ba giới hạn cụ thể của mô phỏng này:**
1. **Hình học đường phố phẳng đơn tuyến:** Thế giới chỉ có một đoạn đường thẳng đơn giản, không có ngã tư, vòng xuyến, dải phân cách phức tạp, gờ giảm tốc hay góc cua khuất tầm nhìn.
2. **Mô hình hành vi tác nhân đơn giản hóa:** Phương tiện xung quanh chỉ tuân theo IDM một chiều và quỹ đạo cắt đầu cosin cố định; tác nhân không có khả năng quan sát gương chiếu hậu, không biết lách tránh chướng ngại vật hay biểu hiện các phản ứng xã hội (nháy đèn, nhường đường, nổi nóng).
3. **Mô hình cảm biến hình học lý tưởng:** Cảm biến giả định quét hoàn hảo mọi vật thể trong tầm 120 m không bị che khuất tia nhìn (line-of-sight raycasting); không mô phỏng độ trễ xử lý (processing latency), nhiễu đo lường bounding box, hay hiện tượng mù cảm biến do mưa bão, sương mù và ánh sáng ngược chói chang.

**Nếu được thêm một tuần:**
Đo đạc ảnh hưởng của **độ trễ nhận thức (perception latency)** kết hợp với mở rộng kịch bản sang **nút giao ngã tư có đèn tín hiệu giao thông (signalized intersection)** để kiểm chứng khả năng phản ứng của planner khi gặp luồng giao thông cắt ngang đa hướng.

---

## 9. Rắc rối của bạn (bước G + chương 10)

- **Rắc rối:** Người đi bộ bất ngờ băng ngang đường ngoài vạch kẻ (jaywalking) từ lề đường phía nam (bên phải xe ego) ở đoạn đường thẳng thoáng đãng sau trạm xe buýt. Ngoài đời giống tình huống người dân tùy tiện bước nhanh xuống lòng đường giữa hai hàng xe hoặc đón xe buýt ngoài trạm quy định.
- **Căn cứ:** Planner chỉ chủ động giảm tốc ở khu vực có vạch kẻ đường cho người đi bộ (`crosswalk`); trên đoạn đường thẳng sau trạm buýt, ego duy trì tốc độ hành trình cao (~12 m/s). Khi người đi bộ bất ngờ lao ra từ lề đường với cự ly kích hoạt gần ($25 - 50$ m) và vận tốc $1.2 - 2.2$ m/s, planner phản ứng chậm hoặc không dự đoán trước ý đồ cắt ngang, dẫn đến phanh không kịp.
- **Giả định (`hazard.json: why`):**
  - `space`: `h0_x` $\in [140.0, 220.0]$ m (đoạn đường thẳng sau trạm buýt); `h0_v` $\in [1.2, 2.2]$ m/s (dải tốc độ người đi bộ từ bước bình thường đến bước nhanh qua đường); `h0_trig` $\in [25.0, 50.0]$ m (khoảng cách kích hoạt thử thách phản xạ xe: phanh gấp hết cỡ sẽ tránh được, nhưng chần chừ sẽ va chạm).
  - `exposure`: `0.04` (trung bình 1 lần xuất hiện trong 25 chuyến đi nội thành, căn cứ theo báo cáo thống kê tai nạn giao thông đô thị về tần suất người đi bộ sang đường tùy tiện).
- **Kết quả theo `evidence/mine.json`:**
  - Tỷ lệ kịch bản khả thi: `accepted = 0.9927` (99.27% $\approx 99\%$, loại `infeasible = 11` trên tổng 1,500 mẫu rút).
  - Thống kê policy gốc (`baseline`):
    - Tổng số va chạm: `crashes = 122`
    - Tránh được bằng phanh hết cỡ: `avoidable = 119`
    - Không thể tránh được: `unavoidable = 1`
    - Không quy kết được: `unattributed = 2`
    - Va chạm tốc độ thấp: `low_speed = 1`
    - Xác suất lỗi: $P(\text{lỗi planner} \mid \text{rắc rối}) = 7.99 \times 10^{-2}$ (khoảng Wilson 95%: $[6.72 \times 10^{-2}, 9.48 \times 10^{-2}]$)
    - Tần suất mỗi chuyến: `per_trip = 3.20e-03` (cận trên `per_trip_hi = 3.79e-03`).
  - Thống kê policy đã chọn (`chosen`):
    - Tổng số va chạm: `crashes = 120`
    - `avoidable = 119`, `unavoidable = 1`, `unattributed = 0`, `low_speed = 1`
    - Xác suất lỗi: $P(\text{lỗi planner} \mid \text{rắc rối}) = 7.99 \times 10^{-2}$ (khoảng Wilson 95%: $[6.72 \times 10^{-2}, 9.48 \times 10^{-2}]$)
    - Tần suất mỗi chuyến: `per_trip = 3.20e-03` (cận trên `per_trip_hi = 3.79e-03`).
  - So sánh tần suất: Tần suất mỗi chuyến của rắc rối này ($3.20 \times 10^{-3}$) cao gấp hơn 3 lần tần suất va chạm lách xe buýt (`bus_bypass` $p \approx 1.0 \times 10^{-3}$), cho thấy đây là rủi ro đô thị nghiêm trọng.
  - **Nhận định về "tránh được là chuẩn lạc quan":**
    - `avoidable` đếm nhiều hơn số va chạm thực tế tránh được vì giả định oracle biết trước thời điểm chướng ngại vật xuất hiện và phanh tối đa ở giới hạn lốp ($\mu g$) ngay lập tức (cận trên của lỗi planner).
    - Ngược lại, oracle chỉ thử duy nhất phương án phanh thẳng mà không đánh lái, nên với những tình huống có thể đánh lái vòng tránh an toàn thì oracle lại bỏ qua, làm nó đếm ít đi.
- **Hình:**
  ![hazard](file:///d:/nghia/vin/TRACK4/day11/Track4-Day11-DoManhNghia-2A202602971-Scenario-Forge-Student/evidence/shots/ch10_hazard.png)
- **Nếu tự lái:** Người lái người quan sát thấy tư thế và chuyển động hướng vào lòng đường của người đi bộ từ xa (> 40 m), nhả ga rà phanh phòng ngừa trước và đánh lái nhẹ sang trái để tạo khoảng cách an toàn, tránh va chạm êm ái mà không cần đạp phanh chết cứng ở giới hạn ma sát lốp.
- **Cách sửa:**
  - *Núm chỉnh hiện tại:* Không có núm chỉnh nào trong `policy_candidates.json` sửa được triệt để rắc rối này vì các núm hiện có chỉ tập trung vào xe cắt đầu (`cutinLat`) hoặc vạch kẻ đường cố định.
  - *Logic mới cần thêm cho planner:* Bổ sung mô-đun **dự đoán ý đồ người đi bộ (pedestrian intent prediction)**: khi phát hiện người đi bộ ở lề đường có hướng vận tốc cắt ngang trục đường, hệ thống tự động kích hoạt chế độ cảnh giới (precautionary yield), giảm tốc độ hành trình xuống dưới 8 m/s và chuẩn bị áp lực phanh trước (brake pre-fill) ngay từ khoảng cách 35 m.
