import streamlit as st
import random

# Page setup
st.set_page_config(page_title="5. Sınıf Soru Bankası & AI", page_icon="🎓", layout="wide")

# Session state initialization
if "skor" not in st.session_state:
    st.session_state["skor"] = 0
if "dogru" not in st.session_state:
    st.session_state["dogru"] = 0
if "yanlis" not in st.session_state:
    st.session_state["yanlis"] = 0
if "mevcut_soru" not in st.session_state:
    st.session_state["mevcut_soru"] = None
if "cevaplandi" not in st.session_state:
    st.session_state["cevaplandi"] = False

# Scoreboard component
def skor_tahtasi():
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Puan", st.session_state["skor"])
    col2.metric("Doğru", st.session_state["dogru"])
    col3.metric("Yanlış", st.session_state["yanlis"])

# Standard Question Generator
def SablonSoruUret(ders, konu):
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
                "dogru": str(d_cevap)
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
                "dogru": d_cevap
            }

    elif ders == "Fen Bilimleri":
        if konu == "Güneş, Dünya ve Ay":
            sorular = [
                {"soru": "Güneş'e en yakın gezegen hangisidir?", "siklar": ["Merkür", "Venüs", "Dünya", "Mars"], "dogru": "Merkür"},
                {"soru": "Ay'ın evrelerinden hangisi Dünya'dan bakıldığında tamamen karanlık görünür?", "siklar": ["Yeni Ay", "Dolunay", "İlk Dördün", "Son Dördün"], "dogru": "Yeni Ay"},
                {"soru": "Dünya'nın kendi etrafında dönmesi sonucu ne oluşur?", "siklar": ["Gece ve Gündüz", "Mevsimler", "Yıllar", "Ay Evreleri"], "dogru": "Gece ve Gündüz"}
            ]
            return random.choice(sorular)

    elif ders == "Türkçe":
        if konu == "Sözcükte Anlam":
            sorular = [
                {"soru": "'Açık' sözcüğü hangisinde gerçek anlamıyla kullanılmıştır?", "siklar": ["Kapı açık kalmış.", "Açık fikirli biridir.", "Açık sözlü insanları severim.", "Açık bir anlatımı var."], "dogru": "Kapı açık kalmış."},
                {"soru": "Hangisi zıt (karşıt) anlamlı kelime çiftidir?", "siklar": ["Siyah - Beyaz", "Okul - Mektep", "Cevap - Yanıt", "Al - Kırmızı"], "dogru": "Siyah - Beyaz"}
            ]
            return random.choice(sorular)

# Gemini AI Question Generator
def GeminiSoruUret(api_key, ders, konu):
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        5. sınıf {ders} dersi {konu} konusu ile ilgili test sorusu hazırla.
        Yanıtı TAM OLARAK şu JSON formatında ver, başka hiçbir metin ekleme:
        {{
            "soru": "Soru metni",
            "siklar": ["Şık1", "Şık2", "Şık3", "Şık4"],
            "dogru": "Şık1"
        }}
        """
        response = model.generate_content(prompt)
        import json
        clean_json = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"AI Soru Üretme Hatası: {e}")
        return None

# --- UI START ---
st.title("🎓 5. Sınıf Akıllı Test Platformu")

# Sidebar Controls
st.sidebar.header("⚙️ Ayarlar & Menü")
mod = st.sidebar.radio("Soru Üretim Modu", ["Şablon Bankası (Ücretsiz)", "Yapay Zekâ (Gemini)"])

if mod == "Yapay Zekâ (Gemini)":
    api_key = st.sidebar.text_input("Gemini API Key Girin:", type="password")
    st.sidebar.caption("[API Key Alın](https://aistudio.google.com/app/apikey)")

ders = st.sidebar.selectbox("Ders Seçin", ["Matematik", "Fen Bilimleri", "Türkçe"])

konu_liste = {
    "Matematik": ["Doğal Sayılarla Çarpma", "Kesirlerde Toplama"],
    "Fen Bilimleri": ["Güneş, Dünya ve Ay"],
    "Türkçe": ["Sözcükte Anlam"]
}
konu = st.sidebar.selectbox("Konu Seçin", konu_liste[ders])

# Main Area Layout
skor_tahtasi()
st.divider()

if st.button("🎲 Yeni Soru Getir", type="primary"):
    st.session_state["cevaplandi"] = False
    if mod == "Şablon Bankası (Ücretsiz)":
        st.session_state["mevcut_soru"] = SablonSoruUret(ders, konu)
    else:
        if not api_key:
            st.warning("Lütfen sol menüden Gemini API Key girin!")
        else:
            with st.spinner("Yapay zekâ soru hazırlıyor..."):
                st.session_state["mevcut_soru"] = GeminiSoruUret(api_key, ders, konu)

# Question Display Area
if st.session_state["mevcut_soru"]:
    q = st.session_state["mevcut_soru"]
    st.subheader(f"📌 {ders} | {konu}")
    st.markdown(f"### **Soru:** {q['soru']}")
    
    secim = st.radio("Cevabınızı seçin:", q["siklar"], key="soru_secim")
    
    if st.button("Cevabı Kontrol Et") and not st.session_state["cevaplandi"]:
        st.session_state["cevaplandi"] = True
        if secim == q["dogru"]:
            st.success("🎉 Tebrikler! Doğru Cevap. (+10 Puan)")
            st.session_state["skor"] += 10
            st.session_state["dogru"] += 1
        else:
            st.error(f"❌ Yanlış Cevap. Doğru Yanıt: **{q['dogru']}**")
            st.session_state["yanlis"] += 1
            
        st.rerun()
