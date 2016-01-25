import numpy as np
import pandas as pd
from frame_analysis import FrameAnalysis
from video_utilities import VideoUtilities
from video_analysis import VideoAnalysis
import cv2


class VideoFeatureExtraction(object):
    """
    Class for running all feature extraction
    """

    def __init__(self):
        """
        Default constructor
        """
        pass

    @staticmethod
    def run(video_id, video):
        '''
        Main function for running all feature extraction steps.
        TODO: move this to "__main__"

        ARGS:
            video_id: unique video identifier
            video: path to video file (mp4 format)
        RETURNS:
            dataframe with frame-by-frame analysis
        '''

        ## Go through every frame in the video and extract features
        cap = cv2.VideoCapture(video)
        frame = None

        ## Output dataframes
        video_df = pd.DataFrame()
        img_quality_df = pd.DataFrame()

        num_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        #num_frames = 3
        debug = 0
        if debug == 0:
            i_frame = 0
            while i_frame < num_frames:
                ## Progress logging
                if i_frame % 100 == 0:
                	print i_frame

                if frame is not None:
                    prev_frame = frame.copy()
                else:
                    prev_frame = None

                ret,frame = cap.read()
                ## If there are no more frames, break out of loop
                if ret == False:
                    break

                frame_series = pd.DataFrame(index=[0])
                frame_series['video_id'] = video_id
                frame_series['frame_number'] = i_frame
                frame_series['time'] = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000.

                ##=======================
                ## Image quality metrics
                ##=======================
                ## Blur
                blur_df = SceneAnalysis.get_blur(frame)

                ## Color Spectrum
                color_df = SceneAnalysis.get_hsv_hists(frame)

                img_quality_df = img_quality_df.append(pd.concat([frame_series, blur_df, color_df], axis=1), ignore_index=True)
                #img_quality_df = img_quality_df.append(frame_series)

                ##=======================
                ## Video/motion metrics
                ##=======================
                ## Optical Flow
                if prev_frame is not None:
                    flow_df = VideoUtilities.optical_flow_on_frame(frame, prev_frame)
                else:
                    flow_df = None

                ## Merge results into single dataframe
                #video_df = video_df.append(pd.concat([frame_series, blur_df, color_df, flow_df], axis=1, ignore_index=True))
                #video_df = video_df.append(frame_series)
                #cat['video_id'] = video_id

                #cat = pd.concat([blur_df, color_df, flow_df], axis=1)
                if flow_df is not None:
                    flow_series = flow_df.copy()
                    ##NOTE: the below code is duplicated above - bad style
                    flow_series['video_id'] = video_id
                    flow_series['frame_number'] = i_frame #cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES-1)
                    flow_series['time'] = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000.
                    #cat = pd.concat([frame_series, cat], axis=1)
                    video_df = video_df.append(flow_series, ignore_index=True)

                i_frame += 1
        else:
            img_quality_df = pd.read_pickle(video_id + '.img_quality.pkl')

        ## After completing the frame-by-frame analysis, run video metrics
        ## scene changes
        scene_change_df = VideoAnalysis.detect_cut(video, img_quality_df['time'])
        img_quality_df['is_scene_transition'] = scene_change_df['is_scene_transition'].copy()

        ## Pickle model and save it to S3 or local directory
        img_quality_df.to_pickle(video_id + '.img_quality.pkl')
        video_df.to_pickle(video_id + '.flow.pkl')
        return img_quality_df, video_df

if __name__ == "__main__":
    video = "../media/CKeLfaOl0Qk.mp4"
    video_df = pd.read_pickle('CKeLfaOl0Qk.img_quality.pkl')
    video_series = video_df['time']
    scene_change_df = VideoAnalysis.detect_cut(video, video_series)
    #print scene_change_df[scene_change_df['is_scene_transition'] == 1]
    video_df['is_scene_transition'] = scene_change_df['is_scene_transition'].copy()
    print video_df[video_df['is_scene_transition'] == 1]
