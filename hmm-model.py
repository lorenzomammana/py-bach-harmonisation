from hmmlearn import hmm
import numpy as np
import sys
from os import listdir
from os.path import isfile, join

# name = sys.argv[1]
name = "chords-dur"

modeldir = "model-" + name + "/"
inputdir = modeldir + "input/"

parameters = open(modeldir + "PARAMETERS").readlines()

hidden_states = int(parameters[4].split(":")[1].strip()) - 1
visible_states = int(parameters[5].split(":")[1].strip()) - 1

model = hmm.MultinomialHMM(n_components=hidden_states)

model.transmat_ = np.zeros([hidden_states, hidden_states])
model.emissionprob_ = np.zeros([hidden_states, visible_states])

inputfiles = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]

for file in inputfiles:
    rows = open(inputdir + file).readlines()

    for i in range(1, len(rows)):
        hidden_state_l = int(rows[i - 1].split("\t")[0]) - 1
        hidden_state_c = int(rows[i].split("\t")[0]) - 1
        visible_state = int(rows[i].split("\t")[1]) - 1

        model.transmat_[hidden_state_l, hidden_state_c] += 1
        model.emissionprob_[hidden_state_c, visible_state] += 1

for idx in np.where(~model.transmat_.any(axis=1)):
    model.transmat_[idx, :] = 1 / hidden_states

for idx in np.where(~model.emissionprob_.any(axis=1)):
    model.emissionprob_[idx, :] = 1 / visible_states

model.transmat_ = (model.transmat_.T/model.transmat_.sum(axis=1)).T
model.emissionprob_ = (model.emissionprob_.T/model.emissionprob_.sum(axis=1)).T

model.startprob_ = np.zeros([hidden_states, 1])
model.startprob_[:] = 1 / hidden_states

[vis, hid] = model.sample(100)
f = open("sample.txt", "w+")

for i in range(0, len(vis)):
    f.write(str(hid[i]) + " " + str(vis[i][0]) + "\n")

f.close()
