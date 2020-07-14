from mirai import Mirai, Plain, At, AtAll, Image, Face, MessageChain, Friend, Group, Member, UnexpectedException, Cancelled
import asyncio
from pydevtools import debug

from plugins.utilities import multi_event_handler
from plugins.utilities import start_with, text_match, regex_match, with_photo, assert_at, groups_restraint
import myconfig

qq = myconfig.qq
authKey = myconfig.authKey
mirai_api_http_locate = myconfig.mirai_api_http_locate

app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

test_group_list=myconfig.test_group_list
test_friend_list=myconfig.test_friend_list

@app.receiver("UnexpectedException")
async def exception_handler_normal(context: UnexpectedException):
    print("get an error")
    debug(context) # 调用了库 devtools 中的 debug 函数, 可以美观的在控制台输出 Pydantic 模型.

# include plugins
from plugins import recom_tags
from plugins import setu
from plugins import pcr_tool
# from plugins import hourcall


if __name__ == "__main__":
    app.run()