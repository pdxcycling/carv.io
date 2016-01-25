import pandas as pd
import numpy as np
import cv2


class FrameAnalysis(object):
    """
    This encapsulate all methods to process a single image in a video
    """

    # Blur Detection
    # Based on
    # http://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
    @staticmethod
    def get_blur(image):
        """
        Uses the Laplancian to find a single number metric of blur.
        The lower the number, the more blurry the image.
        A reasonable threshold is ~< 100 is blurry, > 100 is sharp.

        Args:
            image: a single video frame
        Returns:
            single number metric for blur/sharpess
        """
        # TODO: Machine learning to determine the proper threshold
        #       of Blur vs. non-Blur
        out = pd.DataFrame([cv2.Laplacian(image, cv2.CV_64F).var()],
                           columns=['blur'])
        return out

    @staticmethod
    def get_hsv_hists(image, bw_mask=True):
        """
        Calculates a Hue, Saturation, Value, White Pixels, Black Pixels

        INPUT
            image: RGB image
            bw_mask: Whether to separate black and white pixels
        OUTPUT
            Dataframe containing histograms of Hue, Saturation, Value
            Also contains black pixel count and white pixel count if
            bw_mask is true.
        """

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Mask off black and white values
        # Black/white values may affect color hist
        # NOTE: # saturation and value do not need to be masked
        bw_count_df = pd.DataFrame()  # !
        if bw_mask:
            mask, bw_count_df = SceneAnalysis._get_filter_bw(hsv)
            hue_df = hsv[:, :, 0] * mask
        else:
            hue_df = hsv[:, :, 0]

        # Create binned value counts per HSV channel
        hue_hist_df = SceneAnalysis._get_hist(hue_df.ravel(),
                                              num_bins=72,
                                              max_val=180,
                                              prefix="hue_bin_")
        sat_hist_df = SceneAnalysis._get_hist(hsv[:, :, 1].ravel(),
                                              num_bins=25,
                                              max_val=255,
                                              prefix="sat_bin_")
        val_hist_df = SceneAnalysis._get_hist(hsv[:, :, 2].ravel(),
                                              num_bins=25,
                                              max_val=255,
                                              prefix="val_bin_")
        out = pd.concat([hue_hist_df, sat_hist_df, val_hist_df, bw_count_df],
                        axis=1)
        return out

    @staticmethod
    def _get_filter_bw(hsv_image):
        """
        Filter out black and white pixels. These are identified by the value
        and saturation pixel components (HSV format)

        ARGS:
            hsv_image: input image in HSV format
        RETURNS:
            mask: image mask to exclude black and white pixels
            bw_df: dataframe containing black and white pixel counts
        """
        # Create dataframe for black and white pixels
        bw_df = pd.DataFrame(index=[0])

        # Pixels with 'value' component less than 10 (out of 255)
        # are marked as black
        v_mask = (hsv_image[:, :, 2] > 10)
        bw_df['num_black_pixels'] = np.sum(v_mask == 0)

        # Pixels with 'saturation' component less than 10 (out of 255)
        # are marked as white
        s_mask = (hsv_image[:, :, 1] > 10)
        bw_df['num_white_pixels'] = np.sum(s_mask + (v_mask == 0) == 0)

        # Create a mask of 1's (non-black/white pixel)
        # and 0's (black/white pixel)
        mask = s_mask * v_mask
        vec_function = np.vectorize(lambda x: 1 if x > 0 else -1)
        mask = vec_function(mask)
        return mask, bw_df

    @staticmethod
    def _get_hist(hsv_image, num_bins, max_val, prefix):
        '''
        Returns a histogram for the given image parameter (H,S,V)

        ARGS:
            hsv_image:  self explanatory
            num_bins:   number of bins in histogram
            max_val:    maximum possible value that image parameter can take
            prefix:     prefix of image parameter
        RETURNS:
            DataFrame of histogram
        '''
        hist, bins = np.histogram(hsv_image.ravel(), num_bins, [0, max_val])
        out = pd.DataFrame(index=[0])
        out = pd.DataFrame(np.array([hist.ravel()]))
        out.columns = [prefix + str(v) for v in bins[:-1]]
        return out

    @staticmethod
    def find_faces(images):
        """
        Facial detection (unimplemented, potential coming attraction)
        """
        pass
