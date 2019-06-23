from midiutil.MidiFile import *
import pickle
from chorale import Chorale

with open('model-chords-dur/DICTIONARY.pkl', 'rb') as f:
    dictionary = pickle.load(f)

sample = open("sample.txt")
lines = sample.readlines()
sample.close()

input_midi = MIDIFile(1, deinterleave=False)
input_midi.addTempo(0, 0, 100)

input_midi.addTimeSignature(0, 0, 4, 2, 24)

choraleManager = Chorale()

stressbar = False


def addnote(start, note, duration, newbar, channel, time):
    if note == "P" or note == "":
        return 1

    volume = 80

    if newbar and stressbar:
        volume = 96

    print(str(channel) + " " + str(choraleManager.notepitch(note)) +
         " " + str(start) + " " + str(duration) + " " + str(volume))

    if choraleManager.notepitch(note) == -1:
        input_midi.addNote(0, channel, 0, start, 4, 0)
        time += 4
    else:
        input_midi.addNote(0, channel, choraleManager.notepitch(note), start, duration, volume)


time = 0
duration = 1

for line in lines:
    hid = int(line.split("\n")[0].split(" ")[0]) + 1
    vis = int(line.split("\n")[0].split(" ")[1]) + 1
    row = dictionary[str(hid) + " " + str(vis)].split(" ")

    if row[0] == "END":
        break

    for i in range(0, 4):
        addnote(time, row[i].replace("_", " "), duration, False, i, time)

    time += 1

with open("sample.mid", "wb") as output_file:
    input_midi.writeFile(output_file)

