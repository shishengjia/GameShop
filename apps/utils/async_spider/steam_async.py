from bs4 import BeautifulSoup as bs
from aiohttp import TCPConnector
import json
import asyncio
import aiohttp
import logging
import pprint
import time
import re

category_info = {
    "leisure": ["%E4%BC%91%E9%97%B2", 20],
    "sports": ["%E4%BD%93%E8%82%B2", 9],
    "adventure": ["%E5%86%92%E9%99%A9", 30],
    "action": ["%E5%8A%A8%E4%BD%9C", 30],
    "moba": ["%E5%A4%A7%E5%9E%8B%E5%A4%9A%E4%BA%BA%E5%9C%A8%E7%BA%BF", 6],
    "simulation": ["%E6%A8%A1%E6%8B%9F", 16],
    "independent": ["%E7%8B%AC%E7%AB%8B", 30],
    "speed": ["%E7%AB%9E%E9%80%9F", 8],
    "strategy": ["%E7%AD%96%E7%95%A5", 30],
    "roleplay": ["%E8%A7%92%E8%89%B2%E6%89%AE%E6%BC%94", 30]
}


class Steam:
    def __init__(self, max_concurrency=50):
        self.url = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/" \
                           "?query=v&start={}&count=15&cc=CN&l=schinese&v=4&tag={}"
        # self.file_name = file_name
        self.game_urls = []
        self.games = {"count": 0, "games": []}
        self.count = 0
        self.bounded_sempahore = asyncio.BoundedSemaphore(max_concurrency)

    async def _http_request_get_game_list(self, url):
        """
        直接获取游戏列表页面的html
        :param url:
        :return:
        """
        async with self.bounded_sempahore:
            try:
                async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
                    async with session.get(url) as response:
                        json_data = await response.read()
                        return json_data
            except Exception as e:
                logging.warning("Exception1: {}".format(e))

    async def _http_request_get_game_detail(self, url):
        """
        获取游戏详情页的html
        :param url:
        :return:
        """
        async with self.bounded_sempahore:
            try:
                async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
                    async with session.get(url) as response:
                        html = await response.read()
                        return html.decode("utf8")
            except Exception as e:
                logging.warning("Exception2: {}".format(e))

    async def _http_request_get_game_comments(self, url):
        """
        获取游戏评论
        :param url:
        :return:
        """
        async with self.bounded_sempahore:
            try:
                async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
                    async with session.get(url) as response:
                        json_data = await response.read()
                        return json_data
            except Exception as e:
                logging.warning("Exception2: {}".format(e))

    async def _http_request_verify_age(self, game_detail_url, game_id):
        """
        年龄验证
        :param game_detail_url:
        :param game_id:
        :return:
        """
        async with self.bounded_sempahore:
            try:
                async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
                    async with session.get(game_detail_url) as response:

                        values = response.cookies.output()

                        session_id = re.findall("sessionid=(.*?);", values)[0]

                        data = {
                            "sessionid": session_id,
                            "ageDay": "11",
                            "ageMonth": "January",
                            "ageYear": "1990",
                        }
                    async with session.post("https://store.steampowered.com/agecheckset/app/{}/".format(game_id),
                                            data=data) as response:
                        html = await response.read()
                        return bs(html, "lxml")
            except Exception as e:
                logging.warning("Exception3: {}".format(e))

    def get_game_info(self, json_data, category):
        """
        解析api返回的数据，提取出游戏相关信息
        :param json_data:
        :param category:
        :return:
        """
        soup = bs(json.loads(json_data)["results_html"], 'lxml')
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
            self.game_urls.append([game_detail_url, (name, game_detail_url, cover_url, price, tags, system, category)])
            self.count += 1
            print("{} games url get".format(self.count))

    async def get_game_detail(self, soup, info, game_id):
        """
        解析游戏详情页
        :param soup: bs(html)
        :param info:
        :param game_id:
        :return:
        """
        try:

            # game shot
            imgs_1080 = [item.get("href").split("url=")[1] for item in
                         soup.select(".highlight_player_item.highlight_screenshot a")]
            if len(imgs_1080) >= 3:
                imgs_1080 = imgs_1080[:3]

            # game desc
            desc = soup.select("#game_area_description")[0].get_text()

            # game release date
            date = soup.select(".glance_ctn_responsive_left .date")[0].get_text().split(" ")[-1]

            # game company
            company = soup.select(".glance_ctn_responsive_left .dev_row #developers_list a")[0].get_text()

            # comments api
            comment_api = "https://store.steampowered.com/appreviews/{}?start_offset=0&day_range=30" \
                          "&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=schinese&l=schinese".format(
                game_id)
            data = await self._http_request_get_game_comments(comment_api)
            comments_soup = bs(json.loads(data)["html"], "lxml")
            comments = [item.get_text().strip() for item in comments_soup.select(".content")]

            name, game_detail_url, cover_url, price, tags, system, category = info

            return name, game_detail_url, cover_url, price, tags, system, category, desc, date, company, imgs_1080, comments
        except Exception as e:
            logging.warning("Exception4: {}".format(e))

    def save(self, info):
        """
        保存数据
        :param info:
        :return:
        """
        name, game_detail_url, cover_url, price, tags, system, category, desc, date, company, imgs_1080, comments = info
        _data = {
            "name": name,
            "category": category,
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

    async def download_one_game(self, url, category):
        """
        处理 一个 游戏列表的获取以及解析
        :param url:
        :param category:
        :return:
        """
        data = await self._http_request_get_game_list(url)
        if data:
            self.get_game_info(data, category)

    async def download_one_game_detail(self, url):
        """
        处理 一个 游戏详情页的获取以及解析
        :param url: [url, game_info]
        :return:
        """
        data = await self._http_request_get_game_detail(url[0])
        if data:
            game_id = url[0].strip("/").split("/")[4]

            # age verify
            if "View Page" in data:
                soup = await self._http_request_verify_age(url[0], game_id)
            else:
                soup = bs(data, "lxml")

            game_data = await self.get_game_detail(soup, url[1], game_id)

            # 过滤掉没有信息的 游戏捆绑包 页面
            if game_data:
                self.save(game_data)

    async def download_multi_game(self, game_list_urls):
        """
        执行 所有 游戏列表获取及解析 任务
        :param game_list_urls: [[url, main_category], ...]
        :return:
        """
        features, results = [], []

        for info in game_list_urls:
            # add jobs
            features.append(self.download_one_game(info[0], info[1]))

        for feature in asyncio.as_completed(features):
            try:
                results.append((await feature))
            except Exception as e:
                logging.warning("Exception5: {}".format(e))

        return results

    async def download_multi_game_detail(self, game_urls):
        """
        执行 所有 游戏详情页获取及解析 任务
        :param game_urls:
        :return:
        """
        features, results = [], []

        for url in game_urls:
            # add jobs
            features.append(self.download_one_game_detail(url))

        for feature in asyncio.as_completed(features):
            try:
                results.append((await feature))
            except Exception as e:
                logging.warning("Exception6: {}".format(e))

        return results

    async def crawl(self, category_info):
        """
        主函数 执行所有任务
        :param _category:
        :return:
        """
        game_list_urls = []
        for key, value in category_info.items():
            game_list_urls.extend([[self.url.format(i * 15, value[0]), key] for i in range(value[1])])

        # 下载游戏基本信息
        await self.download_multi_game(game_list_urls)
        pprint.pprint(self.game_urls)

        # 下载游戏详情
        await self.download_multi_game_detail(self.game_urls)
        pprint.pprint(self.games)


if __name__ == "__main__":
    crawler = Steam(max_concurrency=40)

    start_time = time.time()

    future = asyncio.Task(crawler.crawl(category_info))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    print("Total {} seconds".format(time.time() - start_time))


