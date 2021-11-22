#!/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle, run, request
import sys
import requests
import json
import os

requests.packages.urllib3.disable_warnings()   # 关闭https警告
reload(sys)   # python2 语法
sys.setdefaultencoding('utf8')  # python2

app = Bottle()

@app.route('/gitlab_bot', method='POST')
def gitlab_bot():
    feishu_bot_url = os.getenv('BOT_URL')
    # "https://open.feishu.cn/open-apis/bot/v2/hook/a874304d-ae40-44fe-bf44-84cd86b9747b"
    result = False     # 状态flag
    post_string = ''

    try:
        # 获取gitlab post的数据并进行合并
        for key in request.params.keys():
            post_string = post_string + key
        for value in request.params.values():
            post_string = post_string + value

        print post_string

        post_dict = json.loads(post_string)

        # 解析指定字段内容
        event_type = post_dict.get("object_kind")
        author_name = post_dict.get("user").get("name")
        project_name = post_dict.get("project").get("name")
        action_status = post_dict.get("object_attributes").get("action")
        title = post_dict.get("object_attributes").get("title")
        description = post_dict.get("object_attributes").get("description")
        project_url = post_dict.get("object_attributes").get("url")


        # 规避为添加受理人员异常
        if post_dict.get("assignees") == None:
            assignees = None
        else:
            assignees = post_dict.get("assignees")[0].get("name")
        # 更具不同时间类型发送不通消息体
        if post_dict.get("object_kind") == "issue":
            result = True

            if action_status == "close":
                assignees = None

            feishu_text_msg = "项目名称：{}\r\n提交者：{}\r\n事件类型：{}\r\n执行动作：{}\r\n标题：{}\r\n内容：{}\r\n指派处理人员：{}\r\n项目地址：{}".format(project_name, author_name, event_type, action_status, title, description, assignees, project_url)

        if post_dict.get("object_kind") == "note":
            result = True
            event_type = "comments"

            feishu_text_msg = "项目名称：{}\r\n提交者：{}\r\n事件类型：{}\r\n内容：{}\r\n项目地址：{}".format(project_name, author_name, event_type, description, project_url)

        if post_dict.get("object_kind") == "merge_request":
            result = True
            # merge结束后异常处理
            source_branch = post_dict.get("object_attributes").get("source_branch")
            target_branch = post_dict.get("object_attributes").get("target_branch")

            feishu_text_msg = "项目名称：{}\r\n提交者：{}\r\n事件类型：{}\r\n执行动作：{}\r\nBranch：{} ---> {}\r\n标题：{}\r\n内容：{}\r\n指派处理人员：{}\r\n项目地址：{}".format(project_name, author_name, event_type, action_status, source_branch, target_branch, title, description, assignees, project_url)


        # 拼接发送消息内容
        feishu_text_data = {}
        dict_content = {}
        dict_content["text"] = feishu_text_msg
        feishu_text_data["msg_type"] = "text"
        feishu_text_data["content"] = dict_content

        feishu_headers = {"Content-Type": "application/json"}
        response = requests.post(feishu_bot_url, headers=feishu_headers, data=json.dumps(feishu_text_data))
        print(response, response.json())

    except Exception as err:
        print('===> Exception')
        print(str(err).decode("string_escape"))
    finally:
        print('===> Finally')

    content = "创建失败"

    if result == True:
        content = "创建成功"
    return content

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=6666)


