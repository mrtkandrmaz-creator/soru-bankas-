import streamlit as st
import random
import json
import time
import math
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Milyonluk Soru Bankası", page_icon="🎓", layout="wide")

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

MEB_MUFREDAT = {
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve Doğal Sayılarla İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar, Çizimler ve Açı Ölçme",
        "5. Ünite: Veri İşleme ve Uzunluk/Zaman Ölçme",
        "6. Ünite: Alan Ölçme ve Geometrik Cisimler"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay",
        "2. Ünite: Canlılar Dünyası",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim",
        "5. Ünite: Işığın Yayılması ve Tam Gölge",
        "6. Ünite: İnsan ve Çevre",
        "7. Ünite: Elektrik Devre Elemanları"
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
        "4. Ünite: Bilim, Teknoloji ve Toplum",
        "5. Ünite: Üretim, Dağıtım ve Tüketim",
        "6. Ünite: Etkin Vatandaşlık",
        "7. Ünite: Küresel İlişkiler"
    ],
    "İngilizce": [
        "Unit 1: Hello!",
        "Unit 2: My Town",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine",
        "Unit 5: Health",
        "Unit 6: Movies",
        "Unit 7: Party Time",
        "Unit 8: Fitness",
        "Unit 9: The Animal Shelter",
        "Unit 10: Festivities"
    ],
    "Almanca (Deutsch)": [
        "Einheit 1: Hallo! / Kennenlernen",
        "Einheit 2: Meine Familie und Ich",
        "Einheit 3: Schule und Schulsachen",
        "Einheit 4: Mein Tag / Uhrzeiten",
        "Einheit 5: Hobbys und Freizeit",
        "Einheit 6: Tiere und Farben"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket",
        "4. Ünite: Hz. Muhammed ve Aile Hayatı",
        "5. Ünite: Çevremizde Dinin İzleri"
    ],
    "Bilişim Teknolojileri ve Yazılım": [
        "1. Ünite: Bilişim Okuryazarlığı ve İletişim",
        "2. Ünite: İnternet Güvenliği ve Dijital Yurttaşlık",
        "3. Ünite: Görsel İşleme ve Sunum Programları",
        "4. Ünite: Problem Çözme ve Algoritma Mantığı"
    ],
    "Müzik & Beden Eğitimi": [
        "Müzik: Ses Bilgisi, Notalar ve Ritim",
        "Beden Eğitimi: Hareket Becerileri ve Oyun Kuralları"
    ],
    "Genel Kültür & Mega Bilgi Yarışması Havuzu": [
        "Mega Kategori: Dünya Coğrafyası ve Harita Bilgisi",
        "Mega Kategori: Tarihî İcatlar, Bilim İnsanları ve Keşifler",
        "Mega Kategori: Dünya Mutfağı, Coğrafi İşaretli Yemekler ve Kültür",
        "Mega Kategori: Doğa, Evren, Astronomi ve Genel Kültür"
    ]
}

def svg_iletki_aci_ciz(derece, etiket="Açı"):
    rad = math.radians(derece)
    x = int(140 + 85 * math.cos(rad))
    y = int(110 - 85 * math.sin(rad))
    return f'''
    <svg width="280" height="125" viewBox="0 0 280 125" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8fafc" rx="8" stroke="#e2e8f0"/>
      <path d="M 50 110 A 90 90 0 0 1 230 110 Z" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
      <line x1="50" y1="110" x2="230" y2="110" stroke="#334155" stroke-width="2"/>
      <line x1="140" y1="110" x2="225" y2="110" stroke="#94a3b8" stroke-width="3" stroke-dasharray="3"/>
      <line x1="140" y1="110" x2="{x}" y2="{y}" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>
      <circle cx="140" cy="110" r="4" fill="#1e40af"/>
      <text x="140" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">{etiket}: {derece}°</text>
    </svg>
    '''

def svg_sutun_grafik(kategori1, v1, kategori2, v2, baslik="Grafik"):
    max_v = max(v1, v2, 1)
    h1 = int((v1 / max_v) * 60)
    h2 = int((v2 / max_v) * 60)
    return f'''
    <svg width="280" height="125" viewBox="0 0 280 125" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="8" stroke="#cbd5e1"/>
      <text x="140" y="18" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e293b" text-anchor="middle">{baslik}</text>
      <rect x="50" y="{95 - h1}" width="45" height="{h1}" fill="#3b82f6" rx="3"/>
      <text x="72" y="{90 - h1}" font-family="sans-serif" font-size="10" fill="#1e293b" text-anchor="middle">{v1}</text>
      <text x="72" y="112" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="middle">{kategori1}</text>
      <rect x="160" y="{95 - h2}" width="45" height="{h2}" fill="#10b981" rx="3"/>
      <text x="182" y="{90 - h2}" font-family="sans-serif" font-size="10" fill="#1e293b" text-anchor="middle">{v2}</text>
      <text x="182" y="112" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="middle">{kategori2}</text>
    </svg>
    '''

MEGA_Dunya_Cografyasi = [
    ("Dünyanın en uzun nehirleri sıralamasında Nil Nehri'nden sonra ikinci sırada yer alan ve Güney Amerika'da bulunan dev nehir hangisidir?", "Amazon Nehri", ["Nil Nehri", "Mississippi Nehri", "Yangtze Nehri"]),
    ("Asya ve Avrupa kıtalarını birbirinden ayıran, İstanbul ve Çanakkale boğazlarını da içine alan su yolu sistemine ne denir?", "Türk Boğazları", ["Cebelitarık Boğazı", "Süveyş Kanalı", "Panama Kanalı"]),
    ("Dünyanın en büyük yüzölçümüne sahip ülkesi hangisidir?", "Rusya", ["Kanada", "Çin", "Amerika Birleşik Devletleri"]),
    ("Yeryüzünün en derin noktası olan Mariana Çukuru hangi okyanusta yer almaktadır?", "Pasifik (Büyük) Okyanusu", ["Atlantik Okyanusu", "Hint Okyanusu", "Arktik Okyanusu"]),
    ("Afrika kıtasının en kuzeyinde yer alan, Akdeniz'e kıyısı olan ve başkenti Tunus olan ülke hangisidir?", "Tunus", ["Fas", "Mısır", "Cezayir"]),
    ("Dünyanın en büyük çölü olup Afrika'nın kuzeyini kaplayan dev çölün adı nedir?", "Sahra Çölü", ["Gobi Çölü", "Atakama Çölü", "Kalahari Çölü"]),
    ("Güney Amerika kıtasında yer alan ve dünyanın en uzun sıradağları unvanını elinde bulunduran dağ silsilesi hangisidir?", "And Dağları", ["Alpler", "Himalaya Dağları", "Kayalık Dağları"]),
    ("Dünyanın en yüksek dağı olan Everest Dağı hangi iki ülkenin sınırında yer almaktadır?", "Nepal ve Çin (Tibet)", ["Hindistan ve Pakistan", "Şili ve Arjantin", "İsviçre ve İtalya"]),
    ("Avrupa'nın ortasından doğup Karadeniz'e dökülen, kıtanın en uzun ikinci nehri hangisidir?", "Tuna Nehri", ["Ron Nehri", "Ren Nehri", "Elbe Nehri"]),
    ("Türkiye'nin komşuları arasında yer almayan, Asya kıtasının doğusunda ada ülkesi olan devlet hangisidir?", "Japonya", ["İran", "Irak", "Suriye"])
]

MEGA_Tarih_Icatlar = [
    ("Matbaayı bularak bilginin ve kitapların kitlelere yayılmasını sağlayan tarihi mucit kimdir?", "Johannes Gutenberg", ["Thomas Edison", "Isaac Newton", "Alexander Graham Bell"]),
    ("Ampulü ve pratik elektrik dağıtım şebekesini geliştirerek dünyayı aydınlatan Amerikalı mucit kimdir?", "Thomas Edison", ["Nikola Tesla", "Albert Einstein", "Galileo Galilei"]),
    ("Telefonun icadıyla iletişim devrini başlatan ve sesin kabloyla iletimini sağlayan bilim insanı kimdir?", "Alexander Graham Bell", ["Guglielmo Marconi", "Samuel Morse", "Wright Kardeşler"]),
    ("Havacılık tarihinin ilk motorlu ve kontrollü uçuşunu gerçekleştiren mucit kardeşler kimlerdir?", "Wright Kardeşler", ["Montgolfier Kardeşler", "Leonardo da Vinci", "Igor Sikorsky"]),
    ("Kütleçekim kanununu keşfeden ve klasik mekaniğin temellerini atan İngiliz fizikçi kimdir?", "Isaac Newton", ["Galileo Galilei", "Johannes Kepler", "Copernicus"]),
    ("Rölativite (Görelilik) teorisiyle modern fiziğin çehresini değiştiren dahi fizikçi kimdir?", "Albert Einstein", ["Stephen Hawking", "Max Planck", "Niels Bohr"]),
    ("Pusulayı ilk kez yön bulma amacıyla kullanan ve denizcilik tarihine yön veren medeniyet hangisidir?", "Çinliler", ["Eski Mısırlılar", "Antik Yunanlılar", "Fenikeliler"]),
    ("İlk matbaanın ve yazı sisteminin milattan önce gelişim gösterdiği Mezopotamya medeniyeti hangisidir?", "Sümerler", ["Asurlular", "Babilliler", "Hititler"]),
    ("Rönesans döneminde Mona Lisa tablosunu çizen ve uçuş tasarımları yapan çok yönlü dahi kimdir?", "Leonardo da Vinci", ["Michelangelo", "Raffaello", "Donatello"]),
    ("Teleskobu gökyüzüne çevirerek Jüpiter'in uydularını keşfeden İtalyan astronom kimdir?", "Galileo Galilei", ["Nikola Kopernik", "Johannes Kepler", "Isaac Newton"])
]

MEGA_Dunya_Mutfa_Yemekler = [
    ("İtalya'nın Naples kentinde doğan, hamur üzerine domates sosu ve peynir eklenerek yapılan dünyaca ünlü yemek hangisidir?", "Pizza", ["Spagetti", "Lazanya", "Risotto"]),
    ("Japon mutfağına ait olan, sirke ile tatlandırılmış pirinç ve çiğ/pişmiş deniz ürünlerinin birleşiminden oluşan lezzet nedir?", "Suşi", ["Ramen", "Tempura", "Sashimi"]),
    ("Meksika mutfağından gelen, mısır veya buğday tortillası içerisine et, fasulye ve sebze sarılarak yapılan popüler yiyecek nedir?", "Tako", ["Burrito", "Nachos", "Quesadilla"]),
    ("Fransa kökenli olan, ince hamur katmanları arasına tatlı veya tuzlu malzemeler konularak yapılan hamur işi hangisidir?", "Kruvasan", ["Baget", "Makaron", "Quiche"]),
    ("Gaziantep yöremize ait, ince yıkanmış yufkalar arasına fıstık konularak fırınlanan coğrafi işaretli tatlımız nedir?", "Baklava", ["Künefe", "Kazandibi", "Sütlaç"]),
    ("Trabzon mutfağıyla özdeşleşen, uzun ve kayık şekilli, içerisine peynir ve yumurta kırılan hamur işi hangisidir?", "Karadeniz Pidesi", ["Lahmacun", "Mantı", "Börek"]),
    ("Hindistan mutfağının vazgeçilmezi olan, baharat ve otların yoğurt veya etle harmanlandığı aromatik yemek tarzı nedir?", "Köri Soslu Yemekler", ["Paella", "Fondü", "Ratatouille"]),
    ("Çin mutfağından dünyaya yayılan, ince hamur içine kıyma veya sebze doldurularak buharda pişirilen hamur yemeği nedir?", "Dim Sum", ["Noodle", "Wonton", "Pekin Ördeği"]),
    ("İspanya'ya özgü olan, safran, pirinç, deniz ürünleri ve etin geniş bir tavada pişirilmesiyle hazırlanan geleneksel yemek nedir?", "Paella", ["Tapas", "Gazpacho", "Tortilla"]),
    ("Kayseri ilimizle özdeşleşen, küçük hamur parçalarının içerisine kıyma konulup bükülerek suda haşlanan meşhur yemek nedir?", "Mantı", ["Erişte", "Tarhana", "Öcce"])
]

MEGA_Doga_Evren_Kultur = [
    ("Güneş sistemimizde Güneş'e en yakın olan ilk gezegen hangisidir?", "Merkür", ["Venüs", "Mars", "Dünya"]),
    ("Güneş sistemindeki en büyük gezegen unvanına sahip gaz devi hangisidir?", "Jüpiter", ["Satürn", "Uranüs", "Neptün"]),
    ("Dünya'nın uydusu olan Ay'ın evreleri arasında yeni ay ile dolunay arasında görülen parlak döneme ne denir?", "İlk Dördün", ["Son Dördün", "Hilal", "Şişkin Ay"]),
    ("Atmosferin dünyamızı zararlı güneş ışınlarından koruyan tabakasının adı nedir?", "Ozon Katmanı", ["Troposfer", "İyonosfer", "Mezosfer"]),
    ("Küresel iklim değişikliğine ve buzulların erimesine yol açan en temel sera gazı hangisidir?", "Karbondioksit (CO2)", ["Oksijen", "Azot", "Helyum"]),
    ("Dünya yüzeyinin yaklaşık yüzde kaçı sularla kaplıdır?", "%71", ["%50", "%30", "%85"]),
    ("Fotosentez yaparak oksijen üreten ve doğanın akciğerleri olarak bilinen canlı grubu hangisidir?", "Bitkiler ve Algler", ["Memeliler", "Sürüngenler", "Kuşlar"]),
    ("Güneş tutulması sırasında hangi gök cismi hangilerinin arasına girer?", "Ay, Güneş ile Dünya arasına girer", ["Dünya, Güneş ile Ay arasına girer", "Güneş, Ay ile Dünya arasına girer"]),
    ("Bir yıldızın yaşam döngüsünün sonunda süpernova patlamasıyla çökmesi sonucu oluşan, ışığın bile kaçamadığı çekim alanına ne denir?", "Karadelik", ["Nötron Yıldızı", "Beyaz Cüce", "Bulutsu"]),
    ("Yeryüzündeki tatlı su kaynaklarının en büyük oranı hangi formda depolanmıştır?", "Buzullar ve Kutuplar", ["Nehirler", "Yeraltı Gölleri", "Atmosferdeki Nem"])
]

def dinamik_yapay_zekali_soru_motoru(ders, unite):
    isimler = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin", "Kaan", "Deniz", "Ömer", "Duru", "Bora", "Ece", "Arda", "Eren", "Defne", "Mert", "Asya", "Kerem", "İrem"]
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Trabzon", "Konya", "Eskişehir", "Gaziantep", "Kars", "Erzurum", "Nevşehir", "Samsun", "Mersin", "Diyarbakır"]
    nesneler = ["fidan", "kitap", "bilye", "elma", "kalem", "sayfa", "pul", "kart", "çiçek", "ceviz"]
    
    kisi = random.choice(isimler)
    sehir = random.choice(sehirler)
    nesne = random.choice(nesneler)

    if "Mega Kategori" in ders:
        secilen_mega_havuz = []
        if "Coğrafyası" in unite:
            secilen_mega_havuz = MEGA_Dunya_Cografyasi
        elif "İcatlar" in unite:
            secilen_mega_havuz = MEGA_Tarih_Icatlar
        elif "Yemek" in unite:
            secilen_mega_havuz = MEGA_Dunya_Mutfa_Yemekler
        else:
            secilen_mega_havuz = MEGA_Doga_Evren_Kultur

        soru_tuple = random.choice(secilen_mega_havuz)
        q_text = soru_tuple[0]
        dogru = soru_tuple[1]
        celd = soru_tuple[2][:]
        random.shuffle(celd)
        
        siklar = [dogru] + celd[:3]
        random.shuffle(siklar)
        return {
            "ders": "Genel Kültür & Bilgi Yarışması",
            "unite": unite,
            "soru": q_text,
            "gorsel_svg": None,
            "siklar": list(dict.fromkeys(siklar)),
            "dogru": dogru
        }

    if ders == "Matematik":
        if "1. Ünite" in unite:
            b1, b2, b3 = random.randint(100, 999), random.randint(100, 999), random.randint(10, 999)
            sayi_str = f"{b3}{b2:03d}{b1:03d}"
            boluk_tipi = random.choice(["binler", "birler", "milyonlar"])
            q_text = f"{sehir} ilinde düzenlenen bilgi şöleninde {kisi}, {sayi_str} adet {nesne} sayısını incelemektedir. Bu doğal sayının **{boluk_tipi} bölüğünde** yer alan sayı aşağıdakilerden hangisidir?"
            
            if boluk_tipi == "binler":
                dogru = f"{b2:03d}"
                celd = [f"{b1:03d}", f"{b3:03d}", f"{(b2 + random.randint(1, 15)):03d}"]
            elif boluk_tipi == "birler":
                dogru = f"{b1:03d}"
                celd = [f"{b2:03d}", f"{b3:03d}", f"{(b1 + random.randint(1, 15)):03d}"]
            else:
                dogru = f"{b3}"
                celd = [f"{b1:03d}", f"{b2:03d}", f"{b3 + random.randint(1, 10)}"]

        elif "2. Ünite" in unite:
            pay = random.randint(2, 7)
            carpan = random.randint(2, 5)
            payda = (pay + random.randint(1, 5)) * carpan
            pay_gen = pay * carpan
            q_text = f"{kisi}, tarlasının {pay_gen}/{payda} kısmına organik domates ekmiştir. Bu kesrin **en sade hali** aşağıdakilerden hangisidir?"
            ebob = math.gcd(pay_gen, payda)
            dogru = f"{pay_gen//ebob}/{payda//ebob}"
            celd = [f"{(pay_gen//ebob) + 1}/{payda//ebob}", f"{pay_gen//ebob}/{(payda//ebob) + 2}", f"{(pay_gen//ebob)*2}/{(payda//ebob)*2 + 1}"]

        elif "3. Ünite" in unite:
            toplam = random.choice([120, 150, 200, 250, 300, 400, 500, 600])
            yuzde = random.choice([10, 20, 25, 30, 40, 50, 60, 75, 80])
            sonuc = (toplam * yuzde) // 100
            q_text = f"{kisi}, {toplam} adet {nesne} içeren arşivinin **%{yuzde}** kısmını dijital ortama aktarmıştır. {kisi} kaç adet {nesne} aktarmıştır?"
            dogru = f"{sonuc} adet"
            celd = [f"{sonuc + random.choice([5, 10, 15])} adet", f"{abs(sonuc - 8)} adet", f"{toplam - sonuc} adet"]

        elif "4. Ünite" in unite:
            aci_deg = random.choice([r for r in range(15, 175) if r != 90])
            tur = "Dar Açı" if aci_deg < 90 else "Geniş Açı"
            q_text = f"{kisi}, geometri tahtasında iletki yardımıyla {aci_deg}° ölçüsünde bir açı oluşturmuştur. Bu açının geometrik sınıfı hangisidir?"
            dogru = f"{tur}"
            celd = ["Dik Açı", "Doğru Açı", "Geniş Açı" if tur == "Dar Açı" else "Dar Açı"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_iletki_aci_ciz(aci_deg), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru}

        elif "5. Ünite" in unite:
            v1, v2 = random.randint(25, 95), random.randint(25, 95)
            fark = abs(v1 - v2)
            q_text = f"Grafikte {sehir} ve {random.choice(sehirler)} kentlerindeki günlük nem veya sıcaklık değerleri ({v1} ve {v2}) olarak ölçülmüştür. Bu iki değer arasındaki fark kaçtır?"
            dogru = f"{fark}"
            celd = [f"{fark + 4}", f"{v1 + v2}", f"{abs(fark - 3)}"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_sutun_grafik("A Kenti", v1, "B Kenti", v2, "İstatistiksel Veri Grafiği"), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru}

        else:
            kisa = random.randint(4, 12)
            uzun = random.randint(10, 20)
            alan = kisa * uzun
            q_text = f"Kenar uzunlukları {kisa} m ve {uzun} m olan dikdörtgen şeklindeki bir parkın **alanı** kaç m² dir?"
            dogru = f"{alan} m²"
            celd = [f"{(kisa + uzun)*2} m²", f"{alan + 14} m²", f"{abs(alan - 10)} m²"]

    elif ders == "Fen Bilimleri":
        if "1. Ünite" in unite:
            gok_cismi = random.choice(["Güneş", "Dünya", "Ay"])
            if gok_cismi == "Ay":
                q_text = f"{kisi}, gece gözlem kulübünde gökyüzünü incelerken {gok_cismi}'ın evrelerini çizmektedir. Dünyaya en yakın gök cismi ve doğal uydu kimdir?"
                dogru = "Ay"
                celd = ["Güneş", "Mars", "Jüpiter"]
            else:
                q_text = "Güneş, Dünya ve Ay'ın hacimsel ve boyutsal büyüklüklerine göre küçükten büyüğe doğru sıralaması hangisidir?"
                dogru = "Ay < Dünya < Güneş"
                celd = ["Dünya < Ay < Güneş", "Güneş < Dünya < Ay", "Ay < Güneş < Dünya"]

        elif "3. Ünite" in unite:
            zemin1, zemin2 = random.sample(["Buzlu cam zemin", "Halılı koridor", "Asfalt yol", "Cilalı parke", "Toprak zemin"], 2)
            q_text = f"{kisi}, deney arabasını **{zemin1}** ve **{zemin2}** üzerinde özdeş kuvvetle test ediyor. {zemin1} üzerinde arabanın daha çabuk durduğu saptanıyor. Bunun temel sebebi nedir?"
            dogru = f"{zemin1} yüzeyindeki sürtünme kuvvetinin daha yüksek olması"
            celd = [f"{zemin2} yüzeyinde yer çekiminin sıfır olması", "Arabanın tekerleklerinin plastik yapısı", "Ortam sıcaklığının değişmesi"]

        elif "7. Ünite" in unite:
            pil_sayisi = random.randint(2, 6)
            q_text = f"Basit bir elektrik devresinde ampul sayısı sabit tutulup özdeş pil sayısı **{pil_sayisi} katına** çıkarılırsa devredeki ampulün parlaklığı nasıl etkilenir?"
            dogru = "Parlaklık artış gösterir."
            celd = ["Parlaklık azalır.", "Parlaklık tamamen yok olur.", "Değişim gözlenmez."]

        else:
            q_text = f"{kisi}, fen laboratuvarında katı bir maddenin ısı alarak sıvı hale geçmeden doğrudan gaz hâline geçtiğini gözlemliyor. Bu hal değişiminin özel adı nedir?"
            dogru = "Süblimleşme"
            celd = ["Buharlaşma", "Erime", "Yoğuşma"]

    elif ders == "İngilizce":
        if "Unit 1" in unite or "Unit 2" in unite:
            ulke = random.choice(["Turkey", "Germany", "Spain", "Japan", "Britain", "Canada"])
            q_text = f"- Where is {kisi} from?\n- {kisi} is from **{ulke}**.\n\nWhich question prompts this answer?"
            dogru = "Where are you / is he from?"
            celd = ["What is your favorite hobby?", "How old are you?", "What time is it?"]
        elif "Unit 5" in unite:
            hastalik = random.choice(["headache", "toothache", "sore throat", "fever", "flu"])
            q_text = f"If {kisi} has a severe **{hastalik}**, what should {kisi} do according to health advice?"
            dogru = "Stay in bed, rest, and see a doctor."
            celd = ["Eat ice cream outside.", "Play intense basketball.", "Run a marathon."]
        else:
            q_text = f"Which English phrase correctly matches 'kitap okumak ve resim yapmak'?"
            dogru = "Read books and draw pictures"
            celd = ["Play dodgeball and swim", "Ride a horse and skate", "Listen to pop music and dance"]

    elif "Almanca" in ders:
        q_text = f"Almanca 'Wie geht es dir?' sorusuna {kisi} nasıl kibar bir yanıt vermelidir?"
        dogru = "Danke, es geht mir gut."
        celd = ["Ich heiße Mehmet.", "Ich bin elf Jahre alt.", "Auf Wiedersehen."]
    elif ders == "Türkçe":
        q_text = f"'{kisi} zorlu projeyi başarıyla tamamlayınca herkesin **takdirini topladı**.' cümlesindeki deyimin anlamı nedir?"
        dogru = "Beğenilmek ve övülmek"
        celd = ["Eşya toplamak", "Para biriktirmek", "Yarışmayı kaybetmek"]
    elif ders == "Sosyal Bilgiler":
        q_text = f"{sehir} ilinde ikamet eden {kisi}'nin çevresine karşı gösterdiği **en temel vatandaşlık sorumluluğu** nedir?"
        dogru = "Doğayı korumak ve toplumsal kurallara uymak"
        celd = ["Şehirdeki tüm binaları boyamak", "Yol yapımını üstlenmek", "Fabrika kurmak"]
    elif "Bilişim" in ders:
        q_text = f"{kisi}, dijital dünyada kişisel verilerini korumak için ne tür bir şifre tercih etmelidir?"
        dogru = "Büyük-küçük harf, rakam ve sembol içeren karmaşık şifreler"
        celd = ["123456 sayı dizisi", "Doğum tarihi", "Sadece adı"]
    else:
        q_text = f"{kisi}, müzik dersinde ritim tutarken temel nota değerlerini öğrenmektedir. Bu disiplinli çalışma neyi geliştirir?"
        dogru = "Estetik algı ve ritim duyusu"
        celd = ["Fiziksel kas gücü", "Matematiksel hız", "Yabancı dil"]

    siklar = [dogru] + celd
    random.shuffle(siklar)
    return {
        "ders": ders,
        "unite": unite,
        "soru": q_text,
        "gorsel_svg": None,
        "siklar": list(dict.fromkeys(siklar)),
        "dogru": dogru
    }

def harmanlanmis_soru_uret(secilen_uniteler, hedef_sayi):
    havuz = []
    hash_kayitlari = set()
    
    if not secilen_uniteler:
        return []
        
    u_count = len(secilen_uniteler)
    taban = hedef_sayi // u_count
    kalan = hedef_sayi % u_count
    dagilim = [taban + (1 if i < kalan else 0) for i in range(u_count)]
    
    for idx, (h_ders, h_unite) in enumerate(secilen_uniteler):
        istenen = dagilim[idx]
        uretilen = 0
        deneme = 0
        
        while uretilen < istenen and deneme < 1000:
            deneme += 1
            s = dinamik_yapay_zekali_soru_motoru(h_ders, h_unite)
            
            fingerprint = hashlib.sha256((s["soru"] + "".join(s["siklar"]) + s["dogru"]).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_kayitlari and len(s["siklar"]) == 4:
                hash_kayitlari.add(fingerprint)
                havuz.append(s)
                uretilen += 1
                
    # DERSLERE GÖRE GRUPLAMA VE SIRALAMA (Aynı dersin soruları peş peşe gelsin)
    havuz.sort(key=lambda x: x["ders"])
    return havuz

st.title("🎓 MEB 5. Sınıf Tümü Kapsayan Soru Bankası")

st.sidebar.header("⚙️ Müfredat ve Mega Havuz Seçimi")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=("Genel Kültür" in ders_adi or "Matematik" in ders_adi)):
        select_all = st.checkbox(f"Tüm {ders_adi} Üniteleri", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])

if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    if secilen_uniteler:
        if st.sidebar.button("✨ Ders Sıralı Test Üret", type="primary", use_container_width=True):
            with st.spinner("Sorular derslere göre gruplanıp sıraya diziliyor..."):
                sorular = harmanlanmis_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.sidebar.warning("⚠️ Lütfen en az 1 ünite veya mega havuz seçin.")

if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("🚀 Çok Yönlü Soru Üretim Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Kategori/Ünite Sayısı: **{len(secilen_uniteler)}**. Sorular derslerine göre gruplanacak ve bir ders bitmeden diğerine geçilmeyecektir.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular ders bazlı gruplandırılarak hazırlandı!")
    
    # Ders dağılımını göster
    ders_dagilimi = {}
    for s in st.session_state["soru_listesi"]:
        d = s["ders"]
        ders_dagilimi[d] = ders_dagilimi.get(d, 0) + 1
        
    st.markdown("### 📋 Ders Dağılımı:")
    for d, c in ders_dagilimi.items():
        st.write(f"- **{d}**: {c} Soru")
    
    toplam_sn = st.session_state["toplam_sure_sn"]
    st.markdown(f"**Toplam Soru:** {len(st.session_state['soru_listesi'])} | **Tahmini Süre:** {toplam_sn // 60} Dk {toplam_sn % 60} Sn")
    
    col1, col2 = st.columns(2)
    if col1.button("⏱️ Testi Başlat", type="primary"):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
        
    if col2.button("🔄 Yeniden Üret"):
        st.session_state["sorular_hazir"] = False
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

    # Ders değişimi kontrolü ve bildirimi
    c_left, c_right = st.columns([3, 1])
    c_left.markdown(f"### 📚 Ders: **{q['ders']}**")
    c_right.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")
    
    st.caption(f"📌 Ünite / Kategori: {q['unite']}")
    st.markdown(f"#### **Soru {idx + 1} / {len(st.session_state['soru_listesi'])}**\n{q['soru']}")

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=135)

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
        sonraki_soru = st.session_state["soru_listesi"][idx + 1]
        btn_label = "Sonraki Soru ➡️"
        if sonraki_soru["ders"] != q["ders"]:
            btn_label = f"Diğer Derse Geç ({sonraki_soru['ders']}) ➡️"
            
        if b2.button(btn_label, type="primary"):
            st.session_state["mevcut_soru_index"] += 1
            st.rerun()
    else:
        if b2.button("🏁 Testi Bitir", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Test Sonu Karnesi")
    
    toplam = len(st.session_state["soru_listesi"])
    dogru = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    
    st.metric("Doğru / Toplam", f"{dogru} / {toplam}")
    st.progress(dogru / toplam if toplam > 0 else 0)
    
    if st.button("🔄 Yeni Test Yap"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
