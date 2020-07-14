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

from apikeys import *
from fuzzname import Fuzzname
from ocr_tool import Ocr_tool
from material import Material
from record import Record

path_prefix="./plugins/"
# path_prefix=""

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list

# """
@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=None)
def tagrc(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    # parse message
    context = _tagrc_par(message, context)
    # print("context",context)
    tags=context['tags'] if 'tags' in context else None
    images=context['images'] if 'images' in context else None

    if not tags and not images:return
    # 获取城市的天气预报
    tagrc_report = get_recomm_tags(tags=tags,images=images)
    if tagrc_report is None: return 
    # 向用户发送天气预报

    ret_msg=[Plain(text=tagrc_report)]

    return ret_msg

def _tagrc_par(message, context):
    # 去掉消息首尾的空白符
    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()

    images_arg = message.getFirstComponent(Image)
    
    print("stripped_arg", stripped_arg)
    print("images_arg", images_arg)
    if stripped_arg:
        context['tags'] = stripped_arg
    elif images_arg:
        context['images'] = [images_arg.url]
    
    return context

# """


@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[text_match(['hello', 'help', '帮助']), assert_at()])    #以关键词开头并需要at bot
def hello(message, **kw_args):

    info_msg="""明日方舟 公开招募助手机器人
    用法:
    1.输入词条列表，空格隔开
        如: 近卫 男
    2.发送招募词条截图
    3.tell 干员名称
        如: tell 艾雅法拉
    4.mati/材料 固源岩组
    5.mati/材料
        (不加名称，查看表格)
    6.update_data
        从wiki上更新干员和敌人数据，群聊中需要@，如：@this_bot update_data
    Github链接: https://github.com/Akaisorani/QQ-bot-Arknights-Helper"""

    ret_msg=[Plain(text=info_msg)]

    return ret_msg


@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[text_match(['update_data']), assert_at()])    #以关键词开头并需要at bot
def update_data(message, **kw_args):

    tags_recom.char_data.fetch_data()
    print("fetch done")
    tags_recom.char_data.extract_all_char()
    print("extract done")
    
    
    info_msg="update done"+"\nupdated {0}characters, {1}enemies".format(len(tags_recom.char_data.char_data),len(tags_recom.char_data.enemy_data))

    ret_msg=[Plain(text=info_msg)]

    return ret_msg

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(['tell'])])    #以关键词开头并需要at bot
def tell(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_tell_par(message, context)

    name=context['name'] if 'name' in context else None
    if not name :return
    tell_report = get_peo_info(name=name)
    if tell_report is None: return 

    if isinstance(tell_report, list):
        ret_msg=tell_report
    else:
        ret_msg=[Plain(text=tell_report)]

    return ret_msg

def _tell_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("tell","").strip()
    
    print("tell stripped_arg", stripped_arg)

    if stripped_arg:
        context['name'] = stripped_arg
    return context

@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(['mati',"材料"])])    #以关键词开头并需要at bot
def mati(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_mati_par(message, context)

    name=context['name'] if 'name' in context else None
    if not name:
        # url="https://akaisorani.github.io/QQ-bot-Arknights-Helper/akaisora/plugins/materials"
        url="https://img.nga.178.com/attachments/mon_202005/16/-klbw3Q5-43dbXeZ3uT3cS2io-1bf.png"
        # url="https://arkonegraph.herokuapp.com/"

        ret_msg=[
            Image.fromBytes(get_bytes_image_from_url(url))
        ]
    else:
        report = get_material_recom(name=name)
        if report is None: return 
        ret_msg=[
            Plain(text=report)
        ]

    return ret_msg

def _mati_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("mati","").replace("材料","").strip()
    
    print("mati stripped_arg", stripped_arg)

    if stripped_arg:
        context['name'] = stripped_arg
    return context


@multi_event_handler(app, ["FriendMessage", "GroupMessage", "TempMessage"], filter=[start_with(['stat',"统计"])])    #以关键词开头并需要at bot
def stat(message, **kw_args):
    context = kw_args["context"] if 'context' in kw_args else {}

    context=_stat_par(message, context)

    name=context['name'] if 'name' in context else None
    if name:
        report = get_stat_report(name=name)
        if report is None: return
    else:
        return

    if isinstance(report, list):
        ret_msg=report
    else:
        ret_msg=[Plain(text=report)]

    return ret_msg

def _stat_par(message, context):

    stripped_arg = message.getAllofComponent(Plain)
    stripped_arg = ''.join([x.toString() for x in stripped_arg]).strip()
    stripped_arg=stripped_arg.replace("stat","").replace("统计","").strip()
    
    print("tell stripped_arg", stripped_arg)

    if stripped_arg:
        context['name'] = stripped_arg
    return context

# functions

def get_recomm_tags(tags: str, images: list) -> str:
    # 这里简单返回一个字符串
    tags_list=tags.split() if tags else []
    report=tags_recom.recom(tags_list, images)
    
    return report
    
def get_peo_info(name: str) -> str:
    # 这里简单返回一个字符串
    report=tags_recom.char_data.get_peo_info(name)
    
    return report

def get_material_recom(name: str) -> str:
    # 这里简单返回一个字符串
    report=material_recom.recom(name)
    
    return report

def get_stat_report(name: str) -> str:
    # 这里简单返回一个字符串
    rep_num=10

    if name=="tag":
        obj=tags_recom.record.get()
    elif name=="干员":
        obj=tags_recom.char_data.record.get()
        if "friend" not in obj:obj["friend"]=dict()
        obj=obj["friend"]
    elif name=="敌人":
        obj=tags_recom.char_data.record.get()
        if "enemy" not in obj:obj["enemy"]=dict()
        obj=obj["enemy"]
    elif name=="材料":
        obj=material_recom.record.get()
    else:
        return None 

    report=""
    lis=list(obj.items())
    lis.sort(key=lambda x:x[1], reverse=True)
    lis=lis[:rep_num]
    lis=["{0}({1})".format(x[0],x[1]) for x in lis]
    res=", ".join(lis)
    report="群友最喜欢查的前{0}个{1}是：\n".format(rep_num,name)+res
    
    return report

def get_bytes_image_from_url(url):
    r=requests.get(url,timeout=30)
    buffer=r.content
    return buffer

class Character(object):
    def __init__(self):
        self.char_data=dict()
        self.enemy_data=dict()
        self.head_data=[]
        self.head_key_map={
            "职业":"job",
            "星级":"rank",
            "性别":"sex",
            "阵营":"affiliation",
            "标签":"tags",
            "获取途径":"obtain_method"
        }
        self.fuzzname=Fuzzname()
        self.record=Record(path_prefix+"record_peo.txt")

    def extract_all_char(self, text_file=None, enemy_file=None):
        if text_file is None:text_file=path_prefix+"chardata.json"  
        if enemy_file is None:enemy_file=path_prefix+"enemylist.json"

        if not os.path.exists(text_file) or not os.path.exists(enemy_file):
            self.fetch_data()

        # deal char
        with open(text_file,encoding='UTF-8') as fp:
            self.char_data=json.load(fp)

        # deal enemy
        with open(enemy_file,encoding='UTF-8') as fp:
            self.enemy_data=json.load(fp)
           
        # fuzzy name+pinyin -> name
        self.fuzzname.fit(list(self.char_data.keys())+list(self.enemy_data.keys()))
            
    def filter(self, tags, flags={}):
        tags=tags[:]
        ranks=self.gen_ranks(tags)
        for name, dic in self.char_data.items():
            if set(tags).issubset(set(dic["tags"])): pass
            else: continue
            if dic["rank"] in ranks or ('show_all' in flags and flags['show_all']==True): pass
            else: continue
            if "公开招募" in dic["obtain_method"] or ('show_all' in flags and flags['show_all']==True): pass
            else: continue
                
            yield name
     
    def gen_ranks(self, tags):
        ranks=["1","2","3","4","5","6"]
        for i in range(1,7):
            if ">={0}".format(i) in tags:
                ranks=[x for x in ranks if x>=str(i)]
                tags.remove(">={0}".format(i))
            if "<={0}".format(i) in tags:
                ranks=[x for x in ranks if x<=str(i)]
                tags.remove("<={0}".format(i))
        if "高级资深干员" not in tags:
            ranks.remove("6")
        if "资深干员" in tags:
            ranks=["5"]
        if "高级资深干员" in tags:
            ranks=["6"]
        return ranks
        
    def get_peo_info(self, name=None):
        if not name: return None
        res="None"
        if name in self.char_data:
            res=self.format_friend_info(name)
            self.record.add("friend/"+name)
        elif name in self.enemy_data:
            res=self.format_enemy_info(name)
            self.record.add("enemy/"+name)
        else:
            res=self.fuzzname.predict(name)
            res="你可能想查 {0}".format(res)
        
        return res

    def format_friend_info(self, name):
        res=[]
        for tp, cont in self.char_data[name]['all'].items():
            if tp:
                if tp=="干员代号":tp="姓名"
                res.append("{0}: {1}".format(tp,cont))
        url=self.char_data[name]["link"]
        res.append(url)
        res_text="\n".join(res)

        # r=requests.get(self.char_data[name]["head_pic"],timeout=30)
        # buffer=r.content
        bytes_image=get_bytes_image_from_url(self.char_data[name]["head_pic"])

        ret_msg=[
            Image.fromBytes(bytes_image),
            # Image.fromRemote(self.char_data[name]["head_pic"]),
            # Image.fromFileSystem("./plugins/image.jpg"),
            Plain(text="\n"),
            Plain(text=res_text)
        ]

        return ret_msg

    def format_enemy_info(self, name):
        res=[name]
        url=self.enemy_data[name]["link"]
        res.append(url)
        res_text="\n".join(res)

        # r=requests.get(self.enemy_data[name]["head_pic"],timeout=30)
        # buffer=r.content
        bytes_image=get_bytes_image_from_url(self.enemy_data[name]["head_pic"])

        ret_msg=[
            Image.fromBytes(bytes_image),
            Plain(text="\n"),
            Plain(text=res_text)
        ]

        return ret_msg
        
    def fetch_data(self):
        # self.fetch_character_from_wikijoyme()
        self.fetch_character_from_akmooncell()

        try:
            self.fetch_enemy_from_akmooncell()
        except Exception as e:
            print(e)
            self.fetch_enemy_from_wikijoyme()

    def fetch_character_from_wikijoyme(self, filename="chardata.json"):
        r=requests.get("http://wiki.joyme.com/arknights/干员数据表")
        if r.status_code!=200: raise IOError("Cannot fetch char from wikijoyme")
        tree=html.fromstring(r.text)

        # table head data
        tb_head=tree.xpath("//table[@id='CardSelectTr']//th/text()")
        tb_head=[x.strip() for x in tb_head]
        
        # deal with character
        char_res_lis=tree.xpath("//tr[@data-param1]")

        char_data=dict()
        for char_tr in char_res_lis:
            name=char_tr.xpath("./td[2]/a[1]/text()")[0]
            char_data[name]=dict()
            char_data[name]["job"]=char_tr.xpath("./@data-param1")[0]
            char_data[name]["rank"]=char_tr.xpath("./@data-param2")[0].split(",")[0]
            char_data[name]["sex"]=char_tr.xpath("./@data-param3")[0]
            char_data[name]["affiliation"]=char_tr.xpath("./@data-param4")[0]
            tag_string=char_tr.xpath("./@data-param5")[0]+", " \
                        +char_data[name]["sex"]+", " \
                        +char_data[name]["job"]+", " \
                        +("资深干员" if char_data[name]["rank"]=="5" else "")+", " \
                        +("高级资深干员" if char_data[name]["rank"]=="6" else "")+", "
            taglist=[x.strip() for x in tag_string.split(",")]
            taglist=[x for x in taglist if x!=""]
            char_data[name]["tags"]=taglist
            #如果俩小车是支援机械的话加个tag
            if name in ["Castle-3","Lancet-2"]:
                char_data[name]["tags"].append("支援机械")
            char_data[name]["obtain_method"]=list(map(lambda x: x.strip(), char_tr.xpath("./@data-param6")[0].split(",")))
            
            #deal head and data
            td_lis=char_tr.xpath(".//td")
            text_lis=["".join([xx.strip() for xx in x.xpath(".//text()")]) for x in td_lis]
            all_lis=[x.strip() for x in text_lis]
            all_dict=dict(zip(tb_head,all_lis))
            char_data[name]["all"]=all_dict

            # link
            char_link_root="http://wiki.joyme.com/arknights/"
            url=char_link_root+urllib.parse.quote(name)
            char_data[name]["link"]=url

            char_data[name]["type"]="friend"

        with open(path_prefix+filename,"w",encoding='utf-8') as fp:
            json.dump(char_data, fp)

        return char_data

    def fetch_character_from_akmooncell(self, filename="chardata.json"):
        def fetch_data_with_json_format():
            r=requests.get("http://ak.mooncell.wiki/load.php?debug=false&lang=zh-cn&modules=ext.gadget.charFilter&skin=vector&version=0vmy0ui")
            if r.status_code!=200: raise IOError("Cannot fetch char from akmooncell")
            rtext=r.text.replace("\n","")
            rtext=re.sub(r"<.*?>","",rtext)
            result=re.search(r"(?<=datalist=)(.*?)(?=;console)",rtext).group(1)
            content=eval(result)
            # print(content)

            char_data=dict()
            for char_tr in content:
                name=char_tr["cn"]
                # if name=="杜宾":
                #     print(char_tr)
                char_data[name]=dict()
                char_data[name]["job"]=char_tr["class"]
                char_data[name]["rank"]=str(int(char_tr["rarity"])+1)
                char_data[name]["sex"]=char_tr["sex"]
                char_data[name]["affiliation"]=char_tr["camp"]
                char_data[name]["tags"]=char_tr["tag"]\
                            +[char_data[name]["job"]]\
                            +[char_tr["position"]]\
                            +(["资深干员"] if char_data[name]["rank"]=="5" else [])\
                            +(["高级资深干员"] if char_data[name]["rank"]=="6" else [])
                char_data[name]["obtain_method"]=char_tr["approach"]
                
                #deal head and data
                char_data[name]["all"]={
                    "姓名":char_tr["cn"],
                    "出身":char_tr["camp"],
                    "种族":','.join(char_tr["race"]),
                    "初始生命":char_tr["oriHp"],
                    "初始攻击":char_tr["oriAtk"],
                    "初始防御":char_tr["oriDef"],
                    "初始法术抗性":char_tr["oriRes"],
                    "初始再部署时间":char_tr["oriDt"],
                    "初始部署费用":char_tr["oriDc"],
                    "初始阻挡数":char_tr["oriBlock"],
                    "初始攻击间隔":char_tr["oriCd"],
                    "标签":','.join(char_tr["tag"]),
                    "特性":char_tr["feature"],
                }

                # link
                char_link_root="http://ak.mooncell.wiki/w/"
                url=char_link_root+urllib.parse.quote(name)
                char_data[name]["link"]=url

                char_data[name]["type"]="friend"
            return char_data

        def fetch_data_with_source():
            r=requests.get("http://ak.mooncell.wiki/w/干员一览")
            if r.status_code!=200: raise IOError("Cannot fetch char from akmooncell")
            rtext=r.text
            rtext=rtext.replace("\n","")
            rtext=re.sub(r"&lt;span style=.*?&gt;","",rtext)
            rtext=re.sub(r"&lt;/span&gt;","",rtext)
            
            tree=html.fromstring(rtext)
            char_res_lis=tree.xpath("//div[@class='smwdata']")

            char_data=dict()
            for char_a in char_res_lis:
                name=char_a.xpath("./@data-cn")[0]
                char_data[name]=dict()
                char_data[name]["job"]=char_a.xpath("./@data-class")[0]
                char_data[name]["rank"]=str(int(char_a.xpath("./@data-rarity")[0])+1)
                char_data[name]["sex"]=char_a.xpath("./@data-sex")[0]
                char_data[name]["affiliation"]=char_a.xpath("./@data-camp")[0]
                char_data[name]["tags"]=char_a.xpath("./@data-tag")[0].split(" ")\
                            +[char_data[name]["job"]]\
                            +[char_a.xpath("./@data-position")[0]]\
                            +(["资深干员"] if char_data[name]["rank"]=="5" else [])\
                            +(["高级资深干员"] if char_data[name]["rank"]=="6" else [])
                char_data[name]["obtain_method"]=char_a.xpath("./@data-approach")[0].split(" ")
                char_data[name]["head_pic"]="http:"+char_a.xpath("./@data-icon")[0]
                
                
                #deal head and data
                char_data[name]["all"]={
                    "姓名":name,
                    "出身":char_a.xpath("./@data-camp")[0],
                    "种族":char_a.xpath("./@data-race")[0],
                    "初始生命":char_a.xpath("./@data-ori-hp")[0],
                    "初始攻击":char_a.xpath("./@data-ori-atk")[0],
                    "初始防御":char_a.xpath("./@data-ori-def")[0],
                    "初始法术抗性":char_a.xpath("./@data-ori-res")[0],
                    "初始再部署时间":char_a.xpath("./@data-ori-dt")[0],
                    "初始部署费用":char_a.xpath("./@data-ori-dc")[0],
                    "初始阻挡数":char_a.xpath("./@data-ori-block")[0],
                    "初始攻击间隔":char_a.xpath("./@data-ori-cd")[0],
                    "标签":char_a.xpath("./@data-tag")[0],
                    "特性":char_a.xpath("./@data-feature")[0],
                }

                # link
                char_link_root="http://ak.mooncell.wiki/w/"
                url=char_link_root+urllib.parse.quote(name)
                char_data[name]["link"]=url

                char_data[name]["type"]="friend"
                # if name=="杜宾":
                #     print(char_data[name])
            return char_data

        char_data=fetch_data_with_source()

        with open(path_prefix+filename,"w",encoding='utf-8') as fp:
            json.dump(char_data, fp)

        return char_data

    def fetch_enemy_from_akmooncell(self, filename="enemylist.json"):
        # get enemy data
        r=requests.get("http://ak.mooncell.wiki/w/敌人一览")
        if r.status_code!=200: raise IOError("Cannot fetch enemy from akmooncell")
        tree=html.fromstring(r.text)

        enemy_res_lis=tree.xpath("//div[@class='smwdata']")

        enemy_data=dict()
        enemy_link_root="http://ak.mooncell.wiki/w/"
        for enemy_a in enemy_res_lis:
            name=enemy_a.xpath("./@data-name")[0]
            # print("===="+name)
            enemy_data[name]=dict()
            link=enemy_link_root+urllib.parse.quote(name)

            enemy_data[name]["link"]=link
            enemy_data[name]["type"]="enemy"
            enemy_data[name]["head_pic"]="http:"+enemy_a.xpath("./@data-file")[0]
        
        with open(path_prefix+filename,"w",encoding='utf-8') as fp:
            json.dump(enemy_data, fp)

        return enemy_data

    def fetch_enemy_from_wikijoyme(self, filename="enemylist.json"):
        # get enemy data
        r=requests.get("http://wiki.joyme.com/arknights/敌方图鉴")
        if r.status_code!=200: raise IOError("Cannot fetch enemy from wikijoyme")
        tree=html.fromstring(r.text)

        enemy_res_lis=tree.xpath("//tr[@data-param1]")

        enemy_data=dict()
        enemy_link_root="http://ak.mooncell.wiki/w/"
        for enemy_a in enemy_res_lis:
            name=enemy_a.xpath("./td[2]/a[1]/text()")[0]
            print("===="+name)
            enemy_data[name]=dict()
            link=enemy_link_root+urllib.parse.quote(name)

            enemy_data[name]["link"]=link
            enemy_data[name]["type"]="enemy"
        
        with open(path_prefix+filename,"w",encoding='utf-8') as fp:
            json.dump(enemy_data, fp)

        return enemy_data
                
class Tags_recom(object):
    def __init__(self):
        self.char_data=Character()
        self.char_data.extract_all_char()
        self.all_tags={
        '狙击', '术师', '特种', '重装', '辅助', '先锋', '医疗', '近卫',
        '减速', '输出', '生存', '群攻', '爆发', '召唤', '快速复活','费用回复',
        '新手', '治疗', '防护', '位移', '削弱', '控场', '支援',
        '支援机械', "机械",
        '近战位', '远程位',
        '近战', '远程',
        '资深干员','高级资深干员', 
        '资深','高资', 
        #'女', '男',
        #'女性', '男性',
        '狙击干员', '术师干员', '特种干员', '重装干员', '辅助干员', '先锋干员', '医疗干员', '近卫干员',
        #'女性干员', '男性干员',
        # flags
        '全部'
        }  
        
        self.ocr_tool=Ocr_tool()
        self.record=Record(path_prefix+"record_tags.txt",writecnt=50)
        
    def recom_tags(self, tags, flags={}):
        tags=self.strip_tags(tags)
    
        itertag=self.iter_all_combine(tags)
        if itertag is None:return []
        cob_lis=list(itertag)
        cob_lis.remove([])
        cob_lis=[(tags_lis, list(self.char_data.filter(tags_lis, flags))) for tags_lis in cob_lis]
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        
        # print("")
        # for x in cob_lis:
            # print(x)
        
        # remove same result
        for i in range(0,len(cob_lis)):
            for j in range(0,len(cob_lis)):
                if i==j:continue
                if set(cob_lis[i][1])==set(cob_lis[j][1]):
                    if set(cob_lis[i][0]).issubset(set(cob_lis[j][0])):
                        cob_lis[j]=(cob_lis[j][0],[])
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        # print("")
        # for x in cob_lis:
            # print(x)
   
        # special remove
        if ('show_all' not in flags or flags['show_all']==False):
            for i in range(len(cob_lis)):
                if self.is_special_rm(cob_lis[i]):
                    cob_lis[i]=(cob_lis[i][0],[])
            cob_lis=[x for x in cob_lis if x[1]!=[]]
            # print("")
            # for x in cob_lis:
                # print(x)   

        # sort
        cob_lis.sort(key=self.avg_rank, reverse=True)
        for tags_lis, lis in cob_lis:
            lis.sort(key=lambda x:self.char_data.char_data[x]["rank"], reverse=True)
        # print("")
        # for x in cob_lis:
            # print(x)
            
        # for x in cob_lis:
            # print(self.avg_rank(x))
            
        # # build reverse index
        # char_dic=dict()
        # for i in range(len(cob_lis)):
            # for name in cob_lis[i][1]:
                # if name not in char_dic:
                    # char_dic[name]=[i]
                # else:
                    # char_dic[name].append(i)
        # # print("")
        # # print(char_dic)
        
        # # remove duplicate
        # min_size_id=dict()
        # for name, lis in char_dic.items():
            # if len(lis)>1:
                # min_size_id[name]=lis[0]
                # for id in lis:
                    # if len(cob_lis[id][1])<len(cob_lis[min_size_id[name]][1]):
                        # min_size_id[name]=id
                        
        # for name, lis in char_dic.items():
            # if len(lis)>1:                        
                # for id in lis:
                    # if id!=min_size_id[name]:
                        # cob_lis[id][1].remove(name)
        # cob_lis=[x for x in cob_lis if x[1]!=[]]
        # # print("")
        # # for x in cob_lis:
            # # print(x)
        
        #merge less rank 3
        if ('show_all' not in flags or flags['show_all']==False):
            tag_cnt=0
            max_num_until_del=15
            for tags_lis, lis in cob_lis:
                cnt=0
                sp_lis=[]
                while len(lis)>0 and self.char_data.char_data[lis[-1]]["rank"]<="3":
                    res=lis.pop()
                    if res in ["Castle-3","Lancet-2","THRM-EX"]:
                        sp_lis.append(res)
                    else:
                        cnt+=1
                
                if len(sp_lis)>0:
                    lis.extend(sp_lis)
                if cnt>0 and len(lis)>0:
                    lis.append("...{0}".format(cnt))
                    # delete all contain <=3
                    if tag_cnt+len(lis)>max_num_until_del:
                        lis.clear()
                        max_num_until_del=-1
                tag_cnt+=len(lis)
            cob_lis=[x for x in cob_lis if x[1]!=[]]
            
        return cob_lis
        # print("")
        # for x in cob_lis:
            # print(x)        
                
        
    
    def is_special_rm(self, cob_i):
        if set(cob_i[0])==set(["女"]):
            return True
        # if set(cob_i[0])==set(["男"]):
            # return True
        return False
        
    def avg_rank(self, cob_i):
        rank_map={1:0.5, 2:1, 3:10, 4:2, 5:0.5, 6:3}
        rank_list=list(map(lambda x:int(self.char_data.char_data[x]["rank"]),cob_i[1]))
        sum_score=0
        sum_cnt=0
        for i in range(1,7):
            sum_score+=rank_list.count(i)*rank_map[i]*i
            sum_cnt+=rank_list.count(i)*rank_map[i]
        if sum_cnt==0:return 0
        else: return sum_score/sum_cnt
    
    def strip_tags(self, tags):
        restags=[]
        for tag in tags:
            if tag in ["高级资深干员","高资"]:
                restags.append("高级资深干员")
            elif tag in ["资深干员","资深"]:
                restags.append("资深干员")
            elif tag in ["近战","远程"]:
                restags.append(tag+"位")
            elif tag in ["机械"]:
                restags.append(tag+"支援机械")
            # elif tag in ["男性","女性"]:
            #     tag=tag.replace("性","")
            #     restags.append(tag)              
            # elif "性干员" in tag:
            #     tag=tag.replace("性干员","")
            #     restags.append(tag)
            elif "干员" in tag:
                tag=tag.replace("干员","")
                restags.append(tag)
            else:
                restags.append(tag)
        return restags
        
    def iter_all_combine(self, tags):
        if len(tags)==0:
            yield []
            return
        tag=tags[0]
        new_tags=tags[:]
        new_tags.remove(tag)
        for x in self.iter_all_combine(new_tags):
            yield [tag]+x
        for x in self.iter_all_combine(new_tags):
            yield x
    
    def check_legal_tags(self, tags):
        if not tags: return False
        for tag in tags:
            if tag not in self.all_tags:
                return False
        return True
        
    def filter_legal_tags(self, tags):
        if not tags: return []
        res=[]
        for tag in tags:
            if tag in self.all_tags:
                res.append(tag)
        return res

    def split_flags(self, tags):
        if not tags: return [],{}
        tags=list(set(tags))
        flags={}
        if '全部' in tags:
            flags['show_all']=True
            tags.remove('全部')
        else:
            flags['show_all']=False

        return tags, flags



    def record_tags(self, tags):
        for tag in tags:
            self.record.add(tag)


    def recom(self, tags=None, images=None):
        if not tags:
            if images:
                tags=self.get_tags_from_image(images)
                if not tags:
                    print("MYDEBUG image checkfail {0}".format(images[0]))
                    return None
            else:
                return None
        
        tags, flags=self.split_flags(tags)

        if not self.check_legal_tags(tags):
            print("MYDEBUG no legal tags")
            return None

        self.record_tags(tags)
        cob_lis=self.recom_tags(tags, flags)
        if not cob_lis:
            return "没有或者太多"
        line_lis=[]
        for tags_lis, lis in cob_lis:
            new_lis=[]
            for x in lis:
                if x in self.char_data.char_data:
                    new_lis.append(x+"★"+self.char_data.char_data[x]["rank"])
                else:
                    new_lis.append("★1~3"+x)
            lef='【'+'+'.join(tags_lis)+"】:\n"
            rig=', '.join(new_lis)
            line_lis.append(lef+rig)
        res="\n\n".join(line_lis)
        return res
    
    def get_tags_from_image(self, images):
        tags=self.ocr_tool.get_tags_from_url(images[0])
        tags=self.filter_legal_tags(tags)
        tags=list(set(tags))
        print("ocr res=",tags)
        if len(tags)>=2 and len(tags)<=8:
            return tags
        else:
            return []
        
        

tags_recom=Tags_recom()
material_recom=Material()

if __name__=="__main__":
    filename="chardata.html"

    char_data=Character()
    char_data.fetch_data()
    print("fetch_done")
    
    char_data.extract_all_char()
    print(char_data.char_data["艾雅法拉"])

    res2=tags_recom.char_data.get_peo_info("艾斯戴尔")
    print(res2)

    print(char_data.enemy_data["大鲍勃"])
    tags_recom.char_data.fetch_data()
    tags_recom.char_data.extract_all_char()
    res2=tags_recom.char_data.get_peo_info("法术大师A2")
    print(res2)
    
    res=tags_recom.recom(["狙击干员","辅助干员", "削弱", "支援机械", "治疗"])
    
    # res=tags_recom.recom(["近卫", "男", "支援"])
    print(res)
    print("="*15)
    url="https://c2cpicdw.qpic.cn/offpic_new/1224067801//39b40a48-b543-4082-986d-f29ee82645d3/0?vuin=2473990407&amp;amp;term=2"
    url="https://c2cpicdw.qpic.cn/offpic_new/391809494//857ddb74-7a0d-40ae-98db-068f8c733c86/0?vuin=2473990407&amp;amp;term=2"
    url="https://gchat.qpic.cn/gchatpic_new/2465342838/698793878-3133403591-5DB0FBC01E75F719EA8CD107F6416BAA/0?vuin=2473990407&amp;amp;term=2"
    # res=tags_recom.recom(images=[url])
    # print(res)
    


    res=material_recom.recom("聚酸酯块")
    print(res)

    # for i in range(20):
    #     tags_recom.recom(["狙击干员","辅助干员", "削弱", "女性干员", "治疗"])
    #     tags_recom.recom(["近卫", "男", "支援"])
    #     tags_recom.char_data.get_peo_info("艾丝戴尔")
    #     tags_recom.char_data.get_peo_info("艾雅法拉")
    #     res=material_recom.recom("聚酸酯块")
    #     tags_recom.char_data.get_peo_info("大鲍勃")
    
    # for name in ["tag","干员","材料","敌人"]:
    #     report = get_stat_report(name=name)
    #     print(report)

    res=tags_recom.recom(["远程", "支援"])
    print(res)

    res=tags_recom.recom(["支援机械"])
    print(res)



    
    # st=set()
    # for name,dic in tags_recom.char_data.char_data.items():
        # st=st|set(dic['tags'])
    # print(st)
    
    

