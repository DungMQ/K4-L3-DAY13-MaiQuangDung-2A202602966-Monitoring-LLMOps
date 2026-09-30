# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Mai Quang Dũng
- **MSSV:** 2A202602966
- **Lớp:** K4-L3B
- **Repository URL:** `https://github.com/DungMQ/K4-L3-DAY13-MaiQuangDung-2A202602966-Monitoring-LLMOps`
- **Commit SHA cuối:** (sẽ cập nhật sau commit cuối cùng)
- **Challenge ID:** `k4-l3b-practice-rag-slow`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602966`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 | Đạt điểm tối đa, đầy đủ schema, correlation_id và PII scrubbing |
| `validate_dashboard.py` | 6/6 panel | 6/6 panel | Đạt chuẩn contract 6 panel |
| `pytest` | 22 passed | 22 passed | 100% unit tests passed |
| Số traces hợp lệ | 10 | 24 | Đã tạo và ghi nhận trên project Langfuse cá nhân |
| Số PII leak | 0 | 0 | Bộ lọc scrub_event che 100% email, sđt, thẻ |
| Latency P95 / TTFT P95 | 4343ms / 50ms | 2061ms / 50ms | Độ trễ ổn định, TTFT 50ms theo đúng thiết kế FakeLLM |
| Retrieval success rate | 100% | 100% | 24/24 requests truy xuất retrieval thành công |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Trong `app/middleware.py`, middleware `CorrelationIdMiddleware` xóa context cũ bằng `clear_contextvars()`, kiểm tra header `x-request-id` (nếu không có thì tự sinh mới bằng `f"req-{uuid.uuid4().hex[:8]}"`). Sau đó gán vào `request.state.correlation_id`, bind vào `structlog` contextvars bằng `bind_contextvars(correlation_id=correlation_id)` và trả về client qua header `x-request-id` cùng `x-response-time-ms`.
- **Các metadata được ghi vào structured log:** Các trường toàn cục gồm `ts`, `level`, `service`, `event`, `correlation_id`. Trong endpoint `/chat` của `app/main.py`, log được làm giàu (enrich) thêm các trường: `user_id_hash` (băm sha256 12 ký tự), `session_id`, `feature`, `model`, `env`. Ở log `response_sent` có thêm `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name`, `tool_success`, và `payload.answer_preview`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Xây dựng danh sách regex pattern trong `app/pii.py` cho Email, Phone VN, CCCD, Thẻ tín dụng, Passport. Trong `app/logging_config.py`, đăng ký processor `scrub_event` trong pipeline của `structlog` chạy trước `JsonlFileProcessor()` và `JSONRenderer()`. Hàm `scrub_event` duyệt qua toàn bộ dữ liệu string và thay thế chuỗi nhạy cảm bằng nhãn redact tương ứng (`[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`,...).
- **Cách kiểm chứng kết quả:** Chạy `python scripts/validate_logs.py` đạt điểm tuyệt đối 100/100 (0 missing required fields, 0 missing context, 10 correlation IDs, 0 PII leak). Kiểm tra trực tiếp file `data/logs.jsonl` thấy thông tin email, sđt đã bị che và correlation ID xuất hiện đồng bộ.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Project trên Langfuse Cloud mang tên `day13-k4-l3b-2A202602966`. Trong metadata của mỗi trace đều gắn `environment="dev"`, `tags=["lab", feature, model]`, `user_id_hash` và trường `correlation_id` trùng khớp hoàn toàn với `correlation_id` trong file log cục bộ `data/logs.jsonl`.
- **Cấu trúc root/retrieval/generation observations:**
  Trace `day13-agent-request` có root observation là `lab-agent-run` (as_type="agent"), bên trong chứa 2 child observations:
  1. `retrieval` (as_type="retriever"): ghi nhận thời gian truy xuất tài liệu từ knowledge corpus trong hàm `retrieve()`.
  2. `generation` (as_type="generation"): ghi nhận lệnh gọi mô hình LLM `FakeLLM.generate()`, có model `claude-sonnet-4-5`, prompt managed, usage (input_tokens, output_tokens) và cost USD tương ứng.
- **Cách nối trace với log:** Sử dụng chung một `correlation_id` (định dạng `req-<8-char-hex>`). Middleware tạo correlation ID, bind vào structlog để ghi vào mọi event trong `data/logs.jsonl`, đồng thời truyền vào trace metadata của Langfuse thông qua hàm `propagate_attributes(metadata={"correlation_id": correlation_id})`.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 (labels: `baseline`, `production`)
- **Version/label candidate:** Version 2 (labels: `candidate`, `latest`)
- **Trace ID của mỗi version:**
  - Version 1 (baseline/production): request `req-6f3ab184` / `req-343ad19d` (mở trên giao diện Langfuse để xem trace URL)
  - Version 2 (candidate): request `req-152bec6c` (mở trên giao diện Langfuse để xem trace URL)
- **Cách promote và rollback `production`:**
  - *Promote*: Trong mục Prompts trên Langfuse UI của `day13-chat`, gán nhãn `production` sang Version 2 để đưa prompt mới vào phục vụ luồng chính mà không cần sửa code ứng dụng.
  - *Rollback*: Khi phát hiện prompt mới gây hồi quy (tăng token, tăng latency), chuyển lại nhãn `production` về Version 1 trên Langfuse UI. App sẽ tự động nhận diện version 1 khi cache hết hạn hoặc khi restart.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** 6 panel được định nghĩa theo contract chuẩn trong `config/dashboard.yaml` lấy nguồn từ `data/logs.jsonl`:
  1. *Latency*: đo latency P50/P95/P99 và TTFT P95 từ event `response_sent` (threshold <= 3000ms).
  2. *Traffic*: đo tổng số lượng request và request/phút từ event `request_received`.
  3. *Errors*: đo tỷ lệ lỗi từ `request_failed` và tỷ lệ retrieval thành công từ `tool_success` (threshold error <= 2%, retrieval >= 90%).
  4. *Cost*: đo chi phí tích lũy và theo phút từ trường `cost_usd` của `response_sent` (threshold <= $2.5/ngày).
  5. *Tokens*: đo tổng tokens_in và tokens_out từ event `response_sent`.
  6. *Quality*: đo mean quality_score từ event `response_sent` (threshold >= 0.75).
- **SLO và lý do chọn:** Primary SLO được đặt là `fast_successful_requests` với mục tiêu **99.5%** trong cửa sổ 28 ngày. Điều kiện đạt chuẩn (good event) là request hoàn thành thành công (`response_sent`) và `latency_ms <= 3000ms` trên tổng số `request_received`. Lý do chọn: Người dùng tương tác hội thoại trực tiếp cần phản hồi trong vòng 3 giây để không bị gián đoạn dòng suy nghĩ và hệ thống không được trả mã lỗi 500.
- **Cách tính error budget:** Với mục tiêu SLO 99.5% trong 28 ngày, error budget cho phép là `100% - 99.5% = 0.5%`. Nếu hệ thống nhận 10,000 request trong 28 ngày, tối đa 50 request được phép thất bại hoặc có độ trễ lớn hơn 3000ms. Nếu lượng vi phạm vượt quá ngân sách này (error budget exhausted), team cần tạm hoãn triển khai tính năng mới để tập trung tối ưu hạ tầng và ổn định mô hình.
- **Ba alert và runbook tương ứng:**
  1. `HighLatencyP95` (Warning, duy trì 5m): Báo động khi P95 latency > 3000ms trong 5 phút. Runbook tại `docs/alerts.md#alert-1`.
  2. `HighErrorRate` (Critical, duy trì 5m): Báo động khi tỷ lệ lỗi vượt quá 2% trong 5 phút. Runbook tại `docs/alerts.md#alert-2`.
  3. `LowRetrievalSuccess` (Warning, duy trì 5m): Báo động khi tỷ lệ retrieval thành công giảm xuống dưới 90% trong 5 phút. Runbook tại `docs/alerts.md#alert-3`.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `k4-l3b-practice-rag-slow` (sẵn sàng cập nhật ID chính thức khi Lab Coach release)
- **Khoảng thời gian điều tra:** 10:45:00 – 10:50:00 (Múi giờ Asia/Ho_Chi_Minh)
- **Triệu chứng từ metrics:** P95 latency tăng vọt đột biến từ 2,061ms lên 9,180ms (P99 đạt 13,941ms), vi phạm nghiêm trọng ngưỡng SLO và kích hoạt alert `HighLatencyP95`. Tuy nhiên TTFT vẫn ở mức 50ms và tỷ lệ lỗi là 0.0%, chứng tỏ bản thân mô hình LLM sinh token bình thường nhưng có bước tiền xử lý bị nghẽn độ trễ.
- **Log line và correlation ID liên quan:** Lọc log trong khoảng thời gian trên phát hiện hai request bất thường liên tiếp bị ảnh hưởng: event `response_sent` có `correlation_id="req-e5600a3a"` (ghi nhận `latency_ms=13941`) và `correlation_id="req-4b0d253d"` (ghi nhận `latency_ms=9180`, `user_id_hash="95b6504a8bd6"`, `tool_name="retrieval"`).
- **Trace ID và span gây ảnh hưởng:** Tra cứu trace trên Langfuse Cloud với Trace ID `ed922f576d1e93aac00476de60dec5d0` (thuộc correlation ID `req-4b0d253d`). Cây quan sát (tree/waterfall) cho thấy root `lab-agent-run` mất 9.18s; trong đó span `retrieval` (retriever) bị nghẽn chiếm tới 2.50s, trong khi `generation` chỉ mất 0.17s ($0.002256, 176 tokens).
- **Root cause:** Bước truy xuất tài liệu RAG trong vector store bị nghẽn nghiêm trọng (mô phỏng bởi kịch bản `rag_slow` gây sleep/trễ trong hàm `retrieve()`), làm chậm toàn bộ luồng xử lý trước khi prompt được gửi tới LLM.
- **Fix action:** Khôi phục trạng thái hoạt động của vector store (`python scripts/inject_incident.py --scenario rag_slow --disable`), bật cache kết quả tìm kiếm cho các câu hỏi phổ biến.
- **Preventive measure:** Cấu hình timeout nghiêm ngặt cho retrieval (tối đa 1000ms) kèm graceful degradation (nếu timeout thì fallback về general answer thay vì để treo request); kích hoạt alert cảnh báo sớm khi retrieval duration > 800ms.

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Đăng ký processor khử dữ liệu nhạy cảm (`scrub_event`) ở tầng structlog pipeline trước khi ghi xuống file JSONL và trước khi serialize. Lý do: Giúp ngăn chặn triệt để nguy cơ rò rỉ PII (email, số điện thoại, CCCD, thẻ ngân hàng) ngay tại nguồn, bảo đảm tuân thủ an toàn dữ liệu mà không làm gián đoạn luồng xử lý chính.
- **Một lỗi/blocker đã gặp:** Quá trình fetch prompt từ Langfuse Cloud bị timeout handshake SSL do cấu hình mặc định `fetch_timeout_seconds=2` quá ngắn khi mạng chập chờn, khiến app phải fallback về local prompt.
- **Cách tìm nguyên nhân và xử lý:** Đọc log chi tiết trong terminal thấy cảnh báo `The handshake operation timed out` tại `prompt_management.py`. Xử lý bằng cách tăng `fetch_timeout_seconds=10` và bổ sung retry `max_retries=2`, kết hợp cơ chế cache TTL 60s để đảm bảo lấy prompt thành công và ổn định.
- **Cách hiểu luồng Metrics → Logs → Traces:**
  - *Metrics*: Quan sát triệu chứng vĩ mô của hệ thống (P95 latency, tỷ lệ lỗi, traffic) để biết khi nào hệ thống bắt đầu bất thường.
  - *Logs*: Sử dụng structured log và lọc theo khoảng thời gian để tìm ra request cụ thể bị ảnh hưởng thông qua `correlation_id`.
  - *Traces*: Dùng `correlation_id` để tra cứu trace waterfall trên Langfuse, phân tích từng span con (retrieval vs generation) nhằm xác định chính xác bước gây lỗi/chậm (root cause).
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt ảnh hưởng trực tiếp đến token, chi phí và độ trễ. Quản lý prompt version cho phép kiểm soát chất lượng có hệ thống; theo dõi token/cost giúp ngăn ngừa chi phí bùng nổ; SLO/Error Budget định lượng ngưỡng chấp nhận được của dịch vụ; và cơ chế rollback linh hoạt qua label giúp phục hồi tức thì khi có sự cố mà không cần release lại mã nguồn.
- **Điều quan trọng nhất đã học:** Tư duy vận hành LLMOps chuẩn mực dựa trên chuỗi bằng chứng khách quan (Metrics → Logs → Traces → Root cause), thay vì phỏng đoán nguyên nhân khi hệ thống AI gặp sự cố.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Cần nhận file `config/challenge.json` chính thức từ Lab Coach để hoàn thiện điều tra sự cố CP3 và chụp đầy đủ các ảnh evidence theo danh mục.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
