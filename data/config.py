# api id, hash
API_ID = 1488
API_HASH = 'abcde1488'

DELAYS = {
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
    'PREDICT': [5, 8],   # delay after prediction
    'TASK': [2, 3],     # delay after completed a task
    'REPEAT': [100, 180]
}

# Is it need to buy this https://t.me/ApeCryptoChat/26060 booster
BOOST_TURBO_CHARGER = True

BLACKLIST_TASKS = ['Connect Telegram and complete identity verification', 'Подключите Telegram и пройдите верификацию личности', 'Подключение TON к кошельку OKX']

PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": "socks5",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "socks5"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}
# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

SOFT_INFO = f"""{"OKX Racer".center(40)}
Soft for https://t.me/OKX_official_bot
{"Functional:".center(40)}
register accounts in web app; make random prediction;
complete tasks; active booster "Reload Fuel Tank";
upgrade booster "Turbo Charger"

The soft also collects statistics on accounts and uses proxies from {f"the {PROXY['PROXY_PATH']} file" if PROXY['USE_PROXY_FROM_FILE'] else "the accounts.json file"}
To buy this soft with the option to set your referral link write me: https://t.me/Axcent_ape
"""
