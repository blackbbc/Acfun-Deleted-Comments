#encoding: utf-8
'''
Created on 2015-05-18 21:51

author: Yu Zhenchuan
email: yuzhenchuan@delete.so
'''

import time
#from django.views.decorators.csrf import requires_csrf_token
from django.db.models import Q
from django.shortcuts import render_to_response
from django.utils import timezone
from AliModel.models import *
from api.base import *
from django.forms.models import model_to_dict
from django.http import JsonResponse
from api.error_code import *
from api.tools import *
import urllib
import re

#搜索的SQL实例
ac_finder = ac_comments()
#留言的SQL实例
ds_commentor = ds_comments()

#暂时不校验前端POST的csrf
#留言的添加和刷新
def refresh_ds_comments(request):
    #输出数据
    json_result = dict()
    try:
        if request.method == 'GET': #刷新评论
            page = request.GET.get('page', '')
            if len(page) == 0: #page为评论的页数
                page = 0
            else:
                page = int(page)

            #回显数据的操作
            total_comments = int(db_commentdb.objects.all().count()) #获取共有多少留言，用以留言板的page显示
            qs_comments = db_commentdb.objects.all().order_by('-sortDate')[page*10:page*10+10] #只获取一个页面的留言内容
            result_comments = []
            for qs in qs_comments:
                dict_comments = model_to_dict(qs)
                comments2_cid = dict_comments['cid'] #将queryset转换为字典来组成json
                qs_comments2 = db_comment2db.objects.filter(cid=comments2_cid) #获取该留言下的评论
                dict_comments2 = []
                for qs_foo in qs_comments2: #将queryset转换为字典来组成json
                    dict_comments2_foo = model_to_dict(qs_foo)
                    dict_comments2.append(dict_comments2_foo)

                dict_comments['comment2'] = dict_comments2 #将留言下的评论放入该条留言中
                result_comments.append(dict_comments)

            #构造回显的json
            json_result['total'] = total_comments
            json_result['result'] = result_comments
        elif request.method == 'POST': #发送评论
            #获取用户输入数据
            username = request.POST.get('username', '')
            content = request.POST.get('content', '')
            position = request.POST.get('position', '')
            date = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

            #获取请求基础信息
            try:
                ip_address = request.META['REMOTE_ADDR']
            except Exception:
                ip_address = '127.0.0.1'

            #数据清理

            #content = clear_word(content) #过滤敏感词、小广告等，一旦发现，立刻将content置空

            #录入数据的操作
            if len(content) == 0:
                deny_address(ip_address) #惩罚这个IP地址?
                json_result['status'] = 'bad word!'
            else:
                if position == '0': #用户操作为新建一条留言
                    #直接插入数据到留言表即可

                    ds_commentor.new_comment(username, content, date, date)
                else: #用户操作为评论别人的留言
                    #先插入数据到留言评论表'''
                    #再更新留言表的时间即可
                    #这两步要放在一个事务里，否则会出现数据库来不及刷盘的问题
                    ds_commentor.add_comment(position, username, content, date)

    except Exception:
        return JsonResponse(json_result)

    return JsonResponse(json_result)

#首页内容的刷新
def refresh_main_page_view(request):
    json_result = dict()
    sql = '''
            SELECT * FROM (
                SELECT * FROM accomments
                WHERE isDelete = 1
                ORDER BY checkTime DESC
                LIMIT 5
                ) as a
            LEFT JOIN accommentsinfo as b
            ON a.acid = b.id
            '''
    json_result['contents_view'] = ac_finder.search(sql)

    return JsonResponse(json_result)

#搜索关键词检查
pattern_search = re.compile(r'''
    ^ac\d{1,7}$ | ^ab\d{1,7}$ |     #ab1234567
    ^\d{1,7}$ |                     #1234567
    ^带带我$   #带带我
    ''', re.VERBOSE)
#\%E5\%B8\%A6\%E5\%B8\%A6\%E6\%88\%91
#搜索页数检查
pattern_page = re.compile(r'''
    ^\d{1,6}$ |     #0-999999
    ^$              #默认为空表示第一页
    ''', re.VERBOSE)

#获取搜索结果
def get_search_results(request):
    request.encoding = 'utf-8'
    #输出数据
    json_result = dict()
    json_result['total'] = 0
    json_result['result'] = []
    json_result['status'] = 0

    try:
        if request.method != 'POST':
            pass
        else:
            #获取用户输入数据
            search = urllib.unquote(request.POST.get('search', '').encode('utf-8'))
            page = request.POST.get('page', '')

            if pattern_search.search(search) == None:
                json_result['status'] = DS_EINVAL
                json_result['message'] = '<span>格式不对劲哟~</span></br>ac1234567, ab1234567, 1234567, 带带我'
                return JsonResponse(json_result)

            if pattern_page.search(page) == None:
                json_result['status'] = DS_EINVAL
                json_result['message'] = '<span>规格限制</span>最高页数只有999999哟~'
                return JsonResponse(json_result)

            #确定page的值
            if len(page) == 0:
                page = 0
            else:
                page = int(page)

            search_data = ['', '']
            flags = [False, False, False,]
            #获取“带带我”的数据
            if search == '带带我':
                search_data[1] = page
                flags[2] = True
            #获取ac/ab
            else:
                if search.find('ac') == 0:
                    search_data[0] = search[2:]
                    search_data[1] = page
                    flags[0] = True

                if search.find('ab') == 0:
                    search_data[0] = search[2:]
                    search_data[1] = page
                    flags[1] = True

                #既不是ac开头，也不是ab开头，那么我们两个都搜搜看
                if not (flags[0] or flags[1]):
                    search_data[0] = search
                    search_data[1] = page
                    flags[0] = True
                    flags[1] = True

            finder(search_data, json_result, flags)

    except Exception:
        return JsonResponse(json_result)

    return JsonResponse(json_result)

#获取爬虫速度
def get_spider_speed(request):
    #输出数据
    json_result = dict()
    end_time = 0
    now_time = time.mktime(
                    time.strptime(
                        timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '%Y-%m-%d %H:%M:%S'
                    )
                )
    speed = 0
    json_result['speed'] = 0
    json_result['status'] = 'alive'
    try:
        if request.method == 'GET':
            qs_status = db_status.objects.filter(Q(name='acscore')|Q(name='acfunend')) #获取status表的所有信息
            for qs in qs_status:
                dict_qs = model_to_dict(qs)
                if dict_qs['name'] == 'acscore':
                    speed = int(dict_qs['score'])
                elif dict_qs['name'] == 'acfunend':
                    foo_time = time.strptime(str(dict_qs['status']), '%Y-%m-%d %H:%M:%S')
                    end_time = time.mktime(foo_time)

            json_result['speed'] = speed
            if (now_time - end_time) > 1800 :
                json_result['status'] = 'dead'

    except Exception:
        return JsonResponse(json_result)

    return JsonResponse(json_result)

#总搜索器，控制搜索的逻辑
'''
输入定义--list：
    0: 搜索关键词
    1: 搜索页数

输出定义--dict：
    一个Json字典

搜索选择器定义--list：
    0: ac
    1: ab
    2: 带带我
'''
def finder(input, output, flags):
    if flags[0]:
        search_ac(input[0], input[1], output)

    if flags[1]:
        search_ac(-int(input[0]), input[1], output)

    if flags[2]:
        search_foyue(input[1], output)

#ac开头的搜索器
def search_ac(search, page, dict):
    search = int(search)
    page = int(page)

    total_searchs = int(db_ac_contents.objects.filter(acid=search, isDelete=1).count()) #获取共有多少条搜索结果，以进行分页
    sql = '''
            SELECT * FROM (
                SELECT * FROM accomments
                WHERE acid = %s
                AND isDelete = 1
                ORDER BY layer
                LIMIT %s, 10
                ) as a
            LEFT JOIN accommentsinfo as b
            ON a.acid = b.id
            '''
    #构造回显的json
    dict['total'] += total_searchs
    dict['result'] += ac_finder.search(sql, search, page * 10)

#带带我
def search_foyue(page, dict):
    total_searchs = int(db_ac_contents_siji.objects.all().count()) #获取共有多少条搜索结果，以进行分页
    sql = '''
            SELECT * FROM (
                SELECT * FROM accomments_siji
                ORDER BY checkTime DESC
                LIMIT %s, 10
                ) as a
            LEFT JOIN accommentsinfo as b
            ON a.acid = b.id
            '''

    #构造回显的json
    dict['total'] += total_searchs
    dict['result'] += ac_finder.search(sql, page * 10)
