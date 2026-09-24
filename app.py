import streamlit as st
import random
import json
import time
import math
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Dinamik Soru Motoru", page_icon="🎓", layout="wide")

# =========================================================
# 1. SESSION STATE BAŞLATMA
# =========================================================
if "sorular_hazir" not in st.session_state:
    st.session_state["sorular_hazir"] = False
if "test_aktif" not in st.session_state:
    st.session_state["test_aktif"] = False
if "test_bitti" not in st.session_state:
    st.session_state["test_bitti"] = False
if "soru_listesi" not in st.session_state:
    st.session_state["soru_listesi"] = []
if "kullanici_cevaplari" not in st.session_state:
    st.session_state["kullanici_cevaplari"] = {}
if "mevcut_soru_index" not in st.session_state:
    st.session_state["mevcut_soru_index"] = 0
if "baslangic_zamani" not in st.session_state:
    st.session_state["baslangic_zamani"] = None
if "toplam_sure_sn" not in st.session_state:
    st.session_state["toplam_sure_sn"] = 0

# MEB MÜFREDATI
MEB_MUFREDAT = {
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve Doğal Sayılarla İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar, Çizimler ve Açı Ölçme",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri",
        "6. Ünite: Veri İşleme ve Uzunluk/Zaman Ölçme",
        "7. Ünite: Alan Ölçme ve Geometrik Cisimler"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay",
        "2. Ünite: Canlılar Dünyası",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim",
        "5. Ünite: Işığın Yayılması ve Tam Gölge",
        "6. Ünite: İnsan ve Çevre",
        "7. Ünite: Elektrik Devre Elemanları"
    ],
    "Türkçe": [
        "1. Tema: Sözcükte Anlam ve Mantık Muhakeme",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragraf Analizi ve Görsel Okuma",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları"
    ],
    "Sosyal Bilgiler": [
        "1. Ünite: Birey ve Toplum (Hak ve Sorumluluklar)",
        "2. Ünite: Kültür ve Miras",
        "3. Ünite: İnsanlar, Yerler ve Çevreler",
        "4. Ünite: Bilim, Teknoloji ve Toplum",
        "5. Ünite: Üretim, Dağıtım ve Tüketim"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket"
    ],
    "İngilizce": [
        "Unit 1: Hello!",
        "Unit 2: My Town",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine"
    ]
}

# =========================================================
# 2. DINAMIK SVG ÇİZİM MOTORU (Görsel Gerektiren Sorular İçin)
# =========================================================
def svg_dinamik_ucgen_ciz(a_aci, b_aci, c_aci, koseler=("A", "B", "C")):
    max_aci = max(a_aci, b_aci, c_aci)
    
    if max_aci == 90:
        p_top, p_left, p_right = "50, 20", "50, 110", "220, 110"
        dik_sembol = '<path d="M 50 95 L 65 95 L 65 110" fill="none" stroke="#ef4444" stroke-width="2"/>'
    elif max_aci > 90:
        p_top, p_left, p_right = "180, 25", "30, 110", "230, 110"
        dik_sembol = ""
    else:
        p_top, p_left, p_right = "130, 20", "40, 110", "220, 110"
        dik_sembol = ""

    a_lbl = "?" if a_aci == 0 else f"{a_aci}°"
    b_lbl = "?" if b_aci == 0 else f"{b_aci}°"
    c_lbl = "?" if c_aci == 0 else f"{c_aci}°"

    return f'''
    <svg width="280" height="135" viewBox="0 0 280 135" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="8" stroke="#cbd5e1"/>
      <polygon points="{p_top} {p_left} {p_right}" fill="#eff6ff" stroke="#2563eb" stroke-width="3"/>
      {dik_sembol}
      <text x="130" y="16" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">{koseler[0]} ({a_lbl})</text>
      <text x="25" y="125" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">{koseler[1]} ({b_lbl})</text>
      <text x="235" y="125" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">{koseler[2]} ({c_lbl})</text>
    </svg>
    '''

# =========================================================
# 3. GELİŞMİŞ ALT KATEGORİLİ DİNAMİK SORU MOTORU
# =========================================================
def tum_dersler_alt_kategori_engine(ders, unite):
    isimler = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin"]
    u_low = unite.lower()
    kisi = random.choice(isimler)
    
    # ---------------------------------------------------------
    # MATEMATİK
    # ---------------------------------------------------------
    if ders == "Matematik":
        if "üçgen" in u_low or "açı" in u_low:
            koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
            sub_cat = random.choice(["verilmeyen_aci", "ikizkenar", "eskenar", "aci_cesitleri"])
            
            if sub_cat == "verilmeyen_aci":
                a, b = random.randint(30, 90), random.randint(20, 70)
                c = 180 - (a + b)
                q = f"Şekildeki {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[0]}) = {a}° ve m({koseler[1]}) = {b}° olduğuna göre verilmeyen m({koseler[2]}) kaç derecedir?"
                ans, celd = f"{c}°", [f"{c+10}°", f"{abs(c-15)}°", f"{c+20}°"]
                svg = svg_dinamik_ucgen_ciz(a, b, 0, koseler)
            elif sub_cat == "ikizkenar":
                tepe = random.choice([40, 50, 70, 80, 100])
                taban = (180 - tepe) // 2
                q = f"{koseler[0]}{koseler[1]}{koseler[2]} ikizkenar üçgeninde tepe açısı m({koseler[0]}) = {tepe}°'dir. Taban açılarından m({koseler[1]}) kaç derecedir?"
                ans, celd = f"{taban}°", [f"{taban+10}°", f"{taban-10}°", f"{180-tepe}°"]
                svg = svg_dinamik_ucgen_ciz(tepe, taban, taban, koseler)
            elif sub_cat == "eskenar":
                q = f"Bütün kenar uzunlukları eşit olan bir {koseler[0]}{koseler[1]}{koseler[2]} eşkenar üçgeninin bir iç açısının ölçüsü kaç derecedir?"
                ans, celd = "60°", ["90°", "45°", "180°"]
                svg = svg_dinamik_ucgen_ciz(60, 60, 60, koseler)
            else:
                a = random.choice([30, 90, 110])
                tur = "Dik Açılı Üçgen" if a == 90 else ("Geniş Açılı Üçgen" if a > 90 else "Dar Açılı Üçgen")
                b = 30 if a > 90 else (40 if a == 90 else 50)
                c = 180 - (a + b)
                q = f"Açıları {a}°, {b}° ve {c}° olan üçgen açı türüne göre hangisidir?"
                ans = tur
                celd = list({"Dar Açılı Üçgen", "Dik Açılı Üçgen", "Geniş Açılı Üçgen"} - {tur}) + ["Doğru Açı"]
                svg = svg_dinamik_ucgen_ciz(a, b, c, koseler)
            return {"soru": q, "siklar": [ans]+celd, "dogru": ans, "gorsel_svg": svg}
            
        elif "doğal sayılar" in u_low:
            sub = random.choice(["basamak", "toplama", "yuvarlama"])
            if sub == "basamak":
                sayi = random.randint(10000, 999999)
                q = f"{sayi} sayısının binler basamağındaki rakamın basamak değeri kaçtır?"
                b_deger = (sayi // 1000) % 10 * 1000
                ans = str(b_deger)
                celd = [str(b_deger // 10), str(b_deger * 10), str((sayi // 1000) % 10)]
            elif sub == "toplama":
                n1, n2 = random.randint(1500, 8500), random.randint(1000, 5000)
                q = f"{kisi} {n1} TL parasına {n2} TL daha eklerse toplam kaç TL'si olur?"
                ans = str(n1 + n2)
                celd = [str(n1+n2+100), str(n1+n2-50), str(n1+n2+500)]
            else:
                sayi = random.randint(100, 999)
                ans = str(round(sayi, -1))
                q = f"{sayi} sayısı en yakın onluğa yuvarlandığında hangi sayı elde edilir?"
                celd = [str(int(ans)+10), str(int(ans)-10), str(sayi)]
            return {"soru": q, "siklar": [ans]+celd, "dogru": ans, "gorsel_svg": None}
            
        else: # Kesirler / Ondalık
            pay = random.randint(1, 5)
            payda = random.choice([10, 100])
            ans = str(pay / payda)
            q = f"{pay}/{payda} kesrinin ondalık gösterimi aşağıdakilerden hangisidir?"
            celd = [str(pay), str(payda/pay), "0.00" + str(pay)]
            return {"soru": q, "siklar": [ans]+celd, "dogru": ans, "gorsel_svg": None}

    # ---------------------------------------------------------
    # FEN BİLİMLERİ
    # ---------------------------------------------------------
    elif ders == "Fen Bilimleri":
        if "güneş" in u_low:
            sub = random.choice(["kat_oran", "sicaklik", "hareket"])
            if sub == "kat_oran":
                q = f"{kisi}'nin araştırmasına göre Güneş'in çapı Dünya'nın çapının yaklaşık kaç katıdır?"
                ans, celd = "109 katı", ["10 katı", "500 katı", "1000 katı"]
            elif sub == "sicaklik":
                q = f"Güneş'in yüzey sıcaklığı yaklaşık kaç °C'dir?"
                ans, celd = "6000 °C", ["15 milyon °C", "1000 °C", "100 °C"]
            else:
                q = f"Dünya'nın kendi ekseni etrafındaki dönüş süresi ve sonucu hangisidir?"
                ans, celd = "24 saat - Gece/Gündüz", ["365 gün - Mevsimler", "27 gün - Ay Evreleri", "12 saat - Yıl"]
        else:
            q = f"{kisi}, {unite} ile ilgili deneyinde hangi değişkeni bağımsız değişken olarak seçmelidir?"
            ans, celd = "Miktarı değiştirilen etken", ["Sabit tutulan etken", "Ölçülen sonuç", "Gözlemlenmeyen yapı"]
        return {"soru": q, "siklar": [ans]+celd, "dogru": ans, "gorsel_svg": None}

    # ---------------------------------------------------------
    # TÜRKÇE
    # ---------------------------------------------------------
    elif ders == "Türkçe":
        sub = random.choice(["eş_anlam", "zıt_anlam", "mecaz"])
        sözlük = [("Mektep", "Okul", "Öğrenci"), ("Muallim", "Öğretmen", "Sınıf"), ("Hediye", "Armağan", "Eşya")]
        secilen = random.choice(sözlük)
        if sub == "eş_anlam":
            q = f"'{secilen[0]}' sözcüğünün eş anlamlısı aşağıdakilerden hangisidir?"
            ans, celd = secilen[1], [secilen[2], "Kitap", "Kalem"]
        else:
            q = f"Cümlede koyu yazılmış kelime mecaz anlamda kullanılmıştır. {kisi} hangi cümleyi kurmuştur?"
            ans, celd = "Bana karşı çok soğuk davrandı.", ["Hava bugün çok soğuk.", "Çayını soğuk içti.", "Soğuk su hasta eder."]
        return {"soru": q, "siklar": [ans]+celd, "dogru": ans, "gorsel_svg": None}

    # ---------------------------------------------------------
    # SOSYAL BİLGİLER / DİN KÜLTÜRÜ / İNGİLİZCE
    # ---------------------------------------------------------
    elif ders == "Sosyal Bilgiler":
        q = f"{kisi}, {unite} konusunda hak ve sorumluluklarını öğrenmektedir. Hangisi bir sorumluluk örneğidir?"
        ans, celd = "Odasını temiz tutmak", ["Eğitim almak", "Sağlık hizmeti almak", "Oyun oynamak"]
        return {"soru": q, "siklar": [ans]+celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        q = f"{unite} konusunda öğretmenin sorduğu soruya {kisi} doğru cevap vermiştir. Doğru cevap hangisidir?"
        ans, celd = "Güzel ahlak ve nezaket", ["Bencillik", "Kibir", "İsraf"]
        return {"soru": q, "siklar": [ans]+celd, "dogru": ans, "gorsel_svg": None}

    else: # İngilizce
        q = random.choice([
            ("How old are you?", "I am 10 years old.", ["My name is Can.", "Fine, thanks.", "In the morning."]),
            ("Where are you from?", "I am from Turkey.", ["Yes, I am.", "At 8 o'clock.", "It is a pencil."])
        ])
        return {"soru": q[0], "siklar": [q[1]]+q[2], "dogru": q[1], "gorsel_svg": None}

# =========================================================
# 4. BENZERLİK ENGELLEYİCİ VE SIKI FİLTRELEME MOTORU
# =========================================================
def kesin_benzersiz_soru_uret(secilen_uniteler, hedef_sayi):
    havuz = []
    hash_set = set()
    
    if not secilen_uniteler:
        return []

    ders_gruplari = {}
    for ders, unite in secilen_uniteler:
        ders_gruplari.setdefault(ders, []).append(unite)

    her_ders_icin_sayi = max(1, hedef_sayi // len(ders_gruplari))

    for ders, uniteler in ders_gruplari.items():
        uretilen_ders_sorusu = 0
        deneme = 0
        while uretilen_ders_sorusu < her_ders_icin_sayi and deneme < 400:
            deneme += 1
            secilen_u = random.choice(uniteler)
            s = tum_dersler_alt_kategori_engine(ders, secilen_u)
            s["ders"] = ders
            s["unite"] = secilen_u
            
            # Soru Şıkları Karıştır
            random.shuffle(s["siklar"])

            # SHA-256 Sıkı Hash Kontrolü
            fingerprint = hashlib.sha256((s["soru"] + s["dogru"] + "".join(s["siklar"])).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_set and len(s["siklar"]) == 4:
                hash_set.add(fingerprint)
                havuz.append(s)
                uretilen_ders_sorusu += 1

    return havuz

# =========================================================
# 5. STREAMLIT ARAYÜZ
# =========================================================
st.title("🎓 MEB 5. Sınıf Dinamik Soru Bankası")

st.sidebar.header("⚙️ Müfredat ve Soru Ayarları")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=False):
        select_all = st.checkbox(f"Tüm {ders_adi} Üniteleri", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Test Üret", type="primary", use_container_width=True):
        if secilen_uniteler:
            with st.spinner("Sorular üretiliyor..."):
                sorular = kesin_benzersiz_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen en az 1 ünite seçin!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Üret", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.rerun()

# --- ARAYÜZ AKIŞI ---
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Soru Üretim Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Sol menüden **'Test Üret'** butonuna basınız.")
    else:
        st.warning("⚠️ Lütfen sol menüden ders ve ünite seçiniz.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular başarıyla üretildi!")
    st.markdown(f"**Toplam Soru Sayısı:** {len(st.session_state['soru_listesi'])}")
    
    if st.button("⏱️ Testi Başlat", type="primary"):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()

elif st.session_state["test_aktif"]:
    gecen_sure = int(time.time() - st.session_state["baslangic_zamani"])
    kalan_sure = st.session_state["toplam_sure_sn"] - gecen_sure

    if kalan_sure <= 0:
        st.warning("⏰ Süreniz doldu!")
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    c_left, c_right = st.columns([3, 1])
    c_left.caption(f"📌 {q['ders']} - {q['unite']}")
    c_right.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")

    st.markdown(f"### **Soru {idx + 1}:**\n{q['soru']}")

    # Görsel Varsa Çiz
    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=145)

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Şıkkınızı seçin:", q["siklar"], index=secim_index, key=f"radio_{idx}")
    if secim:
        st.session_state["kullanici_cevaplari"][idx] = secim

    st.divider()
    b1, b2 = st.columns(2)
    if idx > 0 and b1.button("⬅️ Önceki Soru"):
        st.session_state["mevcut_soru_index"] -= 1
        st.rerun()

    if idx + 1 < len(st.session_state["soru_listesi"]):
        if b2.button("Sonraki Soru ➡️", type="primary"):
            st.session_state["mevcut_soru_index"] += 1
            st.rerun()
    else:
        if b2.button("🏁 Testi Bitir", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Test Sonu Karnesi")
    
    toplam = len(st.session_state["soru_listesi"])
    dogru = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    
    st.metric("Doğru / Toplam", f"{dogru} / {toplam}")
    st.progress(dogru / toplam if toplam > 0 else 0)
    
    if st.button("🔄 Yeni Test Yap"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
