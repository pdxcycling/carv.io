import math
import numpy as np
import pandas as pd


class FlowPreprocess():
    """
    Collection of (static) utilities for processing optical flow data.
    """

    @staticmethod
    def flow_angles(df):
        """
        Calculate the angle of motion for every tracked point

        Args:
            df: Dataframe containing tracked optical flow points
        Returns:
            list of angles for each tracked point
        """
        angles = []
        for new_pos, old_pos in zip(df['flow_pt_pos(t)'],
                                    df['flow_pt_pos(t-1)']):
            # print new_pos, old_pos
            angles.append(FlowPreprocess._calculate_angle(new_pos, old_pos))
        return angles

    @staticmethod
    def _calculate_angle(new_pos, old_pos):
        """
        Helper for calculating the angles between two points

        Args:
            new_pos: position of point in current frame
            old_pos: position of point in previous frame
        Returns:
            angle of point's motion
        """
        angle = math.atan2((new_pos[1] - old_pos[1]),
                           (new_pos[0] - old_pos[0]))
        return angle

    @staticmethod
    def flow_distances(df):
        """
        Get distance traveled between frames for each tracked point

        Args:
            df: Dataframe containing tracked optical flow points
        Returns:
            list of distance traveled between frames for each tracked point
        """
        distances = []
        for new_pos, old_pos in zip(df['flow_pt_pos(t)'],
                                    df['flow_pt_pos(t-1)']):
            # print new_pos, old_pos
            distances.append(FlowPreprocess._calculate_distance(new_pos,
                                                                old_pos))
        return distances

    @staticmethod
    def _calculate_distance(new_pos, old_pos):
        """
        Euclidean distance calculator
        """
        dist = math.sqrt((new_pos[0] - old_pos[0])**2 +
                         (new_pos[1] - old_pos[1])**2)
        return dist
