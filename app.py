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
    "Kars": {"yemek": "Kars Kazı ve Gravyer Peyniri", "ipucu": "Kars'ın yüksek dağlarında beslenen kazların kar yağdıktan sonra tuzlanıp kurutulması ve fırında bulgurla sunulmasıdır."},
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
    "Osmaniye": {"yemek": "Osmaniye Yerfıstığı", "ipucu": "Bölgenin kırmızı topraklarında yetişen, yüksek yağ oranına ve çıtır lezzete sahip özel fıstıktır."},
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
    "İtalya": {"yemek": "Pizza / Makarna", "ipucu": "Mayalı hamurun ince açılıp üzerine domates sosu, mozzarella peyniri ve çeşitli malzemeler dizilerek fırınlanmasıyla yapılır."},
    "Japonya": {"yemek": "Suşi / Ramen", "ipucu": "Özel sirke ile tatlandırılmış haşlanmış pirincin deniz yosunu ve çiğ balıkla sarılmasıdır."},
    "Meksika": {"yemek": "Taco / Burrito", "ipucu": "Mısır unundan yapılan tortilla ekmeklerinin içine et, fasulye ve avokado sosu doldurularak yenir."},
    "Çin": {"yemek": "Noodle", "ipucu": "Buğday veya pirinç unundan yapılan uzun ince şerit halindeki eriştelerin sebze ve etle wok tavada sotelemesidir."},
    "Fransa": {"yemek": "Kroasan", "ipucu": "Un, maya ve bolca tereyağının kat kat açılarak hilal şeklinde fırınlanmasıyla elde edilen gevrek hamur işidir."},
    "Hindistan": {"yemek": "Köri Soslu Tavuk", "ipucu": "Tavuk parçalarının zerdeçal, kimyon, kişniş ve acı baharatlardan oluşan yoğun sarı renkli sosla pişirilmesidir."},
    "Amerika Birleşik Devletleri": {"yemek": "Hamburger", "ipucu": "Yuvarlak sandviç ekmeğinin arasına dana etinden yapılan köfte, marul, domates ve soslar konularak hazırlanır."},
    "Yunanistan": {"yemek": "Musakka", "ipucu": "Patlıcan dilimleri ve kıymalı domates sosunun kat kat dizilerek üzerine bechamel sos dökülüp fırınlanmasıyla yapılır."},
    "İspanya": {"yemek": "Paella", "ipucu": "Pirinç, safran, zeytinyağı ve deniz ürünleriyle geniş tabakalı tavada pişirilen geleneksel yemektir."},
    "Almanya": {"yemek": "Prezel ve Sosis", "ipucu": "Düğümlenmiş şekle sahip, üzeri iri tuz taneleriyle kaplı, dışı çıtır içi yumuşak bir unlu mamüldür."},
    "Tayland": {"yemek": "Pad Thai", "ipucu": "Pirinç eriştelerinin yumurta, tofu, fıstık, balık sosu ve karidesle wok tavada harmanlanıp pişirilmesidir."},
    "Güney Kore": {"yemek": "Kimchi", "ipucu": "Çin lahanası ve turpun sarımsak, zencefil ve acı biber salçasıyla fermente edilmesiyle yapılan garnitürdür."},
    "Brezilya": {"yemek": "Feijoada", "ipucu": "Siyah fasulye, domuz eti ve sığır etinin toprak tencerede kısık ateşte uzun süre pişirilmesiyle yapılan ulusal yemektir."},
    "Lübnan": {"yemek": "Falafel ve Humus", "ipucu": "Nohudun ezilip baharatlar ve taze otlarla karıştırılarak yuvarlak köfteler halinde kızgın yağda kızartılmasıdır."},
    "Arjantin": {"yemek": "Empanada", "ipucu": "Ay şeklindeki hamur parçalarının içine kıymalı veya peynirli harç doldurularak fırında pişirilmesidir."},
    "Vietnam": {"yemek": "Pho", "ipucu": "Pirinç erişteleri, uzun süre kemik suyuyla kaynatılan et dilimleri ve taze otlarla servis edilen çorbadır."},
    "İngiltere": {"yemek": "Fish and Chips", "ipucu": "Beyaz etli balık filetosunun hamur harcına bulanarak kızartılması ve yanında patates kızartmasıyla sunulmasıdır."},
    "Fas": {"yemek": "Kuskus", "ipucu": "Buğday irmik tanelerinin buharda pişirilip üzerine sebze, et ve özel baharatlı sos dökülerek servis edilmesidir."},
    "Rusya": {"yemek": "Borsç Çorbası", "ipucu": "Kırmızı pancarın başrolde olduğu, lahana ve et eklenerek üzerine ekşi krema ile sunulan çorbadır."},
    "İsveç": {"yemek": "İsveç Köftesi", "ipucu": "Kıyma, soğan ve baharatlardan yapılan küçük yuvarlak köftelerin krema bazlı kahverengi sos ve reçelle servis edilmesidir."},
    "Belçika": {"yemek": "Belçika Wafflesu", "ipucu": "Özel kalıplarda pişirilen, dışı çıtır içi yumuşak hamurun üzerine çikolata, çilek ve krema sürülerek yenmesidir."},
    "İsviçre": {"yemek": "Fondü", "ipucu": "Çeşitli eritilmiş peynirlerin özel bir tencerede ısıtılarak ekmek parçalarının sosa batırılarak yendiği yemektir."},
    "Macaristan": {"yemek": "Gulaş", "ipucu": "Dana eti, patates ve kök sebzelerin yoğun miktarda tatlı kırmızı toz biber ile tencere yahni şeklinde pişmesidir."},
    "Ukrayna": {"yemek": "Varenyky", "ipucu": "İnce açılmış mayasız hamurun içine patates veya mantar koyulup kapatılarak suda haşlanan bir çeşit mantıdır."},
    "Küba": {"yemek": "Küba Sandviçi", "ipucu": "Küba ekmeği arasına domuz eti, jambon, peynir, turşu ve hardal konularak pres makinesinde ısıtılmasıdır."},
    "Mısır": {"yemek": "Kişeri", "ipucu": "Mercimek, makarna, pirinç ve nohut karışımının üzerine kızarmış soğan ve domates sosu dökülerek yapılan yemektir."},
    "Avustralya": {"yemek": "Meat Pie (Etli Turta)", "ipucu": "Kıymalı ve soğanlı koyu sosun, ufalanan tereyağlı turta hamuruyla kaplanıp fırında pişirilmesiyle elde edilir."},
    "Endonezya": {"yemek": "Nasi Goreng", "ipucu": "Haşlanmış pirincin soya sosu, sarımsak, sebze ve etle tavada karıştırılarak kavrulmasıdır."},
    "İran": {"yemek": "Fesencan", "ipucu": "Tavuk veya ördek etinin dövülmüş ceviz içi ve nar ekşisi sosuyla uzun süre kısık ateşte pişirilmesiyle yapılır."},
    "Fas": {"yemek": "Tajin", "ipucu": "Konik biçimli toprak kaplarda et ve sebzelerin kendi suyuyla uzun süre pişirildiği Kuzey Afrika yemeğidir."},
    "Portekiz": {"yemek": "Pastel de Nata", "ipucu": "Çıtır milföy hamurunun içi özel krema dolgusuyla doldurularak fırında üzeri karamelize olana kadar pişirilen tarttır."},
    "Avusturya": {"yemek": "Schnitzel", "ipucu": "Dana bonfile etinin dövülerek inceltilmesi, un, yumurta ve galeta ununa bulanarak kızgın yağda kızartılmasıdır."},
    "Polonya": {"yemek": "Pierogi", "ipucu": "Yarım ay şeklinde kapatılmış, içi patates, peynir veya kıymayla doldurulan haşlanmış Polonya mantısıdır."},
    "Çekya": {"yemek": "Trdelnik", "ipucu": "Şeker ve cevizle kaplanmış hamurun metal silindirlere sarılarak ateş üstünde döndürülen tatlı çöreğidir."},
    "Hollanda": {"yemek": "Stroopwafel", "ipucu": "İki ince waffle katmanının arasına karamel bazlı şurup sürülerek yapıştırılan tatlı bisküvidir."},
    "Danimarka": {"yemek": "Danimarka Hamur İşi (Danish)", "ipucu": "Tereyağlı hamur katmanlarının arasına reçel, çikolata veya krem peynir sürülerek hazırlanan tatlı hamur işidir."},
    "Norveç": {"yemek": "Lutefisk", "ipucu": "Kurutulmuş beyaz balığın su ve sodalı potas çözeltisinde bekletilip fırınlanmasıyla yapılan geleneksel yemektir."},
    "Finlandiya": {"yemek": "Lohikeitto", "ipucu": "Taze somon balığı parçaları, patates, pırasa ve krema ile yapılan lezzetli Fin balık çorbasıdır."},
    "İrlanda": {"yemek": "Irish Stew (İrlanda Yahnisi)", "ipucu": "Kuzu eti, patates, soğan ve havuç kullanılarak ağır ateşte güveçte pişirilen geleneksel yemektir."},
    "Romanya": {"yemek": "Sarmale", "ipucu": "Lahana yapraklarının içine kıymalı ve pirinçli harç sarılarak kısık ateşte domates sosuyla pişirilmesidir."},
    "Bulgaristan": {"yemek": "Tarator Çorbası", "ipucu": "Yoğurt, salatalık, sarımsak, zeytinyağı ve cevizle yapılan soğuk servis edilen yaz çorbasıdır."},
    "Sırbistan": {"yemek": "Cevapi", "ipucu": "Baharatlı kıyma karışımından yapılan küçük silindirik köftelerin somun ekmek ve soğanla sunulmasıdır."},
    "Hırvatistan": {"yemek": "Crni Rižot (Siyah Risotto)", "ipucu": "Mürekkep balığı mürekkebiyle siyah renk verilen, deniz ürünlü geleneksel pirinç pilavıdır."},
    "Bosna-Hersek": {"yemek": "Boşnak Böreği", "ipucu": "Elde açılan incecik yufkaların arasına kıymalı, peynirli veya patatesli harç konularak spiral şeklinde sarılmasıdır."},
    "Gürcistan": {"yemek": "Haçapuri", "ipucu": "Kayık şeklinde açılan mayalı hamurun içine bolca peynir ve tereyağı, pişmeye yakın da yumurta kırılmasıyla yapılır."},
    "Azerbaycan": {"yemek": "Şah Pilavı", "ipucu": "Lavaş yufkası kaplı tencerenin içinde safranlı pirinç, kuzu eti ve kuru meyvelerle fırında pişirilen ana yemektir."},
    "İsrail": {"yemek": "Shakshuka (Şakşuka)", "ipucu": "Domates sosu, biber, soğan ve baharatlar içinde pişirilen sosun üzerine bütün yumurta kırılmasıyla yapılır."},
    "Surudi": {"yemek": "Mütebbel", "ipucu": "Közlenmiş patlıcanların tahin, sarımsak, yoğurt ve zeytinyağı ile ezilerek püre haline getirilmesidir."},
    "Japonya": {"yemek": "Tempura", "ipucu": "Karides ve sebze parçalarının buzlu özel unlu harca bulanarak derin ve kızgın yağda çıtır kızartılmasıdır."},
    "Malezya": {"yemek": "Laksa", "ipucu": "Baharatlı ve hindistan cevizi sütü içeren yoğun soslu, deniz ürünlü veya tavuklu erişte çorbasıdır."},
    "Singapur": {"yemek": "Chili Crab (Acılı Yengeç)", "ipucu": "Büyük yengeçlerin domates ve acı biberli koyu, tatlı-ekşi bir sosla wok tavada pişirilmesidir."},
    "Filipinler": {"yemek": "Adobo", "ipucu": "Tavuz veya domuz etinin soya sosu, sirke, sarımsak ve karabiberle uzun süre marine edilip pişirilmesidir."},
    "Şili": {"yemek": "Completo", "ipucu": "Uzun sosisli sandviç ekmeğinin içine sosis, bolca avokado ezmesi, domates ve mayonez konulmasıdır."},
    "Kolombiya": {"yemek": "Arepa", "ipucu": "Mısır unundan yapılan yuvarlak ve yassı ekmeklerin ızgarada pişirilip içi açılarak peynir veya etle doldurulmasıdır."},
    "Peru": {"yemek": "Ceviche", "ipucu": "Çiğ balık parçalarının taze limon suyu, kırmızı soğan, acı biber ve mısırla marine edilerek pişirilmeden sunulmasıdır."},
    "Venezuela": {"yemek": "Pabellón Criollo", "ipucu": "Pilav, siyah fasulye, didilmiş sığır eti ve kızarmış tatlı muz dilimlerinin bir arada sunulmasıdır."},
    "Etiyopya": {"yemek": "İncera", "ipucu": "Tef unundan yapılan, süngerimsi ve ekşimsi dokuya sahip büyük ve esnek mayalı gözleme ekmektir."},
    "Gana": {"yemek": "Jollof Pilavı", "ipucu": "Pirinç, domates sosu, soğan, biber ve çeşitli baharatların tek tencerede et suyuyla pişirilmesidir."},
    "Nijerya": {"yemek": "Pounded Yam (Dövülmüş Yam)", "ipucu": "Yam bitkisinin kökünün haşlanıp sakız kıvamına gelene kadar dövülerek top şeklinde et yemekleriyle yenmesidir."},
    "Güney Afrika": {"yemek": "Bobotie", "ipucu": "Baharatlı kıymanın üzerine yumurtalı ve sütlü sos dökülerek fırınlanan geleneksel et yemeğidir."}
}
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

   # --- BİLGİ YARIŞMASI (DÜNYA BAŞKENTLERİ, TÜRK VE DÜNYA MUTFAĞI ENTEGRASYONU) ---
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
            
            soru = f"{kaynak_turu}<br><br>🌍 <b>[Bilgi Yarışması - Dünya Mutfakları]</b><br><i>'{ipucu}'</i><br><br>Yukarıda yapım özellikleri verilen meşhur lezzet hangi ülkenin mutfağına aittir?"
            return {"soru": soru, "siklar": [dogru] + yanlislar, "dogru": dogru}
            
        else:
            # Diğer bilgi yarışması kategorileri için standart akış
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
