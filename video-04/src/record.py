"""Video 04 (coaching class fees register, "maan lijiye" story format). Usage: python3 record.py dur.json out.mp4   (PREVIEW=1 renders at 4 fps for a layout check)"""
import sys, os, json, urllib.parse, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from director import Stage
if os.environ.get("PREVIEW"): Stage.FPS=4
DUR=json.load(open(sys.argv[1])); T=sum(DUR); OUT=sys.argv[2]
BEATS=json.load(open(os.path.join(HERE,"beats.json"),encoding="utf-8")); PROMPT=open(os.path.join(HERE,"prompt.txt"),encoding="utf-8").read()
t=dt.date.today()
def mo(n):   # month n months before the current one, as YYYY-MM
    y,m=t.year,t.month-n
    while m<1: m+=12; y-=1
    return "%04d-%02d"%(y,m)
P=lambda *ks: [{"m":mo(k),"on":(t.isoformat() if k==0 else mo(k)+"-05")} for k in ks]
def seed():   # sample data: Rohan 2 months, Diya 2 months, Aarav 1 month due, Kabir fully paid -> Rs 4,700 due in total
    return [{"id":"s1","name":"Rohan","phone":"9800000033","batch":"Class 12","fee":"1200","join":mo(2),"paid":P(2),"sent":""},
            {"id":"s2","name":"Diya","phone":"9800000032","batch":"Class 9","fee":"700","join":mo(3),"paid":P(3,2),"sent":""},
            {"id":"s3","name":"Aarav","phone":"9800000031","batch":"Class 10","fee":"900","join":mo(2),"paid":P(2,1),"sent":""},
            {"id":"s4","name":"Kabir","phone":"9800000035","batch":"Class 10","fee":"800","join":mo(3),"paid":P(3,2,1,0),"sent":""}]
INIT="try{if(!localStorage.getItem('fees-register-v1'))localStorage.setItem('fees-register-v1',"+json.dumps(json.dumps(seed()))+")}catch(e){}"
Y="<b style='color:#FFC400'>%s</b>"
def STORY(kick, head, lines):   # story panel: lines = [(delay_seconds, html)]
    h="<div class='tKick aPop'>%s</div><div class='aIn' style='font:700 96px/1.2 Poppins;text-align:center;animation-delay:.35s'>%s</div>" % (kick, head)
    return h+"".join("<div class='aIn' style='font:500 52px/1.35 Poppins;color:#b9c4d8;margin-top:34px;text-align:center;animation-delay:%ss'>%s</div>" % (dl, x) for dl, x in lines)
TWEAK="h1{padding-left:190px;font-size:26px !important}.sub{display:none}.stats,form{margin-bottom:10px !important}.st{padding:8px 16px !important}form{padding:10px 16px !important}.top{margin-bottom:6px !important}.row{padding:6px 16px !important;margin-bottom:5px !important}"
if __name__=="__main__":
  with Stage(os.path.join(HERE,"fees.html"),BEATS,T,OUT,INIT,durations=DUR,zoom=1.5,maxw=1240) as s:
    pg,m,J=s.pg,s.marks,s.js; row=lambda n: pg.locator(".row",has_text=n)
    J("c=>{const e=document.createElement('style'); e.textContent=c; document.head.appendChild(e); const k=document.getElementById('dCur'); k.style.left='1850px'; k.style.top='1020px'}",TWEAK)
    # 0 hook
    J("D.progress(%f); D.cap(''); D.title('कोचिंग क्लास','किसकी फ़ीस<br><b>अभी तक बाकी?</b>')" % s.T); s.until(m[1])
    # 1 turn
    J("D.wipe(()=>D.unpanel())"); s.hold(.6); J("D.capPop('AI का बनाया <b>फ़्री फ़ीस रजिस्टर</b>')"); s.until(s.at(1,.26))
    J("D.spot('#list',10); D.capPop('किसकी <b>कितनी फ़ीस बाकी</b>')"); s.until(s.at(1,.46))
    J("D.spot(D.row('Rohan').querySelector('.wa'),8); D.capPop('याद दिलाना = <b>एक बटन</b>')"); s.until(s.at(1,.74))
    J("D.unspot(); D.capPop('टूल का लिंक और प्रॉम्प्ट <b>डिस्क्रिप्शन में</b>')"); s.until(m[2])
    # 2 story (not the tool)
    J("h=>{D.cap(''); D.wipe(()=>D.panel(h)); D.chapter('1 · मान लीजिए')}",STORY("मान लीजिए","घर पर कोचिंग · "+Y%"तीन बैच",[(6.2,"फ़ीस: कोई 1 तारीख़ को · कोई 15 को · कोई “अगले हफ़्ते”"),(12.6,"रजिस्टर के पीछे टिक लगते जाते हैं"),(16.2,"महीने के आख़िर में "+Y%"हिसाब उलझ जाता है")])); s.until(m[3])
    # 3 four counters
    J("D.wipe(()=>D.unpanel()); D.chapter('2 · चार गिनती')"); s.hold(.7); J("D.spot('.stats',10); D.capPop('सबसे ऊपर <b>चार गिनती</b>')"); s.until(s.at(3,.38))
    caps=["<b>कुल</b> कितनी फ़ीस बाकी","कितने <b>बच्चों</b> पर बाकी","इस महीने कितनी <b>जमा हुई</b>","कुल कितने <b>बच्चे</b>"]
    for k in range(4):
        J(f"D.spot(document.querySelectorAll('.st')[{k}],8); D.cap('{caps[k]}')"); s.until(s.at(3,.38+.155*(k+1)))
    # 4 count-up of the sample total, then where it lives in the tool
    J("D.unspot(); D.cap(''); D.stat(4700,'इस सैंपल कोचिंग में फ़ीस बाकी<br><span style=\"font:500 34px Poppins;color:#b9c4d8\">Sample data · 4 बच्चे</span>','₹')"); s.until(s.at(4,.50))
    J("D.unpanel()"); s.hold(.5); J("D.focus('.st.tot',1.5,10); D.capPop('डायरी में ये जोड़ <b>कहीं नहीं मिलता</b>')"); s.until(s.at(4,.80))
    J("D.capPop('यहाँ <b>हर वक़्त सामने</b>')"); s.until(m[5])
    # 5 the list
    J("D.unzoom(); D.unspot(); D.chapter('3 · लिस्ट'); D.cap('')"); s.hold(.9); J("D.spot('#list',10); D.capPop('सबसे ज़्यादा बाकी <b>सबसे ऊपर</b>')"); s.until(s.at(5,.38))
    J("D.focus(D.row('Rohan').querySelector('.chip'),1.4,12); D.capPop('कौन से <b>महीने</b> · कुल <b>कितनी</b>')"); s.until(s.at(5,.76))
    J("D.unzoom(); D.unspot()"); s.hold(.9); J("D.spot(D.row('Kabir'),10); D.capPop('पूरी जमा → <b>हरा निशान</b>')"); s.until(m[6])
    # 6 new student = one line
    J("D.chapter('4 · नया बच्चा'); D.spot('#f',10); D.capPop('नया बच्चा = <b>बस एक लाइन</b>')"); s.until(s.at(6,.22))
    s.type("#name","Isha"); s.until(s.at(6,.33)); s.type("#phone","9800000034",45); s.until(s.at(6,.46)); s.type("#batch","Class 9",55); s.until(s.at(6,.54)); s.type("#fee","700"); s.until(s.at(6,.63))
    s.click(pg.locator("button.add")); J("D.spot(D.row('Isha'),10); D.capPop('इस महीने की फ़ीस <b>अपने आप बाकी</b>')"); s.until(m[7])
    # 7 new month -> dues appear by themselves (not the tool)
    J("""()=>{D.unspot(); D.cap(''); D.wipe(()=>{D.steps('नया महीना शुरू होते ही',['हर बच्चे की फ़ीस <b>अपने आप बाकी</b>','नई लिस्ट <b>बनानी नहीं पड़ती</b>']);
      const a=document.querySelectorAll('.sItem'); document.querySelector('.sTitle').style.animationDelay='1.6s'; a[0].style.animationDelay='3.9s'; a[1].style.animationDelay='8.3s'})}"""); s.until(m[8])
    # 8 fees received
    J("D.wipe(()=>D.unpanel()); D.chapter('5 · फ़ीस आई')"); s.hold(.7); J("D.spot(D.row('Diya').querySelector('[data-a=pay]'),8); D.capPop('फ़ीस आ गई? <b>फ़ीस आई</b> दबाइए')"); s.until(s.at(8,.22))
    s.click(row("Diya").locator("[data-a=pay]")); J("D.spot(D.row('Diya').querySelector('.chip'),10); D.capPop('सबसे पुराना महीना <b>पहले जमा</b>')"); s.until(s.at(8,.50))
    J("D.spot('.st.tot',8); D.capPop('बाकी रकम <b>घट गई</b>')"); s.until(s.at(8,.62))
    J("D.spot('.st.in',8); D.capPop('इस महीने की जमा <b>बढ़ गई</b>')"); s.until(s.at(8,.76))
    J("D.spot(D.row('Diya').querySelector('[data-a=undo]'),8); D.capPop('गलती से दब गया? <b>वापस</b> ले लीजिए')"); s.until(m[9])
    # 9 WhatsApp reminder
    J("D.unspot(); D.chapter('6 · याद दिलाना'); D.capPop('अब <b>याद दिलाने</b> की बात')"); s.until(s.at(9,.09))
    J("D.focus(D.row('Rohan').querySelector('.chip'),1.4,12); D.capPop('रोहन: <b>दो महीने</b> की फ़ीस बाकी')"); s.until(s.at(9,.235))
    J("D.unzoom(); D.unspot()"); s.hold(.9); J("D.spot(D.row('Rohan').querySelector('.wa'),8); D.capPop('<b>WhatsApp याद दिलाओ</b> दबाइए')"); s.until(s.at(9,.33))
    s.click(row("Rohan").locator("[data-a=wa]")); text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>{D.unspot(); D.panel(h); D.capPop('नाम · महीने · रकम — <b>पहले से लिखा हुआ</b>')}","<div class='waTo aIn'>WhatsApp · पैरेंट · +91 98000 00033</div><div class='waMsg aIn' style='animation-delay:.3s'><div class='waTop'>✔ मैसेज पहले से लिखा हुआ</div>"+text+"</div>"); s.until(s.at(9,.70))
    J("D.capPop('आपको बस <b>भेजना</b> है')"); s.until(s.at(9,.79))
    J("D.unpanel(); D.focus(D.row('Rohan').querySelector('.sent'),1.3,10); D.capPop('याद <b>किस दिन दिलाया</b> — लिखा रहता है')"); s.until(m[10])
    # 10 before / after (not the tool)
    J("""()=>{D.unzoom(); D.unspot(); D.cap(''); D.chapter('फ़र्क क्या है?');
      D.versus('पुराना तरीका',['महीने <b>गिनने</b> पड़ते हैं','कुल जोड़ <b>नहीं होता</b>','मैसेज <b>खुद लिखो</b>'],'फ़ीस रजिस्टर',['बाकी महीने <b>सामने</b>','कुल <b>हमेशा जुड़ा</b>','मैसेज <b>एक बटन</b>']);
      const dl=[2.0,5.2,6.9,9.6,10.0,12.2,14.0]; const c=document.querySelectorAll('.vsCard'), a=[...c[0].querySelectorAll('div'),c[1],...c[1].querySelectorAll('div')];
      c[0].style.animationDelay='.3s'; a.forEach((e,i)=>e.style.animationDelay=dl[i]+'s') }"""); s.until(m[11])
    # 11 data stays local, CSV, who else can use it
    J("D.chapter(''); D.unpanel(); D.spot('#list',10); D.capPop('डेटा <b>सिर्फ़ आपके पास</b>, किसी सर्वर पर नहीं')"); s.until(s.at(11,.25))
    J("D.spot('#csv',10); D.capPop('पूरी लिस्ट <b>एक्सेल</b> के लिए डाउनलोड')")
    with pg.expect_download(): s.click(pg.locator("#csv"))
    s.until(s.at(11,.42))
    J("D.unspot(); D.cap(''); D.wipe(()=>D.steps('जहाँ भी हर महीने फ़ीस आती है',['<b>ट्यूशन</b>','<b>डांस</b> क्लास','<b>जिम</b>','<b>हॉस्टल</b>'],1.0,2.6))"); s.until(m[12])
    # 12 prompt
    J("p=>{D.panel(\"<div class='prH aIn'>प्रॉम्प्ट और टूल का लिंक डिस्क्रिप्शन में</div><pre class='pr aIn' style='animation-delay:.3s'></pre>\"); document.querySelector('pre.pr').textContent=p}",PROMPT); s.until(m[13])
    # 13 question
    s.end_card("फ़ीस का हिसाब <b style=\"color:#FFC400\">कैसे रखते हैं?</b>","कमेंट में लिखिए · Dhandha AI"); s.until(m[14]+1.2)
  print("wrote",OUT,[round(x,1) for x in DUR])
