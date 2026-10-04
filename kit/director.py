"""Shared frame-accurate stage for Dhandha AI videos.
Long video (1920x1080): see video-03/src/record.py.   Short (1080x1920): see video-03/src/short.py.
    with Stage(html, beats, total, out_mp4, init_js, durations=dur, zoom=1.36, maxw=1350) as s:
        s.js("D.progress(%f); D.title('टेलर की दुकान','ऑर्डर लेट,<br>ग्राहक <b>नाराज़?</b>')" % s.T); s.until(s.marks[1])
        s.js("D.wipe(()=>D.unpanel()); D.chapter('1 · समस्या'); D.capPop('ऊपर <b>चार गिनती</b>')"); s.hold(.8); s.js("D.focus('.stats',1.4)"); s.until(s.marks[2])
        s.js("D.unzoom(); D.unspot(); D.steps('तीन काम, एक टूल',['ऑर्डर <b>लिखो</b>','हाल <b>बदलो</b>','वॉट्सऐप <b>भेजो</b>'])"); s.until(s.marks[3])
"""
import os, time, shutil, subprocess, glob, base64
from playwright.sync_api import sync_playwright
from timing import beat_durations

KIT = os.path.dirname(os.path.abspath(__file__))
LOGO = "file://" + os.path.join(KIT, "brand", "dhandha-ai-logo.png")

DIRECTOR = r"""
(() => {
  const css = document.createElement('style');
  css.textContent = `
  html{background:#f4f6fb} body{padding:22px 0 0 !important}
  .wrap{zoom:1.14;max-width:1480px !important} .row{padding:11px 16px !important;margin-bottom:8px !important} .sub{margin-bottom:14px !important} .stats,form{margin-bottom:14px !important} .foot{display:none}
  #dCap{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:#0B1220;color:#fff;font:700 46px Poppins;padding:18px 40px;border-radius:18px;z-index:9000;white-space:nowrap;box-shadow:0 14px 40px #0006;transition:opacity .35s;opacity:0}
  #dCap b{color:#FFC400}
  #dSpot{position:fixed;border:6px solid #FFC400;border-radius:22px;box-shadow:0 0 0 9999px rgba(11,18,32,.55);z-index:8000;transition:all .55s cubic-bezier(.2,.8,.2,1);opacity:0;pointer-events:none}
  #dCur{position:fixed;left:1500px;top:900px;width:44px;height:44px;z-index:9500;transition:left .7s cubic-bezier(.2,.8,.2,1),top .7s cubic-bezier(.2,.8,.2,1);pointer-events:none}
  #dCur.click::after{content:'';position:absolute;left:-18px;top:-18px;width:60px;height:60px;border-radius:50%;background:#FFC40088;animation:rp .5s ease-out forwards}
  @keyframes rp{from{transform:scale(.3);opacity:1}to{transform:scale(1.6);opacity:0}}
  #dPanel{position:fixed;inset:0;background:#0B1220;z-index:8500;display:none;align-items:center;justify-content:center;flex-direction:column;color:#fff;font-family:Poppins;opacity:0;transition:opacity .4s}
  .tag{position:fixed;right:28px;top:20px;background:#0B1220;color:#FFC400;font:600 22px Poppins;padding:6px 16px;border-radius:999px;z-index:7000}
  .waMsg{background:#e9f7ee;border-radius:26px;padding:44px 52px;max-width:1300px;color:#0B1220;font:500 50px/1.45 Poppins;box-shadow:0 20px 60px #0008}
  .waTop{font:700 34px Poppins;color:#1fa855;margin-bottom:26px}
  .waTo{font:500 32px Poppins;color:#b9c4d8;margin-bottom:22px}
  pre.pr{font:500 33px/1.5 'DejaVu Sans Mono',monospace;color:#e8edf7;white-space:pre-wrap;max-width:1560px}
  .prH{font:700 44px Poppins;color:#FFC400;margin-bottom:26px;align-self:flex-start;margin-left:180px}
  body{transition:transform .9s cubic-bezier(.3,.7,.2,1);transform-origin:0 0}
  #dCap.pop{animation:capPop .38s cubic-bezier(.2,1.3,.4,1)}
  @keyframes capPop{from{transform:translateX(-50%) translateY(26px) scale(.94);opacity:0}to{transform:translateX(-50%) translateY(0) scale(1);opacity:1}}
  #dBar{position:fixed;left:0;top:0;height:8px;width:0;background:#FFC400;z-index:9600}
  #dChap{position:fixed;left:28px;top:20px;background:#FFC400;color:#0B1220;font:700 24px Poppins;padding:7px 18px;border-radius:999px;z-index:9400;opacity:0;transform:translateX(-30px);transition:all .45s cubic-bezier(.2,.8,.2,1)}
  #dChap.on{opacity:1;transform:none}
  #dWipe{position:fixed;inset:0;background:#FFC400;z-index:9700;transform:translateX(-101%);pointer-events:none}
  #dWipe.go{animation:wipe .7s cubic-bezier(.7,0,.3,1)}
  @keyframes wipe{0%{transform:translateX(-101%)}45%,55%{transform:translateX(0)}100%{transform:translateX(101%)}}
  .aIn{opacity:0;animation:aIn .6s cubic-bezier(.2,.9,.3,1) forwards}
  @keyframes aIn{from{opacity:0;transform:translateY(46px)}to{opacity:1;transform:none}}
  .aPop{opacity:0;animation:aPop .55s cubic-bezier(.2,1.5,.4,1) forwards}
  @keyframes aPop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}
  .tKick{font:700 40px Poppins;color:#0B1220;background:#FFC400;padding:8px 26px;border-radius:999px;margin-bottom:38px}
  .tHead{font:700 104px/1.22 Poppins;text-align:center;max-width:1640px}
  .tHead .w{display:inline-block;white-space:pre}
  .tHead b{color:#FFC400}
  .tLine{height:8px;background:#FFC400;border-radius:4px;margin-top:40px;width:0;animation:tLine .8s .5s cubic-bezier(.3,.7,.2,1) forwards}
  @keyframes tLine{to{width:420px}}
  .sTitle{font:700 64px Poppins;color:#FFC400;margin-bottom:44px}
  .sItem{display:flex;align-items:center;gap:30px;font:600 56px Poppins;margin:15px 0;width:1300px;background:#152039;border-radius:22px;padding:22px 34px}
  .sItem i{flex:none;width:76px;height:76px;border-radius:50%;background:#FFC400;color:#0B1220;font:700 44px Poppins;display:flex;align-items:center;justify-content:center;font-style:normal}
  .sItem b{color:#FFC400}
  .nBig{font:700 230px/1 Poppins;color:#FFC400}
  .nLab{font:600 56px Poppins;margin-top:26px;text-align:center}
  .vsRow{display:flex;gap:50px;align-items:stretch}
  .vsCard{width:720px;border-radius:30px;padding:44px 48px;font:500 46px/1.5 Poppins}
  .vsCard h3{font:700 58px Poppins;margin:0 0 20px}
  .vsBad{background:#3a1620;border:5px solid #ff5a6e}.vsBad h3{color:#ff8a98}
  .vsGood{background:#12301f;border:5px solid #2fd47a}.vsGood h3{color:#5fe89d}`;
  document.head.appendChild(css);
  const mk = (id, html='') => { const d=document.createElement('div'); d.id=id; d.innerHTML=html; document.documentElement.appendChild(d); return d; };
  const cap = mk('dCap'), spot = mk('dSpot'), panel = mk('dPanel');
  const cur = mk('dCur', '<svg viewBox="0 0 24 24" width="44" height="44"><path d="M4 2l15 11-7 1.2L16 22l-3.2 1.4-3.8-7.6L4 20z" fill="#0B1220" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>');
  const bar = mk('dBar'), chap = mk('dChap'), wipe = mk('dWipe');
  const tag = document.createElement('div'); tag.className='tag'; tag.textContent='Sample data'; document.documentElement.appendChild(tag);
  window.D = {
    cap(h){ if(!h){cap.style.opacity=0;return} cap.innerHTML=h; cap.style.opacity=1 },
    spot(sel, pad=10){ const el = typeof sel==='string'?document.querySelector(sel):sel; if(!el){spot.style.opacity=0;return}
      const r=el.getBoundingClientRect(); Object.assign(spot.style,{left:(r.left-pad)+'px',top:(r.top-pad)+'px',width:(r.width+2*pad-12)+'px',height:(r.height+2*pad-12)+'px',opacity:1}) },
    unspot(){ spot.style.opacity=0 },
    row(name){ return [...document.querySelectorAll('.row')].find(r=>r.querySelector('.nm').textContent===name) },
    move(el){ const r=el.getBoundingClientRect(); cur.style.left=(r.left+r.width/2)+'px'; cur.style.top=(r.top+r.height/2)+'px' },
    click(){ cur.classList.remove('click'); void cur.offsetWidth; cur.classList.add('click') },
    panel(html){ panel.innerHTML=html; panel.style.display='flex'; requestAnimationFrame(()=>panel.style.opacity=1); cur.style.opacity=0; tag.style.opacity=0 },
    unpanel(){ panel.style.opacity=0; setTimeout(()=>panel.style.display='none',400); cur.style.opacity=1; tag.style.opacity=1 },
    // ---- animation helpers ----
    capPop(h){ D.cap(h); if(h){ cap.classList.remove('pop'); void cap.offsetWidth; cap.classList.add('pop') } },
    progress(sec){ bar.style.transition='none'; bar.style.width='0'; void bar.offsetWidth; bar.style.transition='width '+sec+'s linear'; bar.style.width='100%' },
    chapter(t){ if(!t){chap.classList.remove('on');return} chap.classList.remove('on'); setTimeout(()=>{chap.textContent=t; chap.classList.add('on')},200) },
    wipe(fn){ wipe.classList.remove('go'); void wipe.offsetWidth; wipe.classList.add('go'); if(fn) setTimeout(fn,330) },
    zoom(sel, scale=1.5){ const el = typeof sel==='string'?document.querySelector(sel):sel; const b=document.body; if(!el){b.style.transform='none';return}
      const tr=b.style.transition; b.style.transition='none'; const old=b.style.transform; b.style.transform='none'; const r=el.getBoundingClientRect(); b.style.transform=old; void b.offsetWidth; b.style.transition=tr;
      scale=Math.max(1,Math.min(scale,1780/r.width,820/r.height)); const cx=r.left+r.width/2, cy=r.top+r.height/2; b.style.transform=`translate(${960-cx*scale}px,${470-cy*scale}px) scale(${scale})` },
    unzoom(){ document.body.style.transform='none' },
    focus(sel, scale=1.5, pad=10){ D.unspot(); D.zoom(sel, scale); setTimeout(()=>D.spot(sel,pad), 950) },
    title(kicker, head){ const words=head.split(/(<b>.*?<\/b>|<br>|\s+)/).filter(x=>x&&x.trim()||x==='<br>'); let i=0;
      const h=words.map(w=>w==='<br>'?'<br>':`<span class="w aIn" style="animation-delay:${.25+.11*i++}s">${w} </span>`).join('');
      D.panel(`<div class="tKick aPop">${kicker}</div><div class="tHead">${h}</div><div class="tLine"></div>`) },
    steps(title, items, gap=0.9, start=0.5){ D.panel(`<div class="sTitle aIn">${title}</div>`+items.map((t,i)=>`<div class="sItem aIn" style="animation-delay:${start+gap*i}s"><i>${i+1}</i><span>${t}</span></div>`).join('')) },
    stat(to, label, pre='', suf='', dur=1400){ D.panel(`<div class="nBig aPop"><span id="dNum">${pre}0${suf}</span></div><div class="nLab aIn" style="animation-delay:.5s">${label}</div>`);
      const el=document.getElementById('dNum'), t0=performance.now(); const tick=(t)=>{ const k=Math.min(1,(performance.now()-t0)/dur), e=1-Math.pow(1-k,3); el.textContent=pre+Math.round(to*e).toLocaleString('en-IN')+suf; if(k<1) requestAnimationFrame(tick) }; requestAnimationFrame(tick) },
    versus(badT, badLines, goodT, goodLines){ const li=(a,d)=>a.map((x,i)=>`<div class="aIn" style="animation-delay:${d+.45*i}s">${x}</div>`).join('');
      D.panel(`<div class="vsRow"><div class="vsCard vsBad aIn"><h3>${badT}</h3>${li(badLines,.4)}</div><div class="vsCard vsGood aIn" style="animation-delay:${.6+.45*badLines.length}s"><h3>${goodT}</h3>${li(goodLines,1+.45*badLines.length)}</div></div>`) },
  };
})();
"""

# Virtual clock, installed before the page loads. Real-time screen recording on this machine captured only ~5-13
# frames/s and stretched time (visuals ended up seconds behind the narration), so the Stage now renders frame by frame:
# page time only moves when Stage advances it, and every frame is a screenshot -> exact 30 fps, exact sync.
VCLOCK = r"""
(() => {
  let now = 0, seq = 1; const timers = new Map(); let rafs = [];
  performance.now = () => now;
  window.setTimeout = (fn, ms=0, ...a) => { const id = seq++; timers.set(id, {t: now + Math.max(0, +ms||0), fn, a}); return id };
  window.setInterval = (fn, ms=0, ...a) => { const id = seq++; timers.set(id, {t: now + Math.max(1, +ms||0), fn, a, every: Math.max(1, +ms||0)}); return id };
  window.clearTimeout = window.clearInterval = (id) => { timers.delete(id) };
  window.requestAnimationFrame = (fn) => { const id = seq++; rafs.push([id, fn]); return id };
  window.cancelAnimationFrame = (id) => { rafs = rafs.filter(r => r[0] !== id) };
  window.__adv = (dt) => {
    const end = now + dt; let busy = 0;
    for (let guard = 0; guard < 500; guard++) {
      let pick = null, pid = 0;
      for (const [id, t] of timers) if (t.t <= end && (!pick || t.t < pick.t)) { pick = t; pid = id }
      if (!pick) break;
      now = Math.max(now, pick.t); busy++;
      if (pick.every) pick.t += pick.every; else timers.delete(pid);
      try { typeof pick.fn === 'function' && pick.fn(...pick.a) } catch (e) { console.error(e) }
    }
    now = end;
    const run = rafs; rafs = []; busy += run.length;
    for (const [, fn] of run) { try { fn(now) } catch (e) { console.error(e) } }
    for (const an of document.getAnimations()) {
      busy++;
      if (an.__vt === undefined) { an.pause(); an.__vt = 0 }
      an.__vt += dt;
      let endT = Infinity; try { endT = an.effect.getComputedTiming().endTime } catch (e) {}
      if (an.__vt >= endT) { try { an.finish() } catch (e) {} } else an.currentTime = an.__vt;
    }
    return busy;
  };
})();
"""

# Vertical overlay for Shorts. The page is laid out as a 540x960 phone (so the tool's own mobile layout is used)
# and rendered at 2x -> 1080x1920.
SHORT_DIRECTOR = r"""
(() => {
  const css = document.createElement('style');
  css.textContent = `
  html{background:#f4f6fb} body{padding:132px 10px 0 !important}
  #f,.top,.sub,.foot{display:none !important} h1{font-size:22px !important;margin-bottom:10px}
  #dTop{position:fixed;left:0;right:0;top:0;height:120px;background:#0B1220;z-index:9000;display:flex;align-items:center;justify-content:center;text-align:center;color:#fff;font:700 31px/1.22 Poppins;padding:0 18px}
  #dTop b{color:#FFC400} #dTop div.pop{animation:tPop .4s cubic-bezier(.2,1.3,.4,1)}
  @keyframes tPop{from{transform:translateY(18px) scale(.94);opacity:0}to{transform:none;opacity:1}}
  #dBar{position:fixed;left:0;top:120px;height:5px;width:0;background:#FFC400;z-index:9600}
  #dSpot{position:fixed;border:4px solid #FFC400;border-radius:14px;box-shadow:0 0 0 9999px rgba(11,18,32,.55);z-index:8000;transition:all .5s cubic-bezier(.2,.8,.2,1);opacity:0;pointer-events:none}
  #dPanel{position:fixed;inset:120px 0 0 0;background:#0B1220;z-index:8500;display:none;align-items:center;justify-content:center;flex-direction:column;color:#fff;font-family:Poppins;opacity:0;transition:opacity .35s;padding:0 28px;text-align:center}
  .waMsg{background:#e9f7ee;border-radius:16px;padding:24px 26px;color:#0B1220;font:500 27px/1.45 Poppins;text-align:left}
  .waTop{font:700 20px Poppins;color:#1fa855;margin-bottom:12px}
  .waTo{font:500 19px Poppins;color:#b9c4d8;margin-bottom:14px}
  .aIn{opacity:0;animation:aIn .6s cubic-bezier(.2,.9,.3,1) forwards}
  @keyframes aIn{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
  .aPop{opacity:0;animation:aPop .55s cubic-bezier(.2,1.5,.4,1) forwards}
  @keyframes aPop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}
  .tag{position:fixed;right:10px;top:132px;background:#0B1220;color:#FFC400;font:600 13px Poppins;padding:3px 10px;border-radius:999px;z-index:7000}`;
  document.head.appendChild(css);
  const mk = id => { const d=document.createElement('div'); d.id=id; document.documentElement.appendChild(d); return d };
  const top = mk('dTop'), spot = mk('dSpot'), panel = mk('dPanel'), bar = mk('dBar');
  const tag = document.createElement('div'); tag.className='tag'; tag.textContent='Sample data'; document.documentElement.appendChild(tag);
  window.D = {
    cap(h){ top.innerHTML = '<div class="pop">'+h+'</div>' },
    spot(sel, pad=6){ const el = typeof sel==='string'?document.querySelector(sel):sel; if(!el){spot.style.opacity=0;return}
      const r=el.getBoundingClientRect(); Object.assign(spot.style,{left:(r.left-pad)+'px',top:(r.top-pad)+'px',width:(r.width+2*pad-8)+'px',height:(r.height+2*pad-8)+'px',opacity:1}) },
    unspot(){ spot.style.opacity=0 },
    row(n){ return [...document.querySelectorAll('.row')].find(r=>r.querySelector('.nm').textContent===n) },
    move(){}, click(){},
    progress(sec){ bar.style.transition='none'; bar.style.width='0'; void bar.offsetWidth; bar.style.transition='width '+sec+'s linear'; bar.style.width='100%' },
    panel(h){ panel.innerHTML=h; panel.style.display='flex'; requestAnimationFrame(()=>panel.style.opacity=1); tag.style.opacity=0; spot.style.opacity=0 },
    unpanel(){ panel.style.opacity=0; setTimeout(()=>panel.style.display='none',350); tag.style.opacity=1 },
    end(logo, big, small){ D.panel(`<img class="aPop" src="${logo}" style="width:170px;height:170px;border-radius:50%;margin-bottom:30px"><div class="aIn" style="font:700 38px/1.25 Poppins;animation-delay:.3s">${big}</div><div class="aIn" style="font:500 22px Poppins;color:#b9c4d8;margin-top:18px;animation-delay:.6s">${small}</div>`) },
  };
})();
"""

class Stage:
    """with Stage(page_html, beats, total_seconds, out_mp4, init_js, durations=...) as s: ... s.until(s.at(i, .5))
    Frame-accurate: page time is virtual, each of the 30 frames per second is a screenshot (about 3x real time to render)."""
    FPS = 30
    def __init__(self, html_path, beats, total, out, init_js="", durations=None, zoom=1.14, maxw=1480, size=(1920, 1080), scale=1, director=None, tail=1.2):
        self.size, self.scale, self.director, self.tail = size, scale, director, tail   # Shorts: size=(540, 960), scale=2, director=SHORT_DIRECTOR
        self.zoom, self.maxw = zoom, maxw   # bigger zoom + smaller maxw = larger, more readable tool on screen
        self.html, self.T, self.out, self.init = html_path, total, out, init_js
        self.D = list(durations) if durations else beat_durations(beats, total)   # exact durations when the narration was made per beat
        if durations: self.T = sum(self.D)
        self.marks = [0.0]
        for d in self.D: self.marks.append(self.marks[-1] + d)
    def __enter__(self):
        self.pw = sync_playwright().start(); self.b = self.pw.chromium.launch()
        self.ctx = self.b.new_context(viewport={"width": self.size[0], "height": self.size[1]}, device_scale_factor=self.scale, accept_downloads=True)
        self.ctx.add_init_script(VCLOCK + "window.open=(u)=>{window.__opened=u;return null};" + self.init)
        self.pg = self.ctx.new_page(); self.cdp = self.ctx.new_cdp_session(self.pg)
        self.pg.goto("file://" + os.path.abspath(self.html))
        self.pg.evaluate(self.director or DIRECTOR.replace(".wrap{zoom:1.14;max-width:1480px !important}", ".wrap{zoom:%s;max-width:%spx !important}" % (self.zoom, self.maxw)))
        self.pg.evaluate("document.fonts.ready.then(()=>1)")
        for _ in range(20): self.pg.evaluate("__adv(35)")           # settle load-time timers and transitions
        self.enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-c:v", "png", "-r", str(self.FPS), "-i", "-",
                                     "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", "-an", self.out], stdin=subprocess.PIPE)
        self.shot = {"format": "png", "optimizeForSpeed": True}
        if self.scale != 1: self.shot["clip"] = {"x": 0, "y": 0, "width": self.size[0], "height": self.size[1], "scale": self.scale}
        self.n, self.shots, self.dirty, self.last = 0, 0, 3, None
        return self
    @property
    def now(self): return self.n / self.FPS
    def frame(self):
        busy = self.pg.evaluate("__adv(%r)" % (1000.0 / self.FPS))
        if busy or self.dirty > 0 or self.last is None:
            self.last = base64.b64decode(self.cdp.send("Page.captureScreenshot", self.shot)["data"]); self.shots += 1
            self.dirty = 2 if busy else self.dirty - 1
        self.enc.stdin.write(self.last); self.n += 1
    def hold(self, sec):
        for _ in range(max(1, round(sec * self.FPS))): self.frame()
    def at(self, i, frac): return self.marks[i] + self.D[i] * frac
    def until(self, sec):
        while self.now < sec: self.frame()
    def js(self, code, arg=None):
        self.dirty = 3
        return self.pg.evaluate(code, arg) if arg is not None else self.pg.evaluate(code)
    def move(self, loc): self.js("el=>D.move(el)", loc.element_handle()); self.hold(0.6)
    def click(self, loc):
        self.move(loc); self.js("D.click()"); loc.click(); self.dirty = 3; self.hold(0.25)
    def type(self, sel, text, delay=65):
        loc = self.pg.locator(sel); self.move(loc); loc.click()
        for ch in text: self.pg.keyboard.type(ch); self.dirty = 3; self.hold(delay / 1000)
    def end_card(self, big_html, small):
        self.js("a=>D.panel(`<img src='${a[0]}' style='width:300px;height:300px;border-radius:50%;margin-bottom:44px'><div style='font:700 84px Poppins'>${a[1]}</div><div style='font:500 44px Poppins;color:#b9c4d8;margin-top:22px'>${a[2]}</div>`)", [LOGO, big_html, small])
    def __exit__(self, *a):
        try:
            if a[0] is None: self.until(self.T + self.tail)
        finally:
            self.enc.stdin.close(); self.enc.wait(); self.ctx.close(); self.b.close(); self.pw.stop()
        print("stage: %d frames (%.1fs), %d screenshots" % (self.n, self.now, self.shots))
