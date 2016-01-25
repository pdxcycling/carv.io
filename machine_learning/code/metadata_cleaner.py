import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import datetime
from datetime import date, timedelta
from dateutil.parser import parse
from nltk.tokenize import RegexpTokenizer

class MetadataCleaner():
    '''
    '''

    @staticmethod
    def clean(meta_df):
        '''
        '''
        m_df = meta_df.copy()
        # Find videos with more than 50 ratings
        meta_df = meta_df[meta_df['ratingCount'] >= 50].copy()

        ## Translate duration into seconds
        meta_df['duration'] = meta_df['duration'].apply(MetadataCleaner._to_seconds)

        # Translate date into a numeric format, and add these as features
        date_df = meta_df['date'].apply(MetadataCleaner.get_date_features)
        meta_df = pd.concat([meta_df, date_df], axis=1)

        # Drop duplicate columns
        meta_df = meta_df.drop_duplicates('id')

        # Create target variables
        # Creating three classes: good, average, bad
        # Let's use the <20, 20-80, >80 as the bins
        cutoff_lo, cutoff_hi = MetadataCleaner.get_percentiles(meta_df['like_pct'], 20, 80)
        meta_df['target_class'] = meta_df['like_pct'].apply(lambda x: MetadataCleaner.target_bin(x, cutoff_lo, cutoff_hi))

        # Get dummy variables for categories
        meta_df = pd.get_dummies(meta_df, prefix='sport', columns=['sport'])

        return meta_df

    @staticmethod
    def drop_columns(meta_df):
        '''
        '''
        columns_to_drop = ['viewCount',
                           'likeCount',
                           'dislikeCount',
                           'favoriteCount',
                           'commentCount',
                           'ratingCount',
                           'like_pct',
                           'date'
                          ]
        meta_df = meta_df.drop(columns_to_drop, axis=1)
        return meta_df

    @staticmethod
    def text_prep(meta_df):
        pass

    @staticmethod
    def target_bin(like_pct, cutoff_lo, cutoff_hi):
        if like_pct < cutoff_lo:
            cat = 'bad'
        elif like_pct < cutoff_hi:
            cat = 'avg'
        else:
            cat = 'good'
        return cat

    @staticmethod
    def _to_seconds(string):
        '''
        Helper
        '''
        minutes, seconds = (0, 0)
        matches = re.search('(\d+)M', string)
        if matches:
            minutes = float(matches.group(1))

        matches = re.search('(\d+)S', string)
        if matches:
            seconds = float(matches.group(1))

        total_seconds = minutes * 60. + seconds
        return total_seconds

    @staticmethod
    def get_date_features(d):
        out = pd.Series()
        out['date_year'] = parse(d).year
        out['date_day'] = parse(d).day
        out['date_month'] = parse(d).month
        out['date_hour'] = parse(d).hour
        out['date_minute'] = parse(d).minute
        out['date_delta'] = (datetime.datetime.now() - parse(d).replace(tzinfo=None)).days

        return out

    @staticmethod
    def get_percentiles(array, percentile_lo, percentile_hi):
        cutoff_lo = np.percentile(array, percentile_lo)
        cutoff_hi = np.percentile(array, percentile_hi)
        return (cutoff_lo, cutoff_hi)
