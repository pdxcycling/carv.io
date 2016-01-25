'''
Quality Metrics:
- Top 3 colors across active scenes
  - These probably need to be binned
- Avg_sat across active scenes
- Avg_val across active scenes

Longest scene:
- All metadata

Most active scene:
- All metadata

Scenes:
- Number of total scenes
- Number of static scenes
- Number of action scenes
- Average duration of scenes

Action:
- Action/(static + action) percentage

Shake:
- Worst shake coeff for static scene
- Duration of worst shake coeff
- Avg shake coeff (weighted by time)
- Avg shake coeff (unweighted by time)
- biggest range of middle 50% (flow_percentile_75 - flow_percentile_25)
- duration of biggest middle 50%
- Average flow angle standard dev
- Worst flow angle standard dev
- Duration of flow angle standard dev

Blur:
- Avg blur
- Max blur
- Duration of max blur
- Blur percentage


Metadata:
All metadata
'''
import pandas as pd
import numpy as np
import re
from collections import defaultdict, Counter

class ModelFeatures(object):
    '''
    '''

    def __init__(self):
        pass

    @staticmethod
    def try_split(x):
        '''
        Helper for get_top_colors
        '''
        try:
            return float(x.split('_')[-1])
        except:
            return ''

    @staticmethod
    def get_top_colors(raw_df):
        '''
        Gah. A big boy function.
        '''
        ## Convert colors strings to floats
        df = raw_df.copy()
        df.reset_index(inplace=True)
        col_names = df.columns
        for col in col_names:
            matches = re.search('top_color_', col)
            if matches:
                #df[col] = df[col].apply(lambda x: try: float(x.split('_')[-1]) except: '')
                df[col] = df[col].apply(ModelFeatures.try_split)

        ## Find column names with colors
        color_columns = []
        col_names = df.columns
        for col in col_names:
            matches = re.search('top_color_', col)
            if matches:
                color_columns.append(col)
        sorted(color_columns)

        top_color_cntr = Counter()
        points = 10
        for col in color_columns:
            row = 0
            for color_str in df[col]:
                #import ipdb; ipdb.set_trace()
                top_color_cntr[color_str] += int(points) * int(df['duration'][row])
                row += 1
            points = points - 1

        top_colors = []
        for k,v in top_color_cntr.most_common(10):
            top_colors.append(k)
        return top_colors

    @staticmethod
    def _weighted_avg(values, weights):
        '''
        '''
        return 1. * np.sum((values * weights)) / weights.sum()

    @staticmethod
    def find_condition():
        pass

    @staticmethod
    def create_features_for_video(metadata_df, scene_df):
        '''
        '''
        feature_df = metadata_df.copy()
        feature_df.reset_index(inplace=True)
        action_df = scene_df[scene_df['is_static_scene'] == 0].copy()
        static_df = scene_df[scene_df['is_static_scene'] == 1].copy()

        ## These probably need to be binned better
        top_colors = ModelFeatures.get_top_colors(action_df)
        for i, color in enumerate(top_colors):
            feature_df['color_' + str(i)] = color

        '''
        Editing analysis
        '''
        # Leads with static scene
        feature_df['static_begin'] = scene_df['is_static_scene'].values[0]
        # Duration
        if feature_df['static_begin'].any() == 1:
            feature_df['static_begin_duration'] = scene_df['duration'].values[0]
        else:
            feature_df['static_begin_duration'] = 0
        # Ends with static scene
        feature_df['static_end'] = scene_df['is_static_scene'].values[-1]
        # Duration
        if feature_df['static_end'].any() == 1:
            feature_df['static_begin_duration'] = scene_df['duration'].values[-1]
        else:
            feature_df['static_begin_duration'] = 0

        '''
        Image quality metrics
        Only for action scenes
        '''
        # Avg_sat across active scenes
        feature_df['avg_sat'] = ModelFeatures._weighted_avg(action_df['avg_sat'], action_df['duration'])
        # Average saturation level of most saturated scene
        feature_df['most_saturated_scene_sat'] = action_df['avg_sat'].max()
        # Average saturation level of least saturated scene
        feature_df['least_saturated_scene_sat'] = action_df['avg_sat'].min()
        # Avg_val across active scenes
        feature_df['avg_val'] = ModelFeatures._weighted_avg(action_df['avg_sat'], action_df['duration'])
        # Average value level of highest V (HSV)scene
        feature_df['most_saturated_scene_sat'] = action_df['avg_val'].max()
        ## Duration??
        # Average value level of lowest V (HSV) scene
        feature_df['least_saturated_scene_sat'] = action_df['avg_val'].min()
        ## Duration??

        '''
        Scenes
        '''
        # Number of total scenes
        feature_df['num_scenes'] = scene_df.shape[0]
        # Number of static scenes
        feature_df['num_static_scenes'] = static_df.shape[0]
        # Number of action scenes
        feature_df['num_action_scenes'] = action_df.shape[0]
        # Average duration of scenes
        feature_df['avg_scene_duration'] = feature_df['duration'] / feature_df['num_scenes']
        # Action scene percentage
        feature_df['action_scene_pct'] = feature_df['num_action_scenes'] / feature_df['num_scenes']
        # Action duration percentage
        feature_df['action_time_pct'] = action_df['duration'].sum() / feature_df['duration']

        '''
        Shake
        '''
        # Worst shake coeff for static scene
        feature_df['max_shake'] = action_df['shake_coeff'].max()
        # Duration of worst shake coeff
        max_shake = feature_df['max_shake'].values[0]
        #print max_shake
        #print action_df
        #print action_df[action_df['shake_coeff'] == max_shake]
        feature_df['max_shake_duration'] = action_df[action_df['shake_coeff'] == max_shake]['duration'].values[0]
        # Avg shake coeff (weighted by time)
        feature_df['avg_shake_weighted'] = ModelFeatures._weighted_avg(action_df['shake_coeff'], action_df['duration'])
        # Avg shake coeff (unweighted by time)
        feature_df['avg_shake_unweighted'] = action_df['shake_coeff'].mean()
        # biggest range of middle 50% (flow_percentile_75 - flow_percentile_25)
        feature_df['max_middle_50%_spread'] = np.max(action_df['flow_percentile_75'] - action_df['flow_percentile_25'])
        # duration of biggest middle 50%
        # feature_df['max_middle_50%_spread_duration'] = None
        # Average flow angle standard dev weighted
        feature_df['avg_flow_angle_std_weighted'] = ModelFeatures._weighted_avg(action_df['flow_angle_std_dev'], action_df['duration'])
        # Average flow angle standard dev unweighted
        feature_df['avg_flow_angle_std_unweighted'] = action_df['flow_angle_std_dev'].mean()
        # largest flow angle standard dev
        feature_df['largest_flow_angle_std_dev'] = action_df['flow_angle_std_dev'].max()
        # Duration of flow angle standard dev
        max_std_dev = feature_df['largest_flow_angle_std_dev'].values[0]
        #print action_df[action_df['flow_angle_std_dev'] == max_std_dev]
        feature_df['largest_flow_angle_std_dev_duration'] = action_df[action_df['flow_angle_std_dev'] == max_std_dev]['duration'].values[0]
        # smallest flow angle standard dev
        feature_df['smallest_flow_angle_std_dev'] = action_df['flow_angle_std_dev'].min()

        '''
        Movement
        '''
        # Number of flow points per action scene
        feature_df['avg_flow_pts_unweighted'] = action_df['avg_flow_pts_per_frame'].mean()
        feature_df['avg_flow_pts_weighted'] = ModelFeatures._weighted_avg(action_df['avg_flow_pts_per_frame'], action_df['duration'])

        '''
        Blur/Sharpness
        '''
        # Avg blur
        feature_df['avg_blur'] = ModelFeatures._weighted_avg(action_df['blur'], action_df['duration'])
        # Percentage of blurry frames
        feature_df['percentage_blurry_frames'] = ModelFeatures._weighted_avg(action_df['blur_pct'], action_df['duration'])

        '''
        Longest scene:
        '''
        # Concatentate all metadata

        '''
        Most active scene:
        '''
        # Concatentate all metadata

        return feature_df

    @staticmethod
    def get_feature_df(metadata_df):
        path = "/Users/fiannacci/data_science_class/project_exploration/machine_learning/"
        feature_df = pd.DataFrame()
        for v_id in metadata_df['id']:
            try:
                ## Note: get rid of relative paths!
                print v_id
                video_scene_df = pd.read_pickle(path + 'model/data/' + v_id + '.analysis.pkl')
                video_meta_df = metadata_df[metadata_df['id'] == v_id]
                video_feature_df = ModelFeatures.create_features_for_video(video_meta_df, video_scene_df)
                feature_df = feature_df.append(video_feature_df, ignore_index=True)
            except:
                print "-I- " + v_id + " had a problem"
        return feature_df
