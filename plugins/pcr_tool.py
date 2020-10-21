from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio
from pydevtools import debug

import requests
import urllib
from html import unescape
from lxml import html
import os, sys, re
import json
import pytz
from datetime import datetime

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/plugins/"
sys.path.append(o_path)

from utilities import multi_event_handler
from utilities import start_with, text_match, regex_match, with_photo, assert_at, groups_restraint
from utilities import schedule_job
import myconfig

path_prefix="./plugins/"
# path_prefix=""

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

# app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")
app=myconfig.app

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(['查排名'])])    #以关键词开头并需要at bot
def query_rank(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_query_rank_par(message, context)

    name=context['name'] if 'name' in context else None
    if not name :return
    report = get_clan_rank_bigfun(name)

    if isinstance(report, list):
        ret_msg=report
    else:
        ret_msg=[Plain(text=report)]

    # print("ret_msg",ret_msg)

    return ret_msg

#@schedule_job(app, 'cron', day_of_week='*', hour='*', minute='15', second='0', timezone=pytz.timezone("Asia/Shanghai"))
# @schedule_job(app, 'cron', day_of_week='*', hour='*', minute='*', second='*/30', timezone=pytz.timezone("Asia/Shanghai"))
async def rank_every_day():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    timetext=now.strftime('%H:%M:%S')
    msgformat="""【排名定时播报】
"""

    # text=msgformat.format(timetext)
    text=msgformat
    print(text)
    rank_msg=get_clan_rank_bigfun("DSY巫妖兔田魂匣会")
    msg=[Plain(text=text)]+rank_msg


    group_id_list=[1059794476]

    try:
        for group_id in group_id_list:
            await app.sendGroupMessage(group_id, msg)
            # await app.sendGroupMessage(group_id, [Plain(text=f'现在时间 {timetext}')])

    except Exception as e:
        print(e)
        # pass


def _query_rank_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("查排名","").strip()
    
    print("tell stripped_arg", stripped_arg)

    if stripped_arg:
        context['name'] = stripped_arg
    else:
        context['name'] = "DSY巫妖兔田魂匣会"
    return context

def get_clan_rank(name):
    url="https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/name/0"
    data={'history': 0, 'clanName': name}
    headers={
        'Host': 'service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com',
        # 'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Content-Type': 'application/json',
        # 'Origin': 'https://kengxxiao.github.io',
        'Custom-Source': 'KyoukaOfficial',
        'Origin': 'https://kengxxiao.github.io',
        'Referer': 'https://kengxxiao.github.io/Kyouka/',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7'
    }
    data_json = json.dumps(data)
    r=requests.post(url, data_json, headers=headers)
    res=r.text
    print("text","***"+r.text+"***")
    ttt=r.content.decode('utf-8')
    print("content",ttt)

    while res[0]!='{':
        res=res[1:]
    while res[-1]!='}':
        res=res[:-1]
    # print("---"+res+"---")
    res=json.loads(res)
    timestamp=res["ts"]
    timetext=datetime.fromtimestamp(timestamp).astimezone(pytz.timezone('Asia/Shanghai')).strftime('%H:%M:%S')
    # print(res)
    res=res["data"]
    # print(res)
    if len(res)==0:
        return [Plain(text="未查找到该公会")]
    elif len(res)==1:
        res=res[0]
        text=["公会名: ",res["clan_name"],"\n",
        "排名: ",str(res["rank"]),"\n",
        "伤害: ",str(res["damage"]),"\n",
        "会长: ",res["leader_name"],"\n",
        "时间: ",timetext
        ]

        text="".join(text)

        return [Plain(text=text)]

    elif len(res)>1:
        # print(res)
        text_lis=[]
        for res_i in res:
            text_lis.append(res_i["clan_name"]+" | "+str(res_i["rank"])+"\n")
            if len(text_lis)>=10: break
        text="".join(text_lis)
        text=text[:-1]
        if len(res)>10:
            text=text+"\n···"
        text=text+"\n时间: "+timetext


        return [Plain(text="查找到以下公会:\n"),Plain(text=text)]

    # return ret_msg

def get_clan_rank_bigfun(name):
    url="https://www.bigfun.cn/api/feweb"
    params={'target': 'gzlj-search-clan/a', 'name': name}
    headers={
        "Host": "www.bigfun.cn",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
        "x-csrf-token": "djhHVQKW-RowiB-PY36METnO5tMPn3-FvgX0",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.bigfun.cn/tools/pcrteam/search",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7",
        "Cookie": "DedeUserID=1286456; DedeUserID__ckMd5=4e589c0cd289d165; sid=abkel8jj; _csrf=nqbhv5B-4Yyzik1vp3h5BH-L; UM_distinctid=17443267ea0126-09ad0cf725e639-31647305-1aeaa0-17443267ea2b52; finger=351232418; session-api=atteoirfj84hrkjr8s7abpv92m; SESSDATA=99b1e01d%2C1616476371%2C013b7*91; bili_jct=9370395acad166736aa670116dfb5175; CNZZDATA1275376637=136186176-1581524895-https%253A%252F%252Fwww.bigfun.cn%252F%7C1601019668",
    }

    
    # data_json = json.dumps(data)
    r=requests.get(url, headers=headers,params=params)
    res=r.text
    # print("text","***"+r.text+"***")
    # ttt=r.content.decode('utf-8')
    # print("content",ttt)

    # while res[0]!='{':
    #     res=res[1:]
    # while res[-1]!='}':
    #     res=res[:-1]
    # print("---"+res+"---")
    res=json.loads(res)
    print(res)
    # timestamp=res["ts"]
    # timetext=datetime.fromtimestamp(timestamp).astimezone(pytz.timezone('Asia/Shanghai')).strftime('%H:%M:%S')
    # print(res)
    res=res["data"]
    # print(res)
    if not res:
        return [Plain(text="未查找到该公会")]
    elif isinstance(res,dict):
        # res=res[0]
        text=["公会名: ",res["clan_name"],"\n",
        "排名: ",str(res["rank"]),"\n",
        "伤害: ",str(res["damage"]),"\n",
        "会长: ",res["leader_name"],
        ]

        text="".join(text)

        return [Plain(text=text)]

    elif isinstance(res,list):
        # print(res)
        text_lis=[]
        for res_i in res:
            text_lis.append(res_i["clan_name"]+" | "+str(res_i["rank"])+"\n")
            if len(text_lis)>=10: break
        text="".join(text_lis)
        text=text[:-1]
        if len(res)>10:
            text=text+"\n···"
        text=text+"\n时间: "+timetext


        return [Plain(text="查找到以下公会:\n"),Plain(text=text)]

    # return ret_msg


if __name__=="__main__":
    # res=get_clan_rank("DSY兔田欢送会")
    # print(res)
    # res=get_clan_rank("大枫树")
    # print(res)
    # res=get_clan_rank("农场")
    # print(res)



    res=get_clan_rank_bigfun("DSY巫妖兔田魂匣会")
    print(res)
