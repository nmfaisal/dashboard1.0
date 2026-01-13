from pathlib import Path
import pandas as pd
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import threading
import webbrowser
import sys

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

TRACE_LOG = BASE_DIR / "srv" / "data" / "trace_log.csv"

# 🔴 THIS MUST RUN BEFORE to_csv
TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)

COLUMN_LABELS = {
    "item_id": "Work Order No",
    "location": "Location",
    "status": "Quantity",
    "timestamp": "Scan Time",
    "model": "Model/Part No",
    "substance": "Raw Mtrl Substanstance",
}

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
        html.Div(id="item-detail-view"),

    ],
)

@app.callback(
    Output("trace-table", "data"),
    Output("trace-table", "columns"),
    Output("current-status", "children"),
    Output("item-detail-view", "children"),
    Input("refresh", "n_intervals"),
    Input("search-item", "value"),
)
def update_table(_, item_id):
    if not TRACE_LOG.exists():
        return [], [], "No trace data yet.", ""

    df = pd.read_csv(TRACE_LOG)

    # ======================
    # EXISTING FILTER LOGIC
    # ======================
    if item_id:
        df_filtered = df[df["item_id"] == item_id]
    else:
        df_filtered = df

    columns = [
        {"name": COLUMN_LABELS.get(c, c), "id": c}
        for c in df.columns
    ]

    status = "No item selected"
    if not df_filtered.empty:
        last = df_filtered.iloc[-1]
        status = html.B(
            f"Last seen: {last['item_id']} | Location: {last['location']} | Time: {last['timestamp']}"
        )

    # ======================
    # NEW: DETAIL VIEW
    # ======================
    detail_view = ""

    if item_id and not df_filtered.empty:
        df_sorted = df_filtered.sort_values("timestamp")

        cards = []
        for _, row in df_sorted.iterrows():
            cards.append(
                html.Div(
                    style={
                        "border": "1px solid #ccc",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "marginBottom": "10px",
                        "backgroundColor": "#f9f9f9",
                    },
                    children=[
                        html.Div([
                            html.B("Location: "),
                            row["location"]
                        ]),
                        html.Div([
                            html.B("Quantity: "),
                            row["status"]
                        ]),
                        html.Small(f"Time: {row['timestamp']}"),
                    ],
                )
            )

        detail_view = html.Div(
            children=[
                html.H3(f"Item ID: {item_id}"),
                html.Div(cards),
            ]
        )

    return (
        df_filtered.to_dict("records"),
        columns,
        status,
        detail_view,
    )


def open_browser():
    webbrowser.open_new("http://localhost:8050")


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=8050, debug=False)
