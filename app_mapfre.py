
import pandas as pd
import streamlit as st
import math

st.set_page_config(page_title="Tarifa MAPFRE", layout="centered")
st.title("Calculadora Vidre  - Tarifa MAPFRE - Entrada en Metros")

# Cargar tarifa MAPFRE y tabla de múltiplos externa
tarifa_df = pd.read_csv("tarifa_mapfre_completa.csv")
tabla_multiplos = pd.read_csv("tabla_multiplos_6x6_hasta_5m.csv", index_col=0)
tabla_multiplos.columns = tabla_multiplos.columns.astype(float)
tabla_multiplos.index = tabla_multiplos.index.astype(float)

# Paso 1: Entrada de medidas en metros
st.header("1. Medidas del vidrio (en metros)")
ancho_m = st.number_input("Introduce el ancho del vidrio (m):", min_value=0.01, step=0.01)
alto_m = st.number_input("Introduce el alto del vidrio (m):", min_value=0.01, step=0.01)

# Convertir a cm
ancho_cm = ancho_m * 100
alto_cm = alto_m * 100

# Área real
area_real = (ancho_cm * alto_cm) / 10000
st.markdown(f"**Área real (m²):** {area_real:.2f}")

# Paso 2: Ajustar al siguiente múltiplo de 6 cm
def siguiente_multiplo(valor):
    return math.ceil(valor / 6) * 6

ancho_corr = siguiente_multiplo(ancho_cm)
alto_corr = siguiente_multiplo(alto_cm)

# Área corregida según tabla real
try:
    area_corregida = float(tabla_multiplos.loc[ancho_corr, alto_corr])
except KeyError:
    st.error("Las medidas están fuera del rango de la tabla de múltiplos (24 cm a 504 cm).")
    st.stop()

st.markdown(f"**Medidas ajustadas:** {ancho_corr} cm × {alto_corr} cm")
st.markdown(f"**Área corregida (m²):** {area_corregida:.2f}")
if area_corregida < 0.5:
    st.warning("Aviso: el área corregida es inferior a 0.5 m²")

# Paso 3: Selección de tarifa o precio manual
st.header("2. Selección del vidrio")
metodo = st.radio("¿Deseas introducir el precio manual o seleccionar desde tarifa MAPFRE?",
                  ["Seleccionar desde tarifa MAPFRE", "Introducir precio manual"])

if metodo == "Seleccionar desde tarifa MAPFRE":
    seleccion = st.selectbox("Selecciona el tipo de vidrio:", tarifa_df["Descripción"])
    precio_m2 = tarifa_df.query("Descripción == @seleccion")["Precio (€)"].values[0]
else:
    precio_m2 = st.number_input("Introduce el precio manual por m² (€):", min_value=0.0, step=0.1)

# Cálculo del precio total
precio_total = round(precio_m2 * area_corregida, 2)
st.markdown(f"**Precio por m²:** {precio_m2:.2f} €")
st.markdown(f"### **Precio total del vidrio:** {precio_total:.2f} €")



# Sección: Cálculo de canto pulido
st.header("¿Deseas añadir canto pulido?")
total_canto_pulido = 0

if st.checkbox("Añadir canto pulido"):
    metodo_canto = st.radio("¿Cómo deseas calcular el precio del canto pulido?",
                            ["Seleccionar desde tarifa MAPFRE", "Precio manual"])

    if metodo_canto == "Seleccionar desde tarifa MAPFRE":
        filtro_canto = tarifa_df[tarifa_df["Descripción"].str.contains("canto pulido", case=False)]
        seleccion_canto = st.selectbox("Selecciona el tipo de canto pulido:", filtro_canto["Descripción"])
        precio_canto = filtro_canto.query("Descripción == @seleccion_canto")["Precio (€)"].values[0]
    else:
        precio_canto = st.number_input("Introduce el precio por metro lineal (€):", min_value=0.0, step=0.1)

    st.subheader("Introduce cuántos lados quieres pulir")
    lados_anchos = st.number_input("Cantidad de lados anchos a pulir", min_value=0, step=1)
    lados_largos = st.number_input("Cantidad de lados largos a pulir", min_value=0, step=1)

    # Asumimos que las variables ancho_cm y alto_cm ya fueron definidas como cm reales o convertidos
    ml_anchos = (ancho_cm / 100) * lados_anchos
    ml_largos = (alto_cm / 100) * lados_largos
    ml_total = round(ml_anchos + ml_largos, 2)

    total_canto_pulido = round(ml_total * precio_canto, 2)
    st.markdown(f"**Total de metros lineales pulidos:** {ml_total:.2f} ml")
    st.markdown(f"**Total canto pulido:** {total_canto_pulido:.2f} €")



# Sección final: resumen total del presupuesto con IVA
st.header("Resumen total del presupuesto")

precio_vidrio = precio_total if 'precio_total' in locals() else 0
precio_canto = total_canto_pulido if 'total_canto_pulido' in locals() else 0
subtotal = round(precio_vidrio + precio_canto, 2)
iva = round(subtotal * 0.21, 2)
total_con_iva = round(subtotal + iva, 2)

st.markdown(f"**Subtotal (sin IVA):** {subtotal:.2f} €")
st.markdown(f"**IVA (21%):** {iva:.2f} €")
st.markdown(f"### **TOTAL CON IVA: {total_con_iva:.2f} €**")
