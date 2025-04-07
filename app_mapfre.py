
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tarifa MAPFRE", layout="centered")
st.title("Calculadora de Vidrios - Tarifa MAPFRE")

# Cargar tarifa MAPFRE
tarifa_df = pd.read_csv("tarifa_mapfre_completa.csv")

# Tabla de múltiplos de ejemplo (extiéndela con los valores reales)
anchos = [24, 30, 36, 42, 48]
largos = [24, 30, 36, 42, 48]
valores = [
    [0.06, 0.07, 0.09, 0.10, 0.12],
    [0.07, 0.09, 0.11, 0.13, 0.14],
    [0.09, 0.11, 0.13, 0.15, 0.17],
    [0.10, 0.13, 0.15, 0.18, 0.20],
    [0.12, 0.14, 0.17, 0.20, 0.23],
]
tabla_multiplos = pd.DataFrame(valores, index=anchos, columns=largos)

def buscar_area_corregida(ancho_cm, largo_cm):
    ancho_mult = min([m for m in tabla_multiplos.index if m >= ancho_cm], default=None)
    largo_mult = min([m for m in tabla_multiplos.columns if m >= largo_cm], default=None)

    if ancho_mult is None or largo_mult is None:
        return None, "Medida fuera del rango de la tabla de múltiplos."

    area_corregida = tabla_multiplos.loc[ancho_mult, largo_mult]
    aviso = "Aviso: área corregida inferior a 0.5 m²" if area_corregida < 0.5 else ""
    return area_corregida, aviso

# 1. Medidas
st.header("1. Medidas del vidrio")
ancho = st.number_input("Introduce el ancho del vidrio (cm):", min_value=1.0, step=0.5)
largo = st.number_input("Introduce el largo del vidrio (cm):", min_value=1.0, step=0.5)

area_corregida, aviso = buscar_area_corregida(ancho, largo)
if area_corregida:
    st.markdown(f"**Área corregida según múltiplos:** {area_corregida:.2f} m²")
    if aviso:
        st.warning(aviso)
else:
    st.error(aviso)
    st.stop()

# 2. Precio del vidrio
st.header("2. Precio del vidrio")
metodo_precio_vidrio = st.radio("¿Cómo deseas introducir el precio del vidrio?", ["Usar tarifa MAPFRE", "Introducir precio manualmente"])

if metodo_precio_vidrio == "Usar tarifa MAPFRE":
    producto_seleccionado = st.selectbox("Selecciona un tipo de vidrio:", tarifa_df["Descripción"])
    precio_unitario = tarifa_df.query("Descripción == @producto_seleccionado")["Precio (€)"].values[0]
else:
    precio_unitario = st.number_input("Introduce el precio manual por m² (€):", min_value=0.0, step=0.1)

st.markdown(f"**Precio unitario:** {precio_unitario:.2f} €/m²")
precio_vidrio_total = round(area_corregida * precio_unitario, 2)
st.markdown(f"**Precio total del vidrio:** {precio_vidrio_total:.2f} €")

# 3. Canto pulido
st.header("3. Cálculo de canto pulido")
total_canto_pulido = 0.0

if st.checkbox("¿Quieres añadir canto pulido?"):
    cantidad_anchos = st.number_input("¿Cuántos lados anchos quieres pulir?", min_value=0, step=1)
    cantidad_largos = st.number_input("¿Cuántos lados largos quieres pulir?", min_value=0, step=1)

    metodo_precio_pulido = st.radio("¿Cómo deseas calcular el precio del canto pulido?", ["Usar tarifa MAPFRE", "Introducir precio manualmente"])

    if metodo_precio_pulido == "Usar tarifa MAPFRE":
        filtro_pulido = tarifa_df[tarifa_df["Descripción"].str.contains("canto|pulido", case=False)]
        opcion_pulido = st.selectbox("Selecciona tipo de canto pulido:", filtro_pulido["Descripción"])
        precio_pulido = filtro_pulido.query("Descripción == @opcion_pulido")["Precio (€)"].values[0]
    else:
        precio_pulido = st.number_input("Introduce el precio por metro lineal (€):", min_value=0.0, step=0.1)

    ml_total = round((ancho / 100) * cantidad_anchos + (largo / 100) * cantidad_largos, 2)
    total_canto_pulido = round(ml_total * precio_pulido, 2)

    st.markdown(f"**Metros lineales a pulir:** {ml_total:.2f} ml")
    st.markdown(f"**Total canto pulido:** {total_canto_pulido:.2f} €")

# 4. Total
st.header("4. Total presupuesto")
precio_total = precio_vidrio_total + total_canto_pulido
st.markdown(f"### **Total presupuesto: {precio_total:.2f} €**")
