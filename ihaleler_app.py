import streamlit as st
from datetime import datetime
import pandas as pd

# ----------- Başlangıç: Kullanıcı Yönetimi ---------------

if 'users' not in st.session_state:
    # Kullanıcılar: kullanıcı_adı: {password, profile, ihaleler, operasyonel_giderler}
    st.session_state.users = {}

if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

def register():
    st.subheader("Kayıt Ol")
    username = st.text_input("Kullanıcı Adı", key="register_username")
    password = st.text_input("Şifre", type='password', key="register_password")
    if st.button("Kayıt Ol"):
        if username == "" or password == "":
            st.warning("Lütfen kullanıcı adı ve şifre girin.")
        elif username in st.session_state.users:
            st.error("Bu kullanıcı adı zaten alınmış!")
        else:
            st.session_state.users[username] = {
                "password": password,
                "profile": None,
                "ihaleler": [],
                "operasyonel_giderler": []
            }
            st.success("Kayıt başarılı! Lütfen giriş yapın.")

def login():
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı", key="login_username")
    password = st.text_input("Şifre", type='password', key="login_password")
    if st.button("Giriş Yap"):
        if username in st.session_state.users and st.session_state.users[username]["password"] == password:
            st.session_state.logged_in_user = username
            st.success(f"Hoşgeldin {username}!")
            st.experimental_rerun()
        else:
            st.error("Kullanıcı adı veya şifre yanlış.")

def logout():
    st.session_state.logged_in_user = None
    st.experimental_rerun()

# ----------- Profil Bilgileri (İlk Kayıt Sonrası) -------------

def get_profile_info():
    st.subheader("Profil Bilgileri - İlk Kayıt")
    garage_level = st.number_input("Garaj Seviyeniz", min_value=1, max_value=100, step=1)
    vehicle_count = st.number_input("Araç Sayınız", min_value=0, step=1)
    vehicle_names = []
    for i in range(vehicle_count):
        name = st.text_input(f"Araç {i+1} Adı", key=f"vehicle_name_{i}")
        vehicle_names.append(name)
    trailer_count = st.number_input("Toplam Dorse Sayınız", min_value=0, step=1)

    if st.button("Profil Bilgilerini Kaydet"):
        # Boş isim kontrolü
        if any([name.strip() == "" for name in vehicle_names]):
            st.warning("Lütfen tüm araç isimlerini doldurun.")
            return
        st.session_state.users[st.session_state.logged_in_user]["profile"] = {
            "garage_level": garage_level,
            "vehicle_count": vehicle_count,
            "vehicle_names": vehicle_names,
            "trailer_count": trailer_count
        }
        st.success("Profil bilgileri kaydedildi!")
        st.experimental_rerun()

# ----------- İhale Girişi -------------

def ihale_girisi():
    st.header("İhale Girişi")
    ihale_turu = st.text_input("İhale Türü (örn: Kimyasal)")
    ihale_bedeli = st.number_input("Toplam İhale Bedeli (USD)", min_value=0.0, step=0.01)
    birim_urun_maliyeti = st.number_input("Birim Ürün Maliyeti (USD)", min_value=0.0, step=0.01)
    urun_sayisi = st.number_input("Ürün Sayısı (Adet)", min_value=0, step=1)

    if st.button("İhale Kaydet"):
        if ihale_turu.strip() == "":
            st.warning("Lütfen ihale türünü girin.")
            return
        yeni_ihale = {
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ihale_turu": ihale_turu,
            "ihale_bedeli": ihale_bedeli,
            "birim_urun_maliyeti": birim_urun_maliyeti,
            "urun_sayisi": urun_sayisi
        }
        st.session_state.users[st.session_state.logged_in_user]["ihaleler"].append(yeni_ihale)
        st.success("İhale kaydedildi!")

# ----------- Operasyonel Giderler -------------

def operasyonel_giderler():
    st.header("Operasyonel Giderler Ekleme")
    user_data = st.session_state.users[st.session_state.logged_in_user]

    profile = user_data["profile"]
    if profile is None:
        st.warning("Öncelikle profil bilgilerinizi doldurun.")
        return

    # 1. Garaj Bakımı
    garaj_bakimi = st.number_input("Garaj Bakımı Tutarı (USD)", min_value=0.0, step=0.01)

    # 2. Garaj Seviye Yükseltmesi
    col1, col2 = st.columns(2)
    with col1:
        yeni_garaj_seviyesi = st.number_input("Garaj Seviyesi Yükseltme (Yeni Seviye)", min_value=profile["garage_level"], max_value=100, step=1)
    with col2:
        garaj_yuksektme_maliyeti = st.number_input("Yükseltme Maliyeti (USD)", min_value=0.0, step=0.01)

    # 3. Maaş Ödemesi
    st.subheader("Şoför Maaşları")
    maas_adi = st.text_input("Şoför Adı")
    maas_tutari = st.number_input("Maaş Tutarı (USD)", min_value=0.0, step=0.01)
    if st.button("Maaş Ekle"):
        if maas_adi.strip() == "":
            st.warning("Lütfen şoför adını girin.")
        else:
            gider = {
                "tip": "Maaş Ödemesi",
                "ad": maas_adi,
                "tutar": maas_tutari,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            user_data["operasyonel_giderler"].append(gider)
            st.success(f"{maas_adi} için maaş eklendi.")
            st.experimental_rerun()

    # 4. Araç Bakımı
    st.subheader("Araç Bakımı")
    arac_listesi = profile["vehicle_names"]
    if len(arac_listesi) == 0:
        st.info("Öncelikle profil bölümünden araç ekleyin.")
    else:
        arac_secimi = st.selectbox("Bakımı Yapılan Aracı Seçin", arac_listesi)
        arac_bakim_maliyeti = st.number_input("Bakım Maliyeti (USD)", min_value=0.0, step=0.01, key="arac_bakim_maliyeti")
        if st.button("Araç Bakımı Ekle"):
            gider = {
                "tip": "Araç Bakımı",
                "arac": arac_secimi,
                "tutar": arac_bakim_maliyeti,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            user_data["operasyonel_giderler"].append(gider)
            st.success(f"{arac_secimi} için araç bakımı eklendi.")
            st.experimental_rerun()

    # 5. Araç Alımı
    st.subheader("Araç Alımı")
    yeni_arac_adi = st.text_input("Alınan Araç Adı", key="arac_alim_adi")
    yeni_arac_maliyeti = st.number_input("Araç Maliyeti (USD)", min_value=0.0, step=0.01, key="arac_alim_maliyet")
    if st.button("Araç Alımı Kaydet"):
        if yeni_arac_adi.strip() == "":
            st.warning("Lütfen araç adını girin.")
        else:
            # Araç sayısını ve listeyi güncelle
            profile["vehicle_names"].append(yeni_arac_adi)
            profile["vehicle_count"] += 1

            gider = {
                "tip": "Araç Alımı",
                "arac": yeni_arac_adi,
                "tutar": yeni_arac_maliyeti,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            user_data["operasyonel_giderler"].append(gider)
            st.success(f"{yeni_arac_adi} aracı alındı ve listeye eklendi.")
            st.experimental_rerun()

    # 6. Araç Satımı
    st.subheader("Araç Satımı")
    satilacak_arac = st.selectbox("Satılan Aracı Seçin", arac_listesi, key="satilan_arac_secimi")
    satis_tutari = st.number_input("Satış Tutarı (USD)", min_value=0.0, step=0.01, key="satis_tutari")
    if st.button("Araç Satışını Kaydet"):
        # Araç listeden çıkar
        if satilacak_arac in profile["vehicle_names"]:
            profile["vehicle_names"].remove(satilacak_arac)
            profile["vehicle_count"] -= 1
            gider = {
                "tip": "Araç Satımı",
                "arac": satilacak_arac,
                "tutar": -satis_tutari,  # Satıştan para kazanıldığı için negatif gider olarak eklenir
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            user_data["operasyonel_giderler"].append(gider)
            st.success(f"{satilacak_arac} satıldı ve listeden çıkarıldı.")
            st.experimental_rerun()
        else:
            st.warning("Bu araç zaten satılmış veya listede yok.")

    # 7. Dorse Alımı
    st.subheader("Dorse Alımı")
    dorse_tipi = st.text_input("Alınan Dorse Tipi")
    dorse_maliyeti = st.number_input("Dorse Maliyeti (USD)", min_value=0.0, step=0.01)
    if st.button("Dorse Alımını Kaydet"):
        if dorse_tipi.strip() == "":
            st.warning("Lütfen dorse tipini girin.")
        else:
            gider = {
                "tip": "Dorse Alımı",
                "dorse_tipi": dorse_tipi,
                "tutar": dorse_maliyeti,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            user_data["operasyonel_giderler"].append(gider)
            # Dorse sayısını güncelle
            profile["trailer_count"] += 1
            st.success(f"{dorse_tipi} tipi dorse alındı.")
            st.experimental_rerun()

    # 8. Emeklilik / İşten Kovma
    st.subheader("Emeklilik ve İşten Kovma")
    kovulan_sofor = st.text_input("İşten Kovulan veya Emekli Olan Şoför Adı")
    tazminat_tutari = st.number_input("Tazminat Tutarı (USD)", min_value=0.0, step=0.01)
    if st.button("Emeklilik/Kovma Kaydet"):
        if kovulan_sofor.strip() == "":
            st.warning("Lütfen şoför adını girin.")
        else:
            gider = {
                "tip": "Emeklilik/İşten Kovma",
                "ad": kovulan_sofor,
                "tutar": tazminat_tutari,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            user_data["operasyonel_giderler"].append(gider)
            st.success(f"{kovulan_sofor} için tazminat kaydedildi.")
            st.experimental_rerun()

    # 9. Araç Yükseltme Bedeli
    st.subheader("Araç Yükseltme Bedeli")
    arac_yukseltme = st.selectbox("Yükseltilecek Aracı Seçin", arac_listesi, key="arac_yukseltme_secimi")
    yukseltme_tutari = st.number_input("Yükseltme Tutarı (USD)", min_value=0.0, step=0.01)
    if st.button("Araç Yükseltme Kaydet"):
        gider = {
            "tip": "Araç Yükseltme",
            "arac": arac_yukseltme,
            "tutar": yukseltme_tutari,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        user_data["operasyonel_giderler"].append(gider)
        st.success(f"{arac_yukseltme} için yükseltme kaydedildi.")
        st.experimental_rerun()

# ----------- Günlük Rapor -------------

def gunluk_rapor():
    st.header("Günlük Rapor")
    user_data = st.session_state.users[st.session_state.logged_in_user]

    ihaleler = user_data["ihaleler"]
    giderler = user_data["operasyonel_giderler"]

    bugun = datetime.now().date()

    bugun_ihaleler = [ih for ih in ihaleler if datetime.strptime(ih["tarih"], "%Y-%m-%d %H:%M:%S").date() == bugun]
    bugun_giderler = [g for g in giderler if datetime.strptime(g["tarih"], "%Y-%m-%d %H:%M:%S").date() == bugun]

    toplam_ihale_sayisi = len(bugun_ihaleler)
    toplam_ihale_geliri = sum(ih["ihale_bedeli"] for ih in bugun_ihaleler)
    toplam_urun_maliyeti = sum(ih["birim_urun_maliyeti"] * ih["urun_sayisi"] for ih in bugun_ihaleler)
    toplam_operasyonel_gider = sum(g["tutar"] for g in bugun_giderler)

    toplam_kar = toplam_ihale_geliri - toplam_urun_maliyeti - toplam_operasyonel_gider

    st.write(f"Günlük Toplam İhale Sayısı: **{toplam_ihale_sayisi}**")
    st.write(f"Günlük Toplam İhale Geliri: **{toplam_ihale_geliri:.2f} USD**")
    st.write(f"Günlük Ürün Maliyeti: **{toplam_urun_maliyeti:.2f} USD**")
    st.write(f"Günlük Operasyonel Maliyet: **{toplam_operasyonel_gider:.2f} USD**")
    st.write(f"Günlük Toplam Kar: **{toplam_kar:.2f} USD**")

# ----------- Grafiksel Raporlar -------------

def grafiksel_rapor():
    st.header("Raporlar")

    user_data = st.session_state.users[st.session_state.logged_in_user]
    ihaleler = pd.DataFrame(user_data["ihaleler"])
    giderler = pd.DataFrame(user_data["operasyonel_giderler"])

    if ihaleler.empty:
        st.info("Henüz ihale verisi yok.")
        return

    # Tarih filtresi
    filtre_tipi = st.radio("Raporlama Süresi Seçin", ["Günlük", "Haftalık", "Aylık"])

    def tarih_filtre(df, tarih_sutunu):
        df[tarih_sutunu] = pd.to_datetime(df[tarih_sutunu])
        bugun = pd.Timestamp.now().normalize()
        if filtre_tipi == "Günlük":
            baslangic = bugun
        elif filtre_tipi == "Haftalık":
            baslangic = bugun - pd.Timedelta(days=7)
        else:  # Aylık
            baslangic = bugun - pd.Timedelta(days=30)
        return df[df[tarih_sutunu] >= baslangic]

    ihaleler_filtered = tarih_filtre(ihaleler, "tarih")
    giderler_filtered = tarih_filtre(giderler, "tarih")

    # 1. Grafik: İhale Türü Dağılımı
    st.subheader("İhale Türü Dağılımı")
    ihale_tur_sayilari = ihaleler_filtered["ihale_turu"].value_counts()
    st.bar_chart(ihale_tur_sayilari)

    # 2. Grafik: İhale Türlerine Göre Gelirler
    st.subheader("İhale Türlerine Göre Gelirler")
    gelirler = ihaleler_filtered.groupby("ihale_turu")["ihale_bedeli"].sum()
    st.bar_chart(gelirler)

    # 3. Grafik: Operasyonel Giderlerin Dağılımı
    if not giderler_filtered.empty:
        st.subheader("Operasyonel Giderlerin Dağılımı")
        gider_tipi_toplam = giderler_filtered.groupby("tip")["tutar"].sum()
        st.bar_chart(gider_tipi_toplam)
    else:
        st.info("Henüz operasyonel gider verisi yok.")

# ----------- Ana Akış -------------

def main():
    st.title("İhale Oyunu Takip Uygulaması")

    if st.session_state.logged_in_user is None:
        secim = st.radio("Giriş veya Kayıt Ol", ["Giriş Yap", "Kayıt Ol"])
        if secim == "Giriş Yap":
            login()
        else:
            register()
    else:
        st.sidebar.title(f"Hoşgeldin, {st.session_state.logged_in_user}!")
        if st.sidebar.button("Çıkış Yap"):
            logout()

        user_data = st.session_state.users[st.session_state.logged_in_user]

        if user_data["profile"] is None:
            get_profile_info()
        else:
            sekme = st.sidebar.radio("Sekmeler", ["İhale Girişi", "Operasyonel Giderler", "Günlük Rapor", "Raporlar"])

            if sekme == "İhale Girişi":
                ihale_girisi()
            elif sekme == "Operasyonel Giderler":
                operasyonel_giderler()
            elif sekme == "Günlük Rapor":
                gunluk_rapor()
            elif sekme == "Raporlar":
                grafiksel_rapor()

if __name__ == "__main__":
    main()

