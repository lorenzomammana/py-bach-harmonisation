from chorale import Chorale
from copy import deepcopy
import sys

chordslocation = sys.argv[1]
ornamentationlocation = sys.argv[2]

f = open(chordslocation)
chords = f.read().splitlines()
lines = chords[0:10]
chords = chords[10:]
f.close()

f = open(ornamentationlocation)
ornamentation = f.read().splitlines()[10:]
f.close()

choraleManager = Chorale()

for i in range(0, len(chords), 4):
    rows = [deepcopy(chords[i]).split("\t"), deepcopy(chords[i + 1]).split("\t"), deepcopy(chords[i + 2]).split("\t"),
            deepcopy(chords[i + 3]).split("\t")]

    orn = ornamentation[i].split("\t")[6].split("/")

    if rows[0][2] != "":
        for j in range(0, 3):
            pitchchange = orn[j].split(",")

            for k in range(1, 4):
                change = int(pitchchange[k])
                if change != 0 and int(pitchchange[k - 1]) != change:
                    note = choraleManager.notepitch(rows[0][3 + j])
                    rows[k][3 + j] = choraleManager.notesymbol(note + change)

    for row in rows:
        lines.append(deepcopy(row))

f = open('custom/ornamentation/' + chordslocation.split("/").pop(), 'w+')

for line in lines:
    if isinstance(line, list):
        f.write("\t".join(line) + "\n")
    else:
        f.write(line + "\n")

f.close()
