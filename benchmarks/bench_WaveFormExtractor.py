import h5py
import numpy as np
import time
import os
import psutil, shutil
import gc
import atexit
from tables import *

##### PARAMETERS
# folder containing the file
directory = "."
# bxr file to be loaded
fileName = os.path.join(
    os.path.dirname(__file__), "../tests/test_samples/full_sample.bxr"
)
# [300, 340] # set interval of unit to be considered for the analysis in the clusterName (if [] will take all)
intervalOfUnitsToWorkWith = []
# name of the cluster to work with
clusterName = "Group 1"
binSizeAFR = 0.25
# bin size dimension [s] to calculate AFR on all units

##### FUNCTIONS:

##### ANALISYS ROUTINE
# loading .bxr file
temp = h5py.File(fileName, "r")
resultDirectory = os.path.join(os.path.dirname(__file__), "out_wfe")
atexit.register(shutil.rmtree, resultDirectory)
if not os.path.exists(resultDirectory):
    os.makedirs(resultDirectory)

import os, psutil

_process = psutil.Process(os.getpid())

for chunks in np.logspace(1, 4, 100):
    gc.collect()
    chunks = int(chunks)
    _start_time = time.time()
    ### Loading cluster
    # select only the channels belonging to the cluster specified in clusterName
    clusters = temp["3BUserInfo/ChsGroups"]
    cluster = []
    for idx in range(clusters.shape[0]):
        if str(clusters[idx]["Name"]) == clusterName:
            clusterUnits = clusters[idx]["Units"]
            clusterChs = clusters[idx]["Chs"]
    numUnit = len(clusterUnits)

    ### load recording parameters
    # num of recorded frames for a ch
    NRecFrames = temp["3BRecInfo/3BRecVars/NRecFrames"][0]
    # sampling frequenk reference.
    samplingRate = temp["3BRecInfo/3BRecVars/SamplingRate"][0]
    # recording duraton in [s]
    recordingLength = NRecFrames / samplingRate

    ### extract and demux time stamp for each single unit
    start = time.time()
    unitTimeStamp = []
    unitNumSpikes = np.array(np.zeros(numUnit))
    start = time.time()
    spikeUnits = np.array(temp["3BResults/3BChEvents/SpikeUnits"][: 1024 * chunks])
    partial_len = len(temp["3BResults/3BChEvents/SpikeUnits"]) / 1024 * chunks
    spikeChIDs = np.array(temp["3BResults/3BChEvents/SpikeChIDs"][: 1024 * chunks])
    spikeTimes = np.array(temp["3BResults/3BChEvents/SpikeTimes"][: 1024 * chunks])

    startExtraction = time.time()
    # depending on the acq version it can be 1 or -1
    signalInversion = temp["/3BRecInfo/3BRecVars/SignalInversion"][0]
    # in uVolt
    maxVolt = temp["/3BRecInfo/3BRecVars/MaxVolt"][0]
    # in uVolt
    minVolt = temp["/3BRecInfo/3BRecVars/MinVolt"][0]
    tQLevel = temp["/3BRecInfo/3BRecVars/BitDepth"][0]
    # quantized levels corresponds to 2^num of bit to encode the signal
    QLevel = np.power(2, tQLevel)
    fromQLevelToUVolt = (maxVolt - minVolt) / QLevel
    # check the version as waveform can be store in a matrix (version < 103) or in an array (version > 103)
    vaweFormVersion = temp["3BResults/3BChEvents"].attrs["Version"]
    if vaweFormVersion > 102:
        # if version > 102 the spike waves are not in a bidimensional matrix but in a monodimensional matrix
        # extract the total number of detected waveforms
        numWaveForms = temp["3BResults/3BChEvents/SpikeUnits"].size
        # extract the spike length
        waveLength = int(temp["3BResults/3BChEvents/SpikeForms"].size / numWaveForms)
        # reshape the WaveForms array into a bidimensional matrix
        spikeWaves = temp["/3BResults/3BChEvents/SpikeForms"][
            : (1024 * chunks * waveLength)
        ]
        spikeWaves = spikeWaves.reshape(1024 * chunks, waveLength)
    else:
        spikeWaves = temp["/3BResults/3BChEvents/SpikeForms"][: 1024 * chunks][:]
    endExtraction = time.time()

    title = "test"
    for idxUnit, idx in zip(clusterUnits, range(len(clusterUnits))):
        tempSpike = np.where(spikeUnits == idxUnit)[0]
        if len(tempSpike) == 0:
            continue
        chLabelIndex = [spikeChIDs[tempSpike[0]]]
        chLabel = temp["3BResults/3BInfo/ChIDs2Labels"][chLabelIndex][0].decode()
        spikeTimesSec = spikeTimes[tempSpike] / samplingRate
        tempWaves = spikeWaves[tempSpike]
        spikeWavesUVolt = (
            (tempWaves * signalInversion) - (QLevel / 2)
        ) * fromQLevelToUVolt
        testWave = spikeWaves[0]
        unitTimeStamp.append(spikeTimesSec.tolist())
        unitNumSpikes[idx] = len(tempSpike)
        # store time stamp
        startStoring = time.time()
        np.savetxt(
            resultDirectory + "/" + chLabel + "_unit_" + str(idxUnit) + ".txt",
            spikeTimesSec,
        )
        np.savetxt(
            resultDirectory + "/" + chLabel + "_unit_" + str(idxUnit) + "_waves.txt",
            spikeWavesUVolt,
        )
        endStoring = time.time()
        # file = open(resultDirectory + '\\' + chLabel + '_unit_' + str(idxUnit) + '.dat', "wb")
        # file.write(tempSpike)
        # file.close()

    print(chunks, time.time() - _start_time, _process.memory_info().rss)

end = time.time()
temp.close()

### calculate average firing rate on all the units
start = time.time()
# fixed bin size
binsAFR = np.arange(0, recordingLength, binSizeAFR)
hist, binsEdge = np.histogram(
    sum(unitTimeStamp, []), bins=binsAFR, normed=False, weights=None, density=None
)
# convert to firing rate averaged on all units
histFiringRate = hist / (binSizeAFR * numUnit)
xScale = (binsEdge[1:] - binsEdge[0:-1]) / 2.0 + binsEdge[0:-1]
title = "AFR"
temp.close()
end = time.time()
