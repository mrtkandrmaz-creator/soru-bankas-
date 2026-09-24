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
        "1. Kategori: Dünya Başkentleri ve Coğrafya",
        "2. Kategori: Türk Mutfağı ve Yöresel Lezzetler",
        "3. Kategori: Dünya Mutfakları ve Lezzetler",
        "4. Kategori: Harita Bilgisi ve Yönler",
        "5. Kategori: Bilim Tarihi ve İcatlar",
        "6. Kategori: Genel Kültür ve Doğa Harikaları"
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
# 3. SVG GEOMETRİ ÇİZİCİ
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
# 4. GENİŞLETİLMİŞ VERİ TABANI VE HİBRİT ÜRETİCİ
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem", "Onur", "Görkem", "Arda", "Defne", "Cem", "Melis", "Umut", "Naz"]
NESNELER = ["fındık", "bilye", "kitap", "kalem", "pul", "elma", "ceviz", "etiket", "sayfa", "çikolata", "kart", "balon"]

BASKENT_LISTESI = [
    ("Fransa", "Paris"), ("İtalya", "Roma"), ("Japonya", "Tokyo"), ("Almanya", "Berlin"), 
    ("İspanya", "Madrid"), ("İngiltere", "Londra"), ("Yunanistan", "Atina"), ("Rusya", "Moskova"), 
    ("Azerbaycan", "Bakü"), ("Mısır", "Kahire"), ("İran", "Tahran"), ("Irak", "Bağdat"),
    ("Çin", "Pekin"), ("Hindistan", "Yeni Delhi"), ("Güney Kore", "Seul"), ("Kanada", "Ottawa")
]

YEMEK_SEHIR_LISTESI = [
    ("Künefe", "Hatay"), ("Cağ Kebabı", "Erzurum"), ("İskender Kebap", "Bursa"),
    ("Mantı", "Kayseri"), ("Baklava", "Gaziantep"), ("Tantuni", "Mersin"),
    ("Etli Ekmek", "Konya"), ("Hamsi Tava", "Trabzon"), ("Pide", "Samsun"),
    ("Çiğ Köfte", "Şanlıurfa"), ("Testi Kebabı", "Yozgat"), ("Keşkek", "Aydın"),
    ("İnegöl Köfte", "Bursa"), ("Oltu Kebabı", "Erzurum"), ("Kepse Pilavı", "Mersin")
]
ALL_SEHIRLER = ["Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Trabzon", "Erzurum", "Gaziantep", "Konya", "Samsun", "Adana", "Hatay", "Mersin", "Kayseri", "Şanlıurfa", "Yozgat", "Aydın", "İzmit", "Eskişehir", "Sivas", "Van"]

DNY_MUTFAK_LISTESI = [
    ("Sushi", "Japonya"), ("Pizza", "İtalya"), ("Taco", "Meksika"),
    ("Kruvasan", "Fransa"), ("Hamburger", "Amerika Birleşik Devletleri"),
    ("Paella", "İspanya"), ("Makarna", "İtalya"), ("Çin Mantısı (Dim Sum)", "Çin"),
    ("Pad Thai", "Tayland"), ("Pho", "Vietnam"), ("Fish and Chips", "İngiltere"),
    ("Gulaş", "Macaristan"), ("Falafel", "Lübnan"), ("Borsç", "Rusya")
]
ALL_ULKELER = ["Japonya", "İtalya", "Meksika", "Fransa", "Amerika Birleşik Devletleri", "İspanya", "Çin", "Almanya", "İngiltere", "Brezilya", "Yunanistan", "Tayland", "Vietnam", "Macaristan", "Lübnan", "Rusya", "Arjantin"]

HARITA_HAVUZU = [
    ("Haritalarda yön bulmamıza yardımcı olan ve genellikle kuzeyi gösteren işaret nedir?", "Kuzey oku (Pusula gülü)", ["Ölçek", "Lejant", "Eş yükselti"]),
    ("Fiziki haritalarda suları ve denizleri göstermek için hangi renk kullanılır?", "Mavi", ["Yeşil", "Kahverengi", "Sarı"]),
    ("Fiziki haritalarda dağları ve yüksek yerleri göstermek için hangi renk tonları kullanılır?", "Kahverengi ve tonları", ["Mavi ve tonları", "Koyu yeşil", "Parlak sarı"]),
    ("Ülkemizin kuzeyinde yer alan deniz hangisidir?", "Karadeniz", ["Akdeniz", "Ege Denizi", "Kızıldeniz"]),
    ("Haritalarda yer alan sembollerin ne anlama geldiğini gösteren tabloya ne denir?", "Lejant (Harita anahtarı)", ["Ölçek", "Pusula gülü", "Kuzey oku"])
]

ICAT_HAVUZU = [
    ("Telefonu icat ederek ilk sesli iletişim kuran mucit kimdir?", "Alexander Graham Bell", ["Thomas Edison", "Nikola Tesla", "Isaac Newton"]),
    ("Ampulü icat ederek elektriğin aydınlatmada kullanılmasını sağlayan kimdir?", "Thomas Edison", ["Alexander Graham Bell", "Albert Einstein", "Wright Kardeşler"]),
    ("Matbaayı geliştirerek kitapların çoğaltılmasını hızlandıran kişi kimdir?", "Johannes Gutenberg", ["Galileo Galilei", "Leonardo da Vinci", "Blaise Pascal"]),
    ("İlk motorlu uçağı icat ederek havacılık tarihini başlatanlar kimlerdir?", "Wright Kardeşler", ["Marie Curie", "Thomas Edison", "Alexander Graham Bell"]),
    ("Pusulayı ilk defa yön bulmak amacıyla denizcilikte kullanan medeniyetler kimlerdir?", "Uzak Doğu (Çinliler)", ["Romalılar", "Yunanlılar", "Mayalar"])
]

GENEL_KULTUR_HAVUZU = [
    ("Dünyanın en uzun nehri olarak bilinen Nil Nehri hangi kıtadadır?", "Afrika", ["Asya", "Avrupa", "Amerika"]),
    ("Dünyanın en yüksek dağı olan Everest Dağı hangi kıtada yer alır?", "Asya", ["Afrika", "Avrupa", "Antarktika"]),
    ("Türkiye Cumhuriyeti'nin kurucusu ve ilk cumhurbaşkanı kimdir?", "Mustafa Kemal Atatürk", ["Fatih Sultan Mehmet", "İsmet İnönü", "Kanuni Sultan Süleyman"]),
    ("Türkiye Cumhuriyeti'nin başkenti neresidir?", "Ankara", ["İstanbul", "İzmir", "Bursa"]),
    ("Dünyanın yüzölçümünün büyük kısmını kaplayan ve 'Mavi Gezegen' olarak bilinen gezegen hangisidir?", "Dünya", ["Mars", "Venüs", "Jüpiter"])
]

def dinamik_soru_uretici(ders, unite):
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    nesne = random.choice(NESNELER)
    kisi2 = random.choice([i for i in ISIMLER if i != kisi])

    if ders == "Matematik":
        if "1. ünite" in u_low:
            sayi = random.randint(10000, 9999999)
            carpan = random.choice([100000, 10000, 1000, 100, 10])
            b_deg = ((sayi // carpan) % 10) * carpan
            q = f"{kisi}'in yazdığı <b>{sayi}</b> sayısındaki seçilen basamağın basamak değeri kaçtır?"
            ans = str(b_deg)
            celd = [str(b_deg * 10 if b_deg > 0 else 100), str(max(10, b_deg // 10 if b_deg > 0 else 50)), str(b_deg + 250)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "2. ünite" in u_low:
            payda = random.choice([8, 10, 12, 16, 20])
            p1, p2 = random.randint(1, payda // 2), random.randint(1, payda // 2)
            top = p1 + p2
            q = f"{kisi} pastanın {p1}/{payda}'sini, {kisi2} ise {p2}/{payda}'sini yemiştir. Toplam ne kadar yenmiştir?"
            ans = f"{top}/{payda}"
            celd = [f"{top + 1}/{payda}", f"{max(1, top - 1)}/{payda}", f"{top}/{payda + 4}"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "3. ünite" in u_low:
            p = random.choice([10, 20, 25, 50])
            fiyat = random.randint(100, 1000)
            indirim = (fiyat * p) // 100
            ans = str(fiyat - indirim)
            q = f"{kisi} fiyatı {fiyat} TL olan ürünü <b>%{p}</b> indirimle almıştır. Kaç TL öder?"
            celd = [str(indirim), str(fiyat + indirim), str(fiyat - indirim + 50)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "4. ünite" in u_low:
            aci1 = random.randint(25, 65)
            ans = f"{90 - aci1}°"
            q = f"Komşu tümler iki açıdan biri {aci1}° olduğuna göre diğer açı kaç derecedir?"
            celd = [f"{90 - aci1 + 15}°", f"{abs(90 - aci1 - 10)}°", "45°"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "5. ünite" in u_low:
            koseler = random.choice([("A", "B", "C"), ("K", "L", "M"), ("P", "R", "S")])
            t = random.choice(["eskenar", "dik", "ikizkenar"])
            if t == "eskenar":
                ans, svg = "60°", svg_dinamik_ucgen_ciz("eskenar", ["?", "60°", "60°"], koseler)
                q = f"Şekildeki eşkenar üçgende verilmeyen açı kaç derecedir?"
                celd = ["90°", "45°", "30°"]
            elif t == "dik":
                ans, svg = "60°", svg_dinamik_ucgen_ciz("dik", ["?", "90°", "30°"], koseler)
                q = f"Şekildeki dik üçgende m({koseler[1]}) = 90° ve diğeri 30° iken m({koseler[0]}) kaçtır?"
                celd = ["45°", "30°", "75°"]
            else:
                ans, svg = "50°", svg_dinamik_ucgen_ciz("ikizkenar", ["?", "65°", "65°"], koseler)
                q = f"Şekildeki ikizkenar üçgende taban açılar 65° ise tepe açısı kaçtır?"
                celd = ["60°", "40°", "70°"]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": svg}
        else:
            saat = random.randint(2, 7)
            ans = str(saat * 60)
            q = f"{kisi} {saat} saat süren etkinlik yapmıştır. Bu etkinlik kaç dakikadır?"
            celd = [str(saat * 60 + 30), str(saat * 60 - 15), str(saat * 50)]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Fen Bilimleri":
        q = f"{kisi} fen laboratuvarında gözlem yapmaktadır. Saf bir maddenin ısı alarak sıvı hale geçmesi olayına ne denir?"
        ans, celd = "Erime", ["Donma", "Buharlaşma", "Yoğuşma"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Türkçe":
        q = f"Aşağıdaki sözcüklerden hangisinin yazımı <b>yanlıştır</b>?"
        ans, celd = "herkez", ["herkes", "yalnız", "itiraf"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Sosyal Bilgiler":
        q = f"{kisi}'in evde odasını toplu tutması onun hangi özelliğini gösterir?"
        ans, celd = "Sorumluluk sahibi olduğunu", ["Haklarını bildiğini", "Çocuk olduğunu", "Kuralları bozduğunu"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        q = f"Ramazan ayında imsak ile akşam ezanı arasında tutulan farz ibadet nedir?"
        ans, celd = "Oruç", ["Zekat", "Hac", "Kurban"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    elif ders == "İngilizce":
        q = f"İngilizcede yön tarif ederken 'Sola dön' demek için hangi kalıp kullanılır?"
        ans, celd = "Turn left", ["Turn right", "Go straight", "Stop"]
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    else: # 🏆 Bilgi Yarışması (Milyarlarca Benzersiz Kombinasyon ve Sıfır Tekrar Motoru)
        if "1. kategori" in u_low:
            ulke, dogru_baskent = random.choice(BASKENT_LISTESI)
            q = f"<b>{ulke}</b> ülkesinin başkenti olan dünya şehri aşağıdakilerden hangisidir?"
            ans = dogru_baskent
            celd = [b for u, b in BASKENT_LISTESI if b != ans]
            random.shuffle(celd)
            celd = celd[:3]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "2. kategori" in u_low:
            yemek, dogru_sehir = random.choice(YEMEK_SEHIR_LISTESI)
            q = f"Ülkemizin eşsiz lezzetlerinden biri olan <b>{yemek}</b> hangi ilimizle özdeşleşmiştir?"
            ans = dogru_sehir
            celd = [s for s in ALL_SEHIRLER if s != ans]
            random.shuffle(celd)
            celd = celd[:3]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "3. kategori" in u_low:
            mutfak, dogru_ulke = random.choice(DNY_MUTFAK_LISTESI)
            q = f"Dünya mutfağında çok popüler olan ve özel bir lezzet olan <b>{mutfak}</b> hangi ülke ile özdeşleşmiştir?"
            ans = dogru_ulke
            celd = [u for u in ALL_ULKELER if u != ans]
            random.shuffle(celd)
            celd = celd[:3]
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "4. kategori" in u_low:
            q, ans, celd = random.choice(HARITA_HAVUZU)
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        elif "5. kategori" in u_low:
            q, ans, celd = random.choice(ICAT_HAVUZU)
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
        else:
            q, ans, celd = random.choice(GENEL_KULTUR_HAVUZU)
            return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

# =========================================================
# 5. SORU LİSTESİ OLUŞTURUCU (MÜKERRERLİK ENGELLEYİCİ)
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
        while uretilen_sayi < dersin_hedef_sayisi and deneme < 2000:
            deneme += 1
            secilen_u = random.choice(uniteler)
            s = dinamik_soru_uretici(ders, secilen_u)
            s["ders"] = ders
            s["unite"] = secilen_u
            
            random.shuffle(s["siklar"])

            # Sadece soru metnini baz alarak aynı sorunun kopya olarak düşmesini tamamen engelle
            fingerprint = hashlib.sha256(s["soru"].encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                tam_soru_listesi.append(s)
                uretilen_sayi += 1

    return tam_soru_listesi[:hedef_sayi]

# =========================================================
# 6. STREAMLIT ARAYÜZÜ
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
            with st.spinner("Benzersiz ve tekrarsız sorular üretiliyor..."):
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
    st.info("Sol panelden mod seçip üniteleri belirledikten sonra **'Hazırla ve Başlat'** butonuna tıklayın.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorularınız Başarıyla Oluşturuldu!")
    
    ders_sayilari = {}
    for s in st.session_state['soru_listesi']:
        ders_sayilari[s['ders']] = ders_sayilari.get(s['ders'], 0) + 1
    
    cols = st.columns(len(ders_sayilari))
    for i, (d_isimlendirme, d_adet) in enumerate(ders_sayilari.items()):
        cols[i].markdown(f"""
        <div style="background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center;">
            <h4 style="color: #1e293b; margin: 0; font-size: 16px;">{d_isimlendirme}</h4>
            <h1 style="color: #2563eb; margin: 5px 0 0 0; font-size: 36px;">{d_adet}</h1>
            <p style="color: #64748b; margin: 0; font-size: 12px;">Adet Soru</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button("⏱️ Sınavı Başlat", type="primary", use_container_width=True):
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
