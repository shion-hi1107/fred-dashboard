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
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()

def parse_data(obs):
    dates, values = [], []
    for item in obs:
        if item["value"] != ".":
            dates.append(datetime.strptime(item["date"], "%Y-%m-%d"))
            values.append(float(item["value"]))
    return dates, values

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

    graphs = {}

    for key, (sid, title, unit) in datasets.items():
        obs = get_data(sid)["observations"]
        d, v = parse_data(obs)
        g = create_graph(d, v, title)
        latest = obs[-1]["value"]
        graphs[key] = (g, latest, title, unit)

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
    body {{
        font-family: Arial;
        text-align: center;
        margin: 0;
        background: white;
        color: black;
    }}

    body.dark {{
        background: #121212;
        color: white;
    }}

    header {{
        padding: 15px;
        font-size: 24px;
        font-weight: bold;
    }}

    .controls {{
        margin: 10px;
    }}

    button {{
        padding: 10px 15px;
        margin: 5px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        background: #007bff;
        color: white;
        font-weight: bold;
    }}

    button:hover {{
        opacity: 0.8;
    }}

    .box {{
        display: none;
        padding: 10px;
    }}

    .active {{
        display: block;
    }}

    img {{
        width: 100%;
        max-width: 500px;
    }}

    .big {{
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }}
    </style>

    <script>
    function show(id) {{
        let boxes = document.getElementsByClassName("box");
        for (let i = 0; i < boxes.length; i++) {{
            boxes[i].classList.remove("active");
        }}
        document.getElementById(id).classList.add("active");
    }}

    function toggleDark() {{
        document.body.classList.toggle("dark");
        localStorage.setItem("dark", document.body.classList.contains("dark"));
    }}

    window.onload = function() {{
        if(localStorage.getItem("dark") === "true") {{
            document.body.classList.add("dark");
        }}
    }}
    </script>

    </head>

    <body>

    <header>📊 Economic Dashboard</header>

    <div class="controls">
        <button onclick="toggleDark()">🌙</button>
        <button onclick="show('rate')">金利</button>
        <button onclick="show('cpi')">CPI</button>
        <button onclick="show('unemp')">失業率</button>
        <button onclick="show('sp')">S&P500</button>
        <button onclick="show('fx')">ドル円</button>
        <button onclick="show('nasdaq')">NASDAQ</button>
    </div>

    {''.join([
        f'''
        <div id="{k}" class="box {'active' if k=='rate' else ''}">
            <h2>{v[2]}</h2>
            <div class="big">{v[1]} {v[3]}</div>
            <img src="data:image/png;base64,{v[0]}">
        </div>
        ''' for k, v in graphs.items()
    ])}

    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
