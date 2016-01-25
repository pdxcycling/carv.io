"""
Processes video on EC2 worker nodes
"""
import boto
import sys
import os
from boto.s3.key import Key
import re
from os import listdir
from os.path import isfile, join
from video_feature_extraction import VideoFeatureExtraction


def list_completed_videos():
    """
    Helper to find files that have already been analyzed

    Args:
        none
    Returns:
        List of file names that have already been analyzed
    """
    completed_files = []
    path = '../code/'
    files_completed = [f for f in listdir(path) if isfile(join(path, f))]
    for f in files_completed:
        matches = re.search('(\S+)\.flow\.pkl', f)
        if matches:
            v_id = matches.groups(0)[0]
            completed_files.append(v_id)
    return completed_files


if __name__ == '__main__':
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('S3-BUCKET')

    # Connect to S3
    conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)

    # Get list of files in video processing directory
    path = '../videos_to_process/'
    files = [f for f in listdir(path) if isfile(join(path, f))]

    # Get list of files that have already been processed
    videos_completed = list_completed_videos()

    # Run video feature extraction on each file
    feature_extractor = VideoFeatureExtraction()
    for f in files:
        # Get video from filename
        video_id = f.split('.')[0]

        # Skip to next if video has already been processed
        if video_id in videos_completed:
            print "-I- Video already processed"
            continue

        video_path = join(path, f)
        # Run the extractor. This saves file in a pickle, so not capturing
        # returned dataframes.
        feature_extractor.run(video_id, video_path)

        # Save pickled dataframes to S3
        pkl_dir = "/home/ubuntu/code/"
        img_quality_file_path = pkl_dir + '/' + str(video_id) + \
                                '.img_quality.pkl'
        flow_file_path = pkl_dir + '/' + str(video_id) + '.flow.pkl'
        os.system('s3cmd put ' + img_quality_file_path + ' s3://' +
                  bucket_name + '/' + 'img_quality/')
        os.system('s3cmd put ' + flow_file_path + ' s3://' + bucket_name +
                  '/' + 'flow/')
