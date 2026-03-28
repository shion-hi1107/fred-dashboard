from flask import Flask
import requests
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import os
import time

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

CACHE = {}
CACHE_TIME = 3600

def get_data(series_id):
    now = time.time()
    if series_id in CACHE and now - CACHE[series_id]["time"] < CACHE_TIME:
        return CACHE[series_id]["data"]

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json"
    data = requests.get(url).json()

    CACHE[series_id] = {"data": data, "time": now}
    return data

def create_graph(dates, values, title):
    plt.figure()
    plt.plot(dates, values)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()

def parse_data(observations):
    dates = []
    values = []
    for item in observations:
        if item["value"] != ".":
            dates.append(datetime.strptime(item["date"], "%Y-%m-%d"))
            values.append(float(item["value"]))
    return dates, values

@app.route("/")
def index():

    obs1 = get_data("DGS10")["observations"]
    d1, v1 = parse_data(obs1)
    g1 = create_graph(d1, v1, "Interest Rate")
    l1 = obs1[-1]

    obs2 = get_data("CPIAUCSL")["observations"]
    d2, v2 = parse_data(obs2)
    g2 = create_graph(d2, v2, "CPI")
    l2 = obs2[-1]

    obs3 = get_data("UNRATE")["observations"]
    d3, v3 = parse_data(obs3)
    g3 = create_graph(d3, v3, "Unemployment")
    l3 = obs3[-1]

    obs4 = get_data("SP500")["observations"]
    d4, v4 = parse_data(obs4)
    g4 = create_graph(d4, v4, "S&P500")
    l4 = obs4[-1]

    obs5 = get_data("DEXJPUS")["observations"]
    d5, v5 = parse_data(obs5)
    g5 = create_graph(d5, v5, "USD/JPY")
    l5 = obs5[-1]

    obs6 = get_data("NASDAQCOM")["observations"]
    d6, v6 = parse_data(obs6)
    g6 = create_graph(d6, v6, "NASDAQ")
    l6 = obs6[-1]

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
    body {{
        font-family: Arial;
        text-align: center;
        margin: 10px;
        background-color: white;
        color: black;
    }}

    .dark {{
        background-color: #121212;
        color: white;
    }}

    button {{
        padding: 10px;
        margin: 5px;
        font-size: 16px;
    }}

    .box {{ display: none; }}
    .active {{ display: block; }}

    img {{
        width: 100%;
        max-width: 500px;
    }}

    .big {{
        font-size: 30px;
        font-weight: bold;
    }}
    </style>

    <script>
    function show(id) {{
        var boxes = document.getElementsByClassName("box");
        for (var i = 0; i < boxes.length; i++) {{
            boxes[i].classList.remove("active");
        }}
        document.getElementById(id).classList.add("active");
    }}

    function toggleDark() {{
        document.body.classList.toggle("dark");
    }}
    </script>

    </head>

    <body>

    <h1>📊 Dashboard</h1>

    <button onclick="toggleDark()">🌙 ダークモード</button><br>

    <button onclick="show('rate')">金利</button>
    <button onclick="show('cpi')">CPI</button>
    <button onclick="show('unemp')">失業率</button>
    <button onclick="show('sp')">S&P500</button>
    <button onclick="show('fx')">ドル円</button>
    <button onclick="show('nasdaq')">NASDAQ</button>

    <div id="rate" class="box active">
        <h2>金利</h2>
        <div class="big">{l1["value"]} %</div>
        <img src="data:image/png;base64,{g1}">
    </div>

    <div id="cpi" class="box">
        <h2>CPI</h2>
        <div class="big">{l2["value"]}</div>
        <img src="data:image/png;base64,{g2}">
    </div>

    <div id="unemp" class="box">
        <h2>失業率</h2>
        <div class="big">{l3["value"]} %</div>
        <img src="data:image/png;base64,{g3}">
    </div>

    <div id="sp" class="box">
        <h2>S&P500</h2>
        <div class="big">{l4["value"]}</div>
        <img src="data:image/png;base64,{g4}">
    </div>

    <div id="fx" class="box">
        <h2>USD/JPY</h2>
        <div class="big">{l5["value"]}</div>
        <img src="data:image/png;base64,{g5}">
    </div>

    <div id="nasdaq" class="box">
        <h2>NASDAQ</h2>
        <div class="big">{l6["value"]}</div>
        <img src="data:image/png;base64,{g6}">
    </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
