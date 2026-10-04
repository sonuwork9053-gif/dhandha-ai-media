"""Short for video 02 (1080x1920). Usage: python3 short.py dur-short.json out.mp4"""
import sys, os, json, urllib.parse, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from director import Stage, SHORT_DIRECTOR, LOGO
BEATS=json.load(open(os.path.join(HERE,"beats-short.json"),encoding="utf-8"))
DUR=json.load(open(sys.argv[1])); OUT=sys.argv[2]
t=dt.date.today(); d=lambda n:(t-dt.timedelta(days=n)).isoformat()
seed=[{"id":"s1","name":"Ramesh ji","phone":"9800000011","amt":"1200","type":"out","date":d(34),"sent":""},
 {"id":"s2","name":"Ramesh ji","phone":"9800000011","amt":"650","type":"out","date":d(21),"sent":""},
 {"id":"s3","name":"Pappu Tea Stall","phone":"9800000014","amt":"1400","type":"out","date":d(12),"sent":""},
 {"id":"s4","name":"Sunita ji","phone":"9800000012","amt":"640","type":"out","date":d(6),"sent":""}]   # three people, so every row fits on the phone screen
INIT="try{if(!localStorage.getItem('udhaar-khata-v1'))localStorage.setItem('udhaar-khata-v1',"+json.dumps(json.dumps(seed))+")}catch(e){}"
with Stage(os.path.join(HERE,"udhaar.html"),BEATS,sum(DUR),OUT,INIT,durations=DUR,size=(540,960),scale=2,director=SHORT_DIRECTOR,tail=0.8) as s:
    pg,m,J=s.pg,s.marks,s.js; row=lambda n: pg.locator(".row",has_text=n)
    J("D.progress(%f); D.cap('दुकान का कितना पैसा<br><b>उधार में फँसा?</b>'); D.spot(document.querySelectorAll('.st')[0],6)" % s.T); s.until(m[1])
    J("D.cap('<b>कुल कितना बाकी</b> — एक नज़र में'); D.spot('.stats',6)"); s.until(s.at(1,.55))
    J("D.cap('किस पर <b>सबसे ज़्यादा</b> — सबसे ऊपर'); D.spot(D.row('Ramesh ji'),6)"); s.until(m[2])
    J("D.cap('<b>WhatsApp याद दिलाओ</b> दबाइए'); D.spot(D.row('Ramesh ji').querySelector('[data-a=wa]'),5)"); s.until(s.at(2,.27))
    row("Ramesh ji").locator("[data-a=wa]").click(); text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>{D.cap('मैसेज <b>पहले से लिखा हुआ</b>'); D.panel(h)}","<div class='waTo'>WhatsApp · +91 98000 00011</div><div class='waMsg aIn'><div class='waTop'>✔ आपको बस भेजना है</div>"+text+"</div>"); s.until(m[3])
    J("l=>{D.cap('टूल <b>फ़्री</b> है'); D.end(l,'लिंक डिस्क्रिप्शन में<br><b style=\"color:#FFC400\">पूरा वीडियो चैनल पर</b>','Dhandha AI')}",LOGO)
print("wrote",OUT,[round(x,1) for x in DUR])
