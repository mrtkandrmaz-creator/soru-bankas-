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
# MÜFREDAT YAPISI (ALT KATEGORİSİZ DÜZ ÜNİTE YAPISI)
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
# DINAMIK SVG ÇİZİM MOTORU (Geometri Soruları İçin)
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
# RASTGELE DEĞİŞKEN MATRİSLERİ (TRİLYONLARCA KOMBİNASYON)
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem", "Yara", "Onur", "Görkem", "Arda", "Defne"]
NESNELER = ["fındık", "bilye", "kitap", "kalem", "pul", "elma", "ceviz", "etiket", "sayfa", "çikolata", "kart", "balon"]
MADDELER = ["su", "zeytinyağı", "alkol", "sirke", "süt", "cıva", "meyve suyu"]
YEMEKLER = ["Mantı", "Çiğ Köfte", "Cağ Kebabı", "Tantuni", "Künefe", "Yağlama", "Baklava", "Kuru Fasulye"]

# =========================================================
# BAĞIMSIZ DINAMIK SORU ÜRETICI
# =========================================================
def dinamik_soru_uretici(ders, unite):
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    nesne = random.choice(NESNELER)
    madde = random.choice(MADDELER)
    
    # ---------------------------------------------------------
    # 📐 MATEMATİK DERSİ (BAĞIMSIZ ALT SORU TİPLERİ)
    # ---------------------------------------------------------
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

            else: # yuvarlama
                sayi = random.randint(105, 995)
                ans = str(round(sayi, -1))
                q = f"<b>{sayi}</b> sayısı en yakın onluğa yuvarlandığında {kisi} hangi sonucu bulmalıdır?"
                celd = [str(int(ans) + 10), str(int(ans) - 10), str(sayi)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. ünite" in u_low:
            alt_tip = random.choice(["bileşik", "sıralama", "toplama", "cokluk"])
            if alt_tip == "bileşik":
                tam, payda = random.randint(1, 5), random.randint(3, 8)
                pay = random.randint(1, payda - 1)
                b_pay = tam * payda + pay
                q = f"<b>{tam} tam {pay}/{payda}</b> tam sayılı kesrinin bileşik kesre dönüştürülmüş hali aşağıdakilerden hangisidir?"
                ans = f"{b_pay}/{payda}"
                celd = [f"{b_pay + 1}/{payda}", f"{b_pay - 1}/{payda}", f"{tam * pay}/{payda}"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

            elif alt_tip == "sıralama":
                p1, p2, p3 = 2, 5, 7
                payda = 9
                q = f"<b>{p1}/{payda}</b>, <b>{p2}/{payda}</b> ve <b>{p3}/{payda}</b> kesirlerinin küçükten büyüğe sıralanışı hangisidir?"
                ans = f"{p1}/{payda} < {p2}/{payda} < {p3}/{payda}"
                celd = [f"{p3}/{payda} < {p2}/{payda} < {p1}/{payda}", f"{p2}/{payda} < {p1}/{payda} < {p3}/{payda}", f"{p1}/{payda} < {p3}/{payda} < {p2}/{payda}"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

            elif alt_tip == "toplama":
                pay1, pay2, payda = random.randint(1, 3), random.randint(1, 3), 9
                ans = f"{pay1 + pay2}/{payda}"
                q = f"{kisi} bir pastanın önce <b>{pay1}/{payda}</b>'ini, sonra <b>{pay2}/{payda}</b>'sini yemiştir. Toplam kaçta kaçını yemiştir?"
                celd = [f"{pay1 + pay2}/{payda * 2}", f"{pay1 * pay2}/{payda}", f"{abs(pay2 - pay1)}/{payda}"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

            else: # cokluk
                toplam, payda, pay = random.choice([20, 30, 40, 50, 60, 100]), 5, random.choice([1, 2, 3])
                sonuc = (toplam // payda) * pay
                q = f"{kisi} {toplam} adet {nesne}sinin <b>{pay}/{payda}</b>'ini arkadaşına vermiştir. Kaç adet {nesne} vermiştir?"
                ans = str(sonuc)
                celd = [str(sonuc + 5), str(abs(sonuc - 3)), str(toplam // payda)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. ünite" in u_low:
            alt_tip = random.choice(["ondalik_okuma", "karsilastirma", "yuzde_sembol", "yuzde_hesap"])
            if alt_tip == "ondalik_okuma":
                tam, ondalik = random.randint(1, 15), random.choice([25, 75, 5])
                q = f"<b>{tam}.{ondalik}</b> ondalık gösteriminin okunuşu aşağıdakilerden hangisidir?"
                ans = f"{tam} tam yüzde {ondalik}" if ondalik in [25, 75] else f"{tam} tam onda {ondalik}"
                celd = [f"{tam} tam binde {ondalik}", f"{tam} tam {ondalik}", f"yüzde {tam}"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            elif alt_tip == "karsilastirma":
                q = f"Aşağıdaki ondalık gösterimlerden hangisi <b>en büyüktür</b>?"
                ans = "5.8"
                celd = ["5.08", "5.79", "5.125"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            elif alt_tip == "yuzde_sembol":
                p = random.choice([10, 20, 25, 50, 75])
                q = f"<b>%{p}</b> ifadesinin kesir gösterimi aşağıdakilerden hangisidir?"
                ans = f"{p}/100"
                celd = [f"100/{p}", f"{p}/10", f"1/{p}"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            else:
                fiyat, yuzde = random.choice([100, 200, 300, 500]), random.choice([10, 20, 25, 50])
                indirim = (fiyat * yuzde) // 100
                ans = str(fiyat - indirim)
                q = f"{kisi} {fiyat} TL değerindeki bir ürünü <b>%{yuzde}</b> indirimle satın almıştır. Kaç TL ödemiştir?"
                celd = [str(indirim), str(fiyat + indirim), str(fiyat - 10)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. ünite" in u_low or "5. ünite" in u_low:
            alt_tip = random.choice(["ucgen_aci", "aci_tur"])
            if alt_tip == "ucgen_aci":
                koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
                a, b = random.randint(35, 80), random.randint(30, 70)
                c = 180 - (a + b)
                q = f"Şekildeki {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[0]}) = {a}° ve m({koseler[1]}) = {b}° olduğuna göre verilmeyen m({koseler[2]}) açısı kaç derecedir?"
                ans = f"{c}°"
                celd = [f"{c + 10}°", f"{abs(c - 15)}°", f"{c + 20}°"]
                svg = svg_dinamik_ucgen_ciz(a, b, 0, koseler)
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": svg}
            else:
                aci = random.choice([45, 90, 120, 150])
                tur = "Dik Açı" if aci == 90 else ("Geniş Açı" if aci > 90 else "Dar Açı")
                q = f"Ölçüsü <b>{aci}°</b> olan bir açı, açı türüne göre aşağıdakilerden hangisidir?"
                ans = tur
                celd = list({"Dar Açı", "Dik Açı", "Geniş Açı", "Doğru Açı"} - {tur})
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        else: # 6. Ünite
            saat = random.randint(2, 5)
            ans = str(saat * 60)
            q = f"{kisi} sinemada <b>{saat} saat</b> süren bir film izlemiştir. Bu süre kaç dakikadır?"
            celd = [str(saat * 60 + 30), str(saat * 100), str(saat * 45)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # ---------------------------------------------------------
    # 🔬 FEN BİLİMLERİ DERSİ (BAĞIMSIZ ALT SORU TİPLERİ)
    # ---------------------------------------------------------
    elif ders == "Fen Bilimleri":
        if "1. ünite" in u_low:
            alt_tip = random.choice(["gunes", "ay_yapi", "evreler", "hareketler"])
            if alt_tip == "gunes":
                q = f"{kisi}'nin fen dersinde öğrendiğine göre Güneş'in yüzey sıcaklığı yaklaşık kaç °C'dir?"
                ans, celd = "6000 °C", ["15 Milyon °C", "1000 °C", "100 °C"]
            elif alt_tip == "ay_yapi":
                q = f"Ay'da atmosferin olmamasının temel sonucu aşağıdakilerden hangisidir?"
                ans, celd = "Gece ve gündüz sıcaklık farkının çok yüksek olması", ["Ay'ın kendi etrafında dönmemesi", "Sürekli yağmur yağması", "Işık kaynağı olması"]
            elif alt_tip == "evreler":
                evre = random.choice(["Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"])
                tanimlar = {
                    "Yeni Ay": "Ay'ın Dünya'dan bakıldığında tamamen karanlık göründüğü evre",
                    "İlk Dördün": "Ay'ın 'D' harfi şeklinde aydınlık göründüğü ana evre",
                    "Dolunay": "Ay'ın tamamen aydınlık ve dairesel göründüğü ana evre",
                    "Son Dördün": "Ay'ın 'ters D' harfi şeklinde göründüğü ana evre"
                }
                q = f"<b>{tanimlar[evre]}</b> aşağıdakilerden hangisidir?"
                ans = evre
                celd = list({"Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"} - {evre})
            else:
                q = f"Dünya'nın kendi ekseni etrafındaki dönüşünü {kisi} kaç saatte tamamlar?"
                ans, celd = "24 Saat", ["365 Gün", "27 Gün", "12 Saat"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. ünite" in u_low:
            alt_tip = random.choice(["mikro", "mantar", "bitki", "hayvan"])
            if alt_tip == "mikro":
                q = f"Sütten yoğurt yapılmasını sağlayan mikroskobik canlı grubu hangisidir?"
                ans, celd = "Yararlı Bakteriler", ["Zararlı Mantarlar", "Virüsler", "Amip"]
            elif alt_tip == "mantar":
                q = f"Aşağıdakilerden hangisi kendi besinini üretemeyen mantarlar sınıfındadır?"
                ans, celd = "Şapkalı Mantar", ["Eğrelti Otu", "Papatya", "Çam Ağacı"]
            elif alt_tip == "bitki":
                q = f"Aşağıdakilerden hangisi <b>çiçeksiz bir bitkidir</b>?"
                ans, celd = "Eğrelti Otu", ["Gül", "Lale", "Elma Ağacı"]
            else:
                q = f"Aşağıdaki canlılardan hangisi <b>omurgalı hayvanlar</b> sınıfında yer alır?"
                ans, celd = "Kedi", ["Sinek", "Ahtapot", "Salyangoz"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. ünite" in u_low:
            alt_tip = random.choice(["dinamometre", "surtunme"])
            if alt_tip == "dinamometre":
                a1 = random.randint(5, 50)
                q = f"Bir dinamometreye {a1} N ağırlığındaki cisim asıldığında kaç N kuvvet ölçer?"
                ans, celd = f"{a1} N", [f"{a1 * 10} N", f"{a1 + 5} N", f"{max(1, a1 - 2)} N"]
            else:
                q = f"{kisi} oyuncak arabayı sürerken hangi yüzeyde <b>sürtünme kuvveti en fazladır</b>?"
                ans, celd = "Halı Zemin", ["Buzlu Zemin", "Cam Zemin", "Cilalı Tahta"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. ünite" in u_low:
            q = f"Sıvı bir maddenin ısı vererek katı hâle geçmesi olayına ne ad verilir?"
            ans, celd = "Donma", ["Erime", "Buharlaşma", "Süblimleşme"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        else: # 5. ünite
            q = f"Aşağıdaki maddelerden hangisi <b>opak (ışığı geçirmeyen)</b> maddedir?"
            ans, celd = "Tahta Levha", ["Pencere Camı", "Şeffaf Poşet", "Temiz Su"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # ---------------------------------------------------------
    # 🏆 BİLGİ YARIŞMASI KATEGORİSİ
    # ---------------------------------------------------------
    elif ders == "🏆 Bilgi Yarışması":
        if "başkent" in u_low or "coğrafya" in u_low:
            havuz = [
                ("Fransa", "Paris", ["Lyon", "Marsilya", "Nice"]),
                ("Almanya", "Berlin", ["Münih", "Frankfurt", "Hamburg"]),
                ("Japonya", "Tokyo", ["Kyoto", "Osaka", "Hiroşima"]),
                ("İtalya", "Roma", ["Milano", "Venedik", "Napoli"]),
                ("İspanya", "Madrid", ["Barselona", "Sevilla", "Valensiya"]),
                ("İngiltere", "Londra", ["Manchester", "Liverpool", "Birmingham"]),
                ("Kanada", "Ottawa", ["Toronto", "Vancouver", "Montreal"])
            ]
            sec = random.choice(havuz)
            q = f"<b>{sec[0]}</b> ülkesinin başkenti aşağıdakilerden hangisidir?"
            return {"soru": q, "siklar": [sec[1]] + sec[2], "dogru": sec[1], "gorsel_svg": None}
        
        elif "mutfak" in u_low:
            sehir = random.choice(YEMEKLER)
            q = f"<b>{sehir}</b> lezzeti ile meşhur olan ilimiz/ülkemiz hangisidir?"
            ans, celd = "Gaziantep", ["Kayseri", "Adana", "Trabzon"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        else:
            q = "Dünyanın en büyük okyanusu hangisidir?"
            ans, celd = "Büyük Okyanus (Pasifik)", ["Atlas Okyanusu", "Hint Okyanusu", "Arktik Okyanusu"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # ---------------------------------------------------------
    # 📚 TÜRKÇE, SOSYAL, DİN, İNGİLİZCE
    # ---------------------------------------------------------
    elif ders == "Türkçe":
        q = f"'{random.choice(['Mektep', 'Muallim', 'Hediye'])}' kelimesinin eş anlamlısı nedir?"
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

    else: # İngilizce
        q = f"Choose the correct option: 'Where are you from?'"
        ans, celd = "I am from Turkey.", ["I am 10 years old.", "My name is Can.", "Fine, thanks."]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

# =========================================================
# KESİN BENZERSİZ SORU ÜRETME MOTORU
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

            # SHA-256 ile parmak izi kontrolü
            fingerprint = hashlib.sha256((s["soru"] + s["dogru"] + "".join(s["siklar"])).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_set and len(s["siklar"]) == 4:
                hash_set.add(fingerprint)
                havuz.append(s)
                uretilen_ders_sorusu += 1

    return havuz[:hedef_sayi]

# =========================================================
# STREAMLIT ARAYÜZ
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
            with st.spinner("Soru havuzundan benzersiz sorular üretiliyor..."):
                sorular = kesin_benzersiz_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen en az 1 ünite veya ders seçin!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Üret", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.rerun()

# --- ARAYÜZ AKIŞI ---
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Soru & Yarışma Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Sol menüdeki **'Soru Üret / Başlat'** butonuna basınız.")
    else:
        st.warning("⚠️ Lütfen sol menüden üniteleri seçiniz.")

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

    # --- ÜST BİLGİ & SINAVI BİTİR ÜST BUTONU ---
    c_left, c_middle, c_right = st.columns([3, 1, 1])
    c_left.caption(f"📌 **{q['ders']}** - {q['unite']}")
    c_middle.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")
    
    # Her soru ekranının üst alanında yer alan Sınavı Bitir butonu
    if c_right.button("🏁 Sınavı Bitir", key=f"top_finish_{idx}", type="secondary", use_container_width=True):
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

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
        if b2.button("🏁 Sınavı Tamamla", type="primary"):
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
