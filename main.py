from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BOT_TOKEN = "8485547227:AAEnNbuM5Ongt_PSIT9tH4-z8cAOBDYDg7k"
CHAT_IDS = ["2053231295"]  # bisa ditambah kalau mau kirim ke beberapa user
URL = "https://blog.indodax.com/"

last_article = None

@app.route("/run")
def check_articles():
    global last_article
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("h2", class_="post-title").find("a")
        title = article.text.strip()
        link = article["href"]

        if last_article != link:
            last_article = link
            for chat_id in CHAT_IDS:
                message = f"🆕 Artikel baru di Indodax Blog!\n\n{title}\n{link}"
                requests.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    params={"chat_id": chat_id, "text": message}
                )
            print(f"✅ Notified: {title}")
        else:
            print("No new article found.")

        return "✅ Checked Indodax Blog!"

    except Exception as e:
        print("Error:", e)
        return f"❌ Error: {e}"

@app.route("/")
def home():
    return "Indodax Notifier Running on Railway!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
