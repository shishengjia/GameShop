# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Q

from pure_pagination import Paginator, PageNotAnInteger

from company.models import GameCompany
from operation.models import UserFavorite, UserGame
from utils.LoginJudge import LoginRequiredMixin
import time
import json
from random import randint
from operation.models import Order
from game.models import GameTag, Game2, Comment
from utils.steam import import_data, remove_duplicate


class GameListView(View):
    def get(self, request):
        # import_data()
        all_game = Game2.objects.all().order_by("tag_id")
        all_tags = GameTag.objects.all()
        all_year = [year for year in range(2000, 2020)]

        key_word = request.GET.get("key_word", "")
        if key_word:
            all_game = all_game.filter(name__icontains=key_word)

        tag_id = request.GET.get("tag", "")
        if tag_id:
            tag_id = int(tag_id)
            all_game = all_game.filter(tag_id=tag_id)

        year_ = request.GET.get("year", "")
        if year_:
            year_ = int(year_)
            all_game = all_game.filter(release_time__year=year_)

        sort = request.GET.get("sort", "")
        if sort:
            if sort == "price":
                all_game = all_game.order_by("price")
                all_game = remove_duplicate(all_game)
            else:
                all_game = all_game.order_by("-price")
                all_game = remove_duplicate(all_game)


        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_game, per_page=15, request=request)
        games = p.page(page)

        return render(request, "index.html", {
            "all_tags": all_tags,
            "games": games,
            "tag_id": tag_id,
            "year_": year_,
            "all_year": all_year,
            "sort": sort,
            "current_page": "game_list"
        })


class GameDetailView(View):
    def get(self, request, game_id):
        game = Game2.objects.get(id=game_id)

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

        comment_objects = Comment.objects.filter(game_id=game_id)
        comments = [item.comment for item in comment_objects]
        if len(comments) >= 3:
            comments = comments[:3]

        return render(request, "game_detail.html",{
            "game": game,
            "has_fav_game": has_fav_game,
            "has_buy": has_buy,
            "current_page": "game_list",
            "comments": comments
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

            return HttpResponse('{"status": "fail","msg": "cancel collect"}',
                                content_type="application/json")
        else:
            if int(fav_id) > 0:
                user_fav = UserFavorite()
                user_fav.user = request.user
                user_fav.fav_game_id = int(fav_id)
                user_fav.save()

                return HttpResponse('{"status": "success","msg": "already collect"}',
                                    content_type="application/json")
            else:
                return HttpResponse('{"status": "fail","msg": "collect error"}',
                                    content_type="application/json")



