from playwright.sync_api import sync_playwright
import os, urllib.parse, datetime as dt
R=[]; ok=lambda n,c: R.append((n,bool(c)))
t=dt.date.today(); MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def mo(n):   # month n months before the current one, as YYYY-MM
    y,m=t.year,t.month-n
    while m<1: m+=12; y-=1
    return "%04d-%02d"%(y,m)
nm=lambda n: MON[int(mo(n)[5:])-1]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1280,"height":820}); pg.add_init_script("window.open=(u)=>{window.__o=u}")
    pg.on("dialog", lambda d: d.accept())
    pg.goto("file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),"fees.html")))
    ok("empty state", "Abhi koi student nahi" in pg.inner_text("#list"))
    ok("join month defaults to this month", pg.input_value("#join")==mo(0))
    def add(n,ph,bt,fee,back):
        pg.fill("#name",n); pg.fill("#phone",ph); pg.fill("#batch",bt); pg.fill("#fee",str(fee)); pg.fill("#join",mo(back)); pg.click("button.add")
    add("Aarav","9800000031","Class 10",800,1); add("Diya","9800000032","Class 9",700,0); add("Rohan","9800000033","Class 12",1200,2)
    ok("sorted by amount due", pg.locator(".nm").all_inner_texts()==["Rohan","Aarav","Diya"])
    ok("chip lists months and amount", pg.locator(".row").nth(0).locator(".chip").inner_text()=="%s, %s, %s · ₹3,600 baaki"%(nm(2),nm(1),nm(0)))
    ok("counters", [pg.inner_text(x) for x in ("#sTot","#sDue","#sIn","#sAll")]==["₹5,900","3","₹0","3"])
    r=pg.locator(".row").nth(0); ok("pay button names the oldest month", r.locator("[data-a=pay]").inner_text()==nm(2)+" ki fees aayi")
    r.locator("[data-a=pay]").click()
    ok("oldest month paid first", pg.locator(".row").nth(0).locator(".chip").inner_text()=="%s, %s · ₹2,400 baaki"%(nm(1),nm(0)))
    ok("counters after payment", [pg.inner_text(x) for x in ("#sTot","#sIn")]==["₹4,700","₹1,200"])
    pg.locator(".row").nth(0).locator("[data-a=wa]").click(); u=urllib.parse.unquote(pg.evaluate("window.__o"))
    ok("whatsapp number+name+months+amount", u.startswith("https://wa.me/919800000033?text=") and "Rohan ki %s aur %s ki fees ₹2,400 baaki"%(nm(1),nm(0)) in u)
    ok("reminder mark", "Yaad dilaya" in pg.locator(".row").nth(0).inner_text())
    d=pg.locator(".row",has_text="Diya"); d.locator("[data-a=pay]").click(); d=pg.locator(".row",has_text="Diya")
    ok("fully paid: green chip, no whatsapp/pay button", d.locator(".chip").inner_text()==nm(0)+" tak jama" and d.locator("[data-a=wa]").count()==0 and d.locator("[data-a=pay]").count()==0)
    ok("due count drops", [pg.inner_text(x) for x in ("#sTot","#sDue","#sIn")]==["₹4,000","2","₹1,900"])
    d.locator("[data-a=undo]").click()
    ok("undo restores the due", [pg.inner_text(x) for x in ("#sTot","#sDue","#sIn")]==["₹4,700","3","₹1,200"])
    pg.reload(); ok("survives reload", pg.locator(".row").count()==3 and pg.inner_text("#sTot")=="₹4,700")
    with pg.expect_download() as dl: pg.click("#csv")
    ok("csv 1+3 rows", len(open(dl.value.path(),encoding="utf-8-sig").read().strip().splitlines())==4)
    pg.fill("#name","X"); pg.fill("#phone","12"); pg.fill("#batch","B"); pg.fill("#fee","5"); pg.click("button.add"); ok("bad phone rejected", pg.locator(".row").count()==3)
    pg.locator(".row",has_text="Diya").locator("[data-a=del]").click(); ok("remove student", pg.locator(".row").count()==2 and pg.inner_text("#sAll")=="2")
    pg.set_viewport_size({"width":540,"height":960}); ok("no sideways scroll on phone", pg.evaluate("document.documentElement.scrollWidth<=540"))
    b.close()
for n,c in R: print("PASS" if c else "FAIL",n)
print(sum(c for _,c in R),"/",len(R))
