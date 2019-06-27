from hmmlearn import hmm
import numpy as np
import sys
from os import listdir
from os.path import isfile, exists, join
from dotmap import DotMap

# TODO viterbi

def readInputs(inputdir, trainset):

    f = open('datasets/' + trainset)
    inputfiles = f.read().splitlines()
    f.close()

    data = {}

    for file in inputfiles:
        file = 'bch' + file.zfill(3) + '.txt'
        rows = open(inputdir + file).readlines()
        data[file] = DotMap()
        data[file].hiddens = []
        data[file].visibles = []
        data[file].size = 0

        for i in range(0, len(rows)):
            hidden_state = int(rows[i].split("\t")[0]) - 1
            visible_state = int(rows[i].split("\t")[1]) - 1

            data[file].hiddens.append(hidden_state)
            data[file].visibles.append(visible_state)

            data[file].size += 1
    
    return data

def createModel(parameters, data):

    K_SMOOTHING = 0.01

    model = hmm.MultinomialHMM(n_components=parameters.hidden_states)

    model.startprob_ = np.zeros(parameters.hidden_states)
    model.transmat_ = np.zeros((parameters.hidden_states, parameters.hidden_states))
    model.emissionprob_ = np.zeros((parameters.hidden_states, parameters.visible_states))

    for _, v in data.items():
        
        model.startprob_[v.hiddens[0]] += 1
        model.emissionprob_[v.hiddens[0], v.visibles[0]] += 1

        for i in range(1, v.size):
            hidden_state_l = v.hiddens[i - 1]
            hidden_state_c = v.hiddens[i]
            visible_state_c = v.visibles[i]

            model.transmat_[hidden_state_l, hidden_state_c] += 1
            model.emissionprob_[hidden_state_c, visible_state_c] += 1

    model.transmat_ += K_SMOOTHING
    model.emissionprob_ += K_SMOOTHING

    model.startprob_ = model.startprob_ / model.startprob_.sum()
    model.transmat_ = (model.transmat_.T / model.transmat_.sum(axis=1)).T
    model.emissionprob_ = (model.emissionprob_.T / model.emissionprob_.sum(axis=1)).T

    # [vis, hid] = model.sample(100)
    # f = open("sample.txt", "w+")

    # for i in range(0, len(vis)):
    #   f.write(str(hid[i]) + " " + str(vis[i][0]) + "\n")

    # f.close()

    return model

def decode(model, data):

    out = {}
    
    chunk = 1 / len(data)
    perc = 0.0

    for k, v in data.items():
        out[k] = DotMap()
        out[k].visibles = v.visibles.copy()

        X = np.atleast_2d(out[k].visibles).T

        logprob, H = model.decode(X)

        out[k].logprob = logprob
        out[k].hiddens = H

        perc += chunk
        print('Processing: ' + "{:.2f}".format(perc * 100) + '%', end='\r')

    return out

def saveResults(out, outputdir):

    for k, v in out.items():

        f = open(outputdir + k, "w+")

        for hidden, visible in zip(v.hiddens, v.visibles):
            f.write(str(hidden + 1) + ' ' + str(visible + 1) + '\n')
        
        f.close()

if __name__ == '__main__':

    assert not len(sys.argv) < 2, 'model name required'
    name = sys.argv[1]
    train = sys.argv[2]
    test = sys.argv[3]

    modeldir = "model-" + name + "/"
    inputdir = modeldir + "input/"
    outputdir = modeldir + "viterbi/"

    # assert exists(modeldir) and not isfile(modeldir), 'model ' + name + ' not found'
    # assert exists(inputdir) and not isfile(inputdir), 'input for model ' + name + ' not found'
    # assert exists(outputdir) and not isfile(outputdir), 'output dir for model ' + name + ' not found'
    # assert exists(modeldir + "PARAMETERS") and isfile(modeldir + "PARAMETERS"), 'input PARAMETERS for model ' + name + ' not found'

    rawParameters = open(modeldir + "PARAMETERS").readlines()

    parameters = DotMap()
    parameters.hidden_states = int(rawParameters[4].split(":")[1].strip()) - 1
    parameters.visible_states = int(rawParameters[5].split(":")[1].strip()) - 1

    # read (hidden, visible) pairs from input/ folder 
    traindata = readInputs(inputdir, train)

    # create HMM model
    model = createModel(parameters, traindata)

    # predict hidden states using model

    testdata = readInputs(inputdir, test)

    out = decode(model, testdata)

    # save results
    saveResults(out, outputdir)
