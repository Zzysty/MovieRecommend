#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author:
@contact: @qq.com
@software: PyCharm 
@file: forms.py 
@time:
"""
from django import forms
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    # requried=True 如果表单中这个值不能为空
    # username 和password的变量名要和request.POST中(也就是html中form中的name名字一致)
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)

class RegisterForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
    email = forms.EmailField(required=True)


# forget.html中，用于验证邮箱格式和验证码
class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})

# reset.html中，用于验证新设的密码长度是否达标
class ResetForm(forms.Form):
    newpwd1 = forms.CharField(required=True, min_length=6, error_messages={'required': '密码不能为空.', 'min_length': "至少6位"})
    newpwd2 = forms.CharField(required=True, min_length=6, error_messages={'required': '密码不能为空.', 'min_length': "至少6位"})

# 用户信息表单
class UserForm(forms.Form):
    username = forms.CharField(required=True)
    gender = forms.CharField(required=True)
    location = forms.CharField(required=False)
    email = forms.EmailField(required=True)
