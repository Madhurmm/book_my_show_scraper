# -*- coding: utf-8 -*-
import scrapy
import os
import random


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


class BmsCineDataCookieJarSpider(scrapy.Spider):

    name = 'bms_cine_data_cookiejar'
    allowed_domains = ['bookmyshow.com']

    def start_requests(self):
        list_region_code = read_file('bms_cinema_data/data/', 'bms_region.txt')
        start_urls = list(
            map(lambda region_code: 'https://in.bookmyshow.com/{}/cinemas'.format(region_code), list_region_code))
        #using cookiejar to handle each individual cookie session
        for i, url in enumerate(start_urls):
            yield scrapy.Request(url, meta={'cookiejar': i},
                                 callback=self.parse)

    def parse(self, response):
        id = str(random.randint(100000, 999999))
        web_service_url = "https://in.bookmyshow.com/serv/getData?cmd=QUICKBOOK&type=MT&getRecommendedData=1&={}".format(
            id)

        yield response.follow(web_service_url, callback=self.fetching_cine_data,
                              meta={'cookiejar': response.meta['cookiejar']})

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