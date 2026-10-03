import sys, os, time, json, datetime as dt, shutil, subprocess, glob, urllib.parse
from playwright.sync_api import sync_playwright

T = float(sys.argv[1])            # narration length in seconds
OUT = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = "file://" + os.path.join(HERE, "..", "..", "kit", "brand", "dhandha-ai-logo.png")

BEATS = [
 "आपके कस्टमर का फ़िल्टर दस दिन पहले बदलना था, और किसी ने फोन नहीं किया। क्यों? क्योंकि आपको पता ही नहीं था। और कस्टमर ऐसे ही हाथ से निकलते हैं।",
 "इस वीडियो में मैं एक फ्री टूल दिखा रहा हूँ जो AI ने बनाया है। ये हर सुबह बताता है कि आज किस कस्टमर को याद दिलाना है। और आख़िर में वो पूरा प्रॉम्प्ट मिलेगा जिससे आप अपना टूल खुद बनवा सकते हैं।",
 "ज़्यादातर छोटे बिज़नेस में फॉलो-अप डायरी में होता है, या याददाश्त के भरोसे। जब तक याद आता है, कस्टमर किसी और से काम करवा चुका होता है। यहाँ ऊपर चार गिनती हैं: कितने लेट हो चुके, कितने आज के हैं, कितने अगले सात दिन में आएँगे, और कुल कितने कस्टमर हैं।",
 "नया कस्टमर जोड़ना बस एक लाइन का काम है। नाम, मोबाइल नंबर, कौन सा काम, पिछली तारीख़, और कितने दिन बाद दोबारा याद दिलाना है। जोड़ो दबाते ही वो लिस्ट में अपनी जगह पर पहुँच जाता है।",
 "लिस्ट हमेशा ज़रूरत के हिसाब से लगती है। जो सबसे ज़्यादा लेट है वो सबसे ऊपर, लाल रंग में। आज वाले नारंगी में। जिनमें अभी समय है वो हरे में, नीचे।",
 "अब असली काम। व्हाट्सऐप भेजो दबाइए। कस्टमर के नाम और काम के साथ मैसेज पहले से लिखा हुआ खुलता है। आपको बस भेजना है। और टूल याद रखता है कि रिमाइंडर किस दिन गया था।",
 "सर्विस हो गई? काम हो गया दबाइए। अगली तारीख़ अपने आप आगे बढ़ जाती है, और कस्टमर लिस्ट में नीचे चला जाता है। नब्बे दिन बाद वो खुद ऊपर आ जाएगा।",
 "पूरा डेटा आपके अपने फोन या कंप्यूटर में रहता है, किसी सर्वर पर नहीं। और जब चाहें पूरी लिस्ट एक्सेल के लिए डाउनलोड कर सकते हैं।",
 "ये रहा वो प्रॉम्प्ट जो मैंने वादा किया था। इसे किसी भी AI चैट में पेस्ट कीजिए, अपने बिज़नेस का काम लिखिए, और आपका अपना फॉलो-अप टूल तैयार। पूरा प्रॉम्प्ट डिस्क्रिप्शन में है।",
 "अगला कौन सा काम AI से करवाना है? कमेंट में लिखिए, अगला वीडियो उसी पर बनेगा।",
]
w = [len(b.replace(" ", "")) + 12 for b in BEATS]      # +12 ≈ paragraph pause
D = [T * x / sum(w) for x in w]
print("beat durations:", [round(x, 1) for x in D])

PROMPT = """Mere chhote business ke liye ek single-file HTML tool banao,
naam "Follow-up Register".

• Form: customer ka naam, 10 ank ka mobile, kaam (dropdown),
  pichhli tareekh, kitne din baad follow-up.
• List: due date ke hisaab se sorted, sabse late upar.
  Har row pe chip: "X din late" (laal), "Aaj" (narangi),
  "X din baaki" (hara).
• Upar 4 ginti: late, aaj, agle 7 din, kul customer.
• Har row pe "WhatsApp bhejo" button: wa.me link, customer ke
  naam aur kaam ke saath pehle se likha message.
  Bhejne ki tareekh yaad rakho.
• "Kaam ho gaya" button: pichhli tareekh aaj kar do,
  agli due date apne aap badhe.
• Data sirf browser ke localStorage mein rahe. CSV download do.
• Koi server, login ya paid service nahi. Mobile pe bhi chale."""

t = dt.date.today()
seed = [
 {"id": "a1", "name": "Sharma ji", "phone": "9800000001", "svc": "Filter change", "last": (t - dt.timedelta(days=100)).isoformat(), "days": "90", "sent": ""},
 {"id": "a2", "name": "Gupta Store", "phone": "9800000002", "svc": "RO service", "last": (t - dt.timedelta(days=90)).isoformat(), "days": "90", "sent": ""},
 {"id": "a3", "name": "Verma ji", "phone": "9800000003", "svc": "AMC renewal", "last": (t - dt.timedelta(days=360)).isoformat(), "days": "365", "sent": ""},
 {"id": "a4", "name": "Khan sahab", "phone": "9800000004", "svc": "RO service", "last": (t - dt.timedelta(days=30)).isoformat(), "days": "90", "sent": ""},
]

INIT = "window.open=(u)=>{window.__opened=u;return null};try{if(!localStorage.getItem('followup-register-v1'))localStorage.setItem('followup-register-v1'," + json.dumps(json.dumps(seed)) + ")}catch(e){}"

DIRECTOR = r"""
(() => {
  const css = document.createElement('style');
  css.textContent = `
  html{background:#f4f6fb} body{padding:22px 0 0 !important}
  .wrap{zoom:1.14;max-width:1480px !important} .row{padding:11px 16px !important;margin-bottom:8px !important} .sub{margin-bottom:14px !important} .stats,form{margin-bottom:14px !important}
  #dCap{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:#0B1220;color:#fff;font:700 46px Poppins;padding:18px 40px;border-radius:18px;z-index:9000;white-space:nowrap;box-shadow:0 14px 40px #0006;transition:opacity .35s;opacity:0}
  #dCap b{color:#FFC400}
  #dSpot{position:fixed;border:6px solid #FFC400;border-radius:22px;box-shadow:0 0 0 9999px rgba(11,18,32,.55);z-index:8000;transition:all .55s cubic-bezier(.2,.8,.2,1);opacity:0;pointer-events:none}
  #dCur{position:fixed;left:1500px;top:900px;width:44px;height:44px;z-index:9500;transition:left .7s cubic-bezier(.2,.8,.2,1),top .7s cubic-bezier(.2,.8,.2,1);pointer-events:none}
  #dCur.click::after{content:'';position:absolute;left:-18px;top:-18px;width:60px;height:60px;border-radius:50%;background:#FFC40088;animation:rp .5s ease-out forwards}
  @keyframes rp{from{transform:scale(.3);opacity:1}to{transform:scale(1.6);opacity:0}}
  #dPanel{position:fixed;inset:0;background:#0B1220;z-index:8500;display:none;align-items:center;justify-content:center;flex-direction:column;color:#fff;font-family:Poppins;opacity:0;transition:opacity .4s}
  .tag{position:fixed;right:28px;top:20px;background:#0B1220;color:#FFC400;font:600 22px Poppins;padding:6px 16px;border-radius:999px;z-index:7000}
  .waMsg{background:#e9f7ee;border-radius:26px;padding:44px 52px;max-width:1300px;color:#0B1220;font:500 50px/1.45 Poppins;box-shadow:0 20px 60px #0008;position:relative}
  .waTop{font:700 34px Poppins;color:#1fa855;margin-bottom:26px;display:flex;align-items:center;gap:16px}
  .waTo{font:500 32px Poppins;color:#b9c4d8;margin-bottom:22px}
  pre.pr{font:500 33px/1.5 'DejaVu Sans Mono',monospace;color:#e8edf7;white-space:pre-wrap;max-width:1560px}
  .prH{font:700 44px Poppins;color:#FFC400;margin-bottom:26px;align-self:flex-start;margin-left:180px}
  `;
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

def run():
    vdir = os.path.join(HERE, "rec"); shutil.rmtree(vdir, ignore_errors=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1920, "height": 1080}, locale="en-IN", record_video_dir=vdir,
                            record_video_size={"width": 1920, "height": 1080}, accept_downloads=True)
        ctx.add_init_script(INIT)
        pg = ctx.new_page(); t_page = time.monotonic()
        pg.goto("file://" + os.path.join(HERE, "followup.html"))
        pg.evaluate(DIRECTOR); pg.wait_for_timeout(700)
        t0 = time.monotonic(); head = t0 - t_page
        marks = [0.0]
        for d in D: marks.append(marks[-1] + d)
        def until(sec):   # wait until absolute time on the narration clock
            rem = sec - (time.monotonic() - t0)
            if rem > 0: pg.wait_for_timeout(rem * 1000)
        def at(i, frac): return marks[i] + D[i] * frac
        def click(loc):
            pg.evaluate("el=>D.move(el)", loc.element_handle()); pg.wait_for_timeout(750)
            pg.evaluate("D.click()"); loc.click(); pg.wait_for_timeout(250)
        J = lambda s: pg.evaluate(s)

        # 1 hook
        J("D.spot(D.row('Sharma ji'),12); D.cap('फ़िल्टर <b>10 दिन लेट</b> — और किसी ने फोन नहीं किया')")
        until(marks[1])
        # 2 turn
        J("D.unspot(); D.cap('AI का बनाया <b>फ्री टूल</b> · आख़िर में पूरा प्रॉम्प्ट')")
        until(marks[2])
        # 3 problem + counters
        J("D.cap('डायरी और याददाश्त = <b>छूटे हुए कस्टमर</b>')")
        until(at(2, .48))
        caps = ["कितने <b>लेट</b> हो चुके", "कितने <b>आज</b> के हैं", "<b>अगले 7 दिन</b> में कितने", "<b>कुल</b> कितने कस्टमर"]
        for k in range(4):
            J(f"D.spot(document.querySelectorAll('.st')[{k}],8); D.cap('{caps[k]}')")
            until(at(2, .50 + .125 * (k + 1)))
        # 4 add customer
        J("D.spot('#f',10); D.cap('नया कस्टमर = <b>बस एक लाइन</b>')")
        step = D[3] * .62 / 5
        base = marks[3] + .6
        pg.evaluate("el=>D.move(el)", pg.locator("#name").element_handle()); pg.wait_for_timeout(600)
        pg.locator("#name").click(); pg.keyboard.type("Mehta ji", delay=70); until(base + step)
        pg.evaluate("el=>D.move(el)", pg.locator("#phone").element_handle()); pg.wait_for_timeout(500)
        pg.locator("#phone").click(); pg.keyboard.type("9800000005", delay=60); until(base + 2 * step)
        pg.evaluate("el=>D.move(el)", pg.locator("#svc").element_handle()); pg.wait_for_timeout(500)
        pg.select_option("#svc", "Filter change"); until(base + 3 * step)
        pg.evaluate("el=>D.move(el)", pg.locator("#last").element_handle()); pg.wait_for_timeout(500)
        pg.fill("#last", (t - dt.timedelta(days=83)).isoformat()); until(base + 4 * step)
        pg.evaluate("el=>D.move(el)", pg.locator("#days").element_handle()); pg.wait_for_timeout(500)
        until(at(3, .72))
        click(pg.locator("button.add"))
        J("D.spot(D.row('Mehta ji'),10); D.cap('<b>Mehta ji</b> अपनी जगह पर पहुँच गए')")
        until(marks[4])
        # 5 list
        J("D.spot('#list',10); D.cap('सबसे ज़रूरी <b>सबसे ऊपर</b>')"); until(at(4, .28))
        J("D.spot(D.row('Sharma ji'),10); D.cap('सबसे लेट → <b>लाल</b>')"); until(at(4, .58))
        J("D.spot(D.row('Gupta Store'),10); D.cap('आज वाले → <b>नारंगी</b>')"); until(at(4, .76))
        J("D.spot(D.row('Khan sahab'),10); D.cap('अभी समय है → <b>हरा</b>')"); until(marks[5])
        # 6 whatsapp
        J("D.unspot(); D.cap('अब <b>असली काम</b>')"); until(at(5, .10))
        click(pg.locator(".row", has_text="Sharma ji").locator("[data-a=wa]"))
        url = pg.evaluate("window.__opened"); text = urllib.parse.unquote(url.split("text=")[1])
        html = ("<div class='waTo'>WhatsApp · +91 98000 00001</div><div class='waMsg'><div class='waTop'>✔ मैसेज पहले से लिखा हुआ</div>" + text + "</div>")
        pg.evaluate("h=>{D.panel(h); D.cap('आपको बस <b>भेजना</b> है')}", html)
        until(at(5, .74))
        J("D.unpanel(); D.spot(D.row('Sharma ji'),10); D.cap('टूल को याद है: <b>रिमाइंडर कब गया</b>')")
        until(marks[6])
        # 7 kaam ho gaya
        J("D.unspot(); D.cap('सर्विस हो गई? <b>काम हो गया</b> दबाइए')"); until(at(6, .16))
        click(pg.locator(".row", has_text="Sharma ji").locator("[data-a=done]"))
        pg.wait_for_timeout(300)
        J("D.spot(D.row('Sharma ji'),10); D.cap('अगली तारीख़ <b>अपने आप</b> — 90 दिन बाकी')")
        until(marks[7])
        # 8 data
        J("D.spot('.sub',10); D.cap('डेटा <b>सिर्फ़ आपके पास</b>, किसी सर्वर पर नहीं')"); until(at(7, .52))
        J("D.spot('#csv',10); D.cap('पूरी लिस्ट <b>एक्सेल</b> के लिए डाउनलोड')")
        with pg.expect_download(): click(pg.locator("#csv"))
        until(marks[8])
        # 9 prompt
        pg.evaluate("p=>{D.unspot(); D.panel(\"<div class='prH'>यही प्रॉम्प्ट डिस्क्रिप्शन में है</div><pre class='pr'></pre>\"); document.querySelector('pre.pr').textContent=p; D.cap('')}", PROMPT)
        until(marks[9])
        # 10 close
        pg.evaluate("l=>{D.panel(`<img src='${l}' style='width:300px;height:300px;border-radius:50%;margin-bottom:44px'><div style='font:700 84px Poppins'>अगला काम <b style=\"color:#FFC400\">कौन सा?</b></div><div style='font:500 44px Poppins;color:#b9c4d8;margin-top:22px'>कमेंट में लिखिए · Dhandha AI</div>`)}", LOGO)
        until(marks[10] + 1.2)
        ctx.close(); b.close()
    webm = glob.glob(os.path.join(vdir, "*.webm"))[0]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{head:.3f}", "-i", webm, "-t", f"{T + 1.2:.3f}",
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", "-an", OUT], check=True)
    print("wrote", OUT, "head", round(head, 2))

run()
