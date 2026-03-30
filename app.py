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
    fig.add_trace(go.Scatter(x=dates, y=values, mode='lines'))
    fig.update_layout(template="plotly_white", height=350)
    return pio.to_html(fig, full_html=False)

def comment(title):
    return f"{title}は現在の経済状況を示す重要な指標であり、金融政策や市場動向の影響を受けて変動すると一般的に考えられています。"

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
                <p style="font-size:14px;color:gray;">{comment(title)}</p>
                {graph}
            </div>
        </div>
        """

    return f"""
    <html>
    <head>

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

    <p>このサイトは経済データを分かりやすく解説する情報提供サイトです。</p>

    <button onclick="show('rate')">金利</button>
    <button onclick="show('cpi')">CPI</button>
    <button onclick="show('unemp')">失業率</button>
    <button onclick="show('sp')">S&P500</button>
    <button onclick="show('fx')">ドル円</button>
    <button onclick="show('nasdaq')">NASDAQ</button>
    <button onclick="show('policy')">ポリシー</button>
    <button onclick="show('contact')">お問い合わせ</button>

    {blocks}

    <div id="policy" class="box">
      <div class="card">
        <h2>プライバシーポリシー</h2>
        <p>本サイトは広告配信を行う可能性があります。Cookieを使用する場合があります。</p>
        <p>本サイトは投資助言を目的としておらず、最終判断はご自身でお願いします。</p>
      </div>
    </div>

    <div id="contact" class="box">
      <div class="card">
        <h2>お問い合わせ</h2>
        <form action="https://formspree.io/f/mlgojwnv" method="POST">
          <input type="text" name="name" placeholder="名前" required><br><br>
          <input type="email" name="email" placeholder="メール" required><br><br>
          <textarea name="message" placeholder="内容" required></textarea><br><br>
          <button type="submit">送信</button>
        </form>
      </div>
    </div>

    <footer style="font-size:12px;color:gray;margin:20px;">
    本サイトは一般情報提供であり投資助言ではありません。
    </footer>

    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
