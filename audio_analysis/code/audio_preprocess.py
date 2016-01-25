import sys
from aubio import fvec, source, pvoc, filterbank, tempo
from numpy import vstack, zeros

class Audio(object):
    '''
    Process the audio into forms useful for feature extraction
    TODO: Is this actually a RawAudioObject?
    '''
    ## class variables
    win_s = 512                 # fft size
    hop_s = win_s / 2           # hop size

    def __init__(self, filename):
        '''
        Default constructor
        '''
        self.filename = filename    # Name of file... this may not need to be stored
        self.samplerate = None  #
        self.data = None        # Numpy array of audio data
        self.time_range = None  # Numpy array of floats

    def _preprocess(self):
        '''
        Preprocessing pipeline
        '''
        # Read file
        # Extract frequency bands
        # Extract beats
        pass

    def _read_file(self, filename):
        '''
        Takes a filename
        Returns an numpy array of
        '''
        pass

    def _extract_frequency_bands(self):
        '''

        '''
        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        pass

    def _extract_energies(self):


win_s = 512                 # fft size
hop_s = win_s / 2           # hop size

filename = sys.argv[1]

samplerate = 44100

filename = "media/archive/audio.wav"


s = source(filename, samplerate, hop_s)

pv = pvoc(win_s, hop_s)

f = filterbank(40, win_s)
f.set_mel_coeffs_slaney(samplerate)

energies = zeros((40,))
o = {}

total_frames = 0
downsample = 2
x_time = []

while True:
    samples, read = s()
    fftgrain = pv(samples)
    new_energies = f(fftgrain)
    x_time.append(total_frames / float(samplerate))
    print 'Time: %f' % (total_frames / float(samplerate) ),
    print ' '.join(['%f' % b for b in new_energies])
    energies = vstack( [energies, new_energies] )
    total_frames += read
    if read < hop_s: break


if 0:
    print "done computing, now plotting"
    import matplotlib.pyplot as plt
    from demo_waveform_plot import get_waveform_plot
    from demo_waveform_plot import set_xlabels_sample2time
    fig = plt.figure()
    plt.rc('lines',linewidth='.8')
    wave = plt.axes([0.1, 0.75, 0.8, 0.19])
    get_waveform_plot(filename, samplerate, block_size = hop_s, ax = wave )
    wave.yaxis.set_visible(False)
    wave.xaxis.set_visible(False)

    n_plots = len(energies.T)
    all_desc_times = [ x * hop_s  for x in range(len(energies)) ]
    for i, band in enumerate(energies.T):
        ax = plt.axes ( [0.1, 0.75 - ((i+1) * 0.65 / n_plots),  0.8, 0.65 / n_plots], sharex = wave )
        ax.plot(all_desc_times, band, '-', label = 'band %d' % i)
        #ax.set_ylabel(method, rotation = 0)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.axis(xmax = all_desc_times[-1], xmin = all_desc_times[0])
        ax.annotate('band %d' % i, xy=(-10, 0),  xycoords='axes points',
                horizontalalignment='right', verticalalignment='bottom',
                size = 'xx-small',
                )
    set_xlabels_sample2time( ax, all_desc_times[-1], samplerate)
    #plt.ylabel('spectral descriptor value')
    ax.xaxis.set_visible(True)
    plt.show()

    def _get_tempo(self):

        o = tempo("default", win_s, hop_s, samplerate)

    def plot():
        '''
        '''
        plt.figure(figsize=(20,12))
        #plt.pcolor(energies.T,cmap=plt.cm.Reds)
        plt.pcolormesh(np.array(x_time), np.array([range(40)]).T * 2000 - 40000, energies[:-1].T, alpha=0.3)
