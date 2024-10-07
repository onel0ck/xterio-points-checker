import os
import requests
import random
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from loguru import logger

# Configure loguru
logger.remove()
logger.add(
    "xterio_checker.log",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    rotation="1 day"
)
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True
)

class ProxyManager:
    def __init__(self, proxy_file):
        self.proxies = self.load_proxies(proxy_file)
        self.proxy_index = 0

    def load_proxies(self, proxy_file):
        with open(proxy_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def get_next_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

class WalletManager:
    def __init__(self, wallet_file):
        self.wallets = self.load_wallets(wallet_file)

    def load_wallets(self, wallet_file):
        with open(wallet_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def get_address_from_private_key(self, private_key):
        account = Account.from_key(private_key)
        return account.address

class XterioAPI:
    BASE_URL = "https://api.xter.io"

    def __init__(self, proxy):
        self.proxy = proxy
        self.session = self.create_session()

    def create_session(self):
        session = requests.Session()
        session.proxies = {'http': self.proxy, 'https': self.proxy}
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://xter.io/",
            "Origin": "https://xter.io"
        })
        return session

    def login(self, wallet_address, private_key):
        url = f"{self.BASE_URL}/account/v1/login/wallet"
        
        try:
            response = self.session.get(f"{self.BASE_URL}/account/v1/login/wallet/{wallet_address}")
            response.raise_for_status()
            login_message = response.json()['data']['message']

            message = encode_defunct(text=login_message)
            signed_message = Account.sign_message(message, private_key)

            payload = {
                "address": wallet_address,
                "type": "eth",
                "sign": signed_message.signature.hex(),
                "provider": "METAMASK",
                "invite_code": ""
            }
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()['data']['id_token']
        except requests.RequestException as e:
            logger.error(f"Error during login for {wallet_address}: {str(e)}")
            if response:
                logger.error(f"Response content: {response.text}")
            return None

    def get_points(self, wallet_address, auth_token):
        url = f"{self.BASE_URL}/account/v1/points/dashboard?"
        self.session.headers.update({"authorization": auth_token})
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            total_points = data['data']['total_points'][0]
            points = total_points['points']
            bonus_points = total_points['bonus_points']
            return points + bonus_points
        except requests.RequestException as e:
            logger.error(f"Error fetching points for {wallet_address}: {str(e)}")
            if response:
                logger.error(f"Response content: {response.text}")
            return None

class PointsChecker:
    def __init__(self, wallet_manager, proxy_manager):
        self.wallet_manager = wallet_manager
        self.proxy_manager = proxy_manager

    def check_points(self, private_key):
        address = self.wallet_manager.get_address_from_private_key(private_key)
        proxy = self.proxy_manager.get_next_proxy()
        if not proxy:
            logger.error(f"No proxy available for {address}")
            return None
        
        xterio_api = XterioAPI(proxy)
        auth_token = xterio_api.login(address, private_key)
        if auth_token:
            time.sleep(2)
            points = xterio_api.get_points(address, auth_token)
            if points is not None:
                logger.success(f"{address}:{points}")
                return f"{address}:{points}"
        logger.error(f"Failed to get points for {address}")
        return None

    def check_all_wallets(self):
        results = []
        total_points = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_wallet = {executor.submit(self.check_points, private_key): private_key for private_key in self.wallet_manager.wallets}
            for future in as_completed(future_to_wallet):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        total_points += int(result.split(':')[1])
                except Exception as e:
                    logger.error(f"Error processing wallet: {str(e)}")
        
        return results, total_points

def main():
    proxy_manager = ProxyManager('proxies.txt')
    wallet_manager = WalletManager('wallets.txt')
    points_checker = PointsChecker(wallet_manager, proxy_manager)

    logger.info("Starting XTERIO points check...")
    results, total_points = points_checker.check_all_wallets()

    with open('result.txt', 'w') as f:
        for result in results:
            f.write(f"{result}\n")
        f.write(f"\nTotal points across all accounts: {total_points}")

    logger.success(f"Check completed. Results saved to result.txt. Total points: {total_points}")

if __name__ == "__main__":
    main()