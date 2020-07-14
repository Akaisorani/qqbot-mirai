from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio
from pydevtools import debug

import requests
import urllib
from html import unescape
from lxml import html
import os, sys, re
import json

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/plugins/"
sys.path.append(o_path)

from utilities import multi_event_handler
from utilities import start_with, text_match, regex_match, with_photo, assert_at, groups_restraint
import myconfig

path_prefix="./plugins/"
# path_prefix=""

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(['查排名'])])    #以关键词开头并需要at bot
def query_rank(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_query_rank_par(message, context)

    name=context['name'] if 'name' in context else None
    if not name :return
    report = get_clan_rank(name)

    if isinstance(report, list):
        ret_msg=report
    else:
        ret_msg=[Plain(text=report)]

    # print("ret_msg",ret_msg)

    return ret_msg

def _query_rank_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("查排名","").strip()
    
    print("tell stripped_arg", stripped_arg)

    if stripped_arg:
        context['name'] = stripped_arg
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
        'Referer': 'https://kengxxiao.github.io/Kyouka/',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7'
    }
    data_json = json.dumps(data)
    r=requests.post(url, data_json, headers=headers)
    res=r.text
    # print("text","***"+r.text+"***")
    # ttt=r.content.decode('utf-8')
    # print("content",ttt)

    while res[0]!='{':
        res=res[1:]
    while res[-1]!='}':
        res=res[:-1]
    # print("---"+res+"---")
    res=json.loads(res)
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
        "会长: ",res["leader_name"]
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


        return [Plain(text="查找到以下公会:\n"),Plain(text=text)]

    # return ret_msg


if __name__=="__main__":
    res=get_clan_rank("DSY马家沟挖矿公会")
    print(res)
    res=get_clan_rank("大枫树")
    print(res)
    res=get_clan_rank("农场")
    print(res)