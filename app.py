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
CACHE_TIME = 600

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
    fig.add_trace(go.Scatter(x=dates, y=values, mode='lines'))

    fig.update_layout(
        title=title,
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return pio.to_html(fig, full_html=False)

# 🔥 安全コメント生成（状況対応）
def generate_comment(title, values):
    if not values or len(values) < 2:
        return "データに基づく一般的な情報を表示しています。"

    latest = values[-1]
    prev = values[-2]

    try:
        latest = float(latest)
        prev = float(prev)
    except:
        return "市場データは様々な要因の影響を受けるとされています。"

    change = latest - prev

    if change > 0:
        trend = "上昇傾向"
    elif change < 0:
        trend = "低下傾向"
    else:
        trend = "横ばい"

    if title == "金利":
        return f"米国金利は現在、{trend}で推移していると見られており、金融政策やインフレ動向の影響が背景にある可能性があります。"

    elif title == "CPI":
        return f"CPIは{trend}の動きが見られ、物価動向を示す指標として注目されているとされています。"

    elif title == "失業率":
        return f"失業率は{trend}の傾向が見られ、労働市場の状況を反映していると考えられています。"

    elif title == "S&P500":
        return f"株式市場は{trend}で推移しており、金利や経済状況の影響を受けていると見られています。"

    elif title == "ドル円":
        return f"為替は{trend}の動きとなっており、金利差や経済状況の影響が考えられています。"

    elif title == "NASDAQ":
        return f"ハイテク株は{trend}の動きが見られ、金利動向の影響を受けやすいとされています。"

    return "市場は様々な要因により変動すると一般的に考えられています。"

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
        obs = get_data(sid)["observations"]
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
                <p style="font-size:14px; color:gray;">{comment}</p>
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
    body {{
        font-family: Arial;
        margin: 0;
        background: #f4f6f9;
        text-align: center;
    }}

    body.dark {{
        background: #121212;
        color: white;
    }}

    header {{
        padding: 20px;
        font-size: 24px;
        font-weight: bold;
    }}

    button {{
        padding: 10px 15px;
        margin: 5px;
        border-radius: 8px;
        border: none;
        background: #007bff;
        color: white;
        font-weight: bold;
    }}

    .box {{ display: none; }}
    .active {{ display: block; }}

    .card {{
        background: white;
        margin: 20px auto;
        padding: 20px;
        border-radius: 12px;
        max-width: 700px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    body.dark .card {{
        background: #1e1e1e;
    }}

    .big {{
        font-size: 36px;
        font-weight: bold;
        margin: 10px;
    }}

    footer {{
        font-size: 12px;
        color: gray;
        padding: 20px;
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

    <button onclick="toggleDark()">🌙</button><br>

    <button onclick="show('rate')">金利</button>
    <button onclick="show('cpi')">CPI</button>
    <button onclick="show('unemp')">失業率</button>
    <button onclick="show('sp')">S&P500</button>
    <button onclick="show('fx')">ドル円</button>
    <button onclick="show('nasdaq')">NASDAQ</button>

    {blocks}

    <footer>
    本サイトの情報は一般的な情報提供を目的としており、投資助言を行うものではありません。<br>
    金融商品に関する最終的な判断はご自身の責任でお願いします。
    </footer>

    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
