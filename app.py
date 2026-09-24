import streamlit as st
import random
import json
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="5. Sınıf Akıllı Test Platformu", page_icon="🎓", layout="wide")

# Streamlit Secrets'tan API Anahtarını Güvenli Şekilde Alma
# Streamlit Secrets okuma yöntemleri
API_KEY = None

try:
    # 1. Doğrudan sözlük yöntemiyle dene
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "API_KEY" in st.secrets:
        API_KEY = st.secrets["API_KEY"]
    else:
        # 2. get yöntemiyle dene
        API_KEY = st.secrets.get("GEMINI_API_KEY", st.secrets.get("API_KEY", None))
except Exception as e:
    API_KEY = None
# Session State Başlatma
if "test_aktif" not in st.session_state:
    st.session_state["test_aktif"] = False
if "soru_listesi" not in st.session_state:
    st.session_state["soru_listesi"] = []
if "mevcut_soru_index" not in st.session_state:
    st.session_state["mevcut_soru_index"] = 0
if "baslangic_zamani" not in st.session_state:
    st.session_state["baslangic_zamani"] = 0
if "toplam_sure" not in st.session_state:
    st.session_state["toplam_sure"] = 0
if "dogru" not in st.session_state:
    st.session_state["dogru"] = 0
if "yanlis" not in st.session_state:
    st.session_state["yanlis"] = 0
if "cevaplandi" not in st.session_state:
    st.session_state["cevaplandi"] = False

# 1. Şablon Tabanlı Soru Üretici
def sablon_soru_uret(ders, konu):
    if ders == "Matematik":
        if konu == "Doğal Sayılarla Çarpma":
            s1 = random.randint(100, 999)
            s2 = random.randint(10, 99)
            d_cevap = s1 * s2
            siklar = [d_cevap, d_cevap + 10, max(0, d_cevap - 15), d_cevap + 100]
            random.shuffle(siklar)
            return {
                "soru": f"{s1} × {s2} işleminin sonucu kaçtır?",
                "siklar": [str(x) for x in siklar],
                "dogru": str(d_cevap),
                "kaynak": "Şablon Bankası"
            }
        elif konu == "Kesirlerde Toplama":
            pay1, pay2 = random.randint(1, 4), random.randint(1, 4)
            payda = random.randint(5, 12)
            d_cevap = f"{pay1 + pay2}/{payda}"
            siklar = [d_cevap, f"{pay1 + pay2}/{payda + 2}", f"{pay1}/{payda}", f"{pay2 + 1}/{payda}"]
            random.shuffle(siklar)
            return {
                "soru": f"({pay1}/{payda}) + ({pay2}/{payda}) işleminin sonucu kaçtır?",
                "siklar": siklar,
                "dogru": d_cevap,
                "kaynak": "Şablon Bankası"
            }

    elif ders == "Fen Bilimleri":
        if konu == "Güneş, Dünya ve Ay":
            sorular = [
                {"soru": "Güneş'e en yakın gezegen hangisidir?", "siklar": ["Merkür", "Venüs", "Dünya", "Mars"], "dogru": "Merkür"},
                {"soru": "Ay'ın evrelerinden hangisi Dünya'dan bakıldığında tamamen karanlık görünür?", "siklar": ["Yeni Ay", "Dolunay", "İlk Dördün", "Son Dördün"], "dogru": "Yeni Ay"},
                {"soru": "Dünya'nın kendi etrafında dönmesi sonucu ne oluşur?", "siklar": ["Gece ve Gündüz", "Mevsimler", "Yıllar", "Ay Evreleri"], "dogru": "Gece ve Gündüz"}
            ]
            secilen = random.choice(sorular)
            secilen["kaynak"] = "Şablon Bankası"
            return secilen

    elif ders == "Türkçe":
        if konu == "Sözcükte Anlam":
            sorular = [
                {"soru": "'Açık' sözcüğü hangisinde gerçek anlamıyla kullanılmıştır?", "siklar": ["Kapı açık kalmış.", "Açık fikirli biridir.", "Açık sözlü insanları severim.", "Açık bir anlatımı var."], "dogru": "Kapı açık kalmış."},
                {"soru": "Hangisi zıt (karşıt) anlamlı kelime çiftidir?", "siklar": ["Siyah - Beyaz", "Okul - Mektep", "Cevap - Yanıt", "Al - Kırmızı"], "dogru": "Siyah - Beyaz"}
            ]
            secilen = random.choice(sorular)
            secilen["kaynak"] = "Şablon Bankası"
            return secilen

# 2. Yapay Zekâ (Gemini) Soru Üretici
def gemini_soru_uret(api_key, ders, konu):
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        5. sınıf {ders} dersi {konu} konusu ile ilgili zorluğu uygun test sorusu hazırla.
        Yanıtı TAM OLARAK şu JSON formatında ver, başka hiçbir metin veya açıklama ekleme:
        {{
            "soru": "Soru metni",
            "siklar": ["Şık1", "Şık2", "Şık3", "Şık4"],
            "dogru": "Şık1"
        }}
        """
        response = model.generate_content(prompt)
        clean_json = response.text.strip().replace("```json", "").replace("```", "")
        veri = json.loads(clean_json)
        veri["kaynak"] = "Yapay Zekâ (Gemini)"
        return veri
    except Exception:
        return None

# Hibrit Soru Hazırlayıcı
def soru_hazirla(api_key, ders, konu):
    if random.choice([True, False]) and api_key:
        ai_soru = gemini_soru_uret(api_key, ders, konu)
        if ai_soru:
            return ai_soru
    return sablon_soru_uret(ders, konu)


# --- ARAYÜZ (UI) ---
st.title("🎓 5. Sınıf Zaman Ayarlı Test Platformu")

# Yan Menü (Ayarlar)
st.sidebar.header("⚙️ Test Ayarları")

ders = st.sidebar.selectbox("Ders Seçin", ["Matematik", "Fen Bilimleri", "Türkçe"], disabled=st.session_state["test_aktif"])

konu_liste = {
    "Matematik": ["Doğal Sayılarla Çarpma", "Kesirlerde Toplama"],
    "Fen Bilimleri": ["Güneş, Dünya ve Ay"],
    "Türkçe": ["Sözcükte Anlam"]
}
konu = st.sidebar.selectbox("Konu Seçin", konu_liste[ders], disabled=st.session_state["test_aktif"])

soru_sayisi = st.sidebar.number_input("Soru Sayısı Girin:", min_value=1, max_value=20, value=5, step=1, disabled=st.session_state["test_aktif"])

if API_KEY:
    st.sidebar.success("🔑 Gemini API Aktif")
else:
    st.sidebar.warning("⚠️ API Key Tanımsız (Şablon Modu)")


# TESTİ BAŞLATMA
if not st.session_state["test_aktif"]:
    st.info(f"Seçilen: **{ders} | {konu}** — Toplam **{soru_sayisi}** soru hazırlanacak. Her soru için 80 saniye (Toplam: **{soru_sayisi * 80}** saniye) süreniz olacak.")
    
    if st.button("🚀 Testi Başlat", type="primary"):
        with st.spinner("Sorular hazırlanıyor..."):
            st.session_state["soru_listesi"] = [soru_hazirla(API_KEY, ders, konu) for _ in range(soru_sayisi)]
            st.session_state["mevcut_soru_index"] = 0
            st.session_state["dogru"] = 0
            st.session_state["yanlis"] = 0
            st.session_state["cevaplandi"] = False
            st.session_state["toplam_sure"] = soru_sayisi * 80
            st.session_state["baslangic_zamani"] = time.time()
            st.session_state["test_aktif"] = True
            st.rerun()

# TEST EKRANI
else:
    # Süre Hesaplama
    gecen_sure = int(time.time() - st.session_state["baslangic_zamani"])
    kalan_sure = st.session_state["toplam_sure"] - gecen_sure

    # Süre Bitti Kontrolü
    if kalan_sure <= 0:
        st.error("⏰ Süreniz doldu! Test sonlandırılıyor...")
        st.session_state["test_aktif"] = False
        st.rerun()

    # Sayaç ve İlerleme Çubuğu
    dakika = kalan_sure // 60
    saniye = kalan_sure % 60
    
    col_sure, col_skor = st.columns([2, 1])
    col_sure.metric("⌛ Kalan Süre", f"{dakika:02d}:{saniye:02d}")
    col_skor.write(f"📊 **Soru:** {st.session_state['mevcut_soru_index'] + 1} / {len(st.session_state['soru_listesi'])}")
    col_skor.write(f"✅ Doğru: {st.session_state['dogru']} | ❌ Yanlış: {st.session_state['yanlis']}")
    
    st.progress((st.session_state["mevcut_soru_index"] + 1) / len(st.session_state["soru_listesi"]))
    st.divider()

    # Mevcut Soru
    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    st.caption(f"🤖 Soru Kaynağı: **{q['kaynak']}**")
    st.markdown(f"### **Soru {idx + 1}:** {q['soru']}")

    secim = st.radio("Cevabınızı seçin:", q["siklar"], key=f"soru_{idx}")

    if st.button("Cevabı Onayla") and not st.session_state["cevaplandi"]:
        st.session_state["cevaplandi"] = True
        if secim == q["dogru"]:
            st.success("🎉 Doğru Cevap!")
            st.session_state["dogru"] += 1
        else:
            st.error(f"❌ Yanlış Cevap. Doğru Yanıt: **{q['dogru']}**")
            st.session_state["yanlis"] += 1

    # Sonraki Soruya Geçiş
    if st.session_state["cevaplandi"]:
        if idx + 1 < len(st.session_state["soru_listesi"]):
            if st.button("Sonraki Soru ➡️"):
                st.session_state["mevcut_soru_index"] += 1
                st.session_state["cevaplandi"] = False
                st.rerun()
        else:
            if st.button("🏁 Testi Bitir"):
                st.session_state["test_aktif"] = False
                st.rerun()

    # Test Bitiş Özeti
    if not st.session_state["test_aktif"] and st.session_state["mevcut_soru_index"] > 0:
        st.balloons()
        st.success("🎉 Test Tamamlandı!")
        toplam = len(st.session_state["soru_listesi"])
        d = st.session_state["dogru"]
        y = st.session_state["yanlis"]
        st.write(f"**Sonuç:** {toplam} Soruda {d} Doğru, {y} Yanlış. Puan: **{int((d/toplam)*100)}**")
