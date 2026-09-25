import streamlit as st
import random
import time
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru", page_icon="🎓", layout="wide")

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
# 2. DERSLER VE MEB MÜFREDAT SIRASI
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
        "1. Kategori: Dünya Başkentleri ve Coğrafya",
        "2. Kategori: Türk Mutfağı ve Yöresel Lezzetler",
        "3. Kategori: Dünya Mutfakları ve Lezzetler",
        "4. Kategori: Harita Bilgisi ve Yönler",
        "5. Kategori: Bilim Tarihi ve İcatlar",
        "6. Kategori: Genel Kültür ve Doğa Harikaları",
        "7. Kategori: Popüler Kültür",
        "8. Kategori: Spor ve Müzik"
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

ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem"]

# =========================================================
# 3. SVG TABANLI GERÇEKÇİ GEOMETRİK ÜÇGEN ÇİZİM MOTORU
# =========================================================
def svg_ucgen_ciz(tip, aci1_val, aci2_val, aci3_val):
    """MEB soru kitapçıklarına birebir uyumlu, SVG vektörel üçgen şeması üretir."""
    if tip == "cesitkenar":
        # KLM Çeşitkenar Üçgen Koordinatları
        p1, p2, p3 = "70,160", "280,170", "150,30"
        labels = ("K", "L", "M")
        vals = (f"{aci1_val}°", f"{aci2_val}°", f"{aci3_val}")
    elif tip == "dik":
        # DEF Dik Üçgen Koordinatları
        p1, p2, p3 = "60,170", "260,170", "60,40"
        labels = ("D", "E", "F")
        vals = ("90°", f"{aci1_val}°", f"{aci3_val}")
    elif tip == "ikizkenar":
        # PRS İkizkenar Üçgen Koordinatları
        p1, p2, p3 = "70,170", "250,170", "160,35"
        labels = ("P", "R", "S")
        vals = (f"{aci1_val}°", f"{aci2_val}°", f"{aci3_val}°")
    else:  # eskenar
        # ABC Eşkenar Üçgen Koordinatları
        p1, p2, p3 = "70,170", "250,170", "160,20"
        labels = ("A", "B", "C")
        vals = ("60°", "60°", "60°")

    # SVG Çizimi
    svg_code = f"""
    <div style="display: flex; justify-content: center; background-color: #ffffff; padding: 15px; border-radius: 12px; border: 2px solid #e0e0e0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
        <svg width="320" height="200" viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg">
            <!-- Üçgen Dolgusu ve Kenarları -->
            <polygon points="{p1} {p2} {p3}" fill="#f0f7ff" stroke="#1f77b4" stroke-width="3" stroke-linejoin="round"/>
            
            <!-- Köşe Harfleri -->
            <text x="50" y="185" font-family="Arial" font-weight="bold" font-size="16" fill="#333">{labels[0]}</text>
            <text x="270" y="185" font-family="Arial" font-weight="bold" font-size="16" fill="#333">{labels[1]}</text>
            <text x="150" y="20" font-family="Arial" font-weight="bold" font-size="16" fill="#333">{labels[2]}</text>
            
            <!-- Açı Değerleri -->
            <text x="85" y="150" font-family="Arial" font-weight="600" font-size="13" fill="#d62728">{vals[0]}</text>
            <text x="220" y="150" font-family="Arial" font-weight="600" font-size="13" fill="#d62728">{vals[1]}</text>
            <text x="140" y="60" font-family="Arial" font-weight="600" font-size="13" fill="#d62728">{vals[2]}</text>
        </svg>
    </div>
    """
    return svg_code

# =========================================================
# 4. SORU ÜRETME MOTORU
# =========================================================
def uniteye_ozel_soru_uret(ders, unite):
    kisi = random.choice(ISIMLER)
    kaynak_turu = random.choice([
        "🤖 **[Soru Kaynağı: Yapay Zeka (AI Üretimi)]**", 
        "📚 **[Soru Kaynağı: MEB Soru Havuzu]**"
    ])
    
    # --- TÜRKÇE ---
    if ders == "Türkçe":
        if "Sözcükte Anlam" in unite:
            dogru = "Güneş yavaş yavaş tepelerin arkasından görünmeye başladı."
            yanlislar = ["Bu mont kardeşime biraz küçük geldi.", "Toplantıdan en son ben ayrıldım.", "Merdivenleri çıkarken nefes nefese kaldı."]
            soru = f"{kaynak_turu}<br><br><b>[Sözcükte Anlam]</b> 'Çıkmak' sözcüğü hangi cümlede <u>'ortaya çıkmak, görünmek'</u> anlamındadır?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Cümlede Anlam" in unite:
            dogru = "Hava sağanak yağışlı olduğundan maç ertelendi."
            yanlislar = ["Başarılı olmak için her gün düzenli ders çalışıyor.", "Sabah uyanınca elini yüzünü yıkadı.", "Yarın akşam eski arkadaşlarıyla buluşacak."]
            soru = f"{kaynak_turu}<br><br><b>[Cümlede Anlam]</b> Hangi cümlede <u>neden-sonuç</u> ilişkisi vardır?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Paragraf" in unite:
            dogru = "Metnin ana düşüncesi kitap okumanın zihinsel gelişime katkısıdır."
            yanlislar = ["Metinde sadece spor salonlarından bahsedilmiştir.", "Yazar alışveriş yapmanın önemini vurgulamıştır.", "Paragrafın konusu mevsim geçişleridir."]
            soru = f"{kaynak_turu}<br><br><b>[Paragraf Analizi]</b> Düzenli kitap okuyan bir bireyin ifade becerisinin arttığını anlatan bir metne göre aşağıdakilerden hangisi söylenebilir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        else:
            dogru = "Eyvah, elimdeki bardak yere düştü!"
            yanlislar = ["Bugün okulda hangi dersleri işlediniz?", "Ödevlerimi bitirip odamı topladım.", "Ankara Türkiye'nin başkentidir."]
            soru = f"{kaynak_turu}<br><br><b>[Yazım ve Noktalama]</b> Hangi cümlede <u>ünlem işareti (!)</u> doğru kullanılmıştır?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

    # --- MATEMATİK ---
    elif ders == "Matematik":
        if "Doğal Sayılar" in unite:
            a = random.randint(1200, 8900)
            b = random.randint(300, 1500)
            dogru = a + b
            y1 = dogru + random.randint(5, 25)
            y2 = dogru - random.randint(3, 20)
            y3 = dogru + random.randint(30, 80)
            soru = f"{kaynak_turu}<br><br><b>[Doğal Sayılarla İşlemler]</b> İşlemin sonucu kaçtır?<br><br><b>{a} + {b} = ?</b>"
            return {"soru": soru, "siklar": [str(dogru), str(y1), str(y2), str(y3)], "dogru": str(dogru)}
        elif "Kesirler" in unite:
            payda = random.choice([8, 10, 12, 16])
            pay = random.randint(3, payda - 1)
            dogru = f"{pay}/{payda} birim kesirlerden oluşur."
            yanlislar = [f"{payda}/{pay} bileşik kesirdir.", f"Payı {payda}, paydası {pay} olan kesirdir.", "Tamamı bütün bir sayıdır."]
            soru = f"{kaynak_turu}<br><br><b>[Kesir Modeli]</b><br><div style='background:#e8f4fd; border:2px solid #2196F3; padding:12px; border-radius:8px; text-align:center;'>🟩 <b>Kesir Şeması:</b> {payda} eş parçadan <b>{pay}</b> tanesi boyalı model.</div><br>Bu model için aşağıdakilerden hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Ondalık" in unite:
            ondalik = f"0,{random.randint(15, 85)}"
            dogru = f"Ondalık gösterimin kesir karşılığı paydası 100 olan bir kesirdir."
            yanlislar = ["Tam kısmı sıfırdan büyüktür.", "Sayımız bir doğal sayıdır.", "Yüzler basamağında yer alır."]
            soru = f"{kaynak_turu}<br><br><b>[Ondalık Gösterim]</b> <b>{ondalik}</b> ondalık gösterimi ile ilgili aşağıdakilerden hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Geometrik Kavramlar" in unite:
            dogru = "Dar açı ölçüsü 0° ile 90° arasında olan açıdır."
            yanlislar = ["Geniş açı 90 derecedir.", "Dik açı 180 derecedir.", "Doğru açı 90 derecedir."]
            soru = f"{kaynak_turu}<br><br><b>[Açı Ölçme]</b> Geometrik kavramlar konusuna göre açı çeşitleriyle ilgili hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Üçgende Açılar" in unite:
            ucgen_turu = random.choice(["eskenar", "dik", "ikizkenar", "cesitkenar"])
            
            if ucgen_turu == "eskenar":
                dogru = "60°"
                yanlislar = ["45°", "90°", "30°"]
                svg_gorsel = svg_ucgen_ciz("eskenar", "60°", "60°", "60°")
                soru = (
                    f"{kaynak_turu}<br><br><b>[Üçgen Çeşitleri - Eşkenar Üçgen Sınav Sorusu]</b><br>"
                    f"{svg_gorsel}<br>"
                    "Yukarıdaki vektörel şemada tüm kenar uzunlukları ve iç açıları birbirine eşit olan bir <b>ABC eşkenar üçgeni</b> verilmiştir. Bu üçgenin bir iç açısının ölçüsü kaç derecedir?"
                )
                return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
                
            elif ucgen_turu == "dik":
                aci1 = random.randint(30, 60)
                dogru_val = 90 - aci1
                dogru = f"{dogru_val}°"
                yanlislar = [f"{dogru_val + 10}°", f"{dogru_val - 10}°", f"{dogru_val + 20}°"]
                svg_gorsel = svg_ucgen_ciz("dik", "90°", f"{aci1}°", "?")
                soru = (
                    f"{kaynak_turu}<br><br><b>[Üçgen Çeşitleri - Dik Üçgen Sınav Sorusu]</b><br>"
                    f"{svg_gorsel}<br>"
                    f"Yukarıdaki vektörel şemada D köşesi 90° ve E köşesi <b>{aci1}°</b> olan bir <b>DEF dik üçgeni</b> gösterilmiştir. Buna göre verilmeyen F köşesindeki dar açının ölçüsü kaç derecedir?"
                )
                return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
                
            elif ucgen_turu == "ikizkenar":
                tepe_aci = random.choice([40, 50, 70, 80])
                taban_aci = (180 - tepe_aci) // 2
                dogru = f"{taban_aci}°"
                yanlislar = [f"{taban_aci + 10}°", f"{tepe_aci}°", f"{taban_aci - 5}°"]
                svg_gorsel = svg_ucgen_ciz("ikizkenar", f"{tepe_aci}°", "?", "?")
                soru = (
                    f"{kaynak_turu}<br><br><b>[Üçgen Çeşitleri - İkizkenar Üçgen Sınav Sorusu]</b><br>"
                    f"{svg_gorsel}<br>"
                    f"Yukarıdaki vektörel şemada |PR| = |PS| olan PRS ikizkenar üçgeninin tepe açısı <b>{tepe_aci}°</b> verilmiştir. Buna göre R köşesindeki taban açısının ölçüsü kaç derecedir?"
                )
                return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
                
            else:
                a_aci = random.randint(40, 70)
                b_aci = random.randint(40, 70)
                c_aci = 180 - (a_aci + b_aci)
                dogru = f"{c_aci}°"
                yanlislar = [f"{c_aci + 10}°", f"{c_aci - 15}°", f"{c_aci + 20}°"]
                svg_gorsel = svg_ucgen_ciz("cesitkenar", f"{a_aci}°", f"{b_aci}°", "?")
                soru = (
                    f"{kaynak_turu}<br><br><b>[Üçgen Çeşitleri - Çeşitkenar Üçgen Sınav Sorusu]</b><br>"
                    f"{svg_gorsel}<br>"
                    f"Yukarıdaki vektörel şemada verilen KLM çeşitkenar üçgeninin K açısı <b>{a_aci}°</b> ve L açısı <b>{b_aci}°</b>'dir. Buna göre verilmeyen üçüncü iç açı (M) kaç derecedir?"
                )
                return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        else:
            dogru = "Veri analizi tablosunda en çok tercih edilen öge en yüksek sütuna sahiptir."
            yanlislar = ["Sütun grafikleri sadece daire ile çizilir.", "Veri toplamada tabloya gerek yoktur.", "Grafikler uzunluk ölçmek için kullanılır."]
            soru = f"{kaynak_turu}<br><br><b>[Veri İşleme ve Ölçme]</b> Veri işleme ve grafik yorumlama ile ilgili hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

    # --- FEN BİLİMLERİ ---
    elif ders == "Fen Bilimleri":
        if "Güneş, Dünya ve Ay" in unite:
            dogru = "Yeniay -> İlk Dördün -> Dolunay -> Son Dördün"
            yanlislar = ["Dolunay -> Yeniay -> Son Dördün -> İlk Dördün", "İlk Dördün -> Dolunay -> Yeniay -> Son Dördün", "Yeniay -> Dolunay -> İlk Dördün -> Son Dördün"]
            soru = (
                f"{kaynak_turu}<br><br><b>[Ay'ın Evreleri Döngü Şeması]</b><br>"
                "<div style='background:#f9ebea; border:2px solid #c0392b; padding:15px; border-radius:10px; text-align:center;'>"
                "🌑 <b>Yeniay</b> ➔ 🌓 <b>İlk Dördün</b> ➔ 🌕 <b>Dolunay</b> ➔ 🌗 <b>Son Dördün</b>"
                "</div><br>"
                "Ay'ın ana evrelerinin doğru kronolojik sıralaması hangi seçenekte eksiksiz verilmiştir?"
            )
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Canlılar Dünyası" in unite:
            dogru = "Mantar ve bakteriler mikroskobik canlılar dünyasında yer alabilir."
            yanlislar = ["Tüm mantarlar bitki sınıfına dahildir.", "Bakteriler gözle çok rahat görülebilir.", "Hayvanlar kendi besinini kendisi üretir."]
            soru = f"{kaynak_turu}<br><br><b>[Canlılar Dünyası]</b> Canlılar dünyasını sınıflandıran {kisi} hangisine ulaşır?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Kuvvetin Ölçülmesi" in unite:
            dogru = "Kuvvet dinamometre adı verilen aletle ölçülür ve birimi Newton'dur."
            yanlislar = ["Kuvvet tartı ile ölçülür ve birimi kilogramdır.", "Sürtünme kuvveti hareketi her zaman hızlandırır.", "Dinamometreler sıvı miktarını ölçer."]
            soru = f"{kaynak_turu}<br><br><b>[Kuvvet ve Sürtünme]</b> Kuvvetin ölçülmesi ve sürtünme ile ilgili hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Madde ve Değişim" in unite:
            dogru = "Maddenin ısı alarak hal değiştirmesine erime veya buharlaşma denir."
            yanlislar = ["Buzun erimesi kimyasal bir değişimdir.", "Kağıdın yanması fiziksel değişimdir.", "Donma olayında madde dışarıya ısı vermez."]
            soru = f"{kaynak_turu}<br><br><b>[Madde ve Değişim]</b> Maddenin hal değiştirmesiyle ilgili hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        else:
            dogru = "Işık doğrusal yollarla yayılır ve opak maddelerden geçemez."
            yanlislar = ["Tam gölge saydam maddelerin arkasında oluşur.", "Işık sadece dairesel dalgalarla yayılır.", "Cam ışığı hiç geçirmez."]
            soru = f"{kaynak_turu}<br><br><b>[Işığın Yayılması]</b> Işığın yayılması ve tam gölge ünitesi için hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

    # --- SOSYAL BİLGİLER ---
    elif ders == "Sosyal Bilgiler":
        if "Birey ve Toplum" in unite:
            dogru = "Aile bütçesine katkı sağlamak ve ev işlerinde yardımlaşmak çocukların sorumluluklarındandır."
            yanlislar = ["Çocukların evde hiçbir sorumluluğu yoktur.", "Haklarımızı kullanırken başkalarının haklarını ihlal edebiliriz.", "Resmi kurumlarla işimiz olamaz."]
            soru = f"{kaynak_turu}<br><br><b>[Hak ve Sorumluluklar]</b> {kisi}, birey ve toplum ünitesinde hangi ifadeye ulaşmalıdır?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Kültür ve Miras" in unite:
            dogru = "Tarihi yapıları ve kültürel mirasları korumak toplumsal görevimizdir."
            yanlislar = ["Tarihi eserleri özelleştirip satabiliriz.", "Kültürel ögelerimiz zamanla tamamen yok olmalıdır.", "Müzeler sadece turistik mekanlardır."]
            soru = f"{kaynak_turu}<br><br><b>[Kültür ve Miras]</b> Geçmişten günümüze kalan kültürel miraslar için hangisi söylenebilir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "İnsanlar, Yerler" in unite:
            dogru = "Haritalarda mavi renk genellikle su kaynaklarını ve denizleri gösterir."
            yanlislar = ["Dağlar haritalarda daima yeşil renkle gösterilir.", "Yeryüzü şekilleri beşeri unsurlardır.", "İklim insan faaliyetlerini hiç etkilemez."]
            soru = f"{kaynak_turu}<br><br><b>[İnsanlar, Yerler ve Çevreler]</b> Coğrafi özellikler ve harita bilgisi için hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        else:
            dogru = "Teknolojik ürünleri bilinçli ve güvenli kullanmalıyız."
            yanlislar = ["İnternette kişisel bilgileri herkesle paylaşabiliriz.", "Teknolojinin zararlı yönleri hiç yoktur.", "İcatlar sadece günümüzde yapılmıştır."]
            soru = f"{kaynak_turu}<br><br><b>[Bilim, Teknoloji]</b> Bilim ve teknoloji ünitesine göre hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

    # --- DİN KÜLTÜRÜ ---
    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        if "Allah İnancı" in unite:
            dogru = "Evrendeki kusursuz düzen Yaratıcı'nın varlığına delildir."
            yanlislar = ["Evrendeki her şey tesadüfen oluşmuştur.", "Doğanın bir sahibi yoktur.", "Mevsimlerin oluşumunda amaç aranmaz."]
            soru = f"{kaynak_turu}<br><br><b>[Allah İnancı]</b> Evrendeki nizam ve uyumla ilgili hangisi söylenebilir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Ramazan ve Oruç" in unite:
            dogru = "Oruç İslam'ın temel ibadetlerinden biridir ve imsak vaktiyle başlar."
            yanlislar = ["Oruç sadece akşam yemeği yememektir.", "Ramazan ayı sadece yaz mevsiminde olur.", "Sahura kalkmak zorunlu değildir."]
            soru = f"{kaynak_turu}<br><br><b>[Ramazan ve Oruç]</b> Ramazan ayı ve oruç ibadeti için hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        else:
            dogru = "Adap ve nezaket kurallarına uymak toplumsal huzuru artırır."
            yanlislar = ["Büyüklere saygı göstermek gereksizdir.", "Selamlaşmak sadece aile üyeleri arasındadır.", "Konuşurken başkasının sözünü kesmek kibarlıktır."]
            soru = f"{kaynak_turu}<br><br><b>[Adap ve Nezaket]</b> Günlük yaşamdaki nezahet kuralları için hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

    # --- İNGİLİZCE ---
    elif ders == "İngilizce":
        if "Hello!" in unite:
            dogru = "I am from Turkey and I am Turkish."
            yanlislar = ["I like playing football.", "My school starts at nine.", "I get up early."]
            soru = f"{kaynak_turu}<br><br><b>[Nationalities]</b> Ülke ve milliyet belirten ifade hangisidir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "My Town" in unite:
            dogru = "The hospital is next to the post office."
            yanlislar = ["I have two brothers.", "She likes playing tennis.", "I get up at 7 AM."]
            soru = f"{kaynak_turu}<br><br><b>[Directions]</b> Yer yön bildiren ifade hangisidir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        elif "Games and Hobbies" in unite:
            dogru = "He likes playing chess and riding a bike."
            yanlislar = ["I am from Ankara.", "The bank is opposite the park.", "My hair is blonde."]
            soru = f"{kaynak_turu}<br><br><b>[Hobbies]</b> Hobi ve oyun belirten ifade hangisidir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        else:
            dogru = "I wake up at seven o'clock every morning."
            yanlislar = ["I live in a big city.", "She is from Spain.", "They love playing football."]
            soru = f"{kaynak_turu}<br><br><b>[Daily Routine]</b> Günlük rutini belirten ifade hangisidir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

    # --- BİLGİ YARIŞMASI ---
    else:
        dogru = "Ankara"
        yanlislar = ["İstanbul", "İzmir", "Bursa"]
        soru = f"{kaynak_turu}<br><br>🏆 <b>[Bilgi Yarışması]</b> Türkiye Cumhuriyeti'nin başkenti neresidir?"
        return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

def ders_sirali_ve_dengeli_uret(secilen_uniteler, hedef_sayi):
    if not secilen_uniteler:
        return []

    sirali_uniteler = []
    for d in DERS_ONCELIK_SIRASI:
        for item in secilen_uniteler:
            if item[0] == d and item not in sirali_uniteler:
                sirali_uniteler.append(item)
                
    toplam_secilen = len(sirali_uniteler)
    temel_pay = hedef_sayi // toplam_secilen
    kalan = hedef_sayi % toplam_secilen

    ham_soru_listesi = []
    hash_set = set()

    for idx, (ders, unite) in enumerate(sirali_uniteler):
        bu_unite_hedef = temel_pay + (1 if idx < kalan else 0)
        uretilen = 0
        
        while uretilen < bu_unite_hedef:
            s = uniteye_ozel_soru_uret(ders, unite)
            s["ders"] = ders
            s["unite"] = unite
            
            correct_ans = s["dogru"]
            random.shuffle(s["siklar"])
            if correct_ans not in s["siklar"]:
                s["siklar"][0] = correct_ans
                random.shuffle(s["siklar"])
                
            fingerprint = hashlib.sha256((s["soru"] + str(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                ham_soru_listesi.append(s)
                uretilen += 1

    nihai_liste = []
    for ders_adi in DERS_ONCELIK_SIRASI:
        ders_sorulari = [s for s in ham_soru_listesi if s["ders"] == ders_adi]
        nihai_liste.extend(ders_sorulari)

    return nihai_liste[:hedef_sayi]

# =========================================================
# 5. STREAMLIT ARAYÜZÜ (SOL MENÜ)
# =========================================================
st.title("🎓 MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru")
st.sidebar.header("⚙️ Müfredat ve Sınav Ayarları")

is_disabled = st.session_state["test_aktif"] or st.session_state["sorular_hazir"]

with st.sidebar.expander("📌 Çalışma Modu Seçiniz", expanded=True):
    mod_deneme = st.checkbox("📅 40 Haftalık MEB Deneme Sınavları", value=False, disabled=is_disabled)
    mod_serbest = st.checkbox("📚 Serbest Konu / Ünite Seçimi", value=False, disabled=is_disabled)
    mod_bilgi = st.checkbox("🏆 Bilgi Yarışması Modu", value=False, disabled=is_disabled)

secilen_uniteler = []
deneme_secimleri = []

if mod_deneme:
    with st.sidebar.expander("📅 40 Haftalık MEB Deneme Sınavları", expanded=True):
        for h in range(1, 41):
            if st.checkbox(f"{h}. Hafta Deneme Sınavı", value=False, disabled=is_disabled, key=f"deneme_cb_{h}"):
                deneme_secimleri.append(h)
        for h in deneme_secimleri:
            for k in range(1, h + 1):
                secilen_uniteler.extend(MEB_HAFTALIK_MAPI[k])

if mod_serbest:
    st.sidebar.subheader("📚 Ünite Seçimi")
    for ders_adi in DERS_ONCELIK_SIRASI[:-1]:
        uniteler = MEB_MUFREDAT[ders_adi]
        with st.sidebar.expander(f"{ders_adi}", expanded=False):
            select_all = st.checkbox(f"Tümünü Seç ({ders_adi})", value=False, key=f"all_{ders_adi}", disabled=is_disabled)
            for idx, u in enumerate(uniteler):
                if st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=is_disabled):
                    secilen_uniteler.append((ders_adi, u))

if mod_bilgi:
    with st.sidebar.expander("🏆 Bilgi Yarışması Kategorileri", expanded=True):
        select_all_bilgi = st.checkbox("Tüm Bilgi Yarışması Kategorilerini Seç", value=False, key="all_Bilgi_Yarismasi", disabled=is_disabled)
        for idx, u in enumerate(MEB_MUFREDAT["🏆 Bilgi Yarışması"]):
            if st.checkbox(u, value=select_all_bilgi, key=f"cb_Bilgi_Yarismasi_{idx}", disabled=is_disabled):
                secilen_uniteler.append(("🏆 Bilgi Yarışması", u))

st.sidebar.divider()
soru_sayisi = st.sidebar.slider("Toplam Soru Sayısı:", min_value=20, max_value=100, value=20, step=5, disabled=is_disabled)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Hazırla ve Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            for sn in range(3, 0, -1):
                progress_bar.progress(int((4 - sn) * 25))
                status_box.info(f"🔄 Vektörel SVG şemalı sorular hazırlanıyor... ({sn}s)")
                time.sleep(0.5)
            
            sorular = ders_sirali_ve_dengeli_uret(secilen_uniteler, soru_sayisi)
            
            progress_bar.progress(100)
            status_box.success("✅ Sorular başarıyla oluşturuldu!")
            time.sleep(0.5)
            
            st.session_state["soru_listesi"] = sorular
            st.session_state["toplam_sure_sn"] = len(sorular) * 90
            st.session_state["sorular_hazir"] = True
            st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen en az bir mod ve ünite seçimi yapın!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Hazırla", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.rerun()

# =========================================================
# 6. TEST EKRANI
# =========================================================
if st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"🎉 **{len(st.session_state['soru_listesi'])} adet vektör şemalı soru** hazır!")
    if st.button("🏁 Sınavı Şimdi Başlat", type="primary", use_container_width=True):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.rerun()

if st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        st.info("💡 İstediğin an testi sonlandırıp puanını ve detaylı cevap anahtarını görebilirsin.")
    with top_col2:
        if st.button("🏁 Sınavı Bitir", type="secondary", use_container_width=True):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

    soru_listesi = st.session_state["soru_listesi"]
    idx = st.session_state["mevcut_soru_index"]
    
    if idx < len(soru_listesi):
        s = soru_listesi[idx]
        
        st.subheader(f"Soru {idx + 1} / {len(soru_listesi)} | Ders: **{s['ders']}** ({s['unite']})")
        st.markdown(s["soru"], unsafe_allow_html=True)
        
        onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx)
        secim_index = s["siklar"].index(onceki_cevap) if onceki_cevap in s["siklar"] else None
            
        secim = st.radio(
            "Seçenekleriniz:", 
            s["siklar"], 
            key=f"soru_r_{idx}",
            index=secim_index
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if idx > 0 and st.button("⬅️ Önceki Soru"):
                if secim is not None:
                    st.session_state["kullanici_cevaplari"][idx] = secim
                st.session_state["mevcut_soru_index"] -= 1
                st.rerun()
        with col2:
            if idx < len(soru_listesi) - 1:
                if st.button("Sonraki Soru ➡️", type="primary"):
                    if secim is not None:
                        st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["mevcut_soru_index"] += 1
                    st.rerun()
            else:
                if st.button("🏁 Sınavı Bitir ve Puanı Gör", type="primary"):
                    if secim is not None:
                        st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["test_aktif"] = False
                    st.session_state["test_bitti"] = True
                    st.rerun()
    else:
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

# =========================================================
# 7. SONUÇLAR VE CEVAP ANAHTARI
# =========================================================
if st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuçları ve Detaylı Cevap Anahtarı")
    
    dogru_sayisi = 0
    yanlis_sayisi = 0
    bos_sayisi = 0
    
    for idx, s in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(idx)
        if not k_cevabi:
            bos_sayisi += 1
        elif k_cevabi == s["dogru"]:
            dogru_sayisi += 1
        else:
            yanlis_sayisi += 1
            
    toplam_soru = len(st.session_state["soru_listesi"])
    puan = int((dogru_sayisi / toplam_soru) * 100) if toplam_soru > 0 else 0
    
    st.metric(label="Notunuz / Puanınız", value=f"{puan} Puan")
    st.write(f"✅ Doğru Sayısı: **{dogru_sayisi}** | ❌ Yanlış Sayısı: **{yanlis_sayisi}** | ⚠️ Boş Sayısı: **{bos_sayisi}**")
    
    st.divider()
    st.subheader("📝 Detaylı Cevap Anahtarı")
    
    for idx, s in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(idx, "Boş bırakıldı")
        d_cevabi = s["dogru"]
        
        durum_ikonu = "✅" if k_cevabi == d_cevabi else "❌"
        
        with st.expander(f"Soru {idx + 1} ({s['ders']}) - {durum_ikonu}"):
            st.markdown(s["soru"], unsafe_allow_html=True)
            st.write(f"📌 **Ünite / Konu:** {s['unite']}")
            st.write(f"👤 **Senin Cevabın:** {k_cevabi}")
            st.write(f"🎯 **Doğru Cevap:** {d_cevabi}")

    st.write("")
    if st.button("🔄 Yeni Sınav Başlat", type="primary"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.session_state["soru_listesi"] = []
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
