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
from datetime import datetime, timedelta

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/plugins/"
sys.path.append(o_path)

from utilities import multi_event_handler
from utilities import start_with, text_match, regex_match, with_photo, assert_at, groups_restraint
from utilities import schedule_job
from parse_duration import parse_duration
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

def apply_filters(message, context, filter):
    if filter is None: return
    if isinstance(filter, list): filters=filter
    else: filters=[filter]

    for fit in filters:
        if not fit(message, context): 
            # print(fit)
            raise Cancelled

@app.receiver("GroupMessage")
async def recall(app: Mirai, group: Group, member: Member, message: MessageChain):
    # print(message)

    # print("IN~~~~~~~~~~~~")
    context={'app': app, 'group': group, 'member':member, 'event_type': "GroupMessage"}

    filter=[text_match(['撤回', 'recall']),assert_at()]
    apply_filters(message, context, filter)

    # print("MID~~~~~~~~~~~~")

    context=_recall_par(message, context)

    msglog=myconfig.msglog

    group_id=group.id


    try:
        
        msg_id=msglog["group"][group_id][-1]

        ret = await app.revokeMessage(msg_id)

        text="撤回"+("成功" if ret else "失败")

    except Exception as e:
        print(e)
        text="撤回" + "失败"
        ret=False

    if ret:
        del msglog["group"][group_id][-1]

    msg = [Plain(text=text)]

    await app.sendGroupMessage(group, msg)


def _recall_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.lower()
    stripped_arg=stripped_arg.replace("撤回","",1).replace("recall","",1).strip()
    
    print("recall stripped_arg", stripped_arg)

    if stripped_arg:
        args=stripped_arg.split()
        args=[x for x in args if x]
        if len(args)==1:
            pass
        else:
            pass

    return context


if __name__=="__main__":
    pass
