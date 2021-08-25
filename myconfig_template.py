["bot"]

qq = 123456789 # 字段 qq 的值
authKey = '123456' # 字段 authKey 的值
mirai_api_http_locate = 'localhost:8080/ws' # httpapi所在主机的地址端口,如果 setting.yml 文件里字段 "enableWebsocket" 的值为 "true" 则需要将 "/" 换成 "/ws", 否则将接收不到消息.

["test"]

test_group_list=[123456789]
test_friend_list=[123456789]

["hourcall"]

group_id_list=[123456789]
group_mrfz_cake_id_list=[123456789]

["weibo"]

group_mrfz_weibo_id_list=[123456789]

["heartbeat"]
group_heartbeat_list=[123456789]

["pic_collect"]
group_pic_collect_list=[123456789]


["share"]

app = None
scheduler = None

["memo"]

memo_dir = "./plugins/memo_data/data"
memo_index_path = "./plugins/memo_data/memo_index.json"
memo_index = None

["sanity"]

sanity_data_path = "./plugins/sanity_data.json"

["setu"]
pixiv_username = ""
pixiv_password = ""
setu_local_save_root = ""


["msglog"]

msglog={"group":{}}

["recomtag"]

cookies_prts = "./cookies_prts.txt"
group_recomtag_id_list=[123456789]

["pic_collector"]

repo_link=""
repo_upload_link=""
repo_download_link=""
