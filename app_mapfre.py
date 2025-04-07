
import pandas as pd
import streamlit as st
import math

st.set_page_config(page_title="Tarifa MAPFRE", layout="centered")
st.title("Calculadora de Vidrios - Flujo con Múltiplos + Extras")

# Cargar tarifa MAPFRE
tarifa_df = pd.read_csv("tarifa_mapfre_completa.csv")

# 1. Medidas reales
st.header("1. Medidas del vidrio")
ancho = st.number_input("Ancho (cm):", min_value=1.0, step=0.5)
alto = st.number_input("Alto (cm):", min_value=1.0, step=0.5)

area_real = (ancho * alto) / 10000
st.markdown(f"**Área real (m²):** {area_real:.2f}")

# 2. Ajuste a múltiplos de 6
def siguiente_multiplo_6(valor):
    return math.ceil(valor / 6) * 6

ancho_corr = siguiente_multiplo_6(ancho)
alto_corr = siguiente_multiplo_6(alto)
area_corr = (ancho_corr * alto_corr) / 10000

st.markdown(f"**Medidas corregidas:** {ancho_corr} cm × {alto_corr} cm")
st.markdown(f"**Área corregida (m²):** {area_corr:.2f}")
if area_corr < 0.5:
    st.warning("Aviso: el área corregida es inferior a 0.5 m²")

# 3. Selección de vidrio principal
st.header("2. Precio del vidrio")
metodo = st.radio("¿Cómo deseas introducir el precio del vidrio?", ["Seleccionar desde tarifa MAPFRE", "Precio manual"])
if metodo == "Seleccionar desde tarifa MAPFRE":
    seleccion = st.selectbox("Selecciona el tipo de vidrio:", tarifa_df["Descripción"])
    precio_vidrio = tarifa_df.query("Descripción == @seleccion")["Precio (€)"].values[0]
else:
    precio_vidrio = st.number_input("Introduce el precio por m² (€):", min_value=0.0, step=0.1)

total_vidrio = round(area_corr * precio_vidrio, 2)
st.markdown(f"**Total vidrio:** {total_vidrio:.2f} €")

# 4. Cálculo de canto pulido
total_canto = 0
st.header("3. ¿Deseas añadir canto pulido?")
if st.checkbox("Añadir canto pulido"):
    cantidad_anchos = st.number_input("¿Cuántos lados anchos quieres pulir?", min_value=0, step=1)
    cantidad_largos = st.number_input("¿Cuántos lados largos quieres pulir?", min_value=0, step=1)

    metodo_canto = st.radio("¿Cómo deseas calcular el precio del canto pulido?",
                             ["Seleccionar desde tarifa MAPFRE", "Precio manual"])
    if metodo_canto == "Seleccionar desde tarifa MAPFRE":
        filtro_canto = tarifa_df[tarifa_df["Descripción"].str.contains("canto|pulido", case=False)]
        tipo_canto = st.selectbox("Selecciona el tipo de canto pulido:", filtro_canto["Descripción"])
        precio_ml = filtro_canto.query("Descripción == @tipo_canto")["Precio (€)"].values[0]
    else:
        precio_ml = st.number_input("Introduce el precio por metro lineal (€):", min_value=0.0, step=0.1)

    ml_total = round((ancho / 100) * cantidad_anchos + (alto / 100) * cantidad_largos, 2)
    total_canto = round(ml_total * precio_ml, 2)
    st.markdown(f"**Metros lineales a pulir:** {ml_total:.2f} ml")
    st.markdown(f"**Total canto pulido:** {total_canto:.2f} €")

# 5. Códigos adicionales
st.header("4. ¿Deseas añadir más conceptos desde la tarifa?")
adicionales = []
total_adicionales = 0

while st.checkbox("Añadir un nuevo concepto adicional"):
    item = st.selectbox("Selecciona un concepto adicional:", tarifa_df["Descripción"], key=f"extra_{len(adicionales)}")
    cantidad = st.number_input("Cantidad:", min_value=0.0, step=0.1, key=f"cantidad_{len(adicionales)}")
    precio_unit = tarifa_df.query("Descripción == @item")["Precio (€)"].values[0]
    subtotal = round(precio_unit * cantidad, 2)
    adicionales.append((item, cantidad, precio_unit, subtotal))
    total_adicionales += subtotal
    st.markdown(f"**Subtotal:** {subtotal:.2f} €")

# 6. Resumen total
st.header("5. Total del presupuesto")
total = total_vidrio + total_canto + total_adicionales
st.markdown(f"**Vidrio:** {total_vidrio:.2f} €")
if total_canto:
    st.markdown(f"**Canto pulido:** {total_canto:.2f} €")
if total_adicionales:
    st.markdown(f"**Adicionales:** {total_adicionales:.2f} €")
st.markdown(f"### **Total general: {total:.2f} €**")
