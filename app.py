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
        "Einheit 1: Hallo! / Kennenlernen (Tanışma ve Selamlaşma)",
        "Einheit 2: Meine Familie und Ich (Ailem ve Ben)",
        "Einheit 3: Schule und Schulsachen (Okul ve Okul Eşyaları)",
        "Einheit 4: Mein Tag / Uhrzeiten (Günlük Yaşam ve Saatler)",
        "Einheit 5: Hobbys und Freizeit (Hobiler ve Serbest Zaman)",
        "Einheit 6: Tiere und Farben (Hayvanlar ve Renkler)"
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

def milyonluk_varyasyon_engine(ders, unite, alt_tip=None):
    isimler = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin", "Kaan", "Deniz", "Ömer", "Duru", "Bora", "Ece", "Arda", "Eren", "Defne", "Mert", "Asya"]
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Trabzon", "Konya", "Eskişehir", "Gaziantep", "Kars", "Erzurum", "Nevşehir"]

    # -----------------------------------------------------
    # MATEMATİK ENGINE
    # -----------------------------------------------------
    if ders == "Matematik":
        sub_types = [
            "dogal_sayi_okuma", "basamak_degeri", "islemler_problem", "bolme_kalan", 
            "kesir_sadelestirme", "kesir_toplama", "ondalik_cozumleme", "yuzde_hesap",
            "aci_turu", "geometri_alan", "grafik_okuma", "uzunluk_donusum"
        ]
        sub_type = alt_tip if alt_tip in sub_types else random.choice(sub_types)
        
        if sub_type == "dogal_sayi_okuma":
            boluk1 = random.randint(100, 999)
            boluk2 = random.randint(100, 999)
            boluk3 = random.randint(10, 999)
            sayi_str = f"{boluk3}{boluk2:03d}{boluk1:03d}"
            
            q_text = f"Bir ağaçlandırma projesinde toplam {sayi_str} adet meşe fidanı dikilmiştir. Bu sayının binler bölüğündeki sayı aşağıdakilerden hangisidir?"
            dogru = f"{boluk2:03d}"
            celd = [f"{boluk1:03d}", f"{boluk3:03d}", f"{boluk2 + 12:03d}"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "kesir_sadelestirme":
            pay = random.randint(2, 9)
            carpan = random.randint(3, 8)
            payda = (pay + random.randint(1, 4)) * carpan
            pay_gen = pay * carpan
            
            q_text = f"Bir tarlanın {pay_gen}/{payda} 'lik kısmına buğday ekilmiştir. Bu kesrin en sade hali aşağıdakilerden hangisidir?"
            ebob = math.gcd(pay_gen, payda)
            dogru = f"{pay_gen//ebob}/{payda//ebob}"
            celd = [f"{pay_gen//ebob + 1}/{payda//ebob}", f"{pay_gen//ebob}/{payda//ebob + 2}", f"{(pay_gen//ebob)*2}/{(payda//ebob)*2 + 1}"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "aci_turu":
            aci_deg = random.choice([r for r in range(15, 170) if r != 90])
            tur = "Dar Açı" if aci_deg < 90 else "Geniş Açı"
            kisi = random.choice(isimler)
            
            q_text = f"{kisi}, iletki ile defterine {aci_deg}° ölçüsünde bir açı çizmiştir. Bu açının çeşidi hangisidir?"
            dogru = f"{tur}"
            celd = ["Dik Açı", "Doğru Açı", "Geniş Açı" if tur == "Dar Açı" else "Dar Açı"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_iletki_aci_ciz(aci_deg), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "yuzde_hesap":
            toplam = random.choice([100, 200, 300, 400, 500])
            yuzde = random.choice([10, 20, 25, 30, 40, 50])
            sonuc = (toplam * yuzde) // 100
            kisi = random.choice(isimler)
            
            q_text = f"{kisi}, {toplam} sayfalık kitabın %{yuzde}'ini okumuştur. {kisi} toplam kaç sayfa okumuştur?"
            dogru = f"{sonuc} sayfa"
            celd = [f"{sonuc + 10} sayfa", f"{sonuc - 5} sayfa", f"{toplam - sonuc} sayfa"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            v1, v2 = random.randint(20, 90), random.randint(20, 90)
            fark = abs(v1 - v2)
            q_text = f"Sütun grafiğinde A ve B kütüphanelerindeki kitap ödünç sayıları ({v1} ve {v2}) gösterilmektedir. İki sayı arasındaki fark kaçtır?"
            dogru = f"{fark}"
            celd = [f"{fark + 5}", f"{v1 + v2}", f"{abs(fark - 4)}"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_sutun_grafik("A Okulu", v1, "B Okulu", v2), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # FEN BİLİMLERİ ENGINE
    # -----------------------------------------------------
    elif ders == "Fen Bilimleri":
        sub_types = ["gunes_dunya_ay", "canlilar", "surtunme", "madde_hal", "isik_golge", "devre"]
        sub_type = alt_tip if alt_tip in sub_types else random.choice(sub_types)
        kisi = random.choice(isimler)

        if sub_type == "gunes_dunya_ay":
            q_text = f"Güneş, Dünya ve Ay'ın büyüklükleri göz önüne alındığında, küçükten büyüğe doğru sıralama hangisidir?"
            dogru = "Ay < Dünya < Güneş"
            celd = ["Dünya < Ay < Güneş", "Güneş < Dünya < Ay", "Ay < Güneş < Dünya"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "surtunme":
            z1, z2 = random.sample(["Zımparalı zemin", "Buzlu zemin", "Halı zemin", "Cilalı tahta"], 2)
            q_text = f"{kisi}, oyuncak arabasını {z1} ve {z2} üzerinde eşit kuvvetle itiyor. {z1} yüzeyinde arabanın daha kısa sürede durduğu gözleniyor. Bu durumun nedeni nedir?"
            dogru = f"{z1} yüzeyindeki sürtünme kuvvetinin daha fazla olması"
            celd = [f"{z2} yüzeyinde sürtünmenin olmaması", "Arabanın kütlesinin değişmesi", "Yerçekiminin zeminlerde farklı olması"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "devre":
            q_text = "Basit bir elektrik devresinde pil sayısı artırılıp ampul sayısı sabit tutulursa ampul parlaklığı nasıl değişir?"
            dogru = "Parlaklık artar."
            celd = ["Parlaklık azalır.", "Parlaklık değişmez.", "Ampul tamamen söner."]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            q_text = "Aşağıdakilerden hangisi maddelerin ısı alarak katı halden sıvı hale geçmesi olayıdır?"
            dogru = "Erime"
            celd = ["Donma", "Buharlaşma", "Yoğuşma"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # ALMANCA (DEUTSCH) ENGINE
    # -----------------------------------------------------
    elif "Almanca" in ders:
        sub_types = ["begruessung", "familie", "schule", "uhrzeit", "hobbys", "farben_tiere"]
        sub_type = alt_tip if alt_tip in sub_types else random.choice(sub_types)
        kisi = random.choice(isimler)

        if sub_type == "begruessung":
            q_text = "Almanca 'Wie heißt du?' (Senin adın ne?) sorusuna verilebilecek en uygun yanıt hangisidir?"
            dogru = "Ich heiße Tim."
            celd = ["Ich bin 11 Jahre alt.", "Mir geht es gut.", "Danke, sehr gut."]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "schule":
            q_text = "Almanca okul eşyalarından 'Bleistift' sözcüğünün Türkçe karşılığı nedir?"
            dogru = "Kurşun Kalem"
            celd = ["Okul Çantası", "Defter", "Silgi"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "uhrzeit":
            q_text = "'Es ist zehn Uhr.' ifadesinin Türkçe karşılığı aşağıdakilerden hangisidir?"
            dogru = "Saat 10:00."
            celd = ["Saat 02:00.", "Saat 05:00.", "Saat 12:00."]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "farben_tiere":
            q_text = "Almanca 'Der Hund ist braun.' cümlesinin Türkçe anlamı hangisidir?"
            dogru = "Köpek kahverengidir."
            celd = ["Kedi siyahtır.", "Kuş sarıdır.", "Köpek beyazdır."]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            q_text = "Almanca 'Mein Lieblingshobby ist Schwimmen.' cümlesinde bahsedilen hobi hangisidir?"
            dogru = "Yüzme"
            celd = ["Futbol Oynama", "Müzik Dinleme", "Resim Yapma"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # İNGİLİZCE ENGINE
    # -----------------------------------------------------
    elif ders == "İngilizce":
        sub_types = ["greetings", "daily_routine", "hobbies", "health", "animals"]
        sub_type = alt_tip if alt_tip in sub_types else random.choice(sub_types)

        if sub_type == "greetings":
            q_text = "Which of the following completes the dialogue correctly?\n\n- 'Where are you from?'\n- 'I am from __________.'"
            dogru = "Turkey"
            celd = ["Turkish", "English", "Spanish"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "health":
            q_text = "If someone has a 'headache', what should they do?"
            dogru = "Take a medicine and rest."
            celd = ["Drink cold water.", "Play basketball.", "Eat ice cream."]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            q_text = "Which pairing of 'Action - Meaning' is CORRECT?"
            dogru = "Ride a bike ➔ Bisiklete binmek"
            celd = ["Play chess ➔ Yüzmek", "Do origami ➔ Şarkı söylemek", "Climb a tree ➔ Resim yapmak"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # BİLİŞİM TEKNOLOJİLERİ ENGINE
    # -----------------------------------------------------
    elif "Bilişim" in ders:
        sub_types = ["guvenlik", "donanim_yazilim", "algoritma"]
        sub_type = alt_tip if alt_tip in sub_types else random.choice(sub_types)

        if sub_type == "guvenlik":
            q_text = "Aşağıdakilerden hangisi güçlü ve güvenli bir şifre oluşturma kuralıdır?"
            dogru = "Harf, sayı ve özel karakterleri karmaşık biçimde kullanmak"
            celd = ["Doğum tarihini veya adını yazmak", "Sadece '123456' gibi ardışık sayılar seçmek", "Şifreyi herkesin görebileceği yere yapıştırmak"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            q_text = "Bir sorunun çözümü için izlenmesi gereken adım adım sıralı yola ne ad verilir?"
            dogru = "Algoritma"
            celd = ["Donanım", "İşletim Sistemi", "İnternet Tarayıcısı"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # TÜRKÇE & SOSYAL & DİN & DİĞER DERSLER
    # -----------------------------------------------------
    elif ders == "Türkçe":
        q_text = "Aşağıdaki cümlelerin hangisinde mecaz (soyut/benzetmeli) bir anlatım vardır?"
        dogru = "Sözleriyle kalbimi kırdı."
        celd = ["Masadaki bardağı yere düşürdü.", "Dışarıda hafif bir yağmur yağıyordu.", "Otobüs durağa zamanında ulaştı."]
        siklar = [dogru] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": "turkce_mecaz"}

    elif ders == "Sosyal Bilgiler":
        q_text = "Sorumluluk ve hak kavramları düşünüldüğünde, aşağıdakilerden hangisi bir öğrencinin okuldaki 'sorumluluğudur'?"
        dogru = "Derslere zamanında girmek ve okul kurallarına uymak"
        celd = ["Temiz bir çevrede eğitim alma hakkını kullanmak", "Kütüphaneden yararlanmak", "Tenefüste dinlenmek"]
        siklar = [dogru] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": "sosyal_hak"}

    elif "Din" in ders:
        q_text = "Aşağıdakilerden hangisi nezaket ve adap kurallarına uygun bir davranıştır?"
        dogru = "Bir ortama girildiğinde selam vermek ve güler yüzlü olmak"
        celd = ["Konuşan birinin sözünü kesmek", "Emanet edilen eşyayı izinsiz başkasına vermek", "Başkalarının özel alanlarına izin almadan girmek"]
        siklar = [dogru] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": "din_adap"}

    else: # Müzik / Beden vb.
        q_text = "Müzikte seslerin sürelerini ve yüksekliklerini göstermeye yarayan simgelere ne ad verilir?"
        dogru = "Nota"
        celd = ["Porte", "Sol Anahtarı", "Vuruş"]
        siklar = [dogru] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": "muzik_nota"}

def harmanlanmis_soru_uret(secilen_uniteler, hedef_sayi):
    havuz = []
    hash_kayitlari = set()
    
    if not secilen_uniteler:
        return []
        
    u_count = len(secilen_uniteler)
    taban = hedef_sayi // u_count
    kalan = hedef_sayi % u_count
    dagilim = [taban + (1 if i < kalan else 0) for i in range(u_count)]
    
    # Tüm kategorilerden eşit ve harmanlanmış sorular çek
    for idx, (h_ders, h_unite) in enumerate(secilen_uniteler):
        istenen = dagilim[idx]
        uretilen = 0
        deneme = 0
        
        while uretilen < istenen and deneme < 400:
            deneme += 1
            s = milyonluk_varyasyon_engine(h_ders, h_unite)
            
            # Benzersizlik doğrulama parmak izi
            fingerprint = hashlib.sha256((s["soru"] + "".join(s["siklar"]) + s["dogru"]).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_kayitlari and len(s["siklar"]) == 4:
                hash_kayitlari.add(fingerprint)
                havuz.append(s)
                uretilen += 1
                
    random.shuffle(havuz)
    return havuz

# -----------------------------------------------------
# STREAMLIT ARAYÜZ
# -----------------------------------------------------
st.title("🎓 MEB 5. Sınıf Tümü Kapsayan Soru Bankası (Almanca Dahil)")

st.sidebar.header("⚙️ Müfretad ve Ders Seçimi")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=("Almanca" in ders_adi or "Matematik" in ders_adi)):
        select_all = st.checkbox(f"Tüm {ders_adi} Üniteleri", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])

if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("🚀 Çok Yönlü Soru Üretim Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Sistem seçilen tüm derslerin soru tiplerinden **farklı kombinasyonlarda**, **tamamen benzersiz** ve **MEB Beceri Temelli** sorular üretecektir.")
        
        if st.button("✨ Karma Test Üret", type="primary"):
            with st.spinner("Sorular harmanlanıyor ve benzersiz şablonlar oluşturuluyor..."):
                sorular = harmanlanmis_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.warning("⚠️ Lütfen sol taraftaki menüden en az 1 ders/ünite seçin.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular tüm MEB soru tiplerinden harmanlanarak başarıyla üretildi!")
    
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

    c_left, c_right = st.columns([3, 1])
    c_left.caption(f"📌 {q['ders']} - {q['unite']}")
    c_right.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")

    st.markdown(f"### **Soru {idx + 1}:**\n{q['soru']}")

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
        if b2.button("Sonraki Soru ➡️", type="primary"):
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
