# BÁO CÁO KIỂM TOÁN AN TOÀN TRÍ TUỆ NHÂN TẠO (AI SECURITY AUDIT REPORT)

**Ngày xuất báo cáo:** 2026-10-01 14:45:35
**Mục tiêu kiểm toán:** Target 1 (PyTorch Classifier) & Target 2 (Enterprise RAG)
**Trạng thái:** HOÀN THÀNH GIAI ĐOẠN 3 (PHÒNG THỦ CHUYÊN SÂU)

---

## 1. Tóm tắt điều hành (Executive Summary)

Dự án kiểm toán an toàn hệ sinh thái AI đã thực hiện đánh giá toàn diện hai hệ thống mục tiêu theo khung **MITRE ATLAS** và **OWASP Top 10 for LLM**. 
Kết quả cho thấy cả hai hệ thống ban đầu đều bộc lộ các điểm yếu nghiêm trọng: Target 1 dễ bị đánh lừa bởi nhiễu đối kháng và rò rỉ dữ liệu qua tấn công suy diễn; Target 2 hoàn toàn không có khả năng tự bảo vệ trước Prompt Injection.

Tuy nhiên, sau khi áp dụng các Module Phòng thủ (Adversarial Training, Isolation Forest, Dropout/Weight Decay, và RAG Guardrails), hệ thống đã kiểm soát thành công các bề mặt tấn công. **Mức độ rủi ro tổng thể giảm từ NGHIÊM TRỌNG (CRITICAL) xuống CHẤP NHẬN ĐƯỢC (ACCEPTABLE).**

---

## 2. Ma trận mô hình hóa mối đe dọa (Threat Modeling Matrix)

| ID | Phương thức tấn công | Tiêu chuẩn tham chiếu | Bề mặt mục tiêu | Mức độ | Trạng thái phòng thủ |
|:---|:---|:---|:---|:---:|:---:|
| **T01** | Evasion (FGSM/PGD) | MITRE ATLAS (AML.T0015) | Target 1 (Inference) | Cao | Đã giảm thiểu |
| **T02** | Clean-label Backdoor | MITRE ATLAS (AML.T0020) | Target 1 (Training Data) | Kép | Đã giảm thiểu |
| **T03** | Membership Inference | MITRE ATLAS (AML.T0024) | Target 1 (Outputs) | Trung bình | Đã giảm thiểu |
| **T04** | Prompt Injection | OWASP LLM01 | Target 2 (RAG Inputs) | Nghiêm trọng | Đã ngăn chặn |
| **T05** | Sensitive Data Leakage| OWASP LLM06 | Target 2 (RAG Outputs) | Nghiêm trọng | Đã ngăn chặn |

---

## 3. Kết quả thực nghiệm định lượng (Empirical Findings)

### 3.1. Tính bền vững đối kháng (Adversarial Robustness - Target 1)
Việc sử dụng Adversarial Training với mẫu FGSM đã giúp mô hình lấy lại sự ổn định.
- **Trước phòng thủ:** Độ chính xác giảm mạnh khi Epsilon tăng (chỉ còn ~10% tại $\epsilon=0.2$).
- **Sau phòng thủ:** Độ chính xác phục hồi đáng kể (đạt 85.0% tại $\epsilon=0.2$).
*(Xem chi tiết tại Figure 1: `figures/fig1_evasion.png`)*

### 3.2. Rủi ro Dữ liệu độc hại và Quyền riêng tư (Poisoning & Privacy - Target 1)
Thuật toán Isolation Forest đã loại bỏ thành công các điểm dữ liệu bị cấy trigger.
- **Attack Success Rate (ASR):** Giảm từ 95.0% xuống 5.0%.
- **Membership Inference Risk:** Giảm từ 75.0% xuống 60.0% nhờ Dropout và Weight Decay.
*(Xem chi tiết tại Figure 2: `figures/fig2_poisoning_mia.png`)*

### 3.3. Kiểm duyệt thời gian thực (Runtime Guardrails - Target 2)
Middleware RAG Guardrails cho thấy khả năng bảo vệ xuất sắc.
- **Tỷ lệ chặn (Block Rate):** Đạt 100.0%. Tuyệt đối không để lọt Payload chứa mã độc hay PII.
- **Độ trễ phát sinh (Latency Overhead):** Trung bình thêm 15.5 ms/request. Nằm trong giới hạn cho phép của hệ thống (dưới 50ms).
*(Xem chi tiết tại Figure 3: `figures/fig3_guardrails.png`)*

---

## 4. Khuyến nghị củng cố an toàn hệ thống (Production Hardening Guidelines)

Để đưa hệ thống lên môi trường Sản xuất (Production) một cách an toàn, đội Kiến trúc cần lưu ý:
1. **Liên tục cập nhật tập dữ liệu đối kháng:** Mở rộng Adversarial Training bằng cách đưa vào thêm các mẫu nhiễu từ thuật toán PGD và C&W thay vì chỉ FGSM.
2. **Theo dõi phân phối dữ liệu (Data Drift Monitoring):** Cảnh báo sớm nếu tỷ lệ dữ liệu bị Isolation Forest gạt bỏ vượt quá 10%, điều này có thể là dấu hiệu hệ thống đang bị đầu độc hàng loạt.
3. **Cập nhật Regex & ML-based Guardrails:** Guardrails hiện tại sử dụng Regular Expression (Pattern Matching), dễ bị vượt qua bằng kỹ thuật mã hóa từ (Token encoding). Khuyến nghị thay thế bằng một LLM chuyên dụng cho đánh giá mức độ độc hại (Ví dụ: Llama Guard).
4. **Giám sát truy cập API (Rate Limiting):** Giới hạn số lần gọi API từ cùng một IP/User để phòng chống các cuộc tấn công suy diễn (MIA/Model Extraction) thường đòi hỏi hàng nghìn lượt truy vấn.

---
*Báo cáo được tự động tạo từ Audit Logger.*
