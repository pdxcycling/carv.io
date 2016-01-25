import pandas as pd
import numpy as np
from scene_postprocess import ScenePostprocess


class VideoPostprocess(object):
    """
    Look at the dataframes (optical flow and image quality) for each video
    and create higher-level features from the frame-by-frame data.

    Questions to consider:
    1. Would random sampling of scenes be as effective as a summary of every scene
    """

    def __init__(self, video_id, flow_df, quality_df):
        """
        Default constructor

        ARGS:
            video_id: unique video identifier
            flow_df: dataframe with optical flow data
            quality_df: dataframe with image quality data
        RETURNS:
            None
        """
        self.video_id = video_id
        self.flow_df = flow_df.copy()
        self.quality_df = quality_df.copy()
        self.scenes = self._split_scenes()

    def _split_scenes(self):
        """
        Split the video up by scenes, and process each scene.

        ARGS:
            None
        RETURNS:
            Returns a list of scene objects
        """
        scene_list = []

        df = self.quality_df
        split_frame_numbers = df[df['is_scene_transition'] == 1]['frame_number'].values
        # Take care of last scene split by appending -1
        split_frame_numbers = np.append(split_frame_numbers, -1)

        ## Handle special case where video is single, continuous scene
        if len(split_frame_numbers) == 0:
            scene_list = [ScenePostprocess(flow_df=self.flow_df, quality_df=self.quality_df)]
        ## Video has multiple scenes
        else:
            i_begin = 0
            for i_end in split_frame_numbers:
                f_df = self._get_frame_range(self.flow_df, i_begin, i_end)
                f_df.reset_index(inplace=True)
                q_df = self._get_frame_range(self.quality_df, i_begin, i_end)
                f_df.reset_index(inplace=True)
                scene_list.append(ScenePostprocess(f_df, q_df))
                i_begin = i_end

        return scene_list

    def _get_frame_range(self, input_df, begin_frame_num, end_frame_num=-1):
        """
        Create a dataframe for a specific range of frames. This is a
        helper function to a helper function.

        ARGS:
            input_df: dataframe to separate
            begin_frame_num: starting frame number
            end_frame_num: ending frame number, non-inclusive
        RETURNS:
            Dataframe containing only frames in given range
        """
        df = input_df.copy()
        df = df[df['frame_number'] >= begin_frame_num]

        if end_frame_num > 0:
            ## non-inclusive interval
            df = df[df['frame_number'] < end_frame_num]
        return df

    def to_df(self):
        """
        Aggregate all scene summary dataframes into a single dataframe

        ARGS:
            None
        RETURNS:
            Dataframe containing a summary of every scene in the video.
        """
        video_df = pd.DataFrame()
        for scene in self.scenes:
            video_df = video_df.append(scene.to_df(), ignore_index=True)

        video_df['video_id'] = self.video_id
        return video_df
