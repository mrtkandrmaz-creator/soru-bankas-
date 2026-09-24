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
# 4. GENİŞLETİLMİŞ VE MİLYONLARCA KOMBİNASYONLU MATRİS HAVUZLARI
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem", "Onur", "Görkem", "Arda", "Defne", "Cem", "Melis", "Umut", "Naz", "Yusuf", "İpek", "Emre", "Ceren", "Tarık", "Lale", "Beste", "Berk", "Aslı"]
NESNELER = ["fındık", "bilye", "kitap", "kalem", "pul", "elma", "ceviz", "etiket", "sayfa", "çikolata", "kart", "balon", "silgi", "defter", "misket", "toka", "klemens", "not kağıdı", "bisküvi"]

# BÜYÜK MATRİS: FEN BİLİMLERİ 1. ÜNİTE (GÜNEŞ, DÜNYA VE AY)
FEN_UNITE_1_MATRIS = [
    ("Güneş'in küre şeklinde olduğunu ve kendi ekseni etrafında döndüğünü ilk savunan veya gözleyen bilimsel gerçeklik aşağıdakilerden hangisidir?", "Güneş de tıpkı Dünya gibi kendi ekseni etrafında döner ve küresel şekle sahiptir.", ["Güneş tamamen hareketsiz ve düz bir levhadır.", "Güneş sadece etrafına ışık saçar, dönme hareketi yapmaz.", "Güneş, Dünya'nın etrafında döner."]),
    ("Dünya'mızın şekli geoit olarak adlandırılır. Bu şeklin temel sebebi nedir?", "Kutuplardan basık, ekvatordan şişkin olması.", ["Tamamen kusursuz bir daire olması.", "Küp şeklinde köşeli olması.", "Sürekli büyüklüğünün değişmesi."]),
    ("Ay'ın Dünya'ya göre büyüklüğü nasıldır?", "Dünya'nın büyüklüğü Ay'ınkinden çok büyüktür (yaklaşık 4 katı çap oranında).", ["Ay, Dünya'dan çok daha büyüktür.", "Dünya ile Ay tamamen aynı boyuttadır.", "Ay, Güneş ile aynı boyuttadır."]),
    ("Ay'ın ana evreleri sırasıyla hangi seçenekte doğru verilmiştir?", "Yeniay -> İlk Dördün -> Dolunay -> Son Dördün", ["Dolunay -> Yeniay -> Son Dördün -> İlk Dördün", "İlk Dördün -> Dolunay -> Yeniay -> Son Dördün", "Yeniay -> Dolunay -> İlk Dördün -> Son Dördün"]),
    ("Dünya'nın kendi ekseni etrafında bir tam tur dönmesi sonucunda ne oluşur?", "Gece ve gündüz", ["Mevsimler", "Yıl", "Ay'ın evreleri"]),
    ("Dünya'nın Güneş etrafında dolanma hareketi ne kadar sürer?", "1 yıl (365 gün 6 saat)", ["1 gün (24 saat)", "1 ay (29.5 gün)", "1 hafta"]),
    ("Ay'ın ana evreleri arasında yaklaşık ne kadar süre geçer?", "Yaklaşık 1 hafta (7-8 gün)", ["24 saat", "1 yıl", "6 ay"]),
    ("Ay'ın ışık kaynağı olma durumu nedir?", "Ay bir ışık kaynağı değildir, Güneş'ten aldığı ışığı yansıtır.", ["Kendi başına büyük bir ışık kaynağıdır.", "Geceleri kendi enerjisiyle parlar.", "Hiçbir şekilde ışık yaymaz ve yansıtmaz."]),
    ("Güneş, Dünya ve Ay'ın büyüklükleri büyükten küçüğe doğru hangi seçenekte doğru sıralanmıştır?", "Güneş > Dünya > Ay", ["Dünya > Güneş > Ay", "Ay > Dünya > Güneş", "Güneş > Ay > Dünya"]),
    ("Ay'ın Dünya etrafındaki dolanım yönü aşağıdakilerden hangisidir?", "Batıdan doğuya doğru (saat yönünün tersine)", ["Doğudan batıya doğru (saat yönünde)", "Sadece kuzey-güney ekseninde", "Tamamen rastgele yönlerde"]),
    ("Aşağıdakilerden hangisi Dünya'nın hareketleri arasında yer alır?", "Kendi ekseni etrafında dönme ve Güneş etrafında dolanma", ["Sadece Güneş etrafında dönme", "Sadece kendi ekseni etrafında dolanma", "Sabit durma ve titreme hareketi"]),
    ("Yeniay ile Dolunay evreleri arasında hangi ara evre yer alır?", "İlk Dördün", ["Son Dördün", "Şişkin Ay", "Hilal"])
]

# Diğer Fen Üniteleri
FEN_UNITE_2 = [
    ("Mikroskobik canlılar grubuna girmeyen organizma aşağıdakilerden hangisidir?", "Kuşlar", ["Bakteriler", "Amip", "Paramesyum"]),
    ("Süngerler ve mercanlar hangi canlı grubuna dahildir?", "Omurgasız hayvanlar", ["Omurgalı hayvanlar", "Mantarlar", "Bitkiler"]),
    ("Şapkalı mantarlar hangi canlılar alemi içerisinde incelenir?", "Mantarlar", ["Bitkiler", "Hayvanlar", "Mikroskobik canlılar"])
]
FEN_UNITE_3 = [
    ("Kuvvetin büyüklüğünü ölçmek için kullanılan araç nedir?", "Dinamometre", ["Termometre", "Barometre", "Kronometre"]),
    ("Dinamometrelerin yapımında kullanılan yayların temel özelliği nedir?", "Esnek olmaları", ["Sert ve kırılgan olmaları", "Elektrik iletmeleri", "Şeffaf olmaları"]),
    ("Sürtünme kuvveti en çok hangi yüzeylerde daha fazladır?", "Pürüzlü yüzeyler", ["Pürüzsüz yüzeyler", "Buzlu zemin", "Yağlanmış zemin"])
]
FEN_UNITE_4 = [
    ("Saf bir maddenin ısı alarak katı halden sıvı hale geçmesine ne denir?", "Erime", ["Donma", "Buharlaşma", "Yoğuşma"]),
    ("Suyun kaynayarak sıvı halden gaz hale geçmesi olayı nasıl adlandırılır?", "Buharlaşma", ["Erime", "Donma", "Süblimleşme"])
]
FEN_UNITE_5 = [
    ("Işık maddelerle karşılaştığında geçiş durumuna göre sınıflandırılır. Aşağıdakilerden hangisi ışığı geçirmeyen (saydam olmayan) maddedir?", "Tahta levha", ["Cam", "Su", "Hava"]),
    ("Tam gölgenin oluşabilmesi için aşağıdakilerden hangisi mutlaka gereklidir?", "Işık kaynağı, opak cisim ve perde", ["Sadece ışık kaynağı", "Şeffaf bir cam ve ayna", "Manyetik alan"])
]

TURKCE_ANLAM = [
    ("Aşağıdaki cümlelerin hangisinde 'çıkmak' sözcüğü 'ortaya çıkmak, görünmek' anlamında kullanılmıştır?", "Güneş yavaş yavaş dağların arkasından çıkıyordu.", ["Bu gömlek bana biraz küçük çıktı.", "Merdivenleri çıkarken çok yoruldum.", "Toplantıdan erken çıkmak zorunda kaldım."]),
    ("Aşağıdaki cümlelerin hangisinde 'tutmak' sözcüğü 'kiralamak' anlamında kullanılmıştır?", "Yaz tatili için sahil kenarında küçük bir ev tuttular.", ["Elimdeki ağır koliyi zorlukla tutuyordum.", "Büyükbabası elinden tutup karşıya geçirdi.", "Çocuk kediyi kucağına alıp sıkıca tuttu."]),
    ("Aşağıdaki cümlelerin hangisinde terim anlamlı bir sözcük kullanılmıştır?", "Öğretmenimiz matematik dersinde üçgenin alanını işledi.", ["Bugün içimdeki neşe ile sokaklarda koştum.", "Bahçedeki sarı yapraklar rüzgarla uçuşuyordu.", "Yolculuk sırasında çok güzel kitaplar okudum."])
]
TURKCE_CUMLE = [
    ("Aşağıdaki cümlelerin hangisinde 'neden-sonuç' (sebep-sonuç) ilişkisi vardır?", "Hava yağmurlu olduğu için pikniği iptal ettik.", ["Ders çalışmak üzere odasına çekildi.", "Erken kalkarsa otobüse yetişebilir.", "Sokakta yürürken eski bir arkadaşıyla karşılaştı."]),
    ("Aşağıdaki cümlelerin hangisinde 'amaç-sonuç' ilişkisi vardır?", "Sınavı kazanmak amacıyla gece gündüz çalıştı.", ["Çok hızlı koştuğu için nefes nefese kaldı.", "Hava karardığına göre eve dönmeliyiz.", "Kitap okumayı çok sevdiğini her fırsatta söyler."])
]
TURKCE_PARAGRAF = [
    ("Bir paragrafın giriş cümlesinde aşağıdakilerden hangisi bulunmaz?", "Önceki cümlelerle bağlantı kuran 'Ancak, bu yüzden, çünkü' gibi bağlaçlar.", ["Ana fikre giriş niteliği.", "Kendinden sonraki cümlelerin açıklayacağı bir konu.", "Okuyucuyu konuya ısındıran bağımsız bir yargı."]),
    ("Metnin ana düşüncesi aşağıdakilerden hangisini ifade eder?", "Yazarın okuyucuya aktarmak istediği temel mesajı veya dersi.", ["Metinde geçen en uzun cümleyi.", "Yazarın kişisel yaşantısındaki tüm detayları.", "Paragrafta kullanılan yan düşüncelerin toplamını."])
]
TURKCE_YAZIM = [
    ("Aşağıdaki sözcüklerden hangisinin yazımı <b>yanlıştır</b>?", "herkez", ["herkes", "yalnız", "yanlış"]),
    ("Aşağıdaki sözcüklerden hangisinin yazımı <b>yanlıştır</b>?", "orjinal", ["orijinal", "sürpriz", "kravat"])
]

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

BASKENT_LISTESI = [
    ("Fransa", "Paris"), ("İtalya", "Roma"), ("Japonya", "Tokyo"), ("Almanya", "Berlin"), 
    ("İspanya", "Madrid"), ("İngiltere", "Londra"), ("Yunanistan", "Atina"), ("Rusya", "Moskova"), 
    ("Azerbaycan", "Bakü"), ("Mısır", "Kahire"), ("İran", "Tahran"), ("Irak", "Bağdat"),
    ("Çin", "Pekin"), ("Hindistan", "Yeni Delhi"), ("Güney Kore", "Seul"), ("Kanada", "Ottawa"),
    ("Brezilya", "Brasilia"), ("Arjantin", "Buenos Aires"), ("Avustralya", "Canberra"), ("Meksika", "Meksiko")
]
YEMEK_SEHIR_LISTESI = [
    ("Künefe", "Hatay"), ("Cağ Kebabı", "Erzurum"), ("İskender Kebap", "Bursa"),
    ("Mantı", "Kayseri"), ("Baklava", "Gaziantep"), ("Tantuni", "Mersin"),
    ("Etli Ekmek", "Konya"), ("Hamsi Tava", "Trabzon"), ("Pide", "Samsun"),
    ("Çiğ Köfte", "Şanlıurfa"), ("Testi Kebabı", "Yozgat"), ("Keşkek", "Aydın")
]
ALL_SEHIRLER = ["Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Trabzon", "Erzurum", "Gaziantep", "Konya", "Samsun", "Adana", "Hatay", "Mersin", "Kayseri", "Şanlıurfa", "Yozgat", "Aydın"]
DNY_MUTFAK_LISTESI = [
    ("Sushi", "Japonya"), ("Pizza", "İtalya"), ("Taco", "Meksika"),
    ("Kruvasan", "Fransa"), ("Hamburger", "Amerika Birleşik Devletleri"),
    ("Paella", "İspanya"), ("Makarna", "İtalya"), ("Pad Thai", "Tayland")
]
ALL_ULKELER = ["Japonya", "İtalya", "Meksika", "Fransa", "Amerika Birleşik Devletleri", "İspanya", "Çin", "Almanya", "İngiltere", "Brezilya", "Türkiye"]
HARITA_HAVUZU = [
    ("Haritalarda yön bulmamıza yardımcı olan ve genellikle kuzeyi gösteren işaret nedir?", "Kuzey oku (Pusula gülü)", ["Ölçek", "Lejant", "Eş yükselti"]),
    ("Fiziki haritalarda suları ve denizleri göstermek için hangi renk kullanılır?", "Mavi", ["Yeşil", "Kahverengi", "Sarı"]),
    ("Haritalarda yer alan sembollerin ne anlama geldiğini gösteren tabloya ne denir?", "Lejant (Harita anahtarı)", ["Ölçek", "Pusula gülü", "Kuzey oku"])
]
ICAT_HAVUZU = [
    ("Telefonu icat ederek ilk sesli iletişim kuran mucit kimdir?", "Alexander Graham Bell", ["Thomas Edison", "Nikola Tesla", "Isaac Newton"]),
    ("Ampulü icat ederek elektriğin aydınlatmada kullanılmasını sağlayan kimdir?", "Thomas Edison", ["Alexander Graham Bell", "Albert Einstein", "Wright Kardeşler"])
]
GENEL_KULTUR_HAVUZU = [
    ("Dünyanın en uzun nehri olarak bilinen Nil Nehri hangi kıtadadır?", "Afrika", ["Asya", "Avrupa", "Amerika"]),
    ("Türkiye Cumhuriyeti'nin kurucusu ve ilk cumhurbaşkanı kimdir?", "Mustafa Kemal Atatürk", ["Fatih Sultan Mehmet", "İsmet İnönü", "Kanuni Sultan Süleyman"])
]

# =========================================================
# 5. DİNAMİK VE MİLYONLARCA KOMBİNASYONLU SORU ÜRETİCİ
# =========================================================
def dinamik_soru_uretici(ders, unite):
    u_low = unite.lower()
    kisi = random.choice(ISIMLER)
    nesne = random.choice(NESNELER)
    kisi2 = random.choice([i for i in ISIMLER if i != kisi])

    # --- MATEMATİK ---
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

    # --- FEN BİLİMLERİ ---
    elif ders == "Fen Bilimleri":
        if "1. ünite" in u_low:
            q, ans, celd = random.choice(FEN_UNITE_1_MATRIS)
        elif "2. ünite" in u_low:
            q, ans, celd = random.choice(FEN_UNITE_2)
        elif "3. ünite" in u_low:
            q, ans, celd = random.choice(FEN_UNITE_3)
        elif "4. ünite" in u_low:
            q, ans, celd = random.choice(FEN_UNITE_4)
        else:
            q, ans, celd = random.choice(FEN_UNITE_5)
        return {"soru": f"{kisi} fen bilimleri dersinde araştırıyor: {q}", "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # --- TÜRKÇE ---
    elif ders == "Türkçe":
        if "1. tema" in u_low:
            q, ans, celd = random.choice(TURKCE_ANLAM)
        elif "2. tema" in u_low:
            q, ans, celd = random.choice(TURKCE_CUMLE)
        elif "3. tema" in u_low:
            q, ans, celd = random.choice(TURKCE_PARAGRAF)
        else:
            q, ans, celd = random.choice(TURKCE_YAZIM)
        return {"soru": f"{kisi} Türkçe testini çözüyor: {q}", "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # --- SOSYAL BİLGİLER ---
    elif ders == "Sosyal Bilgiler":
        if "1. ünite" in u_low:
            q, ans, celd = random.choice(SOSYAL_UNITE_1)
        elif "2. ünite" in u_low:
            q, ans, celd = random.choice(SOSYAL_UNITE_2)
        elif "3. ünite" in u_low:
            q, ans, celd = random.choice(SOSYAL_UNITE_3)
        else:
            q, ans, celd = random.choice(SOSYAL_UNITE_4)
        return {"soru": f"{kisi} sosyal bilgiler çalışmasında soruyor: {q}", "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # --- DİN KÜLTÜRÜ VE AHLAK BİLGİSİ ---
    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        if "1. ünite" in u_low:
            q, ans, celd = random.choice(DIN_UNITE_1)
        elif "2. ünite" in u_low:
            q, ans, celd = random.choice(DIN_UNITE_2)
        else:
            q, ans, celd = random.choice(DIN_UNITE_3)
        return {"soru": q, "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # --- İNGİLİZCE ---
    elif ders == "İngilizce":
        if "unit 1" in u_low:
            q, ans, celd = random.choice(ING_UNITE_1)
        elif "unit 2" in u_low:
            q, ans, celd = random.choice(ING_UNITE_2)
        elif "unit 3" in u_low:
            q, ans, celd = random.choice(ING_UNITE_3)
        else:
            q, ans, celd = random.choice(ING_UNITE_4)
        return {"soru": f"Teacher asks {kisi}: {q}", "siklar": [ans] + celd, "dogru": ans, "gorsel_svg": None}

    # --- BİLGİ YARIŞMASI ---
    else:
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
# 6. EŞİT PAYLAŞTIRICILI SORU LİSTESİ OLUŞTURUCU
# =========================================================
def ders_sirali_soru_uret(secilen_uniteler, hedef_sayi):
    if not secilen_uniteler:
        return []

    toplam_secilen = len(secilen_uniteler)
    temel_pay = hedef_sayi // toplam_secilen
    kalan = hedef_sayi % toplam_secilen

    tam_soru_listesi = []
    hash_set = set()

    for idx, (ders, unite) in enumerate(secilen_uniteler):
        bu_unite_hedef = temel_pay + (1 if idx < kalan else 0)
        
        uretilen_sayi = 0
        deneme = 0
        while uretilen_sayi < bu_unite_hedef and deneme < 5000:
            deneme += 1
            s = dinamik_soru_uretici(ders, unite)
            s["ders"] = ders
            s["unite"] = unite
            
            random.shuffle(s["siklar"])

            # Benzersizlik parmak izi (hash) kontrolü
            fingerprint = hashlib.sha256((s["soru"] + str(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                tam_soru_listesi.append(s)
                uretilen_sayi += 1

    # Tam istenen hedef sayıyı tam tutturmak için karıştırıp döndürelim
    random.shuffle(tam_soru_listesi)
    return tam_soru_listesi[:hedef_sayi]

# =========================================================
# 7. STREAMLIT ARAYÜZÜ
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
    "Toplam Soru Sayısı (20-100 aralığında):", 
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
            with st.spinner("Seçilen üniteler arasında sorular eşit paylaştırılarak anlık üretiliyor..."):
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
    st.success("✅ Sorularınız Eşit Paylaşımla Başarıyla Oluşturuldu!")
    
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
