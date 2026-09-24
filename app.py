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
# 2. DERSLER VE MÜFREDAT YAPISI
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

MEB_HAFTALIK_MAPI = {}
for h in range(1, 41):
    MEB_HAFTALIK_MAPI[h] = []
    t_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Türkçe"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Türkçe", MEB_MUFREDAT["Türkçe"][t_idx]))

    m_idx = min((h - 1) // 7, len(MEB_MUFREDAT["Matematik"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Matematik", MEB_MUFREDAT["Matematik"][m_idx]))

    f_idx = min((h - 1) // 8, len(MEB_MUFREDAT["Fen Bilimleri"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Fen Bilimleri", MEB_MUFREDAT["Fen Bilimleri"][f_idx]))

    s_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Sosyal Bilgiler"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Sosyal Bilgiler", MEB_MUFREDAT["Sosyal Bilgiler"][s_idx]))

    d_idx = min((h - 1) // 13, len(MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Din Kültürü ve Ahlak Bilgisi", MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"][d_idx]))

    i_idx = min((h - 1) // 10, len(MEB_MUFREDAT["İngilizce"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("İngilizce", MEB_MUFREDAT["İngilizce"][i_idx]))

# =========================================================
# 3. GEOMETRİK VE AÇI GÖRSEL ÜRETİCİ (SVG)
# =========================================================
def svg_dinamik_ucgen_ciz(t_tip, gorunen_etiketler, koseler=("A", "B", "C")):
    if t_tip == "eskenar":
        p_top, p_left, p_right = "140, 15", "40, 115", "240, 115"
        dik_sembol = ""
    elif t_tip == "dik":
        p_top, p_left, p_right = "50, 20", "50, 110", "220, 110"
        dik_sembol = '<path d="M 50 95 L 65 95 L 65 110" fill="none" stroke="#ef4444" stroke-width="2"/>'
    elif t_tip == "ikizkenar":
        p_top, p_left, p_right = "140, 20", "60, 110", "220, 110"
        dik_sembol = ""
    elif t_tip == "genis":
        p_top, p_left, p_right = "180, 25", "30, 110", "230, 110"
        dik_sembol = ""
    else:
        p_top, p_left, p_right = "130, 20", "40, 110", "220, 110"
        dik_sembol = ""

    lbl0, lbl1, lbl2 = gorunen_etiketler

    return f'''
    <svg width="280" height="135" viewBox="0 0 280 135" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="8" stroke="#cbd5e1"/>
      <polygon points="{p_top} {p_left} {p_right}" fill="#eff6ff" stroke="#2563eb" stroke-width="3"/>
      {dik_sembol}
      <text x="140" y="16" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">{koseler[0]} ({lbl0})</text>
      <text x="35" y="125" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">{koseler[1]} ({lbl1})</text>
      <text x="235" y="125" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">{koseler[2]} ({lbl2})</text>
    </svg>
    '''

# =========================================================
# 4. SORU ÜRETME MOTORU (KESİN ÜNİTE SADAKATLİ & NET)
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem", "Onur", "Görkem", "Arda", "Defne", "Cem", "Melis", "Umut", "Naz"]
NESNELER = ["fındık", "bilye", "kitap", "kalem", "pul", "elma", "ceviz", "etiket", "sayfa", "çikolata", "kart", "balon"]
YEMEKLER = ["Mantı", "Çiğ Köfte", "Cağ Kebabı", "Tantuni", "Künefe", "Yağlama", "Baklava", "Kuru Fasulye", "İskender", "Lahmacun", "Pide"]
SEHIRLER = ["Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Trabzon", "Erzurum", "Gaziantep", "Konya", "Samsun", "Adana"]

def dinamik_soru_uretici(ders, unite):
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    nesne = random.choice(NESNELER)
    kisi2 = random.choice([i for i in ISIMLER if i != kisi])

    if ders == "Matematik":
        if "1. ünite" in u_low:
            alt_tip = random.choice(["okuma", "toplama_cikarma", "carpma_bolme", "yuvarlama", "oruntu"])
            if alt_tip == "okuma":
                sayi = random.randint(100000, 9999999)
                b_isimleri = ["yüz binler", "on binler", "binler", "yüzler", "onlar"]
                b_sec = random.choice(b_isimleri)
                carpan = {"yüz binler": 100000, "on binler": 10000, "binler": 1000, "yüzler": 100, "onlar": 10}[b_sec]
                b_deg = ((sayi // carpan) % 10) * carpan
                q = f"{kisi}'in yazdığı <b>{sayi}</b> sayısındaki {b_sec} basamağının basamak değeri kaçtır?"
                ans = str(b_deg)
                celd = [str(b_deg * 10 if b_deg > 0 else 100), str(max(10, b_deg // 10 if b_deg > 0 else 50)), str((sayi // (carpan if carpan > 0 else 1)) % 10 * 100)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            elif alt_tip == "toplama_cikarma":
                n1, n2 = random.randint(1200, 9800), random.randint(1100, 8900)
                ans = str(n1 + n2)
                q = f"{kisi}'in {n1} adet {nesne}si vardı. {kisi2} ona {n2} adet daha {nesne} verirse toplam kaç {nesne}si olur?"
                celd = [str(n1 + n2 + random.randint(10, 150)), str(abs(n1 + n2 - random.randint(20, 200))), str(n1 + n2 + random.randint(200, 500))]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            elif alt_tip == "carpma_bolme":
                n1, n2 = random.randint(15, 95), random.randint(12, 50)
                ans = str(n1 * n2)
                q = f"{kisi} her birinde {n1} adet {nesne} bulunan {n2} koli satın almıştır. Toplam kaç adet {nesne} vardır?"
                celd = [str(n1 * n2 + n1), str(n1 * n2 - n2), str((n1 + 5) * n2)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            elif alt_tip == "yuvarlama":
                sayi = random.randint(110, 990)
                ans = str(round(sayi, -1))
                q = f"<b>{sayi}</b> sayısı en yakın onluğa yuvarlandığında {kisi} hangi sonucu bulmalıdır?"
                celd = [str(int(ans) + 10), str(int(ans) - 10), str(sayi + random.choice([1, 2, 3]))]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            else:
                baslangic = random.randint(5, 20)
                artis = random.randint(3, 9)
                dizi = [baslangic + i * artis for i in range(4)]
                cevap = dizi[-1] + artis
                q = f"{kisi} sayı örüntüsü oluşturmuştur: **{dizi[0]}, {dizi[1]}, {dizi[2]}, {dizi[3]}, ?** Soru işaretli yere gelmesi gereken sayı kaçtır?"
                ans = str(cevap)
                celd = [str(cevap + artis), str(cevap - 2), str(cevap + 4)]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "2. ünite" in u_low:
            alt_tip = random.choice(["bilesik", "toplama_kesir"])
            if alt_tip == "bilesik":
                tam, payda = random.randint(1, 8), random.randint(4, 12)
                pay = random.randint(1, payda - 1)
                b_pay = tam * payda + pay
                q = f"<b>{tam} tam {pay}/{payda}</b> tam sayılı kesrinin bileşik kesre dönüştürülmüş hali hangisidir?"
                ans = f"{b_pay}/{payda}"
                celd = [f"{b_pay + random.randint(1, 3)}/{payda}", f"{b_pay - 1}/{payda}", f"{tam * pay}/{payda}"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
            else:
                payda = random.choice([8, 10, 12, 16])
                p1, p2 = random.randint(1, payda // 2), random.randint(1, payda // 2)
                top = p1 + p2
                q = f"{kisi} pastanın {p1}/{payda}'sini, {kisi2} ise aynı pastanın {p2}/{payda}'sini yemiştir. İkisi toplam pastanın ne kadarını yemiştir?"
                ans = f"{top}/{payda}"
                celd = [f"{top + 1}/{payda}", f"{max(1, top - 1)}/{payda}", f"{top}/{payda + 2}"]
                return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "3. ünite" in u_low:
            p = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
            fiyat = random.randint(120, 950)
            indirim = (fiyat * p) // 100
            ans = str(fiyat - indirim)
            q = f"{kisi} fiyatı {fiyat} TL olan ürünü <b>%{p}</b> indirimle aldığında kaç TL öder?"
            celd = [str(indirim), str(fiyat + indirim), str(fiyat - indirim + random.randint(5, 25))]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "4. ünite" in u_low:
            aci1 = random.choice([25, 35, 40, 45, 50, 55, 65])
            tip = random.choice(["tümler", "butunler"])
            if tip == "tümler":
                toplam = 90
                q = f"Komşu tümler iki açıdan biri {aci1}° olduğuna göre, <b>verilmeyen diğer açı kaç derecedir?</b> (İpucu: Tümler açıların toplamı 90°'dir.)"
            else:
                toplam = 180
                q = f"Komşu bütünler iki açıdan biri {aci1}° olduğuna göre, <b>verilmeyen diğer açı kaç derecedir?</b> (İpucu: Bütünler açıların toplamı 180°'dir.)"
            ans = f"{toplam - aci1}°"
            celd = [f"{toplam - aci1 + 10}°", f"{abs(toplam - aci1 - 15)}°", f"{aci1}°"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

        elif "5. ünite" in u_low:
            koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S"), ("D", "E", "F")])
            ucgen_tipi = random.choice(["eskenar", "ikizkenar", "dik", "genis"])
            if ucgen_tipi == "eskenar":
                gizlenen = random.choice(["a", "b", "c"])
                if gizlenen == "a":
                    q = f"Şekilde verilen eşkenar {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde <b>verilmeyen m({koseler[0]}) kaç derecedir?</b>"
                    ans, etiketler = "60°", ["?", "60°", "60°"]
                elif gizlenen == "b":
                    q = f"Şekilde verilen eşkenar {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde <b>verilmeyen m({koseler[1]}) kaç derecedir?</b>"
                    ans, etiketler = "60°", ["60°", "?", "60°"]
                else:
                    q = f"Şekilde verilen eşkenar {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde <b>verilmeyen m({koseler[2]}) kaç derecedir?</b>"
                    ans, etiketler = "60°", ["60°", "60°", "?"]
                celd = ["90°", "45°", "30°"]
                svg = svg_dinamik_ucgen_ciz("eskenar", etiketler, koseler)
            elif ucgen_tipi == "ikizkenar":
                taban_aci = random.choice([40, 50, 65, 70, 75])
                tepe_aci = 180 - (2 * taban_aci)
                gizlenen = random.choice(["tepe", "taban"])
                if gizlenen == "tepe":
                    q = f"Şekilde verilen ikizkenar {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde taban açılar eşit olduğuna göre <b>verilmeyen tepe açısı m({koseler[0]}) kaç derecedir?</b>"
                    ans, etiketler = f"{tepe_aci}°", ["?", f"{taban_aci}°", f"{taban_aci}°"]
                else:
                    q = f"Şekilde verilen ikizkenar {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde tepe açısı verildiğine göre <b>verilmeyen taban açısı m({koseler[1]}) kaç derecedir?</b>"
                    ans, etiketler = f"{taban_aci}°", [f"{tepe_aci}°", "?", f"{taban_aci}°"]
                celd = [f"{tepe_aci + 10}°", f"{abs(taban_aci - 15)}°", "90°"]
                svg = svg_dinamik_ucgen_ciz("ikizkenar", etiketler, koseler)
            elif ucgen_tipi == "dik":
                d_aci = random.choice([30, 40, 45, 50, 60])
                diger = 90 - d_aci
                q = f"Şekilde verilen dik {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[1]}) = 90° olduğuna göre <b>verilmeyen m({koseler[0]}) kaç derecedir?</b>"
                ans, etiketler = f"{diger}°", ["?", "90°", f"{d_aci}°"]
                celd = [f"{diger + 10}°", f"{abs(diger - 15)}°", "90°"]
                svg = svg_dinamik_ucgen_ciz("dik", etiketler, koseler)
            else:
                genis_aci = random.choice([100, 110, 120, 130])
                kalan = 180 - genis_aci
                dar1 = random.randint(20, kalan - 10)
                dar2 = kalan - dar1
                q = f"Şekilde verilen geniş açılı {koseler[0]}{koseler[1]}{koseler[2]} üçgeninde m({koseler[0]}) = {genis_aci}° olduğuna göre <b>verilmeyen m({koseler[2]}) kaç derecedir?</b>"
                ans, etiketler = f"{dar2}°", [f"{genis_aci}°", f"{dar1}°", "?"]
                celd = [f"{dar2 + 15}°", f"{abs(dar2 - 10)}°", f"{genis_aci - 30}°"]
                svg = svg_dinamik_ucgen_ciz("genis", etiketler, koseler)
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": svg}

        else:
            saat = random.randint(2, 8)
            dakika = random.choice([15, 30, 45, 0])
            toplam_dakika = saat * 60 + dakika
            q = f"{kisi} sinemada <b>{saat} saat {dakika} dakika</b> süren film izlemiştir. Toplam kaç dakikadır?" if dakika > 0 else f"{kisi} sinemada <b>{saat} saat</b> süren film izlemiştir. Süre kaç dakikadır?"
            ans = str(toplam_dakika)
            celd = [str(toplam_dakika + 30), str(toplam_dakika - 15), str(saat * 100)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Fen Bilimleri":
        if "1. ünite" in u_low:
            sub = random.choice(["gunes", "dunya", "ay"])
            if sub == "gunes":
                q = f"Güneş'in şekli küre şeklindedir ve katmanlardan oluşur. Güneş'in yüzey sıcaklığı yaklaşık kaç °C'dir?"
                ans, celd = "6000 °C", ["100 °C", "15 Milyon °C", "500 °C"]
            elif sub == "dunya":
                q = f"Dünya'mızın kendi ekseni etrafında dönme hareketi sonucunda ne oluşur?"
                ans, celd = "Gece ve gündüz", ["Yıllık mevsimler", "Ay'ın ana evreleri", "Güneş tutulması"]
            else:
                q = f"Ay'ın ana evrelerinden biri olan ve Dünya'dan bakıldığında karanlık göründüğü evre hangisidir?"
                ans, celd = "Yeni Ay", ["Dolunay", "İlk Dördün", "Son Dördün"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "2. ünite" in u_low:
            q = f"Sütten yoğurt yapılmasını sağlayan mikroskobik canlı grubu hangisidir?"
            ans, celd = "Yararlı Bakteriler", ["Virüsler", "Zararlı Mantarlar", "Amip"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "3. ünite" in u_low:
            a1 = random.randint(10, 90)
            q = f"Kuvveti ölçmek için kullanılan araç nedir ve {a1} N değerindeki cisim asıldığında yaydaki gösterge kaç N'yi gösterir?"
            ans, celd = f"Dinamometre ({a1} N)", [f"Termometre ({a1} N)", f"Dinamometre ({a1*2} N)", f"Barometre ({a1} N)"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "4. ünite" in u_low:
            q = f"Saf bir katı maddenin ısı alarak sıvı hale geçmesi olayına ne denir?"
            ans, celd = "Erime", ["Donma", "Buharlaşma", "Yoğuşma"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        else:
            q = f"Aşağıdaki maddelerden hangisi ışığı kesinlikle geçirmeyen <b>opak maddedir</b>?"
            ans, celd = "Tahta Parçası", ["Pencere Camı", "Şeffaf Poşet", "Temiz Su"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Türkçe":
        if "1. tema" in u_low:
            q = f"Paragrafta geçen 'Mektep' sözcüğünün eş anlamlısı aşağıdakilerden hangisidir?"
            ans, celd = "Okul", ["Öğretmen", "Kitap", "Sınıf"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "2. tema" in u_low:
            q = f"Aşağıdaki cümlelerin hangisinde bir sebep-sonuç (neden-sonuç) ilişkisi vardır?"
            ans, celd = "Yağmur yağdığı için maç ertelendi.", ["Yarın parka gideceğiz.", "Kitap okumayı çok severim.", "Elma ve armut aldım."]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "3. tema" in u_low:
            q = f"Bir metnin ana düşüncesi (ana fikri) aşağıdakilerden hangisini ifade eder?"
            ans, celd = "Yazarın okuyucuya vermek istediği temel mesajı", ["Metnin kaç kelimeden oluştuğunu", "Kullanılan noktalama işaretlerini", "Hikayedeki karakterlerin yaşını"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        else:
            q = f"Aşağıdaki sözcüklerden hangisinin yazımı <b>yanlıştır</b>?"
            ans, celd = "herkez", ["herkes", "yalnız", "itiraf"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Sosyal Bilgiler":
        if "1. ünite" in u_low:
            q = f"{kisi} gün içinde evde üzerine düşen görevleri yapmaktadır. Hangisi {kisi}'in evdeki bir <b>sorumluluğudur</b>?"
            ans, celd = "Kendi odasını düzenli tutmak", ["Televizyon kumandasını saklamak", "Sürekli dışarıda oynamak", "Oda kapısını kilitlemek"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "2. ünite" in u_low:
            q = f"Milli kültürümüzü yansıtan geleneksel el sanatlarımızdan biri hangisidir?"
            ans, celd = "Ebru Sanatı", ["Futbol oynamak", "Tenis", "Bilgisayar kodlamak"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "3. ünite" in u_low:
            q = f"Aşağıdakilerden hangisi ülkemiz sınırları içinde yer alan <b>doğal varlıklarımızdandır</b>?"
            ans, celd = "Pamukkale Travertenleri", ["Topkapı Sarayı", "Sultanahmet Camii", "Anıtkabir"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        else:
            q = f"Teknolojik ürünleri bilinçli ve güvenli kullanmak için aşağıdakilerden hangisi yapılmalıdır?"
            ans, celd = "Kişisel bilgileri internette kimseyle paylaşmamak", ["Şifreyi herkese söylemek", "Sabaha kadar oyun oynamak", "Tanımayanlarla buluşmak"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        if "1. ünite" in u_low:
            q = f"Evrendeki düzen, intizam ve uyum hangi yüce yaratıcının varlığını ve birliğini kanıtlar?"
            ans, celd = "Allah (c.c.)", ["Doğa olayları", "Rastlantılar", "Gezegenler"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "2. ünite" in u_low:
            q = f"Ramazan ayında tutulan ve farz olan ibadetin adı nedir?"
            ans, celd = "Oruç", ["Zekat", "Hac", "Kurban"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        else:
            q = f"Büyüklere saygı göstermek ve küçükleri sevmek hangi ahlaki kavramla ifade edilir?"
            ans, celd = "Adap ve Nezaket", ["İnatçılık", "Bencillik", "Kıskançlık"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "İngilizce":
        if "unit 1" in u_low:
            q = f"{kisi} tanıştığı arkadaşına ülkesini sormak için hangi cümleyi kurmalıdır?"
            ans, celd = "Where are you from?", ["How old are you?", "What is your name?", "How are you?"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "unit 2" in u_low:
            q = f"İngilizcede 'Sola dön' komutunun karşılığı hangisidir?"
            ans, celd = "Turn left", ["Turn right", "Go straight", "Stop"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "unit 3" in u_low:
            q = f"I like playing chess and painting cümlesinde hangi etkinlikten <b>bahsedilmemiştir</b>?"
            ans, celd = "Yüzmek (Swimming)", ["Satranç oynamak", "Resim yapmak", "İkisi de"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        else:
            q = f"Sabah uyanma eylemini ifade eden İngilizce kalıp hangisidir?"
            ans, celd = "Get up", ["Go to bed", "Have dinner", "Do homework"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    else: # Bilgi Yarışması
        if "1. kategori" in u_low:
            q = f"Fransa'nın başkenti olan dünya şehri hangisidir?"
            ans, celd = "Paris", ["Londra", "Roma", "Madrid"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "2. kategori" in u_low:
            sehir_yemek = random.choice(list(zip(SEHIRLER, YEMEKLER)))
            q = f"Ülkemizin eşsiz lezzetlerinden biri olan <b>{sehir_yemek[1]}</b> hangi yöremiz/ilimizle özdeşleşmiştir?"
            ans = sehir_yemek[0]
            celd = [s for s in SEHIRLER if s != ans][:3]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "3. kategori" in u_low:
            q = f"Dünyanın en uzun nehirlerinden biri olarak bilinen Nil Nehri hangi kıtada yer alır?"
            ans, celd = "Afrika", ["Asya", "Avrupa", "Amerika"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        else:
            q = f"Türkiye Cumhuriyeti'nin başkenti neresidir?"
            ans, celd = "Ankara", ["İstanbul", "İzmir", "Bursa"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

# =========================================================
# 5. SIKİ SEÇİM SADAKATLİ SORU ÜRETME MOTORU
# =========================================================
def ders_sirali_soru_uret(secilen_uniteler, hedef_sayi):
    if not secilen_uniteler:
        return []

    ders_gruplari = {}
    for ders, unite in secilen_uniteler:
        ders_gruplari.setdefault(ders, []).append(unite)

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
        while uretilen_sayi < dersin_hedef_sayisi and deneme < 1000:
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
# 6. STREAMLIT ARAYÜZÜ (HİÇBİR ŞEY ÖNCEDEN SEÇİLİ DEĞİL)
# =========================================================
st.title("🎓 MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru")

st.sidebar.header("⚙️ Müfredat ve Sınav Ayarları")

is_disabled = st.session_state["test_aktif"] or st.session_state["sorular_hazir"]

# Çalışma Modu Seçiniz Alanı (Bilgi Yarışması hemen altında)
with st.sidebar.expander("📌 Çalışma Modu Seçiniz", expanded=True):
    mod_deneme = st.checkbox("📅 40 Haftalık MEB Deneme Sınavları", value=False, disabled=is_disabled, key="mod_deneme_cb")
    mod_serbest = st.checkbox("📚 Serbest Konu / Ünite Seçimi", value=False, disabled=is_disabled, key="mod_serbest_cb")
    mod_bilgi = st.checkbox("🏆 Bilgi Yarışması Modu", value=False, disabled=is_disabled, key="mod_bilgi_cb")

secilen_uniteler = []

if mod_deneme:
    with st.sidebar.expander("📅 40 Haftalık MEB Deneme Sınavları", expanded=True):
        deneme_secimleri = []
        for h in range(1, 41):
            cb_hafta = st.checkbox(f"{h}. Hafta Deneme Sınavı", value=False, disabled=is_disabled, key=f"deneme_cb_{h}")
            if cb_hafta:
                deneme_secimleri.append(h)
        
        for h in deneme_secimleri:
            for k in range(1, h + 1):
                secilen_uniteler.extend(MEB_HAFTALIK_MAPI[k])

if mod_serbest:
    st.sidebar.subheader("📚 Ünite Seçimi")
    for ders_adi in DERS_ONCELIK_SIRASI[:-1]: # Bilgi yarışmasını ayrı tuttuk
        uniteler = MEB_MUFREDAT[ders_adi]
        with st.sidebar.expander(f"{ders_adi}", expanded=False):
            select_all = st.checkbox(f"Tümünü Seç", value=False, key=f"all_{ders_adi}", disabled=is_disabled)
            for idx, u in enumerate(uniteler):
                cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=is_disabled)
                if cb:
                    secilen_uniteler.append((ders_adi, u))

if mod_bilgi:
    with st.sidebar.expander("🏆 Bilgi Yarışması Kategorileri", expanded=True):
        select_all_bilgi = st.checkbox("Tüm Bilgi Yarışması Kategorilerini Seç", value=False, key="all_Bilgi_Yarismasi", disabled=is_disabled)
        for idx, u in enumerate(MEB_MUFREDAT["🏆 Bilgi Yarışması"]):
            cb = st.checkbox(u, value=select_all_bilgi, key=f"cb_Bilgi_Yarismasi_{idx}", disabled=is_disabled)
            if cb:
                secilen_uniteler.append(("🏆 Bilgi Yarışması", u))

st.sidebar.divider()

soru_sayisi = st.sidebar.number_input(
    "Toplam Soru Sayısı (10-100):", 
    min_value=10, 
    max_value=100, 
    value=20, 
    step=5, 
    disabled=is_disabled
)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Hazırla ve Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            with st.spinner("Seçtiğiniz kriterlere göre benzersiz sorular üretiliyor..."):
                sorular = ders_sirali_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen sol menüden en az bir mod ve ünite seçimi yapın!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Hazırla", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.rerun()

# --- EKRAN AKIŞI ---
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Sınav Başlatma Alanı")
    st.info("Sol paneldeki **'Çalışma Modu Seçiniz'** alanından dilediğiniz modu seçip üniteleri işaretledikten sonra **'Hazırla ve Başlat'** butonuna tıklayın.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Seçtiğiniz Kriterlere Uygun Sorular Hazırlandı!")
    st.markdown(f"**Toplam Soru Sayısı:** {len(st.session_state['soru_listesi'])}")
    
    ders_sayilari = {}
    for s in st.session_state['soru_listesi']:
        ders_sayilari[s['ders']] = ders_sayilari.get(s['ders'], 0) + 1
    
    st.markdown("##### 📌 Sınav Ders Dağılımı:")
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
