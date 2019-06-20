import sys
import os
from os import listdir
from os.path import isfile, join
from chorale import Chorale
choraledir = ""

name = sys.argv[1]
outputname = sys.argv[2]

modeldir = "model-" + name
prevstagedir = choraledir + "music/"
outputdir = modeldir + "/" + outputname
resultdir = outputdir + "-results"

if not os.path.exists(resultdir):
    os.mkdir(resultdir)

hiddensymbols = open(modeldir + "/" + "SYMBOLS_HIDDEN").readlines()
inputfiles = [f for f in listdir(outputdir)
              if isfile(join(outputdir, f))]

choraleManager = Chorale()

for file in inputfiles:
    [headers, lines] = choraleManager.readchorale(prevstagedir + file)
    lines.append(Chorale.AFTER)

    linesC = []

    print("Reading from " + outputdir + "/" + file)

    ofile = open(outputdir + "/" + file)

    output = []

    for line in ofile.readlines():
        if line != "\n":
            output.append(line.split(" ")[0])

    ofile.close()

    if (len(output) - 1) != int((len(lines) / 4)):
        if (len(output) - 1) - int((len(lines) / 4)):
            print("Ignoring last: " + str(int(len(output) - (len(lines) / 4))) + " rows")
        else:
            print("Line count doesn't match")
            exit(1)

    lines.pop()

    for i in range(0, len(lines), 4):
        row = [lines[i][0], lines[i][1], lines[i][2]]
        row1 = [lines[i + 1][0], lines[i + 1][1], lines[i + 1][2]]
        row2 = [lines[i + 2][0], lines[i + 2][1], lines[i + 2][2]]
        row3 = [lines[i + 3][0], lines[i + 3][1], lines[i + 3][2]]

        row.append('')
        row.append('')
        row.append('')
        row.append(hiddensymbols[int(output[int(i / 4)])])

        if ":" in row[6]:
            if "/" in row[6]:
                row[6] = row[6].split("/")[0]

        linesC.append(row)
        linesC.append(row1)
        linesC.append(row2)
        linesC.append(row3)

    linesC = choraleManager.unpackchordsymbols(linesC)
    linesC = choraleManager.tidychorale(linesC)

    choraleManager.writechorale(resultdir + "/" + file, headers, linesC)





