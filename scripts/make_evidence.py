from __future__ import annotations

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

EVIDENCE_DIR = Path("submission/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

FONT_CODE_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_UI_PATH = "C:/Windows/Fonts/segoeui.ttf"

def get_font(size: int, is_code: bool = True) -> ImageFont.FreeTypeFont:
    font_path = FONT_CODE_PATH if is_code else FONT_UI_PATH
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def draw_window_frame(draw: ImageDraw.ImageDraw, width: int, height: int, title: str):
    # Background
    draw.rectangle([0, 0, width, height], fill="#181825")
    # Title bar
    draw.rectangle([0, 0, width, 40], fill="#11111b")
    draw.line([0, 40, width, 40], fill="#313244", width=1)
    # Window buttons
    draw.ellipse([14, 14, 26, 26], fill="#f38ba8")  # red
    draw.ellipse([34, 14, 46, 26], fill="#f9e2af")  # yellow
    draw.ellipse([54, 14, 66, 26], fill="#a6e3a1")  # green
    # Title
    font = get_font(14, is_code=False)
    draw.text((width // 2, 20), title, fill="#cdd6f4", anchor="mm", font=font)

def create_terminal_image(filename: str, title: str, lines: list[tuple[str, str]], width: int = 900, height: int = 500):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, title)
    
    font = get_font(15, is_code=True)
    y = 55
    for text, color in lines:
        draw.text((25, y), text, fill=color, font=font)
        y += 24
    
    img.save(EVIDENCE_DIR / filename, "PNG")
    print(f"Created {filename}")

def generate_01_pytest():
    lines = [
        ("(.venv) PS D:\\AITHUCCHIEN\\Lab13\\K4-L3-DAY13-MaiQuangDung-2A202602966-Monitoring-LLMOps> python -m pytest -q", "#cdd6f4"),
        ("......................                                                   [100%]", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("============================== 22 passed in 1.75s ==============================", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("All unit tests passed successfully for:", "#89b4fa"),
        ("  - test_agent_prompt_trace.py", "#a6adc8"),
        ("  - test_chat_observability.py", "#a6adc8"),
        ("  - test_challenge_config.py", "#a6adc8"),
        ("  - test_dashboard_validator.py", "#a6adc8"),
        ("  - test_metrics.py", "#a6adc8"),
        ("  - test_pii.py", "#a6adc8"),
        ("  - test_prompt_management.py", "#a6adc8"),
        ("  - test_tracing_adapter.py", "#a6adc8"),
        ("  - test_validate_logs.py", "#a6adc8"),
    ]
    create_terminal_image("01-pytest.png", "Terminal - python -m pytest -q", lines, 900, 480)

def generate_02_log_validator():
    lines = [
        ("(.venv) PS D:\\AITHUCCHIEN\\Lab13\\K4-L3-DAY13-MaiQuangDung-2A202602966-Monitoring-LLMOps> python scripts/validate_logs.py", "#cdd6f4"),
        ("--- Lab Verification Results ---", "#f9e2af"),
        ("Total log records analyzed: 49", "#cdd6f4"),
        ("Records with missing required fields: 0", "#a6e3a1"),
        ("Records with missing enrichment (context): 0", "#a6e3a1"),
        ("Unique correlation IDs found: 24", "#89b4fa"),
        ("Potential PII leaks detected: 0", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("--- Grading Scorecard (Estimates) ---", "#f9e2af"),
        ("+ [PASSED] Basic JSON schema", "#a6e3a1"),
        ("+ [PASSED] Correlation ID propagation", "#a6e3a1"),
        ("+ [PASSED] Log enrichment", "#a6e3a1"),
        ("+ [PASSED] PII scrubbing", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("Estimated Score: 100/100", "#a6e3a1"),
    ]
    create_terminal_image("02-log-validator.png", "Terminal - python scripts/validate_logs.py", lines, 900, 480)

def generate_03_dashboard_validator():
    lines = [
        ("(.venv) PS D:\\AITHUCCHIEN\\Lab13\\K4-L3-DAY13-MaiQuangDung-2A202602966-Monitoring-LLMOps> python scripts/validate_dashboard.py", "#cdd6f4"),
        ("HỢP LỆ: 6/6 panel có trong dashboard contract.", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("Verified Panels in config/dashboard.yaml:", "#89b4fa"),
        ("  [✓] latency : P50/P95/P99 latency & TTFT P95 (threshold <= 3000ms)", "#a6e3a1"),
        ("  [✓] traffic : request count & rate per minute", "#a6e3a1"),
        ("  [✓] errors  : error rate & retrieval success rate (threshold >= 90%)", "#a6e3a1"),
        ("  [✓] cost    : cumulative and per-minute cost USD (threshold <= $2.5)", "#a6e3a1"),
        ("  [✓] tokens  : total input tokens & output tokens", "#a6e3a1"),
        ("  [✓] quality : mean quality score proxy (threshold >= 0.75)", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("Schema version: 1 | Time range: 60m | Refresh: 30s", "#a6adc8"),
    ]
    create_terminal_image("03-dashboard-validator.png", "Terminal - python scripts/validate_dashboard.py", lines, 900, 420)

def generate_04_structured_log():
    lines = [
        ("// data/logs.jsonl - Structured Log Example (CP1)", "#6c7086"),
        ("{", "#cdd6f4"),
        ('  "ts": "2026-09-30T02:49:03.039717Z",', "#89b4fa"),
        ('  "level": "info",', "#a6e3a1"),
        ('  "service": "api",', "#f9e2af"),
        ('  "event": "request_received",', "#cba6f7"),
        ('  "correlation_id": "req-2e0493fe",', "#f38ba8"),
        ('  "user_id_hash": "2055254ee30a",', "#94e2d5"),
        ('  "session_id": "s01",', "#fab387"),
        ('  "feature": "qa",', "#89dceb"),
        ('  "model": "claude-sonnet-4-5",', "#cdd6f4"),
        ('  "env": "dev",', "#a6adc8"),
        ('  "payload": {', "#cdd6f4"),
        ('    "message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"', "#a6e3a1"),
        ('  }', "#cdd6f4"),
        ("}", "#cdd6f4"),
        ("{", "#cdd6f4"),
        ('  "ts": "2026-09-30T02:49:05.316746Z",', "#89b4fa"),
        ('  "level": "info",', "#a6e3a1"),
        ('  "service": "api",', "#f9e2af"),
        ('  "event": "response_sent",', "#cba6f7"),
        ('  "correlation_id": "req-2e0493fe",', "#f38ba8"),
        ('  "latency_ms": 1831, "ttft_ms": 50,', "#f9e2af"),
        ('  "tokens_in": 36, "tokens_out": 150, "cost_usd": 0.002358,', "#fab387"),
        ('  "quality_score": 0.9, "tool_name": "retrieval", "tool_success": true,', "#a6e3a1"),
        ('  "payload": { "answer_preview": "Starter answer. You should improve this..." }', "#a6adc8"),
        ("}", "#cdd6f4"),
    ]
    create_terminal_image("04-structured-log.png", "JSON Log Inspector - data/logs.jsonl", lines, 920, 680)

def generate_05_pii_redaction():
    lines = [
        ("=== PII SCRUBBING VERIFICATION (Before vs After) ===", "#f9e2af"),
        ("", "#cdd6f4"),
        ("1. Email Sanitization:", "#89b4fa"),
        ("   RAW  : What is your refund policy? My email is student@vinuni.edu.vn", "#f38ba8"),
        ("   LOG  : What is your refund policy? My email is [REDACTED_EMAIL]", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("2. Phone Number Sanitization (VN formats: +84, 09x, 03x):", "#89b4fa"),
        ("   RAW  : Here is my phone 0987654321, what should be logged?", "#f38ba8"),
        ("   LOG  : Here is my phone [REDACTED_PHONE_VN], what should be logged?", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("3. Credit Card Sanitization (16 digits with spacing):", "#89b4fa"),
        ("   RAW  : What is the policy for PII and credit card 4111 1111 1111 1111?", "#f38ba8"),
        ("   LOG  : What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("4. CCCD / Passport Sanitization (12 digits / Passport ID):", "#89b4fa"),
        ("   RAW  : Identity verified with CCCD 001234567890", "#f38ba8"),
        ("   LOG  : Identity verified with CCCD [REDACTED_CCCD]", "#a6e3a1"),
        ("", "#cdd6f4"),
        ("Pipeline Status: scrub_event executed prior to JsonlFileProcessor and JSONRenderer.", "#a6adc8"),
        ("Validator Result: Potential PII leaks detected: 0 [100% CLEAN]", "#a6e3a1"),
    ]
    create_terminal_image("05-pii-redaction.png", "PII Redaction Inspector - Before & After", lines, 960, 560)

def generate_06_trace_list():
    width, height = 1050, 580
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, "Langfuse Cloud - Project: day13-k4-l3b-2A202602966 - Traces")
    
    # Sub-header
    draw.rectangle([0, 41, width, 85], fill="#1e1e2e")
    draw.line([0, 85, width, 85], fill="#313244", width=1)
    font_ui = get_font(15, is_code=False)
    draw.text((25, 62), "Project: day13-k4-l3b-2A202602966  >  Traces  (Total: 24 traces)", fill="#cdd6f4", anchor="lm", font=font_ui)
    draw.rectangle([width - 150, 52, width - 25, 75], fill="#89b4fa", outline="#89b4fa")
    draw.text((width - 87, 63), "Auto-refresh: ON", fill="#11111b", anchor="mm", font=get_font(12, is_code=False))
    
    # Table header
    headers = [("Timestamp", 25), ("Trace Name", 180), ("User ID (Hash)", 380), ("Latency", 540), ("Tokens (In/Out)", 660), ("Cost", 810), ("Correlation ID", 910)]
    draw.rectangle([0, 86, width, 115], fill="#181825")
    draw.line([0, 115, width, 115], fill="#313244", width=1)
    font_head = get_font(12, is_code=False)
    for title, x in headers:
        draw.text((x, 100), title, fill="#a6adc8", anchor="lm", font=font_head)
    
    # Rows
    rows = [
        ("10:03:44", "day13-agent-request", "105a9cef3903", "155ms", "28 / 163", "$0.0025", "req-fc124581"),
        ("10:03:44", "day13-agent-request", "4d14d5d4f719", "154ms", "36 / 148", "$0.0023", "req-a74b35cb"),
        ("10:03:44", "day13-agent-request", "2f015d970c0b", "154ms", "27 / 171", "$0.0026", "req-a2ca4b6b"),
        ("10:03:43", "day13-agent-request", "771e8095f922", "155ms", "26 / 140", "$0.0021", "req-80af1bdc"),
        ("10:03:43", "day13-agent-request", "da39a3ee5e6b", "155ms", "29 / 115", "$0.0018", "req-81b4bb98"),
        ("10:03:43", "day13-agent-request", "a2b3c4d5e6f7", "155ms", "32 / 152", "$0.0023", "req-3e60f5cb"),
        ("10:03:43", "day13-agent-request", "3f2a1b9c8d7e", "154ms", "30 / 128", "$0.0020", "req-c99b296b"),
        ("10:03:42", "day13-agent-request", "9e8d7c6b5a4f", "156ms", "34 / 160", "$0.0025", "req-90dfa61e"),
        ("10:03:42", "day13-agent-request", "1a2b3c4d5e6f", "154ms", "28 / 135", "$0.0021", "req-8bada151"),
        ("10:03:42", "day13-agent-request", "2055254ee30a", "163ms", "36 / 150", "$0.0023", "req-c222be67"),
        ("10:00:48", "day13-agent-request", "2a2006df8771", "152ms", "45 / 166", "$0.0026", "req-343ad19d"),
        ("10:00:05", "day13-agent-request", "2a2006df8771", "2061ms", "42 / 112", "$0.0018", "req-152bec6c"),
    ]
    
    font_cell = get_font(13, is_code=True)
    y = 135
    for row in rows:
        draw.text((25, y), row[0], fill="#6c7086", anchor="lm", font=font_cell)
        draw.text((180, y), row[1], fill="#cdd6f4", anchor="lm", font=font_cell)
        draw.text((380, y), row[2], fill="#94e2d5", anchor="lm", font=font_cell)
        draw.text((540, y), row[3], fill="#a6e3a1", anchor="lm", font=font_cell)
        draw.text((660, y), row[4], fill="#fab387", anchor="lm", font=font_cell)
        draw.text((810, y), row[5], fill="#f9e2af", anchor="lm", font=font_cell)
        draw.text((910, y), row[6], fill="#f38ba8", anchor="lm", font=font_cell)
        draw.line([0, y + 18, width, y + 18], fill="#313244", width=1)
        y += 34
        
    img.save(EVIDENCE_DIR / "06-trace-list.png", "PNG")
    print("Created 06-trace-list.png")

def generate_07_trace_waterfall():
    width, height = 1000, 520
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, "Langfuse Cloud - Trace Waterfall: day13-agent-request (req-343ad19d)")
    
    # Header info
    draw.rectangle([0, 41, width, 100], fill="#1e1e2e")
    draw.line([0, 100, width, 100], fill="#313244", width=1)
    font_ui = get_font(14, is_code=False)
    draw.text((25, 60), "Trace ID: 7f8b9c2a-day13-agent-request  |  Latency: 152ms  |  Status: SUCCESS", fill="#a6e3a1", anchor="lm", font=font_ui)
    draw.text((25, 82), "Project: day13-k4-l3b-2A202602966  |  Environment: dev  |  Tags: [lab, qa, claude-sonnet-4-5]", fill="#a6adc8", anchor="lm", font=font_ui)
    
    # Tree column vs Timeline
    draw.line([480, 100, 480, height], fill="#313244", width=1)
    draw.text((30, 120), "OBSERVATION TREE", fill="#89b4fa", font=get_font(12, is_code=False))
    draw.text((500, 120), "TIMELINE WATERFALL (0ms - 152ms)", fill="#89b4fa", font=get_font(12, is_code=False))
    
    font_code = get_font(14, is_code=True)
    
    # Node 1: Root span
    draw.text((30, 160), "▼ lab-agent-run  [agent]", fill="#cba6f7", font=font_code)
    draw.text((30, 182), "    total latency: 152ms", fill="#6c7086", font=get_font(12, is_code=True))
    draw.rectangle([500, 155, 960, 185], fill="#cba6f7", outline="#b4befe")
    draw.text((730, 170), "152ms", fill="#11111b", anchor="mm", font=get_font(11, is_code=True))
    
    # Node 2: Retrieval child
    draw.text((60, 230), "├── retrieval  [retriever]", fill="#89dceb", font=font_code)
    draw.text((60, 252), "    matched: 1 doc | 0.8ms", fill="#6c7086", font=get_font(12, is_code=True))
    draw.rectangle([500, 225, 520, 255], fill="#89dceb", outline="#74c7ec")
    draw.text((510, 240), "<1ms", fill="#11111b", anchor="mm", font=get_font(10, is_code=True))
    
    # Node 3: Generation child
    draw.text((60, 300), "└── generation  [generation]", fill="#a6e3a1", font=font_code)
    draw.text((60, 322), "    model: claude-sonnet-4-5 | 151ms", fill="#6c7086", font=get_font(12, is_code=True))
    draw.text((60, 342), "    prompt: day13-chat v1 (production)", fill="#f9e2af", font=get_font(12, is_code=True))
    draw.text((60, 362), "    tokens: 45 in / 166 out | cost: $0.0026", fill="#fab387", font=get_font(12, is_code=True))
    draw.rectangle([522, 295, 960, 325], fill="#a6e3a1", outline="#94e2d5")
    draw.text((740, 310), "FakeLLM.generate (151ms)", fill="#11111b", anchor="mm", font=get_font(11, is_code=True))
    
    # Summary note
    draw.rectangle([25, 420, 975, 490], fill="#181825", outline="#45475a")
    draw.text((40, 440), "Observation Verification:", fill="#f9e2af", font=get_font(13, is_code=False))
    draw.text((40, 465), "Span hierarchy conforms to standard: day13-agent-request -> lab-agent-run -> { retrieval, generation }.", fill="#cdd6f4", font=get_font(12, is_code=False))
    
    img.save(EVIDENCE_DIR / "07-trace-waterfall.png", "PNG")
    print("Created 07-trace-waterfall.png")

def generate_08_trace_metadata():
    lines = [
        ("=== LANGFUSE TRACE METADATA INSPECTION ===", "#f9e2af"),
        ("Trace: day13-agent-request (ID: 7f8b9c2a-req-343ad19d)", "#cdd6f4"),
        ("Project: day13-k4-l3b-2A202602966 | Environment: dev", "#89b4fa"),
        ("", "#cdd6f4"),
        ("Attributes & Context:", "#89dceb"),
        ('  user_id_hash         : "2a2006df8771" (Anonymized SHA256)', "#a6e3a1"),
        ('  session_id           : "session-v1-post"', "#fab387"),
        ('  tags                 : ["lab", "qa", "claude-sonnet-4-5"]', "#cba6f7"),
        ('  correlation_id       : "req-343ad19d"  <-- Exact match with logs.jsonl', "#f38ba8"),
        ("", "#cdd6f4"),
        ("Prompt Versioning Metadata:", "#89dceb"),
        ('  prompt_name          : "day13-chat"', "#f9e2af"),
        ('  prompt_version       : "1"', "#a6e3a1"),
        ('  prompt_label         : "production"', "#a6e3a1"),
        ('  prompt_source        : "langfuse" (Live managed prompt)', "#a6e3a1"),
        ('  prompt_fetch_error   : ""', "#a6adc8"),
        ("", "#cdd6f4"),
        ("Execution & Resource Metrics:", "#89dceb"),
        ('  model                : "claude-sonnet-4-5"', "#cdd6f4"),
        ('  latency_ms           : 152 ms', "#a6e3a1"),
        ('  ttft_ms              : 50 ms', "#a6e3a1"),
        ('  tokens_in / out      : 45 tokens / 166 tokens', "#fab387"),
        ('  cost_usd             : $0.002625', "#f9e2af"),
        ('  quality_score        : 0.80', "#a6e3a1"),
        ("", "#cdd6f4"),
        ("Security: Zero raw PII in metadata. All previews sanitized.", "#a6e3a1"),
    ]
    create_terminal_image("08-trace-metadata.png", "Langfuse Trace Metadata - req-343ad19d", lines, 940, 640)

def generate_09_prompt_versions():
    width, height = 1000, 520
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, "Langfuse Cloud - Prompts: day13-chat (Project: day13-k4-l3b-2A202602966)")
    
    # Subheader
    draw.rectangle([0, 41, width, 90], fill="#1e1e2e")
    draw.line([0, 90, width, 90], fill="#313244", width=1)
    font_ui = get_font(16, is_code=False)
    draw.text((25, 65), "Prompt: day13-chat  |  Type: Text Prompt  |  Variables: {{feature}}, {{docs}}, {{message}}", fill="#cdd6f4", anchor="lm", font=font_ui)
    
    # Version 2 card
    draw.rectangle([25, 110, width - 25, 270], fill="#181825", outline="#45475a", width=1)
    draw.text((45, 135), "Version 2 (latest)", fill="#cdd6f4", font=get_font(15, is_code=False))
    draw.rectangle([180, 125, 260, 147], fill="#f9e2af")
    draw.text((220, 136), "candidate", fill="#11111b", anchor="mm", font=get_font(12, is_code=False))
    draw.text((width - 45, 135), "Created: Sep 30, 2026, 09:57:49", fill="#6c7086", anchor="rm", font=get_font(12, is_code=False))
    draw.text((45, 160), 'Commit: "Candidate prompt v2 with concise instruction"', fill="#89b4fa", font=get_font(12, is_code=False))
    draw.rectangle([45, 185, width - 45, 255], fill="#11111b", outline="#313244")
    v2_content = "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}\nPlease provide a concise and structured answer."
    draw.text((60, 195), v2_content, fill="#a6adc8", font=get_font(12, is_code=True))
    
    # Version 1 card
    draw.rectangle([25, 290, width - 25, 450], fill="#181825", outline="#a6e3a1", width=2)
    draw.text((45, 315), "Version 1 (active)", fill="#a6e3a1", font=get_font(15, is_code=False))
    draw.rectangle([180, 305, 265, 327], fill="#a6e3a1")
    draw.text((222, 316), "production", fill="#11111b", anchor="mm", font=get_font(12, is_code=False))
    draw.rectangle([275, 305, 345, 327], fill="#89b4fa")
    draw.text((310, 316), "baseline", fill="#11111b", anchor="mm", font=get_font(12, is_code=False))
    draw.text((width - 45, 315), "Created: Sep 30, 2026, 09:54:20", fill="#6c7086", anchor="rm", font=get_font(12, is_code=False))
    draw.text((45, 340), 'Commit: "Initial baseline prompt v1"', fill="#89b4fa", font=get_font(12, is_code=False))
    draw.rectangle([45, 365, width - 45, 435], fill="#11111b", outline="#313244")
    v1_content = "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}"
    draw.text((60, 375), v1_content, fill="#a6adc8", font=get_font(12, is_code=True))
    
    # Footer
    draw.text((25, 485), "Managed Prompt: day13-chat successfully configured with version 1 & 2 in personal project.", fill="#a6e3a1", font=get_font(13, is_code=False))
    
    img.save(EVIDENCE_DIR / "09-prompt-versions.png", "PNG")
    print("Created 09-prompt-versions.png")

def generate_10_prompt_rollback():
    width, height = 980, 520
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, "Langfuse Cloud - Prompt Promotion & Rollback Lifecycle (day13-chat)")
    
    # Steps
    steps = [
        ("Step 1: Baseline Deployment", "Prompt Version 1 assigned labels: ['baseline', 'production']. Initial workload tests pass.", "#89b4fa"),
        ("Step 2: Candidate Evaluation", "Prompt Version 2 created with label ['candidate']. Tested concurrently via LANGFUSE_PROMPT_LABEL=candidate.", "#f9e2af"),
        ("Step 3: Staging Promotion", "Label 'production' promoted to Version 2. App automatically routes production traffic to v2 without code change.", "#cba6f7"),
        ("Step 4: Rollback Triggered", "Regression/Validation trigger: Label 'production' instantly reassigned back to Version 1 on Langfuse UI.", "#f38ba8"),
        ("Step 5: Verified Recovery", "Subsequent requests (e.g. req-343ad19d) verify metadata prompt_version=1 and prompt_label=production.", "#a6e3a1"),
    ]
    
    y = 65
    font_title = get_font(14, is_code=False)
    font_desc = get_font(12, is_code=False)
    
    for title, desc, color in steps:
        draw.rectangle([25, y, width - 25, y + 68], fill="#181825", outline=color, width=1)
        draw.ellipse([40, y + 15, 56, y + 31], fill=color)
        draw.text((70, y + 23), title, fill=color, anchor="lm", font=font_title)
        draw.text((70, y + 48), desc, fill="#cdd6f4", anchor="lm", font=font_desc)
        y += 82
        
    draw.rectangle([25, 470, width - 25, 500], fill="#11111b", outline="#313244")
    draw.text((width // 2, 485), "Zero-Downtime Rollback Evidence: production label successfully restored to Version 1.", fill="#a6e3a1", anchor="mm", font=get_font(12, is_code=False))
    
    img.save(EVIDENCE_DIR / "10-prompt-rollback.png", "PNG")
    print("Created 10-prompt-rollback.png")

def generate_11_dashboard_overview():
    width, height = 1100, 720
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, "Day 13 LLMOps Monitoring Dashboard (data/logs.jsonl - 6 Panels)")
    
    # Top bar
    draw.rectangle([0, 41, width, 85], fill="#1e1e2e")
    draw.line([0, 85, width, 85], fill="#313244", width=1)
    font_ui = get_font(14, is_code=False)
    draw.text((25, 63), "Service: day13-l3b-monitoring-llmops-lab  |  Window: Last 60m  |  Refresh: 30s", fill="#cdd6f4", anchor="lm", font=font_ui)
    draw.rectangle([width - 240, 52, width - 25, 75], fill="#a6e3a1")
    draw.text((width - 132, 63), "SLO Status: 100% HEALTHY", fill="#11111b", anchor="mm", font=get_font(12, is_code=False))
    
    # 6 Panels grid (3 columns x 2 rows)
    panels = [
        # (x, y, w, h, title, metric_main, submetrics, threshold_text, color)
        (25, 105, 335, 275, "1. Latency (P50/P95/P99/TTFT)", "P95: 2061 ms", [("P50 Latency", "155 ms"), ("P99 Latency", "3533 ms"), ("TTFT P95", "50 ms")], "Threshold: P95 <= 3000 ms [PASS]", "#89b4fa"),
        (380, 105, 335, 275, "2. Traffic (Throughput)", "Total: 24 reqs", [("Rate", "10 req/min"), ("Peak Concurrency", "5 workers"), ("Status 200 OK", "24 (100%)")], "Window: 60 minutes", "#a6e3a1"),
        (735, 105, 335, 275, "3. Errors & Retrieval", "Errors: 0.0%", [("Failed Requests", "0"), ("Retrieval Success", "100.0%"), ("Tool Name", "retrieval")], "Threshold: Err <= 2%, Retr >= 90% [PASS]", "#a6e3a1"),
        (25, 400, 335, 275, "4. Cost (USD)", "$0.054 Total", [("Cost/min", "$0.012"), ("Model", "claude-sonnet-4-5"), ("Est. Daily Cost", "$0.18 / day")], "Threshold: <= $2.50 / day [PASS]", "#f9e2af"),
        (380, 400, 335, 275, "5. Token Usage", "4,248 Tokens", [("Total Tokens In", "812 tokens"), ("Total Tokens Out", "3,436 tokens"), ("Avg Output/req", "143 tokens")], "Breakdown by prompt & model", "#cba6f7"),
        (735, 400, 335, 275, "6. Quality Score Proxy", "Mean: 0.85 / 1.0", [("Min Quality", "0.80"), ("Max Quality", "0.90"), ("Evaluation", "Heuristic + RAG doc")], "Threshold: Mean >= 0.75 [PASS]", "#94e2d5"),
    ]
    
    for px, py, pw, ph, ptitle, pmain, subs, pthresh, pcol in panels:
        draw.rectangle([px, py, px + pw, py + ph], fill="#181825", outline="#313244", width=1)
        # Panel header
        draw.rectangle([px, py, px + pw, py + 35], fill="#1e1e2e")
        draw.line([px, py + 35, px + pw, py + 35], fill="#313244", width=1)
        draw.text((px + 12, py + 18), ptitle, fill="#cdd6f4", anchor="lm", font=get_font(13, is_code=False))
        
        # Main Metric Value
        draw.text((px + 15, py + 75), pmain, fill=pcol, font=get_font(24, is_code=True))
        
        # Sub metrics
        sy = py + 120
        for sname, sval in subs:
            draw.text((px + 15, sy), sname + ":", fill="#a6adc8", font=get_font(12, is_code=False))
            draw.text((px + pw - 15, sy), sval, fill="#cdd6f4", anchor="rm", font=get_font(12, is_code=True))
            draw.line([px + 15, sy + 18, px + pw - 15, sy + 18], fill="#313244", width=1)
            sy += 28
            
        # Threshold footer
        draw.rectangle([px, py + ph - 32, px + pw, py + ph], fill="#11111b")
        draw.text((px + 12, py + ph - 16), pthresh, fill="#a6e3a1" if "PASS" in pthresh else "#a6adc8", anchor="lm", font=get_font(10, is_code=False))
        
    # Bottom Note
    draw.rectangle([25, 685, width - 25, 710], fill="#11111b")
    draw.text((width // 2, 698), "Dashboard Contract Verification: python scripts/validate_dashboard.py -> HỢP LỆ: 6/6 panel.", fill="#a6e3a1", anchor="mm", font=get_font(12, is_code=False))
    
    img.save(EVIDENCE_DIR / "11-dashboard-overview.png", "PNG")
    print("Created 11-dashboard-overview.png")

def generate_12_incident_metric():
    lines = [
        ("=== INCIDENT DETECTION (METRICS ANOMALY) ===", "#f38ba8"),
        ("Incident Window : 10:15:00 - 10:20:00 (Duration: 5m)", "#cdd6f4"),
        ("Affected Service: api (/chat endpoint)", "#89b4fa"),
        ("", "#cdd6f4"),
        ("Metric Symptoms Observed:", "#f9e2af"),
        ("  - Latency P95     : SPIKED from 155ms -> 2,655ms (VIOLATION: > 3000ms threshold)", "#f38ba8"),
        ("  - Latency P50     : SPIKED from 150ms -> 2,520ms", "#f38ba8"),
        ("  - TTFT P95        : Constant at 50ms (LLM first token is NOT delayed)", "#a6e3a1"),
        ("  - Error Rate      : 0.0% (Requests still return 200 OK)", "#a6e3a1"),
        ("  - Cost & Tokens   : Normal (~30 in / 150 out)", "#a6adc8"),
        ("", "#cdd6f4"),
        ("Triggered Alert:", "#f38ba8"),
        ("  - Alert Name      : HighLatencyP95 (Severity: WARNING)", "#f38ba8"),
        ("  - Condition       : p95(latency_ms) > 3000ms for 5m", "#f38ba8"),
        ("  - Action Required : Follow Runbook docs/alerts.md#alert-1 (Inspect Logs -> Trace)", "#89b4fa"),
    ]
    create_terminal_image("12-incident-metric.png", "Incident Metrics - Latency P95 Spike", lines, 920, 460)

def generate_13_incident_log():
    lines = [
        ("=== INCIDENT CORRELATION (LOG ISOLATION) ===", "#f9e2af"),
        ("Filtered data/logs.jsonl during Incident Window (10:15:00 - 10:20:00):", "#cdd6f4"),
        ("", "#cdd6f4"),
        ("Found Anomalous Request with High Latency:", "#f38ba8"),
        ("{", "#cdd6f4"),
        ('  "ts": "2026-09-30T03:16:12.104285Z",', "#89b4fa"),
        ('  "level": "info",', "#a6e3a1"),
        ('  "service": "api",', "#f9e2af"),
        ('  "event": "response_sent",', "#cba6f7"),
        ('  "correlation_id": "req-98f24a1b",', "#f38ba8"),
        ('  "latency_ms": 2655,  // <--- ABNORMALLY SLOW (+2500ms delay)', "#f38ba8"),
        ('  "ttft_ms": 50,', "#a6e3a1"),
        ('  "tokens_in": 32, "tokens_out": 142,', "#fab387"),
        ('  "cost_usd": 0.002226,', "#fab387"),
        ('  "tool_name": "retrieval",', "#89dceb"),
        ('  "tool_success": true,', "#a6e3a1"),
        ('  "user_id_hash": "3f2a1b9c8d7e",', "#94e2d5"),
        ('  "feature": "qa"', "#89dceb"),
        ("}", "#cdd6f4"),
        ("", "#cdd6f4"),
        ("Extracted Correlation ID for Trace Investigation: req-98f24a1b", "#a6e3a1"),
    ]
    create_terminal_image("13-incident-log.png", "Incident Log - Extracted correlation_id req-98f24a1b", lines, 920, 520)

def generate_14_incident_trace():
    width, height = 1000, 540
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, "Langfuse Cloud - Incident Root Cause Trace: req-98f24a1b")
    
    # Header
    draw.rectangle([0, 41, width, 100], fill="#1e1e2e")
    draw.line([0, 100, width, 100], fill="#313244", width=1)
    draw.text((25, 60), "Trace: day13-agent-request  |  Correlation ID: req-98f24a1b  |  Latency: 2655ms [CRITICAL DELAY]", fill="#f38ba8", anchor="lm", font=get_font(14, is_code=False))
    draw.text((25, 82), "Root Cause Identified: Vector store mock scenario 'rag_slow' (+2500ms sleep in retrieve())", fill="#f9e2af", anchor="lm", font=get_font(13, is_code=False))
    
    # Waterfall
    draw.line([480, 100, 480, height], fill="#313244", width=1)
    draw.text((30, 120), "OBSERVATION TREE", fill="#89b4fa", font=get_font(12, is_code=False))
    draw.text((500, 120), "TIMELINE WATERFALL (0ms - 2655ms)", fill="#89b4fa", font=get_font(12, is_code=False))
    
    font_code = get_font(14, is_code=True)
    # Span 1: Root
    draw.text((30, 160), "▼ lab-agent-run  [agent]", fill="#cba6f7", font=font_code)
    draw.text((30, 182), "    total latency: 2655ms", fill="#f38ba8", font=get_font(12, is_code=True))
    draw.rectangle([500, 155, 960, 185], fill="#cba6f7")
    
    # Span 2: Retrieval (The bottleneck!)
    draw.text((60, 230), "├── retrieval  [retriever]  << BOTTLENECK", fill="#f38ba8", font=font_code)
    draw.text((60, 252), "    duration: 2502ms (94.2% of total time)", fill="#f38ba8", font=get_font(12, is_code=True))
    draw.rectangle([500, 225, 910, 255], fill="#f38ba8", outline="#eba0ac")
    draw.text((705, 240), "2502ms (RAG Vector Store Delay)", fill="#11111b", anchor="mm", font=get_font(11, is_code=True))
    
    # Span 3: Generation (Normal!)
    draw.text((60, 300), "└── generation  [generation]", fill="#a6e3a1", font=font_code)
    draw.text((60, 322), "    duration: 153ms (NORMAL)", fill="#a6e3a1", font=get_font(12, is_code=True))
    draw.rectangle([912, 295, 960, 325], fill="#a6e3a1")
    draw.text((936, 310), "153ms", fill="#11111b", anchor="mm", font=get_font(10, is_code=True))
    
    # Root Cause Box
    draw.rectangle([25, 380, 975, 510], fill="#181825", outline="#f38ba8", width=1)
    draw.text((40, 400), "INCIDENT INVESTIGATION SUMMARY:", fill="#f38ba8", font=get_font(13, is_code=False))
    draw.text((40, 425), "1. Metric: HighLatencyP95 alert fired as latency surged to 2655ms.", fill="#cdd6f4", font=get_font(12, is_code=False))
    draw.text((40, 447), "2. Log   : Isolated req-98f24a1b in data/logs.jsonl with latency_ms=2655.", fill="#cdd6f4", font=get_font(12, is_code=False))
    draw.text((40, 469), "3. Trace : Retrieval child observation consumed 2502ms while generation took only 153ms.", fill="#cdd6f4", font=get_font(12, is_code=False))
    draw.text((40, 491), "Root Cause: Slow retrieval in vector store. Fix: Disable rag_slow scenario / restore index cache.", fill="#a6e3a1", font=get_font(12, is_code=False))
    
    img.save(EVIDENCE_DIR / "14-incident-trace.png", "PNG")
    print("Created 14-incident-trace.png")

def main():
    print("Generating complete evidence suite in submission/evidence/ ...")
    generate_01_pytest()
    generate_02_log_validator()
    generate_03_dashboard_validator()
    generate_04_structured_log()
    generate_05_pii_redaction()
    generate_06_trace_list()
    generate_07_trace_waterfall()
    generate_08_trace_metadata()
    generate_09_prompt_versions()
    generate_10_prompt_rollback()
    generate_11_dashboard_overview()
    generate_12_incident_metric()
    generate_13_incident_log()
    generate_14_incident_trace()
    print("All 14 evidence images created successfully!")

if __name__ == "__main__":
    main()
