# 既存コードはそのまま（省略せず全部貼るのが前提）
# ↓ 追加部分だけ理解すればOK

# --- HTML部分の下に追加（body内） ---

# ボタン追加（ナビ）
<button onclick="show('policy')">ポリシー</button>
<button onclick="show('contact')">お問い合わせ</button>

# --- ポリシーページ ---
<div id="policy" class="box">
  <div class="card">
    <h2>プライバシーポリシー</h2>
    <p>
    本サイトではアクセス解析および広告配信のためにCookieを使用する場合があります。<br>
    個人を特定する情報は収集していません。<br><br>

    本サイトは第三者配信の広告サービス（Google AdSense）を利用する場合があります。<br>
    広告配信事業者はユーザーの興味に応じた広告を表示することがあります。<br>
    </p>
  </div>
</div>

# --- お問い合わせページ ---
<div id="contact" class="box">
  <div class="card">
    <h2>お問い合わせ</h2>

    <form onsubmit="alert('送信ありがとうございました（デモ）'); return false;">
      <input type="text" placeholder="お名前" style="width:80%;padding:10px;margin:5px;"><br>
      <input type="email" placeholder="メールアドレス" style="width:80%;padding:10px;margin:5px;"><br>
      <textarea placeholder="お問い合わせ内容" style="width:80%;height:100px;padding:10px;margin:5px;"></textarea><br>
      <button type="submit">送信</button>
    </form>

    <p style="font-size:12px;color:gray;">
    ※現在このフォームは簡易版です。返信は行っていません。
    </p>
  </div>
</div>
