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
        "5. Ünite: Üretim, Dağıtım ve Tüketim"
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

def milyonluk_varyasyon_engine(ders, unite):
    u_low = unite.lower()
    
    isimler = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin", "Kaan", "Deniz", "Ömer", "Duru", "Bora", "Ece", "Arda", "Eren", "Yara", "Kuzey", "Defne", "Mert", "Asya"]
    nesneler = ["kitap", "kalem", "bilye", "fidan", "sayfa", "pul", "çikolata", "roket maketi", "balon", "oyuncak", "etiket", "fındık", "ceviz", "kartPOSTAL"]
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Trabzon", "Konya", "Eskişehir", "Gaziantep", "Kars", "Erzurum", "Muğla", "Nevşehir", "Sivas"]
    kurum_kulup = ["Çevre Kulübü", "TEMA Derneği", "Satranç Kulübü", "TÜBİTAK Proje Ekibi", "Okul Meclisi", "Sıfır Atık Timi", "Robotik Takımı"]

    # -----------------------------------------------------
    # MATEMATİK ENGINE
    # -----------------------------------------------------
    if ders == "Matematik":
        sub_type = random.choice([
            "dogal_sayi_okuma", "basamak_degeri", "islemler_problem", "bolme_kalan", 
            "kesir_sadelestirme", "kesir_toplama", "ondalik_cozumleme", "yuzde_hesap",
            "aci_turu", "geometri_alan", "grafik_okuma", "uzunluk_donusum"
        ])
        
        if sub_type == "dogal_sayi_okuma":
            boluk1 = random.randint(100, 999)
            boluk2 = random.randint(100, 999)
            boluk3 = random.randint(10, 999)
            sayi_str = f"{boluk3}{boluk2:03d}{boluk1:03d}"
            
            soru_p = random.choice([
                f"Aşağıdaki sayılardan hangisinin milyonlar bölüğündeki rakamların toplamı {sum(int(x) for x in str(boluk3))} sayısıdır?",
                f"Bir fidan dikme kampanyasında toplam {sayi_str} adet fidan dikilmiştir. Bu sayının binler bölüğünde hangi sayı yer almaktadır?",
                f"Rakamları birbirinden farklı dokuz basamaklı bir kurguda, binler basamağı {str(boluk2)[1]} olan sayı aşağıdakilerden hangisi olabilir?"
            ])
            dogru = f"{boluk2:03d}" if "binler bölüğü" in soru_p else str(sayi_str)
            celdiriciler = [f"{boluk1:03d}", f"{boluk3:03d}", f"{boluk2 + 15:03d}", f"{boluk1 + 25:03d}"]
            if dogru in celdiriciler: celdiriciler.remove(dogru)
            
            siklar = [dogru] + celdiriciler[:3]
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": soru_p, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "kesir_sadelestirme":
            pay = random.randint(2, 12)
            çarpan = random.randint(3, 9)
            payda = (pay + random.randint(1, 5)) * çarpan
            pay_gen = pay * çarpan
            
            kisi = random.choice(isimler)
            q_text = f"{kisi}, bir tarlanın {pay_gen}/{payda} 'lik kısmına buğday ekmiştir. Bu kesrin en sade gösterimi aşağıdakilerden hangisidir?"
            
            # En sadeleştirme basitleştirmesi
            ebob = math.gcd(pay_gen, payda)
            dogru_sade = f"{pay_gen//ebob}/{payda//ebob}"
            celd = [f"{pay_gen//ebob + 1}/{payda//ebob}", f"{pay_gen//ebob}/{payda//ebob + 2}", f"{(pay_gen//ebob)*2}/{(payda//ebob)*2 + 1}"]
            siklar = [dogru_sade] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru_sade, "kategori": sub_type}

        elif sub_type == "ondalik_cozumleme" or "ondalık" in u_low:
            tam = random.randint(10, 99)
            onda = random.randint(1, 9)
            yüzde = random.randint(1, 9)
            ondalik_val = f"{tam}.{onda}{yüzde}"
            
            q_text = f"Ondalık gösterimi {ondalik_val} olan sayı için verilen basamak çözümlemelerinden hangisi doğrudur?"
            dogru = f"({tam//10} x 10) + ({tam%10} x 1) + ({onda} x 0,1) + ({yüzde} x 0,01)"
            celd = [
                f"({tam//10} x 10) + ({tam%10} x 1) + ({onda} x 0,01) + ({yüzde} x 0,001)",
                f"({tam} x 1) + ({onda} x 0,1) + ({yüzde} x 0,1)",
                f"({tam//10} x 100) + ({tam%10} x 10) + ({onda} x 0,1)"
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "aci_turu" or "açı" in u_low:
            aci_deg = random.choice([r for r in range(15, 175) if r != 90])
            tur = "Dar Açı" if aci_deg < 90 else "Geniş Açı"
            kisi = random.choice(isimler)
            
            q_text = f"{kisi}, iletki ile bir deftere {aci_deg}° ölçüsünde bir açı çiziyor. Bu açı hakkında aşağıdakilerden hangisi söylenebilir?"
            dogru = f"Bu açı bir {tur}dır."
            celd = [
                f"Bu açı bir Dik Açıdır.",
                f"Bu açı bir Doğru Açıdır.",
                f"Bu açı bir {'Geniş Açı' if tur == 'Dar Açı' else 'Dar Açı'}dır."
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_iletki_aci_ciz(aci_deg), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "grafik_okuma" or "veri" in u_low:
            v1, v2 = random.randint(15, 95), random.randint(15, 95)
            k1, k2 = random.sample(["Geri Dönüşüm", "Kompost Atık", "Plastik", "Mavi Kapak", "Kağıt Atık"], 2)
            fark = abs(v1 - v2)
            
            q_text = f"Grafikte {k1} ve {k2} toplama miktarları (kg) gösterilmiştir. İki miktar arasındaki fark kaç kg'dır?"
            dogru = f"{fark} kg"
            celd = [f"{fark + 10} kg", f"{v1 + v2} kg", f"{abs(fark - 5)} kg"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_sutun_grafik(k1, v1, k2, v2), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            kisi = random.choice(isimler)
            n1, n2, n3 = random.randint(120, 450), random.randint(15, 80), random.randint(3, 8)
            ans_val = (n1 + n2) * n3
            
            q_text = f"{kisi}, her birinde {n1} sayfa bulunan kitap serisinden satın alıyor. Daha sonra {n2} sayfa daha ek fasikül çözüp kalan tüm çalışmasını {n3} katına çıkartıyor. Toplam kaç sayfa soru çözülmüştür?"
            dogru = str(ans_val)
            celd = [str(ans_val + 20), str(ans_val - 45), str((n1 * n3) + n2)]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # FEN BİLİMLERİ ENGINE
    # -----------------------------------------------------
    elif ders == "Fen Bilimleri":
        sub_type = random.choice(["gunes_dunya_ay", "canlilar", "surtunme", "madde_hal", "isik_golge", "devre"])
        kisi = random.choice(isimler)
        
        if sub_type == "gunes_dunya_ay" or "güneş" in u_low:
            oran = random.choice(["Güneş > Dünya > Ay", "Dünya > Ay", "Güneş en büyüktür"])
            q_text = f"{kisi}, Fen dersi projesi için Güneş, Dünya ve Ay'ın hacimsel büyüklüklerini kıyaslayan meyve modelleri hazırlamıştır.\n\nBuna göre doğru sıralama aşağıdakilerden hangisidir?"
            dogru = "Güneş > Dünya > Ay"
            celd = ["Dünya > Güneş > Ay", "Ay > Dünya > Güneş", "Güneş > Ay > Dünya"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "surtunme" or "sürtünme" in u_low:
            z1, z2 = random.sample(["Zımpara Kağıdı", "Buz Pisti", "Halı Zemin", "Cilalı Parke"], 2)
            q_text = f"Öğrenci {kisi}, dinamometreye bağladığı tahta takozu sırasıyla {z1} ve {z2} üzerinde çekmiştir. {z1} üzerindeki dinamometre değerinin daha yüksek olduğu görülmüştür.\n\nBu gözleme göre çıkarılabilecek KESİN sonuç hangisidir?"
            dogru = f"{z1} yüzeyindeki sürtünme kuvveti {z2} yüzeyinden daha fazladır."
            celd = [
                f"{z2} yüzeyindeki sürtünme kuvveti daha fazladır.",
                "Tahta takozun kütlesi zemin değiştikçe artmıştır.",
                "Dinamometre sadece buz üzerinde doğru ölçüm yapar."
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "isik_golge" or "ışık" in u_low:
            mesafe = random.randint(10, 50)
            q_text = f"Saydam olmayan bir cisim, ışık kaynağına {mesafe} cm yaklaştırıldığında perdedeki tam gölgenin boyunda nasıl bir değişim gözlenir?"
            dogru = "Tam gölge boyu büyür."
            celd = ["Tam gölge boyu küçülür.", "Tam gölge boyu değişmez.", "Gölge tamamen kaybolur ve saydamlaşır."]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            canli = random.choice(["Şapkalı Mantar", "Amip", "Eğrelti Otu", "Bakteri", "Yosun"])
            q_text = f"Sınıf panosunda resimleri verilen '{canli}' canlı türü hangi canlı grubu altında incelenmektedir?"
            
            grup_dict = {"Şapkalı Mantar": "Mantarlar", "Amip": "Mikroskobik Canlılar", "Eğrelti Otu": "Bitkiler", "Bakteri": "Mikroskobik Canlılar", "Yosun": "Bitkiler"}
            dogru = grup_dict.get(canli, "Mikroskobik Canlılar")
            celd = [g for g in ["Hayvanlar", "Bitkiler", "Mantarlar", "Mikroskobik Canlılar"] if g != dogru]
            siklar = [dogru] + celd[:3]
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # TÜRKÇE ENGINE
    # -----------------------------------------------------
    elif ders == "Türkçe":
        sub_type = random.choice(["sozcuk_anlam", "noktalama", "yazim_kurallari", "paragraf_anafikir", "deyimler"])
        kisi = random.choice(isimler)
        
        if sub_type == "deyimler":
            deyim_list = [
                ("Gözden düşmek", "Değerini ve sevgisini kaybetmek"),
                ("Kulak kabartmak", "Çaktırmadan, belli etmeden dinlemek"),
                ("İğne ile kuyu kazmak", "Çok yetersiz araçlarla büyük sabır gerektiren bir işe girişmek"),
                ("Etekleri zil çalmak", "Çok sevinmek ve coşgulu olmak")
            ]
            d_ad, d_anlam = random.choice(deyim_list)
            q_text = f"'{d_ad}' deyiminin cümle içerisinde doğru kullanımı aşağıdakilerden hangisidir?"
            dogru = f"{kisi}, sınav sonucunun çok iyi geldiğini öğrenince adeta etekleri zil çaldı / {d_anlam.lower()} durumunu yaşadı."
            celd = [
                f"{kisi}, arkadaşının gizli konuşmalarına kulak kabartıp ortamdan uzaklaştı.",
                f"{kisi}, ödevini yapmadığı için hemen {d_ad.lower()} durumuna ulaştı.",
                f"Yavaş yürüyen kaplumbağayı görünce hepsi gülmekten katıldı."
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "noktalama" or "noktalama" in u_low:
            q_text = f"Aşağıdaki cümlelerin hangisinde tırnak işareti ( \" \" ) veya kesme işareti ( ' ) yanlış kullanılmıştır?"
            dogru = f"Ankara'dan gelen otobüs saat 14.30'da otogara vardımı?"
            celd = [
                f"{kisi} \"Yarın kütüphanede buluşalım.\" dedi.",
                f"MEB'in yayımladığı Beceri Temelli Sorular çok faydalı.",
                f"Türkiye'nin başkenti Ankara, tarihi zenginliğiyle bilinir."
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            q_text = f"\"Doğadaki tüm canlılar birbiriyle uyum içerisindedir. Bir halkanın kopması tüm zinciri etkiler.\" \n\nYukarıdaki paragrafa göre çıkarılabilecek ANA FİKİR aşağıdakilerden hangisidir?"
            dogru = "Doğadaki ekolojik denge ve canlılar arası dayanışma hayati önem taşır."
            celd = [
                "İnsanlar doğayı istedikleri gibi şekillendirebilir.",
                "Sadece büyük hayvanlar ekosistem için önemlidir.",
                "Çevre kirliliği sadece şehirleri ilgilendiren bir sorundur."
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

    # -----------------------------------------------------
    # SOSYAL BİLGİLER ENGINE
    # -----------------------------------------------------
    else:
        sub_type = random.choice(["hak_sorumluluk", "kultur_miras", "cografi_unsur", "uretim_tuketim", "bilim_teknoloji"])
        kisi = random.choice(isimler)
        sehir = random.choice(sehirler)
        
        if sub_type == "hak_sorumluluk":
            q_text = f"5. sınıf öğrencisi {kisi}'nin katıldığı {random.choice(kurum_kulup)} kapsamında üstlenebileceği 'SORUMLULUK' örneği aşağıdakilerden hangisidir?"
            dogru = "Toplantı saatlerine zamanında uymak ve verilen görevleri eksiksiz tamamlamak"
            celd = [
                "Düşüncelerini özgürce ifade etme hakkını kullanmak",
                "Okul kütüphanesinden dilediği kitabı ödünç almak",
                "Sağlıklı bir çevrede yaşama hakkını talep etmek"
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        elif sub_type == "kultur_miras":
            eserler = ["Peri Bacaları", "Çatalhöyük", "Göbeklitepe", "Pamukkale Travertenleri", "Sümela Manastırı"]
            secilen_eser = random.choice(eserler)
            is_dogal = secilen_eser in ["Peri Bacaları", "Pamukkale Travertenleri"]
            
            q_text = f"{kisi}, ailesiyle gittiği {sehir} gezisinde '{secilen_eser}' yapısını incelemiştir. Bu varlık hakkında aşağıdakilerden hangisi söylenebilir?"
            dogru = f"Bu varlık bir {'Doğal Varlık' if is_dogal else 'Tarihi Eser / Beşeri Yapı'} örneğidir."
            celd = [
                f"Bu varlık bir {'Beşeri Yapı' if is_dogal else 'Doğal Unsur'} örneğidir.",
                "İnsan eli değmeden günümüz teknolojisiyle yapılmıştır.",
                "Sadece sanayi alanında kullanılan bir üretim tesisidir."
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

        else:
            q_text = f"{sehir} bölgesinde yetiştirilen tarımsal ürünlerin fabrikalarda işlenip market raflarına gelmesi sürecinde hangi ekonomik faaliyet aşamaları sırasıyla uygulanmıştır?"
            dogru = "Üretim ➔ Dağıtım ➔ Tüketim"
            celd = [
                "Tüketim ➔ Üretim ➔ Dağıtım",
                "Dağıtım ➔ Tüketim ➔ Üretim",
                "İthalat ➔ İhracat ➔ Tüketim"
            ]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": dogru, "kategori": sub_type}

def sonsuz_benzersiz_soru_uret(secilen_uniteler, hedef_sayi):
    havuz = []
    hash_kayitlari = set()
    kategori_kayitlari = set()
    
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
        
        while uretilen < istenen and deneme < 300:
            deneme += 1
            s = milyonluk_varyasyon_engine(h_ders, h_unite)
            
            # Benzersizlik doğrulama parmak izi
            fingerprint = hashlib.sha256((s["soru"] + "".join(s["siklar"]) + s["dogru"]).encode('utf-8')).hexdigest()
            kat_key = f"{h_ders}_{s.get('kategori', '')}_{s['dogru']}"
            
            # Hem soru kalıbı hem de şık cevabı benzersizliği kontrolü
            if fingerprint not in hash_kayitlari and kat_key not in kategori_kayitlari and len(s["siklar"]) == 4:
                hash_kayitlari.add(fingerprint)
                kategori_kayitlari.add(kat_key)
                havuz.append(s)
                uretilen += 1
                
    random.shuffle(havuz)
    return havuz

st.title("🎓 MEB Milyonluk Yeni Nesil Soru Bankası")

st.sidebar.header("⚙️ Müfretad ve Soru Ayarları")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=False):
        select_all = st.checkbox(f"Tüm {ders_adi} Üniteleri", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])

if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("🚀 Yeni Nesil Soru Üretim Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Sistem seçilen her üniteden **eşit sayıda**, **tamamen benzersiz** ve **MEB Beceri Temelli** sorular üretecektir.")
        
        if st.button("✨ Milyonluk Soru Havuzundan Üret", type="primary"):
            with st.spinner("Soru şablonları taranıyor, SHA-256 benzersizlik doğrulamasından geçiriliyor..."):
                sorular = sonsuz_benzersiz_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.warning("⚠️ Lütfen sol taraftaki menüden en az 1 ünite seçin.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular benzersiz şablon kombinasyonlarıyla başarıyla üretildi!")
    
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
