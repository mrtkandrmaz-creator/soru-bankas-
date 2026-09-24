import streamlit as st
import random
import time
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Soru & Deneme Sınavı Motoru", page_icon="🎓", layout="wide")

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
# 2. DERS ÖNCELİK SIRASI & MÜFREDAT YAPISI
# =========================================================
DERS_ONCELIK_SIRASI = [
    "Türkçe",
    "Matematik",
    "Fen Bilimleri",
    "Sosyal Bilgiler",
    "Din Kültürü ve Ahlak Bilgisi",
    "İngilizce",
    "🏆 Bilgi Yarışması"
]

MEB_MUFREDAT = {
    "Türkçe": [
        "1. Tema: Sözcükte Anlam ve Mantık Muhakeme",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragraf Analizi ve Görsel Okuma",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları"
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
    ],
    "🏆 Bilgi Yarışması": [
        "1. Kategori: Ülke Başkentleri ve Coğrafya",
        "2. Kategori: Dünya ve Yöresel Mutfaklar",
        "3. Kategori: Güncel Konular ve Genel Kültür",
        "4. Kategori: Ülkeler, Bayraklar ve Kültürler"
    ]
}

# 40 Haftalık MEB Müfredat İlerleme Haritası
MEB_HAFTALIK_MAPI = {}
for h in range(1, 41):
    MEB_HAFTALIK_MAPI[h] = []
    
    # Türkçe
    t_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Türkçe"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Türkçe", MEB_MUFREDAT["Türkçe"][t_idx]))

    # Matematik
    m_idx = min((h - 1) // 7, len(MEB_MUFREDAT["Matematik"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Matematik", MEB_MUFREDAT["Matematik"][m_idx]))

    # Fen Bilimleri
    f_idx = min((h - 1) // 8, len(MEB_MUFREDAT["Fen Bilimleri"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Fen Bilimleri", MEB_MUFREDAT["Fen Bilimleri"][f_idx]))

    # Sosyal Bilgiler
    s_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Sosyal Bilgiler"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Sosyal Bilgiler", MEB_MUFREDAT["Sosyal Bilgiler"][s_idx]))

    # Din Kültürü
    d_idx = min((h - 1) // 13, len(MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Din Kültürü ve Ahlak Bilgisi", MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"][d_idx]))

    # İngilizce
    i_idx = min((h - 1) // 10, len(MEB_MUFREDAT["İngilizce"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("İngilizce", MEB_MUFREDAT["İngilizce"][i_idx]))

# =========================================================
# 3. DİNAMİK SVG GEOMETRİ MOTORU
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
# 4. RASTGELE MATRİS VE SORU ÜRETİCİ
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem", "Yara", "Onur", "Görkem", "Arda", "Defne"]
NESNELER = ["fındık", "bilye", "kitap", "kalem", "pul", "elma", "ceviz", "etiket", "sayfa", "çikolata", "kart", "balon"]
YEMEKLER = ["Mantı", "Çiğ Köfte", "Cağ Kebabı", "Tantuni", "Künefe", "Yağlama", "Baklava", "Kuru Fasulye"]

def dinamik_soru_uretici(ders, unite):
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    nesne = random.choice(NESNELER)

    if ders == "Matematik":
        if "1. ünite" in u_low:
            alt_tip = random.choice(["okuma", "toplama_cikarma", "carpma_bolme", "yuvarlama"])
            if alt_tip == "okuma":
                sayi = random.randint(100000, 9999999)
                b_isimleri = ["yüz binler", "on binler", "binler", "yüzler", "onlar"]
                b_sec = random.choice(b_isimleri)
                carpan = {"yüz binler": 100000, "on binler": 10000, "binler": 1000, "yüzler": 100, "onlar": 10}[b_sec]
                b_deg = ((sayi // carpan) % 10) * carpan
                q = f"{kisi}'in yazdığı <b>{sayi}</b> sayısındaki {b_sec} basamağının basamak değeri kaçtır?"
                ans = str(b_deg)
                celd = [str(b_deg * 10), str(max(10, b_deg // 10)), str((sayi // carpan) % 10)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            elif alt_tip == "toplama_cikarma":
                n1, n2 = random.randint(1500, 9500), random.randint(1200, 8500)
                if random.choice([True, False]):
                    ans = str(n1 + n2)
                    q = f"{kisi}'in {n1} adet {nesne}si vardı. Arkadaşı ona {n2} adet daha {nesne} verirse toplam kaç {nesne}si olur?"
                    celd = [str(n1 + n2 + 100), str(n1 + n2 - 50), str(n1 + n2 + 500)]
                else:
                    ans = str(max(n1, n2) - min(n1, n2))
                    q = f"{kisi} {max(n1, n2)} TL parasının {min(n1, n2)} TL'sini harcadı. Geriye kaç TL'si kalmıştır?"
                    celd = [str(int(ans) + 100), str(abs(int(ans) - 50)), str(int(ans) + 200)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            elif alt_tip == "carpma_bolme":
                n1, n2 = random.randint(12, 85), random.randint(10, 45)
                ans = str(n1 * n2)
                q = f"{kisi} her birinde {n1} adet {nesne} bulunan {n2} koli satın almıştır. Toplam kaç adet {nesne} vardır?"
                celd = [str(n1 * n2 + n1), str(n1 * n2 - n2), str((n1 + 2) * n2)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            else:
                sayi = random.randint(105, 995)
                ans = str(round(sayi, -1))
                q = f"<b>{sayi}</b> sayısı en yakın onluğa yuvarlandığında {kisi} hangi sonucu bulmalıdır?"
                celd = [str(int(ans) + 10), str(int(ans) - 10), str(sayi)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. ünite" in u_low:
            tam, payda = random.randint(1, 5), random.randint(3, 8)
            pay = random.randint(1, payda - 1)
            b_pay = tam * payda + pay
            q = f"<b>{tam} tam {pay}/{payda}</b> tam sayılı kesrinin bileşik kesre dönüştürülmüş hali aşağıdakilerden hangisidir?"
            ans = f"{b_pay}/{payda}"
            celd = [f"{b_pay + 1}/{payda}", f"{b_pay - 1}/{payda}", f"{tam * pay}/{payda}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. ünite" in u_low:
            p = random.choice([10, 20, 25, 50, 75])
            q = f"<b>%{p}</b> ifadesinin kesir gösterimi aşağıdakilerden hangisidir?"
            ans = f"{p}/100"
            celd = [f"100/{p}", f"{p}/10", f"1/{p}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. ünite" in u_low or "5. ünite" in u_low:
            koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
            a, b = random.randint(35, 80), random.randint(30, 70)
            c = 180 - (a + b)
            q = f"Şekildeki {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[0]}) = {a}° ve m({koseler[1]}) = {b}° olduğuna göre verilmeyen m({koseler[2]}) açısı kaç derecedir?"
            ans = f"{c}°"
            celd = [f"{c + 10}°", f"{abs(c - 15)}°", f"{c + 20}°"]
            svg = svg_dinamik_ucgen_ciz(a, b, 0, koseler)
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": svg}

        else:
            saat = random.randint(2, 5)
            ans = str(saat * 60)
            q = f"{kisi} sinemada <b>{saat} saat</b> süren bir film izlemiştir. Bu süre kaç dakikadır?"
            celd = [str(saat * 60 + 30), str(saat * 100), str(saat * 45)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Fen Bilimleri":
        if "1. ünite" in u_low:
            q = f"Güneş'in yüzey sıcaklığı yaklaşık olarak kaç °C'dir?"
            ans, celd = "6000 °C", ["15 Milyon °C", "1000 °C", "100 °C"]
        elif "2. ünite" in u_low:
            q = f"Sütten yoğurt yapılmasını sağlayan faydalı canlı grubu hangisidir?"
            ans, celd = "Yararlı Bakteriler", ["Mantar", "Virüs", "Amip"]
        elif "3. ünite" in u_low:
            a1 = random.randint(5, 50)
            q = f"Bir dinamometreye {a1} N ağırlığında cisim asıldığında kaç N kuvvet gösterir?"
            ans, celd = f"{a1} N", [f"{a1 * 10} N", f"{a1 + 5} N", f"{max(1, a1 - 2)} N"]
        else:
            q = f"Sıvı bir maddenin ısı vererek katı hale geçmesine ne denir?"
            ans, celd = "Donma", ["Erime", "Buharlaşma", "Süblimleşme"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Türkçe":
        q = f"'{random.choice(['Mektep', 'Muallim', 'Hediye'])}' sözcüğünün eş anlamlısı nedir?"
        ans, celd = "Okul", ["Sınıf", "Öğrenci", "Kitap"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Sosyal Bilgiler":
        q = f"{kisi}'in evde üstlendiği hangisi bir sorumluluk örneğidir?"
        ans, celd = "Odasını toplamak", ["Oyun oynamak", "Ders dinlemek", "Dinlenmek"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        q = f"İslam dininde paylaşma ve yardımlaşma ibadetine ne ad verilir?"
        ans, celd = "Zekat", ["Oruç", "Hac", "Namaz"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "İngilizce":
        q = f"Choose the correct option: 'Where are you from?'"
        ans, celd = "I am from Turkey.", ["I am 10 years old.", "My name is Can.", "Fine, thanks."]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    else:
        q = f"<b>{random.choice(YEMEKLER)}</b> lezzeti ile meşhur olan ilimiz/ülkemiz hangisidir?"
        ans, celd = "Gaziantep", ["Kayseri", "Adana", "Trabzon"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

# =========================================================
# 5. DERS DERS SIRALI DÜZENDE SORU ÜRETME MOTORU
# =========================================================
def ders_sirali_soru_uret(secilen_uniteler, hedef_sayi):
    if not secilen_uniteler:
        return []

    ders_gruplari = {}
    for ders, unite in secilen_uniteler:
        ders_gruplari.setdefault(ders, []).append(unite)

    # DERS_ONCELIK_SIRASI sırasına göre sıralı gruplama
    aktif_dersler = [d for d in DERS_ONCELIK_SIRASI if d in ders_gruplari]
    if not aktif_dersler:
        return []

    her_ders_icin_sayi = max(1, hedef_sayi // len(aktif_dersler))
    tam_soru_listesi = []
    hash_set = set()

    for d_idx, ders in enumerate(aktif_dersler):
        uniteler = ders_gruplari[ders]
        dersin_hedef_sayisi = her_ders_icin_sayi if d_idx < len(aktif_dersler) - 1 else (hedef_sayi - len(tam_soru_listesi))
        
        uretilen_sayi = 0
        deneme = 0
        while uretilen_sayi < dersin_hedef_sayisi and deneme < 500:
            deneme += 1
            secilen_u = random.choice(uniteler)
            s = dinamik_soru_uretici(ders, secilen_u)
            s["ders"] = ders
            s["unite"] = secilen_u
            
            random.shuffle(s["siklar"])

            fingerprint = hashlib.sha256((s["soru"] + s["dogru"] + "".join(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                tam_soru_listesi.append(s)
                uretilen_sayi += 1

    return tam_soru_listesi[:hedef_sayi]

# =========================================================
# 6. STREAMLIT ARAYÜZÜ
# =========================================================
st.title("🎓 MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru")

st.sidebar.header("⚙️ Sınav ve Mod Seçimi")

mod_secim = st.sidebar.radio(
    "Çalışma Modu Seçiniz:",
    ["📅 40 Haftalık MEB Deneme Sınavları", "📚 Serbest Konu / Ünite Seçimi"],
    disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"]
)

secilen_uniteler = []

if mod_secim == "📅 40 Haftalık MEB Deneme Sınavları":
    st.sidebar.subheader("📅 Deneme Sınavı Haftası")
    secilen_hafta = st.sidebar.slider(
        "Deneme Sınavı Haftasını Seçin:",
        min_value=1,
        max_value=40,
        value=1,
        disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"]
    )
    
    # O haftaya kadar kapsanan tüm konuları ekle
    for h in range(1, secilen_hafta + 1):
        secilen_uniteler.extend(MEB_HAFTALIK_MAPI[h])
    
    st.sidebar.info(f"💡 **{secilen_hafta}. Hafta Denemesi:** 1. haftadan {secilen_hafta}. haftaya kadar işlenen tüm müfredat konularını kapsar.")

else:
    st.sidebar.subheader("📚 Ünite Seçimi")
    for ders_adi in DERS_ONCELIK_SIRASI:
        uniteler = MEB_MUFREDAT[ders_adi]
        with st.sidebar.expander(f"{ders_adi}", expanded=False):
            select_all = st.checkbox(f"Tümünü Seç", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            for idx, u in enumerate(uniteler):
                cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
                if cb:
                    secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()

soru_sayisi = st.sidebar.number_input(
    "Toplam Soru Sayısı (10-100):", 
    min_value=10, 
    max_value=100, 
    value=20, 
    step=5, 
    disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"]
)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Hazırla ve Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            with st.spinner("Sınav ders sıralamasına uygun şekilde oluşturuluyor..."):
                sorular = ders_sirali_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen ünite seçimi yapın!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Hazırla", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.rerun()

# --- EKRAN AKIŞI ---
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Sınav Başlatma Alanı")
    st.info("Sol panelden modu seçin ve **'Hazırla ve Başlat'** butonuna tıklayın.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular Ders Sırasına Göre Hazırlandı!")
    st.markdown(f"**Toplam Soru Sayısı:** {len(st.session_state['soru_listesi'])}")
    
    # Ders dağılım özeti gösterimi
    ders_sayilari = {}
    for s in st.session_state['soru_listesi']:
        ders_sayilari[s['ders']] = ders_sayilari.get(s['ders'], 0) + 1
    
    st.markdown("##### 📌 Sınav Ders Dağılımı (Sırasıyla):")
    cols = st.columns(len(ders_sayilari))
    for i, (d_isimlendirme, d_adet) in enumerate(ders_sayilari.items()):
        cols[i].metric(d_isimlendirme, f"{d_adet} Soru")

    if st.button("⏱️ Sınavı Başlat", type="primary"):
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

    # --- ÜST BİLGİ & SINAVI BİTİR ÜST BUTONU ---
    c_left, c_middle, c_right = st.columns([3, 1, 1])
    c_left.markdown(f"📖 **Ders:** {q['ders']} | 📌 **Konu:** {q['unite']}")
    c_middle.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")
    
    if c_right.button("🏁 Sınavı Bitir", key=f"top_finish_{idx}", type="secondary", use_container_width=True):
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

    st.markdown(f"### **Soru {idx + 1} / {len(st.session_state['soru_listesi'])}:**\n{q['soru']}", unsafe_allow_html=True)

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=145)

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Cevabınızı seçin:", q["siklar"], index=secim_index, key=f"radio_{idx}")
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
        if b2.button("🏁 Sınavı Tamamla", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuç Karnesi")
    
    toplam = len(st.session_state["soru_listesi"])
    dogru = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    
    st.metric("Doğru / Toplam", f"{dogru} / {toplam}")
    st.progress(dogru / toplam if toplam > 0 else 0)
    
    if st.button("🔄 Yeni Sınav / Deneme Yap"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
