from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio

from datetime import datetime, timedelta
import pytz
import os, sys
import requests
import pixiv_crawler as pc
from pixiv_setu import Pixivsetu
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/plugins/"
sys.path.append(o_path)

from tuchuang import Jd_tuchuang
from utilities import schedule_job
import myconfig

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

# app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")
app=myconfig.app

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list

path_prefix="./plugins/"

pixiv_setu=Pixivsetu()
import time

# @app.onStage("start")
# @schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*', second='*/30', timezone=pytz.timezone("Asia/Shanghai"))
# @schedule_job(app, 'cron', day_of_week='*', hour='5-23/6', minute='55', second='0', timezone=pytz.timezone("Asia/Shanghai"))
async def hourcall():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    timetext=now.strftime('%H:%M:%S')
    msgformat="""【提醒买药小助手】
{0}
大家好，我是本群的“提醒买药小助手”，希望看到消息的人可以放下手中的其他事情打开PCR去买药吧。6小时后我会继续提醒大家去买药，和我一起成为每天买四次药的人吧。
附一张setu
"""

    try:
        setu_msg=pixiv_setu.get_setu("normalrank")
    except Exception as e:
        print(e)
        setu_msg=[Plain(text="没有找到色图")]

    text=msgformat.format(timetext)
    print(text)
    msg=[Plain(text=text)]+setu_msg


    group_id_list=myconfig.group_medi_id_list

    try:
        for group_id in group_id_list:
            await app.sendGroupMessage(group_id, msg)
            # await app.sendGroupMessage(group_id, [Plain(text=f'现在时间 {timetext}')])

    except Exception as e:
        print(e)
        # pass

# @schedule_job('cron', day_of_week='*', hour='*', minute='*', second='*/10', timezone=pytz.timezone("Asia/Shanghai"))
async def job():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    print(now.strftime('%H:%M:%S'))

async def print_time():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    print(now.strftime('%H:%M:%S'))    


# @schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*', second='*/30', timezone=pytz.timezone("Asia/Shanghai"))
# @schedule_job(app, 'cron', day_of_week='*', hour='12', minute='0', second='0', timezone=pytz.timezone("Asia/Shanghai"))
async def mrfz_cake():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    timetext=now.strftime('%H:%M:%S')

    url="https://z3.ax1x.com/2021/04/26/gSEHd1.jpg"
    r=requests.get(url,timeout=30)
    buffer=r.content

    msg=[Image.fromBytes(buffer)]

    group_id_list=myconfig.group_mrfz_cake_id_list

    try:
        for group_id in group_id_list:
            await app.sendGroupMessage(group_id, msg)
            # await app.sendGroupMessage(group_id, [Plain(text=f'现在时间 {timetext}')])

    except Exception as e:
        print(e)
        # pass

# @schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*', second='*/20', timezone=pytz.timezone("Asia/Shanghai"))
@schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*/5', second='0', timezone=pytz.timezone("Asia/Shanghai"))
async def heartbeat():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    timetext=now.strftime('%H:%M:%S')

    msg=[Plain(text=timetext)]

    group_id_list=myconfig.group_heartbeat_list

    try:
        for group_id in group_id_list:
            await app.sendGroupMessage(group_id, msg)
            # await app.sendGroupMessage(group_id, [Plain(text=f'现在时间 {timetext}')])

    except Exception as e:
        print(e)
        print("heartbeat fail, going to kill mirai")
        os.system("ps -aux|grep '/opt/java/jdk1.8.0_144/bin/java -jar mirai-console-wrapper-1.3.0.jar' |grep -v grep | awk '{print $2}' | xargs kill -9")
        # pass


# from apscheduler.schedulers.blocking import BlockingScheduler

if __name__=="__main__":
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
    

