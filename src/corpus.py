"""Module with code to handle the base. Extract data, rewrite and etc.
"""


import os, os.path
import shutil
import scipy.io.wavfile as wavf
import numpy as np
from useful import CORPORA_DIR, FEATURES_DIR
import features


def mit_features(winlen=0.02, winstep=0.01, numcep=13, numdeltas=2):
    """Extracts features from base MIT. The features are saved in a directory with
    name given by '../bases/features/mit_<numcep>_<numdeltas>'

    @param winlen: the length of the analysis window in seconds. Default is
    0.02s (20 milliseconds).
    @param winstep: the step between successive windows in seconds. Default is
    0.01s (10 milliseconds).
    @param numcep: the number of cepstrum to return, default 13.
    @param numdeltas: number of delta calculations.
    """
    if not os.path.exists(FEATURES_DIR):
        os.mkdir(FEATURES_DIR)

    #Feature base: mit_<numcep>_<numdeltas>
    pathfeat = '%smit_%d_%d/' % (FEATURES_DIR, numcep, numdeltas)
    print('CREATING %s' % pathfeat)
    if os.path.exists(pathfeat):
        shutil.rmtree(pathfeat)
    os.mkdir(pathfeat)

    pathdatasets = '%smit/' % CORPORA_DIR
    datasets = os.listdir(pathdatasets)
    datasets.sort()

    for dataset in datasets:
        print(dataset)
        os.mkdir('%s%s' % (pathfeat, dataset))
        speakers = os.listdir('%s%s' % (pathdatasets, dataset))
        speakers.sort()

        for speaker in speakers:
            print(speaker)
            #reading list of utterances from each speaker
            pathspeaker = '%s%s/%s' % (pathdatasets, dataset, speaker)
            utterances = os.listdir(pathspeaker)
            utterances.sort()
            utterances = [utt for utt in utterances if utt.endswith('.wav')]

            #path to write in features
            pathspeaker_feat = '%s%s/%s' % (pathfeat, dataset, speaker)
            os.mkdir('%s' % pathspeaker_feat)

            for utt in utterances:
                path_utt = '%s/%s' % (pathspeaker, utt)
                (samplerate, signal) = wavf.read(path_utt)
                mfccs_deltas = features.mfcc_delta(signal, winlen, winstep, samplerate,
                                                   numcep, numdeltas=numdeltas)
                mfccs_deltas = mfccs_deltas.transpose()
                np.save('%s/%s' % (pathspeaker_feat, utt), mfccs_deltas)

def read_features(numcep, numdeltas, dataset, speaker, uttnum, transpose=True):
    """Reads a feature from a speaker.

    @returns: The features from the utterance given by (dataset, speaker, uttnum).
    """
    mfccs = np.load('%smit_%d_%d/%s/%s/phrase%02d_16k.wav.npy' % (FEATURES_DIR,
                    numcep, numdeltas, dataset, speaker, uttnum))

    if transpose:
        return mfccs.transpose()
    else:
        return mfccs


#TESTS
if __name__ == '__main__':
    import scipy.io.wavfile as wavf
    import os, os.path, shutil
    from useful import CORPORA_DIR, IMAGES_DIR, plotfile


    IMAGES_CORPUS_DIR = '%scorpus/' % IMAGES_DIR

    if os.path.exists(IMAGES_CORPUS_DIR):
            shutil.rmtree(IMAGES_CORPUS_DIR)
    os.mkdir(IMAGES_CORPUS_DIR)

    filecounter = 0
    filename = '%sfigure' % IMAGES_CORPUS_DIR

    numcep = 13
    numdeltas = 0
    voice = ('enroll_2', 'f08', 54)
    (enroll, speaker, speech) = voice

    #Reading MFCCs from features base
    mfccs = read_features(numcep, numdeltas, enroll, speaker, speech)
    numframes = len(mfccs[0])
    frameindices = np.linspace(0, numframes, numframes, False)
    numcoeffs = numcep*(numdeltas + 1)
    print(mfccs.shape)
    for (feat, n) in zip(mfccs, range(numcoeffs)):
        filecounter = plotfile(frameindices, feat, 'MFCC[%d]\n%s' % (n, voice),
                               'frame', 'mfcc[%d][frame]' % n, filename, filecounter,
                               'black')