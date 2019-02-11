from bs4 import BeautifulSoup as bs
import requests
import json
from selenium import webdriver
from selenium.webdriver.support.select import Select
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class Steam:
    def __init__(self, max_workers, page_num, file_name):
        self.url_leisure = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                           "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E4%BC%91%E9%97%B2"
        self.url_sports = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                          "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E4%BD%93%E8%82%B2"
        self.url_adventure = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                             "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E5%86%92%E9%99%A9"
        self.url_action = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                          "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E5%8A%A8%E4%BD%9C"
        self.url_moba = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                        "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E5%A4%A7%E5%9E%8B%E5%A4%9A%E4%BA%BA%E5%9C%A8%E7%BA%BF"
        self.url_simulation = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                              "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E6%A8%A1%E6%8B%9F"
        self.url_independent= "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/" \
                               "render/?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E7%8B%AC%E7%AB%8B"
        self.url_speed = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                         "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E7%AB%9E%E9%80%9F"
        self.url_strategy = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                            "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E7%AD%96%E7%95%A5"
        self.url_roleplay = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                            "?query=&start={}&count=15&cc=CN&l=schinese&v=4&tag=%E8%A7%92%E8%89%B2%E6%89%AE%E6%BC%94"
        self.page_num = page_num
        self.file_name = file_name
        self.game_urls = []
        self.games = {"count": 0, "games": []}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.game_package = 0

    def download_game(self, url):
        game_list_urls = [url.format(i*15) for i in range(self.page_num)]
        all_tasks = [self.executor.submit(self.get_game_url, game_list_url) for game_list_url in game_list_urls]
        for future in as_completed(all_tasks):
            _data = future.result()

        print("{} game urls loaded, start downloading game".format(len(self.game_urls)))

        # start thread pool
        all_tasks = [self.executor.submit(self.get_game_detail, x[0], x[1]) for x in self.game_urls]
        for future in as_completed(all_tasks):
            _data = future.result()
            # print("get {} page".format(_data))

        with open("./steam_data_" + self.file_name, "w") as f:
            json.dump(self.games, f)
        print("{} games".format(self.games["count"]))
        print("{} game packages".format(self.game_package))

    def get_game_url(self, game_list_url):
        results = requests.get(game_list_url).text
        soup = bs(json.loads(results)["results_html"], 'lxml')
        # get info for each game
        for item in soup.select(".tab_item"):
            name = item.select(".tab_item_name")[0].get_text()
            game_detail_url = item.get("href")
            cover_url = item.select(".tab_item_cap_img")[0].get("src")
            price = item.select(".discount_final_price")[0].get_text().split(" ")[1]
            tags = ",".join([item.get_text().strip(", ") for item in item.select(".top_tag")])
            system = [item.get("class") for item in item.select(".platform_img")]
            if len(system) == 0:
                system = "win"
            else:
                system = ",".join([item[1] for item in system])
            self.game_urls.append([game_detail_url, (name, game_detail_url, cover_url, price, tags, system)])

    def get_game_detail(self, url, info):

        soup = None
        results = requests.get(url).text
        game_id = url.strip("/").split("/")[4]

        # age verify
        if "View Page" in results:
            soup = self.verify_age(url, game_id)
        else:
            soup = bs(results, "lxml")
        try:

            #game shot
            imgs_1080 = [item.get("href").split("url=")[1] for item in soup.select(".highlight_player_item.highlight_screenshot a")]
            if len(imgs_1080) >= 3:
                imgs_1080 = imgs_1080[:3]

            # game desc
            desc = soup.select("#game_area_description")[0].get_text()

            # game release date
            date = soup.select(".glance_ctn_responsive_left .date")[0].get_text().split(" ")[-1]

            # game company
            company = soup.select(".glance_ctn_responsive_left .dev_row #developers_list a")[0].get_text()

            # comments from api
            comment_api = "https://store.steampowered.com/appreviews/{}?start_offset=0&day_range=30" \
                          "&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=schinese&l=schinese".format(
                game_id)
            results = requests.get(comment_api).text
            comments_soup = bs(json.loads(results)["html"], "lxml")
            comments = [item.get_text().strip() for item in comments_soup.select(".content")]

            name, game_detail_url, cover_url, price, tags, system = info

            # save data
            self.save((name, game_detail_url, cover_url, price, tags, system, desc, date, company, comments, imgs_1080))
        except Exception as e:
            self.game_package += 1

    def verify_age(self, game_detail_url, game_id):
        # use requests.Session to keep the session same
        s = requests.Session()
        r = s.get(game_detail_url)
        data = {
            "sessionid": r.cookies.values()[0],
            "ageDay": "11",
            "ageMonth": "January",
            "ageYear": "1990",
        }
        # verify by post
        s.post("https://store.steampowered.com/agecheckset/app/{}/".format(game_id), data=data)
        return bs(s.get(game_detail_url).text, "lxml")

    def save(self, info):
        name, game_detail_url, cover_url, price, tags, system, desc, date, company, comments, imgs_1080 = info
        _data = {
            "name": name,
            "game_detail_url": game_detail_url,
            "cover_url": cover_url,
            "price": int(price),
            "tags": tags,
            "system": system,
            "desc": desc,
            "date": date,
            "company": company,
            "comments": comments,
            "imgs_1080": imgs_1080
        }
        self.games["games"].append(_data)
        self.games["count"] += 1
        print("{} games get!".format(self.games["count"]))


# steam = Steam(max_workers=30, page_num=40, file_name="roleplay")
# steam.download_game(steam.url_roleplay)
# with open("./steam_data_strategy", "r") as f:
#     text = json.load(f)
#     games = text["games"]
#     data = []
#     for item in games:
#         data.append(item["name"])
#     print(len(set(data)))

import os
import pprint
from datetime import datetime
from game.models import Game2, Comment
from GameShop.settings import steam_data_action, steam_data_adventure, steam_data_independent, \
    steam_data_leisure, steam_data_moba, steam_data_role_play, steam_data_simulation, \
    steam_data_racing, steam_data_sports, steam_data_strategy

year = []


def import_data():
    game_data = [steam_data_action, steam_data_adventure, steam_data_independent, steam_data_leisure,
                 steam_data_moba, steam_data_role_play, steam_data_simulation, steam_data_racing,
                 steam_data_sports, steam_data_strategy]
    for index, file in enumerate(game_data, start=1):
        print(index)
        game_list = []
        with open(file, "r") as f:
            games = json.load(f)["games"]
            for item in games:
                if len(item["imgs_1080"]) >= 3 and item["date"] != "16" and item["date"] != "04/04/2019":
                    try:
                        game = Game2(name=item["name"], game_detail_url=item["game_detail_url"], cover_url=item["cover_url"],
                                     price=item["price"], os=item["system"], desc=item["desc"],
                                     release_time=datetime.strptime(item["date"], "%Y"),
                                     game_scree_shot_1=item["imgs_1080"][0],
                                     game_scree_shot_2=item["imgs_1080"][1],
                                     game_scree_shot_3=item["imgs_1080"][2],
                                     tag_id=index
                                     )
                        game_list.append(game)
                    except:
                        pprint.pprint(item)
        Game2.objects.bulk_create(remove_duplicate(game_list))

    comment_list = []
    count = 0
    for index, file in enumerate(game_data, start=1):
        print(index)
        with open(file, "r") as f:
            games = json.load(f)["games"]
            for item in games:
                if len(item["comments"]) == 0:
                    count += 1
                if len(item["imgs_1080"]) >= 3 and item["date"] != "16" and item["date"] != "04/04/2019":
                    try:
                        games = Game2.objects.filter(name=item["name"])
                        for game in games:
                            comment_list.extend([Comment(game_id=game.id, comment=comment) for comment in item["comments"]])
                    except Exception as e:
                        print(e)
                        pprint.pprint(item)

    Comment.objects.bulk_create(comment_list)


def remove_duplicate(game_list):
    names = []
    new_game_list = []
    for item in game_list:
        if item.name not in names:
            names.append(item.name)
            new_game_list.append(item)

    return new_game_list












