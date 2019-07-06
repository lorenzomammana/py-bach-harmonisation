# py-bach-harmonisation
Generation of bach chorales harmonisation using Hidden Markov Models.

We gratefully thank the author of "Harmonising Chorales by Probabilistic Inference" (https://github.com/johndpope/allan-harmony) which most of our work is based on.

## Getting started

### Prerequisites
We've worked with Python 3 and this packages:
```
pip install midiutil
pip install hmmlearn
```
### Harmonisation model
First we need to parse the chorales in order to obtain hidden and visible states:
```
python hmm-data.py chords-dur chordtransposed/HARMONIK SOPRAN train_dur test_dur
python hmm-data.py chords-moll chordtransposed/HARMONIK SOPRAN train_moll test_moll
```
This command produces, for each training and testing file, a second file located at model-chords-dur/input which contains a sequence of [idx-hidden idx-visible]. These indices relate respectively to the files at model-chords-dur/SYMBOLS_HIDDEN and model-chords-dur/SYMBOLS_VISIBLE.
Dur refers to chorales in major key, while moll refers to chorales in minor key.
After this operation we can train and test the model:
```
python hmm-model.py chords-dur train_dur test_dur viterbi
python hmm-model.py chords-moll train_moll test_moll viterbi
```
For each test file we compute the most probable hidden states sequence using the Viterbi algorithm.
The results must be converted back to music notation:
```
python hmm-output-expand.py chords-dur viterbi
python hmm-output-expand.py chords-moll viterbi
```
Finally we can create the MIDI file for a generated chorale, for example:
```
python chorale2midi.py model-chords-dur/viterbi-results/bch001.txt transpose
```
### Ornamentation model
After the creation of the harmonisation model, we can create the ornamentation model in a very similar way:
```
python hmm-ornamentation-data.py ornamentation-dur chords-dur viterbi train_dur test_dur
python hmm-ornamentation-data.py ornamentation-moll chords-moll viterbi train_moll test_moll
python hmm-model.py ornamentation-dur train_dur test_dur viterbi
python hmm-model.py ornamentation-moll train_moll test_moll viterbi
python hmm-ornamentation-expand.py ornamentation-dur chords-dur viterbi viterbi
python hmm-ornamentation-expand.py ornamentation-moll chords-moll viterbi viterbi
```
If we want to apply the ornamentation to an harmonised file:
```
python add-ornamentation.py model-chords-dur/viterbi-results/bch001.txt model-ornamentation-dur/viterbi-results/bch001.txt
```
We can now create the ornamented MIDI with the same function described above.
### Harmonise modern music
Given a generic melody file which follows the same structure of those in custom/music we can compute the most probable harmonisation under the models in this way:
```
python custom-viterbi.py blue.txt
python custom-output-expand.py blue.txt
python chorale2midi.py custom/viterbi-results/blue.txt transpose
```

