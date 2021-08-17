from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio
from pydevtools import debug

import requests
import urllib
from html import unescape
from lxml import html
import os, sys, re, io
import json
import pytz
from datetime import datetime
import base64
from PIL import Image as PImage
import imghdr

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/plugins/"
sys.path.append(o_path)

from utilities import multi_event_handler
from utilities import start_with, text_match, regex_match, with_photo, assert_at, groups_restraint
from utilities import schedule_job
from fuzzname import Fuzzname
import myconfig
from upload_cloud import Cloud

path_prefix="./plugins/"
# path_prefix=""

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

# app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")
app=myconfig.app

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list
group_pic_collect_list=myconfig.group_pic_collect_list

repo_link=myconfig.repo_link
repo_upload_link=myconfig.repo_upload_link
repo_download_link=myconfig.repo_download_link
cloud=Cloud(repo_link, repo_upload_link, repo_download_link)


@multi_event_handler(app, ["GroupMessage"], filter=None)    #以关键词开头
def pic_collector(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    

    group_id=context["group"].id
    if group_id not in group_pic_collect_list: return []

    context=_pic_collector_par(message, context)

    images=context['images'] if 'images' in context else None
    if not images:return []
    

    for url in images:
        r=requests.get(url=url)
        buffer=r.content
        width, height=get_shape(buffer)
        if width*height>=1080*720:
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            date_str=now.strftime('%Y%m%d')
            date_time_str=now.strftime("%Y%m%d-%H%M%S")

            fp=io.BytesIO(buffer)
            ext=imghdr.what(None, buffer)
            fp.name="{0}.{1}".format(date_time_str, ext)

            rel_path="{0}/{1}/".format(group_id, date_str)

            result=cloud.upload(file_like=fp, rel_path=rel_path)
            print(result)

    return []

def _pic_collector_par(message, context):

    images_msg = message.getAllofComponent(Image)
    images=[x.url for x in images_msg]
    
    print("images list", images)

    context['images']=images

    return context

@multi_event_handler(app, ["GroupMessage"], filter=[text_match(["图库","pictures"])])    #以关键词匹配
def pic_download_link(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    group_id=context["group"].id
    if group_id not in group_pic_collect_list: return []
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    date_str=now.strftime('%Y%m%d')

    download_link="{0}?p=%2F{1}%2F{2}&mode=grid".format(cloud.repo_download_link, group_id, date_str)

    return [Plain(text=download_link)]

def get_shape(buffer):
    im=PImage.open(io.BytesIO(buffer))
    return im.size


if __name__=="__main__":
    pass