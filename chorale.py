import re
from copy import deepcopy


class Chorale:
    tabbeddata = 1
    columnheadings = "PHRASE\tTAKT\tSOPRAN\tALT\tTENOR\tBASS\tHARMONIK"
    columns = 1
    columnbreaks = []

    notepitches = {
        'C': 0,
        'C#': 1, 'Db': 1, 'Csharp': 1, 'Dflat': 1,
        'D': 2,
        'D#': 3, 'Eb': 3, 'Dsharp': 3, 'Eflat': 3,
        'E': 4,
        'F': 5, 'E#': 5,
        'F#': 6, 'Gb': 6, 'Fsharp': 6, 'Gflat': 6,
        'G': 7,
        'G#': 8, 'Ab': 8, 'Gsharp': 8, 'Aflat': 8,
        'A': 9,
        'A#': 10, 'B': 10, 'Hb': 10,
        'H': 11, 'B#': 11,
        'H#': 12,
    }

    notesymbols = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'B', 'H', 'P']

    BEFORE = ["0", "0", "P", "P", "P", "P", "0", "P,P,P,P", "0", "P:P:P:P",
              "P;P;P;P", "P,P,P,P", "P,P,P,P", "P,P,P,P", "P,P,P,P"]

    AFTER = ["0", "0", "END", "END", "END", "END", "0", "P,P,P,P", "0",
             "P:P:P:P", "P;P;P;P", "P,P,P,P", "P,P,P,P", "P,P,P,P", "P,P,P,P"]

    # write out the header lines of a chorale data file
    def writeheaders(self, file, choralname, stimmen, tonart, takt, tempo, message):
        file.write("Choralname = " + choralname + "\n")
        file.write("Anzahl Stimmen = " + stimmen + "\n")
        file.write("Tonart = " + tonart + "\n")
        file.write("Takt = " + takt + "\n")
        file.write("Tempo = " + tempo + "\n")
        file.write(message + "\n")
        file.write(self.columnheadings + "\n")

    def readheaders(self, file):
        choralname = ""
        stimmen = ""
        tonart = ""
        takt = ""
        tempo = ""
        message = ""

        for line in file:
            if line == "\n":
                break

            if "Choralname" in line:
                choralname = line.split('=')[1].split("\n")[0][1:]
            if "Stimmen" in line:
                stimmen = line.split('=')[1].split("\n")[0][1:]
            if "Tonart" in line:
                tonart = line.split('=')[1].split("\n")[0][1:]
            if "Takt" in line:
                takt = line.split('=')[1].split("\n")[0][1:]
            if "Tempo" in line:
                tempo = line.split('=')[1].split("\n")[0][1:]
            if "Notentextausgabe" in line:
                message = line

        headers = file.readline()
        self.columnheadings = headers

        return [choralname, stimmen, tonart, takt, tempo, message]

    # convert a note representation into a numerical value
    def notepitch(self, note):

        if "P" in note:
            return -1

        match = re.match('^\-*([ABCDEFGH#b]+)[ _]*([-\d]+)', note)
        symbol = match.group(1)
        octave = int(match.group(2))

        noteval = self.notepitches[symbol]
        return noteval + (octave + 4) * 12

    def key2pitch(self, tonart):
        tone = tonart.split("-")[0]
        tone = tone + " -4"
        return self.notepitch(tone)

    def notesymbol(self, note):  # convert a numerical note value to a textual representation
        noteval = note % 12
        octave = ((note - noteval) / 12) - 4
        symbol = self.notesymbols[noteval]

        if len(symbol) == 1:
            symbol += " "

        symbol += str(int(octave))

        return symbol

    def transposerow(self, keypitch, row):

        for i in range(2, 6):
            if row[i] != "" and "P" not in row[i]:
                if row[i][0] == "-":
                    row[i] = "-" + self.notesymbol(self.notepitch(row[i]) - keypitch)
                else:
                    row[i] = "" + self.notesymbol(self.notepitch(row[i]) - keypitch)

        return row

    def readchorale(self, filename, notranspose=False):
        f = open(filename, 'r')

        headers = self.readheaders(f)

        [choralname, stimmen, tonart, takt, tempo, message] = headers

        keypitch = self.key2pitch(tonart)

        # event we're 'in' (so nothing to start with)
        within = self.BEFORE

        lines = []

        f.readline()

        cont = 0
        for line in f:
            line = line.split("\n")[0]

            row = line.split("\t")

            if row == ['']:
                row = ['', '', '', '', '', '', '']
            elif not notranspose:
                # transpose to C major/C minor
                self.transposerow(keypitch, row)

            for i in range(0, 7):
                if row[i] == '':
                    if within[i][0] != "-":
                        row[i] = "-" + within[i]
                    else:
                        row[i] = within[i]
                else:
                    row[i] = row[i].replace(" ", "_")  # replace any spaces in tokens with underscores
                    within[i] = row[i]

            intervals = ["0", "0", "0", "0"]
            bass = None

            for i in range(5, 1, -1):
                if "P" in row[i] or row[i] == "END":
                    intervals[i - 2] = row[i]
                else:
                    if bass is None:
                        bass = self.notepitch(row[i])

                    intervals[i - 2] = str(self.notepitch(row[i]) - bass)
                    if row[i][0] == "-":
                        intervals[i - 2] = "-" + intervals[i - 2]

            row.append(":".join(intervals))
            lines.append(row)

            cont += 1

        f.close()

        if "/" not in lines[0][1]:
            maxbeat = 0
            beat = -1

            for i in range(0, len(lines)):

                row = lines[i]
                if i % 4 == 0:
                    beat += 1

                if "-" not in row[1] and row[1] != "0":
                    beat = 1

                if i % 4 != 0:
                    row[1] = "-" + str(beat)
                else:
                    row[1] = str(beat)

                if beat > maxbeat:
                    maxbeat = beat

                lines[i] = row

            for i in range(0, len(lines)):
                lines[i][1] = lines[i][1] + "/" + str(maxbeat)

        return [headers, lines]

    def beatrows(self, lines):

        linesB = []

        for i in range(0, len(lines), +4):
            row = lines[i]
            ornamentation = []
            tornamentation = []  # transposed relative to initial notes

            for j in range(0, 4):
                sequence = []
                tsequence = []

                sequence = [row[j + 2], lines[i + 1][j + 2], lines[i + 2][j + 2], lines[i + 3][j + 2]]
                ornamentation.append(",".join(sequence))

                firstnote = None

                for note in sequence:
                    firstnote = self.notepitch(note)

                    if "-" not in note and "P" not in note and note != "" and note != "END":
                        tsequence.append(str(self.notepitch(note) - firstnote))
                    else:
                        tsequence.append("-")

                tornamentation.append(",".join(tsequence))

            row = row[0:7] + ["/".join(ornamentation)] + [row[7]]
            row.append(";".join(tornamentation))
            row.append(ornamentation[0])
            row.append(tornamentation[1])
            row.append(tornamentation[2])
            row.append(tornamentation[3])

            if i + 4 > len(lines) - 1:
                row = row[0:7] + ["END,END,END,END"] + row[7:len(row)]
            else:
                nextbeatrow = lines[i + 4]
                intervals = []  # to next notes
                for j in range(0, 4):
                    # / - * P /
                    if "P" not in nextbeatrow[j + 2] and "P" not in row[j + 2]:
                        intervals.append(str(self.notepitch(nextbeatrow[j + 2]) - self.notepitch(row[j + 2])) + ">" +
                                         str(self.notepitch(row[j + 2]) % 12))
                    else:
                        intervals.append("P")

                row = row[0:7] + [",".join(intervals)] + row[7:len(row)]  # intervals to next beat's notes

            linesB.append(row)

        return linesB

    def unpackchordsymbols(self, lines):
        for i in range(0, len(lines)):
            row = deepcopy(lines[i])

            if len(row) == 7 and ":" in row[6] and "/" in row[6]:
                [soprano, row[3], row[4], row[5]] = "/".split(row[6])
            elif len(row) == 7 and ":" in row[6]:
                if row[2] != "":
                    intervals = row[6].split(":")

                    soprano = self.notepitch(row[2])

                    intervals[0] = intervals[0].lstrip("-")

                    for j in range(3, 6):
                        if not intervals[j - 2].lstrip("-").isdigit():
                            row[j] = intervals[j - 2]
                        else:
                            prefix = ""

                            if "-" in intervals[j - 2]:
                                prefix = "-"
                                intervals[j - 2] = intervals[j - 2].replace("-", "")

                            row[j] = prefix + self.notesymbol(soprano - (int(intervals[0]) - int(intervals[j - 2])))

            lines[i] = deepcopy(row)

        return lines

    def tidychorale(self, lines):
        for i in range(0, len(lines)):
            row = ["", "", "", "", "", "", "", ""]
            ev = deepcopy(row)

            for k in range(0, len(lines[i])):
                row[k] = lines[i][k]

            # for j in range(len(row), 7, -1):
            #     print(j)
            #     row[j] = ""

            for j in range(0, 7):
                if row[j] != "" and row[j][0] == "-":
                    row[j] = ""
                else:
                    ev[j] = row[j]

                row[j] = row[j].replace("_", " ")

            lines[i] = deepcopy(row)

        return lines

    def writechorale(self, filename, headers, lines):
        f = open(filename, 'w+')

        [choralname, stimmen, tonart, takt, tempo, message] = headers

        self.writeheaders(f, choralname, stimmen, tonart, takt, tempo, message)
        for i in range(0, len(lines)):
            f.write("\t".join(lines[i]) + "\t\t\n")

        f.close()

