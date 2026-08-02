import os
import requests
import yfinance as yf
from openai import OpenAI
from datetime import datetime
from email.mime.text import MIMEText
import smtplib


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def get_market_snapshot():

    symbols = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Dow": "^DJI",
        "Bitcoin": "BTC-USD"
    }

    result = {}

    for name, ticker in symbols.items():
        data = yf.Ticker(ticker)
        price = data.history(period="1d")["Close"].iloc[-1]
        result[name] = round(price, 2)

    return result


def get_news():

    url = "https://newsapi.org/v2/top-headlines"

    params = {
        "category": "business",
        "language": "en",
        "country": "us",
        "apiKey": os.environ["NEWS_API_KEY"]
    }

    response = requests.get(url, params=params)

    articles = response.json()["articles"]

    headlines = []

    for article in articles[:20]:
        headlines.append(article["title"])

    return headlines


def create_report(news, market):

    prompt = f"""
You are a professional financial analyst.

Create my daily market intelligence report.

Market snapshot:
{market}

Today's news:
{news}

Cover:

1. Market overview
2. Top market-moving stories
3. AI and Big Tech
4. Federal Reserve and macroeconomics
5. Earnings
6. Crypto
7. ETFs
8. Global markets
9. Three things to watch today

Explain why each item matters to investors.
Keep it concise.
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def send_email(report):

    msg = MIMEText(report)

    msg["Subject"] = (
        "Daily Market Intelligence Report - "
        + datetime.now().strftime("%Y-%m-%d")
    )

    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = os.environ["EMAIL_TO"]

    server = smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    )

    server.login(
        os.environ["EMAIL_FROM"],
        os.environ["EMAIL_PASSWORD"]
    )

    server.send_message(msg)

    server.quit()


if __name__ == "__main__":

    market = get_market_snapshot()

    news = get_news()

    report = create_report(
        news,
        market
    )

    send_email(report)

    print("Daily market report sent!")
