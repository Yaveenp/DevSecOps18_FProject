import requests

def get_top_gainers():
    url = "https://api.example.com/market/top-gainers"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        gainers = response.json()
        for stock in gainers:
            print(f"{stock['symbol']}: {stock['price']} ({stock['change_percent']}%)")
    else:
        print("Failed to fetch data.")

get_top_gainers()