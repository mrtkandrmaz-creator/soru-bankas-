import streamlit as st
import random
import json
import time
import math
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Milyonluk Soru Bankası", page_icon="🎓", layout="wide")

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

MEB_MUFREDAT = {
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve Doğal Sayılarla İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar, Çizimler ve Açı Ölçme",
        "5. Ünite: Veri İşleme ve Uzunluk/Zaman Ölçme",
        "6. Ünite: Alan Ölçme ve Geometrik Cisimler"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay",
        "2. Ünite: Canlılar Dünyası",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim",
        "5. Ünite: Işığın Yayılması ve Tam Gölge",
        "6. Ünite: İnsan ve Çevre",
        "7. Ünite: Elektrik Devre Elemanları"
    ],
    "Türkçe": [
        "1. Tema: Sözcükte Anlam ve Mantık Muhakeme",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragraf Analizi ve Görsel Okuma",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları"
    ],
    "Sosyal Bilgiler": [
        "1. Ünite: Birey ve Toplum (Hak ve Sorumluluklar)",
        "2. Ünite: Kültür ve Miras",
        "3. Ünite: İnsanlar, Yerler ve Çevreler",
        "4. Ünite: Bilim, Teknoloji ve Toplum",
        "5. Ünite: Üretim, Dağıtım ve Tüketim"
    ]
}

def svg_iletki_aci_ciz(derece, etiket="Açı"):
    rad = math.radians(derece)
    x = int(140 + 85 * math.cos(rad))
    y = int(110 - 85 * math.sin(rad))
    return f'''
    <svg width="280" height="125" viewBox="0 0 280 125" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8fafc" rx="8" stroke="#e2e8f0"/>
      <path d="M 50 110 A 90 90 0 0 1 230 110 Z" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
      <line x1="50" y1="110" x2="230" y2="110" stroke="#334155" stroke-width="2"/>
      <line x1="140" y1="110" x2="225" y2="110" stroke="#94a3b8" stroke-width="3" stroke-dasharray="3"/>
      <line x1="140" y1="110" x2="{x}" y2="{y}" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>
      <circle cx="140" cy="110" r="4" fill="#1e40af"/>
      <text x="140" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">{etiket}: {derece}°</text>
    </svg>
    '''

def svg_sutun_grafik(kategori1, v1, kategori2, v2, baslik="Grafik"):
    max_v = max(v1, v2, 1)
    h1 = int((v1 / max_v) * 60)
    h2 = int((v2 / max_v) * 60)
    return f'''
    <svg width="280" height="125" viewBox="0 0 280 125" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="8" stroke="#cbd5e1"/>
      <text x="140" y="18" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e293b" text-anchor="middle">{baslik}</text>
      <rect x="50" y="{95 - h1}" width="45" height="{h1}" fill="#3b82f6" rx="3"/>
      <text x="72" y="{90 - h1}" font-family="sans-serif" font-size="10" fill="#1e293b" text-anchor="middle">{v1}</text>
      <text x="72" y="112" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="middle">{kategori1}</text>
      <rect x="160" y="{95 - h2}" width="45" height="{h2}" fill="#10b981" rx="3"/>
      <text x="182" y="{90 - h2}" font-family="sans-serif" font-size="10" fill="#1e293b" text-anchor="middle">{v2}</text>
      <text x="182" y="112" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="middle">{kategori2}</text>
    </svg>
    '''

def milyonluk_varyasyon_engine(ders, unite):
    u_low = unite.lower()
    
    isimler = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin", "Kaan", "Deniz", "Ömer", "Duru", "Bora", "Ece", "Arda"]
    nesneler = ["kitap", "kalem", "bilye", "fidan", "sayfa", "pul", "çikolata", "roket maketi", "balon", "oyuncak"]
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Trabzon", "Konya", "Eskişehir", "Gaziantep"]

    # -----------------------------------------------------
    # MATEMATİK ENGINE
    # -----------------------------------------------------
    if ders == "Matematik":
        if "açı" in u_low or "geometrik" in u_low:
            aci_deg = random.randint(15, 165)
            if aci_deg == 90:
                tur = "Dik Açı"
                celdiriciler = ["Dar Açı", "Geniş Açı", "Doğru Açı"]
            elif aci_deg < 90:
                tur = "Dar Açı"
                celdiriciler = ["Dik Açı", "Geniş Açı", "Tam Açı"]
            else:
                tur = "Geniş Açı"
                celdiriciler = ["Dar Açı", "Dik Açı", "Doğru Açı"]
                
            kisi = random.choice(isimler)
            soru_tipi = random.choice(["gorsel_tur", "oncul_aci", "tamamlama"])
            
            if soru_tipi == "gorsel_tur":
                q_text = f"{kisi}, iletki yardımıyla defterine bir açı çizmiştir. İletki üzerindeki başlangıç koluna göre verilen açının türü nedir?"
                ans = tur
                siklar = [tur] + celdiriciler
            elif soru_tipi == "oncul_aci":
                q_text = f"Görseldeki {aci_deg}°'lik açı ile ilgili;\nI. Türü {tur}'dir.\nII. Ölçüsü dik açıdan büyüktür.\nIII. Komşu açısı ile toplamı 180° olabilir.\nİfadelerinden hangileri kesinlikle doğrudur?"
                ans = "I ve III"
                siklar = ["I ve III", "Yalnız I", "I ve II", "I, II ve III"]
            else:
                fark = 180 - aci_deg
                q_text = f"Şekilde verilen açıyı bir doğru açıya (180°) tamamlamak için kaç derecelik bir açı daha eklenmelidir?"
                ans = f"{fark}°"
                siklar = [f"{fark}°", f"{fark + 10}°", f"{abs(fark - 15)}°", f"{fark + 20}°"]

            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_iletki_aci_ciz(aci_deg), "siklar": list(dict.fromkeys(siklar)), "dogru": ans}
            
        elif "veri" in u_low or "grafik" in u_low:
            v1, v2 = random.randint(20, 80), random.randint(20, 80)
            k1, k2 = random.sample(["A Kitabı", "B Kitabı", "1. Gün", "2. Gün", "Basketbol", "Futbol"], 2)
            toplam = v1 + v2
            fark = abs(v1 - v2)
            
            q_text = f"Verilen sütun grafiğine göre, {k1} ve {k2} değerleri arasındaki fark hesaplanacaktır. İki değer arasındaki fark kaçtır?"
            ans = str(fark)
            siklar = [str(fark), str(fark + 5), str(toplam), str(abs(fark - 4))]
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": svg_sutun_grafik(k1, v1, k2, v2), "siklar": list(dict.fromkeys(siklar)), "dogru": ans}

        else:
            kisi = random.choice(isimler)
            nesne = random.choice(nesneler)
            n1, n2, n3 = random.randint(100, 500), random.randint(20, 90), random.randint(2, 5)
            
            ans_val = (n1 + n2) * n3
            q_text = f"{kisi}, başlangıçta {n1} adet {nesne} almıştır. Daha sonra arkadaşı ona {n2} adet daha vermiş ve elindeki toplam {nesne} sayısını {n3} katına çıkarmıştır. Son durumda {kisi}'nin kaç {nesne}si vardır?"
            
            ans = str(ans_val)
            siklar = [ans, str(ans_val + 10), str(ans_val - 25), str(ans_val + 50)]
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": ans}

    # -----------------------------------------------------
    # FEN BİLİMLERİ ENGINE
    # -----------------------------------------------------
    elif ders == "Fen Bilimleri":
        kisi = random.choice(isimler)
        if "kuvvet" in u_low or "sürtünme" in u_low:
            yuzeyler = ["Buzlu Yüzey", "Zımpara Kağıdı", "Tahta Zemin", "Halı Zemin"]
            y1, y2 = random.sample(yuzeyler, 2)
            q_text = f"{kisi}, özdeş oyuncak arabaları {y1} ve {y2} üzerinde eşit kuvvetle itmiştir. Arabanın {y1} üzerinde daha uzağa gittiği gözlemlenmiştir.\n\nBu deneye göre aşağıdakilerden hangisi kesinlikle doğrudur?"
            ans = f"{y1} üzerindeki sürtünme kuvveti daha azdır."
            celd = [f"{y2} üzerindeki sürtünme kuvveti daha azdır.", "Her iki yüzeyde sürtünme eşittir.", "Arabanın kütlesi yüzeye göre değişmiştir."]
        else:
            q_text = f"Öğrenci {kisi}, Güneş, Dünya ve Ay'ın birbirine göre hareketlerini inceleyen bir model tasarlamıştır. Modelde Ay'ın Dünya etrafındaki dolanma süresi dikkate alınmıştır.\n\nBuna göre aşağıdakilerden hangisi söylenebilir?"
            ans = "Ay, Dünya etrafındaki turunu yaklaşık 27 günde tamamlar."
            celd = ["Güneş, Dünya etrafında dolanır.", "Ay sadece kendi etrafında döner, Dünya etrafında dönmez.", "Dünya'nın dönme süresi Ay ile birebir aynıdır."]

        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": ans}

    # -----------------------------------------------------
    # TÜRKÇE & SOSYAL BİLGİLER ENGINE
    # -----------------------------------------------------
    else:
        kisi = random.choice(isimler)
        sehir = random.choice(sehirler)
        q_text = f"{kisi}, {sehir} gezisinde elde ettiği gözlemleri şu şekilde sıralamıştır:\nI. Tarihi kaleleri ve müzeleri ziyaret etti.\nII. Bölgenin doğal şelalelerinde fotoğraf çekildi.\nIII. Yerel pazardan geleneksel el sanatları satın aldı.\n\nVerilen öncüllerden hangileri 'Beşeri Unsur' kapsamına girer?"
        ans = "I ve III"
        siklar = ["I ve III", "Yalnız II", "I ve II", "I, II ve III"]
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q_text, "gorsel_svg": None, "siklar": list(dict.fromkeys(siklar)), "dogru": ans}

def sonsuz_benzersiz_soru_uret(secilen_uniteler, hedef_sayi):
    havuz = []
    hash_kayitlari = set()
    
    if not secilen_uniteler:
        return []
        
    u_count = len(secilen_uniteler)
    taban = hedef_sayi // u_count
    kalan = hedef_sayi % u_count
    dagilim = [taban + (1 if i < kalan else 0) for i in range(u_count)]
    
    for idx, (h_ders, h_unite) in enumerate(secilen_uniteler):
        istenen = dagilim[idx]
        uretilen = 0
        deneme = 0
        
        while uretilen < istenen and deneme < 150:
            deneme += 1
            s = milyonluk_varyasyon_engine(h_ders, h_unite)
            
            fingerprint = hashlib.sha256((s["soru"] + "".join(s["siklar"]) + s["dogru"]).encode('utf-8')).hexdigest()
            
            if fingerprint not in hash_kayitlari and len(s["siklar"]) == 4:
                hash_kayitlari.add(fingerprint)
                havuz.append(s)
                uretilen += 1
                
    random.shuffle(havuz)
    return havuz

st.title("🎓 MEB Milyonluk Yeni Nesil Soru Bankası")

st.sidebar.header("⚙️ Müfretad ve Soru Ayarları")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=False):
        select_all = st.checkbox(f"Tüm {ders_adi} Üniteleri", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])

if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("🚀 Yeni Nesil Soru Üretim Paneli")
    if secilen_uniteler:
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Sistem seçilen her üniteden **eşit sayıda**, **tamamen benzersiz** ve **MEB Beceri Temelli** sorular üretecektir.")
        
        if st.button("✨ Milyonluk Soru Havuzundan Üret", type="primary"):
            with st.spinner("Soru şablonları taranıyor, SHA-256 benzersizlik doğrulamasından geçiriliyor..."):
                sorular = sonsuz_benzersiz_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 90
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.warning("⚠️ Lütfen sol taraftaki menüden en az 1 ünite seçin.")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular benzersiz şablon kombinasyonlarıyla başarıyla üretildi!")
    
    toplam_sn = st.session_state["toplam_sure_sn"]
    st.markdown(f"**Toplam Soru:** {len(st.session_state['soru_listesi'])} | **Tahmini Süre:** {toplam_sn // 60} Dk {toplam_sn % 60} Sn")
    
    col1, col2 = st.columns(2)
    if col1.button("⏱️ Testi Başlat", type="primary"):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
        
    if col2.button("🔄 Yeniden Üret"):
        st.session_state["sorular_hazir"] = False
        st.rerun()

elif st.session_state["test_aktif"]:
    gecen_sure = int(time.time() - st.session_state["baslangic_zamani"])
    kalan_sure = st.session_state["toplam_sure_sn"] - gecen_sure

    if kalan_sure <= 0:
        st.warning("⏰ Süreniz doldu!")
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    c_left, c_right = st.columns([3, 1])
    c_left.caption(f"📌 {q['ders']} - {q['unite']}")
    c_right.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")

    st.markdown(f"### **Soru {idx + 1}:**\n{q['soru']}")

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=135)

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Şıkkınızı seçin:", q["siklar"], index=secim_index, key=f"radio_{idx}")
    if secim:
        st.session_state["kullanici_cevaplari"][idx] = secim

    st.divider()
    b1, b2 = st.columns(2)
    if idx > 0 and b1.button("⬅️ Önceki Soru"):
        st.session_state["mevcut_soru_index"] -= 1
        st.rerun()

    if idx + 1 < len(st.session_state["soru_listesi"]):
        if b2.button("Sonraki Soru ➡️", type="primary"):
            st.session_state["mevcut_soru_index"] += 1
            st.rerun()
    else:
        if b2.button("🏁 Testi Bitir", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Test Sonu Karnesi")
    
    toplam = len(st.session_state["soru_listesi"])
    dogru = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    
    st.metric("Doğru / Toplam", f"{dogru} / {toplam}")
    st.progress(dogru / toplam if toplam > 0 else 0)
    
    if st.button("🔄 Yeni Test Yap"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
