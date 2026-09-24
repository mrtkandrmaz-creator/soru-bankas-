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
# GELİŞMİŞ ŞABLON TABANLI SORU ÜRETİCİ (MAX VARYASYON)
# =========================================================
def sablon_soru_uret(ders, konu):
    # Matematik Soru Şablonları
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

    # Türkçe Soru Şablonları
    elif ders == "Türkçe":
        if "Sözcükte Anlam" in konu:
            kelimeler = [("Siyah", "Beyaz"), ("Uzun", "Kısa"), ("Zengin", "Fakir"), ("Açık", "Kapalı"), ("Taze", "Bayat")]
            k1, k2 = random.choice(kelimeler)
            return {"soru": f"'{k1}' kelimesinin zıt (karşıt) anlamlısı hangisidir?", "siklar": [k2, "Mavi", "Geniş", "Pahalı"], "dogru": k2, "kaynak": "Şablon Bankası"}
        
        elif "Noktalama" in konu:
            return {"soru": "Tamamlanmış cümlelerin sonuna hangi noktalama işareti konur?", "siklar": ["Nokta (.)", "Virgül (,)", "Soru İşareti (?)", "Ünlem (!)"], "dogru": "Nokta (.)", "kaynak": "Şablon Bankası"}

    # Fen Bilimleri Soru Şablonları
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

    # Genel Varsayılan Şablon Üretici (Sistem çökmesini engeller)
    soru_havuzu = [
        {"soru": f"5. sınıf {ders} dersi '{konu}' konusu ile ilgili temel değerlendirme sorusu aşağıdakilerden hangisidir?", "siklar": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"], "dogru": "Seçenek A"},
        {"soru": f"'{konu}' öğrenme alanında kazanımı doğrulamak için hangi ifade doğru kabul edilir?", "siklar": ["Doğru Kavram", "Yanlış Tanım", "Eksik Bilgi", "Çelişkili İfade"], "dogru": "Doğru Kavram"}
    ]
    secilen = random.choice(soru_havuzu)
    secilen["kaynak"] = "Şablon Bankası"
    return secilen

# =========================================================
# YAPAY ZEKÂ (GEMINI) SORU ÜRETİCİ (NEW SDK)
# =========================================================
def gemini_soru_uret(api_key, ders, konu):
    if not api_key or not api_key.startswith("AIzaSy"):
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        MEB 5. sınıf {ders} dersi "{konu}" konusu ile ilgili MEB kazanımlarına tam uygun 4 şıklı 1 adet test sorusu hazırla.
        Yanıtı YALNIZCA geçerli bir JSON formatında ver, başka hiçbir metin, açıklama veya markdown eki ekleme:
        {{
            "soru": "Soru metni",
            "siklar": ["A Şıkkı Metni", "B Şıkkı Metni", "C Şıkkı Metni", "D Şıkkı Metni"],
            "dogru": "Doğru olan şık metni"
        }}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean_json = response.text.strip().replace("```json", "").replace("
