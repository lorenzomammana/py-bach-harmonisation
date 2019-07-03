from chorale import Chorale
from copy import deepcopy
import sys

choraleManager = Chorale()

file = sys.argv[1]

[headers, lines] = choraleManager.readchorale('custom/music/' + file)
lines.append(Chorale.AFTER)

if 'dur' in headers[2]:
    hiddensymbols = open("model-chords-moll/SYMBOLS_HIDDEN").readlines()
else:
    hiddensymbols = open("model-chords-dur/SYMBOLS_HIDDEN").readlines()

linesC = []

ofile = open("custom/viterbi/" + file)

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

cont = 0

for i in range(0, len(lines)):
    row = deepcopy(lines[i][0:3])

    row.append('')
    row.append('')
    row.append('')
    row.append('')
    row.append('')
    row.append('')

    if row[2][0] != '-' and row[2] != '':
        if i % 4 == 0:
            row[6] = hiddensymbols[int(output[cont])].split("/")[0]
            intervals = row[6].split(":")

            soprano = choraleManager.notepitch(row[2])

            intervals[0] = intervals[0].lstrip("-")

            for j in range(3, 6):
                if not intervals[j - 2].lstrip("-").isdigit():
                    row[j] = intervals[j - 2]
                else:
                    prefix = ""

                    if "-" in intervals[j - 2]:
                        prefix = "-"
                        intervals[j - 2] = intervals[j - 2].replace("-", "")

                    row[j] = prefix + choraleManager.notesymbol(soprano - (int(intervals[0]) - int(intervals[j - 2])))
        else:
            row[0] = ''
            row[1] = ''
        cont += 1
    else:
        row[0] = ''
        row[1] = ''
        row[2] = ''

    lines[i] = deepcopy(row)

f = open('custom/viterbi-results/' + file, 'w+')

choraleManager.writeheaders(f, headers[0], headers[1], headers[2], headers[3], headers[4], headers[5])
f.write("\n")
for line in lines:
    f.write("\t".join(line).replace("_", " ") + "\n")

f.close()
