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

def rsshub_weibo_html2list(htmltext):
    tree=html.fromstring(htmltext)
    lis=tree.xpath("node()")
    res_lis=[]
    for x in lis:
        if isinstance(x,str):
            res_lis.append(["text",x])
        else:
            if x.tag=="a":
                res_lis.append(["text","".join(x.xpath(".//text()"))])
            if x.tag=="br":
                res_lis.append(["text","\n"])
            if x.tag=="img":
                res_lis.append(["image","".join(x.xpath("./@src"))])



    print(res_lis)
    return res_lis
    # print(lis)











if __name__=="__main__":
    ss="""<a href="https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E6%98%8E%E6%97%A5%E6%96%B9%E8%88%9F%23&isnewpage=1" data-hide><span class="surl-text">#明日方舟#</span></a> 01月05日16:00闪断更新公告 <br><br>感谢您对《明日方舟》的关注与支持。《明日方舟》计划将于2021年01月05日16:00 ~ 16:10 期间进行服务器闪断更新。届时将造成玩家强制掉线，无法登录等问题。 为确保您的游戏内帐号数据正常，请在本次闪断更新时提前结束关卡。本次更新给各位玩家带来的不便，敬请谅解！<br><br>闪断更新时间：<br>2021年01月05日16:00 ~ 16:10 期间<br><br>更新内容：<br>◆故事集「此地之外」限时活动开放<br>◆「此地之外」详细活动内容请参照官方相关活动公告<br>◆01月07日04:00【标准寻访】更新资源预载<br>◆01月07日04:00【采购中心-高级凭证区】更新资源预载<br><br>闪断补偿：<br>合成玉*200<br>补偿范围：<br>2021年01月05日16:00更新前所有注册并创建角色的玩家（含游客账号）<br><br>*本次维护不排除延迟开启的可能，如若延迟则请关注官方发布的具体开服时间*<img style src="https://wx2.sinaimg.cn/large/006QZngZgy1gmcmqx1v38j30rs23gtzw.jpg" referrerpolicy="no-referrer"><br><br>"""
    rsshub_weibo_html2list(ss)