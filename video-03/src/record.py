import sys, os, json, urllib.parse, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from director import Stage
DUR=json.load(open(sys.argv[1])); T=sum(DUR); OUT=sys.argv[2]
BEATS=json.load(open(os.path.join(HERE,"beats.json"),encoding="utf-8")); PROMPT=open(os.path.join(HERE,"prompt.txt"),encoding="utf-8").read()
t=dt.date.today(); d=lambda n:(t+dt.timedelta(days=n)).isoformat()
seed=[{"id":"o1","name":"Meena ji","phone":"9800000021","item":"Blouse","due":d(-2),"total":"600","adv":"200","st":1,"sent":""},
 {"id":"o2","name":"Kavita ji","phone":"9800000022","item":"Suit","due":d(0),"total":"1200","adv":"500","st":1,"sent":""},
 {"id":"o3","name":"Pooja ji","phone":"9800000023","item":"Kurta","due":d(2),"total":"450","adv":"450","st":0,"sent":""},
 {"id":"o4","name":"Sunita ji","phone":"9800000024","item":"Alteration","due":d(5),"total":"150","adv":"0","st":0,"sent":""}]
INIT="try{if(!localStorage.getItem('order-register-v1'))localStorage.setItem('order-register-v1',"+json.dumps(json.dumps(seed))+")}catch(e){}"
BIG=lambda a,b: "<div style='font:700 96px/1.25 Poppins;text-align:center'>"+a+"</div><div style='font:500 46px Poppins;color:#b9c4d8;margin-top:30px;text-align:center'>"+b+"</div>"
with Stage(os.path.join(HERE,"orders.html"),BEATS,T,OUT,INIT,durations=DUR,zoom=1.36,maxw=1350) as s:
    pg,m,J=s.pg,s.marks,s.js; row=lambda n: pg.locator(".row",has_text=n)
    J("D.spot(D.row('Meena ji'),12); D.cap('ब्लाउज़ <b>2 दिन लेट</b> — और किसी को पता नहीं था')"); s.until(m[1])
    J("D.unspot(); D.cap('AI का बनाया <b>फ्री ऑर्डर रजिस्टर</b> · लिंक डिस्क्रिप्शन में')"); s.until(m[2])
    J("h=>{D.panel(h); D.cap('')}",BIG("एक पर्ची खोई<br><b style='color:#FFC400'>= एक ग्राहक नाराज़</b>","त्योहार के समय पर्चियाँ बढ़ती जाती हैं")); s.until(m[3])
    J("D.unpanel()"); caps=["कितने ऑर्डर <b>लेट</b>","कितने <b>आज देने हैं</b>","कितने <b>तैयार पड़े हैं</b>","कितना पैसा <b>लेना बाकी</b>"]
    for k in range(4):
        J(f"D.spot(document.querySelectorAll('.st')[{k}],8); D.cap('{caps[k]}')"); s.until(s.at(3,.24+.19*(k+1)))
    J("D.spot('#f',10); D.cap('नया ऑर्डर = <b>एक लाइन</b>')")
    s.type("#name","Rekha ji"); s.until(s.at(4,.22)); s.type("#phone","9800000025",50); s.until(s.at(4,.36))
    s.move(pg.locator("#item")); pg.select_option("#item","Suit"); s.until(s.at(4,.48))
    s.move(pg.locator("#due")); pg.fill("#due",d(3)); s.until(s.at(4,.60)); s.type("#total","1200"); s.until(s.at(4,.72)); pg.fill("#adv",""); s.type("#adv","500"); s.until(s.at(4,.86))
    s.click(pg.locator("button.add")); J("D.spot(D.row('Rekha ji'),10)"); s.until(m[5])
    J("D.spot('#list',10); D.cap('जो पहले देना है <b>वो सबसे ऊपर</b>')"); s.until(s.at(5,.50))
    J("D.spot(D.row('Meena ji'),10); D.cap('लेट → <b>लाल</b>')"); s.until(s.at(5,.76))
    J("D.spot(D.row('Kavita ji'),10); D.cap('आज वाले → <b>नारंगी</b>')"); s.until(m[6])
    J("D.unspot(); D.cap('हर ऑर्डर के तीन हाल: <b>नया → सिलाई में → तैयार</b>')"); s.until(s.at(6,.34))
    s.click(row("Pooja ji").locator("[data-a=nx]")); J("D.spot(D.row('Pooja ji'),10); D.cap('एक बटन → <b>सिलाई में</b>')"); s.until(s.at(6,.64))
    s.click(row("Kavita ji").locator("[data-a=nx]")); J("D.spot(D.row('Kavita ji'),10); D.cap('एक बटन → <b>तैयार</b>')"); s.until(m[7])
    J("D.spot(D.row('Kavita ji').querySelector('.wa'),8); D.cap('तैयार होते ही <b>वॉट्सऐप का बटन</b>')"); s.until(s.at(7,.24))
    s.click(row("Kavita ji").locator("[data-a=wa]")); text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>{D.panel(h); D.cap('आपको बस <b>भेजना</b> है')}","<div class='waTo'>WhatsApp · +91 98000 00022</div><div class='waMsg'><div class='waTop'>✔ मैसेज पहले से लिखा हुआ</div>"+text+"</div>"); s.until(m[8])
    J("D.unpanel(); D.unspot(); D.cap('ग्राहक ले गया? <b>दे दिया</b> दबाइए')"); s.until(s.at(8,.28))
    s.click(row("Kavita ji").locator("[data-a=nx]")); J("D.spot('.stats',10); D.cap('गिनती <b>अपने आप</b> बदल गई')"); s.until(m[9])
    J("D.spot(document.querySelectorAll('.st')[1],8); D.cap('सुबह सबसे पहले: <b>आज कितने देने हैं</b>')"); s.until(m[10])
    J("h=>{D.unspot(); D.panel(h); D.cap('')}",BIG("टेलर · मोबाइल रिपेयर<br>प्रिंटिंग · केक की दुकान","<b style='color:#FFC400'>जहाँ ऑर्डर लेकर बाद में देना हो</b>")); s.until(m[11])
    J("D.unpanel(); D.spot('.sub',10); D.cap('डेटा <b>सिर्फ़ आपके पास</b>, किसी सर्वर पर नहीं')"); s.until(s.at(11,.55))
    J("D.spot('#csv',10); D.cap('पूरी लिस्ट <b>एक्सेल</b> के लिए डाउनलोड')")
    with pg.expect_download(): s.click(pg.locator("#csv"))
    s.until(m[12])
    J("p=>{D.unspot(); D.panel(\"<div class='prH'>प्रॉम्प्ट और टूल का लिंक डिस्क्रिप्शन में</div><pre class='pr'></pre>\"); document.querySelector('pre.pr').textContent=p; D.cap('')}",PROMPT); s.until(m[13])
    s.end_card("आप ऑर्डर का हिसाब <b style=\"color:#FFC400\">कैसे रखते हैं?</b>","कमेंट में लिखिए · Dhandha AI"); s.until(m[14]+1.2)
print("wrote",OUT,[round(x,1) for x in DUR])
