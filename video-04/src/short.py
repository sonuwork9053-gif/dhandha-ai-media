"""Short for video 04 (1080x1920). Usage: python3 short.py dur-short.json out.mp4"""
import sys, os, json, urllib.parse
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from director import Stage, SHORT_DIRECTOR, LOGO
from record import seed
BEATS=json.load(open(os.path.join(HERE,"beats-short.json"),encoding="utf-8"))
DUR=json.load(open(sys.argv[1])); OUT=sys.argv[2]
INIT="try{if(!localStorage.getItem('fees-register-v1'))localStorage.setItem('fees-register-v1',"+json.dumps(json.dumps(seed()[:3]))+")}catch(e){}"   # three students, so every row fits on the phone screen
with Stage(os.path.join(HERE,"fees.html"),BEATS,sum(DUR),OUT,INIT,durations=DUR,size=(540,960),scale=2,director=SHORT_DIRECTOR,tail=0.8) as s:
    pg,m,J=s.pg,s.marks,s.js; row=lambda n: pg.locator(".row",has_text=n)
    J("const c=document.createElement('style'); c.textContent='.mini{display:none}.row{padding:10px 12px !important}'; document.head.appendChild(c)")
    J("D.progress(%f); D.cap('किस बच्चे की <b>फ़ीस बाकी?</b><br>कितने महीने की?'); D.spot(D.row('Rohan').querySelector('.chip'),6)" % s.T); s.until(m[1])
    J("D.cap('<b>कुल कितनी बाकी</b> — एक नज़र में'); D.spot('.st.tot',6)"); s.until(s.at(1,.62))
    J("D.cap('किस पर <b>सबसे ज़्यादा</b> — सबसे ऊपर'); D.spot(D.row('Rohan'),6)"); s.until(m[2])
    J("D.cap('<b>WhatsApp याद दिलाओ</b> दबाइए'); D.spot(D.row('Rohan').querySelector('[data-a=wa]'),5)"); s.until(s.at(2,.2))
    row("Rohan").locator("[data-a=wa]").click(); text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>{D.cap('मैसेज <b>पहले से लिखा हुआ</b>'); D.panel(h)}","<div class='waTo'>WhatsApp · पैरेंट · +91 98000 00033</div><div class='waMsg aIn'><div class='waTop'>✔ आपको बस भेजना है</div>"+text+"</div>"); s.until(m[3])
    J("l=>{D.cap('टूल <b>फ़्री</b> है'); D.end(l,'लिंक डिस्क्रिप्शन में<br><b style=\"color:#FFC400\">पूरा वीडियो चैनल पर</b>','Dhandha AI')}",LOGO)
print("wrote",OUT,[round(x,1) for x in DUR])
