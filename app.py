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
# 2. DINAMIK DİK / DAR / GENİŞ ÜÇGEN VE İLETKİ SVG MOTORU
# =========================================================
def svg_iletki_aci_ciz(derece, etiket="Açı"):
    rad = math.radians(derece)
    x = int(140 + 85 * math.cos(rad))
    y = int(110 - 85 * math.sin(rad))
    return f'''
    <svg width="280" height="125" viewBox="0 0 280 125" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8fafc" rx="8" stroke="#e2e8f0"/>
      <path d="M 50 110 A 90 90 0 0 1 230 110 Z" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
      <line x1="50" y1="110" x2="230" y2="110" stroke="#334155" stroke-width="2"/>
      <line x1="140" y1="110" x2="225" y2="110" stroke="#94a3b8" stroke-width="3" stroke-dasharray="3"/>
      <line x1="140" y1="110" x2="{x}" y2="{y}" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>
      <circle cx="140" cy="110" r="4" fill="#1e40af"/>
      <text x="140" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">{etiket}: {derece}°</text>
    </svg>
    '''

def svg_dinamik_ucgen_ciz(a_aci, b_aci, c_aci, koseler=("A", "B", "C")):
    """
    Açı tiplerine (Dik, Geniş, Dar/İkizkenar/Eşkenar) göre dinamik koordinatlar üreterek SVG çizer.
    """
    max_aci = max(a_aci, b_aci, c_aci)
    
    # 1. Dik Üçgen
    if max_aci == 90:
        p_top = "50, 20"
        p_left = "50, 110"
        p_right = "220, 110"
        dik_sembol = '<path d="M 50 95 L 65 95 L 65 110" fill="none" stroke="#ef4444" stroke-width="2"/>'
    # 2. Geniş Açılı Üçgen
    elif max_aci > 90:
        p_top = "180, 25"
        p_left = "30, 110"
        p_right = "230, 110"
        dik_sembol = ""
    # 3. Dar Açılı / İkizkenar / Eşkenar Üçgen
    else:
        p_top = "130, 20"
        p_left = "40, 110"
        p_right = "220, 110"
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
# 3. ÜÇGENDE AÇILAR ÖZEL DİNAMİK MOTORU
# =========================================================
def ucgende_acilar_engine():
    kisi = random.choice(["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru"])
    koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
    
    kategori = random.choice(["verilmeyen_aci", "ikizkenar_ucgen", "eskenar_ucgen", "ucgen_cesitleri"])
    svg_gorsel = None

    # 1. ALT KATEGORİ: Verilmeyen Açıyı Bulma
    if kategori == "verilmeyen_aci":
        a = random.randint(30, 95)
        b = random.randint(20, 165 - a)
        c = 180 - (a + b)
        
        q = f"Şekildeki {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[0]}) = {a}° ve m({koseler[1]}) = {b}° olarak verilmiştir. {kisi}'nin bulması gereken m({koseler[2]}) verilmeyen açısı kaç derecedir?"
        ans = f"{c}°"
        celd = [f"{c + 10}°", f"{abs(c - 15)}°", f"{c + 20}°"]
        svg_gorsel = svg_dinamik_ucgen_ciz(a, b, 0, koseler)

    # 2. ALT KATEGORİ: İkizkenar Üçgen Açı Hesabı
    elif kategori == "ikizkenar_ucgen":
        senaryo = random.choice(["tepe_verildi", "taban_verildi"])
        if senaryo == "tepe_verildi":
            tepe = random.choice([40, 50, 70, 80, 90, 100])
            taban = (180 - tepe) // 2
            q = f"{koseler[0]}{koseler[1]}{koseler[2]} ikizkenar üçgeninde |{koseler[0]}{koseler[1]}| = |{koseler[0]}{koseler[2]}|'dir. Tepe açısı m({koseler[0]}) = {tepe}° olduğuna göre eşit olan taban açılarından m({koseler[1]}) kaç derecedir?"
            ans = f"{taban}°"
            celd = [f"{taban + 10}°", f"{taban - 10}°", f"{180 - tepe}°"]
            svg_gorsel = svg_dinamik_ucgen_ciz(tepe, taban, taban, koseler)
        else:
            taban = random.randint(35, 75)
            tepe = 180 - (2 * taban)
            q = f"Taban açılarından biri {taban}° olan şekildeki ikizkenar üçgenin tepe açısının (m({koseler[0]})) ölçüsü kaç derecedir?"
            ans = f"{tepe}°"
            celd = [f"{tepe + 15}°", f"{abs(tepe - 10)}°", f"{taban}°"]
            svg_gorsel = svg_dinamik_ucgen_ciz(tepe, taban, taban, koseler)

    # 3. ALT KATEGORİ: Eşkenar Üçgen Açı Özellikleri
    elif kategori == "eskenar_ucgen":
        q = f"Bütün kenar uzunlukları birbirine eşit olan bir {koseler[0]}{koseler[1]}{koseler[2]} eşkenar üçgeninin iç açılarından birinin ölçüsü kaç derecedir?"
        ans = "60°"
        celd = ["90°", "45°", "180°"]
        svg_gorsel = svg_dinamik_ucgen_ciz(60, 60, 60, koseler)

    # 4. ALT KATEGORİ: Açılarına Göre Üçgen Çeşitleri (Dar, Dik, Geniş)
    else:
        a = random.choice([30, 45, 50, 60, 110])
        if a == 90:
            b, c = 40, 50
            tur = "Dik Açılı Üçgen"
            celd = ["Dar Açılı Üçgen", "Geniş Açılı Üçgen", "Eşkenar Üçgen"]
        elif a > 90:
            b, c = 30, 180 - (a + 30)
            tur = "Geniş Açılı Üçgen"
            celd = ["Dar Açılı Üçgen", "Dik Açılı Üçgen", "Eşkenar Üçgen"]
        else:
            b, c = 50, 180 - (a + 50)
            tur = "Dar Açılı Üçgen"
            celd = ["Dik Açılı Üçgen", "Geniş Açılı Üçgen", "Doğru Açılı Üçgen"]

        q = f"Açı ölçüleri {a}°, {b}° ve {c}° olan şekildeki üçgen, açılarına göre nasıl bir üçgendir?"
        ans = tur
        svg_gorsel = svg_dinamik_ucgen_ciz(a, b, c, koseler)

    siklar = [ans] + celd
    random.shuffle(siklar)
    return {"soru": q, "siklar": siklar, "dogru": ans, "gorsel_svg": svg_gorsel}

# =========================================================
# 4. GENEL DİNAMİK ENGINE (DERSLER İÇİN)
# =========================================================
def genel_dinamik_engine(ders, unite):
    u_low = unite.lower()
    
    # Özel Ünite Kontrolü: Üçgende Açılar
    if "üçgen" in u_low or "açı" in u_low:
        res = ucgende_acilar_engine()
        res["ders"] = ders
        res["unite"] = unite
        return res

    isimler = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin", "Kaan", "Deniz", "Ömer"]
    
    # MATEMATİK DİĞER
    if ders == "Matematik":
        n1, n2 = random.randint(120, 950), random.randint(10, 80)
        ans = n1 + n2
        kisi = random.choice(isimler)
        q_text = f"{kisi} biriktirdiği {n1} TL paraya {n2} TL daha eklemiştir. Toplam kaç TL'si olmuştur?"
        siklar = [str(ans), str(ans+10), str(abs(ans-15)), str(ans+25)]
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": str(ans)}

    # FEN BİLİMLERİ
    elif ders == "Fen Bilimleri":
        kisi = random.choice(isimler)
        q_text = f"{kisi}, {unite} konusunda yaptığı deneyde ölçümler almıştır. Aşağıdaki ifadelerden hangisi doğru bir bilimsel çıkarımdır?"
        ans = f"{unite} prensiplerine uygundur"
        celd = ["Hatalı hipotezdir", "Gözlem eksiktir", "Sabit değişkendir"]
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": siklar, "dogru": ans}

    # İNGİLİZCE / DİĞER
    elif ders == "İngilizce":
        q = random.choice([
            ("Wie heißt du / What is your name?", "My name is...", ["I am 10 years old.", "I like pizza.", "Good morning."]),
            ("Where are you from?", "I am from Turkey.", ["Yes, I do.", "At 8 o'clock.", "Fine, thanks."])
        ])
        siklar = [q[1]] + q[2]
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q[0], "gorsel_svg": None, "siklar": siklar, "dogru": q[1]}

    else:
        kisi = random.choice(isimler)
        q_text = f"{kisi}, '{unite}' konusu ile ilgili hazırladığı panoda ana fikri vurgulamaktadır. Hangisi bu ünitenin temel kavramlarındandır?"
        ans = f"{unite} temel ilkesi"
        celd = ["Yanlış kavram A", "Hatalı bilgi B", "Çelişen yargı C"]
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": siklar, "dogru": ans}

# =========================================================
# 5. DERS BAZLI SIRALI SORU ÜRETİM MOTORU
# =========================================================
def kesin_benzersiz_soru_uret(secilen_uniteler, hedef_sayi):
    havuz = []
    hash_set = set()
    
    if not secilen_uniteler:
        return []

    # Ders bazlı gruplama yapıp sıralı oluştur
    ders_gruplari = {}
    for ders, unite in secilen_uniteler:
        ders_gruplari.setdefault(ders, []).append(unite)

    her_ders_icin_sayi = max(1, hedef_sayi // len(ders_gruplari))

    for ders, uniteler in ders_gruplari.items():
        uretilen_ders_sorusu = 0
        deneme = 0
        while uretilen_ders_sorusu < her_ders_icin_sayi and deneme < 300:
            deneme += 1
            secilen_u = random.choice(uniteler)
            s = genel_dinamik_engine(ders, secilen_u)
            
            fingerprint = hashlib.sha256((s["soru"] + s["dogru"] + "".join(s["siklar"])).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_set and len(s["siklar"]) == 4:
                hash_set.add(fingerprint)
                havuz.append(s)
                uretilen_ders_sorusu += 1

    return havuz

# =========================================================
# 6. STREAMLIT ARAYÜZ VE DERS GEÇİŞ AKIŞI
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
            with st.spinner("Sorular ders sırasına göre üretiliyor..."):
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
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Test üret butonuna basarak ders bazlı testinizi başlatabilirsiniz.")
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
    
    # DERS GEÇİŞİ KONTROLÜ
    onceki_q = st.session_state["soru_listesi"][idx - 1] if idx > 0 else None
    ders_degisti = onceki_q and onceki_q["ders"] != q["ders"]

    c_left, c_right = st.columns([3, 1])
    c_left.caption(f"📌 {q['ders']} - {q['unite']}")
    c_right.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")

    # EĞER DERS BİTTİ DİĞER DERSE GEÇİLDİYSE UYARI / ARA GEÇİŞ EKRANI
    if ders_degisti and not st.session_state.get(f"ders_gecildi_{idx}", False):
        st.info(f"🎉 **{onceki_q['ders']}** dersi soruları tamamlandı! Şimdiki Ders: **{q['ders']}**")
        if st.button(f"➡️ {q['ders']} Testine Başla", type="primary"):
            st.session_state[f"ders_gecildi_{idx}"] = True
            st.rerun()
    else:
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
