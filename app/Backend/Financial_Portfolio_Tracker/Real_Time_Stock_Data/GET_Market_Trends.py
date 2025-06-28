import requests

class Get_Market_Trends:
    '''
    Get market trends real time values
    returen: JSON of market trends
    '''
    def get_top_gainers():
        url = "https://www.alphavantage.co/query"
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

if __name__ == '__main__':
    Get_Market_Trends.get_top_gainers()
