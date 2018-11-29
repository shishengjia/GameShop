# -*- encoding: utf-8 -*-
from random import Random
from django.core.mail import send_mail
from GameShop.settings import EMAIL_FROM
from users.models import EmailVerifyCode


# 生成随机字符串
def generate_random_str(randomlength=8):
    strs = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        strs += chars[random.randint(0, length)]
    return strs


def send_email(email, code_length=16):
    code = generate_random_str(code_length)
    email_verify = EmailVerifyCode()
    email_verify.code = code
    email_verify.email = email
    email_verify.save()

    email_title = "Password Reset"
    email_body = "Reset password: http://127.0.0.1/reset/{0}".format(code)
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    if send_status:
        pass