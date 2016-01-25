import pandas as pd
import numpy as np
from youtube_scraper import YouTubeScraper
import time
import random
from savefrom_scraper import SaveFromScraper

yt_df = pd.read_pickle('total_sports.pkl')

save_scraper = SaveFromScraper()

for video_id, rc in zip(yt_df[yt_df['ratingCount'] > 50]['id'][434:500], yt_df[yt_df['ratingCount'] > 50]['ratingCount'][434:500]):
    print video_id, rc
    if 0:
        has_loaded, html = save_scraper._get_html(video_id)
        if has_loaded:
            try:
                links = save_scraper._parse_html(html)
                dl_url = links['360p']
                time.sleep(1)
                save_scraper._download_file(video_id=video_id, download_url=dl_url)
                time.sleep(5 + random.randint(2, 5))
            except:
                pass
        else:
            print "Page failed to load"
