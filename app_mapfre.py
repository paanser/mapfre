
import pandas as pd
import streamlit as st

# Configuración general
st.set_page_config(page_title="Tarifa MAPFRE", layout="centered")

# Cargar tarifa MAPFRE desde archivo CSV
tarifa_df = pd.read_csv("tarifa_mapfre_completa.csv")

# Mostrar selección de producto desde la tarifa MAPFRE
producto_seleccionado = st.selectbox("Selecciona un tipo de vidrio:", tarifa_df["Descripción"])
precio_unitario = tarifa_df.query("Descripción == @producto_seleccionado")["Precio (€)"].values[0]
st.markdown(f"**Precio unitario:** {precio_unitario:.2f} €/m² o unidad")

# Medidas del vidrio
ancho = st.number_input("Introduce el ancho del vidrio (cm):", min_value=1.0, step=0.5)
largo = st.number_input("Introduce el largo del vidrio (cm):", min_value=1.0, step=0.5)

# Calcular área en m²
area_m2 = (ancho * largo) / 10000
st.markdown(f"**Área del vidrio:** {area_m2:.2f} m²")
precio_vidrio_total = round(area_m2 * precio_unitario, 2)
st.markdown(f"**Precio total del vidrio:** {precio_vidrio_total:.2f} €")

# Cálculo de canto pulido
if st.checkbox("¿Quieres calcular canto pulido?"):
    metodo_precio = st.radio("Selecciona cómo ingresar el precio del canto pulido:",
                             ["Usar tarifa MAPFRE", "Ingresar precio manualmente"])

    if metodo_precio == "Usar tarifa MAPFRE":
        filtro_pulido = tarifa_df[tarifa_df["Descripción"].str.contains("canto|pulido", case=False)]
        opcion_pulido = st.selectbox("Selecciona tipo de canto pulido:", filtro_pulido["Descripción"])
        precio_pulido = filtro_pulido.query("Descripción == @opcion_pulido")["Precio (€)"].values[0]
    else:
        precio_pulido = st.number_input("Introduce el precio manual por metro lineal (€):", min_value=0.0, step=0.1)

    # Número de lados a pulir
    cantidad_anchos = st.number_input("¿Cuántos lados anchos quieres pulir?", min_value=0, step=1)
    cantidad_largos = st.number_input("¿Cuántos lados largos quieres pulir?", min_value=0, step=1)

    # Calcular metros lineales
    ml_anchos = (ancho / 100) * cantidad_anchos
    ml_largos = (largo / 100) * cantidad_largos
    ml_total = round(ml_anchos + ml_largos, 2)

    st.markdown(f"**Metros lineales de canto pulido:** {ml_total:.2f} ml")
    total_canto_pulido = round(ml_total * precio_pulido, 2)
    st.markdown(f"**Total canto pulido:** {total_canto_pulido:.2f} €")

    # Total general
    st.markdown("---")
    st.markdown(f"**Precio total vidrio + canto pulido:** {precio_vidrio_total + total_canto_pulido:.2f} €")
