"""Shared screen-recording stage for Dhandha AI long videos (1920x1080).
Usage: see video-02/src/record.py. Beats are timed with kit/timing.py."""
import os, time, shutil, subprocess, glob
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
  .prH{font:700 44px Poppins;color:#FFC400;margin-bottom:26px;align-self:flex-start;margin-left:180px}`;
  document.head.appendChild(css);
  const mk = (id, html='') => { const d=document.createElement('div'); d.id=id; d.innerHTML=html; document.documentElement.appendChild(d); return d; };
  const cap = mk('dCap'), spot = mk('dSpot'), panel = mk('dPanel');
  const cur = mk('dCur', '<svg viewBox="0 0 24 24" width="44" height="44"><path d="M4 2l15 11-7 1.2L16 22l-3.2 1.4-3.8-7.6L4 20z" fill="#0B1220" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>');
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
  };
})();
"""

class Stage:
    """with Stage(page_html, beats, total_seconds, out_mp4, init_js) as s: ... s.until(s.at(i, .5))"""
    def __init__(self, html_path, beats, total, out, init_js=""):
        self.html, self.T, self.out, self.init = html_path, total, out, init_js
        self.D = beat_durations(beats, total)
        self.marks = [0.0]
        for d in self.D: self.marks.append(self.marks[-1] + d)
    def __enter__(self):
        self.vdir = self.out + ".rec"; shutil.rmtree(self.vdir, ignore_errors=True)
        self.pw = sync_playwright().start(); self.b = self.pw.chromium.launch()
        self.ctx = self.b.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir=self.vdir,
                                      record_video_size={"width": 1920, "height": 1080}, accept_downloads=True)
        self.ctx.add_init_script("window.open=(u)=>{window.__opened=u;return null};" + self.init)
        self.pg = self.ctx.new_page(); tp = time.monotonic()
        self.pg.goto("file://" + os.path.abspath(self.html)); self.pg.evaluate(DIRECTOR); self.pg.wait_for_timeout(700)
        self.t0 = time.monotonic(); self.head = self.t0 - tp
        return self
    def at(self, i, frac): return self.marks[i] + self.D[i] * frac
    def until(self, sec):
        rem = sec - (time.monotonic() - self.t0)
        if rem > 0: self.pg.wait_for_timeout(rem * 1000)
    def js(self, code, arg=None): return self.pg.evaluate(code, arg) if arg is not None else self.pg.evaluate(code)
    def move(self, loc): self.pg.evaluate("el=>D.move(el)", loc.element_handle()); self.pg.wait_for_timeout(600)
    def click(self, loc):
        self.move(loc); self.pg.evaluate("D.click()"); loc.click(); self.pg.wait_for_timeout(250)
    def type(self, sel, text, delay=65):
        loc = self.pg.locator(sel); self.move(loc); loc.click(); self.pg.keyboard.type(text, delay=delay)
    def end_card(self, big_html, small):
        self.pg.evaluate("a=>D.panel(`<img src='${a[0]}' style='width:300px;height:300px;border-radius:50%;margin-bottom:44px'><div style='font:700 84px Poppins'>${a[1]}</div><div style='font:500 44px Poppins;color:#b9c4d8;margin-top:22px'>${a[2]}</div>`)", [LOGO, big_html, small])
    def __exit__(self, *a):
        self.ctx.close(); self.b.close(); self.pw.stop()
        webm = glob.glob(os.path.join(self.vdir, "*.webm"))[0]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{self.head:.3f}", "-i", webm, "-t", f"{self.T + 1.2:.3f}",
                        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", "-an", self.out], check=True)
        shutil.rmtree(self.vdir, ignore_errors=True)
