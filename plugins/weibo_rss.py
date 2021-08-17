from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio

import requests
import urllib
from html import unescape
from lxml import html, etree
import os, sys, re
import json
import pytz
from datetime import datetime, timedelta
from io import BytesIO
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/plugins/"
sys.path.append(o_path)

from utilities import schedule_job
import myconfig
# from recom_tags import get_bytes_image_from_url

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

# app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")
app=myconfig.app

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list

path_prefix="./plugins/"

weibo_item_list=[]
max_annon_id=0

import time

# @app.onStage("start")
@schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*/5', second='25', timezone=pytz.timezone("Asia/Shanghai"))
# @schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*', second='*/10', timezone=pytz.timezone("Asia/Shanghai"))
async def mrfz_weibo_broadcast():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    # timetext=now.strftime('%H:%M:%S')

    try:
        msg_lis=get_new_mrfz_weibos()
    except Exception as e:
        print(e)
        traceback.print_exc()
        msg_lis=[]
        # setu_msg=[Plain(text="没有找到色图")]

    if not msg_lis: return
    # print(msg_lis)
    
    group_id_list=myconfig.group_mrfz_weibo_id_list

    # print(msg_lis)
    try:
        for msg in msg_lis:
            for group_id in group_id_list:
                await app.sendGroupMessage(group_id, msg)
                # await app.sendGroupMessage(group_id, [Plain(text=f'现在时间 {timetext}')])

    except Exception as e:
        print(e)
        traceback.print_exc()
        # pass

# @app.onStage("start")
# @schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*/5', second='30', timezone=pytz.timezone("Asia/Shanghai"))
# @schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*', second='*/10', timezone=pytz.timezone("Asia/Shanghai"))
async def mrfz_annon_broadcast():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    # timetext=now.strftime('%H:%M:%S')

    try:
        msg_lis=get_new_mrfz_announcement()
    except Exception as e:
        print(e)
        traceback.print_exc()
        msg_lis=[]
        # setu_msg=[Plain(text="没有找到色图")]

    if not msg_lis: return
    # print(msg_lis)
    
    group_id_list=myconfig.group_mrfz_weibo_id_list

    try:
        for msg in msg_lis:
            for group_id in group_id_list:
                await app.sendGroupMessage(group_id, msg)
                # await app.sendGroupMessage(group_id, [Plain(text=f'现在时间 {timetext}')])

    except Exception as e:
        print(e)
        traceback.print_exc()
        # pass

def load_weibo_list():
    global weibo_item_list
    filename="./plugins/weibo_item_list.json"
    if not os.path.exists(filename):
        weibo_item_list=[]
        dump_weibo_list()

    with open(filename,"r") as fp:
        weibo_item_list=json.load(fp)

def dump_weibo_list():
    global weibo_item_list
    filename="./plugins/weibo_item_list.json"
    with open(filename,"w") as fp:
        json.dump(weibo_item_list, fp)



def get_bytes_image_from_url(url):
    r=requests.get(url,timeout=30)
    buffer=r.content
    return buffer

def get_new_mrfz_weibos():
    # rss_url="https://rsshub.app/weibo/user/6279793937/"
    rss_url="https://rssfeed.today/weibo/rss/6279793937"
    r=requests.get(rss_url)
    # tree=etree.fromstring(r.text)
    # print(r.text)
    if "如果您认为 RSSHub 导致了该错误" in r.text:
        return []
    try:
        tree=etree.parse(BytesIO(r.content))
    except Exception as e:
        traceback.print_exc()
        print(r.text)
        return []

    item_lis=tree.xpath("//item")
    msg_lis=[]

    for item in item_lis:
        link=item.xpath("./link/text()")[0]
        pub_date=item.xpath("./pubDate/text()")[0]
        description=item.xpath("./description/text()")[0]
        
        utc_time=datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
        time=utc_time.replace(tzinfo = pytz.timezone('GMT')).astimezone(pytz.timezone('Asia/Shanghai'))
        converted_time=time.strftime("%Y-%m-%d %H:%M:%S %z")
        


        if link in weibo_item_list: continue

        print(link)
        print(pub_date)
        print(description)
        

        msg_content_lis=rsshub_weibo_html2list(description)

        msg=msg_content_lis+\
                [Plain(text="\n发布时间："), Plain(text=converted_time), Plain(text="\n")]+\
                [Plain(text="原始链接："), Plain(text=link)]

        weibo_item_list.append(link)
        dump_weibo_list()
        # print(msg_lis)
        if utc_time<datetime.now()-timedelta(weeks=1): continue
        msg_lis.append(msg)

    return msg_lis


def rsshub_weibo_html2list(htmltext):
    htmltext=htmltext.replace("<br />","<br/>").replace("<br/><br/>","<br/>").replace("<br><br>","<br>")
    tree=html.fromstring(htmltext)
    lis=tree.xpath("node()")
    # res_lis=[]
    msg_lis=[]
    for x in lis:
        if isinstance(x,str):
            msg_lis.append(Plain(text=x))
        else:
            if x.tag=="a":
                msg_lis.append(Plain(text="".join(x.xpath(".//text()"))))
                if x.xpath("./img"):
                    img=x.xpath("./img")[0]
                    bytes_image=get_bytes_image_from_url(img.xpath("./@src")[0])
                    msg_lis.append(Image.fromBytes(bytes_image))
            if x.tag=="br":
                msg_lis.append(Plain(text="\n"))
            if x.tag=="img":
                bytes_image=get_bytes_image_from_url(x.xpath("./@src")[0])
                msg_lis.append(Image.fromBytes(bytes_image))

    # print(res_lis)
    return msg_lis


def get_mrfz_announcement():
    url="https://ak-fs.hypergryph.com/announce/IOS/announcement.meta.json"
    r=requests.get(url)
    if r.status_code==200:
        res=r.json()
    else:
        res=None
    return res

def get_new_mrfz_announcement():
    global max_annon_id
    annon_list=get_mrfz_announcement()
    if annon_list is None: return None
    annon_list=annon_list["announceList"]
    annon_list.sort(key=lambda x:int(x["announceId"]))
    msg_lis=[]
    for annon in annon_list:
        if int(annon["announceId"])<=max_annon_id: continue

        msg_content_lis=[Plain(text="【游戏公告】\n")]+[Plain(text=annon["title"]+"\n")]+[Plain(text=annon["webUrl"])]

        msg=msg_content_lis

        max_annon_id=max(max_annon_id,int(annon["announceId"]))
        dump_annon_id()
        # print(msg_lis)
        msg_lis.append(msg)
    return msg_lis


def load_annon_id():
    global max_annon_id
    filename="./plugins/mrfz_announce_id.json"
    if not os.path.exists(filename):
        max_annon_id=[]
        dump_annon_id()

    with open(filename,"r") as fp:
        max_annon_id=json.load(fp)

def dump_annon_id():
    global max_annon_id
    filename="./plugins/mrfz_announce_id.json"
    with open(filename,"w") as fp:
        json.dump(max_annon_id, fp)


load_weibo_list()
load_annon_id()


if __name__=="__main__":
    get_new_mrfz_weibos()


if __name__=="__main__" and False:
    # img_url=pixiv_setu.get_setu("德克萨斯")
    # img_url=pixiv_setu.get_setu()
    # print(img_url)

    # BackgroundScheduler: 适合于要求任何在程序后台运行的情况，当希望调度器在应用后台执行时使用
    # scheduler = BackgroundScheduler()
    # scheduler = BlockingScheduler()
    scheduler = AsyncIOScheduler()
    # 采用corn的方式
    # scheduler.add_job(job, 'cron', day_of_week='*', hour='*', minute='*', second='*/10', timezone=pytz.timezone("Asia/Shanghai"))
    # scheduler.add_job(hourcall, 'cron', day_of_week='*', hour='*', minute='*', second='*/10', timezone=pytz.timezone("Asia/Shanghai"))

    now = datetime.now()
    delta = timedelta(days=0, seconds=5, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    # scheduler.add_job(print_time, "interval", seconds=4, id="test1", max_instances=1, end_date=now+delta)
    scheduler.start()
    scheduler.add_job(func=print_time,id="test1", next_run_time=now+delta)
    # scheduler.remove_job("test1")

    '''
    year (int|str) – 4-digit year
    month (int|str) – month (1-12)
    day (int|str) – day of the (1-31)
    week (int|str) – ISO week (1-53)
    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    hour (int|str) – hour (0-23)
    minute (int|str) – minute (0-59)
    econd (int|str) – second (0-59)
            
    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
    end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)
        
    *    any    Fire on every value
    */a    any    Fire every a values, starting from the minimum
    a-b    any    Fire on any value within the a-b range (a must be smaller than b)
    a-b/c    any    Fire every c values within the a-b range
    xth y    day    Fire on the x -th occurrence of weekday y within the month
    last x    day    Fire on the last occurrence of weekday x within the month
    last    day    Fire on the last day within the month
    x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions
    '''

    

    print("asf")
    # time.sleep(30)
    asyncio.get_event_loop().run_forever()
    # app.run()
    print("ghj")

    pass