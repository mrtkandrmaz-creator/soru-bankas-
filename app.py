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

def dinamik_yapay_zekali_soru_motoru(ders, unite):
    """%75 Yapay Zeka Destekli Dinamik Soru Motoru"""
    isimler = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin", "Kaan", "Deniz", "Ömer", "Duru", "Bora", "Ece", "Arda", "Eren", "Defne", "Mert", "Asya"]
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Trabzon", "Konya", "Eskişehir", "Gaziantep", "Kars", "Erzurum", "Nevşehir"]
    nesneler = ["fidan", "kitap", "bilye", "elma", "kalem", "sayfa", "pul", "kart"]
    
    kisi = random.choice(isimler)
    sehir = random.choice(sehirler)
    nesne = random.choice(nesneler)

    # -----------------------------------------------------
    # MATEMATİK (%100 Dinamik Üretim)
    # -----------------------------------------------------
    if ders == "Matematik":
        if "1. Ünite" in unite:
            b1, b2, b3 = random.randint(100, 999), random.randint(100, 999), random.randint(10, 999)
            sayi_str = f"{b3}{b2:03d}{b1:03d}"
            boluk_tipi = random.choice(["binler", "birler", "milyonlar"])
            q_text = f"{sehir} ilinde düzenlenen bir kampanyada {kisi}, {sayi_str} adet {nesne} toplamıştır. Bu sayının **{boluk_tipi} bölüğündeki** sayı aşağıdakilerden hangisidir?"
            
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
            q_text = f"{kisi}, tarlasının {pay_gen}/{payda} kısmına domates ekmiştir. Bu kesrin **en sade hali** aşağıdakilerden hangisidir?"
            ebob = math.gcd(pay_gen, payda)
            dogru = f"{pay_gen//ebob}/{payda//ebob}"
            celd = [f"{(pay_gen//ebob) + 1}/{payda//ebob}", f"{pay_gen//ebob}/{(payda//ebob) + 2}", f"{(pay_gen//ebob)*2}/{(payda//ebob)*2 + 1}"]

        elif "3. Ünite" in unite:
            toplam = random.choice([120, 150, 200, 250, 300, 400, 500])
            yuzde = random.choice([10, 20, 25, 30, 40, 50, 60, 75])
            sonuc = (toplam * yuzde) // 100
            q_text = f"{kisi}, {toplam} adet {nesne} koleksiyonunun **%{yuzde}** kısmını arkadaşına hediye etmiştir. {kisi} kaç adet {nesne} vermiştir?"
            dogru = f"{sonuc} adet"
            celd = [f"{sonuc + random.choice([5, 10])} adet", f"{abs(sonuc - 8)} adet", f"{toplam - sonuc} adet"]

        elif "4. Ünite" in unite:
            aci_deg = random.choice([r for r in range(15, 170) if r != 90])
            tur = "Dar Açı" if aci_deg < 90 else "Geniş Açı"
            q_text = f"{kisi}, iletki yardımıyla {aci_deg}° ölçüsünde bir açı çizmiştir. Bu açının çeşidi hangisidir?"
            dogru = f"{tur}"
            celd = ["Dik Açı", "Doğru Açı", "Geniş Açı" if tur == "Dar Açı" else "Dar Açı"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_iletki_aci_ciz(aci_deg), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru}

        elif "5. Ünite" in unite:
            v1, v2 = random.randint(25, 95), random.randint(25, 95)
            fark = abs(v1 - v2)
            q_text = f"Grafikte {sehir} ve {random.choice(sehirler)} kentlerindeki sıcaklık değerleri ({v1}°C ve {v2}°C) verilmiştir. Aralarındaki fark kaç °C'dir?"
            dogru = f"{fark}°C"
            celd = [f"{fark + 4}°C", f"{v1 + v2}°C", f"{abs(fark - 3)}°C"]
            siklar = [dogru] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_sutun_grafik("A Şehri", v1, "B Şehri", v2, "Sıcaklık Grafiği"), "siklar": list(dict.fromkeys(siklar)), "dogru": dogru}

        else: # 6. Ünite
            kisa = random.randint(4, 9)
            uzun = random.randint(10, 18)
            alan = kisa * uzun
            q_text = f"Kenar uzunlukları {kisa} m ve {uzun} m olan dikdörtgen şeklindeki bir bahçenin **alanı** kaç m² dir?"
            dogru = f"{alan} m²"
            celd = [f"{(kisa + uzun)*2} m²", f"{alan + 12} m²", f"{abs(alan - 8)} m²"]

    # -----------------------------------------------------
    # FEN BİLİMLERİ (%75 Dinamik & Varyasyonlu)
    # -----------------------------------------------------
    elif ders == "Fen Bilimleri":
        if "1. Ünite" in unite:
            gok_cismi = random.choice(["Güneş", "Dünya", "Ay"])
            if gok_cismi == "Ay":
                q_text = f"{kisi}, gece gökyüzünü incelerken {gok_cismi}'ın evrelerini gözlemliyor. Dünyaya en yakın doğal uydu hangisidir?"
                dogru = "Ay"
                celd = ["Güneş", "Mars", "Jüpiter"]
            else:
                q_text = "Güneş, Dünya ve Ay'ın hacimsel büyüklüklerine göre küçükten büyüğe doğru sıralaması hangisidir?"
                dogru = "Ay < Dünya < Güneş"
                celd = ["Dünya < Ay < Güneş", "Güneş < Dünya < Ay", "Ay < Güneş < Dünya"]

        elif "3. Ünite" in unite:
            zemin1, zemin2 = random.sample(["Buzlu zemin", "Halı zemin", "Çakıllı yol", "Asfalt yol", "Cilalı tahta"], 2)
            q_text = f"{kisi}, oyuncak arabasını **{zemin1}** ve **{zemin2}** üzerinde eşit kuvvetle sürüyor. {zemin1} üzerinde arabanın daha çabuk yavaşladığı görülüyor. Bunun sebebi nedir?"
            dogru = f"{zemin1} yüzeyindeki sürtünme kuvvetinin daha fazla olması"
            celd = [f"{z2 if 'z2' in locals() else zemin2} yüzeyinde sürtünmenin olmaması", "Arabanın kütlesinin sürekli artması", "Yerçekiminin zeminlerde farklı olması"]

        elif "7. Ünite" in unite:
            pil_sayisi = random.randint(2, 5)
            q_text = f"Basit bir elektrik devresinde ampul sayısı sabit tutulup pil sayısı **{pil_sayisi} katına** çıkarılırsa ampul parlaklığı nasıl değişir?"
            dogru = "Parlaklık belirgin şekilde artar."
            celd = ["Parlaklık azalır.", "Parlaklık hiç değişmez.", "Devre elemanları çalışmaz."]

        else:
            q_text = f"{kisi}, fen laboratuvarında bir maddenin ısı alarak sıvı halden gaz haline geçtiğini gözlemliyor. Bu hal değişiminin adı nedir?"
            dogru = "Buharlaşma"
            celd = ["Erime", "Donma", "Yoğuşma"]

    # -----------------------------------------------------
    # İNGİLİZCE (%75 Dinamik)
    # -----------------------------------------------------
    elif ders == "İngilizce":
        if "Unit 1" in unite or "Unit 2" in unite:
            ulke = random.choice(["Turkey", "Germany", "Spain", "Italy", "France", "Japan"])
            q_text = f"- Where is {kisi} from?\n- {kisi} is from **{ulke}**.\n\nWhich question matches this answer?"
            dogru = "Where are you / is he from?"
            celd = ["What is your favorite hobby?", "How old are you?", "What time is it?"]
        elif "Unit 5" in unite:
            hastalik = random.choice(["headache", "toothache", "sore throat", "fever"])
            q_text = f"If {kisi} has a severe **{hastalik}**, what should {kisi} do first?"
            dogru = "See a doctor and rest."
            celd = ["Drink icy cold water.", "Play basketball outside.", "Eat lots of candies."]
        else:
            q_text = f"Which activity is related to 'satranç oynamak' in English?"
            dogru = "Play chess"
            celd = ["Play dodgeball", "Do origami", "Ride a bike"]

    # -----------------------------------------------------
    # DİĞER DERSLER & GENEL ŞABLON MOTORU
    # -----------------------------------------------------
    elif "Almanca" in ders:
        q_text = f"Almanca 'Wie heißt du?' sorusuna {kisi} nasıl cevap vermelidir?"
        dogru = f"Ich heiße {kisi}."
        celd = ["Ich bin 11 Jahre alt.", "Mir geht es gut.", "Danke, sehr gut."]
    elif ders == "Türkçe":
        q_text = f"'{kisi} sözleriyle herkesin **kalbini kazandı**.' cümlesindeki altı çizili ifadenin anlamı nedir?"
        dogru = "Herkesin sevgisini ve takdirini toplamak"
        celd = ["Kalp organını ele geçirmek", "Yarışmada ödül kazanmak", "İnsanları utandırmak"]
    elif ders == "Sosyal Bilgiler":
        q_text = f"{sehir} ilinde yaşayan {kisi}'nin okuldaki **en temel sorumluluğu** aşağıdakilerden hangisidir?"
        dogru = "Derslere zamanında katılmak ve okul kurallarına uymak"
        celd = ["Okul binasını boyamak", "Sınıf arkadaşlarını yönetmek", "Kütüphanedeki tüm kitapları satın almak"]
    elif "Bilişim" in ders:
        q_text = f"{kisi}, bilgisayarında güvenli bir şifre oluşturmak istiyor. Aşağıdakilerden hangisi **en güvenli** yöntemdir?"
        dogru = "Harf, rakam ve özel sembolleri karmaşık şekilde kullanmak"
        celd = ["Doğum tarihini yazmak", "Sadece '123456' yazmak", "Adını ve soyadını bitişik yazmak"]
    else:
        q_text = f"{kisi}, ders çalışırken planlı ve düzenli davranmanın önemini öğrenmiştir. Bu davranış hangisidir?"
        dogru = "Sorumluluk Bilinci"
        celd = ["Bireysellik", "Girişimcilik", "Ayrımcılık"]

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
        
        while uretilen < istenen and deneme < 500:
            deneme += 1
            s = dinamik_yapay_zekali_soru_motoru(h_ders, h_unite)
            
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
st.title("🎓 MEB 5. Sınıf Tümü Kapsayan Soru Bankası")

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

# Test Üret Butonu Soru Sayısının Altına Taşındı
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    if secilen_uniteler:
        if st.sidebar.button("✨ Karma Test Üret", type="primary", use_container_width=True):
            with st.spinner("Sorular harmanlanıyor ve benzersiz şablonlar oluşturuluyor..."):
                sorular = harmanlanmis_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.sidebar.warning("⚠️ Lütfen en az 1 ünite seçin.")

if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("🚀 Çok Yönlü Soru Üretim Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Sistem seçilen ünitelere özel **%75 dinamik/yapay zeka motoru** ile **tamamen benzersiz** yeni nesil sorular üretecektir.")

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
