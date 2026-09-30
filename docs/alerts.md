# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải chờ lâu hơn (>3s) trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span con (retrieval vs generation) để xác định bước nào bất thường.
- Mitigation tạm thời: Rollback prompt về version trước nếu token/generation tăng đột biến, hoặc tắt mock incident/giảm tải.
- Owner: `student-2A202602966`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Tỷ lệ lỗi hệ thống `request_failed / request_received`
- Điều kiện và thời gian duy trì: `error_rate > 2%` trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng gặp lỗi 500 và không nhận được phản hồi từ hệ thống
- Ba bước kiểm tra đầu tiên:
  1. Mở panel Errors trên dashboard để xác định tỷ lệ lỗi và phân bố loại lỗi `error_type`.
  2. Lọc `data/logs.jsonl` theo `event == "request_failed"`, trích xuất `correlation_id` và message detail.
  3. Mở trace trên Langfuse có cùng `correlation_id` để kiểm tra stack trace tại span bị fail.
- Mitigation tạm thời: Kích hoạt circuit breaker hoặc fallback response tĩnh để phục vụ tạm thời người dùng, kiểm tra lại kết nối external services.
- Owner: `student-2A202602966`

## Alert 3

- Tên: `LowRetrievalSuccess`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Tỷ lệ retrieval thành công `tool_success == true / tool_name == "retrieval"`
- Điều kiện và thời gian duy trì: `retrieval_success_rate < 90%` trong 5 phút
- Ảnh hưởng tới người dùng: Chatbot không truy xuất được tài liệu phù hợp, dẫn đến chất lượng câu trả lời giảm sút hoặc câu trả lời chung chung
- Ba bước kiểm tra đầu tiên:
  1. Mở panel Errors trên dashboard để xem tỷ lệ `retrieval_success` giảm từ thời điểm nào.
  2. Lọc `data/logs.jsonl` tìm log có `tool_name == "retrieval"` và `tool_success == false`, lấy `correlation_id`.
  3. Mở Langfuse trace tìm span `retrieval` để kiểm tra thông điệp lỗi (ví dụ: timeout vector store).
- Mitigation tạm thời: Khởi động lại kết nối cơ sở dữ liệu vector store hoặc bật chế độ fallback document retrieval cục bộ.
- Owner: `student-2A202602966`
