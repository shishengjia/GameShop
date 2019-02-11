# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from pure_pagination import Paginator, PageNotAnInteger
import json
import requests

from .models import UserProfile, EmailVerifyCode
from operation.models import UserGame, UserFavorite, Order
from game.models import Game2
from utils.LoginJudge import LoginRequiredMixin
from utils.Alipay import AliPay
from .forms import LoginForm, RegisterForm
from GameShop.settings import private_key_path, ali_pub_key_path
from utils.send_email import send_email


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {"register_form": register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "email exist"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = True
            user_profile.password = make_password(pass_word)
            user_profile.save()
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


class LoginView(View):
    def get(self, request):
         return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "login.html", {"msg": "username or password wrong"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class UserInfoView(View, LoginRequiredMixin):
    def get(self, request, user_id):
        return render(request, 'usercenter_info.html', {"current_page": "user_center"})


class UserFavView(View, LoginRequiredMixin):
    def get(self, request, user_id):
        user_collect = UserFavorite.objects.filter(user_id=user_id)
        game_list = []
        for collect in user_collect:
            fav_game_id = collect.fav_game_id
            game = Game2.objects.get(id=fav_game_id)
            game_list.append(game)

        return render(request, 'usercenter_fav.html', {
            "game_list": game_list,
            "current_page": "user_center"
        })

################################ for my team
class PayView(View):
    def get(self, request, info):
        info = info.split("_")
        from datetime import datetime
        time = datetime.now()
        out_trade_no = str(time.year) + str(time.month) + str(time.day) + str(time.hour) + str(time.minute) + str(
            time.microsecond) + str(request.user.id)
        pay = AliPay(
            appid="2016092100558978",
            # app_notify_url="https://localhost:44322/Home/PaymentResult?desktopWallpaperId={}&paymentId={}".format(info[0], out_trade_no),
            app_notify_url="http://178.128.2.120//userspay_return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,  # 默认False,
            return_url="http://178.128.2.120/userspay_return/"
        )
        import time
        trade_no = str(int(time.time()*1000)) + info[1]
        url = pay.direct_pay(
            subject=info[0],
            out_trade_no=trade_no,
            total_amount=int(info[1]),
            return_url="http://178.128.2.120/userspay_return/"
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return HttpResponseRedirect(re_url)


class PayReturnView_(View):
    def get(self, request):
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        pay = AliPay(
            appid="2016092100558978",
            app_notify_url="http://127.0.0.1:8000/userspay_return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,
            return_url="http://127.0.0.1:8000/userspay_return/"
        )

        verify_result = pay.verify(processed_dict, sign)

        if verify_result is True:
            # generated by merchant
            out_trade_no = processed_dict.get("out_trade_no", None)
            # generated by alipay
            trade_no = processed_dict.get("trade_no", None)


            return HttpResponseRedirect("https://localhost:44322/Home/PaymentResult?out_trade_no={data}".format(data=out_trade_no))
###########################################


class OrderView(View, LoginRequiredMixin):
    def get(self, request):
        pay = AliPay(
            appid="2016092100558978",
            app_notify_url="http://127.0.0.1:8000/userpay_return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,
            return_url="http://127.0.0.1:8000/userpay_return/"
        )
        orders = Order.objects.filter(user=request.user)

        for order in orders:
            if order.pay_status != "TRADE_SUCCESS":
                url = pay.query_by_out_trade_no(order.out_trade_no)
                url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
                response = json.loads(requests.get(url).text)
                if response["alipay_trade_query_response"]["code"] == '10000':
                    if response["alipay_trade_query_response"]["trade_status"] == "WAIT_BUYER_PAY":
                        order.save()
                    else:
                        order.trade_no = json.loads(requests.get(url).text)["alipay_trade_query_response"]["trade_no"]
                        order.pay_time = json.loads(requests.get(url).text)["alipay_trade_query_response"]["send_pay_date"]
                        order.pay_status = response["alipay_trade_query_response"]["trade_status"]
                        order.save()
                else:
                    order.delete()
        orders = Order.objects.filter(user=request.user)

        return render(request, "usercenter_order.html", {
            "orders": orders
        })


class PayView2(View, LoginRequiredMixin):
    def get(self, request, game_id):
        if request.user.id is None:
            return render(request, "login.html")
        game = Game2.objects.get(id=game_id)
        pay = AliPay(
            appid="2016092100558978",
            app_notify_url="http://178.128.2.120:8001/userpay_return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,
            return_url="http://178.128.2.120:8001/userpay_return/"
        )

        try:
            order = Order.objects.get(user=request.user, game=game)
            url = pay.direct_pay(
                subject=game.name,
                out_trade_no=order.out_trade_no,
                total_amount=game.price,
                return_url="http://178.128.2.120:8001/userpay_return/"
            )
            re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        except:
            time = datetime.now()
            out_trade_no = str(time.year) + str(time.month) + str(time.day) + str(time.hour) + str(time.minute) + str(
                time.microsecond) + str(request.user.id)
            order = Order()
            order.user = request.user
            order.out_trade_no = out_trade_no
            order.game = game
            order.order_amount = game.price
            order.save()

            url = pay.direct_pay(
                subject=game.name,
                out_trade_no=out_trade_no,
                total_amount=game.price,
                return_url="http://178.128.2.120:8001/userpay_return/"
            )
            re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return HttpResponseRedirect(re_url)


class PayReturnView(View):
    def get(self, request):
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        pay = AliPay(
            appid="2016092100558978",
            app_notify_url="http://178.128.2.120:8001/userpay_return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,
            return_url="http://178.128.2.120:8001/userpay_return/"
        )

        verify_result = pay.verify(processed_dict, sign)

        if verify_result is True:

            # generated by merchant
            out_trade_no = processed_dict.get("out_trade_no", None)
            # generated by alipay
            trade_no = processed_dict.get("trade_no", None)
            trade_status = processed_dict.get("trade_status", None)

            order = Order.objects.get(out_trade_no=out_trade_no)
            order.pay_status = "success"
            order.trade_no = trade_no
            order.pay_time = datetime.now()
            order.save()

            orders = Order.objects.filter(user=request.user)

            return render(request, 'usercenter_order.html', {
                "current_page": "user_center",
                "orders": orders
            })

    def post(self, request):
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        pay = AliPay(
            appid="2016092100558978",
            app_notify_url="http://178.128.2.120:8001/userpay_return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,
            return_url="http://178.128.2.120:8001/userpay_return/"
        )

        verify_result = pay.verify(processed_dict, sign)

        if verify_result is True:
            # generated by merchant
            out_trade_no = processed_dict.get("out_trade_no", None)
            # generated by alipay
            trade_no = processed_dict.get("trade_no", None)
            trade_status = processed_dict.get("trade_status", None)

            order = Order.objects.get(out_trade_no=out_trade_no)
            order.pay_status = "success"
            order.pay_time = datetime.now()
            order.trade_no = trade_no
            order.save()
            return HttpResponse("success")


class ForgetPassword(View):
    def get(self, request):
        return render(request, "forget_password.html")

    def post(self, request):
        email = request.POST.get("email", "")
        try:
            record = UserProfile.objects.get(email=email)
            send_email(email, 16)
            return render(request, "login.html")
        except:
            return render(request, "forget_password.html", {"msg": "This email has not been registered yet"})


class ResetView(View):
    def get(self, request, code):
        all_records = EmailVerifyCode.objects.filter(code=code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email": email})
        return render(request, "login.html")


class ModifyPassword(View):
    def post(self, request):
        pwd = request.POST.get("password", "")
        pwd_again = request.POST.get("password_again", "")
        email = request.POST.get("email", "")
        if pwd != pwd_again:
            return render(request, "password_reset.html", {"email": email, "msg": "两次密码不一致"})
        user = UserProfile.objects.get(email=email)
        user.password = make_password(pwd_again)
        user.save()
        return render(request, "login.html")



class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))