import scipy.io.wavfile
import subprocess
import matplotlib.pyplot

class Preprocess(object):
    '''
    TODO: Instantiate object or just treat these as static methods???
    TODO: Should both audio AND video have beat and frequency analysis???
    '''
    # Location where audio files will be stored

    @staticmethod
    def separate_audio(video_id, video_file_name):
        """
        Strip the audio from a video file

        ARGS:
            video_id: unique global video identifier
            video_file_name: path to video file
        RETURNS:
            String to audio file location
        """
        ## From http://stackoverflow.com/questions/26741116/python-extract-wav-from-video-file
        #_id = video_file_name.split("\.mp4")[0]
        _id = video_id
        audio_folder = "../media/"
        wav_file_name = audio_folder + _id + ".wav"
        command = "ffmpeg -i " + video_file_name + \
                  " -ab 160k -ac 2 -ar 44100 -vn " + wav_file_name
        subprocess.call(command, shell=True)
        return wav_file_name
