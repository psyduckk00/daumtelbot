
import requests
import telegram
from datetime import datetime

TOKEN = "8146688249:AAFcIyUeYXXSO2h2zCHerPHedgyN42yxMrY"
CHAT_ID = "-1002563974261"

def format_change_rate(rate_str):
    if "-" in rate_str:
        return f'<font color="blue">{rate_str}</font>'
    else:
        return f'<font color="red">+{rate_str}</font>'

def format_amount_million_to_eok(value):
    try:
        value = int(value.replace(",", ""))
        if value >= 10**12:
            return f"{round(value / 10**12, 1)}조"
        elif value >= 10**8:
            return f"{value // 100}억"
        else:
            return f"{value}"
    except:
        return value

def send_message(message):
    bot = telegram.Bot(token=TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")

def get_foreign_trades():
    headers = {
        "referer": "https://finance.daum.net/domestic/influential_investors",
        "User-Agent": "Mozilla/5.0"
    }
    url_buy = "https://finance.daum.net/api/ranking/buy"
    url_sell = "https://finance.daum.net/api/ranking/sell"

    buy_resp = requests.get(url_buy, headers=headers)
    sell_resp = requests.get(url_sell, headers=headers)

    try:
        buy_data = buy_resp.json().get("data", [])[:10]
    except:
        buy_data = []
    try:
        sell_data = sell_resp.json().get("data", [])[:10]
    except:
        sell_data = []

    buy_list = []
    if not buy_data:
        buy_list.append("❌ 순매수 데이터를 불러오지 못했습니다.")
    else:
        for i, item in enumerate(buy_data, 1):
            name = item.get("name", "")
            amount = format_amount_million_to_eok(str(item.get("amount", "0")))
            change = format_change_rate(str(item.get("rate", "0.00")))
            buy_list.append(f"{i}. {name} – {amount}, {change}")

    sell_list = []
    if not sell_data:
        sell_list.append("❌ 순매도 데이터를 불러오지 못했습니다.")
    else:
        for i, item in enumerate(sell_data, 1):
            name = item.get("name", "")
            amount = format_amount_million_to_eok(str(item.get("amount", "0")))
            change = format_change_rate(str(item.get("rate", "0.00")))
            sell_list.append(f"{i}. {name} – {amount}, {change}")

    return buy_list, sell_list

def get_foreign_holdings():
    headers = {
        "referer": "https://finance.daum.net/domestic/investor_holdings",
        "User-Agent": "Mozilla/5.0"
    }
    result = {"KOSPI": [], "KOSDAQ": []}
    for market in ["STK", "KSQ"]:
        url = f"https://finance.daum.net/api/investor/holding-stocks?per=15&market={market}&page=1"
        try:
            data = requests.get(url, headers=headers).json().get("data", [])
        except:
            data = []

        if not data:
            result["KOSPI" if market == "STK" else "KOSDAQ"].append("❌ 외국인 보유율 데이터를 불러오지 못했습니다.")
        else:
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

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    buy_list, sell_list = get_foreign_trades()
    holdings = get_foreign_holdings()

    message = f"⏰ <b>{now} Daum 외국인 매매 리포트</b>\n\n"
    message += "1️⃣ [외국인 순매수 TOP10]\n" + "\n".join(buy_list) + "\n\n"
    message += "2️⃣ [외국인 순매도 TOP10]\n" + "\n".join(sell_list) + "\n\n"
    message += "3️⃣ [외국인 보유율 TOP15 – 코스피]\n" + "\n".join(holdings['KOSPI']) + "\n\n"
    message += "4️⃣ [외국인 보유율 TOP15 – 코스닥]\n" + "\n".join(holdings['KOSDAQ'])

    send_message(message)

if __name__ == "__main__":
    main()
