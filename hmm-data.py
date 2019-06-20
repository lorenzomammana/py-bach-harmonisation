import sys
from chorale import Chorale
import os


def internal(arg):
    return {
        'PHRASE': 'column[0]',
        'TAKT': 'column[1]',
        'SOPRAN': 'column[2]',
        'ALT': 'column[3]',
        'TENOR': 'column[4]',
        'BASS': 'column[5]',
        'HARMONIK': 'column[6]',
        'chordtransposed': 'column[9]'
    }[arg]


def readentries(filename):
    entries = []

    f = open(filename, "r")

    for chor in f:
        entries.append("bch" + ('%03d' % int(chor.split("\n")[0])) + ".txt")

    f.close()

    return entries


choraledir = ""
modeldir = ""

inputdir = choraledir + "music/"
datasetdir = choraledir + "datasets/"
name = sys.argv[1]

if "/" in sys.argv[2]:
    splits = sys.argv[2].split('/')
    hidden = internal(splits[0]) + '/' + internal(splits[1])
else:
    hidden = internal(sys.argv[1])

visible = internal(sys.argv[3])
train = sys.argv[4]
test = sys.argv[5]

unseenmarker = "(unknown)"
hiddensymbols = [unseenmarker]
hiddensymbolseen = {unseenmarker: 0}
visiblesymbols = [unseenmarker]
visiblesymbolseen = {unseenmarker: 0}

modeldir += "model-" + name + "/"

if not os.path.exists(modeldir):
    os.mkdir(modeldir)
    os.mkdir(modeldir + "input")
    os.mkdir(modeldir + "viterbi")
    os.mkdir(modeldir + "sampled")

#  perl -I chorale-perl chorale-perl/hmm-data.pl chords-dur chordtransposed/HARMONIK SOPRAN train_dur test_dur

# carica due array con i nomi dei file
trainfiles = readentries(datasetdir + train)
testfiles = readentries(datasetdir + test)


def processfile(file):

    print("Processing " + file)
    [headers, lines] = choraleManager.readchorale("music/" + file)

    linesB = choraleManager.beatrows(lines)

    linesB.append(choraleManager.AFTER)

    outputfile = open(modeldir + "input/" + file, "w+")

    for line in linesB:

        column = line
        if "/" in hidden:
            hiddensymbol = eval(hidden.split("/")[0]) + "/" + eval(hidden.split("/")[1])
        else:
            hiddensymbol = eval(hidden)

        visiblesymbol = eval(visible)

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


if __name__ == '__main__':
    choraleManager = Chorale()

    for file in trainfiles:
        processfile(file)

    for file in testfiles:
        processfile(file)

    f = open(modeldir + "SYMBOLS_HIDDEN", "w+")
    f.write("\n".join(hiddensymbols))
    f.close()

    f = open(modeldir + "SYMBOLS_VISIBLE", "w+")
    f.write("\n".join(visiblesymbols))
    f.close()

    f = open(modeldir + "PARAMETERS", "w+")
    f.write("Name: " + name + "\n")
    f.write("Hidden: " + sys.argv[2] + "\n")
    f.write("Visible: " + sys.argv[3] + "\n\n")
    f.write("Hidden states: " + str(len(hiddensymbols)) + "\n")
    f.write("Visible states: " + str(len(visiblesymbols)) + "\n")
    f.write("Training data: " + train + "\n")
    f.write("Test data: " + test + "\n")
    f.close()
