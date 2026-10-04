"""Owner's-voice narration: any narration wav -> same words in the owner's voice (kNN-VC, pure numpy).

How it works (Baas, van Niekerk, Kamper 2023, "Voice Conversion With Just Nearest Neighbors", MIT licence):
  1. WavLM-Large layer-6 features of the source narration (free TTS voice) and of the owner's reference recording.
  2. Every source frame is replaced by the mean of its 4 nearest reference frames (cosine distance).
  3. A HiFi-GAN vocoder turns those frames back into 16 kHz audio -> the owner's timbre, the source's words and timing.

No external program is run and torch is not needed: the two weight files are plain data, read by a restricted
unpickler (tensors only) and executed by the numpy code below.
  https://github.com/bshall/knn-vc/releases/download/v0.1/WavLM-Large.pt           (1.26 GB)
  https://github.com/bshall/knn-vc/releases/download/v0.1/prematch_g_02500000.pt   (66 MB)

Usage:
  from own_voice import OwnVoice
  ov = OwnVoice("/tmp/knnvc", "kit/voice/owner-ref.wavlm6.npy")   # the owner's reference features (or a .wav to build them)
  ov.convert_file("narr-tts.wav", "narr-own.wav")             # same duration, 16 kHz mono
"""
import io, math, os, pickle, wave, zipfile
import numpy as np
from numpy.lib.stride_tricks import as_strided
from scipy.special import erf
from scipy.signal import resample_poly

F32 = np.float32


# ---------- weight loading (restricted unpickler: tensors and plain containers only) ----------
class _Storage:
    def __init__(self, dtype): self.dtype = dtype

_STORAGES = {'FloatStorage': np.float32, 'LongStorage': np.int64, 'HalfStorage': np.float16,
             'DoubleStorage': np.float64, 'IntStorage': np.int32, 'BoolStorage': np.bool_}

def _rebuild_tensor_v2(storage, offset, size, stride, *a):
    n = int(np.prod(size)) if len(size) else 1
    if len(size) == 0: return storage[offset:offset + 1].reshape(())
    arr = as_strided(storage[offset:], shape=tuple(size), strides=tuple(s * storage.itemsize for s in stride))
    return np.ascontiguousarray(arr)

def _rebuild_parameter(data, requires_grad, hooks): return data

class _Unpickler(pickle.Unpickler):
    def __init__(self, f, zf, root):
        super().__init__(f); self.zf, self.root = zf, root
    def find_class(self, mod, name):
        if mod == 'collections' and name == 'OrderedDict':
            import collections; return collections.OrderedDict
        if mod == 'torch._utils' and name == '_rebuild_tensor_v2': return _rebuild_tensor_v2
        if mod == 'torch._utils' and name == '_rebuild_parameter': return _rebuild_parameter
        if mod == 'torch' and name in _STORAGES: return _Storage(_STORAGES[name])
        raise pickle.UnpicklingError(f'blocked: {mod}.{name}')
    def persistent_load(self, pid):
        _, st, key, _loc, _n = pid
        return np.frombuffer(self.zf.read(f'{self.root}/data/{key}'), dtype=st.dtype)

def load_pt(path):
    zf = zipfile.ZipFile(path)
    pkl = [n for n in zf.namelist() if n.endswith('data.pkl')][0]
    return _Unpickler(io.BytesIO(zf.read(pkl)), zf, pkl.rsplit('/', 1)[0]).load()


# ---------- numpy layers ----------
def conv1d(x, w, b=None, stride=1, dilation=1, pad=0):
    """x [C,T], w [O,C,K] -> [O,T']"""
    if pad: x = np.pad(x, ((0, 0), (pad, pad)))
    x = np.ascontiguousarray(x, dtype=F32)
    C, T = x.shape; O, _, K = w.shape
    To = (T - dilation * (K - 1) - 1) // stride + 1
    win = as_strided(x, shape=(C, To, K), strides=(x.strides[0], x.strides[1] * stride, x.strides[1] * dilation))
    cols = np.ascontiguousarray(win.transpose(1, 0, 2)).reshape(To, C * K)
    y = cols @ w.reshape(O, C * K).T
    if b is not None: y += b
    return y.T

def conv_transpose1d(x, w, b, stride, pad):
    """x [Cin,T], w [Cin,Cout,K] (torch layout)"""
    Cin, T = x.shape; K = w.shape[2]
    up = np.zeros((Cin, (T - 1) * stride + 1), F32); up[:, ::stride] = x
    wf = np.ascontiguousarray(w[:, :, ::-1].transpose(1, 0, 2))
    return conv1d(up, wf, b, pad=K - 1 - pad)

def layer_norm(x, g, b, eps=1e-5):
    m = x.mean(-1, keepdims=True); v = ((x - m) ** 2).mean(-1, keepdims=True)
    return (x - m) / np.sqrt(v + eps) * g + b

def gelu(x): return (0.5 * x * (1.0 + erf(x / math.sqrt(2.0)))).astype(F32)
def lrelu(x, s=0.1): return np.where(x > 0, x, x * s).astype(F32)
def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))
def wn(g, v, axes): return (v * (g / np.sqrt((v ** 2).sum(axis=axes, keepdims=True)))).astype(F32)


class WavLM6:
    """WavLM-Large, feature extractor + first 6 transformer layers (what kNN-VC uses)."""
    H, D, LAYERS = 16, 1024, 6
    def __init__(self, path):
        sd = load_pt(path)['model']
        self.p = {k: np.asarray(v, dtype=F32) for k, v in sd.items()
                  if not k.startswith('encoder.layers.') or int(k.split('.')[2]) < self.LAYERS}
        p = self.p
        self.pos_w = wn(p['encoder.pos_conv.0.weight_g'], p['encoder.pos_conv.0.weight_v'], (0, 1))
        self._bias_cache = {}

    def _rel_bias(self, T):
        if T in self._bias_cache: return self._bias_cache[T]
        emb = self.p['encoder.layers.0.self_attn.relative_attention_bias.weight']   # [320,16]
        nb, md = emb.shape[0] // 2, 800
        rel = np.arange(T)[None, :] - np.arange(T)[:, None]
        bucket = (rel > 0).astype(np.int64) * nb
        r = np.abs(rel); me = nb // 2
        large = me + (np.log(np.maximum(r, 1) / me) / math.log(md / me) * (nb - me)).astype(np.int64)
        bucket += np.where(r < me, r, np.minimum(large, nb - 1))
        out = np.ascontiguousarray(emb[bucket].transpose(2, 0, 1))                     # [H,T,T]
        self._bias_cache = {T: out}
        return out

    def features(self, wav16):
        p = self.p
        x = np.asarray(wav16, F32)[None, :]
        for i, (k, s) in enumerate([(10, 5), (3, 2), (3, 2), (3, 2), (3, 2), (2, 2), (2, 2)]):
            pre = f'feature_extractor.conv_layers.{i}.'
            x = conv1d(x, p[pre + '0.weight'], p.get(pre + '0.bias'), stride=s)
            x = gelu(layer_norm(x.T, p[pre + '2.1.weight'], p[pre + '2.1.bias']).T)
        x = layer_norm(x.T, p['layer_norm.weight'], p['layer_norm.bias'])              # [T,512]
        x = x @ p['post_extract_proj.weight'].T + p['post_extract_proj.bias']          # [T,1024]
        # positional conv: k=128, pad=64, groups=16, drop last frame, gelu
        xc = x.T; G = 16; cg = self.D // G; outs = []
        for g in range(G):
            outs.append(conv1d(xc[g * cg:(g + 1) * cg], self.pos_w[g * cg:(g + 1) * cg], None, pad=64))
        pc = np.concatenate(outs, 0)[:, :-1] + p['encoder.pos_conv.0.bias'][:, None]
        x = x + gelu(pc).T
        T = x.shape[0]; H, hd = self.H, self.D // self.H
        pos_bias = self._rel_bias(T)
        for l in range(self.LAYERS):
            pre = f'encoder.layers.{l}.'
            q_in = layer_norm(x, p[pre + 'self_attn_layer_norm.weight'], p[pre + 'self_attn_layer_norm.bias'])
            ql = q_in.reshape(T, H, hd).transpose(1, 0, 2)                              # [H,T,hd]
            g = sigmoid((ql @ p[pre + 'self_attn.grep_linear.weight'].T + p[pre + 'self_attn.grep_linear.bias'])
                        .reshape(H, T, 2, 4).sum(-1))
            ga, gb = g[..., 0:1], g[..., 1:2]
            gate = ga * (gb * p[pre + 'self_attn.grep_a'].reshape(H, 1, 1) - 1.0) + 2.0   # [H,T,1]
            bias = gate * pos_bias
            def proj(n): return (q_in @ p[pre + f'self_attn.{n}_proj.weight'].T + p[pre + f'self_attn.{n}_proj.bias']) \
                .reshape(T, H, hd).transpose(1, 0, 2)
            q, k, v = proj('q'), proj('k'), proj('v')
            a = (q @ k.transpose(0, 2, 1)) / math.sqrt(hd) + bias
            a = np.exp(a - a.max(-1, keepdims=True)); a /= a.sum(-1, keepdims=True)
            o = (a @ v).transpose(1, 0, 2).reshape(T, self.D)
            x = x + (o @ p[pre + 'self_attn.out_proj.weight'].T + p[pre + 'self_attn.out_proj.bias'])
            h = layer_norm(x, p[pre + 'final_layer_norm.weight'], p[pre + 'final_layer_norm.bias'])
            h = gelu(h @ p[pre + 'fc1.weight'].T + p[pre + 'fc1.bias'])
            x = (x + (h @ p[pre + 'fc2.weight'].T + p[pre + 'fc2.bias'])).astype(F32)
        return x                                                                       # [T,1024], 50 frames/s


class HiFiGAN:
    """kNN-VC 'prematched' HiFi-GAN v1: 1024-dim WavLM frames -> 16 kHz audio (hop 320)."""
    RATES, UK, RK, DIL = [10, 8, 2, 2], [20, 16, 4, 4], [3, 7, 11], [1, 3, 5]
    def __init__(self, path):
        sd = load_pt(path)['generator']
        sd = {k: np.asarray(v, dtype=F32) for k, v in sd.items()}
        w = {}
        for k in sd:
            if k.endswith('.weight_g'):
                base = k[:-9]; v = sd[base + '.weight_v']
                w[base + '.weight'] = wn(sd[k], v, (1, 2))
            elif not k.endswith('.weight_v'):
                w[k] = sd[k]
        self.w = w

    def __call__(self, feats):
        w = self.w
        x = (feats @ w['lin_pre.weight'].T + w['lin_pre.bias']).T.astype(F32)
        x = conv1d(x, w['conv_pre.weight'], w['conv_pre.bias'][None], pad=3)
        for i, (u, k) in enumerate(zip(self.RATES, self.UK)):
            x = conv_transpose1d(lrelu(x), w[f'ups.{i}.weight'], w[f'ups.{i}.bias'][None], u, (k - u) // 2)
            xs = 0
            for j, rk in enumerate(self.RK):
                r = x; pre = f'resblocks.{i * 3 + j}.'
                for m, d in enumerate(self.DIL):
                    t = conv1d(lrelu(r), w[pre + f'convs1.{m}.weight'], w[pre + f'convs1.{m}.bias'][None],
                               dilation=d, pad=(rk * d - d) // 2)
                    t = conv1d(lrelu(t), w[pre + f'convs2.{m}.weight'], w[pre + f'convs2.{m}.bias'][None],
                               pad=(rk - 1) // 2)
                    r = t + r
                xs = xs + r
            x = (xs / 3).astype(F32)
        x = conv1d(lrelu(x, 0.01), w['conv_post.weight'], w['conv_post.bias'][None], pad=3)
        return np.tanh(x[0])


# ---------- audio helpers ----------
def read_wav(path):
    with wave.open(path, 'rb') as f:
        sr, ch, n = f.getframerate(), f.getnchannels(), f.getnframes()
        a = np.frombuffer(f.readframes(n), dtype=np.int16).astype(F32) / 32768.0
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    return a, sr

def write_wav(path, a, sr):
    a = np.clip(a, -1, 1)
    with wave.open(path, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr); f.writeframes((a * 32767).astype(np.int16).tobytes())

def to16k(a, sr):
    if sr == 16000: return a.astype(F32)
    g = math.gcd(sr, 16000)
    return resample_poly(a, 16000 // g, sr // g).astype(F32)


class OwnVoice:
    def __init__(self, model_dir, ref_wav, topk=4, cache=None):
        self.wavlm = WavLM6(os.path.join(model_dir, 'WavLM-Large.pt'))
        self.voc = HiFiGAN(os.path.join(model_dir, 'prematch_g.pt'))
        self.topk = topk
        if ref_wav.endswith('.npy'): cache = ref_wav
        cache = cache or os.path.splitext(ref_wav)[0] + '.wavlm6.npy'
        if cache == ref_wav or (os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(ref_wav)):
            self.ref = np.load(cache).astype(F32)
        else:
            a, sr = read_wav(ref_wav)
            self.ref = self._feats_long(to16k(a, sr)); np.save(cache, self.ref.astype(np.float16))
        self.ref_n = self.ref / np.linalg.norm(self.ref, axis=1, keepdims=True)

    def _feats_long(self, a, chunk_s=12):
        """Features for long audio, in chunks cut at the quietest point near each boundary."""
        out, i, n = [], 0, len(a)
        while i < n:
            j = min(n, i + chunk_s * 16000)
            if j < n:
                lo = j - 2 * 16000
                env = np.convolve(np.abs(a[lo:j]), np.ones(800) / 800, 'same')
                j = lo + int(env.argmin()); j -= (j - i) % 320
            if j - i < 800: break
            out.append(self.wavlm.features(a[i:j])); i = j
        return np.concatenate(out, 0)

    def convert(self, a, sr):
        """a: float mono audio -> converted audio at 16 kHz with the same duration."""
        a16 = to16k(a, sr)
        q = self._feats_long(a16)
        qn = q / np.linalg.norm(q, axis=1, keepdims=True)
        sim = qn @ self.ref_n.T
        idx = np.argpartition(-sim, self.topk, axis=1)[:, :self.topk]
        conv = self.ref[idx].mean(1).astype(F32)
        out, step, ctx = [], 400, 16                       # vocode 8 s at a time with 0.32 s context each side
        for s in range(0, len(conv), step):
            a0, b0 = max(0, s - ctx), min(len(conv), s + step + ctx)
            y = self.voc(conv[a0:b0])
            out.append(y[(s - a0) * 320:(s - a0) * 320 + min(step, len(conv) - s) * 320])
        y = np.concatenate(out)
        y = np.pad(y, (0, max(0, len(a16) - len(y))))[:len(a16)]
        return y / max(1e-6, float(np.abs(y).max())) * 0.9

    def convert_file(self, src_wav, out_wav):
        a, sr = read_wav(src_wav)
        write_wav(out_wav, self.convert(a, sr), 16000)
        return len(a) / sr
