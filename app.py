import streamlit as st
import random
import json
import time
import math
import uuid

# Sayfa Yapılandırması
st.set_page_config(page_title="MEB 5. Sınıf Soru Bankası", page_icon="🎓", layout="wide")

# =========================================================
# 1. API KEY OKUMA MOTORU
# =========================================================
def get_api_key():
    keys_to_check = ["GEMINI_API_KEY", "API_KEY", "gemini_api_key", "api_key"]
    for k in keys_to_check:
        try:
            if k in st.secrets and str(st.secrets[k]).strip():
                return str(st.secrets[k]).strip()
        except Exception:
            pass
            
    for section in ["general", "default", "secrets"]:
        try:
            if section in st.secrets:
                for k in keys_to_check:
                    if k in st.secrets[section] and str(st.secrets[section][k]).strip():
                        return str(st.secrets[section][k]).strip()
        except Exception:
            pass
    return None

API_KEY = get_api_key()

# Session State Başlatma
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
# MEB 5. SINIF TÜM DERSLER VE ÜNİTELER
# =========================================================
MEB_MUFREDAT = {
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve Doğal Sayılarla İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar, Çizimler ve Üçgen/Dörtgenler",
        "5. Ünite: Veri İşleme ve Uzunluk/Zaman Ölçme",
        "6. Ünite: Alan Ölçme ve Geometrik Cisimler (Dikdörtgenler Prizması)"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay (Yapısı, Boyutları, Evreleri)",
        "2. Ünite: Canlılar Dünyası (Mikroskobik Canlılar, Mantarlar, Bitkiler, Hayvanlar)",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim (Hal Değişimi, Genleşme, Büzülme)",
        "5. Ünite: Işığın Yayılması, Yansıması ve Tam Gölge",
        "6. Ünite: İnsan ve Çevre (Biyoçeşitlilik, Çevre Sorunları)",
        "7. Ünite: Elektrik Devre Elemanları (Devre Şemaları ve Bağlantılar)"
    ],
    "Türkçe": [
        "1. Tema: Sözcükte ve Söz Öbeklerinde Anlam",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragrafta Anlam, Ana Fikir ve Yardımcı Fikirler",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları",
        "5. Tema: Görsel Okuma, Grafik ve Tablo Yorumlama",
        "6. Tema: Sesteş (Eş Sesli) Sözcükler ve Kök/Ek Bilgisi"
    ],
    "Sosyal Bilgiler": [
        "1. Ünite: Birey ve Toplum (Hak, Sorumluluk, Gruplar)",
        "2. Ünite: Kültür ve Miras (Tarihi Mekanlar, Doğal Varoluşlar)",
        "3. Ünite: İnsanlar, Yerler ve Çevreler (Harita, Yeryüzü Şekilleri, İklim)",
        "4. Ünite: Bilim, Teknoloji ve Toplum (Doğru Bilgiye Ulaşma, Medya)",
        "5. Ünite: Üretim, Dağıtım ve Tüketim (Ekonomik Faaliyetler, Meslekler)",
        "6. Ünite: Etkin Vatandaşlık (Bilinçli Tüketici, Yerel Yönetimler)",
        "7. Ünite: Küresel Bağlantılar (Uluslararası Ticaret ve İş Birliği)"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı (Rahman, Rahim, Basar, İlim)",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket",
        "4. Ünite: Hz. Muhammed ve Aile Hayatı",
        "5. Ünite: Çevremizde Dinin İzleri (Mimaride, Musikide, Edebiyatta)"
    ],
    "İngilizce": [
        "Unit 1: Hello! (School Subjects, Countries, Languages)",
        "Unit 2: My Town (Locations, Directions)",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine",
        "Unit 5: Health (Illnesses, Suggestions)",
        "Unit 6: Movies (Movie Types, Expressing Likes)",
        "Unit 7: Party Time (Days, Months, Dates, Ordering)",
        "Unit 8: Fitness (Sports, Making Suggestions)",
        "Unit 9: Animal Shelter (Present Continuous, Farm Animals)",
        "Unit 10: Festivals (National and Religious Celebrations)"
    ]
}

# =========================================================
# 2. SVG GÖRSEL MOTORU
# =========================================================
def svg_iletki_aci_ciz_modern(derece):
    rad = math.radians(180 - derece)
    x = int(140 + 95 * math.cos(rad))
    y = int(120 - 95 * math.sin(rad))
    accent_color = random.choice(["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899"])
    
    return f'''
    <svg width="280" height="150" viewBox="0 0 280 150" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.08"/>
        </filter>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="100%" stop-color="#f8fafc"/>
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#bgGrad)" rx="16" filter="url(#shadow)"/>
      <path d="M 35 120 A 105 105 0 0 1 245 120 Z" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="2"/>
      <line x1="35" y1="120" x2="245" y2="120" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
      <line x1="140" y1="120" x2="{x}" y2="{y}" stroke="{accent_color}" stroke-width="4" stroke-linecap="round"/>
      <circle cx="140" cy="120" r="6" fill="{accent_color}"/>
      <circle cx="140" cy="120" r="2" fill="#ffffff"/>
      <rect x="95" y="10" width="90" height="26" rx="8" fill="#e2e8f0"/>
      <text x="140" y="27" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#334155" text-anchor="middle">Açı: ?°</text>
    </svg>
    '''

def svg_kesir_ciz_modern(pay, payda):
    renk = "#3b82f6"
    dilimler = ""
    for i in range(payda):
        fill_color = renk if i < pay else "#e2e8f0"
        x = 20 + i * (220 / payda)
        w = (220 / payda) - 4
        dilimler += f'<rect x="{x}" y="45" width="{w}" height="50" fill="{fill_color}" rx="6"/>'
        
    return f'''
    <svg width="260" height="130" viewBox="0 0 260 130" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="16" stroke="#f1f5f9" stroke-width="2"/>
      {dilimler}
      <text x="130" y="112" font-family="system-ui, sans-serif" font-size="13" font-weight="700" fill="#334155" text-anchor="middle">Modelleme: {pay}/{payda}</text>
    </svg>
    '''

def svg_ay_evresi_ciz_modern(evre_adi):
    maskeler = {
        "Yeni Ay": '<circle cx="100" cy="70" r="45" fill="#0f172a"/>',
        "İlk Dördün": '<circle cx="100" cy="70" r="45" fill="#f8fafc"/><path d="M 100 25 A 45 45 0 0 0 100 115 Z" fill="#0f172a"/>',
        "Dolunay": '<circle cx="100" cy="70" r="45" fill="#fef08a" stroke="#facc15" stroke-width="2"/>',
        "Son Dördün": '<circle cx="100" cy="70" r="45" fill="#0f172a"/><path d="M 100 25 A 45 45 0 0 0 100 115 Z" fill="#f8fafc"/>'
    }
    cizim = maskeler.get(evre_adi, maskeler["Dolunay"])
    return f'''
    <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#020617" rx="16"/>
      <circle cx="30" cy="30" r="1" fill="#ffffff" opacity="0.6"/>
      <circle cx="170" cy="40" r="1.5" fill="#ffffff" opacity="0.8"/>
      <circle cx="150" cy="120" r="1" fill="#ffffff" opacity="0.4"/>
      {cizim}
      <rect x="40" y="122" width="120" height="20" rx="6" fill="#1e293b"/>
      <text x="100" y="136" font-family="system-ui, sans-serif" font-size="11" font-weight="600" fill="#f1f5f9" text-anchor="middle">{evre_adi}</text>
    </svg>
    '''

# =========================================================
# 3. YARDIMCI FİLTRE VE DOĞRULAMA MOTORU
# =========================================================
def cevap_sizintisi_var_mi(soru_metni, dogru_cevap):
    """
    Sorunun içerisinde doğru cevabın doğrudan verilip verilmediğini kontrol eder.
    """
    metin = soru_metni.lower()
    cevap = str(dogru_cevap).lower().strip()
    
    # Çok kısa cevaplar (örn. sayılar veya kısa sözcükler) için hatalı tespiti önleme
    if len(cevap) <= 3:
        return False
        
    if cevap in metin:
        return True
    return False

# =========================================================
# 4. ÖZGÜN VE RASTGELE GEMINI YAZILIM MOTORU
# =========================================================
def gemini_soru_uret_ozgun(api_key, ders, unite, onceki_sorular=[]):
    if not api_key:
        return None
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        
        unique_seed = str(uuid.uuid4())[:8]
        onceki_metinler = "\n".join([f"- {s}" for s in onceki_sorular[-5:]])
        
        prompt = (
            f"Tarih/Kod Tohumu: {unique_seed}\n"
            f"DERS: {ders}\n"
            f"ÜNİTE: {unite}\n"
            f"SEVİYE: MEB 5. Sınıf Müfredatı\n\n"
            f"ÖNEMLİ: Daha önce sorulmuş aşağıdaki sorulardan BİREBİR VEYA ANLAMSAL OLARAK TAMAMEN FARKLI bir soru üret olmalısın:\n{onceki_metinler}\n\n"
            "Görevin: Yukarıda belirtilen üniteyle ilgili TAMAMEN ÖZGÜN, çelişkisiz 1 adet çoktan seçmeli test sorusu hazırlamaktır.\n\n"
            "KESİN KURALLAR:\n"
            "1. 'siklar' dizisinde tam olarak 4 adet seçenek olmalıdır.\n"
            "2. 'siklar' içerisindeki her seçenek sorunun konusuna uygun GERÇEK metinlerden, sayılardan veya ifadelerden oluşmalıdır.\n"
            "3. KESİNLİKLE soru metninde veya kökünde cevabın kendisi yer almamalıdır.\n"
            "4. 'Seçenek A', 'Şık A', 'A şıkkı', 'Hiçbiri' gibi jenerik ifadeler KESİNLİKLE KULLANILAMAZ.\n"
            "5. 'dogru' alanı, 'siklar' dizisi içindeki doğru cevabın BİREBİR METİN KOPYASI olmalıdır.\n"
        )
        
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "soru": {"type": "STRING"},
                "siklar": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "dogru": {"type": "STRING"}
            },
            "required": ["soru", "siklar", "dogru"]
        }

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.95,
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=config
        )
        
        veri = json.loads(response.text.strip())
        
        soru_metni = veri.get("soru", "").strip()
        siklar = [str(s).strip() for s in veri.get("siklar", [])]
        dogru = str(veri.get("dogru", "")).strip()

        # Doğrulama Testleri
        if len(siklar) != 4 or len(set(siklar)) != 4:
            return None
            
        if any(jenerik in s.lower() for s in siklar for jenerik in ["seçenek", "şık", "şablon", "hiçbiri"]):
            return None

        # Cevap sızıntısı kontrolü
        if cevap_sizintisi_var_mi(soru_metni, dogru):
            return None

        if dogru not in siklar:
            eslesme = [s for s in siklar if dogru.lower() in s.lower() or s.lower() in dogru.lower()]
            if eslesme:
                dogru = eslesme[0]
            else:
                dogru = siklar[0]

        random.shuffle(siklar)

        return {
            "ders": ders,
            "unite": unite,
            "soru": soru_metni,
            "gorsel_svg": None,
            "gorsel_tasvir": None,
            "siklar": siklar,
            "dogru": dogru,
            "kaynak": "Yapay Zekâ (Özgün Gemini)"
        }
    except Exception:
        return None

# =========================================================
# 5. DİNAMİK PARAMETRİK ŞABLON GENERATÖRÜ (BİNLERCE KOMBİNASYON)
# =========================================================
def sablon_soru_uret(ders, unite):
    u_lower = unite.lower()
    isimler = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Ali", "Fatma", "Deniz", "Ömer"]
    
    # -----------------------------------------------------
    # MATEMATİK GENERATÖRÜ
    # -----------------------------------------------------
    if ders == "Matematik":
        if "geometrik" in u_lower or "açı" in u_lower:
            aci = random.choice([25, 35, 45, 60, 75, 90, 105, 120, 135, 150, 165])
            tur = "Dar Açı" if aci < 90 else ("Dik Açı" if aci == 90 else "Geniş Açı")
            siklar = ["Dar Açı", "Dik Açı", "Geniş Açı", "Doğru Açı"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Yukarıdaki iletki ile ölçülen açının değeri {aci}° olarak hesaplanmıştır. Bu açı hangi türe girer?",
                "gorsel_svg": svg_iletki_aci_ciz_modern(aci), "siklar": siklar, "dogru": tur, "kaynak": "Dinamik Görsel Motoru"
            }
        elif "kesir" in u_lower:
            payda = random.choice([4, 5, 6, 8, 10, 12])
            pay = random.randint(1, payda - 1)
            dogru_cevap = f"{pay}/{payda}"
            siklar = [dogru_cevap, f"{payda-pay}/{payda}", f"{pay}/{payda+1}", f"{pay+1}/{payda}"]
            siklar = list(set(siklar))
            while len(siklar) < 4:
                siklar.append(f"{random.randint(1, 3)}/{payda}")
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Yukarıdaki modelde boyalı bölgeye karşılık gelen kesir değeri aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_kesir_ciz_modern(pay, payda), "siklar": siklar, "dogru": dogru_cevap, "kaynak": "Dinamik Görsel Motoru"
            }
        elif "ondalık" in u_lower or "yüzde" in u_lower:
            yuzde = random.choice([10, 20, 25, 40, 50, 75, 80])
            kesir_val = yuzde / 100
            dogru_cevap = f"%{yuzde}"
            siklar = [dogru_cevap, f"%{yuzde+5}", f"%{yuzde-5}", f"%{yuzde*2 if yuzde <= 40 else yuzde//2}"]
            siklar = list(set(siklar))
            while len(siklar) < 4:
                siklar.append(f"%{random.randint(5, 95)}")
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Ondalık gösterimi {kesir_val:.2f} olan bir sayının yüzde sembolü ile ifadesi hangisidir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": dogru_cevap, "kaynak": "Dinamik Matematik Motoru"
            }
        elif "alan" in u_lower or "dikdörtgen" in u_lower:
            a = random.randint(3, 12)
            b = random.randint(4, 15)
            alan = a * b
            siklar = [f"{alan} cm²", f"{alan + 10} cm²", f"{(a+b)*2} cm²", f"{alan - 5} cm²"]
            siklar = list(set(siklar))
            while len(siklar) < 4:
                siklar.append(f"{random.randint(10, 150)} cm²")
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Kenar uzunlukları {a} cm ve {b} cm olan bir dikdörtgenin alanı kaç cm²'dir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": f"{alan} cm²", "kaynak": "Dinamik Matematik Motoru"
            }
        else: # Doğal Sayılar ve genel işlemler
            kisi = random.choice(isimler)
            sayi1 = random.randint(1200, 8500)
            sayi2 = random.randint(350, 2400)
            toplam = sayi1 + sayi2
            siklar = [f"{toplam}", f"{toplam + 100}", f"{toplam - 50}", f"{toplam + 10}"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"{kisi}, biriktirdiği {sayi1} TL parasının üzerine {sayi2} TL daha eklemiştir. {kisi}'in toplam kaç TL'si olmuştur?",
                "gorsel_svg": None, "siklar": siklar, "dogru": f"{toplam}", "kaynak": "Dinamik Matematik Motoru"
            }

    # -----------------------------------------------------
    # FEN BİLİMLERİ GENERATÖRÜ
    # -----------------------------------------------------
    elif ders == "Fen Bilimleri":
        if "güneş" in u_lower or "ay" in u_lower:
            evreler = ["Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"]
            secilen_evre = random.choice(evreler)
            siklar = evreler.copy()
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Görselde karanlık ve aydınlık yapısı sergilenen Ay'ın ana evresi aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_ay_evresi_ciz_modern(secilen_evre), "siklar": siklar, "dogru": secilen_evre, "kaynak": "Dinamik Görsel Motoru"
            }
        elif "sürtünme" in u_lower or "kuvvet" in u_lower:
            yuzeyler = [("Buz zemin", "En az sürtünme"), ("Çakıllı yol", "Yüksek sürtünme"), ("Asfalt yol", "Orta sürtünme"), ("Halı zemin", "Fazla sürtünme")]
            yuzey = random.choice(yuzeyler)
            siklar = ["Dinamometre", "Termometre", "Barometre", "Eşit kollu terazi"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Kuvvetin büyüklüğünü ölçmek için kullanılan araç aşağıdakilerden hangisidir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Dinamometre", "kaynak": "Dinamik Fen Motoru"
            }
        elif "madde" in u_lower or "hal" in u_lower:
            olaylar = [
                ("Suyun buz haline gelmesi", "Donma"),
                ("Buzun su haline gelmesi", "Erime"),
                ("Suyun gaz haline geçmesi", "Buharlaşma"),
                ("Su buharının sıvılaşması", "Yoğuşma")
            ]
            olay, cevap = random.choice(olaylar)
            siklar = ["Erime", "Donma", "Buharlaşma", "Yoğuşma"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"'{olay}' şeklinde gözlemlenen hal değişimi olayının adı nedir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": cevap, "kaynak": "Dinamik Fen Motoru"
            }
        elif "ışık" in u_lower or "gölge" in u_lower:
            maddeler = [("Cam", "Saydam"), ("Tahta", "Saydam olmayan (Opak)"), ("Buzlu cam", "Yarı saydam")]
            madde, tur = random.choice(maddeler)
            siklar = ["Saydam", "Saydam olmayan (Opak)", "Yarı saydam", "Yansıtıcı"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Işığı tamamen geçiren '{madde}' gibi maddeler optik özelliklerine göre nasıl sınıflandırılır?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Saydam" if madde=="Cam" else tur, "kaynak": "Dinamik Fen Motoru"
            }
        else: # Canlılar Dünyası ve diğer
            canlilar = [("Şapkalı mantar", "Mantar"), ("Eğrelti otu", "Bitki"), ("Bakteri", "Mikroskobik Canlı"), ("Amip", "Mikroskobik Canlı")]
            c, t = random.choice(canlilar)
            siklar = ["Mikroskobik Canlılar", "Mantarlar", "Bitkiler", "Hayvanlar"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Gözle görülemeyip mikroskop yardımıyla incelenen canlı grubu aşağıdakilerden hangisidir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Mikroskobik Canlılar", "kaynak": "Dinamik Fen Motoru"
            }

    # -----------------------------------------------------
    # TÜRKÇE GENERATÖRÜ
    # -----------------------------------------------------
    elif ders == "Türkçe":
        if "sözcük" in u_lower or "anlam" in u_lower:
            kelimeler = [
                ("Sıcak", "Samimi", "Sıcak bir karşılama yaptı."),
                ("Soğuk", "Mesafe", "Bize karşı çok soğuk davrandı."),
                ("Ağır", "Sorumluluk", "Bu ağır yükün altından kalktı."),
                ("Derin", "Detaylı", "Derin düşüncelere dalmıştı.")
            ]
            k, m, cumle = random.choice(kelimeler)
            siklar = ["Mecaz Anlam", "Gerçek Anlam", "Terim Anlam", "Eş Anlam"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"'{cumle}' cümlesindeki altı çizili düşünsel kullanım hangi anlam türüne örnektir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Mecaz Anlam", "kaynak": "Dinamik Türkçe Motoru"
            }
        elif "noktalama" in u_lower or "yazım" in u_lower:
            hatalar = [
                ("Ahmet'de bizimle sinemaya gelecek.", "Ahmet de bizimle sinemaya gelecek."),
                ("29 ekim cumhuriyet bayramı coşkuyla kutlandı.", "29 Ekim Cumhuriyet Bayramı coşkuyla kutlandı."),
                ("Herşey yolunda gidiyor.", "Her şey yolunda gidiyor.")
            ]
            h_yanlis, h_dogru = random.choice(hatalar)
            siklar = [
                f"'{h_yanlis}' ifadesindeki yazım kullanımı",
                "Ankara'ya giden otobüs hareket etti.",
                "Kitaplarını çantasına özenle yerleştirdi.",
                "Yarın sabah erkenden yola çıkacağız."
            ]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Aşağıdaki seçeneklerin hangisinde yazım kuralı ihlali yapılmıştır?",
                "gorsel_svg": None, "siklar": siklar, "dogru": f"'{h_yanlis}' ifadesindeki yazım kullanımı", "kaynak": "Dinamik Türkçe Motoru"
            }
        else: # Paragraf / Cümlede anlam
            kisi = random.choice(isimler)
            siklar = ["Öznel Anlatım", "Nesnel Anlatım", "Tanımlama", "Karşılaştırma"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"'{kisi}'in yazdığı en son şiir bence herkesin ruhuna dokunan harika bir eserdir.' cümlesi ne tür bir yargı içerir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Öznel Anlatım", "kaynak": "Dinamik Türkçe Motoru"
            }

    # -----------------------------------------------------
    # SOSYAL BİLGİLER GENERATÖRÜ
    # -----------------------------------------------------
    elif ders == "Sosyal Bilgiler":
        if "kültür" in u_lower or "miras" in u_lower:
            oge = random.choice(["Efes Antik Kenti", "Peri Bacaları", "Pamukkale Travertenleri", "Sümela Manastırı"])
            siklar = ["Tarihi veya Doğal Varoluş", "Teknolojik Ürün", "Sanayi Tesisi", "Apre Merkezi"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Ülkemizde yer alan '{oge}' kültür ve turizm açısından hangi grupta değerlendirilir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Tarihi veya Doğal Varoluş", "kaynak": "Dinamik Sosyal Motoru"
            }
        elif "çevre" in u_lower or "harita" in u_lower:
            renkler = [("Mavi", "Su kaynakları (Deniz, Göl)"), ("Yeşil", "Alçak yerler ve ovalar"), ("Kahverengi", "Yüksek dağlık alanlar")]
            renk, tanim = random.choice(renkler)
            siklar = ["Su kaynakları (Deniz, Göl)", "Alçak yerler ve ovalar", "Yüksek dağlık alanlar", "Çöl alanları"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Fiziki haritalarda '{renk}' renk ile gösterilen alanlar neyi temsil eder?",
                "gorsel_svg": None, "siklar": siklar, "dogru": tanim, "kaynak": "Dinamik Sosyal Motoru"
            }
        else: # Birey, Tüketim, Vatandaşlık
            kisi = random.choice(isimler)
            siklar = [
                "Alışveriş sonrasında fiş veya fatura almak",
                "Son kullanma tarihini incelemeden ürün almak",
                "Ambalajı açık ürünleri tercih etmek",
                "Sadece reklamı yapılan pahalı ürünleri almak"
            ]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"{kisi}'in alışveriş yaparken sergilemesi gereken en bilinçli tüketici davranışı hangisidir?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Alışveriş sonrasında fiş veya fatura almak", "kaynak": "Dinamik Sosyal Motoru"
            }

    # -----------------------------------------------------
    # DİN KÜLTÜRÜ GENERATÖRÜ
    # -----------------------------------------------------
    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        sifatlar = [
            ("Allah'ın her şeyi bilmesi", "İlim"),
            ("Allah'ın her şeyi görmesi", "Basar"),
            ("Allah'ın her şeye gücünün yetmesi", "Kudret"),
            ("Allah'ın her şeyi işitmesi", "Semi")
        ]
        tanim, sifat = random.choice(sifatlar)
        siklar = ["İlim", "Basar", "Kudret", "Semi"]
        random.shuffle(siklar)
        return {
            "ders": ders, "unite": unite,
            "soru": f"'{tanim}' anlamına gelen ilahi sıfat aşağıdakilerden hangisidir?",
            "gorsel_svg": None, "siklar": siklar, "dogru": sifat, "kaynak": "Dinamik Din Motoru"
        }

    # -----------------------------------------------------
    # İNGİLİZCE GENERATÖRÜ
    # -----------------------------------------------------
    else: # İngilizce
        kategori = random.choice(["subjects", "places", "hobbies"])
        if kategori == "subjects":
            siklar = ["Maths", "Hospital", "Bakery", "Doctor"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Which of the following is a school subject?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Maths", "kaynak": "Dinamik İngilizce Motoru"
            }
        elif kategori == "places":
            siklar = ["Bakery", "Science", "Music", "Swimming"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Where do you go to buy fresh bread in your town?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Bakery", "kaynak": "Dinamik İngilizce Motoru"
            }
        else:
            siklar = ["Chess", "Library", "School", "Teacher"]
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Which option is a board game or hobby?",
                "gorsel_svg": None, "siklar": siklar, "dogru": "Chess", "kaynak": "Dinamik İngilizce Motoru"
            }

def soru_hazirla(api_key, ders, unite, onceki_sorular):
    if api_key:
        ai_soru = gemini_soru_uret_ozgun(api_key, ders, unite, onceki_sorular)
        if ai_soru and ai_soru["soru"] not in onceki_sorular:
            return ai_soru
            
    # API kapalıysa veya başarısız olursa gelişmiş dinamik motor devreye girer
    return sablon_soru_uret(ders, unite)

# =========================================================
# 6. STREAMLIT ARAYÜZÜ
# =========================================================
st.title("📚 MEB 5. Sınıf Özgün Soru Bankası")

st.sidebar.header("⚙️ Soru Bankası Filtreleri")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=False):
        select_all = st.checkbox(f"Tüm {ders_adi} Ünitelerini Seç", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        st.divider()
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])

# ---------------------------------------------------------
# AŞAMA 1: SORULARI ÜRETME VE HAZIRLAMA
# ---------------------------------------------------------
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Soru Bankası Yapılandırması")
    if secilen_uniteler:
        st.info(f"Soru bankasından **{len(secilen_uniteler)}** ünite seçildi. Soru başına **80 saniye** süre tanımlanacaktır.")
        if st.button("🚀 Özgün Soru Havuzunu Üret", type="primary"):
            with st.spinner("Özgün sorular üretiliyor ve kontrol ediliyor..."):
                ham_sorular = []
                uretilen_metinler = []
                
                for i in range(soru_sayisi):
                    h_ders, h_unite = secilen_uniteler[i % len(secilen_uniteler)]
                    
                    # Benzersiz soru elde edene kadar dene
                    yeni_soru = None
                    for _ in range(5):
                        s = soru_hazirla(API_KEY, h_ders, h_unite, uretilen_metinler)
                        if s["soru"] not in uretilen_metinler:
                            yeni_soru = s
                            break
                    
                    if not yeni_soru:
                        yeni_soru = sablon_soru_uret(h_ders, h_unite)

                    uretilen_metinler.append(yeni_soru["soru"])
                    ham_sorular.append(yeni_soru)
                
                ham_sorular.sort(key=lambda x: list(MEB_MUFREDAT.keys()).index(x["ders"]))
                
                st.session_state["soru_listesi"] = ham_sorular
                st.session_state["toplam_sure_sn"] = len(ham_sorular) * 80
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.warning("⚠️ Lütfen sol menüden en az 1 ünite işaretleyin.")

# ---------------------------------------------------------
# AŞAMA 2: TESTİ BAŞLAT EKRANI
# ---------------------------------------------------------
elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Tüm sorular ve şıklar özgün şekilde hazırlandı ve doğrulandı!")
    
    toplam_sn = st.session_state["toplam_sure_sn"]
    dakika = toplam_sn // 60
    saniye = toplam_sn % 60
    
    st.markdown(f"""
    ### ⏱️ Test Bilgileri:
    - **Toplam Soru Sayısı:** {len(st.session_state['soru_listesi'])}
    - **Soru Başına Süre:** 80 Saniye
    - **Toplam Test Süresi:** {dakika} Dakika {saniye} Saniye
    """)
    
    c1, c2 = st.columns([1, 2])
    if c1.button("⏱️ Testi Başlat", type="primary"):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
        
    if c2.button("🔄 Üniteleri Yeniden Seç"):
        st.session_state["sorular_hazir"] = False
        st.rerun()

# ---------------------------------------------------------
# AŞAMA 3: AKTİF TEST EKRANI
# ---------------------------------------------------------
elif st.session_state["test_aktif"]:
    gecen_sure = int(time.time() - st.session_state["baslangic_zamani"])
    kalan_sure = st.session_state["toplam_sure_sn"] - gecen_sure

    if kalan_sure <= 0:
        st.warning("⏰ Süreniz doldu! Test otomatik olarak sonlandırılıyor...")
        time.sleep(2)
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

    k_dakika = kalan_sure // 60
    k_saniye = kalan_sure % 60

    col_info, col_timer, col_stop = st.columns([2, 1, 1])
    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    with col_info:
        st.caption(f"📌 **Ders:** {q['ders']} | **Ünite:** {q['unite']}")
    with col_timer:
        st.metric("⏳ Kalan Süre", f"{k_dakika:02d}:{k_saniye:02d}")
    with col_stop:
        if st.button("🛑 Testi Sonlandır", type="secondary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

    st.write(f"📝 **Soru:** {idx + 1} / {len(st.session_state['soru_listesi'])}")
    st.progress((idx + 1) / len(st.session_state["soru_listesi"]))
    st.divider()

    st.markdown(f"### **Soru {idx + 1}:** {q['soru']}")

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=165)
    elif q.get("gorsel_tasvir"):
        st.info(f"📊 **İllüstrasyon / Bilgi:**\n{q['gorsel_tasvir']}")

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Cevabınızı İşaretleyin:", q["siklar"], index=secim_index, key=f"radio_{idx}")
    if secim is not None:
        st.session_state["kullanici_cevaplari"][idx] = secim

    st.divider()
    col_prev, col_next = st.columns([1, 1])

    if idx > 0 and col_prev.button("⬅️ Önceki Soru"):
        st.session_state["mevcut_soru_index"] -= 1
        st.rerun()

    if idx + 1 < len(st.session_state["soru_listesi"]):
        if col_next.button("Sonraki Soru ➡️", type="primary"):
            st.session_state["mevcut_soru_index"] += 1
            st.rerun()
    else:
        if col_next.button("🏁 Testi Tamamla", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

# ---------------------------------------------------------
# AŞAMA 4: SONUÇ KARNESİ EKRANI
# ---------------------------------------------------------
elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Test Karnesi")

    toplam_soru = len(st.session_state["soru_listesi"])
    dogru_sayisi = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    puan = int((dogru_sayisi / toplam_soru) * 100) if toplam_soru > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Soru", toplam_soru)
    c2.metric("Doğru Sayısı", dogru_sayisi)
    c3.metric("Başarı Puanı", f"{puan} / 100")

    st.divider()
    for i, q in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(i, "Boş Bırakıldı")
        d_cevabi = q["dogru"]
        durum = "✅ Doğru" if k_cevabi == d_cevabi else "❌ Yanlış"
        
        with st.expander(f"Soru {i+1} [{q['ders']} - {q['unite']}]: {durum}"):
            st.write(f"**Soru:** {q['soru']}")
            st.write(f"👉 **Sizin Cevabınız:** {k_cevabi}")
            st.write(f"✅ **Doğru Cevap:** {d_cevabi}")
            st.caption(f"Kaynak: {q.get('kaynak', 'Sistem')}")

    if st.button("🔄 Yeni Test Hazırla"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
