import pandas as pd
import numpy as np
import re
from collections import Counter
from flow_preprocess import FlowPreprocess

class ScenePostprocess(object):
    """
    Heavy-lifting macro-feature class
    """

    def __init__(self, flow_df, quality_df, remove_transitions=False):
        """
        Default constructor
        Args:
            flow_df: Optical flow dataframe
            quality_df: Image quality dataframe
            remove_transitions: whether to remove frames around
                                scene transitions
        Returns:
            Nothing
        """
        self.flow_df = flow_df.copy()
        self.quality_df = quality_df.copy()
        self.remove_transitions = remove_transitions
        self.is_static = None
        self.duration = self.get_duration()
        self.num_frames = quality_df.shape[0]

        ## Do some rudimentary cleaning of/addding to the flow data
        self.flow_df['distance'] = FlowPreprocess.flow_distances(self.flow_df)
        self.flow_df['angle'] = FlowPreprocess.flow_angles(self.flow_df)

        ## Add scene-centric timestamps
        ## TODO: This has a few issues with actual start times...
        scene_time_offset = self.quality_df['time'].min()

        self.flow_df['time_scene'] = self.flow_df['time'] - scene_time_offset
        self.quality_df['time_scene'] = self.quality_df['time'] - scene_time_offset
        self.min_time_scene = self.quality_df['time_scene'].min()
        self.max_time_scene =self.quality_df['time_scene'].max()
        self.min_frame_num = self.quality_df['frame_number'].min()
        self.max_frame_num = self.quality_df['frame_number'].max()

    def _find_columns_by_name(self, df, name_re):
        """
        Helper function to find binned features by the prefixes in their names

        Args:
            df:         Dataframe
            name_re:    regular expression for finding colmns
        Returns:
            List of columns that have names that match name_re
        """
        output = []
        cols = df.columns
        for c in cols:
            if re.search(name_re, c):
                output.append(c)
        return output

    def get_duration(self):
        """
        Find scene duration (in seconds)

        Args:
            None
        Returns:
            Duration of scene in seconds
        """
        min_time = np.min(self.quality_df['time'])
        max_time = np.max(self.quality_df['time'])
        return max_time - min_time

    def get_avg_blur(self):
        """
        Find average blur across entire scene
        NOTE: The higher the number, the less the blur.
        Args:
            None
        Returns:
            Average blur as single float value
        """
        avg_blur = np.mean(self.quality_df['blur'])
        return avg_blur

    def get_blur_percentage(self, blur_threshold=100):
        """
        Proportion of of frames in scene that are blurry.
        A frame is "blurry" if its average blur is below blur_threshold

        Args:
            blur_threshold: A float value that defines the threshold between
                            blurry and non-blurry
        Returns:
            Flow value of the proportion of the scene's frames that are blurry
        """
        blur_pct = 1. * np.sum(self.quality_df['blur'] < blur_threshold)/self.quality_df.shape[0]
        return blur_pct

    def get_top_colors(self, num_colors=10):
        """
        Find the dominant colors in all frames across the scene
        NOTE:   This can be sped if only a subset of frames are sampled.
                Need to run experiments on the optimal sampling rate.
        TODO:   This approach should be changed in v2.0

        Args:
            num_colors: The number of most common colors to return.
                        This is 10 by default.
        Returns:
            Numpy array containing the most prevalent colors in the scene
        """
        self.num_colors = num_colors
        max_color_array = np.array(str)

        cols = self._find_columns_by_name(self.quality_df, "hue")
        for frame_num in range(self.min_frame_num, self.max_frame_num + 1):
            frame_color_array = self.quality_df[cols].ix[frame_num].sort_values()[::-1].index.values[:self.num_colors]
            max_color_array = np.append(max_color_array, frame_color_array)

        ## Find most common colors
        color_count = Counter(max_color_array)
        return map(lambda x: x[0], color_count.most_common(self.num_colors))

    def _get_values_from_bin_names(self, cols):
        """
        From a list of columns representing bins, return a list of the values
        of those bins

        Args:
            cols: a list of column names of histogram bins
        Returns:
            A list of the value of each bin
        """
        values = []
        for c in cols:
            matches = re.search('_(\d+.\d+)', c)
            if matches:
                values.append(float(matches.groups(0)[0]))
            else:
                ## This should never happen, but just in case...
                values.append(None)
        return values

    def get_avg_saturation(self):
        """
        Find the average saturation across all frames in the scene

        Args:
            None
        Returns:
            A float value of average scene saturation
        """
        cols = self._find_columns_by_name(self.quality_df, "sat")
        vals = self._get_values_from_bin_names(cols)
        sums = self.quality_df[cols].sum()

        avg = np.sum((sums * vals).values)/np.sum(sums)
        return avg

    def get_avg_value(self):
        """
        Find the average value (from HSV colorspace) across
        all frames in the scene

        Args:
            None
        Returns:
            A float value of average scene HSV value
        """
        cols = self._find_columns_by_name(self.quality_df, "val")
        vals = self._get_values_from_bin_names(cols)
        sums = self.quality_df[cols].sum()

        avg = np.sum((sums * vals).values)/np.sum(sums)
        return avg

    def get_pixel_pct(self, col_name, frame_size=(480., 360.)):
        """
        Calculates the number of pixels in a scene are in col_name

        Args:
            col_name: the name of column of interest
            frame_size:
        Returns:
            Proportion of pixels that are in the column of interest
        """
        frame_pixels = frame_size[0] * frame_size[1]
        num_frames = self.quality_df.shape[0]
        total_pixels = frame_pixels * num_frames
        pixel_cnt = np.sum(self.quality_df[col_name])
        return pixel_cnt / total_pixels

    """
    vvv Flow calculations vvv
    """

    def get_flow_percentile(self, percentile=0.5):
        """
        Find the distance traveled by optical flow point,
        filtered by the specified percentile.

        Args:
            percentile: Flow distance percentile to return.
                        Percentile is between 0 and 1.
        Returns:
            A float value of the flow distance
        """
        return self.flow_df['distance'].quantile(percentile)

    def get_avg_flow(self):
        """
        Find the average distance an optical flow point has traveled between
        frames.

        Args:
            None
        Returns:
            A float value of the average distance an optical flow point
            has traveled between frames
        """
        return self.flow_df['distance'].mean()

    def get_shake(self):
        """
        Return the shakiness of the scene. Shake is calculated by finding the
        median distance an optical flow point has traveled in each frame, and
        averaging these values.
        TODO: vector addition.

        Args:
            None.
        Returns:
            A float value representing the shakiness of a scene.
        """
        if not self.flow_df.empty:
            shake = np.mean((self.flow_df.groupby('frame_number').median())['distance'])
        else:
            shake = 0
        return shake

    def get_flow_angle(self):
        """
        Find the average angle of travel of the optical flow points in a scene.

        Args:
            None
        Returns:
            A float value of the average optical flow angle
        """
        return self.flow_df['angle'].mean()

    def get_flow_angle_std_dev(self):
        """
        Find the standard devation of all optical flows in a scene

        Args:
            None
        Returns:
            A float value of the standard deviation of optical flow angle
        """
        return self.flow_df['angle'].std()

    def is_static_scene(self, remove_transitions=False):
        """
        Determines whether or not scene is a static scene (vs. action scene)
        TODO:   Ignore some time around scene transitions because of fades.
                Ensure that scene is long enough.

        Args:
            remove_transitions: remove frames at beginning and end of scene
        Returns:
            A boolean value of whether a scene is static or not.
        """
        is_static = None
        motion_threshold = 1    # one pixel of movement
        total_flow_points = self.flow_df.shape[0]   ## number of frames in range
        thresholded_df = self.flow_df[self.flow_df['distance'] > motion_threshold].copy()

        if thresholded_df.empty:
            is_static = True
        else:
            ## Due to "artsy" transitions, ignore around beginning/end of scene
            if remove_transitions:
                ## Amount of transition time between scenes
                ## This could be a percentage...
                transition_time_buffer = 1 # in seconds

                ## Ensure that scene is long enough to remove buffer from analysis
                if self.max_time_scene > transition_time_buffer:
                    thresholded_df = thresholded_df[thresholded_df['time_scene'] > transition_time_buffer]
                    thresholded_df = thresholded_df[thresholded_df['time_scene'] < self.max_time_scene - transition_time_buffer]
                ## Do not remove transitions if scene is too short
                else:
                    pass

            if not thresholded_df.empty:
                ##moving_flow_points = thresholded_df.shape[0]
                moving_frames = thresholded_df.groupby(by=['frame_number']).mean().shape[0]
            else:
                ##moving_flow_points = 0
                moving_frames = 0
            ##pts_ratio = 1. * moving_flow_points/self.num_frames
            pts_ratio = 1. * moving_frames/self.num_frames

            # less than 1 moving frame per 4 frames
            is_static = pts_ratio < .25

        return is_static

    def num_trackable_points_per_frame(self):
        """
        Find the total number of optical flow points that are trackable per
        frame.
        "Trackability" is defined as being able to find a specific optical
        flow point between frames.

        Args:
            None
        Returns:
            A dataframe with the number of trackable points, by frame.
        """
        return self.flow_df.groupby('frame_number').size()

    def avg_num_trackable_points_per_frame(self):
        """
        Find the average number of optical flow points that are trackable,
        over all frames in the frame.
        "Trackability" is defined as being able to find a specific optical
        flow point between frames.

        Args:
            None
        Returns:
            A float value of the average number of trackable optical flow
            points in all of the scene's frames
        """
        return 1. * len(self.flow_df) / self.num_frames

    def to_df(self):
        """
        Return a dataframe containing all features
        TODO: better type checking

        Args:
            None
        Returns:
            Dataframe with all features
        """
        scene_df = pd.DataFrame(index=[0])

        top_colors = self.get_top_colors()
        for n in range(self.num_colors):
            scene_df['top_color_' + str(n)] = top_colors[n]
        scene_df['avg_sat'] = self.get_avg_saturation()
        scene_df['avg_val'] = self.get_avg_value()
        scene_df['black_pixel_pct'] = self.get_pixel_pct('num_black_pixels')
        scene_df['white_pixel_pct'] = self.get_pixel_pct('num_white_pixels')

        scene_df['flow_percentile_25'] = self.get_flow_percentile(0.25)
        scene_df['flow_percentile_50'] = self.get_flow_percentile(0.25)
        scene_df['flow_percentile_75'] = self.get_flow_percentile(0.25)
        scene_df['flow_avg'] = self.get_avg_flow()
        scene_df['flow_angle'] = self.get_flow_angle()
        scene_df['flow_angle_std_dev'] = self.get_flow_angle_std_dev()
        scene_df['is_static_scene'] = self.is_static_scene()
        ##scene_df['action_peak_in_scene'] = None   # where in scene does no

        scene_df['shake_coeff'] = self.get_shake()
        scene_df['avg_flow_pts_per_frame'] = self.avg_num_trackable_points_per_frame()
        scene_df['blur'] = self.get_avg_blur()
        scene_df['blur_pct'] = self.get_blur_percentage()

        scene_df['duration'] = self.get_duration()

        return scene_df
