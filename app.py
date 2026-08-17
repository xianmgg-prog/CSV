import streamlit as st
import re
import pandas as pd
import pdfplumber

# Configuración de la página
st.set_page_config(page_title="Conversor A3", page_icon="💶", layout="centered")

st.title("Conversor de Extractos a CSV (A3)")
st.write("Sube tu extracto bancario en PDF para convertirlo automáticamente al formato compatible con A3.")

# Zona de subida de archivos
uploaded_file = st.file_uploader("Arrastra tu PDF aquí", type="pdf")

if uploaded_file is not None:
    with st.spinner("Procesando documento..."):
        text = ""
        # Extraer texto del PDF
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + " "
            
            cleaned_text = text.replace('\n', ' ')

            # Expresión regular para localizar los movimientos
            pattern = r"(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})\s+EUR"
            matches = re.findall(pattern, cleaned_text)
            
            if matches:
                data = []
                for m in matches:
                    f_valor, f_contable, f_operacion, desc, importe, saldo = m
                    desc = re.sub(r'\s+', ' ', desc).strip()
                    
                    data.append({
                        "Fecha": f_operacion,
                        "Concepto": desc,
                        "Importe": importe,
                        "Saldo": saldo
                    })
                    
                df = pd.DataFrame(data)
                
                st.success(f"✅ ¡Se han procesado {len(df)} movimientos con éxito!")
                st.dataframe(df, use_container_width=True)
                
                # Botón de descarga
                csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
                
                st.download_button(
                    label="⬇️ Descargar archivo CSV",
                    data=csv,
                    file_name="movimientos_A3.csv",
                    mime="text/csv",
                    type="primary"
                )
            else:
                st.error("No se encontraron movimientos. Comprueba que el formato del PDF sea el correcto.")
                
        except Exception as e:
            st.error(f"Hubo un error al leer el PDF: {e}")
