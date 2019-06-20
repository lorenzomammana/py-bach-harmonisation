from chorale import Chorale
import sys
from midiutil.MidiFile import *
import math


def addnote(start, note, duration, newbar, channel):
    if note == "P" or note == "":
        return 1

    volume = 80

    if newbar and stressbar:
        volume = 96

    # print(str(channel) + " " + str(choraleManager.notepitch(note)) +
    #     " " + str(start) + " " + str(duration) + " " + str(volume))
    input_midi.addNote(0, channel, choraleManager.notepitch(note), start, duration, volume)


if __name__ == '__main__':
    transpose = False
    toppart = 0

    filename = sys.argv[1]

    if sys.argv[2] == "transpose":
        transpose = True

    f = open(filename, 'r')

    if "/" in filename:
        outputfile = "midi/" + filename.split("/").pop().split(".")[0] + ".mid"
    else:
        outputfile = "midi/" + filename.split(".")[0] + ".mid"

    choraleManager = Chorale()

    [choralname, stimmen, tonart, takt, tempo, message] = choraleManager.readheaders(f)

    input_midi = MIDIFile(1, deinterleave=False)

    input_midi.addTempo(0, 0, int(tempo))
    numerator = int(takt.split("/")[0])
    denominator = int(takt.split("/")[1])

    print("Time : " + takt)
    input_midi.addTimeSignature(0, 0, numerator, int(math.log2(denominator)), 24)
    keypitch = 0

    if transpose:
        keypitch = - choraleManager.key2pitch(tonart)

    stressbar = False

    started = [0, 0, 0, 0]
    current = ["", "", "", ""]
    newbar = ["", "", "", ""]

    beat = -1/16

    f.readline()  # read blank line
    f.readline()  # read blank line
    lines = f.readlines()
    f.close()

    for line in lines:
        beat += 1/16

        if line != "\t\t\t\t\t\t\t\t\t\n":
            [phrase, takt, sopran, alt, tenor, bass, harmonik] = \
                choraleManager.transposerow(keypitch, line.split("\t")[0:7])

            newnotes = [sopran, alt, tenor, bass]

            for i in range(toppart, 4):
                if newnotes[i] != "" and newnotes[i][0] != "-":
                    duration = beat - started[i]
                    if beat == 0:
                        duration = 1 / denominator
                    addnote(started[i] * denominator, current[i], duration * denominator, newbar[i], i)
                    current[i] = newnotes[i]
                    started[i] = beat

                    if takt != "" and takt[0] == "1":
                        newbar[i] = True
                    else:
                        newbar[i] = False

    with open(outputfile, "wb") as output_file:
        input_midi.writeFile(output_file)
