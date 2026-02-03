import sys
import threading
import webbrowser
from pathlib import Path

import pandas as pd
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output

# ==================================================
# EXE-SAFE BASE DIRECTORY
# ==================================================
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()

TRACE_LOG = BASE_DIR / "srv" / "data" / "trace_log.csv"
TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)

# ==================================================
# COLUMN DISPLAY LABELS (UI ONLY)
# ==================================================
COLUMN_LABELS = {
    "timestamp": "Scan Time",
    "item_id": "Work Order No",
    "location": "Location",
    "status": "Quantity",
    "model": "Model",
    "substance": "Substance",
}

LOCATIONS = ["Office", "Incoming", "QC", "FG", "Shipment"]

# ==================================================
# DASH APP
# ==================================================
app = Dash(__name__)

app.layout = html.Div(
    style={"padding": "20px", "fontFamily": "Arial"},
    children=[

        html.H1("📦 Process Tracing Dashboard"),

        # # ----------------------
        # # FILTER INPUTS
        # # ----------------------
        # dcc.Input(
        #     id="search-item",
        #     type="text",
        #     placeholder="Scan / Enter Item ID",
        #     style={"width": "300px", "fontSize": "16px"},
        # ),

        # html.Br(), html.Br(),

        # dcc.Input(
        #     id="search-model",
        #     type="text",
        #     placeholder="Enter Model (optional)",
        #     style={"width": "300px", "fontSize": "16px"},
        # ),

        # html.Br(), html.Br(),

        # html.Div([
        #     html.Label("Start Date"),
        #     dcc.DatePickerSingle(
        #         id="start-date",
        #         display_format="YYYY-MM-DD",
        #     ),
        #         ], style={"marginBottom": "10px"}),

        # html.Div([
        #     html.Label("End Date"),
        #     dcc.DatePickerSingle(
        #         id="end-date",
        #         display_format="YYYY-MM-DD",
        #     ),
        #         ], style={"marginBottom": "20px"}),
        # ----------------------
        # FILTER INPUTS ROW 1
        # ----------------------
        html.Div(
            style={"display": "flex", "gap": "20px", "alignItems": "center"},
            children=[
                dcc.Input(
                    id="search-item",
                    type="text",
                    placeholder="Scan / Enter Item ID",
                    style={"width": "250px", "fontSize": "16px"},
                ),
                dcc.DatePickerSingle(
                    id="start-date",
                    placeholder="Start Date",
                    display_format="DD-MM-YYYY",
                ),
            ],
        ),

        html.Br(),

        # ----------------------
        # FILTER INPUTS ROW 2
        # ----------------------
        html.Div(
            style={"display": "flex", "gap": "20px", "alignItems": "center"},
            children=[
                dcc.Input(
                    id="search-model",
                    type="text",
                    placeholder="Enter Model (optional)",
                    style={"width": "250px", "fontSize": "16px"},
                ),
                dcc.DatePickerSingle(
                    id="end-date",
                    placeholder="End Date",
                    display_format="DD-MM-YYYY",
                ),
            ],
        ),



        dcc.Interval(id="refresh", interval=3000, n_intervals=0),

        html.Div(id="current-status"),
        html.Br(),

        # ----------------------
        # SUMMARY VIEW
        # ----------------------
        html.Div(id="item-summary"),
        html.Br(),

        # ----------------------
        # DETAIL VIEW
        # ----------------------
        html.Div(id="item-detail-view"),
        html.Br(),

        # ----------------------
        # TABLE VIEW
        # ----------------------
        dash_table.DataTable(
            id="trace-table",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
        ),
    ],
)

# ==================================================
# CALLBACK
# ==================================================
@app.callback(
    Output("trace-table", "data"),
    Output("trace-table", "columns"),
    Output("current-status", "children"),
    Output("item-detail-view", "children"),
    Output("item-summary", "children"),
    Input("refresh", "n_intervals"),
    Input("search-item", "value"),
    Input("search-model", "value"),
    Input("start-date", "date"),
    Input("end-date", "date"),
)
def update_table(_, item_id, selected_model, start_date, end_date):


    if not TRACE_LOG.exists():
        return [], [], "No trace data yet.", "", ""

    df = pd.read_csv(TRACE_LOG)
    # df = pd.read_csv(TRACE_LOG)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Apply date filter if selected
    if start_date:
        df = df[df["timestamp"] >= pd.to_datetime(start_date)]

    if end_date:
        df = df[df["timestamp"] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]

    # Ensure quantity is numeric
    df["status"] = pd.to_numeric(df["status"], errors="coerce").fillna(0)

    # ==================================================
    # FILTER PRIORITY
    # Item ID > Model > All
    # ==================================================
    if item_id:
        df_filtered = df[df["item_id"] == item_id]
    elif selected_model:
        df_filtered = df[df["model"] == selected_model]
    else:
        df_filtered = df

    # ==================================================
    # TABLE
    # ==================================================
    columns = [{"name": COLUMN_LABELS.get(c, c), "id": c} for c in df.columns]

    # ==================================================
    # CURRENT STATUS
    # ==================================================
    status_view = "No item selected"
    if not df_filtered.empty:
        last = df_filtered.sort_values("timestamp").iloc[-1]
        status_view = html.B(
            f"Last seen → {last['location']} | Qty: {int(last['status'])} | Time: {last['timestamp']}"
        )

    # ==================================================
    # DETAIL TIMELINE (ONLY FOR ITEM)
    # ==================================================
    detail_view = ""
    if item_id and not df_filtered.empty:
        cards = []
        for _, row in df_filtered.sort_values("timestamp").iterrows():
            cards.append(
                html.Div(
                    style={
                        "border": "1px solid #ccc",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "marginBottom": "8px",
                        "backgroundColor": "#f9f9f9",
                    },
                    children=[
                        html.Div([html.B("Location: "), row["location"]]),
                        html.Div([html.B("Quantity: "), int(row["status"])]),
                        html.Small(f"Time: {row['timestamp']}"),
                    ],
                )
            )

        detail_view = html.Div(
            children=[
                html.H3(f"Timeline — Item ID: {item_id}"),
                html.Div(cards),
            ]
        )

    # ==================================================
    # SUMMARY VIEW
    # ==================================================
    summary_view = ""

    # ----------------------
    # ITEM SUMMARY
    # ----------------------
    if item_id and not df_filtered.empty:

        office_rows = df_filtered[df_filtered["location"] == "Office"]
        model = office_rows.iloc[-1]["model"] if not office_rows.empty else "-"

        qty_by_location = {
            loc: int(df_filtered[df_filtered["location"] == loc]["status"].sum())
            for loc in LOCATIONS
        }

        summary_view = html.Div(
            style={
                "border": "2px solid #2e86de",
                "borderRadius": "10px",
                "padding": "14px",
                "backgroundColor": "#eef4ff",
            },
            children=[
                html.H3("📊 Status Summary"),
                html.Div([
                    html.B("Model: "), model,
                    html.Span(" | "),
                    html.B("Item ID: "), item_id,
                ]),
                html.Br(),
                html.Table(
                    style={"width": "100%", "textAlign": "center"},
                    children=[
                        html.Thead(
                            html.Tr(
                                [html.Th("Location")] +
                                [html.Th(loc) for loc in LOCATIONS]
                            )
                        ),
                        html.Tbody(
                            html.Tr(
                                [html.Td("Quantity")] +
                                [
                                    html.Td(qty_by_location[loc] if qty_by_location[loc] > 0 else "-")
                                    for loc in LOCATIONS
                                ]
                            )
                        ),
                    ],
                ),
            ],
        )

    # ----------------------
    # MODEL SUMMARY
    # ----------------------
    elif selected_model and not df_filtered.empty:

        blocks = []

        # =========================
        # OVERALL MODEL TOTALS
        # =========================
        overall_qty = {
            loc: int(df_filtered[df_filtered["location"] == loc]["status"].sum())
            for loc in LOCATIONS
        }

        overall_block = html.Div(
            style={
                "border": "3px solid #2e86de",
                "borderRadius": "12px",
                "padding": "16px",
                "marginBottom": "20px",
                "backgroundColor": "#e8f0ff",
            },
            children=[
                html.H3("📦 Model Overall Totals"),
                html.Div([
                    html.B("Model: "), selected_model,
                ]),
                html.Br(),
                html.Table(
                    style={"width": "100%", "textAlign": "center"},
                    children=[
                        html.Thead(
                            html.Tr(
                                [html.Th("Location")] +
                                [html.Th(loc) for loc in LOCATIONS]
                            )
                        ),
                        html.Tbody(
                            html.Tr(
                                [html.Td("Total Qty")] +
                                [
                                    html.Td(overall_qty[loc] if overall_qty[loc] > 0 else "-")
                                    for loc in LOCATIONS
                                ]
                            )
                        ),
                    ],
                ),
            ],
        )


        for item, df_item in df_filtered.groupby("item_id"):
            qty_by_location = {
                loc: int(df_item[df_item["location"] == loc]["status"].sum())
                for loc in LOCATIONS
            }

            blocks.append(
                html.Div(
                    style={
                        "border": "2px solid #aaa",
                        "borderRadius": "10px",
                        "padding": "14px",
                        "marginBottom": "12px",
                        "backgroundColor": "#f9f9f9",
                    },
                    children=[
                        html.Div([
                            html.B("Model: "), selected_model,
                            html.Span(" | "),
                            html.B("Item ID: "), item,
                        ]),
                        html.Br(),
                        html.Table(
                            style={"width": "100%", "textAlign": "center"},
                            children=[
                                html.Thead(
                                    html.Tr(
                                        [html.Th("Location")] +
                                        [html.Th(loc) for loc in LOCATIONS]
                                    )
                                ),
                                html.Tbody(
                                    html.Tr(
                                        [html.Td("Quantity")] +
                                        [
                                            html.Td(qty_by_location[loc] if qty_by_location[loc] > 0 else "-")
                                            for loc in LOCATIONS
                                        ]
                                    )
                                ),
                            ],
                        ),
                    ],
                )
            )

        summary_view = html.Div(
            children=[
                html.H3("📊 Status Summary"),
                overall_block,   # 👈 NEW overall totals first
                *blocks          # existing per-item blocks
            ]
        )


    return (
        df_filtered.to_dict("records"),
        columns,
        status_view,
        detail_view,
        summary_view,
    )

# ==================================================
# AUTO OPEN BROWSER
# ==================================================
def open_browser():
    webbrowser.open_new("http://localhost:8050")

# ==================================================
# START SERVER
# ==================================================
if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=8050, debug=False)
