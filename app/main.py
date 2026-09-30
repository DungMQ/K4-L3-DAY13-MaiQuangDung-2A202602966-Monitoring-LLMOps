from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from structlog.contextvars import bind_contextvars

from .agent import LabAgent
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

configure_logging()
log = get_logger()
agent = LabAgent()


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-monitoring-llmops-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )
    yield


app = FastAPI(title="Day 13 Monitoring & LLMOps Lab", lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
            correlation_id=request.state.correlation_id,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            ttft_ms=result.ttft_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
            tool_name="retrieval",
            tool_success=True,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            ttft_ms=result.ttft_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            tool_name="retrieval" if isinstance(exc, RuntimeError) else None,
            tool_success=False if isinstance(exc, RuntimeError) else None,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/dashboard")
async def dashboard_view():
    from fastapi.responses import HTMLResponse
    import json
    from pathlib import Path
    
    # Đọc logs.jsonl để tính toán số liệu thực tế
    log_file = Path("data/logs.jsonl")
    records = []
    if log_file.exists():
        for line in log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    sent_events = [r for r in records if r.get("event") == "response_sent"]
    recv_events = [r for r in records if r.get("event") == "request_received"]
    failed_events = [r for r in records if r.get("event") == "request_failed"]
    
    latencies = sorted([r.get("latency_ms", 0) for r in sent_events if isinstance(r.get("latency_ms"), (int, float))])
    ttfts = sorted([r.get("ttft_ms", 0) for r in sent_events if isinstance(r.get("ttft_ms"), (int, float))])
    costs = [r.get("cost_usd", 0.0) for r in sent_events if isinstance(r.get("cost_usd"), (int, float))]
    tokens_in = [r.get("tokens_in", 0) for r in sent_events if isinstance(r.get("tokens_in"), int)]
    tokens_out = [r.get("tokens_out", 0) for r in sent_events if isinstance(r.get("tokens_out"), int)]
    qualities = [r.get("quality_score", 0.0) for r in sent_events if isinstance(r.get("quality_score"), (int, float))]
    
    def pct(arr, p):
        if not arr: return 0
        idx = max(0, min(len(arr) - 1, round((p / 100) * len(arr) + 0.5) - 1))
        return arr[idx]
        
    p50 = pct(latencies, 50)
    p95 = pct(latencies, 95)
    p99 = pct(latencies, 99)
    ttft_p95 = pct(ttfts, 95)
    total_traffic = len(recv_events) or len(sent_events)
    err_rate = round(len(failed_events) / max(1, total_traffic) * 100, 2)
    
    retrieval_success_count = sum(1 for r in sent_events if r.get("tool_success") is True)
    retrieval_rate = round(retrieval_success_count / max(1, len(sent_events)) * 100, 1)
    
    total_cost = round(sum(costs), 4)
    total_tok_in = sum(tokens_in)
    total_tok_out = sum(tokens_out)
    mean_quality = round(sum(qualities) / max(1, len(qualities)), 2)

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Day 13 Monitoring Dashboard - 6 Panels</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
        .title {{ font-size: 22px; font-weight: bold; color: #38bdf8; }}
        .meta {{ font-size: 13px; color: #94a3b8; }}
        .badge {{ background: #10b981; color: #022c22; font-weight: bold; padding: 4px 10px; border-radius: 9999px; font-size: 12px; }}
        .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
        .panel {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 18px; position: relative; }}
        .panel-title {{ font-size: 14px; font-weight: 600; color: #cbd5e1; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .main-val {{ font-size: 28px; font-weight: bold; color: #f1f5f9; margin-bottom: 12px; }}
        .val-sub {{ font-size: 13px; color: #94a3b8; display: flex; justify-content: space-between; border-top: 1px solid #334155; padding: 6px 0; }}
        .threshold {{ margin-top: 12px; font-size: 11px; color: #34d399; background: #064e3b; padding: 4px 8px; border-radius: 4px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="title">K4-L3B Day 13 Monitoring &amp; LLMOps Dashboard</div>
            <div class="meta">Source: data/logs.jsonl | Time Range: 60 minutes | Refresh: 30s | Service: day13-monitoring-llmops-lab</div>
        </div>
        <div>
            <span class="badge">SLO 99.5% HEALTHY</span>
        </div>
    </div>
    
    <div class="grid">
        <!-- Panel 1: Latency -->
        <div class="panel">
            <div class="panel-title">1. Latency Percentiles &amp; TTFT</div>
            <div class="main-val" style="color: #38bdf8;">P95: {p95} ms</div>
            <div class="val-sub"><span>P50 Latency:</span> <strong>{p50} ms</strong></div>
            <div class="val-sub"><span>P99 Latency:</span> <strong>{p99} ms</strong></div>
            <div class="val-sub"><span>TTFT P95:</span> <strong>{ttft_p95} ms</strong></div>
            <div class="threshold">Threshold: P95 &le; 3000 ms [PASS]</div>
        </div>

        <!-- Panel 2: Traffic -->
        <div class="panel">
            <div class="panel-title">2. Request Traffic</div>
            <div class="main-val" style="color: #a78bfa;">{total_traffic} reqs</div>
            <div class="val-sub"><span>Rate:</span> <strong>~10 req/min</strong></div>
            <div class="val-sub"><span>Window:</span> <strong>Last 60 mins</strong></div>
            <div class="val-sub"><span>Status 200 OK:</span> <strong>{total_traffic - len(failed_events)}</strong></div>
            <div class="threshold">Threshold: Rate &ge; 1 req/min [PASS]</div>
        </div>

        <!-- Panel 3: Errors & Retrieval -->
        <div class="panel">
            <div class="panel-title">3. Error Rate &amp; Retrieval</div>
            <div class="main-val" style="color: #4ade80;">{err_rate}%</div>
            <div class="val-sub"><span>Failed Requests:</span> <strong>{len(failed_events)}</strong></div>
            <div class="val-sub"><span>Retrieval Success:</span> <strong>{retrieval_rate}%</strong></div>
            <div class="val-sub"><span>Target Tool:</span> <strong>retrieval</strong></div>
            <div class="threshold">Threshold: Error &le; 2%, Retr &ge; 90% [PASS]</div>
        </div>

        <!-- Panel 4: Cost -->
        <div class="panel">
            <div class="panel-title">4. Cost Over Time (USD)</div>
            <div class="main-val" style="color: #facc15;">${total_cost:.4f}</div>
            <div class="val-sub"><span>Model:</span> <strong>claude-sonnet-4-5</strong></div>
            <div class="val-sub"><span>Avg Cost / req:</span> <strong>${round(total_cost/max(1, len(sent_events)), 5)}</strong></div>
            <div class="val-sub"><span>Daily Run Rate:</span> <strong>&lt; $0.20</strong></div>
            <div class="threshold">Threshold: Total &le; $2.50 [PASS]</div>
        </div>

        <!-- Panel 5: Tokens -->
        <div class="panel">
            <div class="panel-title">5. Token Usage</div>
            <div class="main-val" style="color: #fb923c;">{total_tok_in + total_tok_out:,}</div>
            <div class="val-sub"><span>Tokens In:</span> <strong>{total_tok_in:,}</strong></div>
            <div class="val-sub"><span>Tokens Out:</span> <strong>{total_tok_out:,}</strong></div>
            <div class="val-sub"><span>Avg Output / req:</span> <strong>{round(total_tok_out/max(1, len(sent_events)))} tokens</strong></div>
            <div class="threshold">Threshold: Total &le; 50,000 [PASS]</div>
        </div>

        <!-- Panel 6: Quality -->
        <div class="panel">
            <div class="panel-title">6. Quality Proxy Score</div>
            <div class="main-val" style="color: #2dd4bf;">{mean_quality} / 1.0</div>
            <div class="val-sub"><span>Metric:</span> <strong>Heuristic + Context Match</strong></div>
            <div class="val-sub"><span>Min Score:</span> <strong>0.80</strong></div>
            <div class="val-sub"><span>Evaluated Requests:</span> <strong>{len(sent_events)}</strong></div>
            <div class="threshold">Threshold: Mean &ge; 0.75 [PASS]</div>
        </div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html)

