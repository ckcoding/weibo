# 微博热搜监控脚本
# 使用说明：将下面的部分数据修改为你的，然后挂在腾讯云函数即可
# 本程序基于python3.6开发,仅做技术交流
# 更新时间：2020.07.15
# 作者；ck
import requests
import re
import json
import imaplib
import smtplib

######以下为需要修改的信息##########
#1：修改为你的发件邮箱地址,请使用QQ邮箱
email='1f5@qq.com'
#2：发件邮箱的授权码(需开启POP3/IMAP/SMTP)等服务
password_key='tvfh'
#收件人邮箱
take_email= ['12fff@qq.com']
#对方的微博主页:例如https://weibo.com/u/56558
weibourl='对方的微博主页链接'
######通用信息，全局调用######
f = open('old.txt', 'r',encoding='utf-8-sig')
oldjson = f.read()
f = open('top.txt', 'r', encoding='utf-8-sig')
topjson = f.read()
f = open('info.txt', 'r', encoding='utf-8-sig')
info = f.read()


def sendEmail(data):
    from email.mime.text import MIMEText
    # email 用于构建邮件内容
    from email.header import Header
    # 用于构建邮件头
    # 发信方的信息：发信邮箱，QQ 邮箱授权码
    from_addr = email
    password = password_key
    # 收信方邮箱
    to_addr = ','.join(take_email)
    # 发信服务器
    smtp_server = 'smtp.qq.com'
    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
    msg = MIMEText(data, 'plain', 'utf-8')
    # 邮件头信息
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header('你关注的人微博有新的动态啦')
    # 开启发信服务，这里使用的是加密传输
    server = smtplib.SMTP_SSL(smtp_server)
    server.connect(smtp_server, 465)
    # 登录发信邮箱
    server.login(from_addr, password)
    # 发送邮件
    server.sendmail(from_addr, to_addr.split(','), msg.as_string())
    # 关闭服务器
    server.quit()
def run(url):
    pattern = re.compile('[1-9]\d*')
    id = pattern.findall(url)[0]
    id_url = 'https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value=' + id
    container = requests.get(id_url).text
    pattern = re.compile('(?<="tab_type":"weibo","containerid":").*(?=","apipath")')
    containerid = pattern.findall(container)[0]
    url='https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value=%s&containerid=%s' % (id , containerid)
    html = requests.get(url).text
    toptext = json.dumps(json.loads(html)['data']['cards'][0]["mblog"])
    pattern = re.compile('(?<="title": {"text":).*(?=,)')
    top = pattern.findall(toptext)

    print(top)
    if top ==[]:
        print('没有置顶')
        time = json.loads(html)['data']['cards'][0]["mblog"]['created_at']
        text = json.loads(html)['data']['cards'][0]["mblog"]['text']
        if text == oldjson:
            print('无变动')
        else:
            print('有变动')
            file = open('old.txt', 'w', encoding='utf-8')
            file.write(text)
            data = '你关注的人微博有新的动态啦' + '\n\n' + '发布时间为：' + time + '\n' + '发布内容为：' + text + '\n\n' + '微博链接：' + weibourl
            sendEmail(data)

    else:
        print('有置顶')
        top_time1 = json.loads(html)['data']['cards'][0]["mblog"]['created_at']
        top_text1 = json.loads(html)['data']['cards'][0]["mblog"]['text']
        top_time2 = json.loads(html)['data']['cards'][1]["mblog"]['created_at']
        top_text2 = json.loads(html)['data']['cards'][1]["mblog"]['text']
        if top_text1 == oldjson:
            print('第一条置顶了')

        else:
            print('有变动')
            file = open('old.txt', 'w', encoding='utf-8')
            file.write(top_text1)
            data = '你关注的人微博有新的置顶微博' + '\n\n' + '置顶微博' + '发布时间为：' + top_time1 + '\n' + '发布内容为：' + top_text1 + '\n\n' + '第二条微博' + '发布时间为：' + top_time2 + '\n' + '发布内容为：' + top_text2 + '\n\n' + '微博链接：' + weibourl
            sendEmail(data)

def main_handler(event, context):
    return run(weibourl)


if __name__ == '__main__':
    run(weibourl)








