import streamlit as st
import random
import time
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Soru & Bilgi Yarışması Motoru", page_icon="🎓", layout="wide")

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

# =========================================================
# MÜFREDAT VE DETAYLI ALT KATEGORİ YAPISI
# =========================================================
MEB_MUFREDAT = {
    "🏆 Bilgi Yarışması": [
        "1. Kategori: Ülke Başkentleri ve Coğrafya",
        "2. Kategori: Dünya ve Yöresel Mutfaklar",
        "3. Kategori: Güncel Konular ve Genel Kültür",
        "4. Kategori: Ülkeler, Bayraklar ve Kültürler"
    ],
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar ve Açı Ölçme",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri",
        "6. Ünite: Veri İşleme ve Ölçme"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay",
        "2. Ünite: Canlılar Dünyası",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim",
        "5. Ünite: Işığın Yayılması ve Tam Gölge"
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
        "4. Ünite: Bilim, Teknoloji ve Toplum"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket"
    ],
    "İngilizce": [
        "Unit 1: Hello! & Nationalities",
        "Unit 2: My Town & Directions",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine"
    ]
}

# =========================================================
# DINAMIK SVG ÇİZİM MOTORU (Görsel Sorular İçin)
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
# TRİLYONLARCA SORU ÜRETEN DİNAMİK SORU MOTORU
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz"]

def dinamik_soru_uretici(ders, unite):
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    
    # 🏆 1. BİLGİ YARIŞMASI
    if ders == "🏆 Bilgi Yarışması":
        if "başkent" in u_low or "coğrafya" in u_low:
            havuz = [
                ("Fransa", "Paris", ["Lyon", "Marsilya", "Nice"]),
                ("Almanya", "Berlin", ["Münih", "Frankfurt", "Hamburg"]),
                ("Japonya", "Tokyo", ["Kyoto", "Osaka", "Hiroşima"]),
                ("İtalya", "Roma", ["Milano", "Venedik", "Napoli"]),
                ("İspanya", "Madrid", ["Barselona", "Sevilla", "Valensiya"]),
                ("İngiltere", "Londra", ["Manchester", "Liverpool", "Birmingham"]),
                ("Kanada", "Ottawa", ["Toronto", "Vancouver", "Montreal"]),
                ("Brezilya", "Brasilia", ["Rio de Janeiro", "Sao Paulo", "Salvador"]),
                ("Güney Kore", "Seul", ["Busan", "Incheon", "Daegu"]),
                ("Mısır", "Kahire", ["İskenderiye", "Lüksor", "Gize"])
            ]
            secilen = random.choice(havuz)
            if random.choice([True, False]):
                q = f"<b>{secilen[0]}</b> ülkesinin başkenti aşağıdakilerden hangisidir?"
                ans, celd = secilen[1], secilen[2]
            else:
                q = f"Başkenti <b>{secilen[1]}</b> olan ülke aşağıdakilerden hangisidir?"
                ans, celd = secilen[0], random.sample(["Hollanda", "Belçika", "İsveç", "Norveç", "Portekiz", "Yunanistan"], 3)
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "mutfak" in u_low:
            havuz = [
                ("Çiğ Köfte ve Baklava", "Gaziantep", ["Kayseri", "Adana", "Trabzon"]),
                ("Cağ Kebabı", "Erzurum", ["Kars", "Erzincan", "Ağrı"]),
                ("Mantı ve Yağlama", "Kayseri", ["Konya", "Sivas", "Yozgat"]),
                ("Tantuni", "Mersin", ["Adana", "Hatay", "Antalya"]),
                ("Künefe", "Hatay", ["Gaziantep", "Şanlıurfa", "Mardin"]),
                ("Pizza ve Pasta", "İtalya", ["Fransa", "İspanya", "Yunanistan"]),
                ("Sushi ve Ramen", "Japonya", ["Çin", "Güney Kore", "Tayland"]),
                ("Taco ve Burrito", "Meksika", ["Brezilya", "Arjantin", "Şili"])
            ]
            secilen = random.choice(havuz)
            q = f"<b>{secilen[0]}</b> lezzeti ile tescillenmiş şehir/ülke aşağıdakilerden hangisidir?"
            return {"soru": q, "siklar": [secilen[1]] + secilen[2], "dogru": secilen[1], "gorsel_svg": None}

        elif "güncel" in u_low:
            havuz = [
                ("Dünyanın en uzun nehri hangisidir?", "Nil Nehri", ["Amazon Nehri", "Tuna Nehri", "Fırat Nehri"]),
                ("Güneş sistemindeki en büyük gezegen hangisidir?", "Jüpiter", ["Satürn", "Mars", "Neptün"]),
                ("İstiklal Marşı'mızın şairi kimdir?", "Mehmet Âkif Ersoy", ["Ziya Gökalp", "Yahya Kemal", "Namık Kemal"]),
                ("Dünyanın en büyük okyanusu hangisidir?", "Büyük Okyanus (Pasifik)", ["Atlas Okyanusu", "Hint Okyanusu", "Arktik Okyanusu"])
            ]
            sec = random.choice(havuz)
            return {"soru": sec[0], "siklar": [sec[1]] + sec[2], "dogru": sec[1], "gorsel_svg": None}

        else:
            havuz = [
                ("Para birimi 'Yen' olan ülke hangisidir?", "Japonya", ["Çin", "Hindistan", "Tayland"]),
                ("Para birimi 'Euro' kullanan Avrupa ülkesi hangisidir?", "Almanya", ["İngiltere", "ABD", "Kanada"]),
                ("Kanguru ve Koala hayvanlarının ana vatanı neresidir?", "Avustralya", ["Afrika", "Güney Amerika", "Asya"])
            ]
            sec = random.choice(havuz)
            return {"soru": sec[0], "siklar": [sec[1]] + sec[2], "dogru": sec[1], "gorsel_svg": None}

    # 📐 2. MATEMATİK
    elif ders == "Matematik":
        if "üçgen" in u_low or "açı" in u_low:
            koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
            a, b = random.randint(30, 85), random.randint(25, 65)
            c = 180 - (a + b)
            q = f"Şekildeki {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[0]}) = {a}° ve m({koseler[1]}) = {b}° olduğuna göre verilmeyen m({koseler[2]}) kaç derecedir?"
            ans = f"{c}°"
            celd = [f"{c+10}°", f"{abs(c-15)}°", f"{c+20}°"]
            svg = svg_dinamik_ucgen_ciz(a, b, 0, koseler)
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": svg}
            
        elif "doğal sayılar" in u_low:
            sub = random.choice(["toplama", "basamak", "yuvarlama"])
            if sub == "toplama":
                n1, n2 = random.randint(1200, 9900), random.randint(1100, 8800)
                q = f"{kisi} biriktirdiği {n1} TL paraya {n2} TL daha eklerse toplam kaç TL'si olur?"
                ans = str(n1 + n2)
                celd = [str(n1 + n2 + 100), str(n1 + n2 - 50), str(n1 + n2 + 500)]
            elif sub == "basamak":
                sayi = random.randint(10000, 999999)
                b_deg = ((sayi // 1000) % 10) * 1000
                q = f"{sayi} sayısındaki binler basamağının basamak değeri kaçtır?"
                ans = str(b_deg)
                celd = [str(b_deg * 10), str(b_deg // 10), str((sayi // 1000) % 10)]
            else:
                sayi = random.randint(105, 995)
                ans = str(round(sayi, -1))
                q = f"{sayi} sayısı en yakın onluğa yuvarlandığında hangi sayı elde edilir?"
                celd = [str(int(ans) + 10), str(int(ans) - 10), str(sayi)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        else: # Kesir / Ondalık
            p1, p2 = random.randint(1, 9), random.choice([10, 100])
            ans = str(round(p1 / p2, 2))
            q = f"{p1}/{p2} kesrinin ondalık gösterimi aşağıdakilerden hangisidir?"
            celd = [str(p1), str(round(p2 / p1, 2)), f"0.0{p1}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # 🔬 3. FEN BİLİMLERİ
    elif ders == "Fen Bilimleri":
        if "güneş" in u_low:
            sub = random.choice(["cap", "sicaklik", "dönme"])
            if sub == "cap":
                q = f"{kisi}'nin fen laboratuvarında öğrendiğine göre Güneş'in çapı Dünya'nın çapının yaklaşık kaç katıdır?"
                ans, celd = "109 katı", ["10 katı", "500 katı", "1000 katı"]
            elif sub == "sicaklik":
                q = f"Güneş'in yüzey sıcaklığı yaklaşık kaç °C olarak bilinmektedir?"
                ans, celd = "6000 °C", ["15 milyon °C", "1000 °C", "100 °C"]
            else:
                q = f"Dünya'nın kendi ekseni etrafında dönme süresi ne kadardır?"
                ans, celd = "24 Saat", ["365 Gün", "27 Gün", "12 Saat"]
        else:
            q = f"{kisi}, {unite} ile ilgili yaptığı deneyde araştırma sonucunu etkileyen tek değişkeni incelemektedir. Bu değişkene ne ad verilir?"
            ans, celd = "Bağımsız Değişken", ["Bağımlı Değişken", "Sabit Değişken", "Kontrol Değişkeni"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # 📚 4. TÜRKÇE
    elif ders == "Türkçe":
        sub = random.choice(["es_anlam", "mecaz", "yazım"])
        if sub == "es_anlam":
            kelimeler = [("Mektep", "Okul"), ("Muallim", "Öğretmen"), ("Hediye", "Armağan"), ("Cevap", "Yanıt")]
            k = random.choice(kelimeler)
            q = f"'{k[0]}' sözcüğünün eş anlamlısı aşağıdakilerden hangisidir?"
            ans, celd = k[1], ["Sınıf", "Öğrenci", "Kitap"]
        elif sub == "mecaz":
            q = f"Aşağıdaki cümlelerin hangisinde {kisi} koyu renkli sözcüğü <b>mecaz anlamda</b> kullanmıştır?"
            ans, celd = "Bana karşı çok <b>soğuk</b> davrandı.", ["Hava bugün çok <b>soğuk</b>.", "Çayını <b>soğuk</b> içti.", "Buzdolabı çok <b>soğuk</b>."]
        else:
            q = f"Aşağıdaki cümlelerin hangisinde bir yazım hatası yapılmıştır?"
            ans, celd = "15 haziran günü geleceğim.", ["15 Haziran günü geleceğim.", "Ankara'ya gitti.", "Her şey yolunda."]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # 🌍 5. SOSYAL / DİN / İNGİLİZCE
    elif ders == "Sosyal Bilgiler":
        q = f"{kisi}, {unite} kapsamında evdeki sorumluluklarını sıralamaktadır. Hangisi bir sorumluluk örneğidir?"
        ans, celd = "Odasını düzenli tutmak", ["Eğitim hakkından yararlanmak", "Oyun oynamak", "Dengeli beslenmek"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        q = f"{unite} konusunda öğretmenin sorduğu soruya {kisi} doğru cevap vermiştir. Doğru olan tutum hangisidir?"
        ans, celd = "Güzel ahlak ve nezaket", ["Kibir ve gurur", "İsraf etmek", "Bencillik"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    else: # İngilizce
        sorular = [
            ("Where are you from?", "I am from Turkey.", ["My name is " + kisi + ".", "Fine, thanks.", "At 8 o'clock."]),
            ("How old are you?", "I am 10 years old.", ["I like music.", "Yes, it is.", "In the school."])
        ]
        s = random.choice(sorular)
        return {"soru": f"Choose the correct response: <b>'{s[0]}'</b>", "siklar": [s[1]] + s[2], "dogru": s[1], "gorsel_svg": None}

# =========================================================
# KESİN BENZERSİZ HASH VE BENZERSİZ FİLTRELEME
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
        while uretilen_ders_sorusu < her_ders_icin_sayi and deneme < 1000 and len(havuz) < hedef_sayi:
            deneme += 1
            secilen_u = random.choice(uniteler)
            s = dinamik_soru_uretici(ders, secilen_u)
            s["ders"] = ders
            s["unite"] = secilen_u
            
            random.shuffle(s["siklar"])

            # Hash ile parmak izi alma (Mükemmel benzersizlik)
            fingerprint = hashlib.sha256((s["soru"] + s["dogru"] + "".join(s["siklar"])).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_set and len(s["siklar"]) == 4:
                hash_set.add(fingerprint)
                havuz.append(s)
                uretilen_ders_sorusu += 1

    return havuz[:hedef_sayi]

# =========================================================
# STREAMLIT ARAYÜZ SÜRÜCÜSÜ
# =========================================================
st.title("🎓 MEB 5. Sınıf Dinamik Soru Bankası & Bilgi Yarışması")

st.sidebar.header("⚙️ Müfredat ve Yarışma Ayarları")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"{ders_adi}", expanded=False):
        select_all = st.checkbox(f"Tümünü Seç", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()

# Soru sayısı 10 ile 100 arasında sınırlandırıldı
soru_sayisi = st.sidebar.number_input(
    "Toplam Soru Sayısı (10-100):", 
    min_value=10, 
    max_value=100, 
    value=10, 
    step=5, 
    disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"]
)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Soru Üret / Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            with st.spinner("Benzersiz sorular üretiliyor..."):
                sorular = kesin_benzersiz_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen en az 1 ders/kategori seçin!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Üret", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.rerun()

# --- ARAYÜZ AKIŞI ---
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Soru & Yarışma Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Kategori/Ünite Sayısı: **{len(secilen_uniteler)}**. Sol menüdeki **'Soru Üret / Başlat'** butonuna basınız.")
    else:
        st.warning("⚠️ Lütfen sol menüden ders veya Bilgi Yarışması kategorisi seçiniz.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular başarıyla üretildi!")
    st.markdown(f"**Toplam Soru Sayısı:** {len(st.session_state['soru_listesi'])}")
    
    if st.button("⏱️ Başlat", type="primary"):
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

    st.markdown(f"### **Soru {idx + 1}:**\n{q['soru']}", unsafe_allow_html=True)

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
        if b2.button("🏁 Bitir", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sonuç Karnesi")
    
    toplam = len(st.session_state["soru_listesi"])
    dogru = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    
    st.metric("Doğru / Toplam", f"{dogru} / {toplam}")
    st.progress(dogru / toplam if toplam > 0 else 0)
    
    if st.button("🔄 Yeni Yarışma / Test Yap"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
