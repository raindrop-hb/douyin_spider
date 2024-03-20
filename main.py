#!/usr/bin/python3.10
# -*- coding: utf-8 -*-
# Copyright (C) 2023 , Inc. All Rights Reserved
# @Time    : 2023/5/17 22:45
# @Author  : raindrop
# @Email   : 196329640@qq.com
# @File    : main.py
import json
import os
from requests import get, head, post
from json import loads, dump
from re import findall
from os import mkdir, path
from time import sleep, localtime, strftime, time
import csv
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote, quote
import uuid
import lxml.html
etree = lxml.html.etree


class Task(object):
    def __init__(self, sec_user_id, count, tc, cookie, XBogus_api):
        self.sec_user_id = sec_user_id
        self.max_cursor = int(round(time() * 1000))
        self.count = count
        self.picture = 0
        self.video = 0
        self.numb = 0
        self.nickname = "Null"
        self.tc = tc
        self.time_start = float(round(time()))
        self.begin_time = int(round(time() * 1000))
        self.status = 1
        self.now_time = int(round(time() * 1000))
        self.end_time = 946656000000
        self.config = configs()
        self.cookie = cookie
        self.passs = False
        self.XBogus_api = XBogus_api
        with open("cache.json", 'r') as f:
            a = json.load(f)
        if str(sec_user_id) in a:
            self.nickname = a[sec_user_id]
        if path.exists(self.nickname + "/断点续传.txt") and (self.nickname != "Null"):
            with open(self.nickname + "/断点续传.txt", 'r', encoding='utf-8') as f:
                # aaa 初始 bbb 结束  ccc 当前 ddd 状态：1未结束，0结束
                duan = f.read().split(",")
            if duan[3] == "1":
                sss = input('检测到未执行完的任务，是否进行断点续传？\n回车是Y，N否')
                result_list = ['n', 'N', 'NO', 'no', '否']
                if sss not in result_list:
                    printt('开始断点续传')
                    self.begin_time = int(duan[0])
                    self.end_time = int(duan[1])
                    self.now_time = int(duan[2])
                    self.status = int(duan[3])
                    self.max_cursor = int(duan[2])
                else:
                    self.passs = True
            else:
                sss = input('检测到上次任务执行完毕，是否进行更新检测？\n回车是Y，N否')
                result_list = ['n', 'N', 'NO', 'no', '否']
                if sss not in result_list:
                    printt("开始检测更新")
                    self.end_time = int(duan[0])
                    self.status = 0
                else:
                    self.passs = True

    def run(self):
        while True:
            if self.passs:
                return True
            if self.task():
                return True

    def task(self):
        form = 'device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=' + self.sec_user_id + '&max_cursor=' + str(self.max_cursor) + '&locate_query=false&show_live_replay_strategy=1&count=50&publish_video_strategy_type=2&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=108.0.5359.95&browser_online=true&engine_name=Blink&engine_version=108.0.5359.95&os_name=Windows&os_version=10&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=250'
        headers = {
            'referer': 'https://www.douyin.com/user/' + self.sec_user_id,
            'cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
        for i in range(10):
            try:
                XB = get(self.XBogus_api + quote(form), timeout=3).json()
                url = 'https://www.douyin.com/aweme/v1/web/aweme/post/?' + form + "&X-Bogus=" + XB['data']["X_Bogus"]
                resp = get(url, headers=headers, timeout=3)
                resps = resp.text.encode("gbk", 'ignore').decode("gbk", "ignore")
                resp = loads(resps)
                break
            except Exception as e:
                if i == 9:
                    printt('触发')
                    print(e)
                    printt('cookies失效，请自行获取cookies填入脚本目录下config.json中\n获取cookies方法：\n1.电脑浏览器打开抖音并登录,随便找一个人的主页打开\n2.按f12键进入开发者模式，点击网络\n3.刷新页面,网络的名称里选择第一个\n4.标头，下滑找到cookie，右键复制值,粘贴到config.json的双引号里里')
                    input('回车退出')
                    if path.exists("cookie"):
                        os.remove("cookie")
                    exit(0)
        if self.numb == 0:
            if self.nickname == "Null":
                for i in range(10):
                    if resp["aweme_list"][i]["author"]["nickname"] == resp["aweme_list"][i + 2]["author"]["nickname"]:
                        self.nickname = resp["aweme_list"][i]["author"]["nickname"]
                        break
                self.nickname = resp["aweme_list"][0]["author"]["nickname"]
                nickname_url = "https://m.douyin.com/web/api/v2/user/info/?reflow_source=reflow_page&sec_uid=" + self.sec_user_id
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 likeMac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1 (compatible; Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)",
                    "cookie": self.cookie
                }
                try:
                    resp_2 = get(nickname_url, headers=headers, timeout=3)
                    resp_2 = resp_2.text.encode('gbk', errors='ignore').decode('gbk')
                    self.nickname = json.loads(resp_2)["user_info"]["nickname"]
                except Exception as e:
                    printt("get username error")
                    print(e)
                with open("cache.json", 'r') as f:
                    a = json.load(f)
                with open("cache.json", 'w') as f:
                    a[self.sec_user_id] = self.nickname
                    dump(a, f, indent=4, ensure_ascii=False)
            self.nickname = self.nickname.replace("*", "")
            printt('即将 {} 线程采集 {} 个 {} 的作品'.format(str(self.tc), str(self.count), self.nickname))
            try:
                mkdir(self.nickname + "/")
            except:
                print("erro")
                pass
            if self.config["spider_setting"]["储存格式"]:
                iiis = ["/video/", "/picture/", "/cover/", "/big_thumbs/", "/bgmusic/"]
                for iiii in iiis:
                    try:
                        mkdir(self.nickname + iiii)
                    except:
                        pass

            if self.config["csv_setting"]["开关"] and (not path.exists(self.nickname + "/断点续传.txt")):
                with open(self.nickname + "/" + self.nickname + "_采集数据.csv", 'w', newline='', encoding='gbk',
                          errors='ignore') as csvfile:
                    writer = csv.writer(csvfile)
                    list_csv = []
                    list_title = ["作品id", "时间", "标题", "格式", "收藏", "评论", "点赞", "分享", "分享链接",
                                  "无水印链接"]
                    for i in self.config["csv_setting"]:
                        if i in list_title and self.config["csv_setting"][i]:
                            list_csv.append(i)
                    writer.writerow(list_csv)
            if self.end_time != 946656000000 and (
            not path.exists(self.nickname + "/" + self.nickname + "_更新数据.csv")):
                with open(self.nickname + "/" + self.nickname + "_更新数据.csv", 'w', newline='', encoding='gbk',
                          errors='ignore') as csvfile:
                    writer = csv.writer(csvfile)
                    list_csv = []
                    list_title = ["作品id", "时间", "标题", "格式", "收藏", "评论", "点赞", "分享", "分享链接",
                                  "无水印链接"]
                    for i in self.config["csv_setting"]:
                        if i in list_title and self.config["csv_setting"][i]:
                            list_csv.append(i)
                    writer.writerow(list_csv)
        printt('共{}个作品，已保存{}个，当前解析到{}'.format(str(self.count), str(self.numb), len(resp["aweme_list"])))
        if self.count == '∞':
            aweme_list = resp["aweme_list"]
        elif len(resp["aweme_list"]) > (int(self.count) - int(self.numb)):
            aweme_list = resp["aweme_list"][:(int(self.count) - int(self.numb))]
        else:
            aweme_list = resp["aweme_list"]
        pool = ThreadPoolExecutor(self.tc)
        for aweme in aweme_list:
            aaa = pool.submit(self.download, aweme)
            if aaa.result() == True:
                return True
            printt(aaa.result())
            self.numb = self.numb + 1
        pool.shutdown()
        if str(self.numb) == str(self.count):
            printt("已采集指定数目作品,共{}个作品,{}个视频，{}个图片，请在脚本目录下查看".format(self.numb, self.video,
                                                                                               self.picture))
            self.time_cha()
            return True
        if resp["has_more"] == 0:
            try:
                os.remove(self.nickname + "/断点续传.txt")
                with open(self.nickname + "/断点续传.txt", 'w', encoding='utf-8') as f:
                    # aaa 初始 bbb 结束  ccc 当前 ddd 状态：1未结束，0结束
                    f.write(str(self.begin_time) + "," + str(self.end_time) + "," + str(self.now_time) + ",0")
            except:
                pass
            printt("数据采集结束,共{}个作品,{}个视频，{}个图片，请在脚本目录下查看".format(self.numb, self.video, self.picture))
            self.time_cha()
            return True
        self.max_cursor = resp["max_cursor"]

    def time_cha(self):
        printt('运行结束')
        time_end = float(round(time()))
        time_diff = int(time_end - self.time_start)
        if time_diff >= 3600:
            hh = time_diff // 3600
            time_diff = time_diff % 3600
        else:
            hh = 0
        if time_diff >= 60:
            mm = time_diff // 60
            time_diff = time_diff % 60
        else:
            mm = 0
        if time_diff > 0:
            ss = time_diff
        printt('本次执行共耗时{}时{}分{}秒'.format(str(hh), str(mm), str(ss)))

    def download(self, aweme):
        if self.numb == 0 and self.status == 0:
            if (aweme["create_time"] * 1000) > self.end_time:
                printt("开始更新作品")
                self.status = 1
            elif (aweme["create_time"] * 1000) <= self.end_time:
                printt("无需更新")
                try:
                    os.remove(self.nickname + "/" + self.nickname + "_更新数据.csv")
                except:
                    pass
                self.status = 0
                return True
        if (aweme["create_time"] * 1000) <= self.end_time:
            if self.end_time != 946656000000:
                printt("整合更新数据")
                with open(self.nickname + "/" + self.nickname + "_采集数据.csv", 'r', newline='', encoding='gbk',
                          errors='ignore') as csvfile:
                    reader = csv.reader(csvfile)
                    reader_1 = [row for row in reader]
                with open(self.nickname + "/" + self.nickname + "_更新数据.csv", 'r', newline='', encoding='gbk',
                          errors='ignore') as csvfile:
                    reader = csv.reader(csvfile)
                    reader_2 = [row for row in reader]
                reader_2.extend(reader_1[1:])
                with open(self.nickname + "/" + self.nickname + "_采集数据.csv", 'w', newline='', encoding='gbk', errors='ignore') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(reader_2)
                os.remove(self.nickname + "/" + self.nickname + "_更新数据.csv")
                with open(self.nickname + "/断点续传.txt", 'w', encoding='utf-8') as f:
                    # aaa 初始 bbb 结束  ccc 当前 ddd 状态：1未结束，0结束
                    f.write(str(self.begin_time) + "," + str(self.end_time) + "," + str(
                        aweme["create_time"] * 1000) + ",0")
            return True

        desc = aweme["statistics"]
        desc['收藏'] = desc.pop('collect_count')
        desc['评论'] = desc.pop('comment_count')
        desc['点赞'] = desc.pop('digg_count')
        desc['分享'] = desc.pop('share_count')
        desc['分享链接'] = aweme["share_info"]['share_url']
        desc['作品id'] = str(aweme["aweme_id"]) + "\t"
        if aweme['images'] == None:
            desc['格式'] = "video"
        else:
            desc['格式'] = "picture"
        del desc['play_count']
        del desc['admire_count']
        time_1 = int(aweme["create_time"])
        if self.now_time > (time_1 * 1000):
            self.now_time = time_1 * 1000
            with open(self.nickname + "/断点续传.txt", 'w', encoding='utf-8') as f:
                # aaa 初始 bbb 结束  ccc 当前 ddd 状态：1未结束，0结束
                f.write(str(self.begin_time) + "," + str(self.end_time) + "," + str(self.now_time) + ",1")
        # 转换成localtime
        time_2 = localtime(time_1)
        # 转换成新的时间格式
        desc['时间'] = strftime("%Y-%m-%d %H:%M:%S", time_2)
        desc['标题'] = aweme['desc']
        # 视频
        iiia = ""
        dess = list()
        list_titles = ["作品id", "时间", "标题", "格式", "收藏", "评论", "点赞", "分享", "分享链接"]
        for iii in list_titles:
            if iii != "分享链接":
                iiia = iiia + iii + ":" + str(desc[iii]) + "\n"
            if self.config["csv_setting"][iii]:
                dess.append(str(desc[iii]))
        if aweme['images'] == None:
            if self.config["spider_setting"]["储存格式"]:
                url = aweme["video"]["play_addr"]["url_list"][0]
                if self.config["spider_setting"]["下载视频"]:
                    video = get(url)
                    with open(self.nickname + "/video/" + aweme["aweme_id"] + '.mp4', 'wb') as f:
                        f.write(video.content)
                try:
                    url = aweme["music"]["play_url"]["url_list"][0]
                    video = get(url)
                    if self.config["spider_setting"]["视频背景音乐"]:
                        with open(self.nickname + "/bgmusic/" + aweme["aweme_id"] + '.mp3', 'wb') as f:
                            f.write(video.content)
                except:
                    pass
                try:
                    url = aweme["video"]["big_thumbs"][0]["img_url"]
                    video = get(url)
                    if self.config["spider_setting"]["视频缩略图"]:
                        with open(self.nickname + "/big_thumbs/" + aweme["aweme_id"] + '.jpeg',
                                  'wb') as f:
                            f.write(video.content)
                except:
                    pass

                try:
                    url = aweme["video"]["cover"]["url_list"][1]
                    video = get(url)
                    if self.config["spider_setting"]["视频封面"]:
                        with open(self.nickname + "/cover/" + aweme["aweme_id"] + '.jpeg', 'wb') as f:
                            f.write(video.content)
                except:
                    pass
            else:
                try:
                    mkdir(self.nickname + "/" + aweme["aweme_id"] + "/")
                except:
                    pass
                url = aweme["video"]["play_addr"]["url_list"][0]
                if self.config["spider_setting"]["下载视频"]:
                    video = get(url)
                    with open(self.nickname + "/" + aweme["aweme_id"] + '/video.mp4', 'wb') as f:
                        f.write(video.content)
                try:
                    url = aweme["music"]["play_url"]["url_list"][0]
                    video = get(url)
                    if self.config["spider_setting"]["视频背景音乐"]:
                        with open(self.nickname + "/" + aweme["aweme_id"] + '/bgmusic/.mp3', 'wb') as f:
                            f.write(video.content)
                except:
                    pass
                try:
                    url = aweme["video"]["big_thumbs"][0]["img_url"]
                    video = get(url)
                    if self.config["spider_setting"]["视频缩略图"]:
                        with open(self.nickname + "/" + aweme["aweme_id"] + '/big_thumbs.jpeg',
                                  'wb') as f:
                            f.write(video.content)
                except:
                    pass

                try:
                    url = aweme["video"]["cover"]["url_list"][1]
                    video = get(url)
                    if self.config["spider_setting"]["视频封面"]:
                        with open(self.nickname + "/" + aweme["aweme_id"] + '/cover.jpeg', 'wb') as f:
                            f.write(video.content)
                except:
                    pass
            if self.config["csv_setting"]["无水印链接"]:
                dess.append(aweme["video"]["play_addr"]["url_list"][-1])
            self.video += 1
        else:
            s = 0
            for i in aweme["images"]:
                s += 1
                url = i["url_list"][-1]
                if self.config["spider_setting"]["下载图片"]:
                    video = get(url)
                    with open(self.nickname + "/picture/" + aweme["aweme_id"] + '_' + str(s) + '.jpeg',
                              'wb') as f:
                        f.write(video.content)
                if self.config["csv_setting"]["无水印链接"]:
                    dess.append(url)
                self.picture += 1

        if ((self.config["csv_setting"]["图文数据"] and desc['格式'] == "picture") or (
                self.config["csv_setting"]["视频数据"] and desc['格式'] == "video")) and self.config["csv_setting"][
            "开关"]:
            with open(self.nickname + "/" + self.nickname + "_采集数据.csv", 'a', newline='', encoding='gbk',
                      errors='ignore') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(dess)
        return iiia


# 下载单个作品
def get_aweme(url, XBogus_api):
    time_1 = int(time())
    # 转换成localtime
    time_2 = localtime(time_1)
    # 转换成新的时间格式
    file = strftime("%Y-%m-%d", time_2)
    headers = {
        "referer": "https://www.douyin.com/",
        "user-agent": "Mozilla/5.0 (Linux; Android 12; 2210132C Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36",
        "cookie": "ttwid=" + get_tt()
    }
    try:
        mkdir(file + "/")
    except:
        pass
    iiia = "未知错误"
    if "video" in url:
        aweme_id = findall('video/(\d+)', url)[0]
        url = f"https://www.iesdouyin.com/share/video/{aweme_id}"
        resp = get(url, headers=headers).text.encode('gbk', errors='ignore').decode('gbk')
        html = etree.HTML(resp)
        resp = html.xpath('/html/body/script[@id="RENDER_DATA"]/text()')[0]
        resp = unquote(resp).encode('gbk', errors='ignore').decode('gbk')
        resp = json.loads(resp)
        desc = resp["app"]["videoInfoRes"]["item_list"][0]["statistics"]
        desc['收藏'] = desc.pop('collect_count')
        desc['评论'] = desc.pop('comment_count')
        desc['点赞'] = desc.pop('digg_count')
        desc['分享'] = desc.pop('share_count')
        desc['格式'] = "video"
        desc.pop("play_count")
        desc['作品id'] = str(resp["app"]["videoInfoRes"]["item_list"][0]["aweme_id"])
        time_1 = int(resp["app"]["videoInfoRes"]["item_list"][0]["create_time"])
        time_2 = localtime(time_1)
        # 转换成新的时间格式
        desc['时间'] = strftime("%Y-%m-%d %H:%M:%S", time_2)
        desc['标题'] = resp["app"]["videoInfoRes"]["item_list"][0]['desc']
        list_titles = ["作品id", "时间", "标题", "格式", "收藏", "评论", "点赞", "分享"]
        values_tuple = ()
        iiia = ""
        for iii in list_titles:
            iiia = iiia + iii + ":" + str(desc[iii]) + "\n"
            values_tuple += (str(desc[iii]),)
        # table.insert('', 0, values=values_tuple)
        video_url = resp["app"]["videoInfoRes"]["item_list"][0]["video"]["play_addr"]["url_list"][
            0].replace("playwm", "play").replace("720p", "1080p")
        content = get(video_url).content
        with open(f"{file}/{desc['作品id']}.mp4", "wb") as f:
            f.write(content)
    if "note" in url:
        url = url.replace("=", "")
        aweme_id = findall('note/(\d+)', url)[0]
        url = f"https://www.iesdouyin.com/share/note/{aweme_id}"
        resp = get(url, headers=headers).text.encode('gbk', errors='ignore').decode('gbk')
        html = etree.HTML(resp)
        resp = html.xpath('/html/body/script[@id="RENDER_DATA"]/text()')[0]
        resp = unquote(resp).encode('gbk', errors='ignore').decode('gbk')
        resp = json.loads(resp)
        desc = resp["app"]["videoInfoRes"]["item_list"][0]["statistics"]
        desc['收藏'] = desc.pop('collect_count')
        desc['评论'] = desc.pop('comment_count')
        desc['点赞'] = desc.pop('digg_count')
        desc['分享'] = desc.pop('share_count')
        desc['格式'] = "note"
        desc.pop("play_count")
        desc['作品id'] = str(resp["app"]["videoInfoRes"]["item_list"][0]["aweme_id"])
        time_1 = int(resp["app"]["videoInfoRes"]["item_list"][0]["create_time"])
        time_2 = localtime(time_1)
        # 转换成新的时间格式
        desc['时间'] = strftime("%Y-%m-%d %H:%M:%S", time_2)
        desc['标题'] = resp["app"]["videoInfoRes"]["item_list"][0]['desc']
        list_titles = ["作品id", "时间", "标题", "格式", "收藏", "评论", "点赞", "分享"]
        values_tuple = ()
        iiia = ""
        for iii in list_titles:
            iiia = iiia + iii + ":" + str(desc[iii]) + "\n"
            values_tuple += (str(desc[iii]),)
        # table.insert('', 0, values=values_tuple)
        s = 0
        for i in resp["app"]["videoInfoRes"]["item_list"][0]["images"]:
            s += 1
            image_url = i["url_list"][-1]
            content = get(image_url).content
            with open(f"{file}/{desc['作品id']}_{str(s)}.jpeg", "wb") as f:
                f.write(content)
    try:
        printt(iiia)
    except:
        pass


def printt(msg):
    def now():
        time_1 = int(time())
        # 转换成localtime
        time_2 = localtime(time_1)
        # 转换成新的时间格式
        file = strftime("%Y-%m-%d", time_2)
        nows = strftime("%H:%M:%S", time_2)
        return nows

    msgs = msg.split("\n")
    for i in msgs:
        print("[" + str(now()) + "] " + str(i))


def now():
    time_1 = int(time())
    # 转换成localtime
    time_2 = localtime(time_1)
    # 转换成新的时间格式
    nows = strftime("%Y-%m-%d %H:%M:%S", time_2)
    return nows


def configs():
    while True:
        if not path.exists("config.json"):
            configg = {
                "spider_setting": {
                    "线程数": 1,
                    "下载图片": 1,
                    "下载视频": 1,
                    "视频背景音乐": 1,
                    "视频缩略图": 1,
                    "视频封面": 1,
                    "储存格式": 1,
                },
                "csv_setting": {
                    "视频数据": 1,
                    "图文数据": 1,
                    "作品id": 1,
                    "时间": 1,
                    "标题": 1,
                    "格式": 1,
                    "收藏": 1,
                    "评论": 1,
                    "点赞": 1,
                    "分享": 1,
                    "分享链接": 1,
                    "无水印链接": 0,
                    "开关": 1
                },
                "cookie": r""""""
            }
            with open('config.json', 'w+') as f:
                dump(configg, f, indent=4, ensure_ascii=False)
        if not path.exists("cache.json"):
            with open("cache.json", 'w') as f:
                a = {'TOM': '初始项'}
                dump(a, f, ensure_ascii=False, indent=4, sort_keys=True)
        with open("config.json", "r") as f:
            configg = f.read()
        a = configg.find("\"cookie\": \"")
        b = len(configg)
        cookie = configg[a + 11:int(len(configg)) - 3]
        configg = loads(configg[:a + 11] + configg[int(len(configg)) - 3:])
        configg["cookie"] = cookie
        if len(configg["csv_setting"]) < 13:
            os.remove("config.json")
            printt("重置config.json文件中")
        else:
            break
    return configg


def get_tt():
    url = "https://ttwid.bytedance.com/ttwid/union/register/"
    json = {"region": "cn", "aid": 1768, "needFid": "false", "service": "www.ixigua.com",
            "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": "true"}
    response = post(url, json=json)
    tt = response.cookies.get_dict()['ttwid']
    return tt


def get_machine_code():
    code = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return str(code)


def main():
    printt(now())
    ex = 1
    config = configs()
    cookie = config["cookie"]
    printt("当前版本号5.26")
    printt("设备码：" + get_machine_code())
    if len(config["cookie"]) == 0:
        printt("config.json未填cookie")
        input("回车退出")
        exit()
    XBogus_api = "http://xbogus.tom14.top/?form="
    if ex:
        a = input('输入主页链接或作品链接(多个链接用|隔开，回车直接读取url.json文件):')
        b = input('请输入要采集的作品数,为1即解析最近更新的,其他数即从现在往上爬取,直接回车即爬取全部作品\n请输入:')
        if b == '':
            b = '∞'
        if a != '':
            with open('url.json', 'w') as f:
                f.write(a)
        with open('url.json', 'r') as f:
            url = f.read()
            urls = url.split('|')
        d = config["spider_setting"]["线程数"]
        for aa in urls:
            aa = aa.replace('复制此链接，打开Dou音搜索，直接观看视频！', '')
            if "https://www.douyin.com/user/" in aa or "https://www.douyin.com/video/" in aa or "https://www.douyin.com/note" in aa:
                a = aa
            elif "https" not in aa:
                a = ''
            else:
                a = 'https' + findall('https(.*)', aa)[0]
                try:
                    for i in range(2):
                        headers = {
                            "referer": "https://www.douyin.com/",
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
                            "cookie": "ttwid=" + get_tt()
                        }
                        a = head(a, headers=headers).headers['Location']
                except:
                    headers = {
                        "referer": "https://www.douyin.com/",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
                        "cookie": cookie
                    }
                    a = head(a, headers=headers).headers['Location']
            if "video" in a or "note" in a:
                printt("检测到{}为作品链接，即将下载作品".format(aa))
                a = a.replace('?previous_page=web_code_link', '').replace('?previous_page=app_code_link', '')
                get_aweme(a, XBogus_api)
            elif "/user/" in a:
                a = findall('user/(.*)\?', a)[0]
                a = a.replace('https://www.douyin.com/user/', '').replace('?previous_page=web_code_link', '').replace(
                    '?previous_page=app_code_link', '')
                printt("检测到{}为主页链接，即将爬取指定数目的作品".format(a))
                c = Task(a, b, int(d), cookie, XBogus_api)
                c.run()
        printt("\n")
        aaaa = input('回车直接退出')
        exit(0)
    else:
        printt("\n\n")
        input('回车直接退出')
        exit(0)


if __name__ == '__main__':
    main()
