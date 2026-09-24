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
# MÜFREDAT VE ALT KATEGORİ YAPISI (MATEMATİK VE FEN 4 ALT KATEGORİLİ)
# =========================================================
MEB_MUFREDAT = {
    "🏆 Bilgi Yarışması": [
        "1. Kategori: Ülke Başkentleri ve Coğrafya",
        "2. Kategori: Dünya ve Yöresel Mutfaklar",
        "3. Kategori: Güncel Konular ve Genel Kültür",
        "4. Kategori: Ülkeler, Bayraklar ve Kültürler"
    ],
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve İşlemler -> 1. Alt Kategori: Okuma, Yazma ve Basamak Değerleri",
        "1. Ünite: Doğal Sayılar ve İşlemler -> 2. Alt Kategori: Toplama ve Çıkarma Problemleri",
        "1. Ünite: Doğal Sayılar ve İşlemler -> 3. Alt Kategori: Çarpma ve Bölme İşlemleri",
        "1. Ünite: Doğal Sayılar ve İşlemler -> 4. Alt Kategori: Yuvarlama ve Tahmin Etme",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler -> 1. Alt Kategori: Bileşik ve Tam Sayılı Kesir Dönüşümü",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler -> 2. Alt Kategori: Kesirlerde Sıralama ve Denk Kesirler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler -> 3. Alt Kategori: Kesirlerle Toplama ve Çıkarma",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler -> 4. Alt Kategori: Bir Çokluğun İstenen Kesir Kadarını Bulma",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler -> 1. Alt Kategori: Ondalık Kesirlerin Okunuşu ve Basamakları",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler -> 2. Alt Kategori: Ondalık Gösterimlerde Karşılaştırma",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler -> 3. Alt Kategori: Yüzde Sembolü ve Dönüşümler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler -> 4. Alt Kategori: Yüzde Hesaplama Problemleri",
        "4. Ünite: Temel Geometrik Kavramlar ve Açı Ölçme -> 1. Alt Kategori: Doğru, Doğru Parçası ve Işın",
        "4. Ünite: Temel Geometrik Kavramlar ve Açı Ölçme -> 2. Alt Kategori: İki Doğrunun Birbirine Göre Konumları",
        "4. Ünite: Temel Geometrik Kavramlar ve Açı Ölçme -> 3. Alt Kategori: Açı Çeşitleri (Dar, Dik, Geniş)",
        "4. Ünite: Temel Geometrik Kavramlar ve Açı Ölçme -> 4. Alt Kategori: İletki ile Açı Ölçme ve Çizim",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri -> 1. Alt Kategori: Açılarına Göre Üçgenler",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri -> 2. Alt Kategori: Kenarlarına Göre Üçgenler",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri -> 3. Alt Kategori: Üçgenin İç Açıları Toplamı",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri -> 4. Alt Kategori: Dörtgenlerde İç Açılar Toplamı",
        "6. Ünite: Veri İşleme ve Ölçme -> 1. Alt Kategori: Sıklık Tablosu ve Sutun Grafiği",
        "6. Ünite: Veri İşleme ve Ölçme -> 2. Alt Kategori: Uzunluk Ölçme Birimleri ve Dönüşümler",
        "6. Ünite: Veri İşleme ve Ölçme -> 3. Alt Kategori: Zaman Ölçme Problemleri",
        "6. Ünite: Veri İşleme ve Ölçme -> 4. Alt Kategori: Çevre ve Alan Ölçme"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay -> 1. Alt Kategori: Güneş'in Yapısı ve Özellikleri",
        "1. Ünite: Güneş, Dünya ve Ay -> 2. Alt Kategori: Ay'ın Yapısı ve Atmosferi",
        "1. Ünite: Güneş, Dünya ve Ay -> 3. Alt Kategori: Ay'ın Evreleri (Ana ve Ara Evreler)",
        "1. Ünite: Güneş, Dünya ve Ay -> 4. Alt Kategori: Güneş, Dünya ve Ay'ın Hareketleri",
        "2. Ünite: Canlılar Dünyası -> 1. Alt Kategori: Mikroskobik Canlılar ve Bakteriler",
        "2. Ünite: Canlılar Dünyası -> 2. Alt Kategori: Mantarlar ve Çeşitleri",
        "2. Ünite: Canlılar Dünyası -> 3. Alt Kategori: Bitkiler (Çiçekli ve Çiçeksiz)",
        "2. Ünite: Canlılar Dünyası -> 4. Alt Kategori: Hayvanlar (Omurgalı ve Omurgasız)",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme -> 1. Alt Kategori: Dinamometre ve Kuvvet Ölçümü",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme -> 2. Alt Kategori: Yayların Uzama Miktarı ve Esneklik",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme -> 3. Alt Kategori: Sürtünme Kuvveti ve Yüzeyler",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme -> 4. Alt Kategori: Hava ve Su Direnci",
        "4. Ünite: Madde ve Değişim -> 1. Alt Kategori: Maddenin Hâl Değişimi (Erime, Donma, Buharlaşma)",
        "4. Ünite: Madde ve Değişim -> 2. Alt Kategori: Ayırt Edici Özellikler (Erime ve Kaynama Noktası)",
        "4. Ünite: Madde ve Değişim -> 3. Alt Kategori: Isı ve Sıcaklık Farkı",
        "4. Ünite: Madde ve Değişim -> 4. Alt Kategori: Maddelerin Isı Etkisiyle Genleşmesi ve Büzülmesi",
        "5. Ünite: Işığın Yayılması ve Tam Gölge -> 1. Alt Kategori: Işığın Doğrusal Yayılması",
        "5. Ünite: Işığın Yayılması ve Tam Gölge -> 2. Alt Kategori: Maddelerin Işığı Geçirmesi (Saydam, Yarı Saydam, Opak)",
        "5. Ünite: Işığın Yayılması ve Tam Gölge -> 3. Alt Kategori: Tam Gölge Oluşumu ve Gölge Boyu",
        "5. Ünite: Işığın Yayılması ve Tam Gölge -> 4. Alt Kategori: Gölge Boyunu Etkileyen Değişkenler"
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
# DINAMIK SVG ÇİZİM MOTORU (Görsel Geometri Soruları İçin)
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
# DEĞİŞKEN MATRİSLERİ (TRİLYONLARCA KOMBİNASYON İÇİN)
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem", "Yara", "Onur", "Görkem"]
NESNELER = ["fındık", "bilye", "kitap", "kalem", "pul", "elma", "ceviz", "etiket", "sayfa", "çikolata", "kart"]
YUZEYLER = ["buzlu zemin", "asfalt yol", "halı saha", "zımpara kağıdı", "cam yüzey", "tahta masa", "toprak yol"]
MADDELER = ["su", "zeytinyağı", "alkol", "sirke", "süt", "cıva"]
YEMEKLER = ["Mantı", "Çiğ Köfte", "Cağ Kebabı", "Tantuni", "Künefe", "Yağlama", "Baklava", "Kuru Fasulye"]

# =========================================================
# TRİLYONLARCA SONSUZ DİNAMİK SORU ÜRETİM MOTORU
# =========================================================
def dinamik_soru_uretici(ders, unite):
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    nesne = random.choice(NESNELER)
    yuzey = random.choice(YUZEYLER)
    madde = random.choice(MADDELER)
    
    # ---------------------------------------------------------
    # 📐 MATEMATİK DERSİ (HER ÜNİTE 4 ALT KATEGORİLİ)
    # ---------------------------------------------------------
    if ders == "Matematik":
        # 1. ÜNİTE
        if "1. alt kategori: okuma" in u_low:
            sayi = random.randint(100000, 9999999)
            b_isimleri = ["yüz binler", "on binler", "binler", "yüzler", "onlar"]
            b_sec = random.choice(b_isimleri)
            carpan = {"yüz binler": 100000, "on binler": 10000, "binler": 1000, "yüzler": 100, "onlar": 10}[b_sec]
            b_deg = ((sayi // carpan) % 10) * carpan
            sablonlar = [
                f"{kisi}'in yazdığı <b>{sayi}</b> sayısındaki {b_sec} basamağının basamak değeri kaçtır?",
                f"Matematik dersinde {kisi} tahtaya <b>{sayi}</b> sayısını yazmıştır. Bu sayıdaki {b_sec} basamak değeri nedir?",
                f"<b>{sayi}</b> sayısını inceleyen {kisi}, {b_sec} basamağındaki rakamın basamak değerini kaç bulur?"
            ]
            ans = str(b_deg)
            celd = [str(b_deg * 10), str(max(10, b_deg // 10)), str((sayi // carpan) % 10)]
            return {"soru": random.choice(sablonlar), "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. alt kategori: toplama" in u_low:
            n1, n2 = random.randint(1500, 9500), random.randint(1200, 8500)
            islem = random.choice(["ekleme", "çıkarma"])
            if islem == "ekleme":
                ans = str(n1 + n2)
                sablonlar = [
                    f"{kisi}'in {n1} adet {nesne}si vardı. Arkadaşı ona {n2} adet daha {nesne} verirse toplam kaç {nesne}si olur?",
                    f"Bir mağazada {n1} TL olan ürüne {n2} TL zam gelmiştir. {kisi}'in ödeyeceği yeni tutar kaç TL'dir?",
                    f"Kütüphanede {n1} roman ve {n2} hikaye kitabı vardır. {kisi} kütüphanede toplam kaç kitap saymıştır?"
                ]
                celd = [str(n1 + n2 + 100), str(n1 + n2 - 50), str(n1 + n2 + 500)]
            else:
                ans = str(max(n1, n2) - min(n1, n2))
                sablonlar = [
                    f"{kisi} {max(n1, n2)} TL parasının {min(n1, n2)} TL'sini harcadı. Geriye kaç TL'si kalmıştır?",
                    f"Bir depodaki {max(n1, n2)} litre suyun {min(n1, n2)} litresi kullanıldı. {kisi} depoda kaç litre su kaldığını hesaplamalıdır?"
                ]
                celd = [str(int(ans) + 100), str(abs(int(ans) - 50)), str(int(ans) + 200)]
            return {"soru": random.choice(sablonlar), "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. alt kategori: çarpma" in u_low:
            n1, n2 = random.randint(12, 85), random.randint(10, 45)
            ans = str(n1 * n2)
            sablonlar = [
                f"{kisi} her birinde {n1} adet {nesne} bulunan {n2} koli satın almıştır. Toplam kaç adet {nesne} vardır?",
                f"Bir okulda {n2} sınıf ve her sınıfta {n1} öğrenci vardır. {kisi} okuldaki toplam öğrenci sayısını kaç bulur?",
                f"Günde {n1} sayfa kitap okuyan {kisi}, {n2} günde toplam kaç sayfa okumuş olur?"
            ]
            celd = [str(n1 * n2 + n1), str(n1 * n2 - n2), str((n1 + 2) * n2)]
            return {"soru": random.choice(sablonlar), "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. alt kategori: yuvarlama" in u_low:
            sayi = random.randint(105, 995)
            ans = str(round(sayi, -1))
            sablonlar = [
                f"{kisi} elindeki <b>{sayi}</b> sayısını en yakın onluğa yuvarlamak istiyor. Elde edilen sayı kaçtır?",
                f"<b>{sayi}</b> sayısı en yakın onluğa yuvarlandığında {kisi} hangi sonucu bulmalıdır?",
                f"Ödevinde <b>{sayi}</b> sayısını en yakın onluğa yuvarlayan {kisi}'in cevabı ne olmalıdır?"
            ]
            celd = [str(int(ans) + 10), str(int(ans) - 10), str(sayi)]
            return {"soru": random.choice(sablonlar), "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 2. ÜNİTE (KESİRLER)
        elif "1. alt kategori: bileşik" in u_low:
            tam = random.randint(1, 5)
            payda = random.randint(3, 8)
            pay = random.randint(1, payda - 1)
            b_pay = tam * payda + pay
            q = f"<b>{tam} tam {pay}/{payda}</b> tam sayılı kesrinin bileşik kesre dönüştürülmüş hali aşağıdakilerden hangisidir?"
            ans = f"{b_pay}/{payda}"
            celd = [f"{b_pay + 1}/{payda}", f"{b_pay - 1}/{payda}", f"{tam * pay}/{payda}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. alt kategori: kesirlerde sıralama" in u_low:
            p1, p2, p3 = 2, 5, 7
            payda = 9
            q = f"<b>{p1}/{payda}</b>, <b>{p2}/{payda}</b> ve <b>{p3}/{payda}</b> kesirlerinin küçükten büyüğe doğru doğru sıralanışı hangisidir?"
            ans = f"{p1}/{payda} < {p2}/{payda} < {p3}/{payda}"
            celd = [
                f"{p3}/{payda} < {p2}/{payda} < {p1}/{payda}",
                f"{p2}/{payda} < {p1}/{payda} < {p3}/{payda}",
                f"{p1}/{payda} < {p3}/{payda} < {p2}/{payda}"
            ]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. alt kategori: kesirlerle toplama" in u_low:
            pay1, pay2, payda = 2, 3, 8
            ans = f"{pay1 + pay2}/{payda}"
            q = f"{kisi} bir pastanın önce <b>{pay1}/{payda}</b>'ini, sonra <b>{pay2}/{payda}</b>'sini yemiştir. Toplam kaçta kaçını yemiştir?"
            celd = [f"{pay1 + pay2}/{payda * 2}", f"{pay1 * pay2}/{payda}", f"{pay2 - pay1}/{payda}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. alt kategori: bir çokluğun" in u_low:
            toplam = random.choice([20, 30, 40, 50, 60, 100])
            payda = 5
            pay = random.choice([1, 2, 3])
            sonuc = (toplam // payda) * pay
            q = f"{kisi} {toplam} adet {nesne}sinin <b>{pay}/{payda}</b>'ini arkadaşına vermiştir. Kaç adet {nesne} vermiştir?"
            ans = str(sonuc)
            celd = [str(sonuc + 5), str(abs(sonuc - 3)), str(toplam // payda)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 3. ÜNİTE (ONDALIK & YÜZDE)
        elif "1. alt kategori: ondalık kesirlerin okunuşu" in u_low:
            tam, ondalik = random.randint(1, 15), random.choice([5, 25, 75, 8])
            q = f"<b>{tam}.{ondalik}</b> ondalık gösteriminin okunuşu aşağıdakilerden hangisidir?"
            ans = f"{tam} tam yüzde {ondalik}" if ondalik in [25, 75] else f"{tam} tam onda {ondalik}"
            celd = [f"{tam} tam binde {ondalik}", f"{tam} tam {ondalik}", f"yüzde {tam}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. alt kategori: ondalık gösterimlerde karşılaştırma" in u_low:
            q = f"Aşağıdaki ondalık gösterimlerden hangisi <b>en büyüktür</b>?"
            ans = "5.8"
            celd = ["5.08", "5.79", "5.125"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. alt kategori: yüzde sembolü" in u_low:
            p = random.choice([10, 20, 25, 50, 75])
            q = f"<b>%{p}</b> ifadesinin kesir gösterimi aşağıdakilerden hangisidir?"
            ans = f"{p}/100"
            celd = [f"100/{p}", f"{p}/10", f"1/{p}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. alt kategori: yüzde hesaplama" in u_low:
            fiyat = random.choice([100, 200, 300, 500])
            yuzde = random.choice([10, 20, 25, 50])
            indirim = (fiyat * yuzde) // 100
            ans = str(fiyat - indirim)
            q = f"{kisi} {fiyat} TL değerindeki bir ürünü <b>%{yuzde}</b> indirimle satın almıştır. Kaç TL ödemiştir?"
            celd = [str(indirim), str(fiyat + indirim), str(fiyat - 10)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 4 & 5. ÜNİTE (GEOMETRİ & ÜÇGENLER)
        elif "üçgenin iç açıları toplamı" in u_low or "üçgende açılar" in u_low:
            koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
            a, b = random.randint(35, 80), random.randint(30, 70)
            c = 180 - (a + b)
            sablonlar = [
                f"Şekildeki {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[0]}) = {a}° ve m({koseler[1]}) = {b}° olduğuna göre verilmeyen m({koseler[2]}) açısı kaç derecedir?",
                f"{koseler[0]}{koseler[1]}{koseler[2]} üçgeninde iki iç açı {a}° ve {b}° olarak ölçülmüştür. {kisi} üçüncü açıyı kaç derece bulmalıdır?"
            ]
            ans = f"{c}°"
            celd = [f"{c + 10}°", f"{abs(c - 15)}°", f"{c + 20}°"]
            svg = svg_dinamik_ucgen_ciz(a, b, 0, koseler)
            return {"soru": random.choice(sablonlar), "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": svg}

        elif "açı çeşitleri" in u_low:
            aci = random.choice([45, 90, 120, 150])
            tur = "Dik Açı" if aci == 90 else ("Geniş Açı" if aci > 90 else "Dar Açı")
            q = f"Ölçüsü <b>{aci}°</b> olan bir açı, açı türüne göre aşağıdakilerden hangisidir?"
            ans = tur
            celd = list({"Dar Açı", "Dik Açı", "Geniş Açı", "Doğru Açı"} - {tur})
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 6. ÜNİTE (VERİ & ÖLÇME)
        else:
            saat = random.randint(2, 5)
            ans = str(saat * 60)
            q = f"{kisi} sinemada <b>{saat} saat</b> süren bir film izlemiştir. Bu süre kaç dakikadır?"
            celd = [str(saat * 60 + 30), str(saat * 100), str(saat * 45)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # ---------------------------------------------------------
    # 🔬 FEN BİLİMLERİ DERSİ (HER ÜNİTE 4 ALT KATEGORİLİ)
    # ---------------------------------------------------------
    elif ders == "Fen Bilimleri":
        # 1. ÜNİTE
        if "1. alt kategori: güneş'in yapısı" in u_low:
            q = f"{kisi}'nin fen dersinde öğrendiğine göre Güneş'in yüzey sıcaklığı yaklaşık kaç °C'dir?"
            ans, celd = "6000 °C", ["15 Milyon °C", "1000 °C", "100 °C"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. alt kategori: ay'ın yapısı" in u_low:
            q = f"Ay'da neredeyse hiç atmosfer olmamasının temel sonucu aşağıdakilerden hangisidir?"
            ans = "Gece ve gündüz arasındaki sıcaklık farkının çok yüksek olması"
            celd = ["Ay'ın kendi etrafında dönmemesi", "Ay'da sürekli yağmur yağması", "Ay'ın ışık kaynağı olması"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. alt kategori: ay'ın evreleri" in u_low:
            evre = random.choice(["Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"])
            tanimlar = {
                "Yeni Ay": "Ay'ın Güneş ile Dünya arasında olduğu ve Dünya'dan bakıldığında karanlık göründüğü evre",
                "İlk Dördün": "Ay'ın Dünya'dan bakıldığında 'D' harfi şeklinde aydınlık göründüğü ana evre",
                "Dolunay": "Ay'ın dairesel ve tamamen aydınlık olarak göründüğü ana evre",
                "Son Dördün": "Ay'ın 'ters D' harfi şeklinde göründüğü ana evre"
            }
            q = f"<b>{tanimlar[evre]}</b> aşağıdakilerden hangisidir?"
            ans = evre
            celd = list({"Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"} - {evre})
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. alt kategori: güneş, dünya ve ay'ın hareketleri" in u_low:
            q = f"Dünya'nın kendi ekseni etrafındaki dönüşünü {kisi} kaç saatte tamamlar?"
            ans, celd = "24 Saat", ["365 Gün", "27 Gün", "12 Saat"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 2. ÜNİTE (CANLILAR)
        elif "1. alt kategori: mikroskobik" in u_low:
            q = f"Sütten yoğurt yapılmasını sağlayan mikroskobik canlı grubu aşağıdakilerden hangisidir?"
            ans, celd = "Yararlı Bakteriler", ["Zararlı Mantarlar", "Virüsler", "Amip"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. alt kategori: mantarlar" in u_low:
            q = f"Aşağıdakilerden hangisi kendi besinini üretemeyen ve mantarlar sınıfında yer alan bir canlıdır?"
            ans, celd = "Şapkalı Mantar", ["Eğrelti Otu", "Papatya", "Çam Ağacı"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. alt kategori: bitkiler" in u_low:
            q = f"Aşağıdakilerden hangisi <b>çiçeksiz bir bitkidir</b>?"
            ans, celd = "Eğrelti Otu", ["Gül", "Lale", "Elma Ağacı"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. alt kategori: hayvanlar" in u_low:
            q = f"Aşağıdaki canlılardan hangisi <b>omurgalı hayvanlar</b> sınıfında yer alır?"
            ans, celd = "Kedi", ["Sinek", "Ahtapot", "Salyangoz"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 3. ÜNİTE (KUUVET & SÜRTÜNME)
        elif "1. alt kategori: dinamometre" in u_low:
            a1 = random.randint(5, 50)
            q = f"Bir dinamometreye {a1} N ağırlığındaki bir cisim asıldığında yay kaç Newton kuvvet ölçer?"
            ans = f"{a1} N"
            celd = [f"{a1 * 10} N", f"{a1 + 5} N", f"{max(1, a1 - 2)} N"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. alt kategori: sürtünme kuvveti" in u_low:
            q = f"{kisi} bir oyuncak arabayı hareket ettirmek istiyor. Hangi yüzeyde <b>sürtünme kuvveti en fazladır</b>?"
            ans = "Halı Zemin"
            celd = ["Buzlu Zemin", "Cam Zemin", "Cilalı Tahta"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 4. ÜNİTE (MADDE VE DEĞİŞİM)
        elif "1. alt kategori: maddelerin hâl değişimi" in u_low:
            q = f"Sıvı bir maddenin ısı vererek katı hâle geçmesi olayına ne ad verilir?"
            ans, celd = "Donma", ["Erime", "Buharlaşma", "Süblimleşme"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. alt kategori: ısı ve sıcaklık" in u_low:
            q = f"Isı ve sıcaklık ile ilgili aşağıda verilen bilgilerden hangisi <b>doğrudur</b>?"
            ans = "Isı bir enerjidir, sıcaklık ise bir ölçümdür."
            celd = [
                "Sıcaklığın birimi Kalori'dir.",
                "Isı termometre ile ölçülür.",
                "Sıcaklık maddeler arasında alınıp verilen bir enerjidir."
            ]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        # 5. ÜNİTE (IŞIK VE GÖLGE)
        else:
            q = f"Aşağıdaki maddelerden hangisi <b>opak (ışığı geçirmeyen)</b> bir maddedir?"
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
# BENZERLİK FİLTRELEME & HASH PARMAK İZİ MOTORU
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

            # SHA-256 ile tam benzersiz parmak izi
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
            st.sidebar.error("⚠️ Lütfen en az 1 alt kategori veya ders seçin!")

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
        st.warning("⚠️ Lütfen sol menüden alt kategorileri seçiniz.")

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
