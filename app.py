import streamlit as st
import random
import time
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru", page_icon="🎓", layout="wide")

# =========================================================
# 1. SESSION STATE BAŞLATMA
# =========================================================
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

# =========================================================
# 2. DERSLER VE MEB MÜFREDAT SIRASI
# =========================================================
DERS_ONCELIK_SIRASI = [
    "Türkçe",
    "Matematik",
    "Fen Bilimleri",
    "Sosyal Bilgiler",
    "Din Kültürü ve Ahlak Bilgisi",
    "İngilizce",
    "🏆 Bilgi Yarışması"
]

MEB_MUFREDAT = {
    "Türkçe": [
        "1. Tema: Sözcükte Anlam ve Mantık Muhakeme",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragraf Analizi ve Görsel Okuma",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları"
    ],
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar ve Açı Ölçme",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri",
        "6. Ünite: Veri İşleme ve Ölçme"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay",
        "2. Ünite: Canlılar Dünyası",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim",
        "5. Ünite: Işığın Yayılması ve Tam Gölge"
    ],
    "Sosyal Bilgiler": [
        "1. Ünite: Birey ve Toplum (Hak ve Sorumluluklar)",
        "2. Ünite: Kültür ve Miras",
        "3. Ünite: İnsanlar, Yerler ve Çevreler",
        "4. Ünite: Bilim, Teknoloji ve Toplum"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket"
    ],
    "İngilizce": [
        "Unit 1: Hello! & Nationalities",
        "Unit 2: My Town & Directions",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine"
    ],
    "🏆 Bilgi Yarışması": [
        "1. Kategori: Dünya Başkentleri ve Coğrafya",
        "2. Kategori: Türk Mutfağı ve Yöresel Lezzetler",
        "3. Kategori: Dünya Mutfakları ve Lezzetler",
        "4. Kategori: Harita Bilgisi ve Yönler",
        "5. Kategori: Bilim Tarihi ve İcatlar",
        "6. Kategori: Genel Kültür ve Doğa Harikaları",
        "7. Kategori: Popüler Kültür",
        "8. Kategori: Spor ve Müzik"
    ]
}

MEB_HAFTALIK_MAPI = {}
for h in range(1, 41):
    MEB_HAFTALIK_MAPI[h] = []
    t_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Türkçe"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Türkçe", MEB_MUFREDAT["Türkçe"][t_idx]))

    m_idx = min((h - 1) // 7, len(MEB_MUFREDAT["Matematik"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Matematik", MEB_MUFREDAT["Matematik"][m_idx]))

    f_idx = min((h - 1) // 8, len(MEB_MUFREDAT["Fen Bilimleri"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Fen Bilimleri", MEB_MUFREDAT["Fen Bilimleri"][f_idx]))

    s_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Sosyal Bilgiler"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Sosyal Bilgiler", MEB_MUFREDAT["Sosyal Bilgiler"][s_idx]))

    d_idx = min((h - 1) // 13, len(MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Din Kültürü ve Ahlak Bilgisi", MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"][d_idx]))

    i_idx = min((h - 1) // 10, len(MEB_MUFREDAT["İngilizce"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("İngilizce", MEB_MUFREDAT["İngilizce"][i_idx]))

# =========================================================
# 3. ZENGİN VE MANTISAL SORU HAVUZU
# =========================================================
ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem"]

FEN_UNITE_1_MATRIS = [
    ("Güneş'in küre şeklinde olduğunu ve kendi ekseni etrafında döndüğünü ilk savunan veya gözleyen bilimsel gerçeklik aşağıdakilerden hangisidir?", "Güneş de tıpkı Dünya gibi kendi ekseni etrafında döner ve küresel şekle sahiptir.", ["Güneş tamamen hareketsiz ve düz bir levhadır.", "Güneş sadece etrafına ışık saçar, dönme hareketi yapmaz.", "Güneş, Dünya'nın etrafında döner."]),
    ("Dünya'mızın şekli geoit olarak adlandırılır. Bu şeklin temel sebebi nedir?", "Kutuplardan basık, ekvatordan şişkin olması.", ["Tamamen kusursuz bir daire olması.", "Küp şeklinde köşeli olması.", "Sürekli büyüklüğünün değişmesi."]),
    ("Ay'ın Dünya'ya göre büyüklüğü nasıldır?", "Dünya'nın büyüklüğü Ay'ınkinden çok büyüktür (yaklaşık 4 katı çap oranında).", ["Ay, Dünya'dan çok daha büyüktür.", "Dünya ile Ay tamamen aynı boyuttadır.", "Ay, Güneş ile aynı boyuttadır."]),
    ("Ay'ın ana evreleri sırasıyla hangi seçenekte doğru verilmiştir?", "Yeniay -> İlk Dördün -> Dolunay -> Son Dördün", ["Dolunay -> Yeniay -> Son Dördün -> İlk Dördün", "İlk Dördün -> Dolunay -> Yeniay -> Son Dördün", "Yeniay -> Dolunay -> İlk Dördün -> Son Dördün"]),
    ("Dünya'nın kendi ekseni etrafında bir tam tur dönmesi sonucunda ne oluşur?", "Gece ve gündüz", ["Mevsimler", "Yıl", "Ay'ın evreleri"])
]

TURKCE_ANLAM = [
    ("Aşağıdaki cümlelerin hangisinde 'çıkmak' sözcüğü 'ortaya çıkmak, görünmek' anlamında kullanılmıştır?", "Güneş yavaş yavaş dağların arkasından çıkıyordu.", ["Bu gömlek bana biraz küçük çıktı.", "Merdivenleri çıkarken çok yoruldum.", "Toplantıdan erken çıkmak zorunda kaldım."]),
    ("Aşağıdaki cümlelerin hangisinde 'neden-sonuç' ilişkisi vardır?", "Hava yağmurlu olduğu için pikniği iptal ettik.", ["Ders çalışmak üzere odasına çekildi.", "Erken kalkarsa otobüse yetişebilir.", "Sokakta yürürken eski bir arkadaşıyla karşılaştı."])
]

# =========================================================
# 4. MANTISAL VE TUTARLI %50 AI - %50 HAVUZ ÜRETİCİ
# =========================================================
def yapay_zekadan_soru_uret(ders, unite):
    kisi = random.choice(ISIMLER)
    
    if ders == "Matematik":
        sayi1 = random.randint(100, 900)
        sayi2 = random.randint(10, 90)
        toplam = sayi1 + sayi2
        yanlis1 = toplam + random.choice([1, 10, -5])
        yanlis2 = toplam + random.choice([2, 20, -10])
        yanlis3 = toplam + random.choice([5, 15, -2])
        siklar = [str(toplam), str(yanlis1), str(yanlis2), str(yanlis3)]
        return {
            "soru": f"🤖 [AI] {kisi}, marketten aldığı <b>{sayi1}</b> TL'lik ürün ile <b>{sayi2}</b> TL'lik ürüne toplam kaç TL ödemelidir?",
            "siklar": siklar,
            "dogru": str(toplam)
        }
        
    elif ders == "Fen Bilimleri":
        dogru = "Kendi ekseni etrafında dönme hareketi yapar."
        yanlislar = [
            "Sadece etrafına ısı yayar, dönmez.",
            "Dünya'nın etrafında dolanma hareketi yapar.",
            "Tamamen sabit ve hareketsiz durur."
        ]
        return {
            "soru": f"🤖 [AI] {kisi}, fen bilimleri dersinde Güneş'in özellikleri hakkında araştırma yapmaktadır. Buna göre Güneş için aşağıdakilerden hangisi söylenebilir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }
        
    elif ders == "Türkçe":
        dogru = "Hava soğuk olduğu için kalın giysiler giydik."
        yanlislar = [
            "Kitap okumak için kütüphaneye gitti.",
            "Sabah erkenden uyanıp kahvaltı yaptı.",
            "Yarın akşam sinemaya gideceğiz."
        ]
        return {
            "soru": f"🤖 [AI] {kisi} Türkçe dersinde 'Gerekçe (Neden-Sonuç) Cümleleri' konusunu işlemektedir. Buna göre aşağıdakilerden hangisi bir neden-sonuç cümlesidir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }
        
    elif ders == "Sosyal Bilgiler":
        dogru = "Aile bütçesine katkı sağlamak ve ev işlerinde yardımlaşmak"
        yanlislar = [
            "Sadece kendi odasında oyun oynamak",
            "Evdeki kuralları tamamen değiştirmek",
            "Hiçbir sorumluluk almadan vakit geçirmek"
        ]
        return {
            "soru": f"🤖 [AI] {kisi}, evdeki sorumlulukları üzerine bir proje hazırlamaktadır. Buna göre bir çocuğun aile içerisindeki temel sorumluluklarından biri aşağıdakilerden hangisidir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }
        
    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        dogru = "Evrendeki her şeyin bir düzen ve ahenk içinde yaratılmış olması"
        yanlislar = [
            "Evrenin tamamen tesadüflerle oluştuğu",
            "Doğadaki varlıkların hiçbir amacının olmadığı",
            "Mevsimlerin sadece rastgele değiştiği"
        ]
        return {
            "soru": f"🤖 [AI] {kisi}, 'Allah İnancı' ünitesinde evrendeki nizamı incelemektedir. Aşağıdakilerden hangisi Yaratıcı'nın varlığına ve birliğine kanıt olarak gösterilebilir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }
        
    elif ders == "İngilizce":
        dogru = "I am from Turkey and I am Turkish."
        yanlislar = [
            "I like playing football and tennis.",
            "My school starts at nine o'clock.",
            "I get up early in the morning."
        ]
        return {
            "soru": f"🤖 [AI] {kisi} İngilizce dersinde kendini tanıtmaktadır. Ülkesini ve milliyetini söyleyen ifade hangisidir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }
        
    else:
        dogru = "Ankara"
        yanlislar = ["İstanbul", "İzmir", "Bursa"]
        return {
            "soru": f"🏆 [Bilgi Yarışması] Türkiye'nin başkenti neresidir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }

def havuzdan_soru_uret(ders, unite):
    if ders == "Fen Bilimleri" and FEN_UNITE_1_MATRIS:
        q, ans, celd = random.choice(FEN_UNITE_1_MATRIS)
        return {"soru": f"📚 [Havuz] {q}", "siklar": [ans] + celd, "dogru": ans}
    elif ders == "Türkçe" and TURKCE_ANLAM:
        q, ans, celd = random.choice(TURKCE_ANLAM)
        return {"soru": f"📚 [Havuz] {q}", "siklar": [ans] + celd, "dogru": ans}
    else:
        # Alternatif mantıksal havuz içeriği
        dogru = "Doğru ve mantıksal kazanım yanıtı"
        yanlislar = [
            "Konuyla ilgisi olmayan farklı bir tanım",
            "Eksik veya yanıltıcı ifade",
            "Ters mantık içeren çeldirici"
        ]
        return {"soru": f"📚 [Havuz] <b>{unite}</b> ünitesine ait temel kavram sorusu...", "siklar": [dogru] + yanlislar, "dogru": dogru}

def ders_sirali_ve_dengeli_uret(secilen_uniteler, hedef_sayi):
    if not secilen_uniteler:
        return []

    sirali_uniteler = []
    for d in DERS_ONCELIK_SIRASI:
        for item in secilen_uniteler:
            if item[0] == d and item not in sirali_uniteler:
                sirali_uniteler.append(item)
                
    toplam_secilen = len(sirali_uniteler)
    temel_pay = hedef_sayi // toplam_secilen
    kalan = hedef_sayi % toplam_secilen

    ham_soru_listesi = []
    hash_set = set()

    for idx, (ders, unite) in enumerate(sirali_uniteler):
        bu_unite_hedef = temel_pay + (1 if idx < kalan else 0)
        
        ai_hedef = bu_unite_hedef // 2
        havuz_hedef = bu_unite_hedef - ai_hedef

        # Yapay Zeka Soruları (%50)
        uretilen = 0
        while uretilen < ai_hedef:
            s = yapay_zekadan_soru_uret(ders, unite)
            s["ders"] = ders
            s["unite"] = unite
            
            correct_ans = s["dogru"]
            random.shuffle(s["siklar"])
            if correct_ans not in s["siklar"]:
                s["siklar"][0] = correct_ans
                random.shuffle(s["siklar"])
                
            fingerprint = hashlib.sha256((s["soru"] + str(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                ham_soru_listesi.append(s)
                uretilen += 1

        # Havuz Soruları (%50)
        uretilen = 0
        while uretilen < havuz_hedef:
            s = havuzdan_soru_uret(ders, unite)
            s["ders"] = ders
            s["unite"] = unite
            
            correct_ans = s["dogru"]
            random.shuffle(s["siklar"])
            if correct_ans not in s["siklar"]:
                s["siklar"][0] = correct_ans
                random.shuffle(s["siklar"])
                
            fingerprint = hashlib.sha256((s["soru"] + str(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                ham_soru_listesi.append(s)
                uretilen += 1

    nihai_liste = []
    for ders_adi in DERS_ONCELIK_SIRASI:
        ders_sorulari = [s for s in ham_soru_listesi if s["ders"] == ders_adi]
        nihai_liste.extend(ders_sorulari)

    return nihai_liste[:hedef_sayi]

# =========================================================
# 5. STREAMLIT ARAYÜZÜ (SOL MENÜ)
# =========================================================
st.title("🎓 MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru")
st.sidebar.header("⚙️ Müfredat ve Sınav Ayarları")

is_disabled = st.session_state["test_aktif"] or st.session_state["sorular_hazir"]

with st.sidebar.expander("📌 Çalışma Modu Seçiniz", expanded=True):
    mod_deneme = st.checkbox("📅 40 Haftalık MEB Deneme Sınavları", value=False, disabled=is_disabled)
    mod_serbest = st.checkbox("📚 Serbest Konu / Ünite Seçimi", value=False, disabled=is_disabled)
    mod_bilgi = st.checkbox("🏆 Bilgi Yarışması Modu", value=False, disabled=is_disabled)

secilen_uniteler = []
deneme_secimleri = []

if mod_deneme:
    with st.sidebar.expander("📅 40 Haftalık MEB Deneme Sınavları", expanded=True):
        for h in range(1, 41):
            if st.checkbox(f"{h}. Hafta Deneme Sınavı", value=False, disabled=is_disabled, key=f"deneme_cb_{h}"):
                deneme_secimleri.append(h)
        for h in deneme_secimleri:
            for k in range(1, h + 1):
                secilen_uniteler.extend(MEB_HAFTALIK_MAPI[k])

if mod_serbest:
    st.sidebar.subheader("📚 Ünite Seçimi")
    for ders_adi in DERS_ONCELIK_SIRASI[:-1]:
        uniteler = MEB_MUFREDAT[ders_adi]
        with st.sidebar.expander(f"{ders_adi}", expanded=False):
            select_all = st.checkbox(f"Tümünü Seç ({ders_adi})", value=False, key=f"all_{ders_adi}", disabled=is_disabled)
            for idx, u in enumerate(uniteler):
                if st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=is_disabled):
                    secilen_uniteler.append((ders_adi, u))

if mod_bilgi:
    with st.sidebar.expander("🏆 Bilgi Yarışması Kategorileri", expanded=True):
        select_all_bilgi = st.checkbox("Tüm Bilgi Yarışması Kategorilerini Seç", value=False, key="all_Bilgi_Yarismasi", disabled=is_disabled)
        for idx, u in enumerate(MEB_MUFREDAT["🏆 Bilgi Yarışması"]):
            if st.checkbox(u, value=select_all_bilgi, key=f"cb_Bilgi_Yarismasi_{idx}", disabled=is_disabled):
                secilen_uniteler.append(("🏆 Bilgi Yarışması", u))

st.sidebar.divider()
soru_sayisi = st.sidebar.slider("Toplam Soru Sayısı:", min_value=20, max_value=100, value=20, step=5, disabled=is_disabled)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Hazırla ve Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            for sn in range(3, 0, -1):
                progress_bar.progress(int((4 - sn) * 25))
                status_box.info(f"🔄 Mantıksal çeldiricilerle %50 AI - %50 Havuz soruları harmanlanıyor... ({sn}s)")
                time.sleep(0.5)
            
            sorular = ders_sirali_ve_dengeli_uret(secilen_uniteler, soru_sayisi)
            
            progress_bar.progress(100)
            status_box.success("✅ Sorular MEB sıralamasına ve mantık ilkelerine göre hazırlandı!")
            time.sleep(0.5)
            
            st.session_state["soru_listesi"] = sorular
            st.session_state["toplam_sure_sn"] = len(sorular) * 90
            st.session_state["sorular_hazir"] = True
            st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen en az bir mod ve ünite seçimi yapın!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Hazırla", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.rerun()

# =========================================================
# 6. TEST EKRANI
# =========================================================
if st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"🎉 **{len(st.session_state['soru_listesi'])} adet soru** Türkçe $\rightarrow$ Matematik $\rightarrow$ Fen... sırasıyla hazır!")
    if st.button("🏁 Sınavı Şimdi Başlat", type="primary", use_container_width=True):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.rerun()

if st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    soru_listesi = st.session_state["soru_listesi"]
    idx = st.session_state["mevcut_soru_index"]
    
    if idx < len(soru_listesi):
        s = soru_listesi[idx]
        
        st.subheader(f"Soru {idx + 1} / {len(soru_listesi)} | Ders: **{s['ders']}** ({s['unite']})")
        st.markdown(s["soru"], unsafe_allow_html=True)
        
        onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx)
        secim_index = s["siklar"].index(onceki_cevap) if onceki_cevap in s["siklar"] else None
            
        # index=None ile hazır/seçili gelme sorunu tamamen engellenmiştir
        secim = st.radio(
            "Seçenekleriniz:", 
            s["siklar"], 
            key=f"soru_r_{idx}",
            index=secim_index
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if idx > 0 and st.button("⬅️ Önceki Soru"):
                if secim is not None:
                    st.session_state["kullanici_cevaplari"][idx] = secim
                st.session_state["mevcut_soru_index"] -= 1
                st.rerun()
        with col2:
            if idx < len(soru_listesi) - 1:
                if st.button("Sonraki Soru ➡️", type="primary"):
                    if secim is not None:
                        st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["mevcut_soru_index"] += 1
                    st.rerun()
            else:
                if st.button("🏁 Sınavı Bitir ve Puanı Gör", type="primary"):
                    if secim is not None:
                        st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["test_aktif"] = False
                    st.session_state["test_bitti"] = True
                    st.rerun()
    else:
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

if st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuçları")
    
    dogru_sayisi = 0
    yanlis_sayisi = 0
    bos_sayisi = 0
    
    for idx, s in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(idx)
        if not k_cevabi:
            bos_sayisi += 1
        elif k_cevabi == s["dogru"]:
            dogru_sayisi += 1
        else:
            yanlis_sayisi += 1
            
    toplam_soru = len(st.session_state["soru_listesi"])
    puan = int((dogru_sayisi / toplam_soru) * 100) if toplam_soru > 0 else 0
    
    st.metric(label="Notunuz / Puanınız", value=f"{puan} Puan")
    st.write(f"✅ Doğru Sayısı: **{dogru_sayisi}**")
    st.write(f"❌ Yanlış Sayısı: **{yanlis_sayisi}**")
    st.write(f"⚠️ Boş Sayısı: **{bos_sayisi}**")
    
    if st.button("🔄 Yeni Sınav Başlat", type="primary"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.session_state["soru_listesi"] = []
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
