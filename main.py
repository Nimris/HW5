import aiohttp
import asyncio
from datetime import datetime, timedelta
from requests import session


class PrivatBankAPIClient:
    Base_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
    
    def __init__(self, days: int):
        self.days = days
        # self.session = None
    
    async def fetch_currency_rates(self, date: str):
        url = f"{self.Base_URL}{date}"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching data for {date}, response status: {response.status}")
                return None        
        
        
    async def get_rates_for_last_days(self):
        self.session = aiohttp.ClientSession()
        results = []
        try:
            for i in range(self.days):
                date = datetime.now() - timedelta(days = i)
                date = date.strftime('%d.%m.%Y')
                data = await self.fetch_currency_rates(date)
                if data:
                    rates = self.extract_currency_rates(data)
                    results.append({date: rates})
                else:
                    print("No data for", date)
                    return None
        finally:
            await self.session.close()
        return results
        
        
    @staticmethod
    def extract_currency_rates(data):
        rates = {}
        for rate in data.get("exchangeRate"):
            if rate.get("currency") in ["USD", "EUR"]:
                rates[rate["currency"]] = {
                    "sale": rate["saleRate"],
                    "purchase": rate["purchaseRate"]
                    }
        return rates
               

async def main(days):
    if days not in range(1, 11):
        print('Please enter a number between 1 and 10.')
        return None

    client = PrivatBankAPIClient(days)
    try:
        rates = await client.get_rates_for_last_days()
    finally:
        await client.session.close()
    
    if rates:
        import pprint
        pprint.pprint(rates)
    else:
        print('No data to display.')
    

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if len(sys.argv) == 3:
        extra_currency = sys.argv[2]
    asyncio.run(main(days))