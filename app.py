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
        "Doğal Sayılar (Okuma, Yazma, Bölükler)",
        "Doğal Sayılarla İşlemler (Toplama, Çıkarma, Çarpma, Bölme)",
        "Kesirler (Bileşik, Tam Sayılı, Sıralama)",
        "Kesirlerle İşlemler (Toplama ve Çıkarma)",
        "Ondalık Gösterim (Okuma, Yazma, Basamak Değerleri)",
        "Yüzdeler (Yüzde Hesabı, Karşılaştırma)",
        "Temel Geometrik Kavramlar ve Çizimler (Doğru, Işın, Açı)",
        "Üçgen ve Dörtgenler (Açı ve Kenar Özellikleri)",
        "Veri Toplama ve Değerlendirme (Sıklık Tablosu, Sütun Grafiği)",
        "Uzunluk ve Zaman Ölçme",
        "Alan Ölçme (Kare ve Dikdörtgen)",
        "Geometrik Cisimler (Prizmalar ve Yüzey Alanı)"
    ],
    "Türkçe": [
        "Sözcükte Anlam (Gerçek, Mecaz, Terim, Zıt, Eş Anlam)",
        "Cümlede Anlam (Öznel, Nesnel, Neden-Sonuç, Amaç-Sonuç)",
        "Paragrafta Anlam (Ana Fikir, Yardımcı Fikir, Başlık)",
        "Yazım Kuralları (Büyük Harfler, de/ki/mi Yazımı)",
        "Noktalama İşaretleri (Nokta, Virgül, İki Nokta, Üç Nokta)",
        "Metin Türleri (Hikaye, Masal, Fabl, Anı, Mektup)",
        "Söz Sanatları (Benzetme, Kişileştirme)",
        "Fiiller ve Kök-Ek Bilgisi"
    ],
    "Fen Bilimleri": [
        "Güneş, Dünya ve Ay (Boyut, Yapı ve Hareketler)",
        "Ay'ın Evreleri (Ana ve Ara Evreler)",
        "Canlılar Dünyası (Mantar, Bitki, Hayvan, Mikroskobik Canlılar)",
        "Kuvvetin Ölçülmesi ve Sürtünme (Dinamometre, Sürtünme Kuvveti)",
        "Maddenin Değişimi (Hal Değişimi, Genleşme, Büzüşme)",
        "Işığın Yayılması ve Yansıma (Düzgün ve Dağınık Yansıma)",
        "Tam Gölge ve Gölge Boyunu Etkileyen Faktörler",
        "İnsan ve Çevre (Çevre Kirliliği, Biyoçeşitlilik)",
        "Elektrik Devre Elemanları (Ampul Parlaklığını Etkileyen Değişkenler)"
    ],
    "Sosyal Bilgiler": [
        "Birey ve Toplum (Haklar, Sorumluluklar, Gruplar)",
        "Kültür ve Miras (Tarihi Mekanlar, Doğal Varlıklar, Birliktelik)",
        "İnsanlar, Yerler ve Çevreler (Harita, Yer Şekilleri, İklim)",
        "Bilim, Teknoloji ve Toplum (Teknolojinin Etkileri, Doğru Bilgi)",
        "Üretim, Dağıtım ve Tüketim (Ekonomik Faaliyetler, Meslekler)",
        "Etkin Vatandaşlık (Yönetim Birimleri, Egemenlik ve Bağımsızlık)",
        "Küresel Bağlantılar (Uluslararası İlişkiler ve Ticaret)"
    ],
    "İngilizce": [
        "Unit 1: Hello! (Countries, Nationalities, School Subjects)",
        "Unit 2: My Town (Directions, Places in Town)",
        "Unit 3: Games and Hobbies (Free Time Activities, Abilities)",
        "Unit 4: My Daily Routine (Telling the Time, Daily Activities)",
        "Unit 5: Health (Illnesses, Suggestions - Should/Shouldn't)",
        "Unit 6: Movies (Types of Movies, Expressing Opinions)",
        "Unit 7: Party Time (Months, Ordinal Numbers, Permission)",
        "Unit 8: Fitness (Sports, Making Suggestions)",
        "Unit 9: Animal Shelter (Present Continuous, Farm Animals)",
        "Unit 10: Festivals (Holidays, Numbers 100-1000)"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "Allah İnancı (Allah'ın Sıfatları, İhlas Suresi)",
        "Ramazan ve Oruç (Oruç, İftar, Sahur, Teravih)",
        "Adap ve Nezaket (Nezaket Kuralları, Selamlaşma)",
        "Hz. Muhammed ve Aile Hayatı (Peygamberimizin Ailesi)",
        "Çevremizde Dinin İzleri (Mimaride, Musikide, Edebiyatta Din)"
    ]
}

# =========================================================
# GELİŞMİŞ ŞABLON TABANLI SORU ÜRETİCİ
# =========================================================
def sablon_soru_uret(ders, konu):
    if ders == "Matematik":
        if "Doğal Sayılarla İşlemler" in konu:
            s1, s2 = random.randint(120, 989), random.randint(12, 85)
            d_cevap = s1 * s2
            siklar = list(set([d_cevap, d_cevap + 10, max(1, d_cevap - 25), d_cevap + 100]))
            while len(siklar) < 4:
                siklar.append(d_cevap + random.randint(2, 50))
            random.shuffle(siklar)
            return {"soru": f"{s1} × {s2} işleminin sonucu kaçtır?", "siklar": [str(x) for x in siklar], "dogru": str(d_cevap), "kaynak": "Şablon Bankası"}
        
        elif "Kesir" in konu:
            p1, p2 = random.randint(1, 5), random.randint(1, 5)
            payda = random.randint(6, 15)
            d_cevap = f"{p1 + p2}/{payda}"
            siklar = [d_cevap, f"{p1 + p2}/{payda + 2}", f"{p1}/{payda}", f"{p2 + 1}/{payda + 1}"]
            random.shuffle(siklar)
            return {"soru": f"({p1}/{payda}) + ({p2}/{payda}) işleminin sonucu kaçtır?", "siklar": list(set(siklar)), "dogru": d_cevap, "kaynak": "Şablon Bankası"}

        elif "Alan Ölçme" in konu or "Geometrik" in konu:
            kenar1, kenar2 = random.randint(4, 15), random.randint(3, 12)
            d_cevap = kenar1 * kenar2
            siklar = [d_cevap, (kenar1 + kenar2) * 2, d_cevap + 6, max(2, d_cevap - 4)]
            random.shuffle(siklar)
            return {"soru": f"Kısa kenarı {kenar2} cm, uzun kenarı {kenar1} cm olan bir dikdörtgenin alanı kaç cm²'dir?", "siklar": [str(x) for x in siklar], "dogru": str(d_cevap), "kaynak": "Şablon Bankası"}

    elif ders == "Türkçe":
        if "Sözcükte Anlam" in konu:
            kelimeler = [("Siyah", "Beyaz"), ("Uzun", "Kısa"), ("Zengin", "Fakir"), ("Açık", "Kapalı"), ("Taze", "Bayat")]
            k1, k2 = random.choice(kelimeler)
            return {"soru": f"'{k1}' kelimesinin zıt (karşıt) anlamlısı hangisidir?", "siklar": [k2, "Mavi", "Geniş", "Pahalı"], "dogru": k2, "kaynak": "Şablon Bankası"}
        
        elif "Noktalama" in konu:
            return {"soru": "Tamamlanmış cümlelerin sonuna hangi noktalama işareti konur?", "siklar": ["Nokta (.)", "Virgül (,)", "Soru İşareti (?)", "Ünlem (!)"], "dogru": "Nokta (.)", "kaynak": "Şablon Bankası"}

    elif ders == "Fen Bilimleri":
        if "Güneş" in konu or "Ay" in konu:
            sorular = [
                {"soru": "Güneş'e en yakın gezegen hangisidir?", "siklar": ["Merkür", "Venüs", "Dünya", "Mars"], "dogru": "Merkür"},
                {"soru": "Ay'ın Dünya ile Güneş arasına girdiği evre hangisidir?", "siklar": ["Yeni Ay", "Dolunay", "İlk Dördün", "Son Dördün"], "dogru": "Yeni Ay"},
                {"soru": "Dünya'nın kendi etrafındaki dönüş süresi ne kadardır?", "siklar": ["24 Saat", "365 Gün", "30 Gün", "12 Saat"], "dogru": "24 Saat"}
            ]
            sec = random.choice(sorular)
            sec["kaynak"] = "Şablon Bankası"
            return sec

    soru_havuzu = [
        {"soru": f"5. sınıf {ders} dersi '{konu}' konusu ile ilgili temel değerlendirme sorusu aşağıdakilerden hangisidir?", "siklar": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"], "dogru": "Seçenek A"},
        {"soru": f"'{konu}' öğrenme alanında kazanımı doğrulamak için hangi ifade doğru kabul edilir?", "siklar": ["Doğru Kavram", "Yanlış Tanım", "Eksik Bilgi", "Çelişkili İfade"], "dogru": "Doğru Kavram"}
    ]
    secilen = random.choice(soru_havuzu)
    secilen["kaynak"] = "Şablon Bankası"
    return secilen

# =========================================================
# DİNAMİK VE YOĞUNLUK KONTROLLÜ SORU ÜRETİCİ
# =========================================================
def gemini_soru_uret(api_key, ders, konu):
    if not api_key or not api_key.startswith("AIzaSy"):
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"MEB 5. sınıf {ders} dersi '{konu}' konusu ile ilgili MEB kazanımlarına uygun 4 şıklı 1 adet test sorusu hazırla.\n"
            "Yanıtı YALNIZCA geçerli bir JSON formatında ver:\n"
            "{\n"
            '  "soru": "Soru metni",\n'
            '  "siklar": ["A Şıkkı", "B Şıkkı", "C Şıkkı", "D Şıkkı"],\n'
            '  "dogru": "Doğru şık metni"\n'
            "}"
        )
        
        t0 = time.time()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        # Yanıt süresi 1.8 saniyeyi geçerse sunucu yoğun kabul edilir ve şablona düşülür
        if time.time() - t0 > 1.8:
            return None

        clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        veri = json.loads(clean_json)
        veri["kaynak"] = "Yapay Zekâ (Gemini)"
        return veri
    except Exception:
        return None

def soru_hazirla(api_key, ders, konu):
    # Sunucu yük dengesi ve çeşitlilik için yapay zeka ile şablon birlikte çalışır
    if api_key and api_key.startswith("AIzaSy") and random.random() < 0.6:
        ai_soru = gemini_soru_uret(api_key, ders, konu)
        if ai_soru:
            return ai_soru
    return sablon_soru_uret(ders, konu)

# =========================================================
# ARAYÜZ (STREAMLIT UI)
# =========================================================
st.title("🎓 MEB 5. Sınıf Canlı Zamanlı Sınav Platformu")

st.sidebar.header("⚙️ Sınav Ayarları")

ders = st.sidebar.selectbox("Ders Seçin", list(MEB_MUFREDAT.keys()), disabled=st.session_state["test_aktif"])
konu = st.sidebar.selectbox("Konu Seçin", MEB_MUFREDAT[ders], disabled=st.session_state["test_aktif"])

soru_sayisi = st.sidebar.number_input("Soru Sayısı Girin:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"])

if st.sidebar.button("🎲 Şablon Soru Üret", use_container_width=True, disabled=st.session_state["test_aktif"]):
    yeni_soru = sablon_soru_uret(ders, konu)
    st.sidebar.success(f"✅ Soru Üretildi!\n\n**Soru:** {yeni_soru['soru']}")

st.sidebar.divider()

if API_KEY and API_KEY.startswith("AIzaSy"):
    st.sidebar.success("🔑 Gemini API + Şablon Hibrit Mod Aktif")
else:
    st.sidebar.warning("⚠️ API Key Tanımsız / Şablon Modu Aktif")

# DURUM 1: TEST HENÜZ BAŞLAMADI
if not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"📋 **Sınav Bilgileri:**\n- Ders: **{ders}**\n- Konu: **{konu}**\n- Soru Sayısı: **{soru_sayisi}**\n- Toplam Süre: **{soru_sayisi * 80} saniye**\n\n*Hazırsanız aşağıdaki butona basarak sınavı başlatabilirsiniz.*")
    
    if st.button("🚀 Sınavı Başlat", type="primary"):
        with st.spinner("Sorular hazırlanıyor (AI + Şablon Hibrit Motor)..."):
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

    # Kullanıcı daha önce seçim yapmadıysa varsayılan olarak ŞIKLAR SEÇİLİ GELMEZ (index=None)
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
            st.write(f"👉 **Sizin Cevabınız:** {k_cevabi}")
            st.write(f"✅ **Doğru Cevap:** {d_cevabi}")
            st.caption(f"Kaynak: {q['kaynak']}")

    st.divider()
    if st.button("🔄 Yeni Sınava Başla", type="primary"):
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
