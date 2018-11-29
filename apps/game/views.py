# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Q

from pure_pagination import Paginator, PageNotAnInteger

from .models import Game, GameType
from company.models import GameCompany
from operation.models import UserFavorite, UserGame
from utils.LoginJudge import LoginRequiredMixin
import time
from random import randint
from operation.models import Order


class GameListView(View):
    def get(self, request):
        # a = randint(2,20)
        # # time.sleep(20)
        # print(a)

        all_game = Game.objects.all().order_by("-add_time")
        all_type = GameType.objects.all()
        all_company = GameCompany.objects.all()
        all_year = sorted({year.release_time.year for year in all_game})

        key_word = request.GET.get("key_word", "")
        if key_word:
            all_game = all_game.filter(name__icontains=key_word)

        type_id = request.GET.get("type", "")
        if type_id:
            type_id = int(type_id)
            all_game = all_game.filter(type_id=type_id)

        company_id = request.GET.get("company_id", "")
        if company_id:
            company_id = int(company_id)
            all_game = all_game.filter(company_id=company_id)

        year_ = request.GET.get("year", "")
        if year_:
            year_ = int(year_)
            all_game = all_game.filter(release_time__year=year_)

        sort = request.GET.get("sort", "")
        if sort:
            if sort == "price":
                all_game = all_game.order_by("price")
            elif sort == "price_desc":
                all_game = all_game.order_by("-price")
            else:
                all_game = all_game.order_by("-buy_nums")


        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_game, per_page=7, request=request)
        games = p.page(page)

        return render(request, "index.html", {
            "all_type": all_type,
            "games": games,
            "all_company": all_company,
            "type_id": type_id,
            "company_id": company_id,
            "year_": year_,
            "all_year": all_year,
            "sort": sort,
            "current_page": "game_list"
        })


class GameDetailView(View):
    def get(self, request, game_id):
        game = Game.objects.get(id=game_id)

        has_buy = False
        has_fav_game = False

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_game_id=int(game.id)):
                has_fav_game = True
            try:
                result = Order.objects.get(user=request.user, game=game, pay_status="TRADE_SUCCESS")
                has_buy = True
            except:
                has_buy = False

        return render(request, "game_detail.html",{
            "game": game,
            "has_fav_game": has_fav_game,
            "has_buy":has_buy,
            "current_page": "game_list"
        })


class AddFavoriteView(View, LoginRequiredMixin):
    def post(self, request):
        fav_id = request.POST.get("fav_id", 0)
        if not request.user.is_authenticated:
            return HttpResponse('{"status": "fail","msg": "not login"}',
                                content_type="application/json")

        exit_records = UserFavorite.objects.filter(user=request.user, fav_game_id=int(fav_id))
        if exit_records:
            exit_records.delete()
            game = Game.objects.get(id=int(fav_id))
            game.fav_nums -= 1
            if game.fav_nums < 0:
                game.fav_nums = 0
            game.save()

            return HttpResponse('{"status": "fail","msg": "cancel collect"}',
                                content_type="application/json")
        else:
            if int(fav_id) > 0:
                user_fav = UserFavorite()
                user_fav.user = request.user
                user_fav.fav_game_id = int(fav_id)
                user_fav.save()

                game = Game.objects.get(id=int(fav_id))
                game.fav_nums += 1
                if game.fav_nums < 0:
                    game.fav_nums = 0
                game.save()

                return HttpResponse('{"status": "success","msg": "already collect"}',
                                    content_type="application/json")
            else:
                return HttpResponse('{"status": "fail","msg": "collect error"}',
                                    content_type="application/json")



