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
        "4. Kategori: Genel Kültür"
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
# DÜNYA ÜLKELERİ VE BAŞKENTLERİ SÖZLÜĞÜ
# =========================================================
DUNYA_ULKELERI = {
    "Türkiye": "Ankara",
    "Almanya": "Berlin",
    "Fransa": "Paris",
    "İtalya": "Roma",
    "İspanya": "Madrid",
    "Birleşik Krallık": "Londra",
    "Rusya": "Moskova",
    "Çin": "Pekin",
    "Japonya": "Tokyo",
    "Hindistan": "Yeni Delhi",
    "Amerika Birleşik Devletleri": "Washington",
    "Kanada": "Ottawa",
    "Brezilya": "Brasilia",
    "Arjantin": "Buenos Aires",
    "Avustralya": "Canberra",
    "Güney Kore": "Seul",
    "Mısır": "Kahire",
    "Yunanistan": "Atina",
    "Hollanda": "Amsterdam",
    "İsveç": "Stockholm",
    "Norveç": "Oslo",
    "Danimarka": "Kopenhag",
    "Finlandiya": "Helsinki",
    "Polonya": "Varşova",
    "Ukrayna": "Kiev",
    "Suudi Arabistan": "Riyad",
    "İran": "Tahran",
    "Irak": "Bağdat",
    "Pakistan": "İslamabad",
    "Endonezya": "Cakarta",
    "Meksika": "Meksika",
    "Güney Afrika": "Pretoria",
    "Portekiz": "Lizbon",
    "İsviçre": "Bern",
    "Avusturya": "Viyana",
    "Belçika": "Brüksel",
    "Macaristan": "Budapeşte",
    "Çekya": "Prag",
    "İrlanda": "Dublin",
    "Yeni Zelanda": "Wellington",
    "Azerbaycan": "Bakü",
    "Gürcistan": "Tiflis",
    "Bulgaristan": "Sofya",
    "Romanya": "Bükreş",
    "Sırbistan": "Belgrad",
    "Hırvatistan": "Zagreb",
    "Bosna-Hersek": "Saraybosna",
    "Arnavutluk": "Tiran",
    "Macaristan": "Budapeşte",
    "Katar": "Doha",
    "Birleşik Arap Emirlikleri": "Abu Dabi",
    "Jordan": "Amman",
    "Suriye": "Şam",
    "Lübnan": "Beyrut",
    "İsrail": "Kudüs",
    "Tayland": "Bangkok",
    "Vietnam": "Hanoi",
    "Malezya": "Kuala Lumpur",
    "Singapur": "Singapur",
    "Filipinler": "Manila",
    "Şili": "Santiago",
    "Kolombiya": "Bogota",
    "Peru": "Lima",
    "Venezuela": "Karakas",
    "Küba": "Havana"
}
# =========================================================
# TÜRK MUTFAĞI VE YÖRESEL LEZZETLER SÖZLÜĞÜ (60 Adet)
# =========================================================
TURK_MUTFAGI_YORESEL = {
    "Gaziantep": {"yemek": "Lahmacun / Baklava", "ipucu": "İnce açılmış hamur üzerine zırh kıyması, domates, sarımsak ve özel baharatlar sürülerek taş fırında pişirilir."},
    "Adana": {"yemek": "Adana Kebap", "ipucu": "Zırhla çekilmiş kuzu eti, kuyruk yağı, kırmızı pul biber ve tuzun harmanlanıp şişe basılmasıyla yapılır."},
    "Trabzon": {"yemek": "Kuymak / Mısır Ekmeği", "ipucu": "Mısır unu, tereyağı ve özel yöresel telli peynirin (kolot peyniri) tavada kavrulup pişirilmesiyle hazırlanır."},
    "Hatay": {"yemek": "Künefe", "ipucu": "Özel tel kadayıf arasına tuzsuz Antakya peyniri konularak tepside kızartılır ve sıcak şerbetle servis edilir."},
    "Kayseri": {"yemek": "Mantı", "ipucu": "Küçük hamur parçalarının içine kıymalı harç koyulup kapatıldıktan sonra suda haşlanır, sarımsaklı yoğurt ve kızarmış sosla yenir."},
    "Erzurum": {"yemek": "Cağ Kebabı", "ipucu": "Kuzu etinin soğan, karabiber ve tuzla terbiye edilip yatay şişe takılarak odun ateşinde döner şeklinde pişirilmesidir."},
    "Bursa": {"yemek": "İskender Kebap", "ipucu": "Özel tırnak pidesi üzerine dizilen yaprak döner, domates sosu, kızgın tereyağı ve yanında yoğurtla servis edilir."},
    "İzmir": {"yemek": "Boyoz", "ipucu": "Un, sıvı yağ ve tahin kullanılarak kat kat açılan, içi boş veya peynirli/ıspanaklı yapılabilen mayasız hamur işidir."},
    "Konya": {"yemek": "Etliekmek", "ipucu": "Çok ince açılmış uzun hamurun üzerine bıçak kıyması ve domates-biber harcı yayılarak fırınlanır."},
    "Eskişehir": {"yemek": "Çibörek", "ipucu": "İnce açılmış daire biçimindeki çiğ kıymalı harcın yarım ay şeklinde kapatılıp kızgın yağda kızartılmasıyla yapılır."},
    "Mersin": {"yemek": "Tantuni", "ipucu": "Kuşbaşı doğranmış yağlı dana etinin pamuk yağı ve toz kırmızı biberle saç tavada hızlıca kavrulup lavaşa dürüm yapılmasıdır."},
    "Şanlıurfa": {"yemek": "Çiğ Köfte", "ipucu": "Bulgur, isot, salça ve baharatların yoğrulma tahtasında hiç pişirilmeden yoğrulmasıdır."},
    "Sivas": {"yemek": "Sivas Köftesi", "ipucu": "Sadece doğal tuz ve mera sığırı etiyle yapılan, içine ekmek içi veya baharat katılmayan özgün bir köfte çeşididir."},
    "Afyonkarahisar": {"yemek": "Afyon Kaymağı ve Sucuğu", "ipucu": "Mandaların sütünden elde edilen yoğun kaymağın yanında, özel baharatlarla harmanlanmış geleneksel sucuğuyla ünlüdür."},
    "Mardin": {"yemek": "Kaburga Dolması", "ipucu": "Kuzu kaburgasının içi bademli, kuş üzümlü ve baharatlı iç pilavla doldurulduktan sonra tencerede uzun süre pişirilmesidir."},
    "Rize": {"yemek": "Muhlama ve Laz Böreği", "ipucu": "Baklavalık yufka arasına özel muhallebi dökülerek yapılan, şerbetli tatlı çeşididir."},
    "Kars": {"yemek": "Kars Kazı ve Gravyer Peyniri", "ipucu": "Yüksek dağlarda beslenen kazların kar yağdıktan sonra tuzlanıp kurutulması ve fırında bulgurla sunulmasıdır."},
    "Malatya": {"yemek": "Kâğıt Kebabı", "ipucu": "Kuzu eti, kuyruk yağı, sarımsak ve biberin yağlı kâğıda sarılarak taş fırında sebzelerle birlikte pişirilmesidir."},
    "Çorum": {"yemek": "Çorum Leblebisi", "ipucu": "Nohudun özel fırınlarda kavrulup dinlendirilmesiyle elde edilen, sarı ve çıtır yapısıyla bilinen atıştırmalıktır."},
    "İsparta": {"yemek": "Fırın Kebabı (Kuyu Kebabı)", "ipucu": "Kuzu etinin derin kuyulardaki meşe odunu ateşinde, hiçbir baharat eklenmeden kendi suyunda saatlerce pişmesidir."},
    "Van": {"yemek": "Van Otlu Peyniri", "ipucu": "İçerisine sirmo, mendil ve yabani sarımsak gibi dağ otları katılarak toprak küplere basılıp salamura edilen peynirdir."},
    "Tokat": {"yemek": "Tokat Kebabı", "ipucu": "Kuzu eti, patlıcan, domates, biber, patates ve sarımsağın özel demir şişlere dizilerek yatay fırında odun ateşinde pişmesidir."},
    "Aydın": {"yemek": "Çökertme Kebabı", "ipucu": "İnce ince doğranmış çıtır patates kızartmalarının üzerine bonfile et, sarımsaklı yoğurt ve domates sosu dökülerek servis edilir."},
    "Erzincan": {"yemek": "Erzincan Tulum Peyniri", "ipucu": "Koyun sütünden yapılan telemeninin keçi derisinden yapılan tulumlara basılarak aylarca olgunlaştırılmasıyla elde edilir."},
    "Nevşehir": {"yemek": "Testi Kebabı", "ipucu": "Kuşbaşı et, sebze ve tereyağının toprak bir testinin içine doldurulup ağzının hamurla kapatılarak tandır ateşinde pişirilmesidir."},
    "Bolu": {"yemek": "Orman Kebabı", "ipucu": "Kuşbaşı kuzu eti, arpacık soğan ve bezelyenin güveçte tereyağı ile harmanlanıp fırınlanmasıyla yapılır."},
    "Çanakkale": {"yemek": "Peynir Helvası", "ipucu": "Tuzsuz taze peynir, un, şeker ve irmik kullanılarak ocakta kavrulan, sıcak veya fırınlanmış olarak sunulan tatlıdır."},
    "Giresun": {"yemek": "Fındık Ezmesi", "ipucu": "Bölgede yetişen kaliteli taze fındıkların kavrulup öğütülerek doğal şekerle krema kıvamına getirilmesidir."},
    "Ordu": {"yemek": "Karalahana Çorbası", "ipucu": "İnce kıyılmış karalahana, mısır yarması, barbunya fasulye ve acı biberin birlikte kaynatılmasıyla yapılır."},
    "Diyarbakır": {"yemek": "Ciğer Kebabı ve Meftune", "ipucu": "Kuzu ciğerinin küp doğranıp şişlere dizilerek mangalda pişirildikten sonra sumaklı soğanla servis edilmesidir."},
    "Antalya": {"yemek": "Piyaz (Tahinli)", "ipucu": "Haşlanmış fasulyenin yumurta, domates, maydanoz ve özel bol tahinli sosla harmanlanmasıyla yapılır."},
    "Bursa": {"yemek": "İnegöl Köfte", "ipucu": "Dana ve kuzu kıymasının karbonat, soğan ve tuzla yoğrularak uzun silindirik şekil verilip izgarada pişirilmesidir."},
    "Sakarya": {"yemek": "Adapazarı Islama Köftesi", "ipucu": "Kıymalı köftelerin kemik suyu ve kırmızı biberle ıslatılmış kızarmış ekmekler eşliğinde sunulmasıdır."},
    "Kocaeli": {"yemek": "Pişmaniye", "ipucu": "Un, şeker, tereyağı ve vanilyanın tel tel çekilerek top şeklinde oluşturulduğu geleneksel tatlıdır."},
    "Tekirdağ": {"yemek": "Tekirdağ Köftesi", "ipucu": "Özel baharatlarla harmanlanmış kıymanın sac ızgarada yassı biçimde pişirilip sosla sunulmasıdır."},
    "Edirne": {"yemek": "Edirne Tava Ciğeri", "ipucu": "Dana ciğerinin incecik yapraklar halinde doğranıp unlanarak kızgın yağda kısa sürede çıtır kızartılmasıdır."},
    "Kırklareli": {"yemek": "Kolaç ve Hardaliye", "ipucu": "Üzüm şırasının vişne yaprağı ve hardal tohumu ile fermente edilerek hazırlanan alkolsüz geleneksel içecektir."},
    "Balıkesir": {"yemek": "Höşmerim Tatlısı", "ipucu": "Tatsız peynir suyunun süzülüp irmik ve şekerle kısık ateşte kavrularak altın sarısı kıvama getirilmesidir."},
    "Çankırı": {"yemek": "Yumurta Tatlısı", "ipucu": "Hamurun kızartıldıktan sonra özel şeker şerbetiyle buluşturulmasıyla yapılan şerbetli tatlıdır."},
    "Kastamonu": {"yemek": "Etli Ekmek ve Çekme Helva", "ipucu": "Un ve yağın kavrulup lif lif teller haline getirilerek hazırlanan hafif ve ağızda dağılan tatlıdır."},
    "Sinop": {"yemek": "Sinop Mantısı", "ipucu": "Üçgen kapatılan minik mantıların üzerine ceviz içi ve erimiş tereyağı dökülerek servis edilmesidir."},
    "Samsun": {"yemek": "Samsun Pidesi (Bafra/Çarşamba)", "ipucu": "Uzun ve kapalı ya da açık şekilde hazırlanan, bol tereyağlı ve kıymalı/peynirli çıtır hamur işidir."},
    "Amasya": {"yemek": "Amasya Çöreği", "ipucu": "Haşhaş ezmesi, ceviz ve tereyağının açılan hamura kat kat sürülüp fırınlanmasıyla yapılır."},
    "Tokat": {"yemek": "Tokat Keşkeği", "ipucu": "Dövülmüş buğday ve etin çömlek içinde odun ateşinde saatlerce ezilerek pişirilmesidir."},
    "Yozgat": {"yemek": "Arabaşı Çorbası", "ipucu": "Un ve suyla yapılan soğuk hamurun, un çorbası eşliğinde hiç çiğnenmeden yutulmasıyla meşhurdur."},
    "Kırşehir": {"yemek": "Kırşehir Çömlek Kebabı", "ipucu": "Koyun eti, arpacık soğan ve biberin çömlek kabında kendi yağıyla fırınlanmasıdır."},
    "Nevşehir": {"yemek": "Nevşehir Kabak Çekirdeği", "ipucu": "Bölgede yetişen kabakların çekirdeklerinin özel tuzlu suyla yıkanıp taş fırınlarda kavrulmasıdır."},
    "Niğde": {"yemek": "Niğde Tava", "ipucu": "Kuşbaşı et, biber ve domatesin tepsiye yayılarak üzerine kuyruk yağı parçalarıyla fırına verilmesidir."},
    "Aksaray": {"yemek": "Aksaray Tava", "ipucu": "Kuzu eti ve sebzelerin toprak güveçte harmanlanarak taş fırında pişirilmesiyle yapılır."},
    "Karaman": {"yemek": "Arabaşı ve Batırık", "ipucu": "İnce bulgur, tahin, domates salçası ve ceviz içinin soğuk suyla yoğrularak çorba kıvamında içilmesidir."},
    "Mersin": {"yemek": "Cezerye", "ipucu": "Havuç, şeker, fındık veya Antep fıstığı ile karanfilin kaynatılıp jel kıvamına getirilmesiyle yapılan tatlıdır."},
    "Osmaniye": {"yemek": "Osmaniye Yerfıstığı", "ipucu": "Bölgenin kırmızı topraklarında yetişen, yüksek yağ oranına ve çıtır lezzete sahip özel kuruyemiştir."},
    "Kilis": {"yemek": "Kilis Tava", "ipucu": "Zırh kıyması, sarımsak, biber ve baharatların tepsiye basılıp dilimlenerek fırınlanmasıdır."},
    "Düzce": {"yemek": "Çerkez Tavuğu ve Mancar", "ipucu": "Haşlanmış tavuk etinin ceviz içi, sarımsak ve toz kırmızı biberli özel sosla harmanlanmasıdır."},
    "Yalova": {"yemek": "Yalova Sütlücesi", "ipucu": "Süt, un ve nişastanın fırında kızartılarak üzerine şerbet dökülmesiyle yapılan hafif tatlıdır."},
    "Bartın": {"yemek": "Bartın Yumurtalı Pidesi", "ipucu": "Pide hamurunun içine peynir ve kırılan bütün yumurtaların pişmeye yakın eklenmesiyle yapılır."},
    "Karabük": {"yemek": "Safranbolu Bükmesi", "ipucu": "Haşhaşlı ve kıymalı iç harcın açılan hamura sarılarak fırında çıtır pişirilmesidir."},
    "Bilecik": {"yemek": "Bilecik Büzgülü Tatlısı", "ipucu": "Yufkanın büzgülü şekilde tepsiye dizilip içi cevizle doldurulduktan sonra şerbetlenmesidir."},
    "Kütahya": {"yemek": "Cimcik Mantısı", "ipucu": "Hamurun çok küçük kareler halinde kesilip ortasından sıkılarak şekillendirilmesiyle yapılır."}
}

# =========================================================
# DÜNYA MUTFAKLARI VE LEZZETLER SÖZLÜĞÜ (60 Adet)
# =========================================================
DUNYA_MUTFAGI_LEZZETLER = {
    "İtalya": {"yemek": "İtalya Pizza / Makarna", "ipucu": "Mayalı hamurun ince açılıp üzerine domates sosu, mozzarella peyniri ve çeşitli malzemeler dizilerek fırınlanmasıyla yapılır."},
    "Japonya": {"yemek": "Japonya Suşi / Ramen", "ipucu": "Özel sirke ile tatlandırılmış haşlanmış pirincin deniz yosunu ve çiğ balıkla sarılmasıdır."},
    "Meksika": {"yemek": "Meksika Taco / Burrito", "ipucu": "Mısır unundan yapılan tortilla ekmeklerinin içine et, fasulye ve avokado sosu doldurularak yenir."},
    "Çin": {"yemek": "Çin Noodle", "ipucu": "Buğday veya pirinç unundan yapılan uzun ince şerit halindeki eriştelerin sebze ve etle wok tavada sotelemesidir."},
    "Fransa": {"yemek": "Fransa Kroasan", "ipucu": "Un, maya ve bolca tereyağının kat kat açılarak hilal şeklinde fırınlanmasıyla elde edilen gevrek hamur işidir."},
    "Hindistan": {"yemek": "Hindistan Köri Soslu Tavuk", "ipucu": "Tavuk parçalarının zerdeçal, kimyon, kişniş ve acı baharatlardan oluşan yoğun sarı renkli sosla pişirilmesidir."},
    "Amerika Birleşik Devletleri": {"yemek": "ABD Hamburger", "ipucu": "Yuvarlak sandviç ekmeğinin arasına dana etinden yapılan köfte, marul, domates ve soslar konularak hazırlanır."},
    "Yunanistan": {"yemek": "Yunanistan Musakka", "ipucu": "Patlıcan dilimleri ve kıymalı domates sosunun kat kat dizilerek üzerine bechamel sos dökülüp fırınlanmasıyla yapılır."},
    "İspanya": {"yemek": "İspanya Paella", "ipucu": "Pirinç, safran, zeytinyağı ve deniz ürünleriyle geniş tabakalı tavada pişirilen geleneksel yemektir."},
    "Almanya": {"yemek": "Almanya Prezel ve Sosis", "ipucu": "Düğümlenmiş şekle sahip, üzeri iri tuz taneleriyle kaplı, dışı çıtır içi yumuşak bir unlu mamüldür."},
    "Tayland": {"yemek": "Tayland Pad Thai", "ipucu": "Pirinç eriştelerinin yumurta, tofu, fıstık, balık sosu ve karidesle wok tavada harmanlanıp pişirilmesidir."},
    "Güney Kore": {"yemek": "Güney Kore Kimchi", "ipucu": "Çin lahanası ve turpun sarımsak, zencefil ve acı biber salçasıyla fermente edilmesiyle yapılan garnitürdür."},
    "Brezilya": {"yemek": "Brezilya Feijoada", "ipucu": "Siyah fasulye, domuz eti ve sığır etinin toprak tencerede kısık ateşte uzun süre pişirilmesiyle yapılan ulusal yemektir."},
    "Lübnan": {"yemek": " Lübnan Falafel ve Humus", "ipucu": "Nohudun ezilip baharatlar ve taze otlarla karıştırılarak yuvarlak köfteler halinde kızgın yağda kızartılmasıdır."},
    "Arjantin": {"yemek": "Arjantin Empanada", "ipucu": "Ay şeklindeki hamur parçalarının içine kıymalı veya peynirli harç doldurularak fırında pişirilmesidir."},
    "Vietnam": {"yemek": "Vietnam Pho", "ipucu": "Pirinç erişteleri, uzun süre kemik suyuyla kaynatılan et dilimleri ve taze otlarla servis edilen çorbadır."},
    "İngiltere": {"yemek": "İngiltere Fish and Chips", "ipucu": "Beyaz etli balık filetosunun hamur harcına bulanarak kızartılması ve yanında patates kızartmasıyla sunulmasıdır."},
    "Fas": {"yemek": "Fas Kuskus", "ipucu": "Buğday irmik tanelerinin buharda pişirilip üzerine sebze, et ve özel baharatlı sos dökülerek servis edilmesidir."},
    "Rusya": {"yemek": "Rusya Borsç Çorbası", "ipucu": "Kırmızı pancarın başrolde olduğu, lahana ve et eklenerek üzerine ekşi krema ile sunulan çorbadır."},
    "İsveç": {"yemek": "İsveç İsveç Köftesi", "ipucu": "Kıyma, soğan ve baharatlardan yapılan küçük yuvarlak köftelerin krema bazlı kahverengi sos ve reçelle servis edilmesidir."},
    "Belçika": {"yemek": "Belçika Wafflesu", "ipucu": "Özel kalıplarda pişirilen, dışı çıtır içi yumuşak hamurun üzerine çikolata, çilek ve krema sürülerek yenmesidir."},
    "İsviçre": {"yemek": "İsviçre Fondü", "ipucu": "Çeşitli eritilmiş peynirlerin özel bir tencerede ısıtılarak ekmek parçalarının sosa batırılarak yendiği yemektir."},
    "Macaristan": {"yemek": "Macaristan Gulaş", "ipucu": "Dana eti, patates ve kök sebzelerin yoğun miktarda tatlı kırmızı toz biber ile tencere yahni şeklinde pişmesidir."},
    "Ukrayna": {"yemek": "Ukrayna Varenyky", "ipucu": "İnce açılmış mayasız hamurun içine patates veya mantar koyulup kapatılarak suda haşlanan bir çeşit mantıdır."},
    "Küba": {"yemek": "Küba Sandviçi", "ipucu": "Ekmek arasına domuz eti, jambon, peynir, turşu ve hardal konularak pres makinesinde ısıtılarak hazırlanan yemektir."},
    "Mısır": {"yemek": "Mısır Kişeri", "ipucu": "Mercimek, makarna, pirinç ve nohut karışımının üzerine kızarmış soğan ve domates sosu dökülerek yapılan yemektir."},
    "Avustralya": {"yemek": "Avustralya Meat Pie (Etli Turta)", "ipucu": "Kıymalı ve soğanlı koyu sosun, ufalanan tereyağlı turta hamuruyla kaplanıp fırında pişirilmesiyle elde edilir."},
    "Endonezya": {"yemek": "Endonezya Nasi Goreng", "ipucu": "Haşlanmış pirincin soya sosu, sarımsak, sebze ve etle tavada karıştırılarak kavrulmasıdır."},
    "İran": {"yemek": "İran Fesencan", "ipucu": "Tavuk veya ördek etinin dövülmüş ceviz içi ve nar ekşisi sosuyla uzun süre kısık ateşte pişirilmesiyle yapılır."},
    "Fas": {"yemek": "Fas Tajin", "ipucu": "Konik biçimli toprak kaplarda et ve sebzelerin kendi suyuyla uzun süre pişirildiği Kuzey Afrika yemeğidir."},
    "Portekiz": {"yemek": "Portekiz Pastel de Nata", "ipucu": "Çıtır milföy hamurunun içi özel krema dolgusuyla doldurularak fırında üzeri karamelize olana kadar pişirilen tarttır."},
    "Avusturya": {"yemek": "Avusturya Schnitzel", "ipucu": "Dana bonfile etinin dövülerek inceltilmesi, un, yumurta ve galeta ununa bulanarak kızgın yağda kızartılmasıdır."},
    "Polonya": {"yemek": "Polonya Pierogi", "ipucu": "Yarım ay şeklinde kapatılmış, içi patates, peynir veya kıymayla doldurulan haşlanmış Polonya mantısıdır."},
    "Çekya": {"yemek": "Çekya Trdelnik", "ipucu": "Şeker ve cevizle kaplanmış hamurun metal silindirlere sarılarak ateş üstünde döndürülen tatlı çöreğidir."},
    "Hollanda": {"yemek": "Hollanda Stroopwafel", "ipucu": "İki ince waffle katmanının arasına karamel bazlı şurup sürülerek yapıştırılan tatlı bisküvidir."},
    "Danimarka": {"yemek": "Danimarka Hamur İşi (Danish)", "ipucu": "Tereyağlı hamur katmanlarının arasına reçel, çikolata veya krem peynir sürülerek hazırlanan tatlı hamur işidir."},
    "Norveç": {"yemek": "Norveç Lutefisk", "ipucu": "Kurutulmuş beyaz balığın su ve sodalı potas çözeltisinde bekletilip fırınlanmasıyla yapılan geleneksel yemektir."},
    "Finlandiya": {"yemek": "Finlandiya Lohikeitto", "ipucu": "Taze somon balığı parçaları, patates, pırasa ve krema ile yapılan lezzetli balık çorbasıdır."},
    "İrlanda": {"yemek": "İrlanda Irish Stew (Yahni)", "ipucu": "Kuzu eti, patates, soğan ve havuç kullanılarak ağır ateşte güveçte pişirilen geleneksel yemektir."},
    "Romanya": {"yemek": "Romanya Sarmale", "ipucu": "Lahana yapraklarının içine kıymalı ve pirinçli harç sarılarak kısık ateşte domates sosuyla pişirilmesidir."},
    "Bulgaristan": {"yemek": "Bulgaristan Tarator Çorbası", "ipucu": "Yoğurt, salatalık, sarımsak, zeytinyağı ve cevizle yapılan soğuk servis edilen yaz çorbasıdır."},
    "Sırbistan": {"yemek": "Sırbistan Cevapi", "ipucu": "Baharatlı kıyma karışımından yapılan küçük silindirik köftelerin somun ekmek ve soğanla sunulmasıdır."},
    "Hırvatistan": {"yemek": "Hırvatistan Crni Rižot (Siyah Risotto)", "ipucu": "Mürekkep balığı mürekkebiyle siyah renk verilen, deniz ürünlü geleneksel pirinç pilavıdır."},
    "Bosna-Hersek": {"yemek": "Bosna Hersek Boşnak Böreği", "ipucu": "Elde açılan incecik yufkaların arasına kıymalı, peynirli veya patatesli harç konularak spiral şeklinde sarılmasıdır."},
    "Gürcistan": {"yemek": "Gürcistan Haçapuri", "ipucu": "Kayık şeklinde açılan mayalı hamurun içine bolca peynir ve tereyağı, pişmeye yakın da yumurta kırılmasıyla yapılır."},
    "Azerbaycan": {"yemek": "Azerbaycan Şah Pilavı", "ipucu": "Lavaş yufkası kaplı tencerenin içinde safranlı pirinç, kuzu eti ve kuru meyvelerle fırında pişirilen ana yemektir."},
    "İsrail": {"yemek": "İsrail Shakshuka (Şakşuka)", "ipucu": "Domates sosu, biber, soğan ve baharatlar içinde pişirilen sosun üzerine bütün yumurta kırılmasıyla yapılır."},
    "Surudi": {"yemek": "Surudi Mütebbel", "ipucu": "Közlenmiş patlıcanların tahin, sarımsak, yoğurt ve zeytinyağı ile ezilerek püre haline getirilmesidir."},
    "Japonya": {"yemek": "Japonya Tempura", "ipucu": "Karides ve sebze parçalarının buzlu özel unlu harca bulanarak derin ve kızgın yağda çıtır kızartılmasıdır."},
    "Malezya": {"yemek": "Malezya Laksa", "ipucu": "Baharatlı ve hindistan cevizi sütü içeren yoğun soslu, deniz ürünlü veya tavuklu erişte çorbasıdır."},
    "Singapur": {"yemek": "Singapur Chili Crab (Acılı Yengeç)", "ipucu": "Büyük yengeçlerin domates ve acı biberli koyu, tatlı-ekşi bir sosla wok tavada pişirilmesidir."},
    "Filipinler": {"yemek": "Filipinler Adobo", "ipucu": "Tavuz veya domuz etinin soya sosu, sirke, sarımsak ve karabiberle uzun süre marine edilip pişirilmesidir."},
    "Şili": {"yemek": "Şili Completo", "ipucu": "Uzun sosisli sandviç ekmeğinin içine sosis, bolca avokado ezmesi, domates ve mayonez konulmasıdır."},
    "Kolombiya": {"yemek": "Kolombiya Arepa", "ipucu": "Mısır unundan yapılan yuvarlak ve yassı ekmeklerin ızgarada pişirilip içi açılarak peynir veya etle doldurulmasıdır."},
    "Peru": {"yemek": "Peru Ceviche", "ipucu": "Çiğ balık parçalarının taze limon suyu, kırmızı soğan, acı biber ve mısırla marine edilerek pişirilmeden sunulmasıdır."},
    "Venezuela": {"yemek": "Venezuela Pabellón Criollo", "ipucu": "Pilav, siyah fasulye, didilmiş sığır eti ve kızarmış tatlı muz dilimlerinin bir arada sunulmasıdır."},
    "Etiyopya": {"yemek": "Etiyopya İncera", "ipucu": "Tef unundan yapılan, süngerimsi ve ekşimsi dokuya sahip büyük ve esnek mayalı gözleme ekmektir."},
    "Gana": {"yemek": "Gana Jollof Pilavı", "ipucu": "Pirinç, domates sosu, soğan, biber ve çeşitli baharatların tek tencerede et suyuyla pişirilmesidir."},
    "Nijerya": {"yemek": "Nijerya Pounded Yam (Dövülmüş Yam)", "ipucu": "Yam bitkisinin kökünün haşlanıp sakız kıvamına gelene kadar dövülerek top şeklinde et yemekleriyle yenmesidir."},
    "Güney Afrika": {"yemek": "Güney Afrika Bobotie", "ipucu": "Baharatlı kıymanın üzerine yumurtalı ve sütlü sos dökülerek fırınlanan geleneksel et yemeğidir."}
}
 

# =========================================================
# GENEL KÜLTÜR VE EĞLENCELİ BİLGİLER SÖZLÜĞÜ (175 Soru)
# =========================================================
GENEL_KULTUR_SORULARI = [
    # --- BÖLÜM 1: BİLİM VE DOĞA (1-25) ---
    {
        "soru": "Hangi hayvanın kalbi karideslerinin kafasında yer alır ve vücut yapısı oldukça ilginçtir?",
        "siklar": ["Karides", "Ahtapot", "Denizanası", "Yengeç"],
        "dogru": "Karides"
    },
    {
        "soru": "Dünyanın en küçük bağımsız devleti olan Vatikan'ın yüz ölçümü yaklaşık olarak kaç kilometrekaredir?",
        "siklar": ["0.44 km²", "5.2 km²", "12.8 km²", "1.5 km²"],
        "dogru": "0.44 km²"
    },
    {
        "soru": "Hangi gezegen Güneş Sistemi'nde saat yönünde (diğer gezegenlerin aksine doğudan batıya) dönen tek gezegendir?",
        "siklar": ["Venüs", "Mars", "Neptün", "Merkür"],
        "dogru": "Venüs"
    },
    {
        "soru": "İnsan vücudunda, doğduğumuzda yaklaşık 300 kemik bulunurken, yetişkin bir insanda bu sayı kemiklerin birleşmesiyle kaça düşer?",
        "siklar": ["206", "180", "245", "220"],
        "dogru": "206"
    },
    {
        "soru": "Mona Lisa tablosu hangi ünlü müzede sergilenmektedir ve her gün binlerce ziyaretçi akınına uğrar?",
        "siklar": ["Louvre Müzesi", "British Museum", "Vatikan Müzeleri", "Metropolitan Sanat Müzesi"],
        "dogru": "Louvre Müzesi"
    },
    {
        "soru": "Hangi ülke 'Bin Göller Ülkesi' olarak anılır ve yüz binlerce göle ev sahipliği yapar?",
        "siklar": ["Finlandiya", "Kanada", "İsveç", "Norveç"],
        "dogru": "Finlandiya"
    },
    {
        "soru": "Nobel Ödülleri her yıl hangi iki şehrin ev sahipliğinde törenlerle sahiplerine verilir?",
        "siklar": ["Stockholm ve Oslo", "Cenevre ve Zürih", "Londra ve Paris", "Berlin ve Viyana"],
        "dogru": "Stockholm ve Oslo"
    },
    {
        "soru": "Dünyanın en uzun sıradağları olan And Dağları hangi kıtada yer almaktadır?",
        "siklar": ["Güney Amerika", "Asya", "Kuzey Amerika", "Afrika"],
        "dogru": "Güney Amerika"
    },
    {
        "soru": "Hangi elementin kimyasal simgesi 'Au' harfleridir ve kelime kökeni latince parlayan şafak anlamına gelir?",
        "siklar": ["Altın", "Gümüş", "Bakır", "Alüminyum"],
        "dogru": "Altın"
    },
    {
        "soru": "Modern Olimpiyat Oyunları'nı 1896 yılında yeniden başlatan ve uluslararası Olimpiyat Komitesi'nin kurucusu olan Fransız tarihçi kimdir?",
        "siklar": ["Pierre de Coubertin", "Louis Pasteur", "Victor Hugo", "Emile Zola"],
        "dogru": "Pierre de Coubertin"
    },
    {
        "soru": "İtalya mutfağının dünyaca ünlü 'Risotto' yemeği temel olarak hangi ana malzemeden yapılır?",
        "siklar": ["Pirinç", "Makarna", "Patates", "Bulgur"],
        "dogru": "Pirinç"
    },
    {
        "soru": "Dünya'nın en derin noktası olan Mariana Çukuru hangi okyanusta yer almaktadır?",
        "siklar": ["Pasifik Okyanusu", "Atlantik Okyanusu", "Hint Okyanusu", "Arktik Okyanusu"],
        "dogru": "Pasifik Okyanusu"
    },
    {
        "soru": "Ünlü 'Yıldızları Gözleyen' veya 'Yıldızlı Gece' tablosuyla tanınan post-empresyonist ressam kimdir?",
        "siklar": ["Vincent van Gogh", "Claude Monet", "Pablo Picasso", "Salvador Dali"],
        "dogru": "Vincent van Gogh"
    },
    {
        "soru": "Hangi ülke 1930 yılında düzenlenen ilk FIFA Dünya Kupası'na hem ev sahipliği yapmış hem de kupayı kazanmıştır?",
        "siklar": ["Uruguay", "Brezilya", "Arjantin", "İtalya"],
        "dogru": "Uruguay"
    },
    {
        "soru": "Meksika mutfağına ait olan ve geleneksel olarak avokado bazlı hazırlanan soğuk meze/sosun adı nedir?",
        "siklar": ["Guacamole", "Salsa", "Humus", "Tapas"],
        "dogru": "Guacamole"
    },
    {
        "soru": "Rock müzik tarihinin efsanevi grubu Queen'in solisti olan ve ikonik sesiyle tanınan sanatçı kimdir?",
        "siklar": ["Freddie Mercury", "Mick Jagger", "David Bowie", "John Lennon"],
        "dogru": "Freddie Mercury"
    },
    {
        "soru": "Anadolu'nun en eski yazılı belgelerinin bulunduğu, Hitit İmparatorluğu'nun başkenti olan antik şehir hangisidir?",
        "siklar": ["Hattuşa", "Ephesus", "Troy", "Zeugma"],
        "dogru": "Hattuşa"
    },
    {
        "soru": "Japon sinemasının ve animasyon dünyasının devi Studio Ghibli'nin kurucularından olan ünlü yönetmen kimdir?",
        "siklar": ["Hayao Miyazaki", "Akira Kurosawa", "Makoto Shinkai", "Takeshi Kitano"],
        "dogru": "Hayao Miyazaki"
    },
    {
        "soru": "Dünyanın en uzun nehirlerinden biri olan Nil Nehri hangi denize dökülmektedir?",
        "siklar": ["Akdeniz", "Kızıldeniz", "Hazar Denizi", "Karadeniz"],
        "dogru": "Akdeniz"
    },
    {
        "soru": "İspanya'nın geleneksel pirinç bazlı, deniz ürünleri veya etle yapılan ünlü ulusal yemeğinin adı nedir?",
        "siklar": ["Paella", "Lasagna", "Fondue", "Kebab"],
        "dogru": "Paella"
    },
    {
        "soru": "Basketbol ligi NBA'de tüm zamanların en çok sayı atan oyuncuları listesinde zirvede yer alan yıldız basketbolcu kimdir?",
        "siklar": ["LeBron James", "Kareem Abdul-Jabbar", "Michael Jordan", "Kobe Bryant"],
        "dogru": "LeBron James"
    },
    {
        "soru": "Osmanlı İmparatorluğu'nda 'Lale Devri' hangi padişah döneminde yaşanmıştır?",
        "siklar": ["III. Ahmet", "I. Ahmed", "Kanuni Sultan Süleyman", "II. Mahmud"],
        "dogru": "III. Ahmet"
    },
    {
        "soru": "Klasik batı müziğinde 'Ay Işığı Sonatı' (Moonlight Sonata) kim tarafından bestelenmiştir?",
        "siklar": ["Ludwig van Beethoven", "Wolfgang Amadeus Mozart", "Johann Sebastian Bach", "Frédéric Chopin"],
        "dogru": "Ludwig van Beethoven"
    },
    {
        "soru": "Coğrafi keşifler döneminde Ümit Burnu'nu ilk kez aşarak Hindistan deniz yolunu bulan Portokalsefer kaşif kimdir?",
        "siklar": ["Vasco da Gama", "Kristof Kolomb", "Macellan", "Amerigo Vespucci"],
        "dogru": "Vasco da Gama"
    },
    {
        "soru": "Eiffel Kulesi yaz aylarında sıcaklığın etkisiyle termal genleşme sebebiyle yaklaşık kaç santimetre uzar?",
        "siklar": ["15 cm", "5 cm", "30 cm", "2 cm"],
        "dogru": "15 cm"
    },
    {
        "soru": "Hangi hayvan türü düz bir hatta zıplayamaz ve fiziksel yapısı nedeniyle sadece öne doğru yürüyebilir?",
        "siklar": ["Fil", "Zürafa", "Penguen", "Su Aygırı"],
        "dogru": "Fil"
    },
    {
        "soru": "Dünyanın en büyük okyanusu olan Pasifik Okyanusu'nun en derin noktası hangi çukurdur?",
        "siklar": ["Mariana Çukuru", "Puerto Rico Çukuru", "Sunda Çukuru", "Java Çukuru"],
        "dogru": "Mariana Çukuru"
    },
    {
        "soru": "Hangi ülkenin bayrağı dünyada dikdörtgen veya kare olmayan (özel iki üçgen dilim formunda) tek ulusal bayraktır?",
        "siklar": ["Nepal", "Bhutan", "Moğolistan", "Sri Lanka"],
        "dogru": "Nepal"
    },
    {
        "soru": "İnsan beyninin bilgi işleme hızı bakımından en aktif olduğu ve en çok rüya gördüğü evre hangisidir?",
        "siklar": ["REM Uykusu", "Derin Uyku", "NREM Uykusu", "Yarı Uyanıklık"],
        "dogru": "REM Uykusu"
    },
    {
        "soru": "Dünya üzerindeki tatlı su kaynaklarının yaklaşık yüzde kaçı kutuplarda ve buzullarda donmuş halde bulunur?",
        "siklar": ["%68", "%90", "%45", "%80"],
        "dogru": "%68"
    },
    {
        "soru": "Hangi antik kentin kalıntıları arasında yer alan ve dünyanın yedi harikasından biri olan heykel tunçtan yapılmış Rodos Heykeli'dir?",
        "siklar": ["Rodos Adası", "İskenderiye", "Babil", "Olimpia"],
        "dogru": "Rodos Adası"
    },
    {
        "soru": "Şahmeran efsanesiyle bilinen ve binlerce yıllık tarihi olan dicle kenarındaki antik şehirimiz hangisidir?",
        "siklar": ["Mardin", "Diyarbakır", "Şanlıurfa", "Gaziantep"],
        "dogru": "Mardin"
    },
    {
        "soru": "Hangi ünlü fizikçi, görelilik teorisini geliştirmiş ve 1921 yılında Nobel Fizik Ödülü'nü kazanmıştır?",
        "siklar": ["Albert Einstein", "Isaac Newton", "Nikola Tesla", "Stephen Hawking"],
        "dogru": "Albert Einstein"
    },
    {
        "soru": "Dünyanın en eski ve en büyük kapalı çarşılarından biri olan Kapalıçarşı hangi padişah döneminde kurulmaya başlanmıştır?",
        "siklar": ["Fatih Sultan Mehmet", "Kanuni Sultan Süleyman", "Yavuz Sultan Selim", "II. Murad"],
        "dogru": "Fatih Sultan Mehmet"
    },
    {
        "soru": "Hangi bitki türü dünyanın en hızlı büyüyen bitkisi unvanına sahiptir ve günde neredeyse bir metre uzayabilir?",
        "siklar": ["Bambu", "Kavak", "Söğüt", "Palmiye"],
        "dogru": "Bambu"
    },
    {
        "soru": "Olimpiyat halkalarında yer alan beş farklı renk hangi kıtaları simgelemektedir ve toplam kaç renktir?",
        "siklar": ["Avrupa, Asya, Afrika, Amerika, Okyanusya", "Avrupa, Asya, Afrika, Amerika, Antarktika", "Kuzey ve Güney Amerika ayrı sayılır", "Sadece dünya renkleridir"],
        "dogru": "Avrupa, Asya, Afrika, Amerika, Okyanusya"
    },
    {
        "soru": "Hangi kuş türü uçabilen ancak yüzebilen ama yürüyemeyen değil, tam tersi uçamayan fakat dünyanın en hızlı koşan kuşudur?",
        "siklar": ["Devekuşu", "Penguen", "Kivi", "Hindi"],
        "dogru": "Devekuşu"
    },
    {
        "soru": "Türkiye'nin ilk UNESCO Dünya Mirası Listesi'ne giren kültürel varlıklarından biri olan Divriği Ulu Cami hangi ilimizdedir?",
        "siklar": ["Sivas", "Erzurum", "Kayseri", "Konya"],
        "dogru": "Sivas"
    },
    {
        "soru": "İnsan gözü yaklaşık olarak kaç farklı renk tonunu birbirinden ayırt edebilir ve algılayabilir?",
        "siklar": ["10 milyon", "1 milyon", "100 bin", "50 milyon"],
        "dogru": "10 milyon"
    },
    {
        "soru": "Hangi müzik aleti klavyeli çalgılar ailesine dahil olmasına rağmen tellere vuran küçük çekiçler yerine telleri kopararak ses çıkarır?",
        "siklar": ["Klavesin (Cembalo)", "Piyano", "Akordiyon", "Org"],
        "dogru": "Klavesin (Cembalo)"
    },
    {
        "soru": "Sinema tarihinin en çok Oscar kazanan (11 Oscar) yapımları arasında yer alan, Jack Nicholson'ın başrolünde oynadığı 1975 yapımı dram filmi hangisidir?",
        "siklar": ["Guguk Kuşu (One Flew Over the Cuckoo's Nest)", "Baba (The Godfather)", "Titanic", "Yüzüklerin Efendisi: Kralın Dönüşü"],
        "dogru": "Guguk Kuşu (One Flew Over the Cuckoo's Nest)"
    },
    {
        "soru": "Tüm zamanların en çok gişe yapan bilim kurgu serilerinden biri olan 'Matrix' film trilojisinin yönetmenleri kimlerdir?",
        "siklar": ["Wachowski Kardeşler", "Christopher Nolan", "Quentin Tarantino", "Martin Scorsese"],
        "dogru": "Wachowski Kardeşler"
    },
    {
        "soru": "Marvel Sinematik Evreni'nin temellerini atan ve 2008 yılında vizyona giren ilk film hangisidir?",
        "siklar": ["Iron Man", "Thor", "Captain America: The First Avenger", "The Avengers"],
        "dogru": "Iron Man"
    },
    {
        "soru": "Hangi animasyon filmi, Akademi Önerleri'nde (Oscar) 'En İyi Animasyon Film' ödülünü kazanan ilk el çizimi (geleneksel animasyon) olmayan veya ilk Pixar yapımı olma özelliğini taşır?",
        "siklar": ["Oyuncak Hikayesi (Toy Story)", "Kayıp Balık Nemo", "Shrek", "Aslan Kral"],
        "dogru": "Oyuncak Hikayesi (Toy Story)"
    },
    {
        "soru": "Stanley Kubrick'in yönettiği, sinema tarihinin başyapıtlarından biri olan 2001: Bir Uzay Macerası (2001: A Space Odyssey) filmindeki ikonik yapay zeka bilgisayarının adı nedir?",
        "siklar": ["HAL 9000", "Skynet", "JARVIS", "DATA"],
        "dogru": "HAL 9000"
    },
    {
        "soru": "J.R.R. Tolkien'in epik fantastik evreni 'Yüzüklerin Efendisi' üçlemesinin sinema uyarlamasını yöneten ve En İyi Yönetmen Oscar'ı kazanan Yeni Zelandalı yönetmen kimdir?",
        "siklar": ["Peter Jackson", "James Cameron", "Steven Spielberg", "Ridley Scott"],
        "dogru": "Peter Jackson"
    },
    {
        "soru": "Müzik dünyasında 'Popun Kralı' olarak anılan ve ikonik 'Moonwalk' dansıyla tanınan efsanevi sanatçı kimdir?",
        "siklar": ["Michael Jackson", "Elvis Presley", "Prince", "Freddie Mercury"],
        "dogru": "Michael Jackson"
    },
    {
        "soru": "Christopher Nolan'ın yönettiği ve rüyalar içinde rüya konseptini işleyen 2010 yapımı bilim kurgu filmi hangisidir?",
        "siklar": ["Başlangıç (Inception)", "Yıldızlararası (Interstellar)", "Tenet", "Prestij"],
        "dogru": "Başlangıç (Inception)"
    },
    {
        "soru": "Harry Potter serisinde Hogwarts'ın bilge ve sevilen müdürü Profesör Albus Dumbledore karakterini canlandıran oyunculardan biri değildir?",
        "siklar": ["Daniel Radcliffe", "Richard Harris", "Michael Gambon", "Jude Law"],
        "dogru": "Daniel Radcliffe"
    },
    {
        "soru": "Quentin Tarantino'nun yönettiği, non-lineer (doğrusal olmayan) kurgusu ve unutulmaz diyaloglarıyla sinema tarihine damga vuran 1994 yapımı film hangisidir?",
        "siklar": ["Ucuz Roman (Pulp Fiction)", "Rezervuar Köpekleri", "Kill Bill", "Django Unchained"],
        "dogru": "Ucuz Roman (Pulp Fiction)"
    },

    # --- BÖLÜM 2: TARİH VE COĞRAFYA (26-50) ---
    {
        "soru": "Dünyanın en derin gölü olan ve dünyadaki toplam sıvı tatlı suyun beşte birini barındıran göl hangisidir?",
        "siklar": ["Baykal Gölü", "Hazar Denizi", "Superior Gölü", "Tanganyika Gölü"],
        "dogru": "Baykal Gölü"
    },
    {
        "soru": "Hangi yazar 'Suç ve Ceza', 'Karamazov Kardeşler' gibi dünya edebiyatının başyapıtlarını kaleme almıştır?",
        "siklar": ["Fyodor Dostoyevski", "Lev Tolstoy", "Anton Çehov", "Nikolay Gogol"],
        "dogru": "Fyodor Dostoyevski"
    },
    {
        "soru": "Dünyanın en yüksek şelalesi olan ve Angel Şelalesi hangi ülkede yer almaktadır?",
        "siklar": ["Venezuela", "Brezilya", "Arjantin", "Güney Afrika"],
        "dogru": "Venezuela"
    },
    {
        "soru": "Hangi uzay aracı insanlık tarihinden bu yana Güneş Sistemi'nin dışına çıkmayı başaran ilk insan yapımı nesnedir?",
        "siklar": ["Voyager 1", "Pioneer 10", "New Horizons", "Cassini"],
        "dogru": "Voyager 1"
    },
    {
        "soru": "Anadolu'nun en eski yazılı belgelerinin bulunduğu ve UNESCO Dünya Belleği Listesi'ndeki kazı alanı nerededir?",
        "siklar": ["Kültepe (Kaniş)", "Hattuşa", "Göbeklitepe", "Çatalhöyük"],
        "dogru": "Kültepe (Kaniş)"
    },
    {
        "soru": "Hangi element periyodik tabloda 'Hg' simgesiyle gösterilen ve oda sıcaklığında sıvı halde bulunan tek metaldir?",
        "siklar": ["Cıva", "Kurşun", "Kalay", "Demir"],
        "dogru": "Cıva"
    },
    {
        "soru": "Dünya'nın uydusu olan Ay'ın Dünya'ya her zaman aynı yüzünü göstermesinin temel sebebi nedir?",
        "siklar": ["Kendi ekseni etrafındaki dönme süresi ile yörünge süresinin eşit olması", "Ay'ın hiç dönmemesi", "Dünyanın çekim gücünün sabitlemesi", "Güneş rüzgarları"],
        "dogru": "Kendi ekseni etrafındaki dönme süresi ile yörünge süresinin eşit olması"
    },
    {
        "soru": "Hangi antik medeniyet sıfır (0) rakamını matematik ve astronomi tarihinde ilk kez kullanan ve simgeleyen medeniyettir?",
        "siklar": ["Mayalar / Hintliler", "Romalılar", "Yunanlılar", "Mısırlılar"],
        "dogru": "Mayalar / Hintliler"
    },
    {
        "soru": "Dünyanın en büyük çölü olan Antarktika çölü coğrafi olarak hangi sınıf çöller arasında yer alır?",
        "siklar": ["Soğuk çöl", "Sıcak çöl", "Kumlu çöl", "Kayalık çöl"],
        "dogru": "Soğuk çöl"
    },
    {
        "soru": "Hangi ünlü ressam eserlerinde kariyeri boyunca mavi rengin tonlarını ağırlıklı olarak kullandığı için 'Mavi Dönem' yaşamıştır?",
        "siklar": ["Pablo Picasso", "Vincent van Gogh", "Claude Monet", "Salvador Dali"],
        "dogru": "Pablo Picasso"
    },
    {
        "soru": "Dünyanın en yüksek aktif yanardağı olan Ojos del Salado hangi iki ülkenin sınırında yer almaktadır?",
        "siklar": ["Şili ve Arjantin", "Peru ve Bolivya", "Ekvador ve Kolombiya", "Meksika ve ABD"],
        "dogru": "Şili ve Arjantin"
    },
    {
        "soru": "Hangi deniz canlısı üç kalbe ve mavi kana sahip olmasıyla bilinir?",
        "siklar": ["Ahtapot", "Yunus", "Fok", "Köpekbalığı"],
        "dogru": "Ahtapot"
    },
    {
        "soru": "Türkiye'nin ilk kâğıt fabrikası hangi ilimizde ve hangi yıl kurulmuştur?",
        "siklar": ["İzmit (1934)", "İstanbul (1926)", "Zonguldak (1940)", "Bursa (1930)"],
        "dogru": "İzmit (1934)"
    },
{
        "soru": "Dünyanın en yüksek şelalesi olan ve Venezüela'da yer alan Angel Şelalesi, hangi nehrin kolu üzerinde bulunur?",
        "siklar": ["Churun Nehri", "Amazon Nehri", "Orinoco Nehri", "Parana Nehri"],
        "dogru": "Churun Nehri"
    },
    {
        "soru": "Yüzölçümü bakımından dünyanın en büyük adası olan ve topraklarının büyük kısmı buzulla kaplı olan ada hangisidir?",
        "siklar": ["Grönland", "Madagaskar", "Borneo", "Büyük Britanya"],
        "dogru": "Grönland"
    },
    {
        "soru": "Afrika kıtasının en yüksek dağ masifi olan ve aynı zamanda tırmanılması en kolay sönmüş volkanlardan biri kabul edilen zirve hangisidir?",
        "siklar": ["Kilimanjaro Dağı", "Kenya Dağı", "Ruwenzori Dağı", "Atlas Dağları"],
        "dogru": "Kilimanjaro Dağı"
    },
    {
        "soru": "Dünya üzerindeki tatlı su kaynaklarının en büyük kısmını barındıran, hacim olarak en büyük tatlı su gölü hangisidir?",
        "siklar": ["Baykal Gölü", "Üstün Göl (Lake Superior)", "Victoria Gölü", "Hazar Denizi"],
        "dogru": "Baykal Gölü"
    },
    {
        "soru": "Avrupa ve Asya kıtalarını birbirinden ayıran, aynı zamanda Karadeniz'i Azak Denizi'ne bağlayan boğaz hangisidir?",
        "siklar": ["Kerç Boğazı", "İstanbul Boğazı", "Çanakkale Boğazı", "Cebelitarık Boğazı"],
        "dogru": "Kerç Boğazı"
    },
    {
        "soru": "Dünyanın en kurak çöllerinden biri olan ve Şili sınırları içerisinde yer alan Atakama Çölü hangi okyanus kıyısındadır?",
        "siklar": ["Pasifik Okyanusu", "Atlantik Okyanusu", "Hint Okyanusu", "Arktik Okyanusu"],
        "dogru": "Pasifik Okyanusu"
    },
    {
        "soru": "Hangi ülke, topraklarının tamamı başka bir tek ülkenin (İtalya) sınırları içinde yer alan bir 'enklav' (şehir-devlet) olma özelliğini taşır?",
        "siklar": ["Vatikan", "Monako", "San Marino", "Liechtenstein"],
        "dogru": "Vatikan"
    },
{
        "soru": "Antik Yunan mitolojisinde gökyüzünün, şimşeğin ve tanrıların kralı olan, Olympos'un lideri tanrı kimdir?",
        "siklar": ["Zeus", "Poseidon", "Hades", "Apollo"],
        "dogru": "Zeus"
    },
    {
        "soru": "Roma İmparatorluğu'nu cumhuriyetten imparatorluğa dönüştüren, suikasta kurban giden ünlü Roma lideri kimdir?",
        "siklar": ["Jul Sezar", "Augustus", "Neron", "Mark Antony"],
        "dogru": "Jul Sezar"
    },
    {
        "soru": "Mezopotamya'da inşa edilen, dini törenlerin yapıldığı ve aynı zamanda gözlemevi olarak kullanılan kadim tapınak kulelerinin adı nedir?",
        "siklar": ["Ziggurat", "Piramit", "Obelisk", "Agora"],
        "dogru": "Ziggurat"
    },
    {
        "soru": "Eski Mısır'da firavunların mumyalandıktan sonra konulduğu devasa anıt mezarların genel adı nedir?",
        "siklar": ["Piramit", "Sfenks", "Lahit", "Mastaba"],
        "dogru": "Piramit"
    },
    {
        "soru": "İskenderiye Kütüphanesi'nin de bulunduğu, Büyük İskender tarafından MÖ 331 yılında kurulan antik Mısır liman kenti hangisidir?",
        "siklar": ["İskenderiye", "Babil", "Kartaca", "Memfis"],
        "dogru": "İskenderiye"
    },
    {
        "soru": "Türk mitolojisinde yeryüzünün yaratıcısı, gök tanrısı ve tüm evrenin hâkimi olarak kabul edilen ulu tanrı kimdir?",
        "siklar": ["Gök Tanrı (Ülgen / Han Tengri)", "Erlik Han", "Kayra Han", "Umay Ana"],
        "dogru": "Gök Tanrı (Ülgen / Han Tengri)"
    },
    {
        "soru": "Orta Çağ Avrupa'sında kilisenin skolastik düşüncesine karşı çıkarak bilimin, sanatın ve antik kültürün yeniden doğuşunu simgeleyen dönem hangisidir?",
        "siklar": ["Rönesans", "Reform", "Aydınlanma Çağ", "Endüstri Devrimi"],
        "dogru": "Rönesans"
    },
    {
        "soru": "İskandinav mitolojisinde gök gürültüsü tanrısı olan,sihirli çekici Mjölnir ile tanınan güçlü tanrı kimdir?",
        "siklar": ["Thor", "Odin", "Loki", "Freyr"],
        "dogru": "Thor"
    },
    {
        "soru": "Anadolu'da kurulmuş olan Lidyalıların para birimini (sikkeyi) icat etmeden önce ticaret hangi yöntemle yapılırdı?",
        "siklar": ["Takas (Barter) usulü", "Değerli taşlar", "İstiridye kabukları", "Kâğıt senetler"],
        "dogru": "Takas (Barter) usulü"
    },
    {
        "soru": "Fransız İhtilali'nin patlak vermesinde ve halkın monarşiye karşı ayaklanmasında simgesel bir dönüm noktası olan hapishane baskını hangisidir?",
        "siklar": ["Bastille Baskını", "Versay Sarayı Kuşatması", "Paris Komünü", "Guillotine Devrimi"],
        "dogru": "Bastille Baskını"
    },
{
        "soru": "İtalya'nın Napoli şehrinde doğan ve dünya çapında en popüler fast-food ürünlerinden biri olan geleneksel hamur işi hangisidir?",
        "siklar": ["Pizza", "Hamburger", "Sushi", "Tacos"],
        "dogru": "Pizza"
    },
    {
        "soru": "Japon mutfağının temel taşlarından biri olan, genellikle sirkeli pirinç ve çiğ balık kombinasyonuyla hazırlanan yemeğin adı nedir?",
        "siklar": ["Sushi", "Ramen", "Tempura", "Sashimi"],
        "dogru": "Sushi"
    },
    {
        "soru": "Meksika kökenli olan, mısır unundan yapılan sert veya yumuşak kabukların içerisine et, sebze ve soslar doldurularak servis edilen popüler lezzet hangisidir?",
        "siklar": ["Taco", "Paella", "Falafel", "Kebab"],
        "dogru": "Taco"
    },
    {
        "soru": "Orta Doğu mutfağına ait olan, nohut veya bakla ezmesinin baharatlarla harmanlanıp kızartılmasıyla yapılan popüler vejetaryen lezzet nedir?",
        "siklar": ["Falafel", "Humus", "Tabule", "Şakshuka"],
        "dogru": "Falafel"
    },
    {
        "soru": "Fransız mutfağının en ünlü soslarından biri olan ve temelinde eritilmiş tereyağı, yumurta sarısı ve limon suyu bulunan emülsiyon sos hangisidir?",
        "siklar": ["Hollandez Sosu", "Beşamel Sos", "Mayonez", "Pesto Sos"],
        "dogru": "Hollandez Sosu"
    },
    {
        "soru": "Hindistan mutfağının vazgeçilmezi olan, onlarca farklı baharatın (zerdeçal, kimyon, kişniş vb.) öğütülmesiyle elde edilen karışımın adı nedir?",
        "siklar": ["Garam Masala (Köri)", "Paprika", "Zahter", "Kimyon"],
        "dogru": "Garam Masala (Köri)"
    },
    {
        "soru": "İtalya'nın kuzeyinde doğan, un ve yumurta ile yapılan, ince şeritler halinde kesilen ve genellikle et veya krema soslarıyla sunulan uzun makarna çeşidi hangisidir?",
        "siklar": ["Tagliatelle", "Spagetti", "Penne", "Macaroni"],
        "dogru": "Tagliatelle"
    },
    {
        "soru": "Güney Amerika ülkesi Peru'nun milli yemeği kabul edilen, taze çiğ balığın limon suyu, soğan ve acı biberle marine edilerek pişirilmeden hazırlandığı lezzet nedir?",
        "siklar": ["Ceviche", "Empanada", "Arepa", "Asado"],
        "dogru": "Ceviche"
    },
    {
        "soru": "Çin mutfağında kökenleri yüzyıllar öncesine dayanan, genellikle buharda pişmiş küçük sepetlerde veya kızartılarak servis edilen içi dolgulu hamur işinin adı nedir?",
        "siklar": ["Dim Sum", "Bao", "Wonton", "Spring Roll"],
        "dogru": "Dim Sum"
    },
{
        "soru": "Rönesans döneminin dahi sanatçısı Leonardo da Vinci'nin Paris'teki Louvre Müzesi'nde sergilenen ünlü tablosunun adı nedir?",
        "siklar": ["Mona Lisa", "Son Akşam Yemeği", "İnci Küpeli Kız", "Venüs'ün Doğuşu"],
        "dogru": "Mona Lisa"
    },
    {
        "soru": "Barok dönemin en büyük Alman bestecilerinden biri olan, özellikle 'Brandenburg Konçertoları' ve kilise müziği eserleriyle tanınan sanatçı kimdir?",
        "siklar": ["Johann Sebastian Bach", "Wolfgang Amadeus Mozart", "Antonio Vivaldi", "Frédéric Chopin"],
        "dogru": "Johann Sebastian Bach"
    },
    {
        "soru": "Kübizm akımının öncülerinden olan, 'Guernica' tablosuyla savaşın acılarını gözler önüne seren İspanyol ressam kimdir?",
        "siklar": ["Pablo Picasso", "Salvador Dali", "Claude Monet", "Henri Matisse"],
        "dogru": "Pablo Picasso"
    },
    {
        "soru": "İtalyan besteci Antonio Vivaldi'nin doğanın döngüsünü keman konçertolarıyla betimlediği dünyaca ünlü eser serisinin adı nedir?",
        "siklar": ["Dört Mevsim", "Requiem", "Gece Müziği", "Saraydan Kız Kaçırma"],
        "dogru": "Dört Mevsim"
    },
    {
        "soru": "Sürrealizm (gerçeküstücülük) akımının en önemli temsilcilerinden biri olan, eriyen saatler temalı 'Belleğin Azmi' tablosunun ressamı kimdir?",
        "siklar": ["Salvador Dali", "Rene Magritte", "Joan Miro", "Frida Kahlo"],
        "dogru": "Salvador Dali"
    },
    {
        "soru": "Klasik dönemde henüz çocuk yaşta besteler yapmaya başlayan, 'Sihirli Flüt' ve 'Don Giovanni' gibi operalarıyla bilinen Avusturyalı deha kimdir?",
        "siklar": ["Wolfgang Amadeus Mozart", "Ludwig van Beethoven", "Franz Schubert", "Giuseppe Verdi"],
        "dogru": "Wolfgang Amadeus Mozart"
    },
    {
        "soru": "Vatikan'daki Sistina Şapeli'nin tavanını süsleyen 'Adem'in Yaratılışı' freskini yapan İtalyan Rönesans sanatçısı kimdir?",
        "siklar": ["Michelangelo", "Raffaello Sanzio", "Donatello", "Giotto di Bondone"],
        "dogru": "Michelangelo"
    },
    {
        "soru": "Piyanonun şairi olarak anılan ve özellikle romantik dönem piyano nocturne (gece müziği) eserleriyle tanınan Polonyalı besteci kimdir?",
        "siklar": ["Frédéric Chopin", "Franz Liszt", "Johannes Brahms", "Pyotr İlyiç Çaykovski"],
        "dogru": "Frédéric Chopin"
    },
    {
        "soru": "Hollandalı ressam Johannes Vermeer'in en ünlü eseri olan ve bakışlarıyla ikonlaşan tablosunun adı nedir?",
        "siklar": ["İnci Küpeli Kız", "Sütçü Kız", "Gece Nöbeti", "Ayçiçekleri"],
        "dogru": "İnci Küpeli Kız"
    },
    {
        "soru": "Kuğu Gölü, Fındıkkıran ve Uyuyan Güzel gibi dünyaca ünlü balelerin müziklerini besteleyen Rus romantik dönem sanatçısı kimdir?",
        "siklar": ["Pyotr İlyiç Çaykovski", "Sergey Rachmaninoff", "İgor Stravinski", "Dmitri Şostakoviç"],
        "dogru": "Pyotr İlyiç Çaykovski"
    },
{
        "soru": "Modern Olimpiyat Oyunları tarihinde en çok altın madalya kazanan (23'ü bireysel olmak üzere toplam 23 altın) efsanevi Amerikan yüzücü kimdir?",
        "siklar": ["Michael Phelps", "Mark Spitz", "Usain Bolt", "Carl Lewis"],
        "dogru": "Michael Phelps"
    },
    {
        "soru": "Futbol tarihindeki en prestijli bireysel ödül olan ve her yıl yılın en iyi futbolcusuna verilen ödülün adı nedir?",
        "siklar": ["Ballon d'Or (Altın Top)", "FIFA The Best", "Altın Ayakkabı", "UEFA Yılın Futbolcusu"],
        "dogru": "Ballon d'Or (Altın Top)"
    },
    {
        "soru": "Atletizmde 100 metre ve 200 metre rekorlarını elinde bulunduran, 'dünyanın en hızlı insanı' unvanlı Jamaikalı eski sprinter kimdir?",
        "siklar": ["Usain Bolt", "Yohan Blake", "Justin Gatlin", "Tyson Gay"],
        "dogru": "Usain Bolt"
    },
    {
        "soru": "Tenis dünyasında 'Grand Slam' turnuvaları arasında yer alan toprak kort turnuvası olarak bilinen organizasyon hangisidir?",
        "siklar": ["Roland Garros (Fransa Açık)", "Wimbledon", "Amerika Açık", "Avustralya Açık"],
        "dogru": "Roland Garros (Fransa Açık)"
    },
    {
        "soru": "Basketbolun mucidi olarak kabul edilen ve bu sporu ilk kez kurallara bağlayan beden eğitimi öğretmeni kimdir?",
        "siklar": ["James Naismith", "Abner Doubleday", "William G. Morgan", "Dr. John Naismith"],
        "dogru": "James Naismith"
    },
    {
        "soru": "Formula 1 tarihinde en çok pilotlar şampiyonluğu kazanan rekortmen pilotlar arasında kimler yer alır?",
        "siklar": ["Michael Schumacher ve Lewis Hamilton", "Ayrton Senna ve Alain Prost", "Max Verstappen ve Sebastian Vettel", "Fernando Alonso ve Niki Lauda"],
        "dogru": "Michael Schumacher ve Lewis Hamilton"
    },
    {
        "soru": "Dünya Kupası tarihinde en çok şampiyonluk kazanan ülke futbol takımı hangisidir?",
        "siklar": ["Brezilya", "Almanya", "Arjantin", "İtalya"],
        "dogru": "Brezilya"
    },
    {
        "soru": "Bisiklet yarışlarının en ünlüsü ve en prestijlisi olan 'Tour de France' (Fransa Bisiklet Turu) geleneksel olarak hangi renkteki mayo ile lideri ödüllendirir?",
        "siklar": ["Sarı Mayo", "Kırmızı Mayo", "Pembe Mayo", "Yeşil Mayo"],
        "dogru": "Sarı Mayo"
    },
{
        "soru": "Dünya çapında milyonlarca oyuncunun katıldığı, internet kültüründe bir fenomene dönüşen ve 'Battle Royale' türünün popülerleşmesini sağlayan oyun hangisidir?",
        "siklar": ["Fortnite", "Minecraft", "World of Warcraft", "League of Legends"],
        "dogru": "Fortnite"
    },
    {
        "soru": "Sosyal medyada kısa ve dikey video akışının popülerleşmesini başlatan, günümüzde TikTok'un öncüsü olarak kabul edilen video paylaşım uygulaması hangisiydi?",
        "siklar": ["Vine", "Periscope", "MySpace", "Tumblr"],
        "dogru": "Vine"
    },
    {
        "soru": "Tüm zamanların en çok izlenen televizyon dizilerinden biri olan, 'Demir Taht' mücadelesini konu alıp fantastik kurguya yeni bir soluk getiren dizi hangisidir?",
        "siklar": ["Game of Thrones", "Breaking Bad", "Stranger Things", "The Walking Dead"],
        "dogru": "Game of Thrones"
    },
    {
        "soru": "İnternet ansiklopedisi olan Wikipedia hangi yıl hayata geçirilmiştir?",
        "siklar": ["2001", "1998", "2005", "2010"],
        "dogru": "2001"
    },
    {
        "soru": "Gelişmiş yapay zeka teknolojileriyle kasım 2022'de halka açık olarak piyasaya sürülerek dünyayı sarsan sohbet botunun geliştiricisi olan şirket hangisidir?",
        "siklar": ["OpenAI", "Google", "Microsoft", "Meta"],
        "dogru": "OpenAI"
    },
    {
        "soru": "Sinema tarihinin en büyük gişe rekorlarından birini kıran, Pandora gezegenindeki Na'vi halkını konu alan James Cameron imzalı bilim kurgu serisi hangisidir?",
        "siklar": ["Avatar", "Yıldız Savaşları", "Yüzüklerin Efendisi", "Marvel Sinematik Evreni"],
        "dogru": "Avatar"
    },
    {
        "soru": "İnternet dünyasında ilk arama motorlarından biri olan ve 1990'larda web dünyasının kapılarını açan popüler platform hangisiydi?",
        "siklar": ["Yahoo!", "Google", "Bing", "DuckDuckGo"],
        "dogru": "Yahoo!"
    },
    {
        "soru": "1980'lerin nostaljik havasını ve bilim kurgu / korku öğelerini harmanlayan, Netflix'in en popüler orijinal dizilerinden biri hangisidir?",
        "siklar": ["Stranger Things", "Black Mirror", "Dark", "The Witcher"],
        "dogru": "Stranger Things"
    },
    {
        "soru": "Dünya genelinde 'Kpop' kültürünün küresel bir akım haline gelmesinde en büyük paya sahip olan ve milyonlarca hayranı (ARMY) bulunan müzik grubu hangisidir?",
        "siklar": ["BTS", "BLACKPINK", "EXO", "Stray Kids"],
        "dogru": "BTS"
    },
    {
        "soru": "İnternet üzerindeki ilk 'tweet' hangi sosyal medya platformunda ve hangi yıl atılmıştır?",
        "siklar": ["Twitter (X) - 2006", "Facebook - 2004", "Instagram - 2010", "Tumblr - 2007"],
        "dogru": "Twitter (X) - 2006"
    }
    {
        "soru": "Boks tarihinin en büyük simgelerinden biri olan, 'kelebek gibi uçarım arı gibi sokarım' sözüyle özdeşleşen efsanevi boksör kimdir?",
        "siklar": ["Muhammad Ali", "Mike Tyson", "Joe Frazier", "George Foreman"],
        "dogru": "Muhammad Ali"
    },
    {
        "soru": "Hangi uluslararası spor organizasyonu her dört yılda bir kış sporları branşlarında (kayak, buz pateni vb.) düzenlenir?",
        "siklar": ["Kış Olimpiyat Oyunları", "Akdeniz Oyunları", "Universiade", "X Games"],
        "dogru": "Kış Olimpiyat Oyunları"
    },
    {
        "soru": "İspanya ve Latin Amerika mutfaklarında yaygın olan, içi kıyma, peynir veya sebze dolgulu ay şeklinde kapatılarak fırınlanan veya kızartılan hamur işi hangisidir?",
        "siklar": ["Empanada", "Burrito", "Quesadilla", "Churro"],
        "dogru": "Empanada"
    },
    {
        "soru": "Güney Amerika'nın omurgasını oluşturan ve dünyanın en uzun kara dağ silsilesi olan dağ sırası hangisidir?",
        "siklar": ["And Dağları", "Alpler", "Kayalık Dağları", "Himalaya Dağları"],
        "dogru": "And Dağları"
    },
    {
        "soru": "Dünya'nın en büyük mercan resifi sistemi olan Büyük Bariyer Resifi hangi ülkenin kuzeydoğu kıyılarında yer alır?",
        "siklar": ["Avustralya", "Endonezya", "Filipinler", "Meksika"],
        "dogru": "Avustralya"
    },
    {
        "soru": "Kuzey Kutbu'nu çevreleyen ve üzerinde kalıcı bir kara parçası bulunmayıp tamamen buzulla kaplı olan okyanus hangisidir?",
        "siklar": ["Arktik Okyanusu", "Güney Okyanusu", "Atlantik Okyanusu", "Pasifik Okyanusu"],
        "dogru": "Arktik Okyanusu"
    },
    {
        "soru": "Hangi ünlü buluşuyla tanınan Thomas Edison, aynı zamanda hangi akım savaşlarında doğrudan yer almıştır?",
        "siklar": ["Doğru Akım (DC)", "Alternatif Akım (AC)", "Kablosuz Elektrik", "Manyetik Dalga"],
        "dogru": "Doğru Akım (DC)"
    },
    {
        "soru": "Dünyanın en eski tapınak merkezi kabul edilen ve 'Tarihin Sıfır Noktası' denilen Göbeklitepe hangi ilimizdedir?",
        "siklar": ["Şanlıurfa", "Adıyaman", "Gaziantep", "Mardin"],
        "dogru": "Şanlıurfa"
    },
    {
        "soru": "Hangi kıtada hiç çöl bulunmamaktadır ve tamamen yeşil alanlar, ormanlar veya dağlık ekosistemler yer alır?",
        "siklar": ["Avrupa", "Asya", "Kuzey Amerika", "Okyanusya"],
        "dogru": "Avrupa"
    },
    {
        "soru": "İnsan vücudundaki en güçlü kas hangisidir ve orantısal olarak en büyük basıncı uygular?",
        "siklar": ["Çene kası (Masseter)", "Uyluk kası (Quadriceps)", "Kalp kası", "Baldır kası"],
        "dogru": "Çene kası (Masseter)"
    },
    {
        "soru": "Hangi ülke, yüz ölçümü olarak dünyanın en büyük ülkesi unvanına sahiptir?",
        "siklar": ["Rusya", "Kanada", "Çin", "Amerika Birleşik Devletleri"],
        "dogru": "Rusya"
    },
    {
        "soru": "Dünyanın en uzun nehirleri sıralamasında ilk sırada yer alan Nil Nehri hangi denize dökülmektedir?",
        "siklar": ["Akdeniz", "Kızıldeniz", "Hint Okyanusu", "Karadeniz"],
        "dogru": "Akdeniz"
    },
    {
        "soru": "Hangi ünlü matematikçi ve filozof, 'Düşünüyorum, öyleyse varım' sözüyle felsefe tarihine damga vurmuştur?",
        "siklar": ["René Descartes", "Sokrates", "Platon", "Aristoteles"],
        "dogru": "René Descartes"
    },
    {
        "soru": "Dünya üzerindeki en büyük mercan resifi sistemi olan Büyük Bariyer Resifi hangi ülkenin açıklarında yer alır?",
        "siklar": ["Avustralya", "Endonezya", "Filipinler", "Meksika"],
        "dogru": "Avustralya"
    },
    {
        "soru": "Hangi gaz atmosferde en yüksek oranda (%78 civarında) bulunan gazdır?",
        "siklar": ["Azot (Nitrojen)", "Oksijen", "Karbondioksit", "Argon"],
        "dogru": "Azot (Nitrojen)"
    },
    {
        "soru": "Dünyanın ilk kadın başbakanı olan Sirimavo Bandaranaike hangi ülkenin yönetiminde görev yapmıştır?",
        "siklar": ["Sri Lanka (Seylan)", "Hindistan", "İsrail", "İngiltere"],
        "dogru": "Sri Lanka (Seylan)"
    },
    {
        "soru": "Hangi antik yazıt, Mısır hiyerogliflerinin çözülmesini sağlayan ve üç farklı yazı dilini barındıran taştır?",
        "siklar": ["Rosetta Taşı", "Hammurabi Kanunları", "Behistun Yazıtları", "Kadeş Antlaşması"],
        "dogru": "Rosetta Taşı"
    },
    {
        "soru": "Türkiye'nin en yüksek dağı olan Ağrı Dağı'nın zirve rakımı yaklaşık olarak kaç metre yüksekliktedir?",
        "siklar": ["5137 metre", "4810 metre", "5650 metre", "4500 metre"],
        "dogru": "5137 metre"
    },

    # --- BÖLÜM 3: EĞLENCELİ BİLGİLER VE SANAT (51-100) ---
    {
        "soru": "Hangi hayvan türü ömrü boyunca hiç su içmeden yaşayabilir ve ihtiyacını yediği besinlerdeki sudan karşılar?",
        "siklar": ["Kanguru faresi", "Deve", "Çöl tilkisi", "Kutup ayısı"],
        "dogru": "Kanguru faresi"
    },
    {
        "soru": "Dünyanın en eski üniversitesi kabul edilen ve hâlâ eğitime devam eden Al-Qarawiyyin Üniversitesi hangi ülkededir?",
        "siklar": ["Fas", "Mısır", "İtalya", "İspanya"],
        "dogru": "Fas"
    },
    {
        "soru": "Hangi renk ışık dalga boyu en uzun olan ve bu nedenle trafikte dur veya uyarı ışığı olarak seçilen renktir?",
        "siklar": ["Kırmızı", "Mavi", "Yeşil", "Sarı"],
        "dogru": "Kırmızı"
    },
    {
        "soru": "Dünya'nın manyetik kutupları coğrafi kutuplarla tam olarak üst üste çakışmaz; manyetik kuzey kutbu hangi ülkeye doğru kaymaktadır?",
        "siklar": ["Kanada'dan Sibirya'ya doğru", "Grönland'dan Afrika'ya doğru", "Avustralya'ya doğru", "Antarktika'nın merkezine doğru"],
        "dogru": "Kanada'dan Sibirya'ya doğru"
    },
    {
        "soru": "Hangi ünlü yazar ve havacı, çocuk edebiyatının şaheseri olan 'Küçük Prens' (Le Petit Prince) kitabını yazmıştır?",
        "siklar": ["Antoine de Saint-Exupéry", "Jules Verne", "Victor Hugo", "Alexandre Dumas"],
        "dogru": "Antoine de Saint-Exupéry"
    },
    {
        "soru": "Dünyanın en küçük kemiği olan üzengi kemiği insan vücudunun hangi bölgesinde yer alır?",
        "siklar": ["Kulak (Orta kulak)", "Burun", "El bileği", "Serçe parmak"],
        "dogru": "Kulak (Orta kulak)"
    },
    {
        "soru": "Hangi göl, iki ülke sınırında yer almasıyla bilinen ve dünyada üzerinde ticari gemi taşımacılığı yapılan en yüksek rakımlı göldür?",
        "siklar": ["Titikaka Gölü", "Van Gölü", "Hazar Denizi", "Victoria Gölü"],
        "dogru": "Titikaka Gölü"
    },
    {
        "soru": "Türkiye'nin ilk milli parkı olan ve yemyeşil doğasıyla bilinen Yozgat Çamlığı Milli Parkı hangi yıl ilan edilmiştir?",
        "siklar": ["1958", "1950", "1965", "1973"],
        "dogru": "1958"
    },
    {
        "soru": "Hangi element periyodik tabloda 'Fe' simgesiyle gösterilir ve latince ismi 'Ferrum' olan metaldir?",
        "siklar": ["Demir", "Fosfor", "Flor", "Fransiyum"],
        "dogru": "Demir"
    },
    {
        "soru": "Dünya çapında bilinen 'Mona Lisa' tablosunun kaşları neden bulunmamaktadır veya görünmemektedir?",
        "siklar": ["Rönesans döneminde kaş almanın moda olması ve restorasyon sırasında silinmesi", "Ressamın unutması", "Çalınmış olması", "Hiç çizilmemiş olması"],
        "dogru": "Rönesans döneminde kaş almanın moda olması ve restorasyon sırasında silinmesi"
    },
    {
        "soru": "Hangi kuş türü sırt üstü uçabilen tek kuş türü olarak bilinir?",
        "siklar": ["Sinekkuşu (Kolibri)", "Kırlangıç", "Papağan", "Serçe"],
        "dogru": "Sinekkuşu (Kolibri)"
    },
    {
        "soru": "Dünyanın en büyük tuz gölü olan Salar de Uyuni hangi Güney Amerika ülkesindedir?",
        "siklar": ["Bolivya", "Şili", "Arjantin", "Peru"],
        "dogru": "Bolivya"
    },
    {
        "soru": "Hangi imparatorluk döneminde Antik Roma'nın nüfusu bir milyonu aşan ilk batı şehri olmuştur?",
        "siklar": ["Roma İmparatorluğu", "Bizans İmparatorluğu", "Osmanlı İmparatorluğu", "Pers İmparatorluğu"],
        "dogru": "Roma İmparatorluğu"
    },
    {
        "soru": "İnsan vücudunda yara iyileşmesinde ve bağışıklık sisteminde kritik rol oynayan 'Çinko' elementi vücutta hangi organda en çok bulunur?",
        "siklar": ["Karaciğer ve Kaslar", "Böbrek", "Beyin", "Akciğer"],
        "dogru": "Karaciğer ve Kaslar"
    },
    {
        "soru": "Hangi ünlü müzisyen kulağının sağır olmasına rağmen dünyanın en büyük senfonilerini bestelemiştir?",
        "siklar": ["Ludwig van Beethoven", "Wolfgang Amadeus Mozart", "Johann Sebastian Bach", "Frédéric Chopin"],
        "dogru": "Ludwig van Beethoven"
    },
    {
        "soru": "Dünyanın en eski yazılı antlaşması olan Kadeş Antlaşması hangi iki devlet arasında imzalanmıştır?",
        "siklar": ["Hititler ve Mısırlılar", "Sümerler ve Asurlular", "Romalılar ve Kartacalılar", "Yunanlılar ve Persler"],
        "dogru": "Hititler ve Mısırlılar"
    },
    {
        "soru": "Hangi gezegen halkalarıyla ünlü olsa da, aslında Satürn dışındaki Jüpiter, Uranüs ve Neptün'ün de halkaları vardır?",
        "siklar": ["Satürn", "Mars", "Venüs", "Merkür"],
        "dogru": "Satürn"
    },
    {
        "soru": "Dünya'nın en sıcak yeri olarak bilinen Ölüm Vadisi (Death Valley) hangi ülkededir?",
        "siklar": ["Amerika Birleşik Devletleri", "Mısır", "Avustralya", "Suudi Arabistan"],
        "dogru": "Amerika Birleşik Devletleri"
    },
    {
        "soru": "Hangi deniz canlısı omurgasız olmasına rağmen dünyanın en büyük gözlerine (futbol topu büyüklüğünde) sahiptir?",
        "siklar": ["Dev Mürekkepbalığı", "Balina Köpekbalığı", "Mavi Balina", "Yunus"],
        "dogru": "Dev Mürekkepbalığı"
    },
    {
        "soru": "Türkiye'de UNESCO Dünya Mirası Listesi'nde yer alan ve pamuk kalelerini andıran travertenleriyle ünlü yerimiz neresidir?",
        "siklar": ["Pamukkale (Denizli)", "Kapadokya (Nevşehir)", "Safranbolu (Karabük)", "Nemrut (Adıyaman)"],
        "dogru": "Pamukkale (Denizli)"
    },
    {
        "soru": "Hangi şair ve yazar 'İstiklal Marşı'mızın şairi olarak hem TBMM'de hem de milletin kalbinde ölümsüzleşmiştir?",
        "siklar": ["Mehmet Akif Ersoy", "Yahya Kemal Beyatlı", "Nazım Hikmet", "Orhan Veli"],
        "dogru": "Mehmet Akif Ersoy"
    },
    {
        "soru": "Dünyanın en küçük ülkesi olan Vatikan hangi şehrin sınırları içerisinde yer almaktadır?",
        "siklar": ["Roma (İtalya)", "Paris (Fransa)", "Madrid (İspanya)", "Atina (Yunanistan)"],
        "dogru": "Roma (İtalya)"
    },
    {
        "soru": "Hangi element periyodik tabloda 'O' harfiyle gösterilen, soluduğumuz ve yaşam için en temel gazdır?",
        "siklar": ["Oksijen", "Azot", "Hidrojen", "Helyum"],
        "dogru": "Oksijen"
    },
    {
        "soru": "Dünya genelinde 'Sıfır Noktası' olarak kabul edilen ve Greenwich Meridyeni'nin geçtiği gözlemevi hangi ülkededir?",
        "siklar": ["İngiltere", "Fransa", "İspanya", "İtalya"],
        "dogru": "İngiltere"
    },
    {
        "soru": "Hangi hayvan türü doğuştan itibaren uçamayan, dik duran ve güney yarımkürede yaşayan sevimli kuşlardır?",
        "siklar": ["Penguen", "Martı", "Pelikan", "Karga"],
        "dogru": "Penguen"
    },

    # --- BÖLÜM 4: KÜLTÜR, SANAT VE TEKNOLOJİ (101-175) ---
    {
        "soru": "Dünyanın ilk haritasını çizen ve coğrafya biliminin öncülerinden olan Türk denizci ve haritacısı kimdir?",
        "siklar": ["Piri Reis", "Kaptanı Derya Barbaros", "Seydi Ali Reis", "Turgut Reis"],
        "dogru": "Piri Reis"
    },
    {
        "soru": "Hangi mimar Osmanlı İmparatorluğu'nun 'Koca Sinan'ı olarak anılır ve Süleymaniye Camii'nin mimarıdır?",
        "siklar": ["Mimar Sinan", "Mimar Sedefkâr Mehmet Ağa", "Balyan Ailesi", "Davut Ağa"],
        "dogru": "Mimar Sinan"
    },
    {
        "soru": "Dünya genelinde internetin temelleri olan ARPANET projesi hangi ülkenin savunma bakanlığı tarafından geliştirilmiştir?",
        "siklar": ["Amerika Birleşik Devletleri", "İngiltere", "Sovyetler Birliği", "Fransa"],
        "dogru": "Amerika Birleşik Devletleri"
    },
    {
        "soru": "Hangi yazar Türk edebiyatında 'Çalıkuşu' romanının yazarı olarak tanınır?",
        "siklar": ["Reşat Nuri Güntekin", "Halide Edip Adıvar", "Peyami Safa", "Yakup Kadri Karaosmanoğlu"],
        "dogru": "Reşat Nuri Güntekin"
    },
    {
        "soru": "Dünyanın en yüksek binası unvanına sahip olan Burj Khalifa hangi şehirde yer almaktadır?",
        "siklar": ["Dubai", "Abu Dabi", "Doha", "Riyad"],
        "dogru": "Dubai"
    },
    {
        "soru": "Hangi futbol kulübü UEFA Kupası'nı (şimdiki UEFA Avrupa Ligi) kazanan ilk ve tek Türk takımıdır?",
        "siklar": ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor"],
        "dogru": "Galatasaray"
    },
    {
        "soru": "Türkiye'nin ilk yerli sondaj gemisi olan ve denizlerde arama yapan gemilerden biri hangisidir?",
        "siklar": ["Fatih", "Yavuz", "Kanuni", "Hepsi"],
        "dogru": "Hepsi"
    },
    {
        "soru": "Hangi müzik türü New Orleans'ta doğmuş olup doğaçlama ritimlerle dünyayı sarmıştır?",
        "siklar": ["Jazz", "Rock", "Klasik Müzik", "Pop"],
        "dogru": "Jazz"
    },
    {
        "soru": "Dünyanın en büyük sinema endüstrisi merkezi olan Hollywood hangi eyalette yer almaktadır?",
        "siklar": ["Kaliforniya", "New York", "Teksas", "Florida"],
        "dogru": "Kaliforniya"
    },
    {
        "soru": "Hangi ünlü bilim insanı radyoaktiviteyi keşfetmiş ve iki farklı alanda Nobel Ödülü kazanan ilk kadın olmuştur?",
        "siklar": ["Marie Curie", "Rosalind Franklin", "Ada Lovelace", "Lise Meitner"],
        "dogru": "Marie Curie"
    },
    {
        "soru": "Anadolu Selçuklu Devleti'nin başkenti olan ve Mevlana Celaleddin-i Rumi'nin türbesinin bulunduğu ilimiz hangisidir?",
        "siklar": ["Konya", "Bursa", "İznik", "Sivas"],
        "dogru": "Konya"
    },
    {
        "soru": "Hangi deniz, Asya ile Avrupa kıtalarını birbirinden ayıran ve İstanbul Boğazı ile Çanakkale Boğazı'na bağlanan denizdir?",
        "siklar": ["Karadeniz", "Akdeniz", "Marmara Denizi", "Ege Denizi"],
        "dogru": "Marmara Denizi"
    },
    {
        "soru": "Dünyanın en çok konuşulan ana dili hangisidir?",
        "siklar": ["Mandarin Çincesi", "İspanyolca", "İngilizce", "Hintçe"],
        "dogru": "Mandarin Çincesi"
    },
    {
        "soru": "Hangi ünlü ressam 'Yıldızlı Gece' (The Starry Night) tablosunu çizen Hollandalı empresyonist sanatçıdır?",
        "siklar": ["Vincent van Gogh", "Claude Monet", "Edvard Munch", "Rembrandt"],
        "dogru": "Vincent van Gogh"
    },
    {
        "soru": "Türkiye'nin en büyük adası unvanına sahip olan ada hangisidir?",
        "siklar": ["Gökçeada", "Bozcaada", "Marmara Adası", "Cunda Adası"],
        "dogru": "Gökçeada"
    },
    {
        "soru": "Hangi gezegen kırmızı gezegen olarak bilinir ve demir oksit yüzünden kırmızı görünür?",
        "siklar": ["Mars", "Jüpiter", "Venüs", "Satürn"],
        "dogru": "Mars"
    },
    {
        "soru": "Dünyanın en uzun demiryolu hattı olan Trans Sibirya Demiryolu hangi ülkeyi baştan başa geçer?",
        "siklar": ["Rusya", "Çin", "Kanada", "Hindistan"],
        "dogru": "Rusya"
    },
    {
        "soru": "Hangi yazar 'Dede Korkut Hikayeleri' Türk edebiyatının temel taşlarından biri olup milli kültürümüzü yansıtır?",
        "siklar": ["Anonim (Halk Eseri)", "Yunus Emre", "Karacaoğlan", "Köroğlu"],
        "dogru": "Anonim (Halk Eseri)"
    },
    {
        "soru": "Türkiye Cumhuriyeti'nin kurucusu Gazi Mustafa Kemal Atatürk'ün nüfusa kayıtlı olduğu il hangisidir?",
        "siklar": ["Gaziantep", "İstanbul", "Ankara", "İzmir"],
        "dogru": "Gaziantep"
    },
    {
        "soru": "Hangi ülke pamuk üretiminde ve pamuk tekstilinde dünya çapında tarihi bir kökene sahip olup Türkiye'nin güneyindedir?",
        "siklar": ["Mısır / Suriye / Türkiye", "İtalya", "Yunanistan", "İspanya"],
        "dogru": "Mısır / Suriye / Türkiye"
    },
    {
        "soru": "Dünya'nın katmanları arasında en sıcak olan ve demir-nikel alaşımından oluşan merkez katman hangisidir?",
        "siklar": ["İç Çekirdek", "Manto", "Yer Kabuğu", "Dış Çekirdek"],
        "dogru": "İç Çekirdek"
    },
    {
        "soru": "Hangi hayvan türü saatte 100 kilometreden fazla hıza ulaşarak karadaki en hızlı koşan memelidir?",
        "siklar": ["Çita", "Aslan", "Leopar", "Ceylan"],
        "dogru": "Çita"
    },
    {
        "soru": "Türkiye'nin en çok komşusu olan sınır kapısı ve ili hangisidir?",
        "siklar": ["Iğdır / Ağrı", "Edirne", "Hakkari", "Artvin"],
        "dogru": "Iğdır / Ağrı"
    },
    {
        "soru": "Hangi antik filozof, Atina'da Lykeion okulunu kurmuş ve Büyük İskender'in öğretmenliğini yapmıştır?",
        "siklar": ["Aristoteles", "Platon", "Sokrates", "Pythagoras"],
        "dogru": "Aristoteles"
    },
    {
        "soru": "Dünyanın en büyük yapay adalarıyla ünlü Palm Jumeirah projesi hangi şehirde inşa edilmiştir?",
        "siklar": ["Dubai", "Tokyo", "Singapur", "Sidney"],
        "dogru": "Dubai"
    },
    {
        "soru": "Hangi element periyodik tabloda 'C' harfiyle gösterilen ve elmastan kömüre kadar pek çok formu olan yaşam elementidir?",
        "siklar": ["Karbon", "Kalsiyum", "Klor", "Bakır"],
        "dogru": "Karbon"
    },
    {
        "soru": "Türk musiki tarihinin en büyük dâhilerinden biri olan ve ıtrî kelimesiyle anılan klasik Türk müziği bestecisi kimdir?",
        "siklar": ["Buhurizade Mustafa Itri", "Dede Efendi", "Zekai Dede", "Tanburi Cemil Bey"],
        "dogru": "Buhurizade Mustafa Itri"
    },
    {
        "soru": "Hangi deniz, dünyanın en tuzlu su kütlelerinden biri olup içinde canlı yaşayamadığı için Ölüdeniz olarak anılır?",
        "siklar": ["Lut Gölü (Ölüdeniz)", "Kızıldeniz", "Hazar Denizi", "Karadeniz"],
        "dogru": "Lut Gölü (Ölüdeniz)"
    },
    {
        "soru": "Dünya genelinde okyanus akıntılarının yönünü ve iklimleri büyük ölçüde etkileyen dönme etkisi nedir?",
        "siklar": ["Coriolis Etkisi", "Sera Etkisi", "Termal Etkisi", "Manyetik Etki"],
        "dogru": "Coriolis Etkisi"
    },
    {
        "soru": "Hangi ülke dünyada en çok saat dilimine (farklı zaman kuşağına) sahip olan ülkedir?",
        "siklar": ["Fransa (denizaşırı topraklarıyla)", "Rusya", "Amerika Birleşik Devletleri", "Çin"],
        "dogru": "Fransa (denizaşırı topraklarıyla)"
    },
    {
        "soru": "Türkiye'nin ilk yerli ve milli haberleşme uydusu olan Türksat 6A hangi yıl uzaya fırlatılmıştır?",
        "siklar": ["2024", "2022", "2020", "2018"],
        "dogru": "2024"
    },
    {
        "soru": "Hangi ünlü yazar 'Sefiller' (Les Misérables) romanını kaleme alarak dünya edebiyatına damga vurmuştur?",
        "siklar": ["Victor Hugo", "Alexandre Dumas", "Emile Zola", "Gustave Flaubert"],
        "dogru": "Victor Hugo"
    },
    {
        "soru": "Dünyanın en büyük çölü olan Sahra Çölü hangi kıtada yer almaktadır?",
        "siklar": ["Afrika", "Asya", "Avustralya", "Güney Amerika"],
        "dogru": "Afrika"
    },
    {
        "soru": "Hangi müzik aleti Türk halk müziğinde 'telli çalgıların şahı' olarak kabul edilir ve üç telli, divan sazı gibi çeşitleri vardır?",
        "siklar": ["Bağlama (Saz)", "Kemençe", "Ney", "Kanun"],
        "dogru": "Bağlama (Saz)"
    },
    {
        "soru": "Türkiye Cumhuriyeti'nin ilk başbakanı ve milli mücadele kahramanlarından olan devlet adamı kimdir?",
        "siklar": ["İsmet İnönü", "Fevzi Çakmak", "Kazım Karabekir", "Celal Bayar"],
        "dogru": "İsmet İnönü"
    },
    {
        "soru": "Hangi gezegen Güneş'e en yakın gezegen konumundadır?",
        "siklar": ["Merkür", "Venüs", "Mars", "Dünya"],
        "dogru": "Merkür"
    },
    {
        "soru": "Dünyanın en eski yazılı destanı olan ve Sümer mitolojisine dayanan destan hangisidir?",
        "siklar": ["Gılgamış Destanı", "İlyada ve Odysseia", "Manas Destanı", "Şehname"],
        "dogru": "Gılgamış Destanı"
    },
    {
        "soru": "Hangi sanat akımı 20. yüzyılın başında nesneleri geometrik şekillere indirgeyerek Picasso ve Braque tarafından başlatılmıştır?",
        "siklar": ["Kübizm", "Empresyonizm", "Sürrealizm", "Barok"],
        "dogru": "Kübizm"
    },
    {
        "soru": "Türkiye'nin en uzun nehirleri arasında ilk sırada yer alan ve Karadeniz'e dökülen nehir hangisidir?",
        "siklar": ["Kızılırmak", "Fırat", "Dicle", "Sakarya"],
        "dogru": "Kızılırmak"
    },
    {
        "soru": "Hangi deniz canlısı dokunaçlarındaki zehirli hücrelerle bilinir ve beyinsiz yaşam formları arasında en eski olanlardandır?",
        "siklar": ["Denizanası", "Ahtapot", "Yengeç", "Sünger"],
        "dogru": "Denizanası"
    },
    {
        "soru": "Dünyanın en kalabalık ülkesi hangisidir?",
        "siklar": ["Hindistan / Çin", "Endonezya", "Amerika Birleşik Devletleri", "Pakistan"],
        "dogru": "Hindistan / Çin"
    },
    {
        "soru": "Hangi ünlü mucit matbaayı geliştirerek modern bilginin yayılmasında çığır açmıştır?",
        "siklar": ["Johannes Gutenberg", "Thomas Edison", "Nikola Tesla", "Alexander Graham Bell"],
        "dogru": "Johannes Gutenberg"
    },
    {
        "soru": "Türkiye'nin ilk coğrafi işaretli tescilli peyniri olan ve Kars ile özdeşleşen peynir türü hangisidir?",
        "siklar": ["Kars Kaşarı", "Ezine Peyniri", "Van Otlu Peyniri", "İzmir Tulumu"],
        "dogru": "Kars Kaşarı"
    },
    {
        "soru": "Hangi kıtada penguenler doğal ortamda sadece güney yarımkürede yer alır?",
        "siklar": ["Antarktika", "Avrupa", "Asya", "Kuzey Amerika"],
        "dogru": "Antarktika"
    },
    {
        "soru": "Dünyanın en büyük yapay havzası olan Panama Kanalı hangi iki okyanusu birbirine bağlar?",
        "siklar": ["Atlantik ve Pasifik Okyanusu", "Hint ve Atlantik Okyanusu", "Pasifik ve Arktik Okyanusu", "Akdeniz ve Kızıldeniz"],
        "dogru": "Atlantik ve Pasifik Okyanusu"
    }
]

# =========================================================
# 3. SVG ÜÇGEN ÇİZİM MOTORU (Çeşitkenar Hariç)
# =========================================================
def svg_ucgen_ciz(tip, tepe_aci, sol_aci, sag_aci):
    def fmt(v):
        return f"{v}°" if v != "?" else "?"

    if tip == "dik":
        p1, p2, p3 = "60,160", "260,160", "60,45"
        labels = ("D", "E", "F")
        pos_list = ("x='45' y='35'", "x='35' y='178'", "x='270' y='178'")
        val_list = ("x='75' y='75'", "x='90' y='145'", "x='210' y='145'")
        semboller = '<rect x="60" y="140" width="20" height="20" fill="none" stroke="#2c3e50" stroke-width="2"/>'
    elif tip == "ikizkenar":
        p1, p2, p3 = "60,160", "260,160", "160,40"
        labels = ("P", "R", "S")
        pos_list = ("x='150' y='30'", "x='35' y='175'", "x='275' y='175'")
        val_list = ("x='145' y='70'", "x='80' y='145'", "x='220' y='145'")
        semboller = '<line x1="103" y1="95" x2="115" y2="105" stroke="#e74c3c" stroke-width="3"/><line x1="207" y1="95" x2="217" y2="105" stroke="#e74c3c" stroke-width="3"/>'
    else:  # eskenar
        p1, p2, p3 = "60,160", "260,160", "160,26"
        labels = ("A", "B", "C")
        pos_list = ("x='150' y='18'", "x='35' y='175'", "x='275' y='175'")
        val_list = ("x='145' y='65'", "x='85' y='145'", "x='220' y='145'")
        semboller = '<line x1="105" y1="95" x2="115" y2="105" stroke="#27ae60" stroke-width="3"/><line x1="205" y1="95" x2="215" y2="105" stroke="#27ae60" stroke-width="3"/><line x1="153" y1="168" x2="167" y2="168" stroke="#27ae60" stroke-width="3"/>'

    v_vals = (fmt(tepe_aci), fmt(sol_aci), fmt(sag_aci))

    svg_code = f"""
    <div style="display: flex; justify-content: center; background-color: #ffffff; padding: 15px; border-radius: 12px; border: 2px solid #dcdde1; box-shadow: 0 4px 6px rgba(0,0,0,0.03);">
        <svg width="340" height="200" viewBox="0 0 340 200" xmlns="http://www.w3.org/2000/svg">
            <polygon points="{p1} {p2} {p3}" fill="#f5fafd" stroke="#2980b9" stroke-width="3.5" stroke-linejoin="round"/>
            {semboller}
            <text {pos_list[0]} font-family="Arial" font-weight="bold" font-size="16" fill="#2c3e50">{labels[0]}</text>
            <text {pos_list[1]} font-family="Arial" font-weight="bold" font-size="16" fill="#2c3e50">{labels[1]}</text>
            <text {pos_list[2]} font-family="Arial" font-weight="bold" font-size="16" fill="#2c3e50">{labels[2]}</text>
            <text {val_list[0]} font-family="Arial" font-weight="bold" font-size="14" fill="#c0392b">{v_vals[0]}</text>
            <text {val_list[1]} font-family="Arial" font-weight="bold" font-size="14" fill="#c0392b">{v_vals[1]}</text>
            <text {val_list[2]} font-family="Arial" font-weight="bold" font-size="14" fill="#c0392b">{v_vals[2]}</text>
        </svg>
    </div>
    """
    return svg_code

# =========================================================
# 4. ZENGİN ALT KATEGORİLİ SORU ÜRETME MOTORU
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
            alt = random.choice([1, 2, 3])
            if alt == 1:
                dogru = "Güneş yavaş yavaş tepelerin arkasından görünmeye başladı."
                yanlislar = ["Bu mont kardeşime biraz küçük geldi.", "Toplantıdan en son ben ayrıldım.", "Merdivenleri çıkarken nefes nefese kaldı."]
                soru = f"{kaynak_turu}<br><br><b>[Sözcükte Anlam - Gerçek/Mecaz/Terim]</b> 'Çıkmak' sözcüğü hangi cümlede <u>'ortaya çıkmak, görünmek'</u> anlamındadır?"
            elif alt == 2:
                dogru = "Keskin bıçak ekmeği çok rahat dilimliyordu."
                yanlislar = ["Keskin bir zekaya sahip olduğunu hemen belli etti.", "Keskin koku tüm odayı sardı.", "Keskin bir virajdan sonra eve ulaştık."]
                soru = f"{kaynak_turu}<br><br><b>[Sözcükte Anlam - Gerçek Anlam]</b> 'Keskin' sözcüğü hangi cümlede <u>gerçek anlamıyla</u> kullanılmıştır?"
            else:
                dogru = "Bu matematik probleminde doğru orantı kullandım."
                yanlislar = ["Sınavda başarılı olmak için çok çalıştı.", "Arkadaşına güzel bir kalem hediye etti.", "Bahçedeki çiçekleri sulamayı unutma."]
                soru = f"{kaynak_turu}<br><br><b>[Sözcükte Anlam - Terim Anlam]</b> Hangi cümlede <u>terim anlamlı</u> bir sözcük vardır?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
            
        elif "Cümlede Anlam" in unite:
            alt = random.choice([1, 2])
            if alt == 1:
                dogru = "Hava sağanak yağışlı olduğundan maç ertelendi."
                yanlislar = ["Başarılı olmak için her gün düzenli ders çalışıyor.", "Sabah uyanınca elini yüzünü yıkadı.", "Yarın akşam eski arkadaşlarıyla buluşacak."]
                soru = f"{kaynak_turu}<br><br><b>[Cümlede Anlam - Neden-Sonuç]</b> Hangi cümlede <u>neden-sonuç</u> ilişkisi vardır?"
            else:
                dogru = "Projeyi bitirmek için sabaha kadar uyumadı."
                yanlislar = ["Yağmur yağdığı için sokaklar ıslanmıştı.", "Kardeşi uyuduğu için ses çıkarmıyordu.", "Hava çok sıcak olduğundan gölgede oturdu."]
                soru = f"{kaynak_turu}<br><br><b>[Cümlede Anlam - Amaç-Sonuç]</b> Hangi cümlede <u>amaç-sonuç</u> ilişkisi vardır?"
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
            tip_secimi = random.choice(["eskenar", "dik", "ikizkenar"])
            if tip_secimi == "eskenar":
                dogru = "60°"
                yanlislar = ["45°", "90°", "30°"]
                svg_gorsel = svg_ucgen_ciz("eskenar", 60, 60, 60)
                soru = f"{kaynak_turu}<br><br><b>[Eşkenar Üçgen Analizi]</b><br>{svg_gorsel}<br>Tüm kenar uzunlukları ve iç açıları birbirine eşit olan bir ABC eşkenar üçgeninde tepe açısı kaç derecedir?"
                return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
            elif tip_secimi == "dik":
                aci1 = random.choice([30, 35, 40, 45, 50, 55, 60])
                dogru_val = 90 - aci1
                dogru = f"{dogru_val}°"
                yanlislar = [f"{dogru_val + 10}°", f"{dogru_val - 10}°", f"{dogru_val + 15}°"]
                svg_gorsel = svg_ucgen_ciz("dik", "?", 90, aci1)
                soru = f"{kaynak_turu}<br><br><b>[Dik Üçgen Soru Tipi]</b><br>{svg_gorsel}<br>E köşesi 90° dik açı ve F köşesi <b>{aci1}°</b> olan DEF dik üçgeninde tepedeki D açısı kaç derecedir?"
                return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
            else:
                tepe_aci = random.choice([40, 50, 60, 70, 80])
                taban_aci = (180 - tepe_aci) // 2
                dogru = f"{taban_aci}°"
                yanlislar = [f"{taban_aci + 10}°", f"{tepe_aci}°", f"{taban_aci - 5}°"]
                svg_gorsel = svg_ucgen_ciz("ikizkenar", tepe_aci, "?", "?")
                soru = f"{kaynak_turu}<br><br><b>[İkizkenar Üçgen Özelliği]</b><br>{svg_gorsel}<br>|PR| = |PS| olan PRS ikizkenar üçgeninde tepe açısı <b>{tepe_aci}°</b> verilmiştir. Taban açısı kaç derecedir?"
                return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
        else:
            dogru = "Veri analizi tablosunda en çok tercih edilen öge en yüksek sütuna sahiptir."
            yanlislar = ["Sütun grafikleri sadece daire ile çizilir.", "Veri toplamada tabloya gerek yoktur.", "Grafikler uzunluk ölçmek için kullanılır."]
            soru = f"{kaynak_turu}<br><br><b>[Veri İşleme ve Ölçme]</b> Veri işleme ve grafik yorumlama ile ilgili hangisi doğrudur?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

    # --- FEN BİLİMLERİ ---
    elif ders == "Fen Bilimleri":
        if "Güneş, Dünya ve Ay" in unite:
            alt_tip = random.choice([1, 2, 3, 4, 5])
            if alt_tip == 1:
                dogru = "Güneş, Dünya ve Ay'ın şekli küreye benzer."
                yanlislar = ["Güneş tam bir kare şeklindedir.", "Dünya düz bir tepsi gibidir.", "Ay'ın şekli üçgene benzer."]
                soru = f"{kaynak_turu}<br><br><b>[Gök Cisimlerinin Şekli]</b> Güneş, Dünya ve Ay'ın geometrik yapısı ile ilgili aşağıdakilerden hangisi doğrudur?"
            elif alt_tip == 2:
                dogru = "Güneş, Dünya'dan çok daha büyük ve uzakta yer alan bir yıldızdır."
                yanlislar = ["Ay, Güneş'ten daha büyüktür.", "Dünya Güneş'in etrafında değil, Güneş Dünya'nın etrafında döner.", "Güneş bir gezegendir."]
                soru = f"{kaynak_turu}<br><br><b>[Boyut ve Özellikler]</b> Güneş, Dünya ve Ay'ın birbirine göre boyutları ve yapıları düşünüldüğünde hangisi doğrudur?"
            elif alt_tip == 3:
                dogru = "Dünya kendi ekseni etrafında döner ve bu hareket sonucunda gece ve gündüz oluşur."
                yanlislar = ["Dünya'nın kendi etrafındaki dönüşü 1 yıl sürer.", "Gece ve gündüz Ay'ın dönmesiyle oluşur.", "Güneş kendi etrafında dönmez."]
                soru = f"{kaynak_turu}<br><br><b>[Dünya'nın Hareketleri]</b> {kisi}'nin incelediği bilgilere göre Dünya'nın kendi ekseni etrafındaki dönme hareketi neyi sağlar?"
            elif alt_tip == 4:
                dogru = "Yeniay -> İlk Dördün -> Dolunay -> Son Dördün"
                yanlislar = ["Dolunay -> Yeniay -> Son Dördün -> İlk Dördün", "İlk Dördün -> Dolunay -> Yeniay -> Son Dördün", "Yeniay -> Dolunay -> İlk Dördün -> Son Dördün"]
                soru = (
                    f"{kaynak_turu}<br><br><b>[Ay'ın Evreleri Döngü Şeması]</b><br>"
                    "<div style='background:#f9ebea; border:2px solid #c0392b; padding:15px; border-radius:10px; text-align:center;'>"
                    "🌑 <b>Yeniay</b> ➔ 🌓 <b>İlk Dördün</b> ➔ 🌕 <b>Dolunay</b> ➔ 🌗 <b>Son Dördün</b>"
                    "</div><br>"
                    "Ay'ın ana evrelerinin doğru kronolojik sıralaması hangi seçenekte eksiksiz verilmiştir?"
                )
            else:
                dogru = "Ay, Dünya'nın etrafındaki dolanma hareketini yaklaşık 29,5 günde tamamlar."
                yanlislar = ["Ay'ın Dünya etrafında dolanması 1 gün sürer.", "Ay kendi ışığını üreten bir yıldızdır.", "Ay üzerinde atmosfer tabakası çok kalındır."]
                soru = f"{kaynak_turu}<br><br><b>[Ay'ın Dolanma Hareketi]</b> Ay'ın hareketleri ile ilgili olarak öğrenciler hangi bilgiye ulaşmalıdır?"
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

   # --- BİLGİ YARIŞMASI KATEGORİLERİ ---
    else:
        if "Başkentleri ve Coğrafya" in unite:
            ulke, dogru = random.choice(list(DUNYA_ULKELERI.items()))
            tum_baskentler = list(DUNYA_ULKELERI.values())
            yanlis_havuzu = [b for b in tum_baskentler if b != dogru]
            yanlislar = random.sample(yanlis_havuzu, 3)
            soru = f"{kaynak_turu}<br><br>🏆 <b>[Bilgi Yarışması - Dünya Başkentleri]</b> <b>{ulke}</b> ülkesinin başkenti neresidir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
            
        elif "Türk Mutfağı ve Yöresel Lezzetler" in unite:
            sehir, veri = random.choice(list(TURK_MUTFAGI_YORESEL.items()))
            dogru = veri["yemek"]
            ipucu = veri["ipucu"]
            tum_lezzetler = [v["yemek"] for v in TURK_MUTFAGI_YORESEL.values()]
            yanlis_havuzu = [l for l in tum_lezzetler if l != dogru]
            yanlislar = random.sample(yanlis_havuzu, 3)
            soru = f"{kaynak_turu}<br><br>🍲 <b>[Bilgi Yarışması - Türk Mutfağı]</b><br><i>'{ipucu}'</i><br><br>Yukarıda tarifi/özellikleri verilen ve <b>{sehir}</b> ile özdeşleşen yöresel lezzetimiz hangisidir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
            
        elif "Dünya Mutfakları ve Lezzetler" in unite:
            ulke, veri = random.choice(list(DUNYA_MUTFAGI_LEZZETLER.items()))
            dogru = veri["yemek"]
            ipucu = veri["ipucu"]
            tum_lezzetler = [v["yemek"] for v in DUNYA_MUTFAGI_LEZZETLER.values()]
            yanlis_havuzu = [l for l in tum_lezzetler if l != dogru]
            yanlislar = random.sample(yanlis_havuzu, 3)
            soru = f"{kaynak_turu}<br><br>🌍 <b>[Bilgi Yarışması - Dünya Mutfakları]</b><br><i>'{ipucu}'</i><br><br>Yukarıda yapım özellikleri verilen meşhur lezzet hangisidir ve hangi ülkenin mutfağına aittir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}

        elif "Genel Kültür" in unite or "Eğlenceli Bilgiler" in unite:
            secilen = random.choice(GENEL_KULTUR_SORULARI)
            dogru = secilen["dogru"]
            tum_siklar = secilen["siklar"]
            soru = f"{kaynak_turu}<br><br>🧠 <b>[Bilgi Yarışması - Genel Kültür]</b><br>{secilen['soru']}"
            return {"soru": soru, "siklar": tum_siklar, "dogru": dogru}
            
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
                status_box.info(f"🔄 Zengin alt kategorili sorular hazırlanıyor... ({sn}s)")
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
    st.info(f"🎉 **{len(st.session_state['soru_listesi'])} adet zenginleştirilmiş soru** hazır!")
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
