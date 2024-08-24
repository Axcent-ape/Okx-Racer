import json
import random
import time
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import asyncio
from urllib.parse import unquote, parse_qs
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector


class OKXRacer:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.account_info = None
        self.rn = 'linkCode_95213168'
        self.thread = thread
        self.proxy = f"{ config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {
            'User-Agent': UserAgent(os='android').random,
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,bg;q=0.6,mk;q=0.5',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Origin': 'https://www.okx.com',
            'Referer': 'https://www.okx.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-mobile': '?1',
            'Sec-Ch-Ua-platform': '"Android"',
        }
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def stats(self):
        await self.login()

        json_data = {"extUserName": self.account_info['user_name'], "linkCode": self.rn.split('_')[1]}
        r = await (await self.session.post(f"https://www.okx.com/priapi/v1/affiliate/game/racer/info?t={int(time.time()*1000)}", json=json_data)).json()

        balance = r.get('data').get('balancePoints')
        referral_link = 'https://t.me/OKX_official_bot/OKX_Racer?startapp=linkCode_' + r.get('data').get('linkCode')

        r = await (await self.session.get(f"https://www.okx.com/priapi/v1/affiliate/game/racer/leaderboard/global?pageNo=1&t={int(time.time() * 1000)}", json=json_data)).json()
        rank = r.get('data').get('userRanking').get('rank')

        r = await (await self.session.get(f"https://www.okx.com/priapi/v1/affiliate/game/racer/invitee-list?pageNo=1&t={int(time.time() * 1000)}", json=json_data)).json()
        referrals = r.get('data').get('total')

        r = await (await self.session.post(f"https://www.okx.com/priapi/v1/affiliate/game/racer/account-binding?t={int(time.time() * 1000)}", json={"isRecheckBinding": False})).json()
        kyc_link = r.get('data').get('verifyKycLink')
        bind_tg = r.get('data').get('bindTgLink')

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, str(balance), str(rank), str(referrals), referral_link, proxy, kyc_link, bind_tg]


    async def info(self):
        json_data = {"extUserName": self.account_info['user_name'], "linkCode": self.rn.split('_')[1]}
        resp = await self.session.post(f"https://www.okx.com/priapi/v1/affiliate/game/racer/info?t={int(time.time()*1000)}", json=json_data)

        return (await resp.json()).get('data')

    async def assess(self, predict: int):
        json_data = {'predict': predict}

        resp = await self.session.post(f"https://www.okx.com/priapi/v1/affiliate/game/racer/assess?t={int(time.time()*1000)}", json=json_data)
        return (await resp.json()).get('data')

    async def boosts(self):
        resp = await self.session.get(f"https://www.okx.com/priapi/v1/affiliate/game/racer/boosts?t={int(time.time() * 1000)}")
        return (await resp.json()).get('data')

    async def active_boost(self, boost_id: int):
        json_data = {"id": boost_id}

        resp = await self.session.post(f"https://www.okx.com/priapi/v1/affiliate/game/racer/boost?t={int(time.time() * 1000)}", json=json_data)
        r = await resp.json()
        return r.get('data') == {} and r.get('code') == 0

    async def get_tasks(self, task_group: bool = False):
        resp = await self.session.get(f"https://www.okx.com/priapi/v1/affiliate/game/racer/group-tasks?t={int(time.time() * 1000)}")
        r = (await resp.json()).get('data')

        tasks = r.get('ungroupedTasks')
        for task_group in r.get('taskGroups'):
            tasks += task_group['tasks']

        return tasks

    async def complete_task(self, task_id: int):
        json_data = {'id': task_id}
        resp = await self.session.post(f'https://www.okx.com/priapi/v1/affiliate/game/racer/task?t={int(time.time() * 1000)}', json=json_data)

        r = await resp.json()
        return r.get('data') == {} and r.get('code') == 0

    async def logout(self):
        await self.session.close()

    async def login(self):
        self.rn = self.rn.split('_')[0] + '_95213168'
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None

        self.session.headers['X-Telegram-Init-Data'] = query

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('OKX_official_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('OKX_official_bot'), short_name="OKX_Racer"),
                platform='android',
                write_allowed=True,
                start_param=self.rn
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            user_data = json.loads(unquote(parse_qs(unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))['user'][0]))
            self.account_info = {'id': user_data['id'], 'user_name': user_data['first_name'] + (user_data['last_name'] if user_data['last_name'] else ' ')}

            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query

        except:
            return None
