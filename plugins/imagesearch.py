from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment

import os, sys
import requests
from lxml import html

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/akaisora/plugins/"
sys.path.append(o_path)

from tuchuang import Jd_tuchuang

path_prefix="./akaisora/plugins/"

# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
@on_command('search', aliases=("搜图",), only_to_me=True)
async def imagesearch(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    # tags = session.get('tags', prompt='输入tag列表，空格隔开')
    # 获取城市的天气预报
    images=session.state['images'] if 'images' in session.state else None
    if not images:return
    img_url = await searchimg(images=images)
    if not img_url: return
    await session.send(img_url)

# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@imagesearch.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    images_arg=session.current_arg_images
    
    print("stripped_arg", stripped_arg)
    print("images_arg", images_arg)
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['tags'] = stripped_arg
        if images_arg:
            session.state['images'] = images_arg
        return



async def searchimg(images) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    try:
        report=imagesearch.search_iqdb(images[0])
    except Exception as e:
        print(e)
        report="error"
    if not report: report="未找到"
    
    return report

class Imagesearch(object):
    def __init__(self):
        pass

    def get_img_from_url(self, url):
        pass

    def search_iqdb(self, url):
        iqdb_root="http://iqdb.org/"

        session=requests.session()
        # r=session.get(iqdb_root)

        payload={
            'url':url
        }
        r=session.post(
            iqdb_root,
            data=payload,
            headers=dict(referer=iqdb_root)
        )
        tree=html.fromstring(r.text)
        res=tree.xpath("//div[@id='pages']/div[@class='nomatch']")
        if res:
            return None
        res=tree.xpath("//div[@id='pages']/div[2]/table/tr/td[@class='image']/a/@href")[0]
        # print(html.tostring(res))
        # res=tree.xpath("//div[@id='pages']/div[2]/table/tbody/tr/td[@class='image']/a[@href]")
        if res[:4]!="http":
            res="http:"+res
        return res





        
imagesearch=Imagesearch()



if __name__=="__main__":
    url="https://gchat.qpic.cn/gchatpic_new/185597551/3941790644-2209752403-06704C9140C2FF29A94C1F11AA4D7CF5/0?vuin=2473990407&amp;amp;term=2"
    url="http://iqdb.org/konachan/f/6/7/f6785b10df399fff3c239475bdbf59d3.jpg"
    res=imagesearch.search_iqdb(url)
    print(res)

    
    

