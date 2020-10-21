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

sanity_data_path=myconfig.sanity_data_path

def dump_sanity_data(sanity_data):
    
    with open(sanity_data_path,"w") as fp:
        json.dump(sanity_data,fp)

def load_sanity_data():
    if not os.path.exists(sanity_data_path):
        dump_sanity_data({})
    with open(sanity_data_path,"r") as fp:
        sanity_data=json.load(fp)
        return sanity_data

sanity_data=load_sanity_data()

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(['体力 ', 'sanity ']),assert_at()])    #以关键词开头并需要at bot
def sanity_alert(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_sanity_alert_par(message, context)

    typ=context['type'] if 'type' in context else None
    if not typ :return

    person_id=context['friend'].id if context['event_type']=="FriendMessage" else context['member'].id
    person_id=str(person_id)

    if typ=="set":
        if person_id not in sanity_data:
            sanity_data[person_id]={}
        
        sanity_data[person_id]['volume']=context['volume']
        sanity_data[person_id]['interval']=context['interval']
        sanity_data[person_id]['job_id']=None

        dump_sanity_data(sanity_data)

        ret_msg=[Plain(text="设置成功")]

    elif typ=="log":
        if person_id not in sanity_data:
            ret_msg=[Plain(text="请先进行设置(体力 设置 132(体力上限) 6min(体力自回时间))")]
        else:
            rest_time=(sanity_data[person_id]['volume']-context['current'])*sanity_data[person_id]['interval']
            msg=[Plain(text="体力满了！")]
            job_id="sanity%s"%person_id
            remove_job(sanity_data[person_id]['job_id'])
            job_id, target_time=delayed_message(msg, context, rest_time)
            sanity_data[person_id]['job_id']=job_id
            dump_sanity_data(sanity_data)

            ret_msg=[Plain(text="更新成功，预测时间{0}".format(target_time.strftime('%Y-%m-%d %H:%M:%S')))]
    elif typ=="cancel":
            if sanity_data[person_id]['job_id'] is not None:
                remove_job(sanity_data[person_id]['job_id'])
                sanity_data[person_id]['job_id']=None
            ret_msg=[Plain(text="取消成功")]
    else:
        return

    if isinstance(ret_msg, list):
        ret_msg=ret_msg
    else:
        ret_msg=[Plain(text=ret_msg)]

    # print("ret_msg",ret_msg)

    return ret_msg

def _sanity_alert_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.lower()
    stripped_arg=stripped_arg.replace("体力","",1).replace("sanity","",1).strip()
    
    print("sanity stripped_arg", stripped_arg)

    if stripped_arg:
        args=stripped_arg.split()
        args=[x for x in args if x]
        if len(args)==3 and (args[0]=="set" or args[0]=="设置"):
            context['type']="set"
            context['volume']=int(args[1])
            context['interval']=parse_duration(args[2])
        elif len(args)>=1 and (args[0]=="cancel" or args[0]=="取消"):
            context['type']="cancel"
        elif len(args)>=1:
            context['type']="log"
            context['current']=int(args[0])
        else:
            pass
    return context


def delayed_message(msg, context, rest_time):    # rest_time:int seconds
    def gen_func():
        async def func_friend():

            friend=context['friend']
            await app.sendFriendMessage(friend, msg)

        async def func_group():

            group=context['group']
            member=context['member']
            new_msg=[At(target=member.id)]+msg
            await app.sendGroupMessage(group, new_msg)

        async def func_temp():

            group=context['group']
            member=context['member']
            await app.sendTempMessage(group, member.id, msg)

        if context['event_type']=="FriendMessage":
            return func_friend
        elif context['event_type']=="GroupMessage":
            return func_temp
        elif context['event_type']=="TempMessage":
            return func_temp
        else:
            return None


    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    delta = timedelta(days=0, seconds=rest_time, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    target_time=now+delta

    func=gen_func()

    if func is None:return None

    person_id=context['friend'].id if context['event_type']=="FriendMessage" else context['member'].id

    scheduler=myconfig.scheduler
    job_id="sanity%d"%person_id
    scheduler.add_job(func=func,id=job_id, next_run_time=target_time)

    return job_id, target_time


def remove_job(job_id):
    scheduler=myconfig.scheduler
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    return True

if __name__=="__main__":
    pass
