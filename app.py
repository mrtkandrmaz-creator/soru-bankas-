import streamlit as st
import random
import json

# Sayfa Yapılandırması
st.set_page_config(page_title="5. Sınıf Ortak Soru Üretici", page_icon="🎓", layout="wide")

# Oturum Durumu (Session State) Başlatma
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

# Skor Tahtası Bileşeni
def skor_tahtasi():
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Puan", st.session_state["skor"])
    col2.metric("Doğru", st.session_state["dogru"])
    col3.metric("Yanlış", st.session_state["yanlis"])

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
    except Exception as e:
        return None

# 3. Ortak (Hibrit) Soru Üretici Mantığı
def hibrit_soru_uret(api_key, ders, konu):
    # %50 İhtimalle veya API anahtarı yoksa Şablon Bankasını kullan
    secim = random.choice(["sablon", "gemini"])
    
    if secim == "gemini" and api_key:
        ai_soru = gemini_soru_uret(api_key, ders, konu)
        if ai_soru:
            return ai_soru
            
    # Yapay zeka seçilemediyse veya hata verdiyse yedek olarak şablona dön
    return sablon_soru_uret(ders, konu)

# --- ARAYÜZ (UI) BAŞLANGICI ---
st.title("🎓 5. Sınıf Akıllı Test Platformu (Ortak Mod)")

# Yan Menü (Sidebar)
st.sidebar.header("⚙️ Ayarlar & Menü")
api_key = st.sidebar.text_input("Gemini API Key (Opsiyonel):", type="password", help="Girmeseniz de şablon soruları çalışmaya devam eder.")
st.sidebar.caption("[Ücretsiz API Key Alın](https://aistudio.google.com/app/apikey)")

ders = st.sidebar.selectbox("Ders Seçin", ["Matematik", "Fen Bilimleri", "Türkçe"])

konu_liste = {
    "Matematik": ["Doğal Sayılarla Çarpma", "Kesirlerde Toplama"],
    "Fen Bilimleri": ["Güneş, Dünya ve Ay"],
    "Türkçe": ["Sözcükte Anlam"]
}
konu = st.sidebar.selectbox("Konu Seçin", konu_liste[ders])

# Ana Ekran Düzeni
skor_tahtasi()
st.divider()

if st.button("🎲 Yeni Soru Getir", type="primary"):
    st.session_state["cevaplandi"] = False
    with st.spinner("Soru hazırlanıyor..."):
        st.session_state["mevcut_soru"] = hibrit_soru_uret(api_key, ders, konu)

# Soru Gösterim Alanı
if st.session_state["mevcut_soru"]:
    q = st.session_state["mevcut_soru"]
    
    col_ders, col_kaynak = st.columns([3, 1])
    col_ders.subheader(f"📌 {ders} | {konu}")
    col_kaynak.caption(f"🤖 Soru Kaynağı: **{q['kaynak']}**")
    
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
