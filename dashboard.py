from pathlib import Path
import pandas as pd
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import threading
import webbrowser
import sys
from pathlib import Path

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

TRACE_LOG = BASE_DIR / "srv" / "data" / "trace_log.csv"

# 🔴 THIS MUST RUN BEFORE to_csv
TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)

app = Dash(__name__)

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("📦 Process Tracing Dashboard"),

        dcc.Input(
            id="search-item",
            type="text",
            placeholder="Scan / Enter Item ID",
            style={"width": "300px"},
        ),

        html.Br(), html.Br(),

        dcc.Interval(id="refresh", interval=3000, n_intervals=0),

        html.Div(id="current-status"),
        html.Br(),

        dash_table.DataTable(
            id="trace-table",
            page_size=10,
            style_table={"overflowX": "auto"},
        ),
    ],
)

@app.callback(
    Output("trace-table", "data"),
    Output("trace-table", "columns"),
    Output("current-status", "children"),
    Input("refresh", "n_intervals"),
    Input("search-item", "value"),
)
def update_table(_, item_id):
    if not TRACE_LOG.exists():
        return [], [], "No trace data yet."

    df = pd.read_csv(TRACE_LOG)

    if item_id:
        df = df[df["item_id"] == item_id]

    columns = [{"name": c, "id": c} for c in df.columns]

    status = "No item selected"
    if not df.empty:
        last = df.iloc[-1]
        status = html.B(
            f"Last seen: {last['location']} | Status: {last['status']} | Time: {last['timestamp']}"
        )

    return df.to_dict("records"), columns, status

def open_browser():
    webbrowser.open_new("http://localhost:8050")


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=8050, debug=False)
