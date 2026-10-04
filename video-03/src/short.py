"""Short for video 03 (1080x1920). Usage: python3 short.py dur-short.json out.mp4   (reference for all Shorts)"""
import sys, os, json, urllib.parse, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from director import Stage, SHORT_DIRECTOR, LOGO
BEATS=json.load(open(os.path.join(HERE,"beats-short.json"),encoding="utf-8"))
DUR=json.load(open(sys.argv[1])); OUT=sys.argv[2]
t=dt.date.today(); d=lambda n:(t+dt.timedelta(days=n)).isoformat()
seed=[{"id":"o1","name":"Meena ji","phone":"9800000021","item":"Blouse","due":d(-2),"total":"600","adv":"200","st":1,"sent":""},
 {"id":"o2","name":"Kavita ji","phone":"9800000022","item":"Suit","due":d(0),"total":"1200","adv":"500","st":1,"sent":""},
 {"id":"o3","name":"Pooja ji","phone":"9800000023","item":"Kurta","due":d(2),"total":"450","adv":"450","st":0,"sent":""}]
INIT="try{if(!localStorage.getItem('order-register-v1'))localStorage.setItem('order-register-v1',"+json.dumps(json.dumps(seed))+")}catch(e){}"
with Stage(os.path.join(HERE,"orders.html"),BEATS,sum(DUR),OUT,INIT,durations=DUR,size=(540,960),scale=2,director=SHORT_DIRECTOR,tail=0.8) as s:
    pg,m,J=s.pg,s.marks,s.js; row=lambda n: pg.locator(".row",has_text=n)
    J("D.progress(%f); D.cap('ब्लाउज़ <b>2 दिन लेट</b><br>और किसी को पता नहीं'); D.spot(D.row('Meena ji'),6)" % s.T); s.until(m[1])
    J("D.cap('कौन सा <b>लेट</b>, कौन सा <b>आज देना है</b>'); D.spot('.stats',6)"); s.until(m[2])
    J("D.cap('कपड़ा तैयार? <b>एक बटन</b>'); D.spot(D.row('Kavita ji').querySelector('[data-a=nx]'),5)"); s.until(s.at(2,.22))
    row("Kavita ji").locator("[data-a=nx]").click(); s.hold(.3)
    J("D.cap('वॉट्सऐप का <b>बटन आ गया</b>'); D.spot(D.row('Kavita ji').querySelector('[data-a=wa]'),5)"); s.until(s.at(2,.50))
    row("Kavita ji").locator("[data-a=wa]").click(); text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>{D.cap('मैसेज <b>पहले से लिखा हुआ</b>'); D.panel(h)}","<div class='waTo'>WhatsApp · +91 98000 00022</div><div class='waMsg aIn'><div class='waTop'>✔ आपको बस भेजना है</div>"+text+"</div>"); s.until(m[3])
    J("l=>{D.cap('टूल <b>फ़्री</b> है'); D.end(l,'लिंक डिस्क्रिप्शन में<br><b style=\"color:#FFC400\">पूरा वीडियो चैनल पर</b>','Dhandha AI')}",LOGO)
print("wrote",OUT,[round(x,1) for x in DUR])
