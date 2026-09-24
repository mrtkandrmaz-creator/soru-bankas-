import streamlit as st
import random
import json
import time
import math

# Sayfa Yapılandırması
st.set_page_config(page_title="MEB 5. Sınıf Sınav Platformu", page_icon="🎓", layout="wide")

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

# =========================================================
# MEB 5. SINIF EKSİKSİZ TÜM DERSLER VE ÜNİTELER
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
# 2. MODERN SVG GÖRSEL MOTORU (UI/UX UYUMLU)
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
      <text x="140" y="27" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto" font-size="12" font-weight="700" fill="#334155" text-anchor="middle">Açı: ?°</text>
    </svg>
    '''

def svg_dikdortgen_ciz_modern(a, b):
    color_pair = random.choice([
        ("#eff6ff", "#2563eb"),
        ("#ecfdf5", "#059669"),
        ("#fef3c7", "#d97706"),
        ("#f3e8ff", "#7c3aed")
    ])
    bg_fill, stroke_color = color_pair
    return f'''
    <svg width="280" height="150" viewBox="0 0 280 150" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="shadow2" x="-5%" y="-5%" width="110%" height="110%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.06"/>
        </filter>
      </defs>
      <rect width="100%" height="100%" fill="#ffffff" rx="16" filter="url(#shadow2)"/>
      <rect x="55" y="30" width="170" height="85" fill="{bg_fill}" stroke="{stroke_color}" stroke-width="3" rx="12"/>
      <rect x="110" y="8" width="60" height="20" rx="6" fill="#f1f5f9"/>
      <text x="140" y="22" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#334155" text-anchor="middle">{a} cm</text>
      <rect x="5" y="62" width="45" height="20" rx="6" fill="#f1f5f9"/>
      <text x="27" y="76" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#334155" text-anchor="middle">{b} cm</text>
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

# =========================================================
# 3. DİNAMİK ŞABLON SAKLAMA / ÜRETME MOTORU
# =========================================================
def sablon_soru_uret(ders, konu):
    if ders == "Matematik":
        if "Açı" in konu or "Geometrik" in konu:
            aci = random.choice([30, 45, 60, 90, 120, 135, 150])
            tur = "Dar Açı" if aci < 90 else ("Dik Açı" if aci == 90 else "Geniş Açı")
            siklar = ["Dar Açı", "Dik Açı", "Geniş Açı", "Doğru Açı"]
            random.shuffle(siklar)
            return {
                "soru": f"Yukarıdaki modern iletki görselinde gösterilen {aci}°'lik açı türü aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_iletki_aci_ciz_modern(aci),
                "siklar": siklar,
                "dogru": tur,
                "kaynak": "Dinamik Görsel Motoru"
            }
        elif "Alan" in konu or "Dikdörtgen" in konu:
            a, b = random.randint(5, 15), random.randint(3, 10)
            alan = a * b
            siklar = [f"{alan} cm²", f"{2*(a+b)} cm²", f"{alan + 6} cm²", f"{max(1, alan - 5)} cm²"]
            siklar = list(set(siklar))
            while len(siklar) < 4:
                siklar.append(f"{alan + random.randint(10, 20)} cm²")
            random.shuffle(siklar)
            return {
                "soru": "Visual kartsı verilen dikdörtgensel bölgenin alanı kaç cm²'dir?",
                "gorsel_svg": svg_dikdortgen_ciz_modern(a, b),
                "siklar": siklar,
                "dogru": f"{alan} cm²",
                "kaynak": "Dinamik Görsel Motoru"
            }
        elif "Kesirler" in konu:
            payda = random.choice([4, 5, 6, 8])
            pay = random.randint(1, payda - 1)
            siklar = [f"{pay}/{payda}", f"{payda-pay}/{payda}", f"{pay}/{payda+1}", f"{pay+1}/{payda}"]
            siklar = list(set(siklar))
            while len(siklar) < 4:
                siklar.append(f"{random.randint(1,3)}/{payda}")
            random.shuffle(siklar)
            return {
                "soru": "Modellemede boyalı bölgeyi ifade eden kesir aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_kesir_ciz_modern(pay, payda),
                "siklar": siklar,
                "dogru": f"{pay}/{payda}",
                "kaynak": "Dinamik Görsel Motoru"
            }

    elif ders == "Fen Bilimleri" and ("Güneş" in konu or "Ay" in konu):
        evreler = ["Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"]
        secilen_evre = random.choice(evreler)
        siklar = evreler.copy()
        random.shuffle(siklar)
        return {
            "soru": "Görselde karanlık uzay zemininde modellenen Ay'ın ana evresi aşağıdakilerden hangisidir?",
            "gorsel_svg": svg_ay_evresi_ciz_modern(secilen_evre),
            "siklar": siklar,
            "dogru": secilen_evre,
            "kaynak": "Dinamik Görsel Motoru"
        }

    return {
        "soru": f"5. Sınıf {ders} dersi '{konu}' başlığıyla ilgili temel bilgi değerlendirme sorusu aşağıdakilerden hangisidir?",
        "gorsel_svg": None,
        "siklar": ["A Seçeneği", "B Seçeneği", "C Seçeneği", "D Seçeneği"],
        "dogru": "A Seçeneği",
        "kaynak": "Müfredat Bankası"
    }

# =========================================================
# 4. GEMINI AI MOTORU (YENİ SDK VE HIZLI MODEL)
# =========================================================
def gemini_soru_uret(api_key, ders, konu):
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"MEB 5. sınıf {ders} dersi '{konu}' konusuyla ilgili tam olarak 4 şıklı 1 adet benzersiz ve müfredata uygun test sorusu üret.\n"
            "Yanıtını YALNIZCA geçerli bir JSON formatında ver:\n"
            "{\n"
            '  "soru": "Soru metni",\n'
            '  "gorsel_tasvir": "Varsa soru için bir metin/tablo/grafik tasviri, yoksa null",\n'
            '  "siklar": ["A Şıkkı", "B Şıkkı", "C Şıkkı", "D Şıkkı"],\n'
            '  "dogru": "Doğru şık metni"\n'
            "}"
        )
        
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        veri = json.loads(clean_json)
        veri["kaynak"] = "Yapay Zekâ (Gemini 2.5)"
        return veri
    except Exception:
        return None

def soru_hazirla(api_key, ders, konu):
    if api_key and random.random() < 0.75:
        ai_soru = gemini_soru_uret(api_key, ders, konu)
        if ai_soru:
            return ai_soru
    return sablon_soru_uret(ders, konu)

# =========================================================
# 5. STREAMLIT ARAYÜZ (UI)
# =========================================================
st.title("🎓 MEB 5. Sınıf Dijital Sınav Platformu")

st.sidebar.header("⚙️ Müfredat ve Sınav Ayarları")

ders = st.sidebar.selectbox("Ders Seçin", list(MEB_MUFREDAT.keys()), disabled=st.session_state["test_aktif"])
konu = st.sidebar.selectbox("Ünite / Konu Seçin", MEB_MUFREDAT[ders], disabled=st.session_state["test_aktif"])
soru_sayisi = st.sidebar.number_input("Soru Sayısı:", min_value=1, max_value=30, value=5, step=1, disabled=st.session_state["test_aktif"])

st.sidebar.divider()

if API_KEY:
    st.sidebar.success("🔑 Gemini 2.5 API Aktif (Hibrit Mod)")
else:
    st.sidebar.info("💡 Şablon Modu Aktif (Secret Eklendiğinde AI Devreye Girer)")

# BAŞLANGIÇ EKRANI
if not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"📋 **Seçilen Sınav Detayları:**\n- **Ders:** {ders}\n- **Konu/Ünite:** {konu}\n- **Soru Sayısı:** {soru_sayisi}")
    
    if st.button("🚀 Sınavı Başlat", type="primary"):
        with st.spinner("MEB müfredatına uygun dinamik sorular ve görseller hazırlanıyor..."):
            st.session_state["soru_listesi"] = [soru_hazirla(API_KEY, ders, konu) for _ in range(soru_sayisi)]
            st.session_state["kullanici_cevaplari"] = {}
            st.session_state["mevcut_soru_index"] = 0
            st.session_state["test_aktif"] = True
            st.session_state["test_bitti"] = False
            st.rerun()

# TEST EKRANI
elif st.session_state["test_aktif"]:
    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    st.write(f"📝 **Soru:** {idx + 1} / {len(st.session_state['soru_listesi'])}")
    st.progress((idx + 1) / len(st.session_state["soru_listesi"]))
    st.divider()

    st.markdown(f"### **Soru {idx + 1}:** {q['soru']}")

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=165)
    elif q.get("gorsel_tasvir"):
        st.info(f"📊 **Tablo / Görsel Bilgisi:**\n{q['gorsel_tasvir']}")

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
        if col_next.button("🏁 Sınavı Tamamla", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

# SONUÇ EKRANI
elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuç Karnesi")

    toplam_soru = len(st.session_state["soru_listesi"])
    dogru_sayisi = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    puan = int((dogru_sayisi / toplam_soru) * 100)

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Soru", toplam_soru)
    c2.metric("Doğru Sayısı", dogru_sayisi)
    c3.metric("Başarı Puanı", f"{puan} / 100")

    st.divider()
    for i, q in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(i, "Boş Bırakıldı")
        d_cevabi = q["dogru"]
        durum = "✅ Doğru" if k_cevabi == d_cevabi else "❌ Yanlış"
        
        with st.expander(f"Soru {i+1}: {durum}"):
            st.write(f"**Soru:** {q['soru']}")
            st.write(f"👉 **Sizin Cevabınız:** {k_cevabi}")
            st.write(f"✅ **Doğru Cevap:** {d_cevabi}")

    if st.button("🔄 Yeni Sınav Oluştur"):
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
