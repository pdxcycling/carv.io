import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import urllib

class VineScraper(object):
    '''
    Random notes:
    Actually, scrape this url: https://vine.co/tags/snowboarding
    Or this: https://vine.co/api/timelines/tags/snowboarding?page=5&anchor=1281492978820640768&size=20
    '''
    ## Static class variables
    ## TODO: what's the preferred style for variables like this?
    max_results_per_page = 20

    def __init__(self, rate_limit=0):
        '''
        Default constructor
        rate_limit: max requests per second
        '''
        self.dir = "./media"
        ## TODO: incorporate rate limiting in scraping requests
        self.rate_limit = rate_limit
        self.speed_throttle = speed_limit == 0

    def scrape(self, tags, num_records):
        '''
        DESCRIPTION:
        INPUT:
        OUTPUT:
        '''
        ## TODO: tags input is currently unused. Do something with this.
        results = []
        page_size = VineScraper.max_results_per_page ## TODO: hard-coded for now...
        num_pages = num_records / page_size
        for i in range(0, num_pages):
            url = 'https://vine.co/api/timelines/tags/snowboarding?page=' + str(i) + '&size=' + str(page_size)
            # From http://stackoverflow.com/questions/27652543/how-to-use-python-requests-to-fake-a-browser-visit
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response_page = requests.get(url, headers=headers)
            results.append(response_page)

        ## TODO: Why is this loop separate?
        for r_page in results:
            self._get_video_from_html(r_page)

    def _get_video_from_html(self, results_page, verbose=False):
        '''
        Finds video URL(s) in results page
        Returns nothing... or should this be the number of videos successfully scraped?
        '''
        print results_page.text
        d = json.loads(results_page.text)
        for record in d['data']['records']:
            video_url = record['videoUrl']
            if verbose:
                print "Video url: " + video_url
            ## Download video
            self._download_from_url(video_url)

    def _download_from_url(self, url):
        target_file_name = self.dir + "/" + url.split('/')[-1].split('?')[0]
        urllib.urlretrieve (url, target_file_name)
