import sys, os, json, urllib.parse
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from director import Stage
DUR=json.load(open(sys.argv[1])); T=sum(DUR); OUT=sys.argv[2]
BEATS=json.load(open(os.path.join(HERE,"beats.json"),encoding="utf-8"))
PROMPT=open(os.path.join(HERE,"prompt.txt"),encoding="utf-8").read()
import datetime as dt
t=dt.date.today(); d=lambda n:(t-dt.timedelta(days=n)).isoformat()
seed=[{"id":"s1","name":"Ramesh ji","phone":"9800000011","amt":"1200","type":"out","date":d(34),"sent":""},
 {"id":"s2","name":"Ramesh ji","phone":"9800000011","amt":"650","type":"out","date":d(21),"sent":""},
 {"id":"s3","name":"Pappu Tea Stall","phone":"9800000014","amt":"1400","type":"out","date":d(12),"sent":""},
 {"id":"s4","name":"Sunita ji","phone":"9800000012","amt":"640","type":"out","date":d(6),"sent":""},
 {"id":"s5","name":"Anil bhai","phone":"9800000013","amt":"300","type":"out","date":d(3),"sent":""}]
INIT="try{if(!localStorage.getItem('udhaar-khata-v1'))localStorage.setItem('udhaar-khata-v1',"+json.dumps(json.dumps(seed))+")}catch(e){}"
with Stage(os.path.join(HERE,"udhaar.html"),BEATS,T,OUT,INIT,durations=DUR) as s:
    pg,m,J=s.pg,s.marks,s.js
    print("beats",[round(x,1) for x in s.D])
    J("D.spot(D.row('Ramesh ji'),12); D.cap('<b>₹1,850 बाकी</b> — और आप भूल चुके हैं')"); s.until(m[1])
    J("D.unspot(); D.cap('AI का बनाया <b>फ्री उधार खाता</b> · लिंक डिस्क्रिप्शन में')"); s.until(m[2])
    caps=["<b>कुल</b> कितना बाकी","कितने <b>लोगों</b> पर","आज कितना <b>उधार दिया</b>","आज कितना <b>वापस आया</b>"]
    for k in range(4):
        J(f"D.spot(document.querySelectorAll('.st')[{k}],8); D.cap('{caps[k]}')"); s.until(s.at(2,.22+.195*(k+1)))
    J("D.spot('#f',10); D.cap('नया उधार = <b>बस एक लाइन</b>')")
    s.type("#name","Sunita ji"); s.until(s.at(3,.22)); s.type("#phone","9800000012",55); s.until(s.at(3,.38)); s.type("#amt","350"); s.until(s.at(3,.50))
    s.click(pg.locator("button.add")); J("D.spot(D.row('Sunita ji'),10); D.cap('वही ग्राहक → रकम <b>उसी खाते में जुड़ी</b>')"); s.until(m[4])
    J("D.spot('#list',10); D.cap('सबसे ज़्यादा बाकी <b>सबसे ऊपर</b>')"); s.until(s.at(4,.62))
    J("D.spot(D.row('Ramesh ji').querySelector('.sv'),8); D.cap('आख़िरी एंट्री <b>कितने दिन पहले</b>')"); s.until(m[5])
    J("D.unspot(); D.cap('अब <b>वसूली</b>')"); s.until(s.at(5,.12))
    s.click(pg.locator(".row",has_text="Ramesh ji").locator("[data-a=wa]"))
    text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>{D.panel(h); D.cap('आपको बस <b>भेजना</b> है')}","<div class='waTo'>WhatsApp · +91 98000 00011</div><div class='waMsg'><div class='waTop'>✔ मैसेज पहले से लिखा हुआ</div>"+text+"</div>"); s.until(m[6])
    J("D.unpanel(); D.unspot(); D.cap('पैसा आ गया? <b>पैसा आया</b> दबाइए')"); s.until(s.at(6,.10))
    s.click(pg.locator(".row",has_text="Anil bhai").locator("[data-a=pay]")); J("D.spot('#f',10)"); s.until(s.at(6,.30))
    s.type("#amt","300"); s.until(s.at(6,.48)); s.click(pg.locator("button.add"))
    J("D.spot(D.row('Anil bhai'),10); D.cap('पूरा चुकता → <b>हिसाब साफ़</b>')"); s.until(m[7])
    J("D.spot('.sub',10); D.cap('डेटा <b>सिर्फ़ आपके पास</b>, किसी सर्वर पर नहीं')"); s.until(s.at(7,.55))
    J("D.spot('#csv',10); D.cap('पूरी एंट्री <b>एक्सेल</b> के लिए डाउनलोड')")
    with pg.expect_download(): s.click(pg.locator("#csv"))
    s.until(m[8])
    J("p=>{D.unspot(); D.panel(\"<div class='prH'>प्रॉम्प्ट और टूल का लिंक डिस्क्रिप्शन में</div><pre class='pr'></pre>\"); document.querySelector('pre.pr').textContent=p; D.cap('')}",PROMPT); s.until(m[9])
    s.end_card("अगला टूल <b style=\"color:#FFC400\">किस काम पर?</b>","कमेंट में लिखिए · Dhandha AI"); s.until(m[10]+1.2)
print("wrote",OUT)
