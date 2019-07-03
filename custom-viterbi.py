import numpy as np
import pickle
import sys

if __name__ == '__main__':
    name = sys.argv[1]

    musicfile = open('custom/music/' + name)
    music = musicfile.read().splitlines()
    musicfile.close()

    if 'dur' in music[2]:
        fvisible = open('model-chords-dur/SYMBOLS_VISIBLE')
    else:
        fvisible = open('model-chords-moll/SYMBOLS_VISIBLE')

    visible = fvisible.read().splitlines()
    fvisible.close()

    a = []

    for line in music[9:]:
        if line != "":
            note = line.split("\t")[2]
            if note != "":
                if "-" in note:
                    note = "-" + note.split("-")[0] + note.split("-")[1]

                note = note.replace(" ", "_")
                a.append(visible.index(note) - 1)
    a = np.atleast_2d(a).T

    if 'dur' in music[2]:
        f = open('model-chords-dur/hmm-model.pkl', 'rb')
    else:
        f = open('model-chords-moll/hmm-model.pkl', 'rb')

    model = pickle.load(f)
    f.close()

    b = model.decode(a)

    f = open('custom/viterbi/' + name, 'w+')
    for i in range(0, len(b[1])):
        f.write(str(b[1][i] + 1) + " " + str(a[i][0] + 1) + "\n")

    f.close()
