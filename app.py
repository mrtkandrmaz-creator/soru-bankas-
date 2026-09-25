# =========================================================
# 8. TEST EKRANI VE SONUÇ GÖSTERİMİ
# =========================================================

# Sorular hazırsa ve test henüz başlamadıysa "Sınavı Başlat" butonu gösterelim
if st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"🎉 **{len(st.session_state['soru_listesi'])} adet soru** başarıyla üretildi ve harmanlandı!")
    if st.button("🏁 Sınavı Şimdi Başlat", type="primary", use_container_width=True):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.rerun()

# Test aktifse soruları ekranda gösterelim
if st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    soru_listesi = st.session_state["soru_listesi"]
    idx = st.session_state["mevcut_soru_index"]
    
    if idx < len(soru_listesi):
        s = soru_listesi[idx]
        
        st.subheader(f"Soru {idx + 1} / {len(soru_listesi)} ({s['ders']} - {s['unite']})")
        st.markdown(s["soru"], unsafe_allow_html=True)
        
        # Eğer geometri sorusu gibi SVG görsel varsa göster
        if s.get("gorsel_svg"):
            st.markdown(s["gorsel_svg"], unsafe_allow_html=True)
            
        # Kullanıcının daha önceki cevabı varsa hatırlatmak için seçili yapabiliriz
        secim = st.radio(
            "Seçenekleriniz:", 
            s["siklar"], 
            key=f"soru_r_{idx}",
            index=s["siklar"].index(st.session_state["kullanici_cevaplari"].get(idx)) if idx in st.session_state["kullanici_cevaplari"] else 0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if idx > 0 and st.button("⬅️ Önceki Soru"):
                st.session_state["kullanici_cevaplari"][idx] = secim
                st.session_state["mevcut_soru_index"] -= 1
                st.rerun()
        with col2:
            if idx < len(soru_listesi) - 1:
                if st.button("Sonraki Soru ➡️", type="primary"):
                    st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["mevcut_soru_index"] += 1
                    st.rerun()
            else:
                if st.button("🏁 Sınavı Bitir ve Puanı Gör", type="primary"):
                    st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["test_aktif"] = False
                    st.session_state["test_bitti"] = True
                    st.rerun()
    else:
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

# Test bittiyse sonuç ekranını gösterelim
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
