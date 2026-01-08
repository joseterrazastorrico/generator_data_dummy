import streamlit as st
import requests
import pandas as pd
import json

def main():
    st.title("Generador de Datos Dummy")
    
    st.sidebar.header("Configuración Global")
    start = st.sidebar.text_input("Fecha de inicio", "2025-01-01 00:00:00")
    end = st.sidebar.text_input("Fecha de fin", "2025-01-02 00:00:00")
    frequency = st.sidebar.text_input("Frecuencia de muestreo", "5min")
    filename = st.sidebar.text_input("Nombre del archivo a guardar", "")
    
    st.sidebar.header("Configuración de Variables")
    input_method = st.sidebar.radio("Método de entrada", ["Manual", "Cargar JSON"])
    
    variables = []
    
    if input_method == "Manual":
        num_vars = st.sidebar.number_input("Número de Variables", min_value=1, max_value=10, value=1)
        
        for i in range(num_vars):
            with st.expander(f"Variable {i+1}"):
                name = st.text_input(f"Nombre de la variable {i+1}", f"Variable_{i+1}")
                min_value = st.number_input(f"Valor mínimo {i+1}", value=0.0)
                max_value = st.number_input(f"Valor máximo {i+1}", value=100.0)
                mean_value = st.number_input(f"Valor promedio {i+1}", value=(min_value + max_value) / 2)
                distribution = st.selectbox(f"Distribución {i+1}", ["normal", "uniform", "poisson", "binary"])
                
                variables.append({
                    "name": name,
                    "min_value": min_value,
                    "max_value": max_value,
                    "mean_value": mean_value,
                    "start": start,
                    "end": end,
                    "distribution": distribution,
                    "frequency": frequency
                })
    elif input_method == "Cargar JSON":
        uploaded_file = st.file_uploader("Subir archivo JSON", type=["json"])
        if uploaded_file is not None:
            try:
                variables = json.load(uploaded_file)
                st.success("Archivo JSON cargado correctamente")
            except Exception as e:
                st.error(f"Error al cargar el archivo JSON: {e}")
        else:
            example_json = """
                    [
                        {
                            "name": "Variable_1",
                            "min_value": 0.0,
                            "max_value": 100.0,
                            "mean_value": 50.0,
                            "start": "2025-01-01 00:00:00",
                            "end": "2025-01-02 00:00:00",
                            "distribution": "normal",
                            "frequency": "5min"
                        },
                        {
                            "name": "Variable_2",
                            "min_value": 10.0,
                            "max_value": 200.0,
                            "mean_value": 105.0,
                            "start": "2025-01-01 00:00:00",
                            "end": "2025-01-02 00:00:00",
                            "distribution": "uniform",
                            "frequency": "5min"
                        }
                    ]
                    """
            json_input = st.text_area("O escribir JSON manualmente", placeholder=example_json.strip())
            if json_input:
                try:
                    variables = json.loads(json_input)
                    st.success("JSON cargado correctamente")
                except Exception as e:
                    st.error(f"Error al procesar el JSON: {e}")
    
    if st.button("Generar Datos"):
        if not variables:
            st.error("No se han definido variables")
            return
        
        response = requests.post("http://localhost:8080/generate_data/", json=variables)
        print(response)
        if response.status_code == 200:
            data = response.json()
            st.write("Muestra de datos generados:")
            data = pd.DataFrame(data)
            st.table(data.head(7))
            data.to_parquet(f'{filename}.parquet')
        else:
            st.error("Error al generar los datos")

if __name__ == "__main__":
    main()