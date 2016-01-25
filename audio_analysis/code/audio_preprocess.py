import sys
from aubio import fvec, source, pvoc, filterbank, tempo
from numpy import vstack, zeros


class Audio(object):
    """
    Process the audio into forms useful for feature extraction
    """
    # Class variables
    win_s = 512                 # fft size
    hop_s = win_s / 2           # hop size

    def __init__(self, filename):
        """
        Default constructor

        ARGS:
            filename: filepath to audi
        RETURNS:
            None
        """
        self.filename = filename    # Name of file... this may not need to be stored
        self.samplerate = None  #
        self.data = None        # Numpy array of audio data
        self.time_range = None  # Numpy array of floats

    def _preprocess(self):
        """
        Preprocessing pipeline

        ARGS:
            None
        RETURNS:
            None
        """
        # Read file
        # Extract frequency bands
        # Extract beats
        pass

    def _read_file(self, filename):
        """
        Takes a filename
        Returns an numpy array of

        ARGS:
            filename: path to audio file
        RETURNS:
            None
        """
        pass

    def _extract_frequency_bands(self):
        """
        Helper function to extract frequency bands from audio

        ARGS:
            None
        RETURNS:
            None
        """
        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        pass

    def _extract_energies(self):

if __name__ == "__main__":
    pass
