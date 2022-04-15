"""MovieSizer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.views.static import serve
from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls import url
from operation.views import IndexView, Index1View, SearchView, refresh, calDefault8Recommendations, reCal_normal
from user.views import LoginView, LogoutView, RegisterView
from movies.views import ContentView, AddComment, DelMovie
from user.views import ForgetPwdView, ResetView, ModifyView, UserInfoView, EditUserView, EditAvatarView


urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    # 首页
    path('', Index1View.as_view(), name='index_1'),                             # 首页
    # path('index.html/', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name='index'),                          # 推荐页
    path('login/', LoginView.as_view(), name="login"),                          # 登录
    path('logout/', LogoutView.as_view(), name="logout"),                       # 登出
    path('content/', ContentView.as_view(), name="content",),                   # 内容页
    path('register/', RegisterView.as_view(), name="register",),                # 注册
    path('movieinfo/<int:movie_id>', ContentView.as_view(), name='movieinfo'),  # 内容页
    path('add_comment/', AddComment.as_view(), name='addcomments'),             # 添加评论
    path('del_ratmovie/<int:movie_id>', DelMovie.as_view(), name='del_ratmovie'),             # 删除评论

    path('userinfo/', UserInfoView.as_view(), name='userinfo'),                 # 个人信息
    path('edit_userinfo/', EditUserView.as_view(), name='edit_userinfo'),       # 修改个人信息
    path('edit_avatar/', EditAvatarView.as_view(), name='edit_avatar'),         # 修改头像

    # weisg
    path('index.html/~', refresh, name='refresh'),                              # 刷新页面，更新推荐
    #path('content.html/~', refresh2, name='refresh2')
    #path('index.html/~', calDefault8Recommendations, name = 'refresh')
    # xgm
    # path('base.html/~', reCal_spark, name='reCal_spark'),
    path('index.html/~', reCal_normal, name='reCal_normal'),                    # 重新计算相似


    # 忘记密码
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),                 # 忘记密码
    # 重置密码
    path('reset/<str:active_code>', ResetView.as_view(), name='reset'),          # 重置密码
    path('modify/', ModifyView.as_view(), name='modify'),                        # 修改密码
    path('captcha/', include('captcha.urls')),                                   # 验证码

    # 搜索电影
    path('search/', SearchView.as_view(), name='search'),                        # 搜索电影

    # media配置( 请求图片 )
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
