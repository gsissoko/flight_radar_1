from datetime import datetime
import pandas as pd

import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:5000"
INDICATORS_MAPPING = {
    "indicator_1": "Compagnie avec le plus de vols en cours",
    "indicator_2": "Compagnie avec le plus de vols régionaux actifs par continent",
    "indicator_3": "Vol avec le trajet le plus long en cours",
    "indicator_4": "Longueur de vol moyenne par continent",
    "indicator_5": "Constructeur d'avions avec le plus de vols actifs",
    "indicator_6": "Top 3 des modèles d'avion en usage par compagnie aérienne",
    "indicator_7": "Aéroport avec la plus grande différence entre vols sortants et entrants"
}


def start_job(execution_date=None, upload_frequency=1800, computation_frequency=1800):
    payload = {
        "initial_date": execution_date,
        "upload_frequency": upload_frequency,
        "computation_frequency": computation_frequency
    }
    response = requests.post(f"{BASE_URL}/start", json=payload)
    print(response)
    return response.json()


def stop_job():
    response = requests.put(f"{BASE_URL}/stop")
    return response.json()


def compute_indicator(indicator_name: str):
    response = requests.get(f"{BASE_URL}/indicators/{indicator_name}")
    return response.json()


st.title("Exalt - Flight Radar")

st.sidebar.header("Gestion du Job")

initial_date = st.sidebar.date_input("Date initiale", datetime.utcnow()).isoformat()
data_upload_frequency = st.sidebar.number_input("Fréquence de collecte des données de vol (en minutes)", value=30)
indicator_computation_frequency = st.sidebar.number_input("Fréquence de calcul des indicateurs (en minutes)", value=30)

if st.sidebar.button("Démarrer le Job"):
    result = start_job(initial_date, data_upload_frequency*60, indicator_computation_frequency*60)
    st.sidebar.json(result)

if st.sidebar.button("Arrêter le Job"):
    result = stop_job()
    st.sidebar.json(result)

st.header("Calcul des Indicateurs")

indicator = st.selectbox(
    "Choisir un indicateur",
    list(INDICATORS_MAPPING.keys()),
    format_func=lambda x: INDICATORS_MAPPING[x]
)

if st.button("Calculer l'indicateur"):
    result = compute_indicator(indicator)
    st.subheader(f"Résultat pour '{INDICATORS_MAPPING[indicator].lower()}':")
    if indicator not in ["indicator_2", "indicator_6"]:
        st.table([result])
    else:
        # Special case: format the result as a table with keys in the first column and values as columns
        formatted_result = {}
        for key, value_dict in result.items():
            for sub_key, sub_value in value_dict.items():
                if sub_key not in formatted_result:
                    formatted_result[sub_key] = {}
                formatted_result[sub_key][key] = sub_value

        # Convert the formatted result to a DataFrame and fill missing values with None
        df = pd.DataFrame(formatted_result).fillna("None")
        st.table(df)

