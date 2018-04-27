# -*- coding: utf-8 -*-
import scrapy
import os


def read_file(base_path, file_name):
    """" Read file and return List of file contents"""

    file_content = []
    abs_path = os.path.abspath(os.path.join(base_path, file_name))
    with open(abs_path, 'r') as file:
        for line in file:
            file_content.append(line.strip())
    return file_content


def read_json(self, path):
    """"Return json from raw text file"""
    pass


class BmsCineDataSpider(scrapy.Spider):
    custom_settings = {
        'DOWNLOAD_DELAY': 1
    }

    name = 'bms_cine_data'
    allowed_domains = ['bookmyshow.com']
    list_region_code = read_file('bms_cinema_data/data/', 'bms_region.txt')
    start_urls = list(
        map(lambda region_code: 'https://in.bookmyshow.com/{}/cinemas'.format(region_code), list_region_code))

    def parse(self, response):
        web_service_url = "https://in.bookmyshow.com/serv/getData?cmd=QUICKBOOK&type=MT&getRecommendedData=1&_={}"

        # fetch cookies
        cookie_dict = {}
        cookie_list = response.headers.getlist("Set-Cookie")
        for cookie in cookie_list:
            cookie = cookie.decode("utf-8")
            if "mqttsid=" not in cookie and 'Rgn' not in cookie:
                continue
            elif "mqttsid=" in cookie:
                cookie_dict['mqttsid'] = cookie.split(';')[0].split('=')[1]
            elif "Rgn=" in cookie:
                cookie_dict['Rgn'] = cookie.split(';')[0].split('=')[1]

        web_service_url = web_service_url.format(cookie_dict['mqttsid'])

        yield response.follow(web_service_url, callback=self.fetching_cine_data, cookies=cookie_dict)


    def fetching_cine_data(self, response):
        import json
        venue_dict = {}
        data = json.loads(response.body.decode("utf-8"))
        bms_node = data['cinemas']
        aivn_node = bms_node['BookMyShow']
        venue_info_dict = aivn_node['aiVN']
        i = 0
        for venue_info in venue_info_dict:
            info = {
                'name': venue_info['VenueName'],
                'lat': venue_info['VenueLatitude'],
                'long': venue_info['VenueLongitude'],
                'address': venue_info['VenueAddress']
            }
            venue_dict[str(i)] = info
            i += 1

        yield venue_dict
        # yield response.body
