import streamlit as st
import random
import json
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="5. Sınıf Sınav Modu", page_icon="🎓", layout="wide")

# --- KESİN VE ESNEK SECRETS OKUMA MANTIGI ---
def get_api_key():
    # 1. Doğrudan Secrets Sözlük Erişimi
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
        elif "API_KEY" in st.secrets:
            return st.secrets["API_KEY"]
        elif "gemini_api_key" in st.secrets:
            return st.secrets["gemini_api_key"]
    except Exception:
        pass
    
    # 2. .get() Metodu Erişimi
    try:
        return st.secrets.get("GEMINI_API_KEY") or st.secrets.get("API_KEY") or st.secrets.get("gemini_api_key")
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

# 1. Şablon Tabanlı Soru Üretici (Yedek Sistem)
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

# 2. Yapay Zekâ (Gemini) Soru Üretici - Yeni SDK Uyumlu
def gemini_soru_uret(api_key, ders, konu):
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        5. sınıf {ders} dersi {konu} konusu ile ilgili zorluğu uygun 4 şıklı test sorusu hazırla.
        Yanıtı YALNIZCA geçerli bir JSON formatında ver, başka hiçbir metin veya açıklama ekleme:
        {{
            "soru": "Soru metni",
            "siklar": ["Şık1", "Şık2", "Şık3", "Şık4"],
            "dogru": "Doğru olan şık metni"
        }}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
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
st.title("🎓 5. Sınıf Canlı Zamanlı Sınav Platformu")

# Yan Menü (Ayarlar)
st.sidebar.header("⚙️ Sınav Ayarları")

ders = st.sidebar.selectbox("Ders Seçin", ["Matematik", "Fen Bilimleri", "Türkçe"], disabled=st.session_state["test_aktif"])

konu_liste = {
    "Matematik": ["Doğal Sayılarla Çarpma", "Kesirlerde Toplama"],
    "Fen Bilimleri": ["Güneş, Dünya ve Ay"],
    "Türkçe": ["Sözcükte Anlam"]
}
konu = st.sidebar.selectbox("Konu Seçin", konu_liste[ders], disabled=st.session_state["test_aktif"])

soru_sayisi = st.sidebar.number_input("Soru Sayısı Girin:", min_value=1, max_value=20, value=5, step=1, disabled=st.session_state["test_aktif"])

# API Durum Bildirimi
if API_KEY:
    st.sidebar.success("🔑 Gemini API Aktif")
else:
    st.sidebar.warning("⚠️ API Key Tanımsız (Şablon Modu)")

# ---------------------------------------------------------
# DURUM 1: TEST HENÜZ BAŞLAMADI
# ---------------------------------------------------------
if not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"📋 **Sınav Bilgileri:**\n- Ders/Konu: **{ders} | {konu}**\n- Soru Sayısı: **{soru_sayisi}**\n- Toplam Süre: **{soru_sayisi * 80} saniye**\n\n*Not: Sınav esnasında doğrular/yanlışlar gösterilmez. Kalan süreniz yukarıda canlı akar.*")
    
    if st.button("🚀 Sınavı Başlat", type="primary"):
        with st.spinner("Sınav soruları hazırlanıyor..."):
            st.session_state["soru_listesi"] = [soru_hazirla(API_KEY, ders, konu) for _ in range(soru_sayisi)]
            st.session_state["kullanici_cevaplari"] = {}
            st.session_state["mevcut_soru_index"] = 0
            st.session_state["toplam_sure"] = soru_sayisi * 80
            st.session_state["baslangic_zamani"] = time.time()
            st.session_state["test_aktif"] = True
            st.session_state["test_bitti"] = False
            st.rerun()

# ---------------------------------------------------------
# DURUM 2: TEST DEVAM EDİYOR (CANLI SAYAÇLI SINAV MODU)
# ---------------------------------------------------------
elif st.session_state["test_aktif"]:
    # Üst Bilgi Barları
    col_sure, col_durum = st.columns([2, 1])
    sure_kutusu = col_sure.empty()  # Canlı sayaç için dinamik alan
    col_durum.write(f"📝 **Soru:** {st.session_state['mevcut_soru_index'] + 1} / {len(st.session_state['soru_listesi'])}")
    
    st.progress((st.session_state["mevcut_soru_index"] + 1) / len(st.session_state["soru_listesi"]))
    st.divider()

    # Soru Gösterimi
    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    st.markdown(f"### **Soru {idx + 1}:** {q['soru']}")

    # Seçilen cevabı hatırla
    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else 0

    secim = st.radio("Cevabınızı seçin:", q["siklar"], index=secim_index, key=f"radio_soru_{idx}")
    st.session_state["kullanici_cevaplari"][idx] = secim

    st.divider()
    col_prev, col_next = st.columns([1, 1])

    # Butonlar
    btn_prev = idx > 0 and col_prev.button("⬅️ Önceki Soru")
    
    if idx + 1 < len(st.session_state["soru_listesi"]):
        btn_next = col_next.button("Sonraki Soru ➡️", type="primary")
        btn_finish = False
    else:
        btn_next = False
        btn_finish = col_next.button("🏁 Sınavı Bitir", type="primary")

    # Butonlara Tıklama Durumu
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

    # CANLI SAYAC DÖNGÜSÜ
    gecen_sure = int(time.time() - st.session_state["baslangic_zamani"])
    kalan_sure = st.session_state["toplam_sure"] - gecen_sure

    if kalan_sure <= 0:
        st.warning("⏰ Süreniz doldu! Sınavınız tamamlanıyor...")
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        time.sleep(1)
        st.rerun()

    # Canlı olarak zaman kutusunu güncelle
    dakika = kalan_sure // 60
    saniye = kalan_sure % 60
    sure_kutusu.metric("⌛ Kalan Süre (Anlık)", f"{dakika:02d}:{saniye:02d}")
    
    # 1 saniye bekle ve sayfayı otomatik yenileyerek sayacı akıt
    time.sleep(1)
    st.rerun()

# ---------------------------------------------------------
# DURUM 3: TEST BİTTİ (SONUÇ KARNESİ VE CEVAP ANAHTARI)
# ---------------------------------------------------------
elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuç Karnesi")

    toplam_soru = len(st.session_state["soru_listesi"])
    dogru_sayisi = 0
    yanlis_sayisi = 0

    # Skor Hesaplama
    for i, q in enumerate(st.session_state["soru_listesi"]):
        kullanici_cevabi = st.session_state["kullanici_cevaplari"].get(i, None)
        if kullanici_cevabi == q["dogru"]:
            dogru_sayisi += 1
        else:
            yanlis_sayisi += 1

    puan = int((dogru_sayisi / toplam_soru) * 100)

    # Özet Kutuları
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Soru", toplam_soru)
    c2.metric("Doğru", dogru_sayisi)
    c3.metric("Yanlış", yanlis_sayisi)
    c4.metric("Başarı Puanı", f"{puan} / 100")

    st.divider()
    st.subheader("🔍 Detaylı Cevap Anahtarı ve İnceleme")

    # Soruları Detaylı İnceleme
    for i, q in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(i, "Boş Bırakıldı")
        d_cevabi = q["dogru"]
        
        with st.expander(f"Soru {i+1}: {'✅ Doğru' if k_cevabi == d_cevabi else '❌ Yanlış'}"):
            st.write(f"**Soru:** {q['soru']}")
            st.write(f"👉 **Sizin Cevabınız:** {k_cevabi}")
            st.write(f"✅ **Doğru Cevap:** {d_cevabi}")
            st.caption(f"Kaynak: {q['kaynak']}")

    st.divider()
    if st.button("🔄 Yeni Sınava Başla", type="primary"):
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
