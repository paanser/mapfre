import pandas as pd

# Cargar tarifa MAPFRE desde archivo CSV
tarifa_df = pd.read_csv("tarifa_mapfre_completa.csv")
tarifa = dict(zip(tarifa_df["Descripción"], tarifa_df["Precio (€)"]))

import streamlit as st

# --------------------------
# CONFIGURACIÓN GENERAL
# --------------------------
st.set_page_config(page_title="Calculador Vidrio Reuglass", layout="centered")

# Tabla de múltiplos de 6 (en cm)
multiplos = [i for i in range(24, 250, 6)]

# Tarifa completa extraída del PDF
def ajustar_a_multiplo(valor_m):
    """Redondea hacia arriba al múltiplo de 6 cm más cercano"""
    valor_cm = valor_m * 100
    for m in multiplos:
        if valor_cm <= m:
            return m / 100
    return multiplos[-1] / 100  # Valor máximo

# --------------------------
# ENTRADA DE MEDIDAS
# --------------------------
st.title("Calculador de Vidrio - Reuglass")
st.header("Paso 1: Medidas del vidrio")

ancho = st.number_input("Ancho del vidrio (en metros)", min_value=0.01, step=0.01)
alto = st.number_input("Alto del vidrio (en metros)", min_value=0.01, step=0.01)

if ancho and alto:
    m2_real = round(ancho * alto, 3)
    ancho_ajustado = ajustar_a_multiplo(ancho)
    alto_ajustado = ajustar_a_multiplo(alto)
    m2_ajustado = round(ancho_ajustado * alto_ajustado, 3)

    st.success(f"Área real: {m2_real} m²")
    st.info(f"Medidas ajustadas: {ancho_ajustado} m x {alto_ajustado} m")
    st.success(f"Área ajustada: {m2_ajustado} m²")

    # --------------------------
    # SELECCIÓN DE PRECIO
    # --------------------------
    st.header("Paso 2: Precio por metro cuadrado")

    metodo_precio = st.radio("Selecciona cómo quieres introducir el precio:", ["Manual", "Por tarifa"])

    if metodo_precio == "Manual":
        st.markdown("### Guía rápida (tarifa 1610 SOSA)")
        for k, v in tarifa.items():
            st.markdown(f"- **{k}**: {v} €/m²")
        precio_m2 = st.number_input("Introduce el precio manualmente (€/m²)", min_value=0.0, step=0.10)
    else:
        seleccion = st.selectbox("Selecciona el tipo de vidrio", list(tarifa.keys()))
        precio_m2 = tarifa[seleccion]
        st.success(f"Precio según tarifa: {precio_m2} €/m²")

    if precio_m2 > 0:
        precio_cristal = round(precio_m2 * m2_ajustado, 2)
        st.success(f"**Precio del vidrio:** {precio_cristal} €")

        # --------------------------
        # CANTO PULIDO DETALLADO
        # --------------------------
        st.header("Paso 3: ¿Deseas añadir canto pulido?")
        activar_canto = st.checkbox("Sí, quiero calcular el canto pulido")

        precio_canto = 0

        if activar_canto:
            lados = st.slider("¿Cuántos lados deseas pulir?", 1, 4, 2)
            precio_lineal = st.number_input("Introduce el precio por metro lineal de pulido (€)", min_value=0.0)

            perimetro_total = 0
            if lados == 1:
                perimetro_total = ancho_ajustado
            elif lados == 2:
                perimetro_total = ancho_ajustado + alto_ajustado
            elif lados == 3:
                perimetro_total = ancho_ajustado * 2 + alto_ajustado
            else:
                perimetro_total = (ancho_ajustado + alto_ajustado) * 2

            precio_canto = round(perimetro_total * precio_lineal, 2)
            st.success(f"Canto pulido: {perimetro_total:.2f} m x {precio_lineal} €/ml = {precio_canto} €")

        # --------------------------
        # MARGEN / INCREMENTO
        # --------------------------
        st.header("Paso 4: Margen (opcional)")
        margen = st.number_input("Porcentaje de incremento (%)", min_value=0.0, max_value=100.0, value=0.0)

        subtotal = precio_cristal + precio_canto
        total_final = round(subtotal * (1 + margen / 100), 2)

        # --------------------------
        # RESULTADO FINAL
        # --------------------------
        st.header("Resultado final")
        st.write(f"Precio del cristal: **{precio_cristal} €**")
        st.write(f"Precio del canto pulido: **{precio_canto} €**")
        st.write(f"Subtotal sin margen: **{subtotal} €**")
        if margen > 0:
            st.write(f"Margen aplicado: {margen}%")
        st.success(f"**Total final: {total_final} €**")
