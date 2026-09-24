import streamlit as st
import random
import json
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="5. Sınıf Sınav Modu", page_icon="🎓", layout="wide")

# --- GELİŞMİŞ SECRETS / API KEY OKUMA MANTIGI ---
def get_api_key():
    for key in ["GEMINI_API_KEY", "API_KEY", "gemini_api_key", "api_key"]:
        try:
            val = st.secrets.get(key)
            if val and str(val).strip():
                return str(val).strip()
        except Exception:
            pass
    try:
        if "general" in st.secrets and "GEMINI_API_KEY" in st.secrets["general"]:
            return str(st.secrets["general"]["GEMINI_API_KEY"]).strip()
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
if "toplam_sure" not in st.session_state:
    st.session_state["toplam_sure"] = 0

# =========================================================
# GERÇEK MEB 5. SINIF EKSİKSİZ MÜFREDAT LİSTESİ
# =========================================================
MEB_MUFREDAT = {
    "Matematik": [
        "Temel Geometrik Kavramlar ve Çizimler (Doğru, Işın, Açı)",
        "Üçgen ve Dörtgenler (Açı ve Kenar Özellikleri)",
        "Alan Ölçme (Kare ve Dikdörtgen)",
        "Kesirler (Bileşik, Tam Sayılı, Sıralama)",
        "Doğal Sayılarla İşlemler (Toplama, Çıkarma, Çarpma, Bölme)"
    ],
    "Fen Bilimleri": [
        "Güneş, Dünya ve Ay (Boyut, Yapı ve Hareketler)",
        "Ay'ın Evreleri (Ana ve Ara Evreler)",
        "Elektrik Devre Elemanları (Ampul Parlaklığını Etkileyen Değişkenler)",
        "Kuvvetin Ölçülmesi ve Sürtünme (Dinamometre)"
    ],
    "Türkçe": [
        "Sözcükte Anlam (Gerçek, Mecaz, Terim, Zıt, Eş Anlam)",
        "Noktalama İşaretleri (Nokta, Virgül, İki Nokta)",
        "Paragrafta Anlam ve Görsel Okuma"
    ],
    "Sosyal Bilgiler": [
        "İnsanlar, Yerler ve Çevreler (Harita, Yer Şekilleri)",
        "Kültür ve Miras (Tarihi Mekanlar ve Semboller)"
    ],
    "İngilizce": [
        "Unit 2: My Town (Directions, Places in Town)",
        "Unit 5: Health (Illnesses, Suggestions)"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "Çevremizde Dinin İzleri (Mimaride Din)",
        "Adap ve Nezaket"
    ]
}

# =========================================================
# DİNAMİK SVG GÖRSEL ÜRETİCİLERİ
# =========================================================
def svg_aci_ciz(aci_derece):
    return f'''
    <svg width="220" height="140" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>
      <path d="M 20 110 L 180 110" stroke="#333" stroke-width="3" marker-end="url(#arrow)"/>
      <line x1="100" y1="110" x2="{100 + 70 * round(random.uniform(0.1, 0.8), 2)}" y2="{110 - 70 * round(random.uniform(0.5, 0.9), 2)}" stroke="#e63946" stroke-width="3"/>
      <circle cx="100" cy="110" r="4" fill="#1d3557"/>
      <text x="105" y="90" font-size="16" font-weight="bold" fill="#e63946">?°</text>
      <text x="95" y="130" font-size="12" fill="#666">Açı Ölçüsü</text>
    </svg>
    '''

def svg_dikdortgen_ciz(a, b):
    return f'''
    <svg width="240" height="140" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>
      <rect x="40" y="30" width="160" height="80" fill="#a8dadc" stroke="#1d3557" stroke-width="3" rx="4"/>
      <text x="110" y="22" font-size="14" font-weight="bold" fill="#1d3557">{a} cm</text>
      <text x="10" y="75" font-size="14" font-weight="bold" fill="#1d3557">{b} cm</text>
    </svg>
    '''

def svg_ay_evresi_ciz(evre_adi):
    return f'''
    <svg width="160" height="160" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#111" rx="8"/>
      <circle cx="80" cy="80" r="50" fill="#e0e0e0" stroke="#fff" stroke-width="2"/>
      <path d="M 80 30 A 50 50 0 0 0 80 130 Z" fill="#222"/>
      <text x="80" y="150" text-anchor="middle" font-size="12" fill="#fff">{evre_adi}</text>
    </svg>
    '''

# =========================================================
# GÖRSEL DESTEKLİ ŞABLON SORU ÜRETİCİ
# =========================================================
def sablon_soru_uret(ders, konu):
    if ders == "Matematik":
        if "Açı" in konu:
            aci = random.choice([30, 45, 60, 90, 120, 135, 150])
            tur = "Dar Açı" if aci < 90 else ("Dik Açı" if aci == 90 else "Geniş Açı")
            siklar = ["Dar Açı", "Dik Açı", "Geniş Açı", "Doğru Açı"]
            return {
                "soru": f"Yukarıdaki görselde gösterilen Açı çeşidi aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_aci_ciz(aci),
                "siklar": siklar,
                "dogru": tur,
                "kaynak": "Görsel Şablon Bankası"
            }
        elif "Alan" in konu:
            a, b = random.randint(6, 12), random.randint(3, 5)
            alan = a * b
            siklar = [f"{alan} cm²", f"{2*(a+b)} cm²", f"{alan + 10} cm²", f"{alan - 5} cm²"]
            random.shuffle(siklar)
            return {
                "soru": "Görselde kenar uzunlukları verilen dikdörtgenin alanı kaç cm²'dir?",
                "gorsel_svg": svg_dikdortgen_ciz(a, b),
                "siklar": siklar,
                "dogru": f"{alan} cm²",
                "kaynak": "Görsel Şablon Bankası"
            }

    elif ders == "Fen Bilimleri":
        if "Ay" in konu:
            return {
                "soru": "Görselde Ay'ın ana evrelerinden biri verilmiştir. Bu evrenin adı nedir?",
                "gorsel_svg": svg_ay_evresi_ciz("İlk Dördün"),
                "siklar": ["İlk Dördün", "Son Dördün", "Yeni Ay", "Dolunay"],
                "dogru": "İlk Dördün",
                "kaynak": "Görsel Şablon Bankası"
            }

    # Varsayılan Soru
    return {
        "soru": f"5. sınıf {ders} dersi '{konu}' konusu ile ilgili görsel değerlendirme sorusu aşağıdakilerden hangisidir?",
        "gorsel_svg": None,
        "siklar": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"],
        "dogru": "Seçenek A",
        "kaynak": "Şablon Bankası"
    }

# =========================================================
# GEMINI YAPAY ZEKÂ SORU ÜRETİCİ (GÖRSEL TASVİR DESTEKLİ)
# =========================================================
def gemini_soru_uret(api_key, ders, konu):
    if not api_key or not api_key.startswith("AIzaSy"):
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"MEB 5. sınıf {ders} dersi '{konu}' konusu ile ilgili 4 şıklı 1 adet test sorusu hazırla.\n"
            "Eğer konu uygunsa soruya görsel bir unsur ekle (örneğin bir şekil, grafik veya diyagram metin tasviri).\n"
            "Yanıtı YALNIZCA geçerli bir JSON formatında ver:\n"
            "{\n"
            '  "soru": "Soru metni",\n'
            '  "gorsel_tasvir": "Görsel açıklaması veya tasviri (varsa, yoksa null)",\n'
            '  "siklar": ["A Şıkkı", "B Şıkkı", "C Şıkkı", "D Şıkkı"],\n'
            '  "dogru": "Doğru şık metni"\n'
            "}"
        )
        
        t0 = time.time()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        if time.time() - t0 > 2.0:
            return None

        clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        veri = json.loads(clean_json)
        veri["kaynak"] = "Yapay Zekâ (Gemini)"
        return veri
    except Exception:
        return None

def soru_hazirla(api_key, ders, konu):
    if api_key and api_key.startswith("AIzaSy") and random.random() < 0.6:
        ai_soru = gemini_soru_uret(api_key, ders, konu)
        if ai_soru:
            return ai_soru
    return sablon_soru_uret(ders, konu)

# =========================================================
# ARAYÜZ (STREAMLIT UI)
# =========================================================
st.title("🎓 MEB 5. Sınıf Resimli & Görsel Destekli Sınav Platformu")

st.sidebar.header("⚙️ Sınav Ayarları")

ders = st.sidebar.selectbox("Ders Seçin", list(MEB_MUFREDAT.keys()), disabled=st.session_state["test_aktif"])
konu = st.sidebar.selectbox("Konu Seçin", MEB_MUFREDAT[ders], disabled=st.session_state["test_aktif"])

soru_sayisi = st.sidebar.number_input("Soru Sayısı Girin:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"])

st.sidebar.divider()

if API_KEY and API_KEY.startswith("AIzaSy"):
    st.sidebar.success("🔑 Gemini API + Görsel Motor Aktif")
else:
    st.sidebar.warning("⚠️ API Key Tanımsız / Görsel Şablon Modu Aktif")

# DURUM 1: TEST HENÜZ BAŞLAMADI
if not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"📋 **Sınav Bilgileri:**\n- Ders: **{ders}**\n- Konu: **{konu}**\n- Soru Sayısı: **{soru_sayisi}**\n- Toplam Süre: **{soru_sayisi * 80} saniye**\n\n*Hazırsanız aşağıdaki butona basarak sınavı başlatabilirsiniz.*")
    
    if st.button("🚀 Sınavı Başlat", type="primary"):
        with st.spinner("Resim içerikli ve müfredata uygun sorular hazırlanıyor..."):
            st.session_state["soru_listesi"] = [soru_hazirla(API_KEY, ders, konu) for _ in range(soru_sayisi)]
            st.session_state["kullanici_cevaplari"] = {}
            st.session_state["mevcut_soru_index"] = 0
            st.session_state["toplam_sure"] = soru_sayisi * 80
            st.session_state["baslangic_zamani"] = time.time()
            st.session_state["test_aktif"] = True
            st.session_state["test_bitti"] = False
            st.rerun()

# DURUM 2: TEST DEVAM EDİYOR
elif st.session_state["test_aktif"]:
    col_sure, col_durum = st.columns([2, 1])
    sure_kutusu = col_sure.empty()
    col_durum.write(f"📝 **Soru:** {st.session_state['mevcut_soru_index'] + 1} / {len(st.session_state['soru_listesi'])}")
    
    st.progress((st.session_state["mevcut_soru_index"] + 1) / len(st.session_state["soru_listesi"]))
    st.divider()

    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    st.markdown(f"### **Soru {idx + 1}:** {q['soru']}")

    # GÖRSEL RENDER MANTIGI (SVG VEYA TASVİR)
    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=160)
    elif q.get("gorsel_tasvir"):
        st.info(f"🖼️ **Soru Görseli / Tasviri:**\n{q['gorsel_tasvir']}")

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Cevabınızı seçin:", q["siklar"], index=secim_index, key=f"radio_soru_{idx}")
    
    if secim is not None:
        st.session_state["kullanici_cevaplari"][idx] = secim

    st.divider()
    col_prev, col_next = st.columns([1, 1])

    btn_prev = idx > 0 and col_prev.button("⬅️ Önceki Soru")
    
    if idx + 1 < len(st.session_state["soru_listesi"]):
        btn_next = col_next.button("Sonraki Soru ➡️", type="primary")
        btn_finish = False
    else:
        btn_next = False
        btn_finish = col_next.button("🏁 Sınavı Bitir", type="primary")

    if btn_prev:
        st.session_state["mevcut_soru_index"] -= 1
        st.rerun()
    elif btn_next:
        st.session_state["mevcut_soru_index"] += 1
        st.rerun()
    elif btn_finish:
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

    gecen_sure = int(time.time() - st.session_state["baslangic_zamani"])
    kalan_sure = st.session_state["toplam_sure"] - gecen_sure

    if kalan_sure <= 0:
        st.warning("⏰ Süreniz doldu! Sınavınız tamamlanıyor...")
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        time.sleep(1)
        st.rerun()

    dakika = kalan_sure // 60
    saniye = kalan_sure % 60
    sure_kutusu.metric("⌛ Kalan Süre (Anlık)", f"{dakika:02d}:{saniye:02d}")
    
    time.sleep(1)
    st.rerun()

# DURUM 3: TEST BİTTİ
elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuç Karnesi")

    toplam_soru = len(st.session_state["soru_listesi"])
    dogru_sayisi = 0
    yanlis_sayisi = 0

    for i, q in enumerate(st.session_state["soru_listesi"]):
        kullanici_cevabi = st.session_state["kullanici_cevaplari"].get(i, None)
        if kullanici_cevabi == q["dogru"]:
            dogru_sayisi += 1
        else:
            yanlis_sayisi += 1

    puan = int((dogru_sayisi / toplam_soru) * 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Soru", toplam_soru)
    c2.metric("Doğru", dogru_sayisi)
    c3.metric("Yanlış", yanlis_sayisi)
    c4.metric("Başarı Puanı", f"{puan} / 100")

    st.divider()
    st.subheader("🔍 Detaylı Cevap Anahtarı ve İnceleme")

    for i, q in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(i, "Boş Bırakıldı")
        d_cevabi = q["dogru"]
        
        with st.expander(f"Soru {i+1}: {'✅ Doğru' if k_cevabi == d_cevabi else '❌ Yanlış'}"):
            st.write(f"**Soru:** {q['soru']}")
            if q.get("gorsel_svg"):
                st.components.v1.html(q["gorsel_svg"], height=160)
            elif q.get("gorsel_tasvir"):
                st.info(f"🖼️ Görsel Tasvir: {q['gorsel_tasvir']}")
            st.write(f"👉 **Sizin Cevabınız:** {k_cevabi}")
            st.write(f"✅ **Doğru Cevap:** {d_cevabi}")
            st.caption(f"Kaynak: {q['kaynak']}")

    st.divider()
    if st.button("🔄 Yeni Sınava Başla", type="primary"):
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
