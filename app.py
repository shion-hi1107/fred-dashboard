import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from flask import Flask
import requests

app = Flask(__name__)

# ===== グラフ作成 =====
def create_graph(data):
    dates = []
    values = []

    for item in data["observations"]:
        if item["value"] != ".":
            dates.append(datetime.strptime(item["date"], "%Y-%m-%d"))
            values.append(float(item["value"]))

    plt.figure()
    plt.plot(dates, values)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return base64.b64encode(buf.getvalue()).decode()


@app.route("/")
def index():

    API_KEY = "f507319255f52e56be8f36a80a366db4"

    # ===== データ取得 =====
    def get_data(series_id):
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json"
        return requests.get(url).json()

    rate_data = get_data("DGS10")
    cpi_data = get_data("CPIAUCSL")
    unemp_data = get_data("UNRATE")

    # ===== 最新値 =====
    rate_latest = rate_data["observations"][-1]["value"]
    cpi_latest = cpi_data["observations"][-1]["value"]
    unemp_latest = unemp_data["observations"][-1]["value"]

    # ===== グラフ =====
    rate_graph = create_graph(rate_data)
    cpi_graph = create_graph(cpi_data)
    unemp_graph = create_graph(unemp_data)

    return f"""
<html>
<head>
    <title>経済ダッシュボード</title>
    <style>
        body {{
            font-family: Arial;
            background-color: #f5f5f5;
            text-align: center;
        }}

        .buttons {{
            margin: 20px;
        }}

        button {{
            padding: 10px 20px;
            margin: 5px;
            font-size: 16px;
            cursor: pointer;
        }}

        .card {{
            background: white;
            padding: 20px;
            margin: auto;
            width: 600px;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}

        .value {{
            font-size: 40px;
            font-weight: bold;
        }}

        img {{
            width: 100%;
        }}
    </style>

    <script>
        function show(type) {{
            document.getElementById("rate").style.display = "none";
            document.getElementById("cpi").style.display = "none";
            document.getElementById("unemp").style.display = "none";

            document.getElementById(type).style.display = "block";
        }}
    </script>
</head>

<body>

<h1>📊 経済ダッシュボード</h1>

<div class="buttons">
    <button onclick="show('rate')">📈 金利</button>
    <button onclick="show('cpi')">💰 CPI</button>
    <button onclick="show('unemp')">👥 失業率</button>
</div>

<div id="rate" class="card">
    <h2>📈 金利</h2>
    <div class="value">{rate_latest} %</div>
    <img src="data:image/png;base64,{rate_graph}">
</div>

<div id="cpi" class="card" style="display:none;">
    <h2>💰 インフレ（CPI）</h2>
    <div class="value">{cpi_latest}</div>
    <img src="data:image/png;base64,{cpi_graph}">
</div>

<div id="unemp" class="card" style="display:none;">
    <h2>👥 失業率</h2>
    <div class="value">{unemp_latest} %</div>
    <img src="data:image/png;base64,{unemp_graph}">
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