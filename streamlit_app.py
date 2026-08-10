"""
Interface web (Streamlit) du prototype pedagogique de systeme expert flou
pour l'estimation du risque de paludisme - modeles de Mamdani et Sugeno.

AVERTISSEMENT : ceci est un prototype pedagogique. Il ne remplace pas un
diagnostic medical et ne doit jamais etre utilise pour une decision clinique.

Lancement local : streamlit run streamlit_app.py
Deploiement     : Streamlit Community Cloud (share.streamlit.io), en connectant
                  le depot GitHub contenant ce fichier + requirements.txt.
"""

import streamlit as st
from fuzzy_paludisme import inference_mamdani, inference_sugeno

st.set_page_config(page_title="Système expert flou - Paludisme (prototype)", page_icon="🩺")

st.title("🩺 Prototype flou d'estimation du risque de paludisme")
st.warning(
    "**Prototype pédagogique** — ce système illustre les modèles de Mamdani et de "
    "Sugeno vus en cours de logique floue. Il n'a pas été validé médicalement et "
    "ne doit **pas** être utilisé pour un diagnostic réel."
)

col1, col2, col3 = st.columns(3)
with col1:
    temp = st.slider("Température corporelle (°C)", 35.0, 42.0, 38.0, 0.1)
with col2:
    fatigue = st.slider("Niveau de fatigue (0-10)", 0.0, 10.0, 5.0, 0.5)
with col3:
    maux = st.slider("Intensité des maux de tête (0-10)", 0.0, 10.0, 5.0, 0.5)

risque_mamdani, activations = inference_mamdani(temp, fatigue, maux)
risque_sugeno = inference_sugeno(temp, fatigue, maux)

c1, c2 = st.columns(2)
c1.metric("Risque estimé — Mamdani", f"{risque_mamdani:.1f} %")
c2.metric("Risque estimé — Sugeno", f"{risque_sugeno:.1f} %")

st.caption(
    f"Degrés d'activation par niveau (Mamdani) : "
    f"Faible={activations['Faible']:.2f}, Moyen={activations['Moyen']:.2f}, "
    f"Élevé={activations['Élevé']:.2f}"
)

st.divider()
st.markdown(
    "Code source et rapport complet : voir le [dépôt GitHub du projet]"
    "(https://github.com/<votre-compte>/paludisme-flou)."
)
