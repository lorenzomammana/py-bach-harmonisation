from chorale import Chorale
import sys
import os
from os import listdir
from os.path import isfile, join
from copy import deepcopy

name = sys.argv[1]
prevstage = sys.argv[2]
outputname = sys.argv[3]
prevoutputname = sys.argv[4]

modeldir = ""
dir = modeldir + "model-" + name + "/"
prevstagedir = modeldir + "model-" + prevstage + "/" + prevoutputname + "-results/"

if not os.path.exists(dir + outputname + "-results"):
    os.mkdir(dir + outputname + "-results")

f = open(dir + "SYMBOLS_HIDDEN")

hiddensymbols = f.readlines()

f.close()

files = [f for f in listdir(dir + outputname)
         if isfile(join(dir + outputname, f))]

choraleManager = Chorale()

for file in files:
    [headers, lines] = choraleManager.readchorale(prevstagedir + file, notranspose=True)
    lines.append(choraleManager.AFTER)

    linesC = []

    print("Reading from" + dir + outputname + "/" + file + "\n")

    ofile = open(dir + outputname + "/" + file)

    output = []

    for line in ofile.readlines():
        if line != "\n":
            output.append(line.split(" ")[0])

    ofile.close()

    if (len(output) - 1) != int((len(lines) / 4)):

        print(len(output))
        print(len(lines) / 4)
        if ((len(output) - 1) - int((len(lines) / 4))) < 3:
            print("Ignoring last: " + str(len(output) - (len(lines) / 4)) + " rows")
        else:
            print("Line count doesn't match")
            exit(1)

    lines.pop()

    for i in range(0, len(lines), 4):
        if i + 4 > len(lines):
            linesC.append(['', '2/2', '', '', '', '', '0,0,0,0/0,0,0,0/0,0,0,0'])
            linesC.append([''])
            linesC.append([''])
            linesC.append([''])
            break

        row = deepcopy(lines[i])[0:7]

        row1 = [lines[i + 1][0], lines[i + 1][1], lines[i + 1][2], "", "", ""]
        row2 = [lines[i + 2][0], lines[i + 2][1], lines[i + 2][2], "", "", ""]
        row3 = [lines[i + 3][0], lines[i + 3][1], lines[i + 3][2], "", "", ""]

        row[6] = hiddensymbols[int(output[int(i / 4)])]
        row[6] = row[6].split("\n")[0]

        pitch = [choraleManager.notepitch(row[3]), choraleManager.notepitch(row[4]), choraleManager.notepitch(row[5])]
        motion = row[6].split("/")

        for j in range(0, 3):
            m = motion[j].split(",")[1:]
            m[2] = m[2].split("\n")[0]

            if m[0] != '0':
                row1[j + 3] = choraleManager.notesymbol(pitch[j] + int(m[0]))

            if m[1] != m[0]:
                row2[j + 3] = choraleManager.notesymbol(pitch[j] + int(m[1]))

            if m[2] != m[1]:
                row3[j + 3] = choraleManager.notesymbol(pitch[j] + int(m[2]))

        linesC.append(row)
        linesC.append(row1)
        linesC.append(row2)
        linesC.append(row3)

    linesC = choraleManager.tidychorale(linesC)
    choraleManager.writechorale(dir + outputname + "-results/" + file, headers, linesC)





