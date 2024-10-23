import random
from colorama import Fore, Style, init
import time
import sys
import json
import os
from Crypto.Cipher import AES
from Crypto import Random
from datetime import datetime
from fake_useragent import FakeUserAgent, UserAgent
import pytz
import cloudscraper
import base64
import hashlib

requests = cloudscraper.create_scraper()

# Inisialisasi UserAgent
ua = UserAgent()

# Membaca konfigurasi dari file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Menggunakan pengaturan dari config.json
use_claim_ads = config['features']['claim_ads']
use_claim_quest = config['features']['claim_quest']
use_claim_lottery = config['features']['claim_lottery']

def log_system(message, timezone='Asia/Jakarta'):
    print(
        f"[⚔] | {message}"
    )

def make_request(method, url, headers, json=None, data=None):
    retry_count = 0
    max_retries = 5 
    while retry_count < max_retries:
        try:
            time.sleep(random.uniform(1, 5))  
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, json=json)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json, data=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json, data=data)
            else:
                raise ValueError("Invalid method.")

            if response.status_code >= 500:
                log_system(f"Status Code: {response.status_code} | Server Down")
                retry_count += 1
                continue
            elif response.status_code >= 400:
                log_system(f"Status Code: {response.status_code} | {response.text}")
                return None
            elif response.status_code >= 200:
                return response.json()
        except Exception as e:
            log_system(f"Error during request: {str(e)}")
            retry_count += 1

    log_system("Max retries exceeded.")
    return None

def reset_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
            
def key_bot():
    api = base64.b64decode("aHR0cDovL2l0YmFhcnRzLmNvbS9hcGkuanNvbg==").decode('utf-8')
    try:
        response = requests.get(api)
        response.raise_for_status()
        try:
            data = response.json()
            header = data['header']
            print('\033[96m' + header + '\033[0m')
        except json.JSONDecodeError:
            print('\033[96m' + response.text + '\033[0m')
    except requests.RequestException as e:
        print_('\033[96m' + f"Failed to load header: {e}" + '\033[0m')

class Banana:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://banana.carv.io',
            'Referer': 'https://banana.carv.io/',
            'Sec-CH-UA-Mobile': '?1',
            'Sec-CH-UA-Platform': '"iOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': ua.random,  # Menggunakan User-Agent acak
            'X-App-ID': 'carv',
            'x-interceptor-id': "994daea3cbe0d2aa80ea5a36ec9d7005a1670fbbac0c9eb5fb2c596d09932242f23d416e9885dcd0230c3ba2f8abc9ee"
        }
    def pad(self, s):
        block_size = 16
        padding = block_size - len(s.encode('utf-8')) % block_size
        return s + chr(padding) * padding

    def get_key_and_iv(self, password, salt, klen=32, ilen=16, msgdgst='md5'):
        password = password.encode('utf-8')
        maxlen = klen + ilen
        keyiv = b''
        prev = b''
        while len(keyiv) < maxlen:
            prev = hashlib.md5(prev + password + salt).digest()
            keyiv += prev
        key = keyiv[:klen]
        iv = keyiv[klen:klen+ilen]
        return key, iv

    def encrypt_timestamp(self, timestamp, password):
        salt = Random.new().read(8)
        key, iv = self.get_key_and_iv(password, salt)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_timestamp = self.pad(timestamp)
        encrypted = cipher.encrypt(padded_timestamp.encode('utf-8'))
        encrypted_data = b"Salted__" + salt + encrypted
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        return encrypted_b64

    def login(self, query):
        url = 'https://interface.carv.io/banana/login'
        headers = {
            **self.headers
        }
        while True:
            payload = {
                        'tgInfo': query,
                }
            time.sleep(2)
            response = make_request('post', url, headers=headers, json=payload)
            data = response
            token = f"{data['data']['token']}"
            return f"Bearer {token}"

    def get_user_info(self, token: str):
        url = 'https://interface.carv.io/banana/get_user_info'
        headers = {
            **self.headers,
            'authorization' : token
        }
        try:
            response = make_request('get', url, headers=headers)
            return response
        except (Exception) as e:
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def get_lottery_info(self, token: str):
        url = 'https://interface.carv.io/banana/get_lottery_info'
        headers = {
            **self.headers,
            'authorization' : token
        }
        try:
            get_user = self.get_user_info(token=token)
            response = make_request('get', url, headers=headers)
            data = response
            if get_user['data']['max_click_count'] > get_user['data']['today_click_count']:
                click = self.do_click(token=token, click_count=get_user['data']['max_click_count'] - get_user['data']['today_click_count'])
                if click['msg'] == "Success":
                    log_system(f"{Fore.GREEN + Style.BRIGHT}[ Clicked {click['data']['peel']}]{Style.RESET_ALL}")
                else:
                    log_system(f"{Fore.RED + Style.BRIGHT}[ {click['msg']} ]{Style.RESET_ALL}")
            else:
                log_system("[INFO] Out of clicks, taking a break.")

            now = datetime.now()
            last_countdown_start_time = datetime.fromtimestamp(data['data']['last_countdown_start_time'] / 1000)
            countdown_interval_minutes = data['data']['countdown_interval']

            elapsed_time_minutes = (now - last_countdown_start_time).total_seconds() / 60
            remaining_time_minutes = max(countdown_interval_minutes - elapsed_time_minutes, 0)
            if remaining_time_minutes > 0 and data['data']['countdown_end'] == False:
                hours, remainder = divmod(remaining_time_minutes * 60, 3600)
                minutes, seconds = divmod(remainder, 60)
                log_system(f"{Fore.BLUE + Style.BRIGHT}[ Claim Your Banana In {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds ]{Style.RESET_ALL}")
            else:
                claim_lottery = self.claim_lottery(token=token, lottery_type=1)
                if claim_lottery['msg'] == "Success":
                    log_system(f"{Fore.GREEN + Style.BRIGHT}[ Lottery Claimed]{Style.RESET_ALL}")
                    time.sleep(2)
                    log_system('Claim Ads')
                    ads = self.claim_ads(token=token, type=2)
                    if ads is not None:
                        code = ads.get('code',0)
                        if code == 0:
                            data = ads.get('data',{})
                            log_system(f"income : {data.get('income',0)} | peels :  {data.get('peels',0)} | speedup :  {data.get('speedup',0)}")
                        else:
                            log_system(f"Code : {code} | msg : {ads.get('msg')}")
                    speedup_count = get_user['data']['speedup_count']
                    if speedup_count > 0:
                        time.sleep(2)
                        speedup = self.do_speedup(token=token)
                        if speedup['msg'] == "Success":
                            log_system(f"{Fore.GREEN + Style.BRIGHT}[ Speedup Applied ]")
                    else:
                        time.sleep(2)
                        ads = self.claim_ads(token=token, type=1)
                        if ads is not None:
                            code = ads.get('code',0)
                            if code == 0:
                                data = ads.get('data',{})
                                log_system(f"income : {data.get('income',0)} | peels :  {data.get('peels',0)} | speedup :  {data.get('speedup',0)}")
                                speedup = {data.get('speedup',0)}
                                if speedup != 0:
                                    time.sleep(2)
                                    speedup = self.do_speedup(token=token)
                                    if speedup['msg'] == "Success":
                                        log_system(f"{Fore.GREEN + Style.BRIGHT}[ Speedup Applied ]")
                            else:
                                log_system(f"Code : {code} | msg : {ads.get('msg')}")
                else:
                    log_system(f"{Fore.RED + Style.BRIGHT}[ {claim_lottery['msg']} ]{Style.RESET_ALL}")
            time.sleep(2)
           

            get_lottery = self.get_user_info(token=token)
            harvest = get_lottery['data']['lottery_info']['remain_lottery_count']
            while harvest > 0:
                time.sleep(10)
                self.do_lottery(token=token)
                harvest -= 1
        except (Exception) as e:
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_click(self, token: str, click_count: int):
        url = 'https://interface.carv.io/banana/do_click'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'clickCount': click_count
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            log_system("[ERROR] An error occurred during the click process.")
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_speedup(self, token: str):
        url = 'https://interface.carv.io/banana/do_speedup'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {}
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            log_system("[ERROR] An error occurred during the speedup process.")
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def claim_lottery(self, token: str, lottery_type: int):
        if not use_claim_lottery:
            print("claim_lottery is disabled in the configuration.")
            return None
        # Logika claim_lottery jika diaktifkan
        url = 'https://interface.carv.io/banana/claim_lottery'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'claimLotteryType': lottery_type
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            log_system("[ERROR] An error occurred during the lottery claim.")
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_lottery(self, token: str):
        url = 'https://interface.carv.io/banana/do_lottery'
        timestamp = str(int(time.time() * 1000))
        encrypted_timestamp = self.encrypt_timestamp(timestamp, "1,1,0")
        headers = {
            **self.headers,
            'authorization' : token,
            "Request-Time": encrypted_timestamp
        }
        payload = {}

        response = make_request('post', url, headers=headers, json=payload)
        data = response
        if data['msg'] == "Success":
            log_system(
                f"{Fore.YELLOW + Style.BRIGHT}[ {data['data']['banana_info']['name']} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {data['data']['banana_info']['ripeness']} ]{Style.RESET_ALL}"
            )
            log_system(f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {data['data']['banana_info']['daily_peel_limit']} ]{Style.RESET_ALL}")
            log_system(
                f"{Fore.YELLOW + Style.BRIGHT}[ Sell Price Peel {data['data']['banana_info']['sell_exchange_peel']} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}[ Sell Price USDT {data['data']['banana_info']['sell_exchange_usdt']} ]{Style.RESET_ALL}"
            )
            log_system("[INFO] Successfully claimed the lottery.")
        else:
            log_system(f"{Fore.RED + Style.BRIGHT}[ {data['msg']} ]{Style.RESET_ALL}")
 

    def get_banana_list(self, token: str):
        url = 'https://interface.carv.io/banana/get_banana_list/v2?page_num=1&page_size=15'
        headers = {
            **self.headers,
            'authorization' : token
        }
        try:
            get_user = self.get_user_info(token=token)
            response = make_request('get', url, headers=headers)
            if response is not None:
                get_banana = response
                filtered_banana_list = [banana for banana in get_banana['data']['list'] if banana['count'] >= 1]
                highest_banana = max(filtered_banana_list, key=lambda x: x['daily_peel_limit'])
                if highest_banana['daily_peel_limit'] > get_user['data']['equip_banana']['daily_peel_limit']:
                    log_system(f"{Fore.MAGENTA + Style.BRIGHT}[ Equipping Banana ]{Style.RESET_ALL}")
                    equip_banana = self.do_equip(token=token, banana_id=highest_banana['banana_id'])
                    if equip_banana['msg'] == "Success":
                        log_system(
                            f"{Fore.YELLOW + Style.BRIGHT}[ {highest_banana['name']}]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {highest_banana['ripeness']} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {highest_banana['daily_peel_limit']} ]{Style.RESET_ALL}"
                        )
                    else:
                        log_system(f"{Fore.RED + Style.BRIGHT}[ {equip_banana['msg']} ]{Style.RESET_ALL}")
                else:
                    log_system("[INFO] Currently using the best available banana.")
                    log_system(
                        f"{Fore.YELLOW + Style.BRIGHT}[ {highest_banana['name']}]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {highest_banana['ripeness']} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {highest_banana['daily_peel_limit']} ]{Style.RESET_ALL}"
                    )
                count_banana = [banana for banana in get_banana['data']['list'] if banana['count'] > 1]
                for sell in count_banana:
                    sell_banana = self.do_sell(token=token, banana_id=sell['banana_id'], sell_count=sell['count'] - 1)
                    if sell_banana['msg'] == "Success":
                        log_system(f"{Fore.MAGENTA + Style.BRIGHT}[ Only One {sell['name']} Remaining ]{Style.RESET_ALL}")
                        log_system(
                            f"{Fore.YELLOW + Style.BRIGHT}[ Sell Got {sell_banana['data']['sell_got_peel']} Peel]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}[ Sell Got {sell_banana['data']['sell_got_usdt']} USDT]{Style.RESET_ALL}"
                        )
                        log_system(
                            f"{Fore.YELLOW + Style.BRIGHT}[ {sell_banana['data']['peel']} Peel]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}[ {sell_banana['data']['usdt']} USDT]{Style.RESET_ALL}"
                        )
                    else:
                        log_system(f"{Fore.RED + Style.BRIGHT}[ {sell_banana['msg']} ]{Style.RESET_ALL}")
        except (Exception) as e:
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_equip(self, token: str, banana_id: int):
        url = 'https://interface.carv.io/banana/do_equip'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'bananaId': banana_id
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            log_system("[ERROR] An error occurred during the equipment process.")
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_sell(self, token: str, banana_id: int, sell_count: int):
        url = 'https://interface.carv.io/banana/do_sell'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'bananaId': banana_id,
            'sellCount': sell_count
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            log_system("[ERROR] An error occurred during the sell process.")
            return log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def achieve_quest(self, quest_id, token):
        url = f'https://interface.carv.io/banana/achieve_quest'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {"quest_id": quest_id}
        response = make_request('post', url, headers=headers, json=payload)
        return response
    
    def claim_quest(self, quest_id, token):
        if not use_claim_quest:
            print("claim_quest is disabled in the configuration.")
            return None
        # Logika claim_quest jika diaktifkan
        url = f'https://interface.carv.io/banana/claim_quest'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {"quest_id": quest_id}
        response = make_request('post', url, headers=headers, json=payload)
        return response

    def claim_quest_lottery(self, token):
        url = 'https://interface.carv.io/banana/claim_quest_lottery'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {}
        response = make_request('post', url, headers=headers, json=payload)
        return response
    
    def get_quest(self, token):
        url = f'https://interface.carv.io/banana/get_quest_list/v2?page_num=1&page_size=15'
        headers = {
            **self.headers,
            'authorization' : token
        }
        response = make_request('get', url, headers=headers)
        return response

    def claim_ads(self, token, type):
        if not use_claim_ads:
            print("claim_ads is disabled in the configuration.")
            return None
        # Logika claim_ads jika diaktifkan
        url = 'https://interface.carv.io/banana/claim_ads_income'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {'type': type}
        response = make_request('post', url, headers=headers, json=payload)
        return response

    def clear_quest(self, token):
            data_quest = self.get_quest(token)
            data = data_quest.get('data')
            quest_list = data.get('list', [])

            for index, quest in enumerate(quest_list, start=1):
                quest_name = quest.get('quest_name', 'N/A')
                is_achieved = quest.get('is_achieved', False)
                is_claimed = quest.get('is_claimed', False)
                quest_id = quest.get('quest_id')
                
                achieved_status = "Yes" if is_achieved else "No"
                claimed_status = "Yes" if is_claimed else "No"
                
                quest_name_color = Fore.CYAN
                achieved_color = Fore.GREEN if is_achieved else Fore.RED
                claimed_color = Fore.GREEN if is_claimed else Fore.RED
                
                log_system(f"{Fore.BLUE}[Quest {index}] : {quest_name_color}{quest_name} {Fore.BLUE}")
                
                if 'bind' in quest_name.lower():
                    if not is_achieved:
                        log_system("[INFO] Skipping Quest")
                        continue
                if 'badge' in quest_name.lower():
                    if not is_achieved:
                        log_system("[INFO] Skipping Quest")
                        continue
                if 'premium' in quest_name.lower():
                    if not is_achieved:
                        log_system("[INFO] Skipping Quest")
                        continue
                if 'pvp' in quest_name.lower():
                    if not is_achieved:
                        log_system("[INFO] Skipping Quest")
                        continue
                if 'mobile' in quest_name.lower():
                    if not is_achieved:
                        log_system("[INFO] Skipping Quest")
                        continue
                if 'telgather' in quest_name.lower():
                    if not is_achieved:
                        log_system("[INFO] Skipping Quest")
                        continue

                if not is_achieved:
                    trys = 3
                    while True:
                        if trys <= 0:
                            break
                        time.sleep(2)
                        achieve_response = self.achieve_quest(quest_id, token=token)
                        response = achieve_response
                        time.sleep(2)
                        if response.get('msg') == "Success":
                            response = self.claim_quest(quest_id, token=token)
                            res = response
                            if res.get('msg') == "Success":
                                log_system(f"{Fore.GREEN}Quest {quest_name} Achieved and Claimed Successfully{Style.RESET_ALL}")
                                break
                        trys -= 1

                    time.sleep(2) 


                if is_achieved and not is_claimed:
                    claim_response = self.claim_quest(quest_id, token=token)
                    res = claim_response
                    if res.get('msg') == "Success":
                        log_system(f"{Fore.GREEN}Quest {quest_name} Achieved and Claimed Successfully{Style.RESET_ALL}")
                    time.sleep(2) 

            is_claimed = data.get('is_claimed')
            trys = 3
            while True:
                if trys <= 0:
                            break
                if is_claimed == True:
                    time.sleep(2)
                    dats = self.claim_quest_lottery(token=token)
                    if dats.get('msg') == "Success":
                        log_system(f"{Fore.GREEN}Claim reward quest done")
                    time.sleep(2)
                    data_quest = self.get_quest(token)
                    data = data_quest.get('data')
                    is_claimed = data.get('is_claimed')
                    trys -= 1
                else:
                    break
                trys -= 1
    

def load_credentials():
    try:
        with open('query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query.txt tidak ditemukan.")
        return [  ]
    except Exception as e:
        print("Terjadi kesalahan saat memuat token:", str(e))
        return [  ]

def main():
    init(autoreset=True)
    delay = random.randint(14400, 14550)
    ban = Banana()
    reset_screen()
    key_bot()
    while True:
        queries = load_credentials()
        
        start_time = time.time()
        assets = 0
        peels = 0
        for index, query in enumerate(queries):
            token = ban.login(query=query)
            time.sleep(2)
            get_user = ban.get_user_info(token=token)
            log_system(
                f"{Fore.CYAN + Style.BRIGHT}[ {get_user['data']['username']}]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Peel {get_user['data']['peel']}]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}[ USDT {get_user['data']['usdt']}]{Style.RESET_ALL}"
            )
            assets += get_user['data']['usdt']
            peels += get_user['data']['peel']
            time.sleep(2)
            ban.clear_quest(token=token)
            time.sleep(2)
            ban.get_lottery_info(token=token)
            time.sleep(2)
            ban.get_banana_list(token=token)
            log_system(f"{Fore.WHITE + Style.BRIGHT}=-={Style.RESET_ALL}" * 10)

        end_time = time.time()
        total = delay - (end_time-start_time)
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        log_system(f"[ Total Assets : {assets} USDT | {peels} Peels ]")
        print(f"{Fore.YELLOW + Style.BRIGHT}[ {round(hours)} Hours {round(minutes)} Minutes {round(seconds)} Seconds Remaining To Process All Account ]{Style.RESET_ALL}", end="\r", flush=True)
        time.sleep(total)
        print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log_system(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
    except KeyboardInterrupt:
        sys.exit(0)