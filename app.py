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

# キャッシュ（1時間）
CACHE = {}
CACHE_TIME = 3600

def get_data(series_id):
    now = time.time()

    if series_id in CACHE and now - CACHE[series_id]["time"] < CACHE_TIME:
        return CACHE[series_id]["data"]

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json"
    response = requests.get(url)
    data = response.json()

    CACHE[series_id] = {
        "data": data,
        "time": now
    }

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

@app.route("/")
def index():

    # 金利
    data1 = get_data("DGS10")
    obs1 = data1["observations"]

    dates1 = []
    values1 = []

    for item in obs1:
        if item["value"] != ".":
            dates1.append(datetime.strptime(item["date"], "%Y-%m-%d"))
            values1.append(float(item["value"]))

    graph1 = create_graph(dates1, values1, "Interest Rate")
    latest1 = obs1[-1]

    # CPI
    data2 = get_data("CPIAUCSL")
    obs2 = data2["observations"]

    dates2 = []
    values2 = []

    for item in obs2:
        if item["value"] != ".":
            dates2.append(datetime.strptime(item["date"], "%Y-%m-%d"))
            values2.append(float(item["value"]))

    graph2 = create_graph(dates2, values2, "CPI")
    latest2 = obs2[-1]

    # 失業率
    data3 = get_data("UNRATE")
    obs3 = data3["observations"]

    dates3 = []
    values3 = []

    for item in obs3:
        if item["value"] != ".":
            dates3.append(datetime.strptime(item["date"], "%Y-%m-%d"))
            values3.append(float(item["value"]))

    graph3 = create_graph(dates3, values3, "Unemployment Rate")
    latest3 = obs3[-1]

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {{
        font-family: Arial;
        text-align: center;
        margin: 10px;
    }}
    .box {{
        border: 1px solid #ccc;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 10px;
    }}
    .big {{
        font-size: 30px;
        font-weight: bold;
    }}
    img {{
        width: 100%;
        max-width: 500px;
    }}
    </style>
    </head>

    <body>

    <h1>📊 Economic Dashboard</h1>

    <div class="box">
        <h2>Interest Rate</h2>
        <div class="big">{latest1["value"]} %</div>
        <p>{latest1["date"]}</p>
        <img src="data:image/png;base64,{graph1}">
    </div>

    <div class="box">
        <h2>CPI</h2>
        <div class="big">{latest2["value"]}</div>
        <p>{latest2["date"]}</p>
        <img src="data:image/png;base64,{graph2}">
    </div>

    <div class="box">
        <h2>Unemployment Rate</h2>
        <div class="big">{latest3["value"]} %</div>
        <p>{latest3["date"]}</p>
        <img src="data:image/png;base64,{graph3}">
    </div>

    <hr>
    <p style='font-size:12px;'>
    This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.
    </p>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
