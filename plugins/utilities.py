from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio
from pydevtools import debug
import re
from typing import List, Union
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

test_group_list=[696694875]
test_friend_list=[1224067801]

def multi_event_handler(app, event_types, filter=None):
    if isinstance(event_types, str):
        event_types=[event_types]

    def deco_func(func):

        def apply_filters(message, context):
            if filter is None: return
            if isinstance(filter, list): filters=filter
            else: filters=[filter]

            for fit in filters:
                if not fit(message, context): raise Cancelled
    
        if "FriendMessage" in event_types:
            @app.receiver("FriendMessage")
            async def event_gm(app: Mirai, friend: Friend, message: MessageChain):
                # print(message)

                context={'app': app, 'friend': friend, 'event_type': "FriendMessage"}

                apply_filters(message, context)

                msg=func(message, context=context)

                if msg is None: raise Cancelled
                await app.sendFriendMessage(friend, msg)
        
        if "GroupMessage" in event_types:
            @app.receiver("GroupMessage")
            async def event_gm(app: Mirai, group: Group, member: Member, message: MessageChain):
                # print(message)

                context={'app': app, 'group': group, 'member':member, 'event_type': "GroupMessage"}

                apply_filters(message, context)

                msg=func(message, context=context)
                # if test_group_list and group.id not in test_group_list: return None
                if msg is None: raise Cancelled

                await app.sendGroupMessage(group, msg)
        
        if "TempMessage" in event_types:
            @app.receiver("TempMessage")
            async def event_gm(app: Mirai, group: Group, member: Member, message: MessageChain):
                # print(message)

                context={'app': app, 'group': group, 'member':member, 'event_type': "TempMessage"}

                apply_filters(message, context)

                msg=func(message, context=context)
                if msg is None: raise Cancelled

                await app.sendTempMessage(group, member, msg)
        
        return func
    
    return deco_func


# filters

def start_with(string):
    def startswith_wrapper(message: MessageChain, context):
        if isinstance(string, str):
            strings=[string]
        elif isinstance(string, list):
            strings=string
        else: return False
        msg_text= message.getAllofComponent(Plain)
        msg_text = ''.join([x.toString() for x in msg_text]).strip()
        flag=False
        for ss in strings:
            if msg_text.startswith(ss):
                flag=True
                break
        return flag
    return startswith_wrapper

def text_match(string):
    def startswith_wrapper(message: MessageChain, context):
        if isinstance(string, str):
            strings=[string]
        elif isinstance(string, list):
            strings=string
        else: return False
        msg_text= message.getAllofComponent(Plain)
        msg_text = ''.join([x.toString() for x in msg_text]).strip()
        flag=False
        for ss in strings:
            if msg_text==ss:
                flag=True
                break
        return flag
    return startswith_wrapper

def regex_match(pattern):
    def regex_depend_wrapper(message: MessageChain, context):
        if not re.match(pattern, message.toString()):
            return False
        return True
    return regex_depend_wrapper

def with_photo(num=1):
    "断言消息中图片的数量"
    def photo_wrapper(message: MessageChain, context):
        if len(message.getAllofComponent(Image)) < num:
            return False
        return True
    return photo_wrapper

def assert_at(qq=None):
    "断言是否at了某人, 如果没有给出则断言是否at了机器人"
    def at_wrapper(message: MessageChain, context):
        app=context['app']
        at_set: List[At] = message.getAllofComponent(At)
        curr_qq = qq or app.qq
        if at_set:
            for at in at_set:
                if at.target == curr_qq:
                    return True
        else:
            return False
    return at_wrapper

def groups_restraint(*groups: List[Union[Group, int]]):
    "断言事件是否发生在某个群内"
    def gr_wrapper(message, context):
        app=context['app']
        group=context['group']
        groups = [group if isinstance(group, int) else group.id for group in groups]
        if group.id not in groups:
            return False
        return True
    return gr_wrapper


# Scheduler

def schedule_job(app, *args, **kw_args):
    '''
    year (int|str) – 4-digit year
    month (int|str) – month (1-12)
    day (int|str) – day of the (1-31)
    week (int|str) – ISO week (1-53)
    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    hour (int|str) – hour (0-23)
    minute (int|str) – minute (0-59)
    econd (int|str) – second (0-59)
            
    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
    end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)
        
    *    any    Fire on every value
    */a    any    Fire every a values, starting from the minimum
    a-b    any    Fire on any value within the a-b range (a must be smaller than b)
    a-b/c    any    Fire every c values within the a-b range
    xth y    day    Fire on the x -th occurrence of weekday y within the month
    last x    day    Fire on the last occurrence of weekday x within the month
    last    day    Fire on the last day within the month
    x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions
    '''

    def deco_func(func):

        # @app.onStage("start")
        # def scheduled_func():
            # if "app" in func.__globals__:
            #     func.__globals__["app"]=app

            # scheduler = BackgroundScheduler()
        scheduler = AsyncIOScheduler()

        scheduler.add_job(func, *args, **kw_args)

        scheduler.start()

        return func

    return deco_func
