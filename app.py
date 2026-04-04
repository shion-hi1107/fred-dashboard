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

def create_plot(dates, values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=values, mode='lines'))
    fig.update_layout(template="plotly_white", height=350)
    return pio.to_html(fig, full_html=False)

def long_comment(title):
    return f"""
    {title}は経済の動きを把握する上で重要な指標の一つです。
    一般的に、この指標は中央銀行の政策や景気動向、インフレ率などの影響を受けて変動すると考えられています。
    例えば、金利が上昇する局面ではインフレ抑制の意図があると見られる一方で、株式市場には下押し圧力がかかる可能性があると指摘されています。
    また、このデータの変化は為替や企業活動にも影響を与える可能性があるため、多くの投資家や経済関係者が注視しているとされています。
    ただし、これらは一般的な見方であり、将来の動きを保証するものではありません。
    """

@app.route("/")
def index():

    datasets = {
        "金利": ("DGS10", "%"),
        "CPI": ("CPIAUCSL", ""),
        "失業率": ("UNRATE", "%"),
        "S&P500": ("SP500", ""),
        "ドル円": ("DEXJPUS", ""),
        "NASDAQ": ("NASDAQCOM", "")
    }

    content = ""

    for title, (sid, unit) in datasets.items():
        obs = get_data(sid)["observations"][-200:]
        d, v = parse_data(obs)
        graph = create_plot(d, v)
        latest = obs[-1]["value"]

        content += f"""
        <div class="card">
            <h2>{title}</h2>
            <div class="big">{latest} {unit}</div>
            <p>{long_comment(title)}</p>
            {graph}
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
    .big {{ font-size:28px; margin:10px; }}
    </style>

    </head>

    <body>

    <h1>📊 経済ダッシュボード</h1>

    <p>
    本サイトは、金利・物価・失業率・株価・為替などの経済指標を分かりやすく可視化し、
    一般的な情報提供を目的としたサイトです。
    各データは公的機関の情報をもとに表示しており、経済の流れを把握する参考情報として活用されることが想定されています。
    なお、本サイトは特定の投資判断を推奨するものではありません。
    </p>

    {content}

    <div class="card">
        <h2>まとめ</h2>
        <p>
        現在の経済環境は、インフレ動向や金融政策の影響を受けて変動していると一般的に見られています。
        各指標は相互に関連しており、一つのデータだけで判断するのではなく、全体的な流れとして把握することが重要とされています。
        今後の動きについては様々な見方があり、不確実性が高い状況が続く可能性があると考えられています。
        </p>
    </div>

    <div class="card">
        <h2>プライバシーポリシー</h2>
        <p>本サイトでは広告配信のためにCookieを使用する場合があります。</p>
        <p>本サイトは情報提供を目的としており、投資助言ではありません。</p>
    </div>

    <div class="card">
        <h2>お問い合わせ</h2>
        <form action="https://formspree.io/f/mlgojwnv" method="POST">
            <input type="text" name="name" placeholder="名前" required><br><br>
            <input type="email" name="email" placeholder="メール" required><br><br>
            <textarea name="message" placeholder="内容" required></textarea><br><br>
            <button type="submit">送信</button>
        </form>
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
