#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2015-07-29 15:11:25
# Project: Acfun

import json
import time
import datetime
from queue import PriorityQueue
from queue import Empty

import pymysql.cursors
from pyspider.libs.base_handler import *

class SpiderPriorityQueue(PriorityQueue):
    def __init__(self):
        PriorityQueue.__init__(self)
        self.counter = 0

    def put(self, priority, item):
        PriorityQueue.put(self, (priority, self.counter, item))
        self.counter += 1

    def get(self, *args, **kwargs):
        _, _, item = PriorityQueue.get(self, *args, **kwargs)
        return item

class Handler(BaseHandler):
    """
    Pyspider
    """

    crawl_config = {
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36',
            'deviceType': "1"
        }
    }

    MAX_NUM = 1500

    API_GET_COMMENT = 'http://www.acfun.tv/comment_list_json.aspx?contentId='
    API_GET_INFO = 'http://www.acfun.tv/api/content.aspx?query='
    VIDEO_URL = 'http://www.acfun.tv/v/ac'
    ARTICLE_URL = 'http://www.acfun.tv/a/ac'

    channel_ids = list()
    ACIDS_list = list()
    ACIDS_set = set()

    queue = SpiderPriorityQueue()

    USE_PROXY = False

    @every(seconds=10)
    def looper(self):
        while True:
            try:
                # 出队
                request = self.__class__.queue.get(False)
                if request['acid'] not in self.__class__.ACIDS_set:
                    continue
                elif int(time.time())-request['updatetime']-request['age'] >= 0:
                    url = 'http://www.acfun.tv/comment_list_json.aspx?contentId=' + \
                           str(request['acid']) + '&currentPage=1'
                    self.crawl(url,
                               callback=self.parse_first_comment,
                               age=request['age'],
                               save={'request':request},
                               proxy=Proxy.get_proxy())
                else:
                    # 进队
                    self.__class__.queue.put(
                        request['updatetime']+request['age'],
                        request)
                    return
            except Empty:
                return

    def update_proxy(self):
        """
        每隔10分钟刷新代理
        """
        self.crawl("http://proxylist.hidemyass.com/search-1298218", callback=self.parse_proxy_page, \
                   age=10*60, priority=10000)

    def parse_proxy_page(self, response):
        """
        解析代理页面
        """

        Proxy.PROXY_LIST = []
        Proxy.PROXY_INDEX = 0

        for each in response.doc('tbody>tr').items():
            available_proxy = {
                "ip": each("td").eq(0).text(),
                "port": each("td").eq(1).text()
            }
            Proxy.PROXY_LIST.append(available_proxy)

    def add_to_queue(self, acid):
        """
        更新队列
        """
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                self.__class__.ACIDS_list.append(acid)
                self.__class__.ACIDS_set.add(acid)

                # 新的请求
                request = {
                    'acid':acid,
                    'updatetime':0, #立刻爬
                    'age':60,
                    'total':0,
                    'times':0
                }

                # 进队
                self.__class__.queue.put(
                    request['updatetime']+request['age'],
                    request)

                #添加到数据库中
                sql = "INSERT INTO `acid_queue`(`acid`, `updatetime`, `age`, `total`, `times`) VALUES (%s, %s, %s, %s, %s) \
                       ON DUPLICATE KEY UPDATE `acid`=VALUES(`acid`), `updatetime`=VALUES(`updatetime`), `age`=VALUES(`age`), `total`=VALUES(`total`), `times`=VALUES(`times`)"
                cursor.execute(sql, (request['acid'], request['updatetime'], request['age'], request['total'], request['times']))

                while len(self.__class__.ACIDS_list) > self.MAX_NUM:
                    poped_acid = self.__class__.ACIDS_list.pop(0)
                    self.__class__.ACIDS_set.discard(poped_acid)

                    #从数据库中删除
                    sql = "DELETE FROM `acid_queue` WHERE `acid` = %s"
                    cursor.execute(sql, poped_acid)

                connection.commit()
        finally:
            connection.close()

    def update_request(self, request):
        """
        更新Request
        """
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        # 进队
        self.__class__.queue.put(
            request['updatetime']+request['age'],
            request)

        try:
            with connection.cursor() as cursor:

                #添加到数据库中
                sql = "INSERT INTO `acid_queue`(`acid`, `updatetime`, `age`, `total`, `times`) VALUES (%s, %s, %s, %s, %s) \
                       ON DUPLICATE KEY UPDATE `acid`=VALUES(`acid`), `updatetime`=VALUES(`updatetime`), `age`=VALUES(`age`), `total`=VALUES(`total`), `times`=VALUES(`times`)"
                cursor.execute(sql, (request['acid'], request['updatetime'], request['age'], request['total'], request['times']))

                connection.commit()
        finally:
            connection.close()

    def init_spider(self):
        """
        初始化队列
        """
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM `acid_queue` ORDER BY `acid` ASC"
                cursor.execute(sql)
                result = cursor.fetchall()
                for item in result:
                    self.__class__.ACIDS_list.append(item['acid'])
                    self.__class__.ACIDS_set.add(item['acid'])
                    self.__class__.queue.put(
                            item['updatetime']+item['age'],
                            item)
        finally:
            connection.close()

        self.__class__.channel_ids = [
            Utils.ARTICLE_COLLECTION,
            Utils.ARTICLE_WORK_EMOTION,
            Utils.ARTICLE_AN_CULTURE,
            Utils.ARTICLE_COMIC_LIGHT_NOVEL,
            Utils.ARTICLE_GAME
        ]

    def on_start(self):
        """
        入口函数
        """

        if len(self.__class__.ACIDS_list) == 0:
            self.init_spider()

        self.looper()

    #每隔三分钟刷新一次
    @every(minutes=3)
    def crawl_channel(self):

        #刷新代理池
        if self.USE_PROXY:
            self.update_proxy()

        #刷新频道信息
        for channel_id in self.__class__.channel_ids:
            url = Utils.get_channel_url(channel_id, 1)
            self.crawl(url,
                       callback=self.parse_channel_page,
                       force_update=True,
                       priority=10,
                       proxy=Proxy.get_proxy())

    def parse_channel_page(self, response):
        """
        解析频道页
        爬第1页评论
        """
        json_data = json.loads(response.text)
        infos = json_data['data']['page']['list']

        for info in infos:
            ac_id = info['contentId']
            ac_user_id = info['user']['userId']
            ac_type = Utils.CHANNEL_NAME[str(info['channelId'])]
            ac_title = info['title']
            ac_up = info['user']['username']
            ac_post_time = datetime.datetime.fromtimestamp(info['releaseDate'] / 1000)
            ac_url = self.ARTICLE_URL + str(ac_id)

            if ac_id not in self.__class__.ACIDS_set:
                self.add_to_queue(ac_id)

                #没问题
                accommentsinfo = Accommentsinfo(ac_id, ac_user_id, ac_type, \
                                                ac_title, ac_up, ac_post_time, ac_url)
                #存一下
                accommentsinfo.save()

    def parse_first_comment(self, response):
        """
        解析评论第一页
        分发其他页评论
        """
        request = response.save['request']
        acid = request['acid']

        json_data = json.loads(response.text)
        total_page = int(json_data['data']['totalPage'])
        total_count = int(json_data['data']['totalCount'])
        comments = json_data['data']['commentContentArr']

        #更新age，继续爬
        delta = total_count - request['total']
        request['times'] += 1
        request['total'] = total_count
        request['updatetime'] = int(time.time())
        if delta == 0:
            request['age'] = min(180, request['age'] * 1.1)
        else:
            request['age'] = max(10, request['age'] * 0.8 + (request['age'] / delta) * 0.1)
        self.update_request(request)

        #首先分发其他页评论
        for page in range(2, total_page+1):
            url = 'http://www.acfun.tv/comment_list_json.aspx?contentId=' + \
                  str(acid) + '&currentPage=' + str(page)
            self.crawl(url, callback=self.parge_comment, age=30*60,
                       save={'acid':acid},
                       proxy=Proxy.get_proxy())

        #然后解析第一页评论
        return self.analyze_comment(acid, comments)


    def parge_comment(self, response):
        """
        解析评论页面
        """
        acid = response.save['acid']

        """
        检查是否删除
        否-->更新数据库
        是-->检查数据库
        """
        json_data = json.loads(response.text)
        comments = json_data['data']['commentContentArr']

        return self.analyze_comment(acid, comments)


    def analyze_comment(self, acid, comments):
        """
        分析评论
        """
        analyze_result = None

        for ccid, comment in comments.items():
            ccid = int(ccid[1:])
            new_comment = Accomments(ccid, acid)

            ac_user_id = comment['userID']
            if ac_user_id != -1:
                new_comment.set_content(comment['content'])
                new_comment.set_user_name(comment['userName'])
                new_comment.set_layer(comment['count'])
                self.check_siji(new_comment)
                new_comment.save()
            else:
                url = "http://www.acfun.tv/a/ac" + str(acid)
                #A fatal bug! Do not return immediately!
                analyze_result = self.update_delete(ccid, url)

        return analyze_result

    def update_delete(self, cid, url):
        """
        更新delete
        """
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM `accomments` WHERE `cid`=%s AND isDelete != 1 "
                cursor.execute(sql, (cid))
                result = cursor.fetchone()
                if result != None:
                    sql = "UPDATE `accomments` SET isDelete=1, checkTime=%s WHERE cid=%s"
                    cursor.execute(sql, (str(datetime.datetime.now()), cid))
                    sql = "INSERT INTO `accomments_delete`(`cid`, `content`, `userName`, `layer`, `acid`, `isDelete`, `siji`, `checkTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
                           ON DUPLICATE KEY UPDATE content=content, userName=userName, layer=layer, acid=acid, isDelete=isDelete, siji=siji, checkTime=VALUES(checkTime) "
                    cursor.execute(sql, (result['cid'], result['content'], result['userName'], result['layer'], result['acid'], 1, result['siji'], result['checkTime']))
                    connection.commit()

        finally:
            connection.close()

        if result != None:
            result['checkTime'] = result['checkTime'].strftime("%Y-%m-%d %H:%M:%S")
            result['url'] = url
            result.pop('isDelete', None)

        return result

    def check_siji(self, comment):
        """
        检查是否老司机
        """
        if comment.get_content().find(u"佛曰：") > -1 \
        or comment.get_content().find(u"如是我闻：") > -1 \
        or comment.get_content().find(u"*：") > -1:
            comment.set_siji(1)
        elif comment.get_content().find(u"ed2k://") > -1:
            #linkUrl = "ed2k:" + comment.get_content()[comment.get_content().find(u"ed2k://"):]
            #encodedContent = comment.get_content().replace(self.encodeFoyu(linkUrl),linkUrl,1)
            #comment.set_content(encodedContent)
            comment.set_siji(1)
        elif comment.get_content().find(u"magnet:?") > -1:
            #linkUrl = "magnet:?" + comment.get_content()[comment.get_content().find(u"magnet:?"):]
            #encodedContent = comment.get_content().replace(self.encodeFoyu(linkUrl),linkUrl,1)
            #comment.set_content(encodedContent)
            comment.set_siji(1)
        else:
            comment.set_siji(0)

class Accommentsinfo(object):
    """
    文章/视频/番剧信息
    """

    def __init__(self, ac_id, ac_user_id, ac_type, ac_title, ac_up, ac_post_time, ac_url):
        self.info = {}
        self.info['id'] = int(ac_id)
        self.info['userId'] = int(ac_user_id)
        self.info['type'] = ac_type
        self.info['title'] = ac_title
        self.info['up'] = ac_up
        self.info['postTime'] = ac_post_time
        self.info['url'] = ac_url

    def get_info(self):
        return self.info

    def set_id(self, ac_id):
        self.info['id'] = int(ac_id)

    def set_user_id(self, ac_user_id):
        self.info['userId'] = ac_user_id

    def set_type(self, ac_type):
        self.info['type'] = ac_type

    def set_title(self, ac_title):
        self.info['title'] = ac_title

    def set_up(self, ac_up):
        self.info['up'] = ac_up

    def set_postTime(self, ac_post_time):
        self.info['postTime'] = ac_post_time

    def set_url(self, ac_url):
        self.info['url'] = ac_url

    def save(self):
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `accommentsinfo`(`id`, `userId`, `type`, `title`, `up`, `postTime`, `url`) VALUES (%s, %s, %s, %s, %s, %s, %s) \
                       ON DUPLICATE KEY UPDATE type=type, title=title, up=up, postTime=postTime, url=url"
                cursor.execute(sql, (self.info['id'], self.info['userId'], self.info['type'], self.info['title'], self.info['up'], self.info['postTime'], self.info['url']))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

        finally:
            connection.close()


class Accomments(object):
    """
    评论信息
    """

    def __init__(self, ac_cid, ac_acid):
        self.info = {}
        self.info['cid'] = int(ac_cid)
        self.info['acid'] = int(ac_acid)
        self.info['checkTime'] = str(datetime.datetime.now())
        self.info['isDelete'] = 0

    def get_info(self):
        return self.info

    def get_content(self):
        return self.info['content']

    def set_content(self, ac_content):
        self.info['content'] = ac_content

    def set_user_name(self, ac_user_name):
        self.info['userName'] = ac_user_name

    def set_layer(self, ac_layer):
        self.info['layer'] = int(ac_layer)

    def set_siji(self, ac_siji):
        self.info['siji'] = int(ac_siji)
        if ac_siji == 1:
            self.save_siji()

    def save(self):
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `accomments`(`cid`, `content`, `userName`, `layer`, `acid`, `isDelete`, `siji`, `checkTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
                       ON DUPLICATE KEY UPDATE content=content, userName=userName, layer=layer, acid=acid, isDelete=isDelete, siji=siji, checkTime=VALUES(checkTime) "
                cursor.execute(sql, (self.info['cid'], self.info['content'], self.info['userName'], self.info['layer'], self.info['acid'], self.info['isDelete'], self.info['siji'], self.info['checkTime']))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

        finally:
            connection.close()

    def save_delete(self):
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `accomments_delete`(`cid`, `content`, `userName`, `layer`, `acid`, `isDelete`, `siji`, `checkTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
                       ON DUPLICATE KEY UPDATE content=content, userName=userName, layer=layer, acid=acid, isDelete=isDelete, siji=siji, checkTime=VALUES(checkTime) "
                cursor.execute(sql, (self.info['cid'], self.info['content'], self.info['userName'], self.info['layer'], self.info['acid'], self.info['isDelete'], self.info['siji'], self.info['checkTime']))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

        finally:
            connection.close()

    def save_siji(self):
        connection = pymysql.connect(host='localhost',
                                     user='deleteso',
                                     passwd='deletepassso',
                                     db='deleteso',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `accomments_siji`(`cid`, `content`, `userName`, `layer`, `acid`, `isDelete`, `siji`, `checkTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
                       ON DUPLICATE KEY UPDATE content=content, userName=userName, layer=layer, acid=acid, isDelete=isDelete, siji=siji, checkTime=VALUES(checkTime) "
                cursor.execute(sql, (self.info['cid'], self.info['content'], self.info['userName'], self.info['layer'], self.info['acid'], self.info['isDelete'], self.info['siji'], self.info['checkTime']))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

        finally:
            connection.close()


class Proxy(object):
    PROXY_LIST = []

    PROXY_INDEX = 0

    @staticmethod
    def get_proxy():
        """
        获取随机代理
        """
        length = len(Proxy.PROXY_LIST)

        if not Handler.USE_PROXY:
            return None

        if length == 0:
            return None

        Proxy.PROXY_INDEX = (Proxy.PROXY_INDEX + 1) % length
        proxy_ip = Proxy.PROXY_LIST[Proxy.PROXY_INDEX]['ip']
        proxy_port = Proxy.PROXY_LIST[Proxy.PROXY_INDEX]['port']
        return proxy_ip + ':' + proxy_port

class Utils(object):
    """
    工具类
    """

    ANIMATION = 1
    MUSIC = 58
    GAME = 59
    FUN = 60
    BANGUMI = 67
    VIDEO = 68
    SPORT = 69
    SCIENCE = 70
    FLASH = 71
    MUGEN = 72

    ARTICLE_ARTICLE = 63
    ARTICLE_COLLECTION = 110
    ARTICLE_WORK_EMOTION = 73
    ARTICLE_AN_CULTURE = 74
    ARTICLE_COMIC_LIGHT_NOVEL = 75
    ARTICLE_GAME = 164

    BEST_GAME = 83
    LIVE_OB = 84
    LOL = 85
    FUNY = 86
    PET = 88
    EAT = 89
    MOVIE = 96
    TV = 97
    VARIETY = 98

    PILE = 99
    DOCUMENTARY = 100
    SING = 101
    DANCE = 102
    VOCALOID = 103
    ACG = 104
    POP = 105
    AN_LITE = 106
    MAD_AMV = 107
    MMD_3D = 108
    AN_COMP = 109

    CHANNEL_NAME = {
        '110': '综合',
        '73': '工作·情感',
        '74': '动漫文化',
        '75': '漫画·轻小说',
        '164': '游戏'
    }

    @staticmethod
    def get_channel_url(channel_id, page_no):
        """
        获取频道地址--最新文章
        http://api.aixifan.com/searches/channel?channelIds=110&pageNo=1&pageSize=10&sort=4&range=86400000
        """
        return 'http://api.aixifan.com/searches/channel?channelIds={}&pageNo={}&pageSize=10&sort=4&range=86400000'.format(channel_id, page_no)
