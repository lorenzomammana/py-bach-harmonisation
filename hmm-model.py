from hmmlearn import hmm
import numpy as np
import sys
from os import listdir
from os.path import isfile, exists, join
from dotmap import DotMap

# TODO viterbi

def readInputs(inputdir):

    inputfiles = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]

    data = {}

    for file in inputfiles:
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

    model = hmm.MultinomialHMM(n_components=parameters.hidden_states)

    model.transmat_ = np.zeros((parameters.hidden_states, parameters.hidden_states))
    model.emissionprob_ = np.zeros((parameters.hidden_states, parameters.visible_states))

    for _, v in data.items():
        
        model.emissionprob_[v.hiddens[0], v.visibles[0]] += 1

        for i in range(1, v.size):
            hidden_state_l = v.hiddens[i - 1]
            hidden_state_c = v.hiddens[i]
            visible_state_c = v.visibles[i]

            model.transmat_[hidden_state_l, hidden_state_c] += 1
            model.emissionprob_[hidden_state_c, visible_state_c] += 1

    for idx in np.where(~model.transmat_.any(axis=1)):
        model.transmat_[idx, :] = 1 / parameters.hidden_states

    for idx in np.where(~model.emissionprob_.any(axis=1)):
        model.emissionprob_[idx, :] = 1 / parameters.visible_states

    model.startprob_ = np.full(parameters.hidden_states, (1 / parameters.hidden_states))
    model.transmat_ = (model.transmat_.T / model.transmat_.sum(axis=1)).T
    model.emissionprob_ = (model.emissionprob_.T / model.emissionprob_.sum(axis=1)).T

    # [vis, hid] = model.sample(100)
    # f = open("sample.txt", "w+")

    # for i in range(0, len(vis)):
    #   f.write(str(hid[i]) + " " + str(vis[i][0]) + "\n")

    # f.close()

    return model

if __name__ == '__main__':

    assert not len(sys.argv) < 2, 'model name required'
    name = sys.argv[1]

    modeldir = "model-" + name + "/"
    inputdir = modeldir + "input/"

    assert exists(modeldir) and not isfile(modeldir), 'model ' + name + ' not found' 
    assert exists(inputdir) and not isfile(inputdir), 'input for model ' + name + ' not found'
    assert exists(modeldir + "PARAMETERS") and isfile(modeldir + "PARAMETERS"), 'input PARAMETERS for model ' + name + ' not found'

    rawParameters = open(modeldir + "PARAMETERS").readlines()

    parameters = DotMap()
    parameters.hidden_states = int(rawParameters[4].split(":")[1].strip()) - 1
    parameters.visible_states = int(rawParameters[5].split(":")[1].strip()) - 1

    data = readInputs(inputdir)
    model = createModel(parameters, data)


