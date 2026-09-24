import streamlit as st
import random
import json
import time
import math

# Sayfa Yapılandırması
st.set_page_config(page_title="5. Sınıf Sınav Platformu", page_icon="🎓", layout="wide")

# =========================================================
# 1. KALICI API KEY OKUMA MOTORU
# =========================================================
def get_api_key():
    # 1. Doğrudan st.secrets kontrolü
    keys_to_check = ["GEMINI_API_KEY", "API_KEY", "gemini_api_key", "api_key"]
    for k in keys_to_check:
        try:
            if k in st.secrets and str(st.secrets[k]).strip():
                return str(st.secrets[k]).strip()
        except Exception:
            pass
            
    # 2. Alt başlıklar altında kontrol (örn: [general] veya [default])
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
if "baslangic_zamani" not in st.session_state:
    st.session_state["baslangic_zamani"] = 0

# =========================================================
# MEB 5. SINIF EKSİKSİZ MÜFREDAT
# =========================================================
MEB_MUFREDAT = {
    "Matematik": [
        "Temel Geometrik Kavramlar ve Çizimler (Doğru, Işın, Açı)",
        "Üçgen ve Dörtgenler (Açı ve Kenar Özellikleri)",
        "Alan Ölçme (Kare ve Dikdörtgen)",
        "Kesirler (Bileşik, Tam Sayılı, Sıralama)"
    ],
    "Fen Bilimleri": [
        "Güneş, Dünya ve Ay (Boyut, Yapı ve Hareketler)",
        "Ay'ın Evreleri (Ana ve Ara Evreler)",
        "Elektrik Devre Elemanları (Ampul Parlaklığını Etkileyen Değişkenler)"
    ],
    "Türkçe": [
        "Sözcükte Anlam (Gerçek, Mecaz, Terim)",
        "Noktalama İşaretleri ve Görsel Okuma"
    ],
    "Sosyal Bilgiler": [
        "İnsanlar, Yerler ve Çevreler (Harita, Yer Şekilleri)",
        "Kültür ve Miras"
    ]
}

# =========================================================
# 2. DİNAMİK VE PARAMETRİK SVG GÖRSEL MOTORU
# =========================================================
def svg_iletki_aci_ciz(derece):
    rad = math.radians(180 - derece)
    x = int(120 + 80 * math.cos(rad))
    y = int(110 - 80 * math.sin(rad))
    renk = random.choice(["#e63946", "#2a9d8f", "#f4a261", "#457b9d", "#7209b7"])
    
    return f'''
    <svg width="260" height="140" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8f9fa" rx="10"/>
      <path d="M 30 110 A 90 90 0 0 1 210 110 Z" fill="#e9ecef" stroke="#6c757d" stroke-width="2"/>
      <line x1="30" y1="110" x2="210" y2="110" stroke="#333" stroke-width="3"/>
      <line x1="120" y1="110" x2="{x}" y2="{y}" stroke="{renk}" stroke-width="4"/>
      <circle cx="120" cy="110" r="5" fill="#333"/>
      <text x="110" y="135" font-size="13" font-weight="bold" fill="#333">Açı: ?°</text>
    </svg>
    '''

def svg_dikdortgen_ciz(a, b):
    bg_renk = random.choice(["#a8dadc", "#cdb4db", "#ffc8dd", "#bde0fe", "#d8f3dc"])
    return f'''
    <svg width="260" height="140" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="10"/>
      <rect x="45" y="25" width="170" height="85" fill="{bg_renk}" stroke="#1d3557" stroke-width="3" rx="6"/>
      <text x="130" y="18" text-anchor="middle" font-size="14" font-weight="bold" fill="#1d3557">{a} cm</text>
      <text x="20" y="72" font-size="14" font-weight="bold" fill="#1d3557">{b} cm</text>
    </svg>
    '''

def svg_ay_evresi_ciz(evre_adi):
    maskeler = {
        "Yeni Ay": '<circle cx="80" cy="70" r="45" fill="#151515"/>',
        "İlk Dördün": '<circle cx="80" cy="70" r="45" fill="#e0e0e0"/><path d="M 80 25 A 45 45 0 0 0 80 115 Z" fill="#151515"/>',
        "Dolunay": '<circle cx="80" cy="70" r="45" fill="#fefae0" stroke="#ffb703" stroke-width="2"/>',
        "Son Dördün": '<circle cx="80" cy="70" r="45" fill="#151515"/><path d="M 80 25 A 45 45 0 0 0 80 115 Z" fill="#e0e0e0"/>'
    }
    cizim = maskeler.get(evre_adi, maskeler["Dolunay"])
    return f'''
    <svg width="180" height="140" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#0b0f19" rx="10"/>
      {cizim}
      <text x="90" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#ffffff">{evre_adi}</text>
    </svg>
    '''

def sablon_soru_uret(ders, konu):
    if ders == "Matematik":
        if "Açı" in konu:
            aci = random.choice([30, 45, 60, 90, 120, 135, 150])
            tur = "Dar Açı" if aci < 90 else ("Dik Açı" if aci == 90 else "Geniş Açı")
            siklar = ["Dar Açı", "Dik Açı", "Geniş Açı", "Doğru Açı"]
            random.shuffle(siklar)
            return {
                "soru": f"Yukarıdaki iletki görselinde gösterilen {aci}°'lik açı çeşidi aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_iletki_aci_ciz(aci),
                "siklar": siklar,
                "dogru": tur,
                "kaynak": "Dinamik Şablon Motoru"
            }
        elif "Alan" in konu:
            a, b = random.randint(5, 18), random.randint(3, 10)
            alan = a * b
            siklar = [f"{alan} cm²", f"{2*(a+b)} cm²", f"{alan + random.randint(4,12)} cm²", f"{max(1, alan - 8)} cm²"]
            siklar = list(set(siklar))
            while len(siklar) < 4:
                siklar.append(f"{alan + random.randint(15, 30)} cm²")
            random.shuffle(siklar)
            return {
                "soru": "Görselde kenar uzunlukları verilen dikdörtgenin alanı kaç cm²'dir?",
                "gorsel_svg": svg_dikdortgen_ciz(a, b),
                "siklar": siklar,
                "dogru": f"{alan} cm²",
                "kaynak": "Dinamik Şablon Motoru"
            }

    elif ders == "Fen Bilimleri" and "Ay" in konu:
        evreler = ["Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"]
        secilen_evre = random.choice(evreler)
        siklar = evreler.copy()
        random.shuffle(siklar)
        return {
            "soru": "Görselde Ay'ın ana evrelerinden biri verilmiştir. Bu evrenin adı nedir?",
            "gorsel_svg": svg_ay_evresi_ciz(secilen_evre),
            "siklar": siklar,
            "dogru": secilen_evre,
            "kaynak": "Dinamik Şablon Motoru"
        }

    return {
        "soru": f"5. sınıf {ders} dersi '{konu}' konusu ile ilgili değerlendirme sorusu aşağıdakilerden hangisidir?",
        "gorsel_svg": None,
        "siklar": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"],
        "dogru": "Seçenek A",
        "kaynak": "Şablon Bankası"
    }

# =========================================================
# 3. GEMINI YAPAY ZEKÂ SORU ÜRETİCİ (YENİ SDK VE HIZLI MOTOR)
# =========================================================
def gemini_soru_uret(api_key, ders, konu):
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"MEB 5. sınıf {ders} dersi '{konu}' konusuyla ilgili 4 şıklı 1 adet benzersiz test sorusu üret.\n"
            "Varsa soruya uygun bir tablo veya görsel tasviri metin olarak ekle.\n"
            "YALNIZCA geçerli bir JSON verisi döndür:\n"
            "{\n"
            '  "soru": "Soru metni",\n'
            '  "gorsel_tasvir": "Varsa tablo/görsel tasviri yoksa null",\n'
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
        veri["kaynak"] = "Yapay Zekâ (Gemini)"
        return veri
    except Exception:
        return None

def soru_hazirla(api_key, ders, konu):
    if api_key and random.random() < 0.7:
        ai_soru = gemini_soru_uret(api_key, ders, konu)
        if ai_soru:
            return ai_soru
    return sablon_soru_uret(ders, konu)

# =========================================================
# 4. ARAYÜZ (STREAMLIT UI)
# =========================================================
st.title("🎓 MEB 5. Sınıf Sınav Platformu")

st.sidebar.header("⚙️ Sınav Ayarları")

ders = st.sidebar.selectbox("Ders Seçin", list(MEB_MUFREDAT.keys()), disabled=st.session_state["test_aktif"])
konu = st.sidebar.selectbox("Konu Seçin", MEB_MUFREDAT[ders], disabled=st.session_state["test_aktif"])
soru_sayisi = st.sidebar.number_input("Soru Sayısı:", min_value=1, max_value=30, value=5, step=1, disabled=st.session_state["test_aktif"])

st.sidebar.divider()

if API_KEY:
    st.sidebar.success("🔑 Gemini API Aktif (Hibrit Mod)")
else:
    st.sidebar.warning("⚠️ API Key Bulunamadı (Şablon Modu Aktif)")

# BAŞLANGIÇ EKRANI
if not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"📋 **Sınav Bilgileri:**\n- Ders: **{ders}**\n- Konu: **{konu}**\n- Soru Sayısı: **{soru_sayisi}**")
    
    if st.button("🚀 Sınavı Başlat", type="primary"):
        with st.spinner("Sorular hazırlanıyor..."):
            st.session_state["soru_listesi"] = [soru_hazirla(API_KEY, ders, konu) for _ in range(soru_sayisi)]
            st.session_state["kullanici_cevaplari"] = {}
            st.session_state["mevcut_soru_index"] = 0
            st.session_state["baslangic_zamani"] = time.time()
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
        st.components.v1.html(q["gorsel_svg"], height=150)
    elif q.get("gorsel_tasvir"):
        st.info(f"🖼️ **Görsel/Tablo:**\n{q['gorsel_tasvir']}")

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Cevabınız:", q["siklar"], index=secim_index, key=f"radio_{idx}")
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
        if col_next.button("🏁 Sınavı Bitir", type="primary"):
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
    c2.metric("Doğru", dogru_sayisi)
    c3.metric("Başarı Puanı", f"{puan} / 100")

    st.divider()
    for i, q in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(i, "Boş")
        d_cevabi = q["dogru"]
        with st.expander(f"Soru {i+1}: {'✅ Doğru' if k_cevabi == d_cevabi else '❌ Yanlış'}"):
            st.write(f"**Soru:** {q['soru']}")
            st.write(f"👉 **Cevabınız:** {k_cevabi}")
            st.write(f"✅ **Doğru Cevap:** {d_cevabi}")

    if st.button("🔄 Yeni Sınav"):
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
