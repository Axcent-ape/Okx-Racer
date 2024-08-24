import os
import random

from utils.racer import OKXRacer
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    racer = OKXRacer(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await racer.login()

    while True:
        try:
            info_data = await racer.info()
            if info_data.get('context').get('isShowNewbieCredit'):
                logger.success(f"Thread {thread} | {account} | Register")

            for task in await racer.get_tasks():
                if task['context']['name'] in config.BLACKLIST_TASKS or task['state']:
                    continue
                if await racer.complete_task(task['id']):
                    logger.success(f"Thread {thread} | {account} | Completed task «{task['context']['name']}» and got {task['points']} points")
                else:
                    logger.warning(f"Thread {thread} | {account} | Couldn't complete task «{task['context']['name']}»")

                await asyncio.sleep(random.uniform(*config.DELAYS['TASK']))

            num_chances = info_data.get('numChances')
            balance = info_data.get('balancePoints')

            boosts = await racer.boosts()
            while boosts[3]['totalStage'] > boosts[3]['curStage'] and boosts[3]['pointCost'] <= balance and config.BOOST_TURBO_CHARGER:
                if await racer.active_boost(3):
                    logger.success(f"Thread {thread} | {account} | Upgrade booster «Turbo Charger» for {boosts[3]['pointCost']} points!")

                    balance -= boosts[3]['pointCost']
                    boosts = await racer.boosts()
                    await asyncio.sleep(1)

            while num_chances:
                predict = random.randint(0, 1)
                assess_data = await racer.assess(predict)
                balance = assess_data.get('balancePoints')

                if assess_data:
                    log = f"Thread {thread} | {account} | {'Won' if assess_data.get('won') else 'Lost'} and chose a prediction {'DOOM' if predict else 'MOON'}! Reward: {assess_data.get('basePoint') * assess_data.get('curCombo')}; Balance: {assess_data.get('balancePoints')}"
                    logger.success(log) if assess_data.get('won') else logger.warning(log)

                else:
                    logger.error(f"Thread {thread} | {account} | Prediction selection error!")

                num_chances -= 1
                await asyncio.sleep(random.uniform(*config.DELAYS['PREDICT']))

            boosts = await racer.boosts()
            sleep = random.uniform(*config.DELAYS['REPEAT'])
            if num_chances == 0 and boosts[1]['totalStage'] > boosts[1]['curStage']:
                if await racer.active_boost(1):
                    sleep = 0
                    logger.success(f"Thread {thread} | {account} | Activate booster «Reload Fuel Tank»")

            if sleep:
                logger.info(f"Thread {thread} | {account} | Sleep {round(sleep, 1)} seconds!")
            await asyncio.sleep(sleep)

        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(5)

    await racer.logout()


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(OKXRacer(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Balance', 'Rank', 'Referrals', 'Referral link', 'Proxy (login:password@ip:port)', 'Verify Kyc Link', 'Bind Tg Link']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")