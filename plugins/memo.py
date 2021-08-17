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
import base64

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/plugins/"
sys.path.append(o_path)

from utilities import multi_event_handler
from utilities import start_with, text_match, regex_match, with_photo, assert_at, groups_restraint
from utilities import schedule_job
from fuzzname import Fuzzname
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

memo_dir=myconfig.memo_dir
memo_index_path=myconfig.memo_index_path
memo_index=myconfig.memo_index
fuz=Fuzzname()

def check_init_memo_index():
    global memo_index
    if not os.path.exists(memo_dir):
        os.makedirs(memo_dir)
    if not os.path.exists(memo_index_path):
        with open(memo_index_path,"w") as fp:
            json.dump({},fp)
    with open(memo_index_path,"r") as fp:
        memo_index=json.load(fp)
    myconfig.memo_index=memo_index
    fuz.fit(memo_index.keys())

check_init_memo_index()

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(["上传 ","upload "])])    #以关键词开头
def memo_upload(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_memo_upload_par(message, context)

    contents=context['contents'] if 'contents' in context else None
    keyword=context['keyword'] if 'keyword' in context else None
    if not keyword:return [Plain(text="关键词为空")]
    if not contents:return [Plain(text="内容为空")]
    
    local_contents = get_local_contents(contents)

    file_path=memo_dir+"/"+keyword+".json"
    with open(file_path,"w") as fp:
        json.dump(local_contents,fp, ensure_ascii=False)
    
    memo_index[keyword]=file_path
    fuz.add(keyword)

    flush_memo_index()

    return [Plain(text="上传成功")]

def _memo_upload_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ' '.join([x.toString() for x in stripped_arg]).strip()  #加空格区分[text][image][text]
    stripped_arg=stripped_arg.replace("upload","",1).replace("上传","",1).strip()
    args=stripped_arg.split(" ")
    args=[x for x in args if x]
    if not args: return context
    keyword=args[0]
    # print("stripped_arg",stripped_arg)
    # print("args",args)

    text_image_contents=[]
    command_flag=False
    keyword_flag=False
    for comp in message:
        if type(comp) == Plain:
            text=comp.toString().strip()
            # 去除指令
            if ("upload" in text or "上传" in text) and not command_flag:
                text=text.replace("upload","",1).replace("上传","",1).strip()
                command_flag=True
            # 去除关键词
            if keyword in text and not keyword_flag:
                text=text.replace(keyword,"",1).strip()
                keyword_flag=True    

            if text:
                text_image_contents.append(("Plain",text))
        elif type(comp) == Image:
            text_image_contents.append(("Image",comp.url))

    
    print("upload contents", text_image_contents)

    if keyword:
        context["keyword"]=keyword
    
    if text_image_contents:
        context["contents"]=text_image_contents
        


    return context

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(["上传撤销 ","upload_delete "])])    #以关键词开头
def memo_upload_delete(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_memo_upload_delete_par(message, context)

    keyword=context['keyword'] if 'keyword' in context else None
    if not keyword:return [Plain(text="关键词为空")]

    if keyword not in memo_index:      
        return [Plain(text="未找到此关键词")]
        
    memo_index.pop(keyword)

    flush_memo_index()

    return [Plain(text="撤销成功")]

def _memo_upload_delete_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("upload_delete","",1).replace("上传撤销","",1).strip()
    if not stripped_arg: return context
    keyword=stripped_arg
  
    print("upload_delete keyword", keyword)

    if keyword:
        context["keyword"]=keyword

    return context

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(["查 ","check_out "])])    #以关键词开头
def memo_get(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_memo_get_par(message, context)

    keyword=context['keyword'] if 'keyword' in context else None
    if not keyword: return [Plain(text="关键词为空")]
    if keyword not in memo_index:
        res=fuz.predict(keyword)
        res="你可能想查 {0}".format(res)
        return [Plain(text="未收录关键词"),Plain(text="，"+res)]
    with open(memo_index[keyword],"r") as fp:
        js_data=json.load(fp)
    ret_msg=local_contents2message_chain(js_data)

    return ret_msg

def _memo_get_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ' '.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("check_out","",1).replace("查","",1).strip()
    args=stripped_arg.split(" ")
    args=[x for x in args if x]
    keyword=args[0]
    
    print("check_out stripped_arg", stripped_arg)
    print("check_out keyword", keyword)

    if keyword:
        context['keyword'] = keyword
    return context


# check_out without command ["查 ","check_out "]
@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=None)    #以关键词开头
def memo_simple_get(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_memo_simple_get_par(message, context)

    keyword=context['keyword'] if 'keyword' in context else None
    if not keyword: return None
    if keyword not in memo_index:
        return None
    if not os.path.exists(memo_index[keyword]):
        del memo_index[keyword]
        flush_memo_index()
        return None
    with open(memo_index[keyword],"r") as fp:
        js_data=json.load(fp)
    ret_msg=local_contents2message_chain(js_data)

    return ret_msg

def _memo_simple_get_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ' '.join([x.toString() for x in stripped_arg]).strip()
    keyword=stripped_arg
    
    #print("check_out2 stripped_arg", stripped_arg)
    #print("check_out2 keyword", keyword)

    if keyword:
        context['keyword'] = keyword
    return context

def get_local_contents(contents):
    res=[]
    for typ, cont in contents:
        if typ=="Plain":
            res.append({typ:cont})
        elif typ=="Image":
            r=requests.get(url=cont)
            base64_data = base64.b64encode(r.content).decode()
            res.append({typ:base64_data})
    return res

def local_contents2message_chain(contents):
    msg=[]
    for item in contents:
        for typ, cont in item.items():
            if typ=="Plain":
                msg.append(Plain(text=cont))
            elif typ=="Image":
                msg.append(Image.fromBase64(cont))       
    return msg



def flush_memo_index():
    global memo_index
    with open(memo_index_path,"w") as fp:
        json.dump(memo_index,fp, ensure_ascii=False)




    




if __name__=="__main__":
    res=get_clan_rank("DSY马家沟挖矿公会")
    print(res)
    res=get_clan_rank("大枫树")
    print(res)
    res=get_clan_rank("农场")
    print(res)