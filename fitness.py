import sys
from os import listdir
from os.path import isfile, exists, join
from dotmap import DotMap

def readInputs(filedir):

    inputfiles = [f for f in listdir(filedir) if isfile(join(filedir, f))]

    data = {}

    for file in inputfiles:
        rows = open(filedir + file).readlines()
        data[file] = DotMap()
        data[file].hiddens = []
        data[file].size = 0

        for i in range(0, len(rows)):
            hidden_state = int(rows[i].replace('\t', ' ').split()[0]) - 1

            data[file].hiddens.append(hidden_state)
            data[file].size += 1
    
    return data

if __name__ == '__main__':
    
    assert not len(sys.argv) < 3, '<input files dir> <viterbi files output dir> required'

    inputDir = sys.argv[1]
    outputDir = sys.argv[2]

    original = readInputs(inputDir)
    viterbi = readInputs(outputDir)

    common = [f for f in original.keys() if f in viterbi.keys()]

    same = 0.0
    total = 0.0
    for f in common:
        for o, v in zip(original[f].hiddens, viterbi[f].hiddens):
            total += 1.0
            if o == v:
                same += 1.0

    print(same / total)



