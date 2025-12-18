import pandas as pd
from dash import Dash, html, dash_table
from pathlib import Path

CSV_PATH = Path("/home/nad/dashboard1.0/srv/data/sales.csv")

  # your real server path


app = Dash(__name__)

if not CSV_PATH.exists():
    raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("CSV Dashboard"),

        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in df.columns],
            page_size=15,
            style_table={"overflowX": "auto"},
        ),
    ],
)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8050,
        debug=True,
    )
