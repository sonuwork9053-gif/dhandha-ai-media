"""Video 02 (kirana udhaar khata, "teen galtiyan" format). Usage: python3 record.py dur.json out.mp4   (PREVIEW=1 renders at 4 fps for a layout check)"""
import sys, os, json, urllib.parse, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","..","kit"))
from director import Stage
if os.environ.get("PREVIEW"): Stage.FPS=4
DUR=json.load(open(sys.argv[1])); T=sum(DUR); OUT=sys.argv[2]
BEATS=json.load(open(os.path.join(HERE,"beats.json"),encoding="utf-8")); PROMPT=open(os.path.join(HERE,"prompt.txt"),encoding="utf-8").read()
t=dt.date.today(); d=lambda n:(t-dt.timedelta(days=n)).isoformat()
seed=[{"id":"s1","name":"Ramesh ji","phone":"9800000011","amt":"1200","type":"out","date":d(34),"sent":""},
 {"id":"s2","name":"Ramesh ji","phone":"9800000011","amt":"650","type":"out","date":d(21),"sent":""},
 {"id":"s3","name":"Pappu Tea Stall","phone":"9800000014","amt":"1400","type":"out","date":d(12),"sent":""},
 {"id":"s4","name":"Sunita ji","phone":"9800000012","amt":"640","type":"out","date":d(6),"sent":""},
 {"id":"s5","name":"Anil bhai","phone":"9800000013","amt":"300","type":"out","date":d(3),"sent":""}]
INIT="try{if(!localStorage.getItem('udhaar-khata-v1'))localStorage.setItem('udhaar-khata-v1',"+json.dumps(json.dumps(seed))+")}catch(e){}"
def CARD(n, head, lines):   # story panel for one mistake: lines = [(delay_seconds, html)]
    h="<div class='tKick aPop'>गलती नंबर %s</div><div class='aIn' style='font:700 100px/1.2 Poppins;text-align:center;animation-delay:.35s'>%s</div>" % (n, head)
    return h+"".join("<div class='aIn' style='font:500 52px/1.35 Poppins;color:#b9c4d8;margin-top:34px;text-align:center;animation-delay:%ss'>%s</div>" % (dl, x) for dl, x in lines)
Y="<b style='color:#FFC400'>%s</b>"
with Stage(os.path.join(HERE,"udhaar.html"),BEATS,T,OUT,INIT,durations=DUR,zoom=1.66,maxw=1120) as s:
    pg,m,J=s.pg,s.marks,s.js; row=lambda n: pg.locator(".row",has_text=n)
    J("const c=document.createElement('style'); c.textContent='h1{padding-left:190px;font-size:26px !important}.sub{display:none}.stats,form{margin-bottom:10px !important}.st{padding:8px 16px !important}form{padding:10px 16px !important}.top{margin-bottom:6px !important}.row{padding:8px 16px !important;margin-bottom:6px !important}'; document.head.appendChild(c); const k=document.getElementById('dCur'); k.style.left='1850px'; k.style.top='1020px'")   # larger tool: no sub line, tighter rows, room for the chapter chip
    # 0 hook
    J("D.progress(%f); D.cap(''); D.title('किराना दुकान','कितना पैसा<br><b>उधार में फँसा?</b>')" % s.T); s.until(m[1])
    # 1 turn: three mistakes, then the tool
    J("D.steps('उधार की तीन गलतियाँ',['छोटा उधार <b>लिखा ही नहीं</b>','कुल जोड़ <b>कभी नहीं हुआ</b>','माँगने में <b>झिझक</b>'],.75,.4)"); s.until(s.at(1,.36))
    J("D.wipe(()=>D.unpanel())"); s.hold(.6); J("D.capPop('AI का बनाया <b>फ़्री उधार खाता</b> · लिंक डिस्क्रिप्शन में')"); s.until(m[2])
    # 2 mistake 1 (story panel)
    J("h=>{D.cap(''); D.wipe(()=>D.panel(h)); D.chapter('1 · लिखा ही नहीं')}",CARD("1","छोटा उधार "+Y%"लिखा ही नहीं",[(4.6,"“बाद में दे दूँगा”"),(7.6,"दुकान में भीड़ · डायरी गल्ले के नीचे"),(11.4,"शाम तक बात "+Y%"दिमाग़ से निकल गई")])); s.until(m[3])
    # 3 new udhaar = one line
    J("D.wipe(()=>D.unpanel())"); s.hold(.7); J("D.spot('#f',10); D.capPop('नया उधार = <b>बस एक लाइन</b>')"); s.until(s.at(3,.30))
    s.type("#name","Sunita ji"); s.until(s.at(3,.44)); s.type("#phone","9800000012",50); s.until(s.at(3,.58)); s.type("#amt","350"); s.until(s.at(3,.68))
    s.click(pg.locator("button.add")); J("D.spot(D.row('Sunita ji'),10); D.capPop('ग्राहक के <b>सामने ही</b> काम हो गया')"); s.until(m[4])
    # 4 same customer -> same account
    J("D.cap('वही ग्राहक → रकम <b>उसी खाते में जुड़ी</b>')"); s.until(s.at(4,.36))
    J("D.focus(D.row('Sunita ji').querySelector('.chip'),1.4,12); D.capPop('₹640 + ₹350 = <b>₹990 बाकी</b>')"); s.until(s.at(4,.80))
    J("D.unzoom(); D.unspot(); D.cap('अलग पन्ना <b>ढूँढना नहीं</b>')"); s.until(m[5])
    # 5 mistake 2 + count-up of the sample total
    J("h=>{D.cap(''); D.wipe(()=>D.panel(h)); D.chapter('2 · जोड़ नहीं हुआ')}",CARD("2","कुल जोड़ "+Y%"कभी नहीं होता",[(4.2,"डायरी के पन्ने भरे हैं…")])); s.until(s.at(5,.62))
    J("D.stat(4540,'इस खाते में कुल बाकी<br><span style=\"font:500 34px Poppins;color:#b9c4d8\">Sample data</span>','₹')"); s.until(m[6])
    # 6 four counters
    J("D.wipe(()=>D.unpanel())"); s.hold(.6)
    caps=["<b>कुल</b> कितना बाकी","कितने <b>लोगों</b> पर","आज कितना <b>उधार दिया</b>","आज कितना <b>वापस आया</b>"]
    J("D.spot('.stats',10); D.capPop('सबसे ऊपर <b>चार गिनती</b>')"); s.until(s.at(6,.22))
    for k in range(4):
        J(f"D.spot(document.querySelectorAll('.st')[{k}],8); D.cap('{caps[k]}')"); s.until(s.at(6,.22+.195*(k+1)))
    # 7 sorted list + days since last entry
    J("D.spot('#list',10); D.capPop('सबसे ज़्यादा बाकी <b>सबसे ऊपर</b>')"); s.until(s.at(7,.48))
    J("D.focus(D.row('Ramesh ji').querySelector('.sv'),1.2,10); D.capPop('आख़िरी एंट्री <b>कितने दिन पहले</b>')"); s.until(s.at(7,.82))
    J("D.unzoom(); D.unspot(); D.cap('पुराना उधार <b>तुरंत पकड़ में</b>')"); s.until(m[8])
    # 8 mistake 3
    J("h=>{D.cap(''); D.wipe(()=>D.panel(h)); D.chapter('3 · माँगने में झिझक')}",CARD("3","माँगने में "+Y%"झिझक",[(3.4,"रोज़ का ग्राहक है… मुँह पर कैसे कहें?"),(6.6,"इसलिए बात "+Y%"टलती जाती है")])); s.until(m[9])
    # 9 WhatsApp reminder
    J("D.wipe(()=>D.unpanel())"); s.hold(.6); J("D.spot(D.row('Ramesh ji').querySelector('.wa'),8); D.capPop('<b>WhatsApp याद दिलाओ</b> दबाइए')"); s.until(s.at(9,.17))
    s.click(row("Ramesh ji").locator("[data-a=wa]")); text=urllib.parse.unquote(J("window.__opened").split("text=")[1])
    J("h=>{D.unspot(); D.panel(h); D.capPop('आपको बस <b>भेजना</b> है')}","<div class='waTo aIn'>WhatsApp · +91 98000 00011</div><div class='waMsg aIn' style='animation-delay:.3s'><div class='waTop'>✔ मैसेज पहले से लिखा हुआ</div>"+text+"</div>"); s.until(s.at(9,.72))
    J("D.unpanel(); D.focus(D.row('Ramesh ji').querySelector('.sent'),1.2,10); D.capPop('याद <b>किस दिन दिलाया</b> — लिखा रहता है')"); s.until(m[10])
    # 10 payment received
    J("D.unzoom(); D.unspot(); D.chapter('पैसा वापस आया'); D.cap('पैसा आ गया? <b>पैसा आया</b> दबाइए')"); s.until(s.at(10,.14))
    s.click(row("Anil bhai").locator("[data-a=pay]")); J("D.spot('#f',10)"); s.until(s.at(10,.30))
    s.type("#amt","300"); s.until(s.at(10,.44)); s.click(pg.locator("button.add"))
    J("D.spot(document.querySelectorAll('.st')[0],8); D.capPop('बाकी रकम <b>अपने आप घटी</b>')"); s.until(s.at(10,.66))
    J("D.spot(D.row('Anil bhai'),10); D.capPop('पूरा चुकता → <b>हिसाब साफ़</b>')"); s.until(m[11])
    # 11 before / after
    J("""()=>{D.unspot(); D.cap(''); D.chapter('डायरी या खाता?');
      D.versus('डायरी',['लिखना <b>छूट जाता</b> है','जोड़ <b>नहीं होता</b>','माँगना <b>टलता</b> है'],'उधार खाता',['हर उधार <b>एक लाइन</b>','कुल <b>हमेशा सामने</b>','याद दिलाना <b>एक बटन</b>']);
      const dl=[1.7,3.9,5.3,7.4,8.4,10.4,12.2]; const c=document.querySelectorAll('.vsCard'), a=[...c[0].querySelectorAll('div'),c[1],...c[1].querySelectorAll('div')];
      c[0].style.animationDelay='.3s'; a.forEach((e,i)=>e.style.animationDelay=dl[i]+'s') }"""); s.until(m[12])
    # 12 data stays local, CSV, who else can use it
    J("D.chapter(''); D.unpanel(); D.spot('#list',10); D.capPop('डेटा <b>सिर्फ़ आपके पास</b>, किसी सर्वर पर नहीं')"); s.until(s.at(12,.27))
    J("D.spot('#csv',10); D.capPop('पूरी एंट्री <b>एक्सेल</b> के लिए डाउनलोड')")
    with pg.expect_download(): s.click(pg.locator("#csv"))
    s.until(s.at(12,.47))
    J("D.unspot(); D.cap(''); D.wipe(()=>D.steps('जहाँ भी उधार चलता है',['<b>किराना</b> दुकान','<b>दूध</b> वाले','<b>चाय</b> की दुकान','<b>प्रेस</b> वाले'],1.35,1.2))"); s.until(m[13])
    # 13 prompt
    J("p=>{D.panel(\"<div class='prH aIn'>प्रॉम्प्ट और टूल का लिंक डिस्क्रिप्शन में</div><pre class='pr aIn' style='animation-delay:.3s'></pre>\"); document.querySelector('pre.pr').textContent=p}",PROMPT); s.until(m[14])
    # 14 question
    s.end_card("उधार का हिसाब <b style=\"color:#FFC400\">कहाँ लिखते हैं?</b>","कमेंट में लिखिए · Dhandha AI"); s.until(m[15]+1.2)
print("wrote",OUT,[round(x,1) for x in DUR])
