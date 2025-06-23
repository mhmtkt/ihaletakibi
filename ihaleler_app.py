# ihaleler_app.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

DOSYA_ADI = "users.json"

# ------------------- Kalıcı Veri Fonksiyonları -------------------
def kayitlari_yukle():
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def kayitlari_kaydet(kullanicilar):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, indent=4, ensure_ascii=False)

# ------------------- Sayiyi Okunabilir Yap -------------------
def sayi_formatla(sayi):
    if sayi >= 1_000_000:
        milyon = sayi // 1_000_000
        kalan = sayi % 1_000_000
        if kalan == 0:
            return f"{milyon} milyon"
        else:
            binler = kalan // 1000
            yuzler = kalan % 1000
            parcalar = []
            if binler > 0:
                parcalar.append(f"{binler} bin")
            if yuzler > 0:
                parcalar.append(f"{yuzler}")
            return f"{milyon} milyon " + " ".join(parcalar)
    elif sayi >= 1000:
        binler = sayi // 1000
        yuzler = sayi % 1000
        if yuzler == 0:
            return f"{binler} bin"
        else:
            return f"{binler} bin {yuzler}"
    else:
        return str(sayi)

# ------------------- Kullanıcı Yönetimi -------------------
def login():
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        users = st.session_state["users"]
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in_user"] = username
            st.success(f"{username} olarak giriş yaptınız.")
            st.experimental_rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre.")

def register():
    st.subheader("Kayıt Ol")
    username = st.text_input("Yeni Kullanıcı Adı", key="reg_user")
    password = st.text_input("Yeni Şifre", type="password", key="reg_pass")
    if st.button("Kayıt Ol"):
        users = st.session_state["users"]
        if username in users:
            st.error("Bu kullanıcı adı zaten kayıtlı.")
        elif username == "" or password == "":
            st.error("Kullanıcı adı ve şifre boş olamaz.")
        else:
            users[username] = {
                "password": password,
                "profile": None,
                "ihaleler": [],
                "operasyonel_giderler": []
            }
            kayitlari_kaydet(users)
            st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
            st.experimental_rerun()

def logout():
    st.session_state["logged_in_user"] = None
    st.experimental_rerun()

# ------------------- Profil Bilgisi -------------------
def get_profile_info():
    st.subheader("Profil Bilgilerinizi Girin")
    user = st.session_state["users"][st.session_state["logged_in_user"]]

    if user.get("profile") is None:
        with st.form("profile_form"):
            garage_level = st.number_input("Garaj Seviyeniz", min_value=1, max_value=100, step=1)
            arac_sayisi = st.number_input("Araç Sayınız", min_value=0, max_value=100, step=1)
            arac_adlari = []
            for i in range(arac_sayisi):
                arac_adlari.append(st.text_input(f"{i+1}. Araç Adı", key=f"arac_{i}"))
            dorse_sayisi = st.number_input("Toplam Dorse Sayınız", min_value=0, max_value=100, step=1)

            submitted = st.form_submit_button("Kaydet")
            if submitted:
                profile = {
                    "garage_level": garage_level,
                    "arac_sayisi": arac_sayisi,
                    "arac_adlari": arac_adlari,
                    "dorse_sayisi": dorse_sayisi
                }
                user["profile"] = profile
                kayitlari_kaydet(st.session_state["users"])
                st.success("Profil bilgileri kaydedildi!")
                st.experimental_rerun()
    else:
        st.info("Profil bilgilerin zaten kayıtlı.")

# ------------------- İhale Girişi -------------------
def ihale_girisi():
    st.subheader("İhale Girişi")
    user = st.session_state["users"][st.session_state["logged_in_user"]]

    with st.form("ihale_form"):
        ihale_turu = st.text_input("İhale Türü (örn: kimyasal)")
        ihale_bedeli = st.number_input("İhalenin Toplam Bedeli ($)", min_value=0.0, format="%.2f")
        birim_urun_maliyeti = st.number_input("Birim Ürün Maliyeti ($)", min_value=0.0, format="%.2f")
        urun_sayisi = st.number_input("Ürün Sayısı (adet)", min_value=0)
        submitted = st.form_submit_button("İhale Kaydet")

        if submitted:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ihale = {
                "ihale_turu": ihale_turu,
                "ihale_bedeli": ihale_bedeli,
                "birim_urun_maliyeti": birim_urun_maliyeti,
                "urun_sayisi": urun_sayisi,
                "tarih": now
            }
            user["ihaleler"].append(ihale)
            kayitlari_kaydet(st.session_state["users"])
            st.success("İhale kaydedildi!")

# ------------------- Operasyonel Giderler -------------------
def operasyonel_giderler():
    st.subheader("Operasyonel Giderler")

    user = st.session_state["users"][st.session_state["logged_in_user"]]
    giderler = user.get("operasyonel_giderler", [])

    secim = st.selectbox("Gider Türü Seçiniz", [
        "Garaj Bakımı", "Garaj Seviye Yükseltmesi", "Maaş Ödemesi", 
        "Araç Bakımı", "Araç Alımı", "Araç Satımı", 
        "Dorse Alımı", "Emeklilik / İşten Kovma", "Araç Yükseltme Bedeli"
    ])

    with st.form("gider_form"):
        if secim == "Garaj Bakımı":
            tutar = st.number_input("Garaj Bakım Tutarı ($)", min_value=0.0, format="%.2f")
        elif secim == "Garaj Seviye Yükseltmesi":
            yeni_seviye = st.number_input("Yeni Garaj Seviyesi", min_value=1, max_value=100, step=1)
            tutar = st.number_input("Yükseltme Maliyeti ($)", min_value=0.0, format="%.2f")
        elif secim == "Maaş Ödemesi":
            sofor_ad = st.text_input("Şoför Adı")
            tutar = st.number_input("Maaş Tutarı ($)", min_value=0.0, format="%.2f")
        elif secim == "Araç Bakımı":
            arac_listesi = user["profile"]["arac_adlari"] if user.get("profile") else []
            arac_sec = st.selectbox("Araç Seçiniz", arac_listesi)
            tutar = st.number_input("Bakım Maliyeti ($)", min_value=0.0, format="%.2f")
        elif secim == "Araç Alımı":
            arac_adi = st.text_input("Alınan Araç Adı")
            tutar = st.number_input("Araç Maliyeti ($)", min_value=0.0, format="%.2f")
        elif secim == "Araç Satımı":
            arac_listesi = user["profile"]["arac_adlari"] if user.get("profile") else []
            arac_sec = st.selectbox("Satılan Araç", arac_listesi)
            tutar = st.number_input("Satış Tutarı ($)", min_value=0.0, format="%.2f")
        elif secim == "Dorse Alımı":
            dorse_tipi = st.text_input("Dorse Tipi")
            tutar = st.number_input("Dorse Maliyeti ($)", min_value=0.0, format="%.2f")
        elif secim == "Emeklilik / İşten Kovma":
            sofor_ad = st.text_input("Şoför Adı")
            tutar = st.number_input("Tazminat Tutarı ($)", min_value=0.0, format="%.2f")
        elif secim == "Araç Yükseltme Bedeli":
            arac_listesi = user["profile"]["arac_adlari"] if user.get("profile") else []
            arac_sec = st.selectbox("Araç Seçiniz", arac_listesi)
            tutar = st.number_input("Yükseltme Maliyeti ($)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Gider Kaydet")

        if submitted:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            gider = {
                "tip": secim,
                "tutar": tutar,
                "tarih": now
            }

            # Özel durumlar:
            if secim == "Garaj Seviye Yükseltmesi":
                user["profile"]["garage_level"] = yeni_seviye
            elif secim == "Araç Alımı":
                user["profile"]["arac_sayisi"] += 1
                user["profile"]["arac_adlari"].append(arac_adi)
            elif secim == "Araç Satımı":
                if arac_sec in user["profile"]["arac_adlari"]:
                    user["profile"]["arac_sayisi"] -= 1
                    user["profile"]["arac_adlari"].remove(arac_sec)
                gider["tutar"] = -tutar  # Satıştan gelir olarak eksi gider yazılır

            giderler.append(gider)
            user["operasyonel_giderler"] = giderler

            kayitlari_kaydet(st.session_state["users"])
            st.success("Operasyonel gider kaydedildi!")

# ------------------- Günlük Rapor -------------------
def gunluk_rapor():
    st.subheader("Günlük Rapor")

    user = st.session_state["users"][st.session_state["logged_in_user"]]
    ihaleler = user.get("ihaleler", [])
    giderler = user.get("operasyonel_giderler", [])

    secilen_tarih = st.date_input("Raporlanacak Tarih", value=datetime.now().date())

    # O günün ihaleleri ve giderleri
    ihaleler_gun = [ih for ih in ihaleler if datetime.strptime(ih["tarih"], "%Y-%m-%d %H:%M:%S").date() == secilen_tarih]
    giderler_gun = [gd for gd in giderler if datetime.strptime(gd["tarih"], "%Y-%m-%d %H:%M:%S").date() == secilen_tarih]

    toplam_ihale_sayisi = len(ihaleler_gun)
    toplam_ihale_geliri = sum(ih["ihale_bedeli"] for ih in ihaleler_gun)
    toplam_urun_maliyeti = sum(ih["birim_urun_maliyeti"] * ih["urun_sayisi"] for ih in ihaleler_gun)
    toplam_operasyonel_gider = sum(gd["tutar"] for gd in giderler_gun)
    toplam_kar = toplam_ihale_geliri - (toplam_urun_maliyeti + toplam_operasyonel_gider)

    st.write(f"**Toplam İhale Sayısı:** {toplam_ihale_sayisi}")
    st.write(f"**Toplam İhale Geliri:** {sayi_formatla(int(toplam_ihale_geliri))}$")
    st.write(f"**Toplam Ürün Maliyeti:** {sayi_formatla(int(toplam_urun_maliyeti))}$")
    st.write(f"**Toplam Operasyonel Gider:** {sayi_formatla(int(toplam_operasyonel_gider))}$")
    st.write(f"**Toplam Kar:** {sayi_formatla(int(toplam_kar))}$")

    # Kâr/zarar uyarısı
    if toplam_kar > 0:
        st.success("Bugün kar ettiniz! 🎉")
    elif toplam_kar < 0:
        st.error("Bugün zarar ettiniz! ⚠️")
    else:
        st.info("Bugün ne kar ne zarar ettiniz.")

    # Excel dışa aktar
    if st.button("Excel'e Dışa Aktar"):
        df_ihaleler = pd.DataFrame(ihaleler_gun)
        df_giderler = pd.DataFrame(giderler_gun)

        with pd.ExcelWriter("gunluk_rapor.xlsx") as writer:
            df_ihaleler.to_excel(writer, sheet_name="Ihaleler", index=False)
            df_giderler.to_excel(writer, sheet_name="Giderler", index=False)

        st.success("gunluk_rapor.xlsx dosyasına dışa aktarıldı.")

# ------------------- Haftalık ve Aylık Rapor -------------------
def haftalik_aylik_rapor():
    st.subheader("Haftalık / Aylık Raporlar")

    user = st.session_state["users"][st.session_state["logged_in_user"]]
    ihaleler = user.get("ihaleler", [])
    giderler = user.get("operasyonel_giderler", [])

    secim = st.selectbox("Rapor Tipi Seçiniz", ["Son 7 Gün", "Son 30 Gün"])

    bugun = datetime.now().date()
    if secim == "Son 7 Gün":
        baslangic = bugun - timedelta(days=7)
    else:
        baslangic = bugun - timedelta(days=30)

    ihaleler_secim = [ih for ih in ihaleler if baslangic <= datetime.strptime(ih["tarih"], "%Y-%m-%d %H:%M:%S").date() <= bugun]
    giderler_secim = [gd for gd in giderler if baslangic <= datetime.strptime(gd["tarih"], "%Y-%m-%d %H:%M:%S").date() <= bugun]

    toplam_ihale_geliri = sum(ih["ihale_bedeli"] for ih in ihaleler_secim)
    toplam_operasyonel_gider = sum(gd["tutar"] for gd in giderler_secim)
    toplam_kar = toplam_ihale_geliri - toplam_operasyonel_gider

    st.write(f"**{secim} İhale Geliri:** {sayi_formatla(int(toplam_ihale_geliri))}$")
    st.write(f"**{secim} Operasyonel Gider:** {sayi_formatla(int(toplam_operasyonel_gider))}$")
    st.write(f"**{secim} Net Kar:** {sayi_formatla(int(toplam_kar))}$")

    # En kârlı ihale türü
    tur_gelirleri = {}
    for ih in ihaleler_secim:
        tur_gelirleri[ih["ihale_turu"]] = tur_gelirleri.get(ih["ihale_turu"], 0) + ih["ihale_bedeli"]

    if tur_gelirleri:
        en_karlı_tur = max(tur_gelirleri, key=tur_gelirleri.get)
        st.write(f"**En Kârlı İhale Türü:** {en_karlı_tur} ({sayi_formatla(int(tur_gelirleri[en_karlı_tur]))}$)")
    else:
        st.write("Bu dönemde ihale verisi yok.")

# ------------------- Grafiksel Rapor -------------------
def grafiksel_rapor():
    st.subheader("Grafiksel Raporlar")

    user = st.session_state["users"][st.session_state["logged_in_user"]]
    ihaleler = user.get("ihaleler", [])
    giderler = user.get("operasyonel_giderler", [])

    st.markdown("**Tarih Aralığı Seçin**")
    baslangic = st.date_input("Başlangıç Tarihi", value=datetime.now().date() - timedelta(days=30))
    bitis = st.date_input("Bitiş Tarihi", value=datetime.now().date())

    if baslangic > bitis:
        st.error("Başlangıç tarihi bitiş tarihinden büyük olamaz!")
        return

    ihaleler_filtreli = [ih for ih in ihaleler if baslangic <= datetime.strptime(ih["tarih"], "%Y-%m-%d %H:%M:%S").date() <= bitis]
    giderler_filtreli = [gd for gd in giderler if baslangic <= datetime.strptime(gd["tarih"], "%Y-%m-%d %H:%M:%S").date() <= bitis]

    if not ihaleler_filtreli:
        st.warning("Seçilen tarihlerde ihale verisi bulunamadı.")
        return

    st.markdown("### İhale Türü Dağılımı")
    tur_sayilari = {}
    for ih in ihaleler_filtreli:
        tur = ih["ihale_turu"]
        tur_sayilari[tur] = tur_sayilari.get(tur, 0) + 1
    tur_df = pd.DataFrame({"Tür": list(tur_sayilari.keys()), "Adet": list(tur_sayilari.values())})
    fig1, ax1 = plt.subplots()
    ax1.pie(tur_df["Adet"], labels=tur_df["Tür"], autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    st.markdown("### İhale Türlerine Göre Gelirler")
    gelirler = {}
    for ih in ihaleler_filtreli:
        tur = ih["ihale_turu"]
        gelirler[tur] = gelirler.get(tur, 0) + ih["ihale_bedeli"]
    gelir_df = pd.DataFrame({"Tür": list(gelirler.keys()), "Gelir": list(gelirler.values())})
    fig2, ax2 = plt.subplots()
    ax2.bar(gelir_df["Tür"], gelir_df["Gelir"], color='green')
    ax2.set_ylabel("Gelir ($)")
    st.pyplot(fig2)

    st.markdown("### Operasyonel Gider Dağılımı")
    if not giderler_filtreli:
        st.info("Henüz operasyonel gider girişi yapılmadı.")
    else:
        gider_turleri = {}
        for gd in giderler_filtreli:
            tur = gd.get("tip", "Bilinmeyen")
            gider_turleri[tur] = gider_turleri.get(tur, 0) + gd["tutar"]
        gider_df = pd.DataFrame({"Kategori": list(gider_turleri.keys()), "Tutar": list(gider_turleri.values())})
        fig3, ax3 = plt.subplots()
        ax3.bar(gider_df["Kategori"], gider_df["Tutar"], color='red')
        ax3.set_ylabel("Gider ($)")
        st.pyplot(fig3)

# ------------------- Ana Fonksiyon -------------------
def main():
    st.title("İhale Takip Uygulaması")

    if "users" not in st.session_state:
        st.session_state["users"] = kayitlari_yukle()
    if "logged_in_user" not in st.session_state:
        st.session_state["logged_in_user"] = None

    if st.session_state["logged_in_user"] is None:
        secim = st.radio("Lütfen seçiniz:", ["Giriş Yap", "Kayıt Ol"])
        if secim == "Giriş Yap":
            login()
        else:
            register()
    else:
        st.sidebar.write(f"Hoşgeldiniz, {st.session_state['logged_in_user']}!")
        if st.sidebar.button("Çıkış Yap"):
            logout()

        user = st.session_state["users"][st.session_state["logged_in_user"]]

        # Profil yoksa doldurt
        if user.get("profile") is None:
            get_profile_info()
            return

        sekmeler = ["İhale Girişi", "Operasyonel Giderler", "Günlük Rapor", "Haftalık/Aylık Rapor", "Grafiksel Rapor"]
        secilen_sekme = st.sidebar.selectbox("Sekme Seçin", sekmeler)

        if secilen_sekme == "İhale Girişi":
            ihale_girisi()
        elif secilen_sekme == "Operasyonel Giderler":
            operasyonel_giderler()
        elif secilen_sekme == "Günlük Rapor":
            gunluk_rapor()
        elif secilen_sekme == "Haftalık/Aylık Rapor":
            haftalik_aylik_rapor()
        elif secilen_sekme == "Grafiksel Rapor":
            grafiksel_rapor()

if __name__ == "__main__":
    main()
