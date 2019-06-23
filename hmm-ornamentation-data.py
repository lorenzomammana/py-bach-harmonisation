from chorale import Chorale
import sys
import os
from copy import deepcopy


def readentries(filename):
    entries = []

    f = open(filename, "r")

    for chor in f:
        entries.append("bch" + ('%03d' % int(chor.split("\n")[0])) + ".txt")

    f.close()

    return entries


harmonydir = ""
modeldir = ""

datasetdir = harmonydir + "datasets/"
# name = sys.argv[1]
# prevstage = sys.argv[2]
# prevoutputname = sys.argv[3]
# train = sys.argv[4]
# test = sys.argv[5]

name = "ornamentation-dur"
prevstage = "chords-dur"
prevoutputname = "viterbi"
train = "train_dur"
test = "test_dur"

modeldir += "model-" + name + "/"
prevstagedir = "model-" + prevstage + "/" + prevoutputname + "-results/"

if not os.path.exists(modeldir):
    os.mkdir(modeldir)
    os.mkdir(modeldir + "input")
    os.mkdir(modeldir + "input-test")
    os.mkdir(modeldir + "viterbi")
    os.mkdir(modeldir + "sampled")

#  perl -I chorale-perl chorale-perl/hmm-data.pl chords-dur chordtransposed/HARMONIK SOPRAN train_dur test_dur

hiddensymbols = []
hiddensymbolseen = {}
visiblesymbols = []
visiblesymbolseen = {}

# carica due array con i nomi dei file
trainfiles = readentries(datasetdir + train)
testfiles = readentries(datasetdir + test)

files = []

if __name__ == '__main__':
    for file in trainfiles:
        files.append("music/" + file)

    for file in testfiles:
        files.append("music/" + file)

    for file in testfiles:
        files.append(prevstagedir + file)

    choraleManager = Chorale()

    for file in files:
        [header, lines] = choraleManager.readchorale(file, False)

        lines.append(choraleManager.AFTER)
        lines.append(choraleManager.AFTER)
        lines.append(choraleManager.AFTER)
        lines.append(choraleManager.AFTER)

        if prevstagedir in file:
            filename = modeldir + "input-test/" + file.split("/").pop()
            print("writing on " + filename)
            outputfile = open(filename, "w+")
        else:
            filename = modeldir + "input/" + file.split("/").pop()
            print("writing on " + filename)
            outputfile = open(filename, "w+")

        for i in range(0, len(lines), 4):
            h = []
            v = ["0"]

            if i + 4 < len(lines):
                c = lines[i]
                c1 = lines[i + 1]
                c2 = lines[i + 2]
                c3 = lines[i + 3]

                if c3[2] != "END":
                    c4 = lines[i + 4]
                else:
                    c4 = deepcopy(c)

                for j in range(3, 6):
                    h.append("0," + str(choraleManager.notepitch(c1[j]) - choraleManager.notepitch(c[j])) + ","
                             + str(choraleManager.notepitch(c2[j]) - choraleManager.notepitch(c[j])) + ","
                             + str(choraleManager.notepitch(c3[j]) - choraleManager.notepitch(c[j])))

                    v.append(str(choraleManager.notepitch(c4[j]) - choraleManager.notepitch(c[j])))

                hiddensymbol = "/".join(h)
                visiblesymbol = "/".join(v)
            else:
                hiddensymbol = "0,0,0,0/0,0,0,0/0,0,0,0"
                for j in range(3, 6):
                    v.append(str(choraleManager.notepitch(c3[j]) - choraleManager.notepitch(c[j])))
                visiblesymbol = "/".join(v)

            try:
                hiddensymbols.index(hiddensymbol)
            except ValueError:
                hiddensymbols.append(hiddensymbol)

            try:
                visiblesymbols.index(visiblesymbol)
            except ValueError:
                visiblesymbols.append(visiblesymbol)

            outputfile.write(str(hiddensymbols.index(hiddensymbol)) + "\t" +
                             str(visiblesymbols.index(visiblesymbol)) + "\n")
        outputfile.close()

    f = open(modeldir + "SYMBOLS_HIDDEN", "w+")
    f.write("\n".join(hiddensymbols))
    f.close()

    f = open(modeldir + "SYMBOLS_VISIBLE", "w+")
    f.write("\n".join(visiblesymbols))
    f.close()

    f = open(modeldir + "PARAMETERS", "w+")
    f.write("Name: " + name + "\n")
    f.write("Hidden: Ornamented notes\n")
    f.write("Visible: Part interval\n\n")
    f.write("Hidden states: " + str(len(hiddensymbols)) + "\n")
    f.write("Visible states: " + str(len(visiblesymbols)) + "\n")
    f.write("Training data: " + train + "\n")
    f.write("Test data: " + test + "\n")
    f.close()
