"""Narration for video 02. Usage: python3 narrate.py /path/hi_IN-pratham-medium.onnx   (writes narr-src.wav, dur.json, narr-short-src.wav, dur-short.json)"""
import sys, os, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from hindi_tts import Voice, phonemize
V=Voice(sys.argv[1], length_scale=1.12)
for src,wav,dur,gap in (("beats.json","narr-src.wav","dur.json",0.55),("beats-short.json","narr-short-src.wav","dur-short.json",0.45)):
    beats=json.load(open(os.path.join(HERE,src),encoding="utf-8"))
    d=V.narrate(beats, os.path.join(HERE,wav), beat_gap=gap); json.dump(d, open(os.path.join(HERE,dur),"w"))
    print(src, len(beats), "beats", round(sum(d),1), "s", [round(x,1) for x in d])
    for b in beats: print("  ", phonemize(b))
print("missing:", V.missing)
