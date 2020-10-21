from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio
from pydevtools import debug

import os, sys
import requests
import pixiv_crawler as pc

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/akaisora/plugins/"
sys.path.append(o_path)

from utilities import multi_event_handler
from utilities import start_with, text_match, regex_match, with_photo, assert_at, groups_restraint
import myconfig

from tuchuang import Jd_tuchuang
from pixiv_setu import Pixivsetu

path_prefix="./akaisora/plugins/"

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

# app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")
app=myconfig.app

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list


@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(['setu',"给我一张色图","给我一份色图","色图 "])])    #以关键词开头
def setu(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_setu_par(message, context)

    tags=context['tags'] if 'tags' in context else None
    report = get_setu(tags=tags)
    if not report: return

    if isinstance(report, list):
        ret_msg=report
    else:
        ret_msg=[Plain(text=report)]

    return ret_msg

def _setu_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("setu","",1).replace("给我一张色图","",1).replace("给我一份色图","",1).replace("色图 ","",1).strip()
    
    print("setu stripped_arg", stripped_arg)

    if stripped_arg:
        context['tags'] = stripped_arg
    return context

def get_setu(tags):
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    try:
        report=pixiv_setu.get_setu(tags)
    except Exception as e:
        print(e)
        report="没有找到色图"
    
    return report


pixiv_setu=Pixivsetu()

if __name__=="__main__":
    # img_url=pixiv_setu.get_setu("德克萨斯")
    img_url=pixiv_setu.get_setu()
    print(img_url)
    
    

