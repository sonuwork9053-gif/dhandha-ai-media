"""Estimate how long each beat of a Hindi narration lasts inside ONE ElevenLabs take.

Raw character counts drift because matras and conjuncts add characters but not time,
and because pauses at sentence ends are not proportional to text. This counts spoken
units (aksharas / Latin syllable-ish groups) and adds explicit pause weights, then
scales everything to the real total duration reported by ElevenLabs.
"""
import re, unicodedata

SENT_PAUSE = 3.0    # in units, after । ? !
COMMA_PAUSE = 1.2   # after , : ;
PARA_PAUSE = 4.5    # between beats (blank line in the TTS text)

def units(text: str) -> float:
    n = 0.0
    for ch in text:
        cat = unicodedata.category(ch)
        if 'ऀ' <= ch <= 'ॿ':
            # independent vowels and consonants are spoken units; matras, virama, nukta are not
            if cat == 'Lo': n += 1.0
            if ch == '्': n -= 0.5      # virama joins two consonants into one cluster
        elif ch.isdigit(): n += 2.0
    n += 0.6 * len(re.findall(r'[A-Za-z]', text))   # Latin words inside Hindi text
    n += SENT_PAUSE * len(re.findall(r'[।?!]', text)) + COMMA_PAUSE * len(re.findall(r'[,:;]', text))
    return n + PARA_PAUSE

def beat_durations(beats, total_seconds):
    w = [units(b) for b in beats]
    return [total_seconds * x / sum(w) for x in w]

if __name__ == '__main__':
    import sys, json
    beats = json.load(open(sys.argv[1])); print([round(x, 2) for x in beat_durations(beats, float(sys.argv[2]))])
