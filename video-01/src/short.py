import sys, os, time, json, datetime as dt, shutil, subprocess, glob, urllib.parse
from playwright.sync_api import sync_playwright
T=float(sys.argv[1]); OUT=sys.argv[2]
HERE=os.path.dirname(os.path.abspath(__file__))
LOGO="file://"+os.path.join(HERE,"..","..","kit","brand","dhandha-ai-logo.png")
BEATS=["आपका कस्टमर दस दिन से लेट है, और आपको पता भी नहीं।","ये फ्री टूल हर सुबह बताता है कि आज किसे याद दिलाना है।","एक बटन दबाइए, और व्हाट्सऐप मैसेज पहले से लिखा हुआ खुल जाता है। आपको बस भेजना है।","ये टूल AI ने बनाया है, और इसे बनवाने का पूरा प्रॉम्प्ट चैनल के वीडियो में है।"]
w=[len(b.replace(" ",""))+10 for b in BEATS]; D=[T*x/sum(w) for x in w]
t=dt.date.today()
seed=[{"id":"a1","name":"Sharma ji","phone":"9800000001","svc":"Filter change","last":(t-dt.timedelta(days=100)).isoformat(),"days":"90","sent":""},
 {"id":"a2","name":"Gupta Store","phone":"9800000002","svc":"RO service","last":(t-dt.timedelta(days=90)).isoformat(),"days":"90","sent":""},
 {"id":"a3","name":"Verma ji","phone":"9800000003","svc":"AMC renewal","last":(t-dt.timedelta(days=360)).isoformat(),"days":"365","sent":""},
 {"id":"a4","name":"Khan sahab","phone":"9800000004","svc":"RO service","last":(t-dt.timedelta(days=30)).isoformat(),"days":"90","sent":""}]
INIT="window.open=(u)=>{window.__opened=u;return null};try{localStorage.setItem('followup-register-v1',"+json.dumps(json.dumps(seed))+")}catch(e){}"
DIRECTOR=r"""
(()=>{const css=document.createElement('style');css.textContent=`
html{background:#f4f6fb} body{padding:250px 0 0 !important}
.wrap{zoom:1.9;max-width:540px !important} #f,.top,.sub{display:none !important} h1{font-size:26px !important;margin-bottom:12px}
.stats{grid-template-columns:1fr 1fr !important;gap:8px !important;margin-bottom:14px !important}
.row{grid-template-columns:1fr auto !important;gap:8px !important;padding:12px !important}
.row>div:nth-child(2){display:none} .acts{grid-column:1/-1} .done,.del{display:none}
.wa{width:100%}
#dTop{position:fixed;left:0;right:0;top:0;height:230px;background:#0B1220;z-index:9000;display:flex;align-items:center;justify-content:center;text-align:center;color:#fff;font:700 62px/1.2 Poppins;padding:0 40px}
#dTop b{color:#FFC400}
#dSpot{position:fixed;border:8px solid #FFC400;border-radius:26px;box-shadow:0 0 0 9999px rgba(11,18,32,.55);z-index:8000;transition:all .5s cubic-bezier(.2,.8,.2,1);opacity:0;pointer-events:none}
#dPanel{position:fixed;inset:230px 0 0 0;background:#0B1220;z-index:8500;display:none;align-items:center;justify-content:center;flex-direction:column;color:#fff;font-family:Poppins;opacity:0;transition:opacity .35s;padding:0 60px;text-align:center}
.waMsg{background:#e9f7ee;border-radius:30px;padding:50px 54px;color:#0B1220;font:500 56px/1.45 Poppins;text-align:left}
.waTop{font:700 40px Poppins;color:#1fa855;margin-bottom:26px}
.waTo{font:500 38px Poppins;color:#b9c4d8;margin-bottom:26px}
.tag{position:fixed;right:24px;top:246px;background:#0B1220;color:#FFC400;font:600 26px Poppins;padding:6px 18px;border-radius:999px;z-index:7000}`;
document.head.appendChild(css);
const mk=id=>{const d=document.createElement('div');d.id=id;document.documentElement.appendChild(d);return d};
const top=mk('dTop'),spot=mk('dSpot'),panel=mk('dPanel');const tag=document.createElement('div');tag.className='tag';tag.textContent='Sample data';document.documentElement.appendChild(tag);
window.D={cap(h){top.innerHTML='<div>'+h+'</div>'},
 spot(sel,pad=10){const el=typeof sel==='string'?document.querySelector(sel):sel;if(!el){spot.style.opacity=0;return}const r=el.getBoundingClientRect();Object.assign(spot.style,{left:(r.left-pad)+'px',top:(r.top-pad)+'px',width:(r.width+2*pad-16)+'px',height:(r.height+2*pad-16)+'px',opacity:1})},
 unspot(){spot.style.opacity=0},row(n){return [...document.querySelectorAll('.row')].find(r=>r.querySelector('.nm').textContent===n)},
 panel(h){panel.innerHTML=h;panel.style.display='flex';requestAnimationFrame(()=>panel.style.opacity=1);tag.style.opacity=0;spot.style.opacity=0}};
})();"""
vdir=os.path.join(HERE,"rec_s"); shutil.rmtree(vdir,ignore_errors=True)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":1080,"height":1920},record_video_dir=vdir,record_video_size={"width":1080,"height":1920})
    ctx.add_init_script(INIT); pg=ctx.new_page(); tp=time.monotonic()
    pg.goto("file://"+os.path.join(HERE,"followup.html")); pg.evaluate(DIRECTOR); pg.wait_for_timeout(600)
    t0=time.monotonic(); head=t0-tp; m=[0.0]
    for d in D: m.append(m[-1]+d)
    def until(s):
        r=s-(time.monotonic()-t0)
        if r>0: pg.wait_for_timeout(r*1000)
    J=pg.evaluate
    J("D.cap('कस्टमर <b>10 दिन लेट</b><br>और आपको पता भी नहीं'); D.spot(D.row('Sharma ji'),10)"); until(m[1])
    J("D.cap('आज <b>किसे याद दिलाना है?</b>'); D.spot('.stats',10)"); until(m[2])
    J("D.cap('एक बटन → <b>मैसेज तैयार</b>'); D.spot(D.row('Sharma ji').querySelector('.wa'),8)"); until(m[2]+D[2]*.30)
    pg.locator(".row",has_text="Sharma ji").locator("[data-a=wa]").click()
    text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>D.panel(h)","<div class='waTo'>WhatsApp · +91 98000 00001</div><div class='waMsg'><div class='waTop'>✔ मैसेज पहले से लिखा हुआ</div>"+text+"</div>"); until(m[3])
    J("l=>{D.cap('ये टूल <b>AI ने बनाया</b>');D.panel(`<img src='${l}' style='width:340px;height:340px;border-radius:50%;margin-bottom:60px'><div style='font:700 76px/1.25 Poppins'>पूरा प्रॉम्प्ट<br><b style=\"color:#FFC400\">चैनल के वीडियो में</b></div><div style='font:500 44px Poppins;color:#b9c4d8;margin-top:36px'>Dhandha AI</div>`)}",LOGO)
    until(m[4]+1.0); ctx.close(); b.close()
webm=glob.glob(os.path.join(vdir,"*.webm"))[0]
subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{head:.3f}","-i",webm,"-t",f"{T+1.0:.3f}","-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","medium","-crf","20","-movflags","+faststart","-an",OUT],check=True)
shutil.rmtree(vdir,ignore_errors=True); print("ok",[round(x,1) for x in D])
