# -*- encoding: utf-8 -*-
from django import forms

from .models import UserProfile


class LoginForm(forms.Form):

    username = forms.CharField(required=True, error_messages={'required': 'email must'})
    password = forms.CharField(required=True, min_length=6, error_messages={'required': 'password not empty',
                                                                            'min_length': 'no less than 6 characters'})


class RegisterForm(forms.Form):

    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=6, error_messages={'required': 'password not enpty',
                                                                            'min_length': 'no less than 6 characters'})
