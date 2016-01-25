import cv2
import numpy as np
import pandas as pd
import math


class VideoUtilities():
    """
    Standard functions for video cleanup
    """

    @staticmethod
    def get_derivative(video, frame_stride=1):
        """
        Take derivative of video. The derivative is calculated as:
            dx/dt = Frame(n + frame_stride) - Frame(n)

        ARGS:
            video: path to video file
            frame_stride: number of frames to between subtraction operations
        RETURNS:
            Dataframe of the derviatives for the video
        """
        deriv_df = pd.DataFrame()

        cap = cv2.VideoCapture(video)
        ret, frame = cap.read()
        frame = VideoAnalysis._img_preprocess(frame)
        frame_series = pd.Series()
        frame_series['time'] = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000.
        deriv_df.append(frame_series, ignore_index=True)

        while frame is not None:
            prev_frame = frame.copy()
            ## Capture image
            i = 0
            while i < frame_stride:
                ret,frame = cap.read()
                i += 1
            ## TODO: Check that there's actually a frame there
            frame = VideoAnalysis._img_preprocess(frame)

            # Take the difference
            frame_diff = abs(frame - prev_frame)
            frame_series = pd.Series()
            frame_series['time'] = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000.
            ## The following functions should be done elsewherez
            frame_series['deriv_mean'] = frame_diff.mean()
            frame_series['deriv_stdev'] = frame_diff.std()
            frame_series['deriv_image'] = frame_diff

            deriv_df = deriv_df.append(frame_series, ignore_index=True)

        return deriv_df

    @staticmethod
    def optical_flow(video, stride=1, preprocess=True):
        """
        Calculate the optical flow for a video.
        Adapted from http://docs.opencv.org/master/d7/d8b/tutorial_py_lucas_kanade.html#gsc.tab=0

        ARGS:
            video:
            stride:
            preprocess: whether video needs to be put into standardized
                        format
        RETURNS:
            A Pandas DataFrame with feature point coordinates

        TODO: Implement stride
        NOTE: Should the distance calculation be done here?
        NOTE: SHould the direction calculation be done here?
        """
        # params for ShiTomasi corner detection
        feature_params = dict( maxCorners = 50,
                                qualityLevel = 0.5,
                                minDistance = 10,
                                blockSize = 7 )

        # Parameters for lucas kanade optical flow
        lk_params = dict( winSize  = (15,15),
                          maxLevel = 5,
                          criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        # Take first frame and find corners in it
        # cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, start_frame)
        cap = cv2.VideoCapture(video)
        ret, frame = cap.read()
        frame_series = pd.Series()
        frame_series['time'] = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000.

        ## Ensure frame is in a standardized format
        if preprocess:
            frame = VideoUtilities._img_preprocess(frame)
        ## Find feature points to track across frames
        p0 = cv2.goodFeaturesToTrack(frame, mask = None, **feature_params)

        ## Output dataframe
        flow_df = pd.DataFrame()

        num_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        i_frame = 0
        while i_frame < num_frames:
            if i_frame % 100 == 0:
                print i_frame

            prev_frame = frame.copy()
            ret,frame = cap.read()
            ## If there are no more frames, break out of loop
            if ret == False:
                break

            if preprocess:
                frame = VideoUtilities._img_preprocess(frame)

            # calculate optical flow if feature points exist
            if p0 is not None:
                p1, st, err = cv2.calcOpticalFlowPyrLK(prev_frame, frame, p0, None, **lk_params)
            else:
                p1, st, err = (None, None, None)

            # Store the result
            frame_series = pd.Series()
            frame_series['time'] = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000.
            #frame_series['frame_number'] = cap.get(cv2.cv.
            frame_series['pt_pos(t)'] = p1      ## Current position of feature points
            frame_series['pt_pos(t-1)'] = p0    ## Previous position of feature points
            frame_series['st'] = st
            frame_series['err'] = err
            flow_df = flow_df.append(frame_series, ignore_index=True)

            # This has the effect of resetting the points to track
            p0 = cv2.goodFeaturesToTrack(frame, mask = None, **feature_params)
            i_frame += 1

        return flow_df

    @staticmethod
    def optical_flow_on_frame(frame, prev_frame, stride=1, preprocess=True):
        """
        Calculate optical flow between two frames
        Adapted from http://docs.opencv.org/master/d7/d8b/tutorial_py_lucas_kanade.html#gsc.tab=0

        ARGS:
            frame: current frame
            prev_frame:
            stride:
            preprocess:
        RETURNS:
            Returns a Pandas DataFrame with feature point coordinates
        """
        # params for ShiTomasi corner detection
        feature_params = dict( maxCorners = 50,
                                qualityLevel = 0.5,
                                minDistance = 10,
                                blockSize = 7 )

        # Parameters for lucas kanade optical flow
        lk_params = dict( winSize  = (15,15),
                          maxLevel = 5,
                          criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        ## Ensure frame is in a standardized format
        if preprocess:
            frame = VideoUtilities._img_preprocess(frame)
            prev_frame = VideoUtilities._img_preprocess(prev_frame)
        ## Find feature points to track across frames
        p0 = cv2.goodFeaturesToTrack(prev_frame, mask = None, **feature_params)

        # calculate optical flow if feature points exist
        if p0 is not None:
            p1, st, err = cv2.calcOpticalFlowPyrLK(prev_frame, frame, p0, None, **lk_params)
        else:
            p1, st, err = (None, None, None)

        ## Output dataframe
        flow_df = pd.DataFrame()

        # Check that optical flow was able to track points
        if p0 is not None:
            # Store the result as one point per row
            for pt0_array, pt1_array, st_array, err_array in zip(p0, p1, st, err):
                ## Cleaning up messy nested arrays
                pt0 = pt0_array[0]
                pt1 = pt1_array[0]
                pt_st = st_array[0]       ## per point st
                pt_err = err_array[0]     ## per point err

                frame_series = pd.Series()
                frame_series['flow_pt_pos(t)'] = pt1      ## Current position of feature points
                frame_series['flow_pt_pos(t-1)'] = pt0    ## Previous position of feature points
                frame_series['flow_st'] = pt_st
                frame_series['flow_err'] = pt_err
                flow_df = flow_df.append(frame_series, ignore_index=True)
            # Return default values when optical flow is not successful
            else:
                frame_series = pd.Series()
                frame_series['flow_pt_pos(t)'] = None      ## Current position of feature points
                frame_series['flow_pt_pos(t-1)'] = None    ## Previous position of feature points
                frame_series['flow_st'] = None
                frame_series['flow_err'] = None

        return flow_df


    @staticmethod
    def _get_flow_distances(flow_df):
        """
        Find the distance each optical flow point has moved between frames

        ARGS:
            flow_df - pandas DataFrame
        RETURNS:
            Returns a pandas DataFrame with the distance each optical flow
            point traveled between frames.
        """
        dist_df = pd.DataFrame()
        output = []
        for pts1, pts0, st in zip(flow_df['pt_pos(t)'], flow_df['pt_pos(t-1)'], flow_df['st']):
            dist_list = []
            try:
                for p1, p0, found in zip(pts1, pts0, st):
                    if found == 1:
                        dist = np.sqrt((p1[0][0] - p0[0][0])**2 + (p1[0][1] - p0[0][1])**2)
                        dist_list.append(dist)
                    else:
                        # TODO: Need to handle this better... probably by saving an st array
                        dist = None
                        # dist_list.append(None)
                output.append(dist_list)
            except:
                output.append(None)

        dist_df['dists'] = np.array(output)
        return dist_df

    @staticmethod
    def get_dist_stats(flow_df):
        """
        Calculates per-frame summary stats for optical flow distances

        ARGS:
            flow_df: dataframe of optical flow analysis
        RETURNS:
            Returns dataframe with statistics appended
        """
        out_df = flow_df.copy()
        col = distances_column_name

        out_df['dist_mean'] = flow_df[col].apply(lambda x: np.mean(x) if x is not None else None)
        out_df['dist_median'] = flow_df[col].apply(lambda x: np.median(x) if x is not None and len(x) > 0 else None) #[np.median(d) if len(d) > 0 else 0 for d in distances]
        out_df['dist_dev'] = flow_df[col].apply(lambda x: np.std(x) if x is not None else None) #[np.std(d) if len(d) > 0 else 0 for d in distances]
        out_df['dist_count'] = flow_df[col].apply(lambda x: len(x) if x is not None else None)# [len(d) for d in distances]

        return out_df

    @staticmethod
    def _get_flow_directions(flow_df):
        """
        """
        pass

    @staticmethod
    def _plot_flow(image):
        """
        For visualizing optical flow

        ARGS:
            image: optical with optical flow
        RETURNS:
            None
        """
        plt.figure(figsize=(20,5))
        #plt.plot(np.array(range(0,num_samples))/30., dist_dev, c='k', alpha=0.7)
        plt.xlim(60,90)
        plt.plot(test['time'][:num_samples]/1000., dist_mean, c='k', alpha=0.3)
        plt.plot(test['time'][:num_samples]/1000., dist_median, c='r', alpha=0.3)
        cleaned_means = [d if not math.isnan(d) else 0 for d in dist_mean]
        val = np.percentile(cleaned_means, 99)
        plt.axhline(val, c='k')

    @staticmethod
    def _img_preprocess(frame):
        """
        Standardized cleaning of images. This involves converting to grayscale
        and Gaussian blurring.

        ARGS:
            frame: a single frame of video to be pre-processed
        RETURNS:
            A dataframe of the preprocessed image.
        """
        processed = frame.copy()
        # Convert to grayscale to eliminate auto-adjustment artifacts
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        # Blur to reduce spurious (minor) image artifacts
        processed = cv2.GaussianBlur(processed, (15,15), 0)
        # TODO: Think about resizing image for faster processing
        return processed

if __name__ == "__main__":
    pass
