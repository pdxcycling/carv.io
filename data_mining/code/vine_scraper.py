import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import urllib

class VineScraper(object):
    """
    Main class for scraping data from Vine

    Potential target URLs for scraping:
    https://vine.co/tags/snowboarding
    https://vine.co/api/timelines/tags/snowboarding?page=5&anchor=1281492978820640768&size=20
    """
    ## Static class variables
    max_results_per_page = 20

    def __init__(self, rate_limit=0):
        """
        Default constructor

        ARGS:
            rate_limit: max requests per second
        RETURNS:
            None
        """
        self.dir = "./media"
        ## TODO: incorporate rate limiting in scraping requests
        self.rate_limit = rate_limit
        self.speed_throttle = speed_limit == 0

    def scrape(self, tags, num_records):
        """
        Scrapes Vine search page and downloads all videos matching
        criteria.

        TODO: Change from hard-coded search.

        ARGS:
            tags: hash tags to search for
            num_records: number of records to return
        RETURNS:
            None
        """
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
        """
        Finds video URL(s) in results page, and downloads video locally.

        ARGS:
            results_page: HTML of Vine page
            verbose: verbose output on
        RETURNS:
            None
        """
        d = json.loads(results_page.text)
        for record in d['data']['records']:
            video_url = record['videoUrl']
            if verbose:
                print "Video url: " + video_url
            self._download_from_url(video_url)

    def _download_from_url(self, url):
        """
        Download video from URL
        """
        target_file_name = self.dir + "/" + url.split('/')[-1].split('?')[0]
        urllib.urlretrieve (url, target_file_name)
