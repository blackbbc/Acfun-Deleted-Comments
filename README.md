# Delete-So
> 感谢原作者[@小川](https://github.com/yuadsl3010/Delete-So)的源代码
> 本人只是将爬虫用Pyspider重写了一遍 预计性能会更好

###网站地址：[http://162.243.138.81:8000](http://162.243.138.81:8000)


#### 数据结构：
  acid     |  updatetime  |  age  |  total
  ----     |  ----------  |  ---  |  -----
  2707837  |  1462251474  |  300  |  10
  2707885  |  1462251827  |  162  |  5

#### 算法：
```python
if delta == 0:
	age = age * 1.1
else:
	age = age * 0.8 + (age / delta) * 0.1
```

***********
####To do list
- [x] 根据文章评论的增长速度确定爬虫的跟踪时间
- [x] 返回的analyze comment只能返回一条，一条就一条吧！
- [x] project update后所有的变量会被重置？！注释掉project_module.py里_need_update函数中的关于RELOAD_PROJECT_INTERVAL的语句

**********

<p>代码路径：</p>
<p>|--django //网站源码</p>
<p>|--sweet-spider //爬虫源码</p>
<p>|--README.md </p>
<p>最近正在将之前的代码迁移至django上，方面以后网站的拓展</p>
<p>分享想法、乐趣和代码！</p>
***************

###附：可用API
####获取视频信息
http://www.acfun.tv/api/content.aspx?query=1288500

http://api.acfun.tv/apiserver/content/info?contentId=1741857
####获取评论信息
http://www.acfun.tv/comment_list_json.aspx?contentId=1777166&currentPage=1

####获取频道信息
http://api.acfun.tv/apiserver/content/channel?orderBy=1&channelId=110&pageSize=20&pageNo=1

###以下api共用头
```json
"deviceType":"1"
```

####今日查看最多
http://api.aixifan.com/searches/channel?channelIds=110&pageNo=1&pageSize=10&sort=1&range=86400000

####今日评论最多
http://api.aixifan.com/searches/channel?channelIds=110&pageNo=1&pageSize=10&sort=2&range=86400000

####今日收藏最多
http://api.aixifan.com/searches/channel?channelIds=110&pageNo=1&pageSize=10&sort=3&range=86400000

####今日最新文章
http://api.aixifan.com/searches/channel?channelIds=110&pageNo=1&pageSize=10&sort=4&range=86400000

####所有频道信息
```java
    public static final class id {

        public static final int ANIMATION = 1;
        public static final int MUSIC     = 58;
        public static final int GAME      = 59;
        public static final int FUN       = 60;
        public static final int BANGUMI   = 67;
        public static final int VIDEO     = 68;
        public static final int SPORT     = 69;
        public static final int SCIENCE   = 70;
        public static final int FLASH     = 71;
        public static final int MUGEN     = 72;

        public static final class ARTICLE {
            public static final int ARTICLE           = 63;
            public static final int COLLECTION        = 110;
            public static final int WORK_EMOTION      = 73;
            public static final int AN_CULTURE        = 74;
            public static final int COMIC_LIGHT_NOVEL = 75;
        }

        public static final int BEST_GAME   = 83;
        public static final int LIVE_OB     = 84;
        public static final int LOL         = 85;
        public static final int FUNY        = 86;
        public static final int KICHIKU     = 87;
        public static final int PET         = 88;
        public static final int EAT         = 89;
        public static final int MOVIE       = 96;
        public static final int TV          = 97;
        public static final int VARIETY     = 98;
        public static final int PILI        = 99;
        public static final int DOCUMENTARY = 100;
        public static final int SING        = 101;
        public static final int DANCE       = 102;
        public static final int VOCALOID    = 103;
        public static final int ACG         = 104;
        public static final int POP         = 105;
        public static final int AN_LITE     = 106;
        public static final int MAD_AMV     = 107;
        public static final int MMD_3D      = 108;
        public static final int AN_COMP     = 109;
    }
```
