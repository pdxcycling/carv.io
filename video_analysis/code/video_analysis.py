import cv2
import io
import base64
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE


class VideoAnalysis(object):
    """

    TODO:
    - Define common interfaces on similar functions
    - Define what format video will come in as
    - Probably want a preprocessed dataframe with image, time, (and maybe features)
    """

    def __init__(self):
        """
        Default constructor
        """
        self.features = pd.DataFrame()

    @staticmethod
    def detect_cut(video_file_path, time_pd_series):
        """
        Detect where the scene boundaries ("cuts") are in the video.
        Uses FFMPEG utility.

        Args:
            video_file_path: Path to video file
            time_pd_series: pandas series with timestamps for every frame
        Returns:
            A dataframe of with each frame labeled as whether it is a
            scene boundary.
        """
        ## Create output array, initialize with all zeros
        time_df = pd.DataFrame(time_pd_series)
        time_df.columns = ["time"]
        out_df = time_df.copy()
        out_df['is_scene_transition'] = 0

        ## Use the bash script to call ffprobe, a utility for detecting scene changes
        p = Popen(["bash", "ffprobe_script.bash", video_file_path], stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()

        # Create a dataframe of scene change times
        #import pdb; pdb.set_trace()

        scene_trans_df = pd.DataFrame(output.split()[2:])
        ## Check that scene transitions occur
        if not scene_trans_df.empty:
            scene_trans_df.columns = ["time"]
            scene_trans_df.time = scene_trans_df.time.apply(lambda x: float(x))

            for scene_time in scene_trans_df.time:
                closest_pt = out_df.ix[(time_df.time - scene_time).abs().argsort()[:1]]
                index = int(closest_pt.index[0])
                out_df['is_scene_transition'][index] = 1

        return out_df

    @staticmethod
    def detect_shake(video):
        '''
        Shake detection
        '''
        pass

    @staticmethod
    def detect_blur(video):
        '''
        Detect blur
        '''
        pass

    @staticmethod
    def optical_flow(video):
        '''
        Optical flow - useful for preprocessing
        Should this go here? Or should this be in preprocessing???
        '''
        pass

    @staticmethod
    def synchrony(video):
        '''
        Audio/Visual Synchrony
        '''
        pass

    @staticmethod
    def find_faces(video):
        '''
        Find faces in the images
        '''
        pass
