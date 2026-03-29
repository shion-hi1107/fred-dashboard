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
CACHE_TIME = 1800

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
    fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', line=dict(width=2)))
    fig.update_layout(template="plotly_white", height=350)
    return pio.to_html(fig, full_html=False)

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
        obs = get_data(sid)["observations"][-200:]
        d, v = parse_data(obs)
        graph = create_plot(d, v, title)
        latest = obs[-1]["value"]

        active = "active" if key == "rate" else ""

        blocks += f"""
        <div id="{key}" class="box {active}">
            <div class="card">
                <h2>{title}</h2>
                <div class="big">{latest} {unit}</div>
                {graph}
            </div>
        </div>
        """

    return f"""
    <html>
    <head>

    <!-- AdSenseコード（あなた専用） -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6188755905265058"
    crossorigin="anonymous"></script>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
    body {{ font-family: Arial; text-align:center; background:#f4f6f9; }}
    .card {{ background:white; margin:20px auto; padding:20px; max-width:700px; border-radius:10px; }}
    .box {{ display:none; }}
    .active {{ display:block; }}
    button {{ padding:10px; margin:5px; }}
    </style>

    <script>
    function show(id) {{
        let boxes = document.getElementsByClassName("box");
        for (let i=0;i<boxes.length;i++) boxes[i].classList.remove("active");
        document.getElementById(id).classList.add("active");
    }}
    </script>

    </head>

    <body>

    <h1>📊 Economic Dashboard</h1>

    <p>このサイトは、経済指標や市場データを分かりやすく可視化し、一般的な情報提供を目的としています。</p>

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
