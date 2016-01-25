from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import urllib
import urllib2
import requests
from selenium.webdriver.common.utils import free_port


class SaveFromScraper(object):
    """
    Web scraper for savefrom.net
    """

    def __init__(self):
        """
        Default constructor

        ARGS:
            None
        RETURNS:
            None
        """
        self.browser = PhantomJS(executable_path='./drivers/phantomjs',
                                 port=free_port())  # Optional argument, if not specified will search path.
        self.timeout = 5 # seconds

    def get_video(self, video_id, url, quality):
        """
        Main function that does heavy lifting
        Select video quality in this function.
        """
        pass

    def _get_html(self, video_id):
        """
        For a given video, returns the HTML for the download page

        ARGS:
            video_id: unique video identifier
        RETURNS:
            Tuple: whether page has loaded, and HTML for page
        """
        url = 'https://www.ssyoutube.com/watch?v=' + video_id ## TODO: remove - this is only for testing
        self.browser.get(url)

        try:
            class_name = "link-download"
            WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located((By.CLASS_NAME, 'link-download')))
            has_loaded = True
            print "Page is ready!"
        except TimeoutException:
            has_loaded = False
            print "Loading took too much time!"

        if has_loaded:
            html = self.browser.page_source
        else:
            html = ""

        return (has_loaded, html)

    def _parse_html(self, html):
        """
        Find the links for downloading the video in the HTML

        ARGS:
            html: web page source
        RETURNS:
            Dictionary containing all links for downloading the video
        """
        link_dict = dict()
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.findAll("a", { "class" : "link-download" }):
            if 'title' in link.attrs:
                title = link.attrs['title'].split(': ')[1]
                url = link.attrs['href']
                link_dict[title] = url
            else:
                pass
        return link_dict

    def _download_file(self, video_id, download_url):
        """
        Download video file from SaveFromNet

        ARGS:
            video_id: unique video identifier
        RETURNS:
            None
        """
        f = urllib2.urlopen(download_url)
        with open(video_id + ".mp4", "wb") as code:
            code.write(f.read())

    def quit(self):
        """
        Quit browser session

        ARGS:
            None
        RETURNS:
            None
        """
        browser.close()
        browser.quit()
