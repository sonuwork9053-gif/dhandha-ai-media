"""Free offline Hindi narration: Devanagari text -> phonemes (own rules) -> Piper VITS .onnx via onnxruntime.

No external program is run. The voice model is a data file:
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-hi_IN-<voice>-medium.tar.bz2
Usage:
  from hindi_tts import Voice
  v = Voice("/path/vits-piper-hi_IN-rohan-medium/hi_IN-rohan-medium.onnx")
  durations = v.narrate(beats, "out.wav")     # one wav, returns exact seconds per beat
"""
import json, re, wave
import numpy as np
import onnxruntime as ort

CONS = {
 'क':'k','ख':'kʰ','ग':'ɡ','घ':'ɡʰ','ङ':'ŋ','च':'tʃ','छ':'tʃʰ','ज':'dʒ','झ':'dʒʰ','ञ':'ɲ',
 'ट':'ʈ','ठ':'ʈʰ','ड':'ɖ','ढ':'ɖʰ','ण':'ɳ','त':'t̪','थ':'t̪ʰ','द':'d̪','ध':'d̪ʰ','न':'n',
 'प':'p','फ':'pʰ','ब':'b','भ':'bʰ','म':'m','य':'j','र':'ɾ','ल':'l','व':'ʋ','श':'ʃ','ष':'ʃ','स':'s','ह':'ɦ','ळ':'l',
}
NUKTA = {'क':'k','ख':'x','ग':'ɡ','ज':'z','फ':'f','ड':'ɽ','ढ':'ɽʰ'}
MATRA = {'ा':'aː','ि':'ɪ','ी':'iː','ु':'ʊ','ू':'uː','े':'eː','ै':'ɛː','ो':'oː','ौ':'ɔː','ृ':'ɾɪ','ॉ':'ɔː','ॅ':'ɛ'}
VOWEL = {'अ':'ə','आ':'aː','इ':'ɪ','ई':'iː','उ':'ʊ','ऊ':'uː','ए':'eː','ऐ':'ɛː','ओ':'oː','औ':'ɔː','ऋ':'ɾɪ','ऑ':'ɔː','ऍ':'ɛ'}
SPOKEN = {'व्हाट्सऐप':'वॉट्सैप','फ्री':'फ़्री','फोन':'फ़ोन'}
LATIN = {'AI':'एआई','WhatsApp':'वॉट्सैप','CSV':'सीएसवी','PDF':'पीडीएफ','Excel':'एक्सेल','YouTube':'यूट्यूब','Dhandha':'धंधा'}
UNSTRESSED = set('का के की है हैं में से को पर और ने भी ही तो कि ये वो था थी थे एक या जो'.split())
VOW_RE = r'(?:aː|iː|uː|eː|ɛː|oː|ɔː|ə|ɪ|ʊ|ɛ)'

def _units(word):
    """Devanagari word -> list of [consonant_ipa or '', vowel_ipa or None, nasal_flag]."""
    out, i, n = [], 0, len(word)
    while i < n:
        ch = word[i]
        if ch in VOWEL:
            out.append(['', VOWEL[ch], False]); i += 1
        elif ch in CONS:
            c = CONS[ch]; i += 1
            if i < n and word[i] == '़': c = NUKTA.get(ch, c); i += 1
            if i < n and word[i] == '्': out.append([c, None, False]); i += 1; continue
            if i < n and word[i] in MATRA: out.append([c, MATRA[word[i]], False]); i += 1
            else: out.append([c, 'ə', False])
        elif ch in 'ंँ':
            if out: out[-1][2] = 'M' if ch == 'ं' else 'N'
            i += 1
        elif ch == 'ः':
            out.append(['ɦ', None, False]); i += 1
        else:
            i += 1
    return out

def _homorganic(nxt):
    if not nxt: return None
    c = nxt[0]
    if c[:1] in ('k','ɡ','x'): return 'ŋ'
    if c.startswith('tʃ') or c.startswith('dʒ'): return 'n'
    if c[:1] in ('ʈ','ɖ'): return 'ɳ'
    if c.startswith('t̪') or c.startswith('d̪') or c[:1] == 'n': return 'n'
    if c[:1] in ('p','b','m','f'): return 'm'
    return None

def word_ipa(word):
    u = _units(word)
    if not u: return ''
    # schwa deletion: final schwa, then medial schwa in VC_CV context (right to left)
    if len(u) > 1 and u[-1][1] == 'ə' and u[-1][0] and not u[-1][2]: u[-1][1] = None
    for k in range(len(u) - 2, 0, -1):
        if u[k][1] == 'ə' and u[k][0] and not u[k][2] and u[k-1][1] and u[k+1][1] and u[k+1][0]:
            u[k][1] = None
    parts = []
    for k, (c, v, nas) in enumerate(u):
        s = c + (v or '')
        if nas:
            h = _homorganic(u[k+1]) if (nas == 'M' and k + 1 < len(u)) else None
            if h: s += h
            elif v: s = c + v[0] + '̃' + v[1:]
        parts.append(s)
    ipa = ''.join(parts).replace('dʒɲ', 'ɡj')
    if word in UNSTRESSED: return ipa
    vs = list(re.finditer(VOW_RE, ipa))
    if not vs: return ipa
    pos = vs[-2].start() if len(vs) >= 2 else vs[0].start()
    return ipa[:pos] + 'ˈ' + ipa[pos:]

_N = ("शून्य एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह तेरह चौदह पंद्रह सोलह सत्रह अठारह उन्नीस बीस "
      "इक्कीस बाईस तेईस चौबीस पच्चीस छब्बीस सत्ताईस अट्ठाईस उनतीस तीस इकतीस बत्तीस तैंतीस चौंतीस पैंतीस छत्तीस सैंतीस अड़तीस उनतालीस चालीस "
      "इकतालीस बयालीस तैंतालीस चौवालीस पैंतालीस छियालीस सैंतालीस अड़तालीस उनचास पचास इक्यावन बावन तिरपन चौवन पचपन छप्पन सत्तावन अट्ठावन उनसठ साठ "
      "इकसठ बासठ तिरसठ चौंसठ पैंसठ छियासठ सड़सठ अड़सठ उनहत्तर सत्तर इकहत्तर बहत्तर तिहत्तर चौहत्तर पचहत्तर छिहत्तर सतहत्तर अठहत्तर उनासी अस्सी "
      "इक्यासी बयासी तिरासी चौरासी पचासी छियासी सत्तासी अट्ठासी नवासी नब्बे इक्यानवे बानवे तिरानवे चौरानवे पचानवे छियानवे सत्तानवे अट्ठानवे निन्यानवे").split()

def hindi_number(n):
    """0..99,99,99,999 -> Hindi words (Indian grouping: हज़ार, लाख, करोड़)."""
    n = int(n)
    if n < 100: return _N[n]
    out = []
    for div, name in ((10000000, 'करोड़'), (100000, 'लाख'), (1000, 'हज़ार'), (100, 'सौ')):
        q, n = divmod(n, div)
        if q: out.append((hindi_number(q) if q >= 100 else _N[q]) + ' ' + name)
    if n: out.append(_N[n])
    return ' '.join(out)

_DEV_DIG = str.maketrans('०१२३४५६७८९', '0123456789')

def normalize(sentence):
    """Digits, rupee sign and percent -> spoken Hindi words (digits were silently skipped before)."""
    s = sentence.translate(_DEV_DIG)
    s = re.sub(r'(?<=\d),(?=\d)', '', s)
    s = re.sub(r'₹\s*(\d+)', lambda m: hindi_number(m.group(1)) + ' रुपये', s)
    s = re.sub(r'(\d+)\s*%', lambda m: hindi_number(m.group(1)) + ' प्रतिशत', s)
    s = re.sub(r'\d{8,}', lambda m: ' '.join(_N[int(c)] for c in m.group(0)), s)      # phone-like: digit by digit
    s = re.sub(r'(\d+)\.(\d+)', lambda m: hindi_number(m.group(1)) + ' दशमलव ' + ' '.join(_N[int(c)] for c in m.group(2)), s)
    return re.sub(r'\d+', lambda m: hindi_number(m.group(0)), s)

def phonemize(sentence):
    sentence = normalize(sentence)
    for k, v in LATIN.items(): sentence = re.sub(r'\b' + k + r'\b', v, sentence)
    for k, v in SPOKEN.items(): sentence = sentence.replace(k, v)
    out = []
    for tok in re.findall(r'[ऀ-ॿ]+|[,?!]|।', sentence):
        if tok == '।': out.append('.')
        elif tok in ',?!': out.append(tok)
        else: out.append(' ' + word_ipa(tok))
    return ''.join(out).strip()

class Voice:
    def __init__(self, onnx_path, length_scale=1.0):
        cfg = json.load(open(onnx_path + '.json', encoding='utf-8'))
        self.ids = {k: v[0] for k, v in cfg['phoneme_id_map'].items()}
        self.sr = cfg['audio']['sample_rate']
        inf = cfg['inference']
        self.scales = np.array([inf['noise_scale'], inf['length_scale'] * length_scale, inf['noise_w']], dtype=np.float32)
        self.sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        self.missing = set()

    def synth(self, sentence):
        ph = phonemize(sentence)
        seq = [self.ids['^'], 0]
        for ch in ph:
            if ch in self.ids: seq += [self.ids[ch], 0]
            else: self.missing.add(ch)
        seq.append(self.ids['$'])
        x = np.array([seq], dtype=np.int64)
        y = self.sess.run(None, {'input': x, 'input_lengths': np.array([x.shape[1]], dtype=np.int64), 'scales': self.scales})[0]
        return y.squeeze().astype(np.float32)

    def narrate(self, beats, out_wav, sentence_gap=0.28, beat_gap=0.55):
        chunks, durs = [], []
        for b in beats:
            n0 = sum(len(c) for c in chunks)
            sents = [s.strip() for s in re.findall(r'[^।?!]+[।?!]?', b) if s.strip()]
            for s in sents:
                chunks.append(self.synth(s)); chunks.append(np.zeros(int(self.sr * sentence_gap), np.float32))
            chunks.append(np.zeros(int(self.sr * (beat_gap - sentence_gap)), np.float32))
            durs.append((sum(len(c) for c in chunks) - n0) / self.sr)
        a = np.concatenate(chunks); a = a / max(1e-6, float(np.abs(a).max())) * 0.9
        with wave.open(out_wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(self.sr); w.writeframes((a * 32767).astype(np.int16).tobytes())
        return durs


class KokoroVoice:
    """Kokoro v1.0 multi-lang ONNX (sherpa-onnx export) driven by the same own phonemizer.
    Model dir: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2
    Hindi speakers: hf_alpha=31, hf_beta=32, hm_omega=33, hm_psi=34. Output 24 kHz."""
    SPK = {'hf_alpha': 31, 'hf_beta': 32, 'hm_omega': 33, 'hm_psi': 34}
    def __init__(self, model_dir, speaker='hm_omega', speed=1.0):
        self.ids = {}
        for line in open(model_dir + '/tokens.txt', encoding='utf-8').read().splitlines():
            if not line.strip('\n'): continue
            sym, num = line.rsplit(' ', 1); self.ids[sym] = int(num)
        v = np.fromfile(model_dir + '/voices.bin', dtype=np.float32).reshape(-1, 510, 256)
        self.style = v[self.SPK[speaker]]
        self.sess = ort.InferenceSession(model_dir + '/model.onnx', providers=['CPUExecutionProvider'])
        self.sr, self.speed, self.missing = 24000, np.array([speed], dtype=np.float32), set()

    def synth(self, sentence):
        ph = phonemize(sentence).replace('̪', '').replace('tʃ', 'ʧ').replace('dʒ', 'ʤ').replace('ɦ', 'h')
        ids = []
        for ch in ph:
            if ch in self.ids: ids.append(self.ids[ch])
            else: self.missing.add(ch)
        ids = ids[:508]
        x = np.array([[0] + ids + [0]], dtype=np.int64)
        y = self.sess.run(None, {'tokens': x, 'style': self.style[len(ids)][None, :], 'speed': self.speed})[0]
        return np.asarray(y).squeeze().astype(np.float32)

    narrate = Voice.narrate
