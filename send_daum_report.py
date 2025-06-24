
import requests
from bs4 import BeautifulSoup
import telegram
from datetime import datetime

# 텔레그램 봇 토큰 및 채널 ID
TOKEN = "6436282670:AAEge9QjzUYycDGe4LQqxvuGcInBHyWn-Eo"
CHAT_ID = "-1002128602192"

# 상승/하락 색상 텍스트 변환
def format_change_rate(rate_str):
    if "-" in rate_str:
        return f'<font color="blue">{rate_str}</font>'
    else:
        return f'<font color="red">+{rate_str}</font>'

# 금액 변환: 백만 → 억 단위
def format_amount_million_to_eok(value):
    try:
        value = int(value.replace(",", ""))
        return f"{value // 100}억"
    except:
        return value

# 메시지 전송 함수
def send_message(message):
    bot = telegram.Bot(token=TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)

# 1. 외국인 순매수/순매도 종목 수집 (Top10)
def get_foreign_trades():
    headers = {
        "referer": "https://finance.daum.net/domestic/influential_investors",
        "User-Agent": "Mozilla/5.0"
    }

    url_buy = "https://finance.daum.net/api/ranking/buy"
    url_sell = "https://finance.daum.net/api/ranking/sell"

    buy_data = requests.get(url_buy, headers=headers).json().get("data", [])[:10]
    sell_data = requests.get(url_sell, headers=headers).json().get("data", [])[:10]

    buy_list = []
    for i, item in enumerate(buy_data, 1):
        name = item.get("name", "")
        amount = format_amount_million_to_eok(str(item.get("amount", "0")))
        change = format_change_rate(str(item.get("rate", "0.00")))
        buy_list.append(f"{i}. {name} – {amount}, {change}")

    sell_list = []
    for i, item in enumerate(sell_data, 1):
        name = item.get("name", "")
        amount = format_amount_million_to_eok(str(item.get("amount", "0")))
        change = format_change_rate(str(item.get("rate", "0.00")))
        sell_list.append(f"{i}. {name} – {amount}, {change}")

    return buy_list, sell_list

# 2. 외국인 보유율 상위 (코스피/코스닥)
def get_foreign_holdings():
    headers = {
        "referer": "https://finance.daum.net/domestic/investor_holdings",
        "User-Agent": "Mozilla/5.0"
    }

    result = {"KOSPI": [], "KOSDAQ": []}
    for market in ["STK", "KSQ"]:
        url = f"https://finance.daum.net/api/investor/holding-stocks?per=15&market={market}&page=1"
        data = requests.get(url, headers=headers).json().get("data", [])
        for i, item in enumerate(data, 1):
            name = item.get("name", "")
            rate = format_change_rate(str(item.get("chgRate", "0.00")))
            volume = f"{item.get('tradeVolume', 0):,}"
            buy_vol = f"{item.get('buyVolume', 0):,}"
            hold = f"{item.get('foreignRate', 0):.2f}%"
            result["KOSPI" if market == "STK" else "KOSDAQ"].append(
                f"{i}. {name} – 등락률: {rate}, 거래량: {volume}, 순매수: {buy_vol}, 보유율: {hold}"
            )
    return result

# 전체 실행
def main():
    now = datetime.now().strftime("%Y-%m-%d")
    buy_list, sell_list = get_foreign_trades()
    holdings = get_foreign_holdings()

    message = f"⏰ <b>{now} 오전 8시 Daum 외국인 매매 리포트</b>\n\n"
    message += "1️⃣ [외국인 순매수 TOP10]\n" + "\n".join(buy_list) + "\n\n"
    message += "2️⃣ [외국인 순매도 TOP10]\n" + "\n".join(sell_list) + "\n\n"
    message += "3️⃣ [외국인 보유율 TOP15 – 코스피]\n" + "\n".join(holdings['KOSPI']) + "\n\n"
    message += "4️⃣ [외국인 보유율 TOP15 – 코스닥]\n" + "\n".join(holdings['KOSDAQ'])

    send_message(message)

if __name__ == "__main__":
    main()
