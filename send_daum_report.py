
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import telegram

BOT_TOKEN = "8146688249:AAFcIyUeYXXSO2h2zCHerPHedgyN42yxMrY"
CHAT_ID = "-1002563974261"

def send_message(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")

def format_percent(value):
    if value.startswith("-"):
        return f"🔵 {value}"
    else:
        return f"🔴 +{value}"

def crawl_daum():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15)

    try:
        driver.get("https://finance.daum.net/domestic/influential_investors")
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        result = "<b>📈 Daum 외국인 매매 리포트</b>\n"

        # 순매수
        try:
            result += "\n<b>1️⃣ 외국인 순매수 TOP10</b>\n"
            table = soup.select("div.card:nth-of-type(1) tbody tr")
            for i, row in enumerate(table[:10], 1):
                cols = row.find_all("td")
                name = cols[1].get_text(strip=True)
                price = cols[2].get_text(strip=True)
                change = format_percent(cols[3].get_text(strip=True))
                result += f"{i}. {name} – {price}, {change}\n"
        except Exception as e:
            result += f"❌ 순매수 데이터 오류: {e}\n"

        # 순매도
        try:
            result += "\n<b>2️⃣ 외국인 순매도 TOP10</b>\n"
            table = soup.select("div.card:nth-of-type(2) tbody tr")
            for i, row in enumerate(table[:10], 1):
                cols = row.find_all("td")
                name = cols[1].get_text(strip=True)
                price = cols[2].get_text(strip=True)
                change = format_percent(cols[3].get_text(strip=True))
                result += f"{i}. {name} – {price}, {change}\n"
        except Exception as e:
            result += f"❌ 순매도 데이터 오류: {e}\n"

        # 보유율 코스피
        try:
            result += "\n<b>3️⃣ 외국인 보유율 TOP15 - 코스피</b>\n"
            driver.get("https://finance.daum.net/domestic/foreign")
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.select("div.box_contents tbody tr")
            for i, row in enumerate(table[:15], 1):
                cols = row.find_all("td")
                name = cols[1].get_text(strip=True)
                rate = format_percent(cols[2].get_text(strip=True))
                volume = cols[3].get_text(strip=True)
                foreign = cols[5].get_text(strip=True)
                result += f"{i}. {name} – {rate}, {volume}, 외인보유: {foreign}\n"
        except Exception as e:
            result += f"❌ 보유율 데이터 오류: {e}\n"

    except Exception as e:
        result = f"❌ 페이지 로딩 실패: {e}"

    driver.quit()
    return result

if __name__ == "__main__":
    message = crawl_daum()
    send_message(message)
