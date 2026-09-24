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
    ],
    "Almanca": [
        "Einheit 1: Hallo! (Selamlaşma ve Tanışma)",
        "Einheit 2: Meine Schule (Okul ve Eşyalar)",
        "Einheit 3: Meine Familie (Aile Tanıtımı)",
        "Einheit 4: Zahlen und Farben (Sayılar ve Renkler)",
        "Einheit 5: Mein Tag (Günlük Rutinler)",
        "Einheit 6: Hobbys und Tiere (Hobiler ve Hayvanlar)"
    ],
    "Bilişim Teknolojileri": [
        "1. Ünite: Bilişim Teknolojileri ve İnternet Etiği",
        "2. Ünite: Problem Çözme ve Algoritma"
    ]
}

# =========================================================
# 2. SVG GÖRSEL MOTORU
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

def svg_ucgen_ciz(a, b, c, köşe_isimleri=("A", "B", "C")):
    # Basit dinamik üçgen çizimi
    return f'''
    <svg width="260" height="140" viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="8" stroke="#e2e8f0"/>
      <polygon points="130,20 40,110 220,110" fill="#eff6ff" stroke="#2563eb" stroke-width="3"/>
      <text x="130" y="15" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e40af" text-anchor="middle">{köşe_isimleri[0]} ({a}°)</text>
      <text x="25" y="125" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e40af" text-anchor="middle">{köşe_isimleri[1]} ({b}°)</text>
      <text x="235" y="125" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e40af" text-anchor="middle">{köşe_isimleri[2]} ({c}°)</text>
    </svg>
    '''

# =========================================================
# 3. ÜÇGENDE AÇILAR ÖZEL MİLYONLUK DİNAMİK MOTORU
# =========================================================
def ucgende_acilar_engine():
    kisi = random.choice(["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Emin"])
    koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
    
    kategori = random.choice(["verilmeyen_aci", "ikizkenar_ucgen", "eskenar_ucgen", "ucgen_cesitleri"])

    # 1. ALT KATEGORİ: İki Açısı Verilen Üçgende Verilmeyen Açıyı Bulma
    if kategori == "verilmeyen_aci":
        a = random.randint(30, 100)
        b = random.randint(20, 170 - a)
        c = 180 - (a + b)
        
        sorulan = random.choice(["A", "B", "C"])
        if sorulan == "A":
            v1, v2, ans_val, s_kose = b, c, a, koseler[0]
            k1_k, k2_k = koseler[1], koseler[2]
        elif sorulan == "B":
            v1, v2, ans_val, s_kose = a, c, b, koseler[1]
            k1_k, k2_k = koseler[0], koseler[2]
        else:
            v1, v2, ans_val, s_kose = a, b, c, koseler[2]
            k1_k, k2_k = koseler[0], koseler[1]

        q = f"Bir {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({k1_k}) = {v1}° ve m({k2_k}) = {v2}° olarak ölçülmüştür. {kisi}'nin bulması gereken m({s_kose}) kaç derecedir?"
        ans = f"{ans_val}°"
        celd = [f"{ans_val + 10}°", f"{abs(ans_val - 15)}°", f"{ans_val + 20}°"]

    # 2. ALT KATEGORİ: İkizkenar Üçgen Açı Hesabı
    elif kategori == "ikizkenar_ucgen":
        senaryo = random.choice(["tepe_verildi", "taban_verildi"])
        if senaryo == "tepe_verildi":
            tepe = random.choice([40, 50, 60, 70, 80, 90, 100])
            taban = (180 - tepe) // 2
            q = f"{koseler[0]}{koseler[1]}{koseler[2]} bir ikizkenar üçgendir. |{koseler[0]}{koseler[1]}| = |{koseler[0]}{koseler[2]}| ve tepe açısı m({koseler[0]}) = {tepe}° olduğuna göre taban açılarından m({koseler[1]}) kaç derecedir?"
            ans = f"{taban}°"
            celd = [f"{taban + 10}°", f"{taban - 10}°", f"{180 - tepe}°"]
        else:
            taban = random.randint(35, 75)
            tepe = 180 - (2 * taban)
            q = f"Taban açılarından biri {taban}° olan ikizkenar bir üçgenin tepe açısının ölçüsü kaç derecedir?"
            ans = f"{tepe}°"
            celd = [f"{tepe + 15}°", f"{abs(tepe - 10)}°", f"{taban}°"]

    # 3. ALT KATEGORİ: Eşkenar Üçgen Açı Özellikleri
    elif kategori == "eskenar_ucgen":
        sistem = random.choice([1, 2])
        if sistem == 1:
            q = f"Bütün kenar uzunlukları birbirine eşit olan bir {koseler[0]}{koseler[1]}{koseler[2]} eşkenar üçgeninin her bir iç açısının ölçüsü kaç derecedir?"
            ans = "60°"
            celd = ["90°", "45°", "180°"]
        else:
            ek = random.randint(10, 40)
            toplam = 60 + ek
            q = f"Bir eşkenar üçgenin bir iç açısına {ek}° eklendiğinde elde edilen yeni açının türü hangisidir?"
            if toplam == 90:
                ans = "Dik Açı"
                celd = ["Dar Açı", "Geniş Açı", "Doğru Açı"]
            elif toplam < 90:
                ans = "Dar Açı"
                celd = ["Dik Açı", "Geniş Açı", "Tam Açı"]
            else:
                ans = "Geniş Açı"
                celd = ["Dar Açı", "Dik Açı", "Doğru Açı"]

    # 4. ALT KATEGORİ: Açılanına Göre Üçgen Çeşitleri (Dar, Dik, Geniş)
    else:
        a = random.randint(20, 80)
        b = random.randint(20, 80)
        c = 180 - (a + b)
        
        if max(a, b, c) == 90:
            tur = "Dik Açılı Üçgen"
            celd = ["Dar Açılı Üçgen", "Geniş Açılı Üçgen", "Eşkenar Üçgen"]
        elif max(a, b, c) > 90:
            tur = "Geniş Açılı Üçgen"
            celd = ["Dar Açılı Üçgen", "Dik Açılı Üçgen", "Eşkenar Üçgen"]
        else:
            tur = "Dar Açılı Üçgen"
            celd = ["Dik Açılı Üçgen", "Geniş Açılı Üçgen", "Doğru Açılı Üçgen"]

        q = f"Açı ölçüleri sırasıyla {a}°, {b}° ve {c}° olan bir üçgen, açılarına göre ne tür bir üçgendir?"
        ans = tur

    siklar = [ans] + celd
    random.shuffle(siklar)
    return {"soru": q, "siklar": siklar, "dogru": ans, "gorsel_svg": None}

# =========================================================
# 4. GÜNEŞ, DÜNYA VE AY ÖZEL DİNAMİK MOTORU
# =========================================================
def gunes_dunya_ay_engine():
    kisi = random.choice(["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru"])
    arac = random.choice(["teleskop", "dürbün", "özel filtreli gözlük", "uzay gözlem simülasyonu"])
    
    kategori = random.choice(["gunes_yapisi", "dunya_hareket", "ay_evreleri", "ay_fiziksel"])

    if kategori == "gunes_yapisi":
        oran = random.choice([109, 1300000, 15000000, 6000])
        if oran == 109:
            q = f"{kisi}, {arac} kullanarak Güneş ve Dünya'nın çaplarını kıyaslamıştır. Güneş'in çapı Dünya'nın çapının yaklaşık kaç katıdır?"
            ans = "109 katı"
            celd = ["50 katı", "500 katı", "1000 katı"]
        elif oran == 1300000:
            q = f"{kisi}'nin astronomi kulübünde sunduğu raporda: 'Güneş'in içine yaklaşık kaç adet Dünya sığabilir?' sorusunun doğru yanıtı aşağıdakilerden hangisidir?"
            ans = "1,3 milyon"
            celd = ["100 bin", "500 bin", "10 milyon"]
        elif oran == 15000000:
            q = f"Güneş'in merkezindeki çekirdek sıcaklığı yaklaşık kaç derecedir?"
            ans = "15 milyon °C"
            celd = ["6000 °C", "100 bin °C", "1 milyon °C"]
        else:
            q = f"Güneş'in yüzey sıcaklığı yaklaşık kaç derecedir?"
            ans = "6000 °C"
            celd = ["15 milyon °C", "1000 °C", "100.000 °C"]

    elif kategori == "dunya_hareket":
        tur = random.choice(["kendi_ekseninde", "gunes_etrafinda"])
        if tur == "kendi_ekseninde":
            q = f"{kisi}, Dünya'nın kendi ekseni etrafındaki bir tam dönüşünü tamamladığını gözlemlemiştir. Bu hareketin süresi ve sonucu hangisinde doğru verilmiştir?"
            ans = "24 saat - Gece ve gündüz oluşur"
            celd = ["365 gün - Mevsimler oluşur", "27 gün - Ay'ın evreleri oluşur", "12 saat - Yıllık sıcaklık farkı oluşur"]
        else:
            q = f"Dünya'nın Güneş etrafındaki dolanma hareketi ile ilgili aşağıdakilerden hangisi doğrudur?"
            ans = "Dolanma süresi 365 gün 6 saattir ve mevsimler meydana gelir."
            celd = ["Dolanma süresi 24 saattir ve gece-gündüz oluşur.", "Dolanma süresi 27 gündür.", "Dolanma hareketi sırasında Dünya sabit kalır."]

    elif kategori == "ay_evreleri":
        evre_tipi = random.choice(["yeniay", "dolunay", "ilk_dordun", "son_dordun"])
        if evre_tipi == "yeniay":
            q = f"{kisi}, gece gökyüzüne baktığında Ay'ı hiç göremediğini fark etmiştir. Bu sırada Ay, Güneş ile Dünya arasındadır. Bu evre hangisidir?"
            ans = "Yeni Ay"
            celd = ["Dolunay", "İlk Dördün", "Son Dördün"]
        elif evre_tipi == "dolunay":
            q = f"Dünya, Güneş ile Ay arasındayken Ay'ın Dünya'ya bakan yüzü tamamen aydınlık görülür. Bu ana evre hangisidir?"
            ans = "Dolunay"
            celd = ["Yeni Ay", "Hilal", "Şişkin Ay"]
        elif evre_tipi == "ilk_dordun":
            q = f"Ay'ın sağ yarısının aydınlandığı ve 'D' harfine benzediği ana evre hangisidir?"
            ans = "İlk Dördün"
            celd = ["Son Dördün", "Yeni Ay", "Dolunay"]
        else:
            q = f"Ay'ın sol yarısının aydınlandığı ve ters 'D' harfine benzediği ana evre hangisidir?"
            ans = "Son Dördün"
            celd = ["İlk Dördün", "Hilal", "Dolunay"]

    else:
        q = f"Ay yüzeyine meteorların çarpması sonucu oluşan büyük çukurlara ne ad verilir?"
        ans = "Krater"
        celd = ["Kanyon", "Obruk", "Fay hattı"]

    siklar = [ans] + celd
    random.shuffle(siklar)
    return {"soru": q, "siklar": siklar, "dogru": ans, "gorsel_svg": None}

# =========================================================
# 5. TÜM DERSLER İÇİN GENEL DİNAMİK ENGINE
# =========================================================
def genel_dinamik_engine(ders, unite):
    u_low = unite.lower()
    
    # Özel Ünite Kontrolü: Üçgende Açılar
    if "üçgende açılar" in u_low or "üçgen" in u_low:
        res = ucgende_acilar_engine()
        res["ders"] = ders
        res["unite"] = unite
        return res

    # Özel Ünite Kontrolü: Güneş, Dünya ve Ay
    elif "güneş, dünya ve ay" in u_low or "güneş" in u_low:
        res = gunes_dunya_ay_engine()
        res["ders"] = ders
        res["unite"] = unite
        return res

    isimler = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin", "Kaan", "Deniz", "Ömer"]
    
    # MATEMATİK DİĞER
    if ders == "Matematik":
        if "açı" in u_low:
            aci_deg = random.randint(15, 165)
            if aci_deg == 90:
                tur, celd = "Dik Açı", ["Dar Açı", "Geniş Açı", "Doğru Açı"]
            elif aci_deg < 90:
                tur, celd = "Dar Açı", ["Dik Açı", "Geniş Açı", "Tam Açı"]
            else:
                tur, celd = "Geniş Açı", ["Dar Açı", "Dik Açı", "Doğru Açı"]
            q_text = f"İletki üzerinde gösterilen {aci_deg}° ölçüsündeki açının türü hangisidir?"
            siklar = [tur] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_iletki_aci_ciz(aci_deg), "siklar": siklar, "dogru": tur}
        else:
            n1, n2 = random.randint(120, 950), random.randint(10, 80)
            ans = n1 + n2
            kisi = random.choice(isimler)
            q_text = f"{kisi} biriktirdiği {n1} TL paraya {n2} TL daha eklemiştir. Toplam kaç TL'si olmuştur?"
            siklar = [str(ans), str(ans+10), str(abs(ans-15)), str(ans+25)]
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": str(ans)}

    # ALMANCA
    elif ders == "Almanca":
        q = random.choice([
            ("Wie heißt du?", "Ich heiße...", ["Danke, gut.", "Ich bin 10 Jahre alt.", "Guten Morgen."]),
            ("Was ist 'die Schule' auf Türkisch?", "Okul", ["Kalem", "Masa", "Kitap"])
        ])
        siklar = [q[1]] + q[2]
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q[0], "gorsel_svg": None, "siklar": siklar, "dogru": q[1]}

    # DİĞER DERSLER
    else:
        kisi = random.choice(isimler)
        q_text = f"{kisi}, '{unite}' konusuyla ilgili yaptığı çalışmada temel bir kavramı araştırmaktadır. Bu ünitenin ana konusu aşağıdakilerden hangisidir?"
        ans = f"{unite} temel prensipleri"
        celd = ["Yanlış eşleştirme A", "Alakasız konu B", "Hatalı ifade C"]
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": siklar, "dogru": ans}

# =========================================================
# 6. BENZERLİK ENGELLEYİCİ VE SIKI FİLTRELEME MOTORU
# =========================================================
def kesin_benzersiz_soru_uret(secilen_uniteler, hedef_sayi):
    havuz = []
    hash_set = set()
    
    if not secilen_uniteler:
        return []
        
    u_count = len(secilen_uniteler)
    taban = hedef_sayi // u_count
    kalan = hedef_sayi % u_count
    dagilim = [taban + (1 if i < kalan else 0) for i in range(u_count)]
    
    for idx, (h_ders, h_unite) in enumerate(secilen_uniteler):
        istenen = dagilim[idx]
        uretilen = 0
        deneme = 0
        
        while uretilen < istenen and deneme < 200:
            deneme += 1
            s = genel_dinamik_engine(h_ders, h_unite)
            
            # SHA-256 Sıkı Hash Kontrolü
            fingerprint = hashlib.sha256((s["soru"] + s["dogru"] + "".join(s["siklar"])).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_set and len(s["siklar"]) == 4:
                hash_set.add(fingerprint)
                havuz.append(s)
                uretilen += 1
                
    random.shuffle(havuz)
    return havuz

# =========================================================
# 7. STREAMLIT ARAYÜZ
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
            with st.spinner("Sorular seçilen ünitelerden %75 dinamik mantıkla üretiliyor..."):
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

# AKIŞ EKRANLARI
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Soru Üretim Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Sol menüdeki **'Test Üret'** butonuna basarak seçtiğiniz ünitelerle eşleşen soruları üretebilirsiniz.")
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

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=135)

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
