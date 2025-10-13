from flask import Flask
import os
import json
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Konfigurasi
BOT_TOKEN = "8485547227:AAEnNbuM5Ongt_PSIT9tH4-z8cAOBDYDg7k"
CHAT_IDS = ["2053231295"]  # bisa tambahkan banyak ID
URL = "https://blog.indodax.com/"
CACHE_FILE = "sent.json"

# --- Fungsi load/simpan cache ---
def load_sent():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(sent), f)

# --- Ambil artikel terbaru dari Indodax Blog ---
def get_latest_article():
    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Ambil artikel pertama
        article = soup.find("h2", class_="post-title").find("a")
        title = article.text.strip()
        link = article["href"]
        return {"title": title, "link": link}
    except Exception as e:
        print("Gagal mengambil artikel:", e)
        return None

# --- Kirim ke Telegram ---
def send_to_telegram(article):
    for chat_id in CHAT_IDS:
        text = f"🆕 Artikel baru di Indodax Blog!\n\n{article['title']}\n{article['link']}"
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
            timeout=10
        )

# --- Proses utama ---
def check_new_article():
    sent = load_sent()
    latest = get_latest_article()
    if not latest:
        return "❌ Gagal ambil artikel."

    link = latest["link"]
    if link not in sent:
        send_to_telegram(latest)
        sent.add(link)
        save_sent(sent)
        print(f"✅ Artikel baru dikirim: {latest['title']}")
        return f"✅ Artikel baru dikirim: {latest['title']}"
    else:
        print("🔁 Tidak ada artikel baru.")
        return "🔁 Tidak ada artikel baru."

# --- Endpoint untuk cron-job.org ---
@app.route("/run")
def run():
    result = check_new_article()
    return result

@app.route("/")
def home():
    return "🚀 Indodax Blog Notifier aktif di Railway!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
