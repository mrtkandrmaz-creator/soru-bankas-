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
# 4. HAVUZ VERİLERİ
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem", "Onur", "Görkem", "Arda", "Defne", "Cem", "Melis", "Umut", "Naz", "Yusuf", "İpek", "Emre", "Ceren", "Tarık", "Lale", "Beste", "Berk", "Aslı"]
NESNELER = ["fındık", "bilye", "kitap", "kalem", "pul", "elma", "ceviz", "etiket", "sayfa", "çikolata", "kart", "balon", "silgi", "defter", "misket", "toka", "klemens", "not kağıdı", "bisküvi"]

FEN_UNITE_1_MATRIS = [
    ("Güneş'in küre şeklinde olduğunu ve kendi ekseni etrafında döndüğünü ilk savunan veya gözleyen bilimsel gerçeklik aşağıdakilerden hangisidir?", "Güneş de tıpkı Dünya gibi kendi ekseni etrafında döner ve küresel şekle sahiptir.", ["Güneş tamamen hareketsiz ve düz bir levhadır.", "Güneş sadece etrafına ışık saçar, dönme hareketi yapmaz.", "Güneş, Dünya'nın etrafında döner."]),
    ("Dünya'mızın şekli geoit olarak adlandırılır. Bu şeklin temel sebebi nedir?", "Kutuplardan basık, ekvatordan şişkin olması.", ["Tamamen kusursuz bir daire olması.", "Küp şeklinde köşeli olması.", "Sürekli büyüklüğünün değişmesi."]),
    ("Ay'ın Dünya'ya göre büyüklüğü nasıldır?", "Dünya'nın büyüklüğü Ay'ınkinden çok büyüktür (yaklaşık 4 katı çap oranında).", ["Ay, Dünya'dan çok daha büyüktür.", "Dünya ile Ay tamamen aynı boyuttadır.", "Ay, Güneş ile aynı boyuttadır."]),
    ("Ay'ın ana evreleri sırasıyla hangi seçenekte doğru verilmiştir?", "Yeniay -> İlk Dördün -> Dolunay -> Son Dördün", ["Dolunay -> Yeniay -> Son Dördün -> İlk Dördün", "İlk Dördün -> Dolunay -> Yeniay -> Son Dördün", "Yeniay -> Dolunay -> İlk Dördün -> Son Dördün"]),
    ("Dünya'nın kendi ekseni etrafında bir tam tur dönmesi sonucunda ne oluşur?", "Gece ve gündüz", ["Mevsimler", "Yıl", "Ay'ın evreleri"]),
    ("Dünya'nın Güneş etrafında dolanma hareketi ne kadar sürer?", "1 yıl (365 gün 6 saat)", ["1 gün (24 saat)", "1 ay (29.5 gün)", "1 hafta"]),
    ("Ay'ın ana evreleri arasında yaklaşık ne kadar süre geçer?", "Yaklaşık 1 hafta (7-8 gün)", ["24 saat", "1 yıl", "6 ay"]),
    ("Ay'ın ışık kaynağı olma durumu nedir?", "Ay bir ışık kaynağı değildir, Güneş'ten aldığı ışığı yansıtır.", ["Kendi başına büyük bir ışık kaynağıdır.", "Geceleri kendi enerjisiyle parlar.", "Hiçbir şekilde ışık yaymaz ve yansıtmaz."]),
    ("Güneş, Dünya ve Ay'ın büyüklükleri büyükten küçüğe doğru hangi seçenekte doğru sıralanmıştır?", "Güneş > Dünya > Ay", ["Dünya > Güneş > Ay", "Ay > Dünya > Güneş", "Güneş > Ay > Dünya"])
]

FEN_UNITE_2 = [("Mikroskobik canlılar grubuna girmeyen organizma aşağıdakilerden hangisidir?", "Kuşlar", ["Bakteriler", "Amip", "Paramesyum"])]
FEN_UNITE_3 = [("Kuvvetin büyüklüğünü ölçmek için kullanılan araç nedir?", "Dinamometre", ["Termometre", "Barometre", "Kronometre"])]
FEN_UNITE_4 = [("Saf bir maddenin ısı alarak katı halden sıvı hale geçmesine ne denir?", "Erime", ["Donma", "Buharlaşma", "Yoğuşma"])]
FEN_UNITE_5 = [("Işık maddelerle karşılaştığında geçiş durumuna göre sınıflandırılır. Aşağıdakilerden hangisi ışığı geçirmeyen (saydam olmayan) maddedir?", "Tahta levha", ["Cam", "Su", "Hava"])]

TURKCE_ANLAM = [("Aşağıdaki cümlelerin hangisinde 'çıkmak' sözcüğü 'ortaya çıkmak, görünmek' anlamında kullanılmıştır?", "Güneş yavaş yavaş dağların arkasından çıkıyordu.", ["Bu gömlek bana biraz küçük çıktı.", "Merdivenleri çıkarken çok yoruldum.", "Toplantıdan erken çıkmak zorunda kaldım."])]
TURKCE_CUMLE = [("Aşağıdaki cümlelerin hangisinde 'neden-sonuç' ilişkisi vardır?", "Hava yağmurlu olduğu için pikniği iptal ettik.", ["Ders çalışmak üzere odasına çekildi.", "Erken kalkarsa otobüse yetişebilir.", "Sokakta yürürken eski bir arkadaşıyla karşılaştı."])]
TURKCE_PARAGRAF = [("Metnin ana düşüncesi aşağıdakilerden hangisini ifade eder?", "Yazarın okuyucuya aktarmak istediği temel mesajı veya dersi.", ["Metinde geçen en uzun cümleyi.", "Yazarın kişisel yaşantısındaki tüm detayları.", "Paragrafta kullanılan yan düşüncelerin toplamını."])]
TURKCE_YAZIM = [("Aşağıdaki sözcüklerden hangisinin yazımı <b>yanlıştır</b>?", "herkez", ["herkes", "yalnız", "yanlış"])]

SOSYAL_UNITE_1 = [("Evde veya okulda üstlendiğimiz görevleri yerine getirmeye ne denir?", "Sorumluluk", ["Hak", "Özgürlük", "Yetki"])]
SOSYAL_UNITE_2 = [("Tarihî eserlerin ve kalıntıların korunması hangi dersin temel konularından biridir?", "Sosyal Bilgiler", ["Matematik", "Fen Bilimleri", "İngilizce"])]
SOSYAL_UNITE_3 = [("Haritalarda yüksek dağları kahverengiyle, denizleri maviyle göstermek hangi harita türüne hastır?", "Fiziki harita", ["Siyasi harita", "Beşeri harita", "Karayolu haritası"])]
SOSYAL_UNITE_4 = [("Geçmişten günümüze bilgi depolamak ve aktarmak için kullanılan en önemli buluşlardan biri nedir?", "Matbaa", ["Dinamometre", "Pusula", "Termometre"])]

DIN_UNITE_1 = [("Evrende her şeyin kusursuz bir düzene sahip olması ve bir yaratıcısının bulunması inancına ne denir?", "Allah İnancı", ["Oruç", "Zekat", "Adap"])]
DIN_UNITE_2 = [("Ramazan ayında imsak vaktinden iftar vaktine kadar yemek ve içmekten uzak durarak yapılan ibadet nedir?", "Oruç", ["Hac", "Zekat", "Kurban"])]
DIN_UNITE_3 = [("Görgü kurallarına uymak, insanlara karşı güler yüzlü ve kibar olmak hangi kavramla ifade edilir?", "Adap ve Nezaket", ["İbadet", "İnanç", "Oruç"])]

ING_UNITE_1 = [("'-Where are you from?' sorusuna aşağıdaki cevaplardan hangisi uygundur?", "I am from Spain", ["I am ten years old", "I like playing tennis", "Good morning"])]
ING_UNITE_2 = [("Yön tarif ederken 'Sola dön' demek için hangi ifade kullanılır?", "Turn left", ["Turn right", "Go straight ahead", "Stop"])]
ING_UNITE_3 = [("Boş zaman aktivitelerini ve hobileri ifade eden ünitenin adı nedir?", "Games and Hobbies", ["My Town", "Hello", "My Daily Routine"])]
ING_UNITE_4 = [("Sabah kalkma, kahvaltı yapma ve okula gitme gibi günlük rutinler hangi ünitede incelenir?", "My Daily Routine", ["Nationalities", "Directions", "Hobbies"])]

BASKENT_LISTESI = [("Fransa", "Paris"), ("İtalya", "Roma"), ("Japonya", "Tokyo"), ("Almanya", "Berlin"), ("İspanya", "Madrid"), ("İngiltere", "Londra"), ("Yunanistan", "Atina"), ("Rusya", "Moskova")]
YEMEK_SEHIR_LISTESI = [("Künefe", "Hatay"), ("Cağ Kebabı", "Erzurum"), ("Mantı", "Kayseri"), ("Baklava", "Gaziantep")]
ALL_SEHIRLER = ["Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Trabzon", "Erzurum", "Gaziantep"]
DNY_MUTFAK_LISTESI = [("Sushi", "Japonya"), ("Pizza", "İtalya"), ("Taco", "Meksika"), ("Kruvasan", "Fransa")]
ALL_ULKELER = ["Japonya", "İtalya", "Meksika", "Fransa", "İspanya", "Çin", "Almanya"]
HARITA_HAVUZU = [("Haritalarda yön bulmamıza yardımcı olan ve genellikle kuzeyi gösteren işaret nedir?", "Kuzey oku (Pusula gülü)", ["Ölçek", "Lejant", "Eş yükselti"])]
ICAT_HAVUZU = [("Telefonu icat ederek ilk sesli iletişim kuran mucit kimdir?", "Alexander Graham Bell", ["Thomas Edison", "Nikola Tesla", "Isaac Newton"])]
GENEL_KULTUR_HAVUZU = [("Dünyanın en uzun nehri olarak bilinen Nil Nehri hangi kıtadadır?", "Afrika", ["Asya", "Avrupa", "Amerika"])]

# =========================================================
# 5. YAPAY ZEKA (%75) VE HAVUZ (%25) HİBRİT ÜRETİCİ
# =========================================================
def yapay_zekadan_soru_uret(ders, unite):
    """Simüle edilmiş Yapay Zeka (%75 ağırlıklı akıllı dinamik soru motoru)"""
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    
    if ders == "Matematik":
        sayi = random.randint(1000, 99999)
        return {"soru": f"🤖 [AI-Üretim] {kisi} <b>{sayi}</b> sayısını incelemektedir. Bu sayının çözümlenmiş hali veya basamak değeri analiziyle ilgili soru...", "siklar": [str(sayi), str(sayi+10), str(sayi-5), str(sayi*2)], "dogru": str(sayi), "gorsel_svg": None}
    elif ders == "Fen Bilimleri":
        return {"soru": f"🤖 [AI-Üretim] {kisi}'in fen laboratuvarında gözlemlediği deney sonucuna göre doğru ifade hangisidir?", "siklar": ["Bilimsel olarak doğrudur", "Tamamen yanlıştır", "Hacmi etkilemez", "Isı yaymaz"], "dogru": "Bilimsel olarak doğrudur", "gorsel_svg": None}
    else:
        return {"soru": f"🤖 [AI-Üretim] {kisi} tarafından hazırlanan özgün <b>{unite}</b> kazanım sorusu...", "siklar": ["Doğru Seçenek A", "Çeldirici B", "Çeldirici C", "Çeldirici D"], "dogru": "Doğru Seçenek A", "gorsel_svg": None}

def havuzdan_soru_uret(ders, unite):
    """Yerel Havuz (%25 ağırlıklı sabit veya matris tabanlı soru motoru)"""
    u_low = unite.lower()
    if ders == "Fen Bilimleri":
        q, ans, celd = random.choice(FEN_UNITE_1_MATRIS)
        return {"soru": f"📚 [Havuz] {q}", "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
    elif ders == "Türkçe":
        q, ans, celd = random.choice(TURKCE_ANLAM)
        return {"soru": f"📚 [Havuz] {q}", "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}
    else:
        return {"soru": f"📚 [Havuz] <b>{unite}</b> ile ilgili standart soru...", "siklar": ["Cevap 1", "Cevap 2", "Cevap 3", "Cevap 4"], "dogru": "Cevap 1", "gorsel_svg": None}

def ders_sirali_soru_uret(secilen_uniteler, hedef_sayi):
    if not secilen_uniteler:
        return []

    toplam_secilen = len(secilen_uniteler)
    temel_pay = hedef_sayi // toplam_secilen
    kalan = hedef_sayi % toplam_secilen

    ham_soru_listesi = []
    hash_set = set()

    for idx, (ders, unite) in enumerate(secilen_uniteler):
        bu_unite_hedef = temel_pay + (1 if idx < kalan else 0)
        
        # %75 Yapay Zeka, %25 Havuz Dağılımı Hesaplama
        ai_hedef = int(bu_unite_hedef * 0.75)
        havuz_hedef = bu_unite_hedef - ai_hedef

        # Yapay Zeka Soruları Üret
        uretilen = 0
        while uretilen < ai_hedef:
            s = yapay_zekadan_soru_uret(ders, unite)
            s["ders"] = ders
            s["unite"] = unite
            random.shuffle(s["siklar"])
            fingerprint = hashlib.sha256((s["soru"] + str(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                ham_soru_listesi.append(s)
                uretilen += 1

        # Havuz Soruları Üret
        uretilen = 0
        while uretilen < havuz_hedef:
            s = havuzdan_soru_uret(ders, unite)
            s["ders"] = ders
            s["unite"] = unite
            random.shuffle(s["siklar"])
            fingerprint = hashlib.sha256((s["soru"] + str(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                ham_soru_listesi.append(s)
                uretilen += 1

    for _ in range(3):
        random.shuffle(ham_soru_listesi)

    return ham_soru_listesi[:hedef_sayi]

# =========================================================
# 6. STREAMLIT ARAYÜZÜ (SOL MENÜ)
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

# HATA ÇÖZÜLDÜ: min_v / max_v yerine doğru parametre adları kullanıldı
soru_sayisi = st.sidebar.slider(
    "Toplam Soru Sayısı:", 
    min_value=20, 
    max_value=100, 
    value=20, 
    step=5, 
    disabled=is_disabled
)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Hazırla ve Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            # Tahmini üretim süresi hesaplama
            tahmini_sure = max(3, int((soru_sayisi * len(secilen_uniteler)) / 120))
            
            # Dinamik Geri Sayım Görselleştirmesi ve Canlı İlerleme Çubuğu
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            for kalan_sn in range(tahmini_sure, 0, -1):
                progress_yuzdesi = int(((tahmini_sure - kalan_sn + 1) / tahmini_sure) * 100)
                progress_bar.progress(min(progress_yuzdesi, 95))
                status_box.info(
                    f"🤖 Soruların %75'i yapay zekadan, %25'i yerel havuzdan harmanlanıyor... "
                    f"Kalan tahmini süre: **{kalan_sn} saniye**"
                )
                time.sleep(1)
            
            # Hibrit Soru Üretim Fonksiyonunu Çalıştır
            sorular = ders_sirali_soru_uret(secilen_uniteler, soru_sayisi)
            
            progress_bar.progress(100)
            status_box.success("✅ Hibrit sorular başarıyla hazırlandı!")
            time.sleep(0.5)
            
            st.session_state["soru_listesi"] = sorular
            st.session_state["toplam_sure_sn"] = len(sorular) * 90
            st.session_state["sorular_hazir"] = True
            st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen sol menüden en az bir mod ve ünite seçimi yapın!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Hazırla", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.rerun()

# =========================================================
# 7. TEST EKRANI VE SONUÇ GÖSTERİMİ
# =========================================================
if st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"🎉 **{len(st.session_state['soru_listesi'])} adet hibrit soru** (%75 AI - %25 Havuz) başarıyla hazırlandı!")
    if st.button("🏁 Sınavı Şimdi Başlat", type="primary", use_container_width=True):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.rerun()

if st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    soru_listesi = st.session_state["soru_listesi"]
    idx = st.session_state["mevcut_soru_index"]
    
    if idx < len(soru_listesi):
        s = soru_listesi[idx]
        
        st.subheader(f"Soru {idx + 1} / {len(soru_listesi)} ({s['ders']} - {s['unite']})")
        st.markdown(s["soru"], unsafe_allow_html=True)
        
        if s.get("gorsel_svg"):
            st.markdown(s["gorsel_svg"], unsafe_allow_html=True)
            
        secim = st.radio(
            "Seçenekleriniz:", 
            s["siklar"], 
            key=f"soru_r_{idx}",
            index=s["siklar"].index(st.session_state["kullanici_cevaplari"].get(idx)) if idx in st.session_state["kullanici_cevaplari"] else 0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if idx > 0 and st.button("⬅️ Önceki Soru"):
                st.session_state["kullanici_cevaplari"][idx] = secim
                st.session_state["mevcut_soru_index"] -= 1
                st.rerun()
        with col2:
            if idx < len(soru_listesi) - 1:
                if st.button("Sonraki Soru ➡️", type="primary"):
                    st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["mevcut_soru_index"] += 1
                    st.rerun()
            else:
                if st.button("🏁 Sınavı Bitir ve Puanı Gör", type="primary"):
                    st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["test_aktif"] = False
                    st.session_state["test_bitti"] = True
                    st.rerun()
    else:
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

if st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuçları")
    
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
    st.write(f"✅ Doğru Sayısı: **{dogru_sayisi}**")
    st.write(f"❌ Yanlış Sayısı: **{yanlis_sayisi}**")
    st.write(f"⚠️ Boş Sayısı: **{bos_sayisi}**")
    
    if st.button("🔄 Yeni Sınav Başlat", type="primary"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.session_state["soru_listesi"] = []
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
