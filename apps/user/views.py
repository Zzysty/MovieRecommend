from random import Random
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django import forms
# Create your views here.
from django.views import View
from django.contrib.auth.hashers import make_password
from user.forms import LoginForm, RegisterForm, ForgetForm, ResetForm
from user.models import UserProfile, Avatars
from operation.models import Review, Rating

from django.contrib.auth.hashers import make_password
from apps.utils.email_send import send_register_email
from .forms import UserForm
from .models import EmailVerifyRecord

# 自定义用户验证
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # noinspection PyBroadException
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):
    def get(self, request):
        return render(request, 'index_1.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            # 如果表单验证通过
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request=request, user=user)
                    return HttpResponseRedirect('/')
                else:
                    return render(request, 'test.html', {'msg': '用户不存在'})
            else:
                return render(request, 'sign.html', {"msg": "用户名或密码错误"})
        else:
            return render(request, 'index_1.html', {"msg": login_form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')

class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "index_1.html", {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("username", "")
            try:
                user = UserProfile.objects.get(username=user_name)
            except:
                user = None
            if user is not None:
                return render(request, 'duplicat.html', {"msg": "用户名已存在，注册失败"})
            pass_word = request.POST.get("password", "")
            Email = request.POST.get("email", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.password = make_password(pass_word)
            user_profile.email = Email

            # # 给注册用户随机选择头像
            # avatar_list = [i.id for i in Avatars.objects.all()]
            # user_profile.image = random.choice(avatar_list)
            # print(user_profile.image)

            user_profile.save()
            return render(request, 'ok.html', {"msg": "注册成功，请登录"})
        else:
            return render(request, 'err.html', {"msg": "注册失败"})


class ForgetPwdView(View):
    '''忘记密码'''
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forget.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'success_send.html')
        else:
            return render(request, 'forget.html', {'forget_form': forget_form})


class ResetView(View):
    '''重置密码'''
    def get(self, request, active_code):
        record = EmailVerifyRecord.objects.filter(code=active_code)
        print(record)
        if record:
            for i in record:
                email = i.email
                is_register = UserProfile.objects.filter(email=email)
                if is_register:
                    return render(request, 'pwd_reset.html', {'email': email})
        return redirect('index')

# 因为<form>表单中的路径要是确定的，所以post函数另外定义一个类来完成
class ModifyView(View):
    """重置密码post部分"""
    def post(self, request):
        reset_form = ResetForm(request.POST)
        if reset_form.is_valid():
            pwd1 = request.POST.get('newpwd1', '')
            pwd2 = request.POST.get('newpwd2', '')
            email = request.POST.get('email', '')

            if pwd1 != pwd2:
                return render(request, 'pwd_reset.html', {'msg': '密码不一致！'})
            else:
                # 密码一致，改变数据库密码
                user = UserProfile.objects.get(email=email)
                user.password = make_password(pwd1)
                print(pwd2)
                user.save()
                return redirect('/')
        else:
            email = request.POST.get('email', '')
            return render(request, 'pwd_reset.html', {'msg': reset_form.errors})

class UserInfoView(View):
    def get(self, request):
        rating = Review.objects.filter(user=request.user)
        user_avatar = UserProfile.objects.get(username=request.user)
        avatars = Avatars.objects.all()
        a_l = []
        for avatar in avatars:
            a_l.append({
                "url": avatar.url,
                'id': avatar.id
            })
        return render(request, 'userinfo.html', locals())

class EditUserView(View):
    def post(self, request):
        userinfo = UserProfile.objects.get(username=request.user)
        # print(userinfo)
        userinfo_form = UserForm(request.POST)
        if userinfo_form.is_valid():
            userinfo.username = request.POST.get('username', '')
            userinfo.gender = request.POST.get('gender', '')
            userinfo.location = request.POST.get('location', '')
            userinfo.email = request.POST.get('email', '')
            userinfo.save()
            return HttpResponseRedirect('/userinfo')
            # return render(request, 'userinfo.html')

class EditAvatarView(View):
    def post(self, request):
        userinfo = UserProfile.objects.get(username=request.user)
        userinfo.image = request.POST.get('avatar', '')
        userinfo.save()
        return HttpResponseRedirect('/userinfo')