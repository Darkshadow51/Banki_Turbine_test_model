import math
import pandas as pd
import streamlit as st

# Nastavenie stránky
st.set_page_config(
    page_title="Matematický model Bankiho turbíny", page_icon="⚙️", layout="wide"
)

st.title("⚙️ Matematický model Bankiho turbíny")
st.markdown(
    "Interaktívny simulačný nástroj pre bakalársku prácu na návrh a overenie"
    " parametrov krížovej (Bankiho) turbíny."
)

# Sidebar - Výber režimu a vstupné parametre
st.sidebar.header("🎛️ Ovládací panel")
rezim = st.sidebar.radio(
    "Zvoľ režim výpočtu:",
    [
        "1. Návrhový režim (Výpočet ideálneho kolesa)",
        "2. Overovací režim (Test existujúceho kolesa)",
    ],
)

st.sidebar.subheader("Hydraulické vstupy")
H = st.sidebar.number_input(
    "Čistý spád H [m]", min_value=0.5, max_value=200.0, value=10.0, step=0.5
)
Q = st.sidebar.number_input(
    "Prietok Q [m³/s]", min_value=0.01, max_value=50.0, value=0.15, step=0.01
)
eta_percent = st.sidebar.slider("Predpokladaná účinnosť η [%]", 50, 90, 78, 1)
eta = eta_percent / 100.0

g = 9.81  # Gravitačné zrýchlenie

# Fyzikálne výpočty
P_teor_W = 1000 * g * Q * H
P_vykon_kW = P_teor_W * eta / 1000
u1_ideal = 0.45 * math.sqrt(2 * g * H)

if rezim == "1. Návrhový režim (Výpočet ideálneho kolesa)":
  st.subheader("📊 Výsledky návrhu pre zadaný spád a prietok")

  col1, col2, col3 = st.columns(3)
  col1.metric("Využiteľný výkon", f"{P_vykon_kW:.2f} kW")
  col2.metric("Teoretický príkon", f"{P_teor_W / 1000:.2f} kW")
  col3.metric("Ideálna obvodová rýchlost", f"{u1_ideal:.2f} m/s")

  st.markdown("---")
  st.write("### 📐 Odporúčaná geometria rotora a prevádzka:")

  D1_opt = 0.38 * (Q**0.25) / (H**0.12)
  if D1_opt < 0.1:
    D1_opt = 0.15

  B_opt = Q / (0.6 * math.sqrt(2 * g * H) * 0.1)
  if B_opt < 0.05:
    B_opt = 0.1
  if B_opt > 1.5:
    B_opt = 1.0

  n_opt = (60 * u1_ideal) / (math.pi * D1_opt)

  col_a, col_b, col_c = st.columns(3)
  col_a.metric("Optimum priemeru (D₁)", f"{D1_opt * 1000:.1f} mm")
  col_b.metric("Optimum šírky rotora (B)", f"{B_opt * 1000:.1f} mm")
  col_c.metric("Optimum otáčok (n)", f"{n_opt:.1f} RPM")

  st.info(
      "💡 **Tip pre bakalársku prácu:** Tieto hodnoty môžeš použiť ako"
      " počiatočný teoretický návrh."
  )

else:
  st.subheader("🔍 Overovací režim pre špecifické koleso")
  st.sidebar.subheader("Rozmery existujúceho kolesa")

  D1_zadany = (
      st.sidebar.number_input(
          "Vonkajší priemer kolesa D₁ [mm]",
          min_value=50,
          max_value=2000,
          value=300,
          step=10,
      )
      / 1000.0
  )
  B_zadany = (
      st.sidebar.number_input(
          "Šírka kolesa B [mm]",
          min_value=50,
          max_value=2000,
          value=200,
          step=10,
      )
      / 1000.0
  )

  n_skutocne = (60 * u1_ideal) / (math.pi * D1_zadany)
  u1_skutocne = (math.pi * D1_zadany * n_skutocne) / 60.0

  col1, col2, col3 = st.columns(3)
  col1.metric("Využiteľný výkon", f"{P_vykon_kW:.2f} kW")
  col2.metric("Ideálne otáčky pre toto koleso", f"{n_skutocne:.1f} RPM")
  col3.metric("Obvodová rýchlosť", f"{u1_skutocne:.2f} m/s")

  st.markdown("### 📋 Analýza prispôsobenia kolesa:")
  if Q > (B_zadany * D1_zadany * 2.0):
    st.warning(
        "⚠️ **Upozornenie:** Zadaný prietok môže byť pre zvolené rozmery kolesa"
        " príliš vysoký."
    )
  else:
    st.success(
        "✅ **Stav:** Zvolené rozmery kolesa sú pre daný prietok a spád"
        " hydraulicky vyhovujúce."
    )

st.markdown("---")
st.subheader("📈 Ukážka závislosti výkonu od prietoku")
if st.checkbox("Zobraziť simulačný graf pre rôzne prietoky"):
  prietoky = [i * 0.02 for i in range(1, 26)]
  vykony = [1000 * g * q * H * eta / 1000 for q in prietoky]
  df_graf = pd.DataFrame({"Prietok [m³/s]": prietoky, "Výkon [kW]": vykony})
  st.line_chart(df_graf.set_index("Prietok [m³/s]"))