"""
This file is used to process videos on AWS.
"""

import boto
import pandas as pd
import numpy as np
import sys
import os
from boto.s3.key import Key
import re
from os import listdir
from os.path import isfile, join
from video_postprocess import VideoPostprocess

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = os.getenv('S3-BUCKET')
conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket = conn.get_bucket(bucket_name)

# Get list of files in video processing directory
path = '../data/'
files = [f for f in listdir(path) if isfile(join(path, f))]

# get list of video ids on the local EC2 instance
id_list = []
for f in files:
    matches = re.search('(\S+)\.flow\.pkl', f)
    if matches:
        v_id = matches.groups(0)[0]
        id_list.append(v_id)

# Run run postprocessing steps on each video on EC2 instance
for v_id in id_list:
    print v_id  # Keep track of progress
    flow_pkl_path = join(path, v_id + '.flow.pkl')
    quality_pkl_path = join(path, v_id + '.img_quality.pkl')
    f_df = pd.read_pickle(flow_pkl_path)
    q_df = pd.read_pickle(quality_pkl_path)

    # Process the video's data, creating a single dataframe
    v = VideoPostprocess(v_id, f_df, q_df)
    v_df = v.to_df()
    v_df.to_pickle("../scene_analysis_results/" + v_id + ".analysis.pkl")

    # TODO: save off results to cloud
    # TODO: create the directories on EC2
    # os.system('s3cmd put ' + img_quality_file_path +
    #           ' s3://' + bucket_name + '/' + 'img_quality/')
    # os.system('s3cmd put ' + flow_file_path +
    #           ' s3://' + bucket_name + '/' + 'flow/')
