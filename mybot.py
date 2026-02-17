import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# توکن ربات تلگرام
TOKEN = '7654399573:AAEOhd7xgrDcFMPuWkZ4A-a5PXBX8Tf9PuI'

# دریافت قیمت لحظه‌ای از بایننس
def get_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url)
    return float(response.json()['price'])

# دریافت داده‌های کندل (OHLCV) از بایننس
def get_candles(symbol, interval='1h', limit=100):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)
    return response.json()

# شناسایی نقاط حمایت و مقاومت
def support_resistance(candles):
    highs = [float(candle[2]) for candle in candles]
    lows = [float(candle[3]) for candle in candles]
    support = min(lows)
    resistance = max(highs)
    return support, resistance

# تحلیل روند بازار
def analyze_market(candles):
    close_prices = [float(candle[4]) for candle in candles]
    if close_prices[-1] > close_prices[-2]:
        return "Bullish"
    elif close_prices[-1] < close_prices[-2]:
        return "Bearish"
    else:
        return "Neutral"

# نقاط ورود و خروج
def entry_exit_points(candles, trend):
    support, resistance = support_resistance(candles)
    if trend == "Bullish":
        entry = support * 1.02
        target = resistance * 1.02
        stop_loss = support
    elif trend == "Bearish":
        entry = resistance * 0.98
        target = support * 0.98
        stop_loss = resistance
    else:
        return None, None, None
    return entry, stop_loss, target

# مدیریت سرمایه
def calculate_position_size(account_balance, risk_percentage, entry_price, stop_loss_price):
    risk_amount = account_balance * (risk_percentage / 100)
    risk_per_unit = abs(entry_price - stop_loss_price)
    position_size = risk_amount / risk_per_unit
    return position_size

# ارسال تحلیل به تلگرام
async def send_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = "BTCUSDT"
    candles = get_candles(symbol)
    trend = analyze_market(candles)
    
    if trend == "Bullish":
        analysis = "روند صعودی: پیشنهاد خرید"
    elif trend == "Bearish":
        analysis = "روند نزولی: پیشنهاد فروش"
    else:
        analysis = "بازار بی‌ثبات است"

    entry, stop_loss, target = entry_exit_points(candles, trend)
    if entry:
        analysis += f"\nنقطه ورود: {entry}\nاستاپ لاس: {stop_loss}\nتارگت: {target}"

    account_balance = 10000
    risk_percentage = 1
    position_size = calculate_position_size(account_balance, risk_percentage, entry, stop_loss)
    analysis += f"\nحجم پوزیشن: {position_size} BTC"

    await update.message.reply_text(analysis)

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات تحلیل بازار هستم.")

# اجرای ربات
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", send_analysis))
    
    app.run_polling()
