# MovieRecommendSystem

使用Django2.2+MySQL,其中MySQL部分支持在线计算

毕设项目
数据集包含MovieLens and 爬虫(猫眼TOP1000)
推荐算法为’协同过滤->基于物品(电影)推荐’
评测指标’对比UserCF | ItemCF 的Precision、Recall、Coverage、Popularity四项指标’
include Django & MySQL & Vue & ElementUI & jQuery & bootstrap

## app

- MovieSizer

- apps

  - movies

    - ContentView
      -  获取所有评论，评分
      -  推荐电影列表
      -  相似度电影列表
    - AddComment
      - 添加评论

  - operation

    - IndexView

      - 返回推荐电影首页的后台数据

    - Index1View

      - 返回系统首页所有数据（1000部电影）
      - 改进后加入分页，使用django的Paginator，每页40部电影，分25页展示

    - 函数

      - refresh

        重新计算该用户的8个推荐，刷新一下推荐列表

      - reCal_normal

        重新执行cal_similar_gry.py 计算电源间相似度

      - recommendForUser

        向用户进行top5推荐。将会显示在电影详情页右侧。
                如果用户已经登陆， 从default和top中进行混合随机推荐
                如果用户没有登陆， 从default中进行推荐

      - calTop8RecommendationsForEveryUser

        基于评价历史的推荐

      - calTop8FavorateMoviesForCurrentUser

        1. 根据review表，统计每个user最喜欢的8部电影（评价数量 >= 8），匹配similarity表，得到8部相似度最高的电影，将推荐结果top8存进Top8Recommend表。
        2. 遍历review表，提取current user的前8个最近评价的电影（根据reviewtime排序）
        3. 这8个电影再按 star 进行排序

        

        

  - user

  

## 页面 templates

### base.html

```django
{% load staticfiles %}
加载静态资源文件
```

```django
{% block title %}
    comedy
{% endblock %}
标题可替换
```

popup	__弹出式广告

```django
{% if request.user.username == 'admin' %}
{#   如果是admin则显示   #}
   <a href="{% url 'reCal_spark' %}" class="login">使用spark重新计算电影相似度</a> 
   <a href="{% url 'reCal_normal' %}" class="login">重新电影计算相似度</a>
{% endif %}
写死给admin
```

#### nav-bar 中 汉堡按钮点击没效果

- 改完，三栏

#### {% block content %}

电影展示的方块，可替换

#### 添加评论的前端Ajax请求在1235行

### index.html

推荐列表的首页

电影列表数据来自 commend_movie，视图函数在operation的 views.py 44行 ；

```
如果用户已经登陆， 从default和top中进行混合随机推荐
如果用户没有登陆， 从default中进行推荐
```

### index_1.html

电影列表首页，包含所有的1000部电影；

结构与 index.html 相同

### content.html

电影详情页面

评分加评论，点send，将两个数据发送到数据库 review 表

#### 冷启动

只有评论和打分数量 大于等于8 ，才进行展示，否则默认推荐，是写死的，在operation的views函数里

### 其余页面不是主要显示页面



> 小功能

数据分页，重置密码(通过发送邮件)
