import datetime
import random
from django.shortcuts import render
from .models import MovieInfo
# Create your views here.
from django.views import View

from operation.models import Default5Recommend, Top5Recommend,Review
from user.models import UserProfile
from movies.models import MovieSimilar, MovieInfo
from django.db.models import Q

from django.core.paginator import EmptyPage, Paginator, InvalidPage, PageNotAnInteger

def random_choie(in_movies):
    try:
        user_recommend_movies = random.sample(in_movies, 8)
    except ValueError:
        user_recommend_movies = in_movies
    return user_recommend_movies

def recommendForUser(request):
    """
    向用户进行top5推荐。将会显示在电影详情页右侧。
            如果用户已经登陆， 从default和top中进行混合随机推荐
            如果用户没有登陆， 从default中进行推荐
    :param request:
    :return:
    """
    user = request.user
    user_recommend_movies = None
    default_recommend_movies = Default5Recommend.objects.all()
   
    if user.is_authenticated :
        # 如果用户已经登陆
        user_recommend_movies = Top5Recommend.objects.filter(user_id=user.id)
        # defautl和recommend随机选取5个， 同时避免了recommend不足5个的情况 
        # 如果是新用户，则推荐默认的8部电影
        if user_recommend_movies.count() < 8:
            user_recommend_movies = default_recommend_movies
    else:
        # 如果用户没有登陆
        user_recommend_movies = default_recommend_movies
    return user_recommend_movies

# 分页器
def show_movies(request):
    # 查询所有数据
    movies = MovieInfo.objects.all().order_by('-averating')
    # 使用Paginator模块对数据分页，一页40条数据
    paginator = Paginator(movies, 40)
    # 使用request.GET.get()函数获取uri中的page参数的数值
    page = int(request.GET.get('page', 1))

    # 我们自己定义一个页码的列表，前端显示的时候据根据这列表来动态生成页码
    # 如果当前页码在最前面5个，再往前减去5会出现负值，所以这种情况要固定展示前11个
    if page - 5 < 1:
        page_range = range(1, 12)
    # 如果当前页码在最后面5个，再往后加上5会超出边界，所以这种情况要固定展示最后11个
    elif page + 5 > paginator.num_pages:
        page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
    else:
        page_range = range(page - 5, page + 6)

    try:
        # 通过获取上面的page参数，查询此page是否为整数并且是否可用
        movie_list = paginator.page(page)
    except PageNotAnInteger:
        movie_list = paginator.page(1)
    except (EmptyPage, InvalidPage):
        movie_list = paginator.page(paginator.num_pages)

    return {
        "movie_list": movie_list,
        "page_range": page_range,
    }

class IndexView(View):
    def get(self, request):
        user = request.user
        userid = user.id
        user_recommend_movie = recommendForUser(request=request)
        # print(user_recommend_movie)
        all_movieinfo = MovieInfo.objects.all().order_by('-releasedate')
        movieinfo = all_movieinfo[1:9]
        movietitle = all_movieinfo[1]
        movielatest = all_movieinfo[9:18]
        return render(request, 'index.html', {
            "moiveinfo": movieinfo,
            "movietitle": movietitle,
            "movielatest": movielatest,
            "commend_movie": user_recommend_movie,
        })

class Index1View(View):
    def get(self, request):
        all_movieinfo = MovieInfo.objects.all().order_by('-releasedate')
        # print(all_movieinfo)

        # 使用Paginator模块对数据分页，一页40条数据
        paginator = Paginator(all_movieinfo, 40)
        # 使用request.GET.get()函数获取uri中的page参数的数值
        page = int(request.GET.get('page', 1))

        # 获取当前页前后各3页
        page_range = list(range(max(page - 3, 1), page)) + list(
            range(page, min(page + 3, paginator.num_pages) + 1))
        # 加上省略号
        if page_range[0] - 1 >= 2:
            page_range.insert(0, '...')
        if paginator.num_pages - page_range[-1] >= 2:
            page_range.append('...')
        # 加上首尾页码
        if page_range[0] != 1:
            page_range.insert(0, 1)
        if page_range[-1] != paginator.num_pages:
            page_range.append(paginator.num_pages)

        try:
            # 通过获取上面的page参数，查询此page是否为整数并且是否可用
            movie_list = paginator.page(page)
        except PageNotAnInteger:
            movie_list = paginator.page(1)
        except (EmptyPage, InvalidPage):
            movie_list = paginator.page(paginator.num_pages)

        movieinfo = all_movieinfo[1:9]
        movietitle = all_movieinfo[1]
        movielatest = all_movieinfo[9:18]
        return render(request, 'index_1.html', {
            "moiveinfo": movieinfo,
            "movietitle": movietitle,
            "movielatest": movielatest,
            "all_movie": all_movieinfo,
            "movie_list": movie_list,
            "page_range": page_range,
        })

# 搜索
class SearchView(View):
    def get(self, request):
        search_key = request.GET.get('key', '')
        print(search_key)

        search_movies = MovieInfo.objects.filter(
                Q(moviename__icontains=search_key) | Q(nation__icontains=search_key) |
                Q(directors__icontains=search_key) | Q(leadactors__icontains=search_key))
        # print(search_movies)
        error_msg = None

        if not search_movies:
            error_msg = "没有查询到结果，请重新输入"

        return render(request, 'search.html', {
            "search_movies": search_movies,
            "error_msg": error_msg,
        })

### WeiSG

'''
# 对每个用户进行基于评价历史的推荐
'''
# re-calculate recommendations for every user
def calTop8RecommendationsForEveryUser():
    from user.models import UserProfile
    user_id_all = UserProfile.objects.values_list('id', flat=True)
    
    for current_user_id in user_id_all:
        calTop8FavorateMoviesForCurrentUser(current_user_id)


# re-calculate recommendations for current user
# 根据review表，统计每个user最喜欢的8部电影（评价数量 >= 8），匹配similarity表，得到8部相似度最高的电影，将推荐结果top8存进Top8Recommend表。
# 若评价数量小于8， 
def sortThird(val):
    return val[2]
    
def calTop8FavorateMoviesForCurrentUser(current_user_id):
    
    # 遍历review表，提取current user的前8个最近评价的电影。
    reviews_descend = Review.objects.all().filter(user_id=current_user_id).order_by('-reviewtime')
   
    # 取前8个最近的评价
    if len(reviews_descend) > 50:
        
        # top_list.append(reviews_descend[i].movie_id)
        reviews_descend = reviews_descend[0: 25]
    
    # 对前8个最近的评价按star排序
    # convert query to list
    tuple_list = []
    for review in reviews_descend:
        tuple_ = (review.user_id, review.movie_id, review.star)
        tuple_list.append(tuple_)
        
    tuple_list.sort(key=sortThird, reverse=True)
    
    if len(tuple_list) > 8:
        tuple_list = tuple_list[0: 8]
        
    # 取Movie_id
    top_list = []
    for review in tuple_list:
        top_list.append(review[1])

    # 每个movie_id对应取得similar movie 的个数
    try:
        num_every_top = (8 / len(top_list)) + 1
    except:
        num_every_top = 1
    # 对多个高分评价电影，遍历similarity表，匹配最相似的电影，存储进Top8Recommend表。

    # 8个相似推荐
    recommend_list = []
    for i in range(len(top_list)):
        recommend_queryset = MovieSimilar.objects.filter(Q(item1__in=[top_list[i]]) | Q(item2__in=[top_list[i]])).order_by('-similar')[: num_every_top]
        for item in recommend_queryset:

            # 只推荐8个
            if len(recommend_list) == 8:
                break

            if (item.item1 == top_list[i]) and (item.item2 not in recommend_list):
                recommend_list.append(item.item2)
            if (item.item2 == top_list[i]) and (item.item1 not in recommend_list):
                recommend_list.append(item.item1)
        # 只推荐8个
        if len(recommend_list) == 8:
            break

    # 新用户，个性推荐不足8个
    if len(recommend_list) < 8:
        queryset = Default5Recommend.objects.all()
        for movie in queryset:
            if len(recommend_list) < 8 and movie.movie_id not in recommend_list:
                recommend_list.append(movie.movie_id)
    
    # 将当前用户的往期相似推荐删除
    Top5Recommend.objects.filter(user_id=current_user_id).delete()

    # 将recommend_list 存进 Top8Recommend
    # print ('****------*******\n recommend_list : ',recommend_list)
    for movie_id in recommend_list:
        top5recommend = Top5Recommend()
        movie = MovieInfo.objects.get(id=movie_id)
        user = UserProfile.objects.get(id=current_user_id)
        top5recommend.movie = movie
        top5recommend.user = user
        top5recommend.save()


'''
#  默认推荐部分
'''
# all-categories, latest, average-rating highest
# 前num_category个最新最高评价的各类电影，后8 - num_category个最新的各类电影

def sortAverating(val):
    return val[2]

def sortReleasedata(val):
    return val[1]

def calDefault8Recommendations(request):
    from movies.models import MovieCategory
    categories = MovieCategory.objects.all()

    recommend_list = []
    # first part
    num_category = len(categories)
    # 从评价人数最多的100部电影里，选平均评价最高的50部电影，按时间降序排序，取前4部
    most_rated = MovieInfo.objects.order_by('-numrating')[0:100]   # list
    # convert to tuple_list
    most_rated_tuples = []
    for movie in most_rated:
        tuple_ = (movie.moviename, movie.releasedate, movie.averating)
        most_rated_tuples.append(tuple_)
    # sort by averating
    most_rated_tuples.sort(key=sortAverating, reverse=True)
    highest_rated = most_rated_tuples[0: 50]

    # sort by releasedate
    highest_rated.sort(key=sortReleasedata, reverse=True)
    highest4 = highest_rated[0: 4]
    
    for movie in highest4:
        recommend_list.append(movie[0])

    # scond part
    # 最新的4部电影，注意不要跟前四部有重复的部分
    newest_movies = MovieInfo.objects.order_by('-averating')[0: 16]
    for movie in newest_movies:
        if len(recommend_list) == 8:
            break
        if movie.moviename not in recommend_list:
            recommend_list.append(movie.moviename)
    
    # 将当前默认推荐删除
    Default5Recommend.objects.filter().delete()

    for moviename in recommend_list:
        default5recommend = Default5Recommend()
        default5recommend.movie = MovieInfo.objects.get(moviename=moviename)
        default5recommend.save()
        

# weisg
# refresh

def refresh(request):
    # 用户已经登陆，点击refresh，重新计算该用户的8个推荐；若未登录，不重新计算
    if request.user.is_authenticated:
        current_user_id = request.user.id
        # print('****------*******\n current_user_id = request.user.id')
        calTop8FavorateMoviesForCurrentUser(current_user_id)
    # refresh后，返回给用户的推荐列表，
    # 已登录则返回新的8个推荐，未登录则返回新的default8个。
    calDefault8Recommendations(request)
    user_recommend_movies = recommendForUser(request)
    # movies_len = len(user_recommend_movies)
    # print ('****------*******\nrefresh - user_recommend_movies : ',user_recommend_movies)
    return render(request, 'index.html', {'commend_movie': user_recommend_movies})
    


'''
def reCal_spark(request):
    print ('\n\n\n\n\nfrom base.html reCal_spark')
    

def reCal_normal(request):
    print ('from base.html reCal_normal ')
'''

from operation import cal_similar_gry
# def reCal_spark(request):
#     print('\n\n\n\n\nfrom base.html reCal_spark')
#     cal_similar_gry()
#     return refresh(request)

def reCal_normal(request):
    print('from base.html reCal_normal ')
    cal_similar_gry()
    return refresh(request)
