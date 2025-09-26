from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from ..core.logging import configure_logging
from ..exec.order_interface import get_positions
from ..monitor import monitor

app = FastAPI(title="LeekBot API")
state: Dict[str, str] = {"mode": "stopped"}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <title>LeekBot Live Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #111; color: #eee; }
        header { padding: 1rem 2rem; background: #1f1f1f; box-shadow: 0 2px 4px rgba(0,0,0,0.6); }
        h1 { margin: 0; font-size: 1.8rem; }
        #status { margin-top: 0.5rem; font-size: 0.9rem; color: #7bd88f; }
        main { padding: 1.5rem 2rem; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 0.5rem; border-bottom: 1px solid #333; text-align: left; }
        th { background: #222; }
        tr:nth-child(even) { background: #1a1a1a; }
        .payload { font-family: "Courier New", monospace; font-size: 0.85rem; }
    </style>
</head>
<body>
    <header>
        <h1>LeekBot Live Monitor</h1>
        <div id=\"status\">Connecting…</div>
    </header>
    <main>
        <p>Streaming live orders, fills, and risk events emitted by the trading engine.</p>
        <table id=\"events\">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Timestamp</th>
                    <th>Category</th>
                    <th>Payload</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </main>
    <script>
        const statusEl = document.getElementById('status');
        const tbody = document.querySelector('#events tbody');

        function prependRow(event) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${event.id}</td>
                <td>${new Date(event.timestamp).toLocaleString()}</td>
                <td>${event.category}</td>
                <td class=\"payload\">${JSON.stringify(event.payload)}</td>`;
            if (tbody.firstChild) {
                tbody.insertBefore(row, tbody.firstChild);
            } else {
                tbody.appendChild(row);
            }
        }

        fetch('/monitor/events').then(resp => resp.json()).then(data => {
            data.events.forEach(prependRow);
        });

        const source = new EventSource('/monitor/stream');
        source.onopen = () => {
            statusEl.textContent = 'Connected';
            statusEl.style.color = '#7bd88f';
        };
        source.onerror = () => {
            statusEl.textContent = 'Connection lost - retrying…';
            statusEl.style.color = '#f9c74f';
        };
        source.onmessage = (msg) => {
            try {
                const event = JSON.parse(msg.data);
                prependRow(event);
            } catch (err) {
                console.error('Failed to parse event', err);
            }
        };
    </script>
</body>
</html>
"""


@app.on_event("startup")
async def startup() -> None:
    configure_logging("./logs")


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return DASHBOARD_HTML


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/status")
async def status() -> Dict[str, str]:
    return state


@app.post("/run")
async def run(mode: str) -> Dict[str, str]:
    state["mode"] = mode
    monitor.record_event("lifecycle", {"mode": mode})
    return state


@app.post("/stop")
async def stop() -> Dict[str, str]:
    state["mode"] = "stopped"
    monitor.record_event("lifecycle", {"mode": "stopped"})
    return state


@app.get("/accounts")
async def accounts() -> Dict[str, str]:
    return {"accounts": list(state.keys())}


@app.get("/positions")
async def positions(account: str, venue: str) -> Dict:
    return {"positions": get_positions(account, venue)}


@app.get("/logs/today")
async def logs() -> Dict[str, str]:
    path = Path("./logs/leekbot.log")
    return {"log": path.read_text() if path.exists() else ""}


@app.get("/monitor/events")
async def monitor_events() -> Dict[str, list[Dict[str, object]]]:
    events = [event.to_dict() for event in monitor.snapshot()]
    return {"events": events}


@app.get("/monitor/stream")
async def monitor_stream(request: Request) -> StreamingResponse:
    try:
        last_event_id = int(request.headers.get("last-event-id", "0"))
    except ValueError:
        last_event_id = 0

    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in monitor.stream(after_id=last_event_id):
            payload = json.dumps(event.to_dict())
            yield f"id: {event.id}\ndata: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
