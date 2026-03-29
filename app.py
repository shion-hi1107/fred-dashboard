from flask import Flask
import requests
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime
import os
import time

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

CACHE = {}
CACHE_TIME = 1800  # ★30分キャッシュ（高速化）

def get_data(series_id):
    now = time.time()
    if series_id in CACHE and now - CACHE[series_id]["time"] < CACHE_TIME:
        return CACHE[series_id]["data"]

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json"
    data = requests.get(url).json()

    CACHE[series_id] = {"data": data, "time": now}
    return data

def parse_data(obs):
    dates, values = [], []
    for item in obs:
        if item["value"] != ".":
            dates.append(datetime.strptime(item["date"], "%Y-%m-%d"))
            values.append(float(item["value"]))
    return dates, values

def create_plot(dates, values, title):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        line=dict(width=2)
    ))

    fig.update_layout(
        title=title,
        template="plotly_white",
        margin=dict(l=10, r=10, t=30, b=10),
        height=350
    )

    return pio.to_html(fig, full_html=False)

def generate_comment(title, values):
    if len(values) < 2:
        return "一般的な情報を表示しています。"

    change = values[-1] - values[-2]

    if change > 0:
        trend = "上昇傾向"
    elif change < 0:
        trend = "低下傾向"
    else:
        trend = "横ばい"

    return f"{title}は現在、{trend}で推移していると見られています。"

@app.route("/")
def index():

    datasets = {
        "rate": ("DGS10", "金利", "%"),
        "cpi": ("CPIAUCSL", "CPI", ""),
        "unemp": ("UNRATE", "失業率", "%"),
        "sp": ("SP500", "S&P500", ""),
        "fx": ("DEXJPUS", "ドル円", ""),
        "nasdaq": ("NASDAQCOM", "NASDAQ", "")
    }

    blocks = ""

    for key, (sid, title, unit) in datasets.items():
        obs = get_data(sid)["observations"][-200:]  # ★データ削減で高速化
        d, v = parse_data(obs)
        graph = create_plot(d, v, title)
        latest = obs[-1]["value"]
        comment = generate_comment(title, v)

        active = "active" if key == "rate" else ""

        blocks += f"""
        <div id="{key}" class="box {active}">
            <div class="card">
                <h2>{title}</h2>
                <div class="big">{latest} {unit}</div>
                <p style="font-size:14px;color:gray;">{comment}</p>
                {graph}
            </div>
        </div>
        """

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="300">

    <style>
    body {{ font-family: Arial; margin: 0; background: #f4f6f9; text-align: center; }}
    header {{ padding: 20px; font-size: 24px; font-weight: bold; }}
    button {{ padding: 10px 15px; margin: 5px; border-radius: 8px; border: none; background: #007bff; color: white; }}
    .box {{ display: none; }}
    .active {{ display: block; }}
    .card {{ background: white; margin: 20px auto; padding: 20px; border-radius: 12px; max-width: 700px; }}
    .big {{ font-size: 36px; font-weight: bold; margin: 10px; }}
    </style>

    <script>
    function show(id) {{
        let boxes = document.getElementsByClassName("box");
        for (let i = 0; i < boxes.length; i++) {{
            boxes[i].classList.remove("active");
        }}
        document.getElementById(id).classList.add("active");
    }}
    </script>

    </head>

    <body>

    <header>📊 Economic Dashboard</header>

    <button onclick="show('rate')">金利</button>
    <button onclick="show('cpi')">CPI</button>
    <button onclick="show('unemp')">失業率</button>
    <button onclick="show('sp')">S&P500</button>
    <button onclick="show('fx')">ドル円</button>
    <button onclick="show('nasdaq')">NASDAQ</button>

    {blocks}

    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
