
Open In Colab

# Création du fichier app.py (version complète et propre)

code_app = """
import streamlit as st
import numpy as np

# ============================================
# CONFIGURATION DE LA PAGE
# ============================================
st.set_page_config(
    page_title="Diagnostic Paludisme",
    page_icon="🩺",
    layout="centered"
)

# ============================================
# TITRE
# ============================================
st.title("🩺 Système Expert Flou")
st.markdown("### Diagnostic du Paludisme")
st.markdown("---")

# ============================================
# FONCTIONS D'APPARTENANCE
# ============================================
def fonction_triangulaire(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

def fuzzification_temp(temp):
    return {
        'Faible': fonction_triangulaire(temp, 35, 36, 37),
        'Moyenne': fonction_triangulaire(temp, 36, 37.5, 39),
        'Élevée': fonction_triangulaire(temp, 38, 40, 42)
    }

def fuzzification_fatigue(fatigue):
    return {
        'Faible': fonction_triangulaire(fatigue, 0, 2, 4),
        'Moyenne': fonction_triangulaire(fatigue, 3, 5, 7),
        'Forte': fonction_triangulaire(fatigue, 6, 8, 10)
    }

def fuzzification_maux(maux):
    return {
        'Faible': fonction_triangulaire(maux, 0, 2, 4),
        'Moyen': fonction_triangulaire(maux, 3, 5, 7),
        'Fort': fonction_triangulaire(maux, 6, 8, 10)
    }

# ============================================
# BASE DE RÈGLES (12 règles)
# ============================================
regles_mamdani = [
    ('Élevée', 'Forte', 'Fort', 'Élevé'),
    ('Élevée', 'Forte', 'Moyen', 'Élevé'),
    ('Élevée', 'Moyenne', 'Fort', 'Élevé'),
    ('Moyenne', 'Moyenne', 'Moyen', 'Moyen'),
    ('Moyenne', 'Forte', 'Moyen', 'Moyen'),
    ('Moyenne', 'Moyenne', 'Fort', 'Moyen'),
    ('Faible', 'Faible', 'Faible', 'Faible'),
    ('Faible', 'Moyenne', 'Faible', 'Faible'),
    ('Moyenne', 'Faible', 'Faible', 'Faible'),
    ('Élevée', 'Forte', 'Faible', 'Moyen'),
    ('Faible', 'Forte', 'Fort', 'Moyen'),
    ('Moyenne', 'Forte', 'Fort', 'Élevé'),
]

regles_sugeno = [
    ('Élevée', 'Forte', 'Fort', 85),
    ('Élevée', 'Forte', 'Moyen', 85),
    ('Élevée', 'Moyenne', 'Fort', 85),
    ('Moyenne', 'Moyenne', 'Moyen', 50),
    ('Moyenne', 'Forte', 'Moyen', 50),
    ('Moyenne', 'Moyenne', 'Fort', 50),
    ('Faible', 'Faible', 'Faible', 25),
    ('Faible', 'Moyenne', 'Faible', 25),
    ('Moyenne', 'Faible', 'Faible', 25),
    ('Élevée', 'Forte', 'Faible', 50),
    ('Faible', 'Forte', 'Fort', 50),
    ('Moyenne', 'Forte', 'Fort', 85),
]

# ============================================
# INFÉRENCE MAMDANI
# ============================================
def inference_mamdani(temp, fatigue, maux):
    t_fuzz = fuzzification_temp(temp)
    f_fuzz = fuzzification_fatigue(fatigue)
    m_fuzz = fuzzification_maux(maux)

    activation = {'Faible': 0.0, 'Moyen': 0.0, 'Élevé': 0.0}

    for t_cond, f_cond, m_cond, risque in regles_mamdani:
        alpha = min(t_fuzz[t_cond], f_fuzz[f_cond], m_fuzz[m_cond])
        if alpha > 0:
            activation[risque] = max(activation[risque], alpha)

    numerateur = 20 * activation['Faible'] + 50 * activation['Moyen'] + 80 * activation['Élevé']
    denominateur = sum(activation.values())

    if denominateur == 0:
        return 0.0
    return round(numerateur / denominateur, 2)

# ============================================
# INFÉRENCE SUGENO
# ============================================
def inference_sugeno(temp, fatigue, maux):
    t_fuzz = fuzzification_temp(temp)
    f_fuzz = fuzzification_fatigue(fatigue)
    m_fuzz = fuzzification_maux(maux)

    numerateur = 0.0
    denominateur = 0.0

    for t_cond, f_cond, m_cond, valeur in regles_sugeno:
        poids = min(t_fuzz[t_cond], f_fuzz[f_cond], m_fuzz[m_cond])
        if poids > 0:
            numerateur += poids * valeur
            denominateur += poids

    if denominateur == 0:
        return 0.0
    return round(numerateur / denominateur, 2)

# ============================================
# INTERFACE UTILISATEUR
# ============================================

# Deux colonnes pour disposer les éléments
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Symptômes")

    temperature = st.slider(
        "🌡️ Température (°C)",
        min_value=35.0,
        max_value=42.0,
        value=37.5,
        step=0.1
    )

    fatigue = st.slider(
        "😴 Niveau de fatigue",
        min_value=0,
        max_value=10,
        value=5,
        step=1
    )

    maux = st.slider(
        "🤕 Maux de tête",
        min_value=0,
        max_value=10,
        value=5,
        step=1
    )

with col2:
    st.subheader("🧠 Résultats")

    # Calcul des risques
    risque_mam = inference_mamdani(temperature, fatigue, maux)
    risque_sug = inference_sugeno(temperature, fatigue, maux)

    # Affichage
    st.metric("Modèle Mamdani", f"{risque_mam}%")
    st.metric("Modèle Sugeno", f"{risque_sug}%")

    st.markdown("---")

    # Interprétation avec couleur
    if risque_mam < 40:
        st.success("✅ **Risque : FAIBLE**")
        st.caption("Pas d'inquiétude immédiate.")
    elif risque_mam < 70:
        st.warning("⚠️ **Risque : MOYEN**")
        st.caption("Surveillance recommandée.")
    else:
        st.error("🔴 **Risque : ÉLEVÉ**")
        st.caption("Consultation médicale recommandée.")

# Pied de page
st.markdown("---")
st.caption("Application développée avec Streamlit | Modèles Mamdani & Sugeno")
"""

# Écrire le fichier
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code_app)

print("✅ Fichier 'app.py' créé avec succès !")
print("\n📁 Vérification :")
!ls -la app.py
     
✅ Fichier 'app.py' créé avec succès !

📁 Vérification :
-rw-r--r-- 1 root root 5610 Aug 10 07:20 app.py

# Installation de Streamlit et ngrok
print("📦 Installation de Streamlit...")
!pip install streamlit -q

print("📦 Installation de ngrok...")
!wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
!tar -xzf ngrok-v3-stable-linux-amd64.tgz

print("✅ Tous les outils sont installés !")
     
📦 Installation de Streamlit...
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.5/10.5 MB 33.1 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.4/11.4 MB 52.7 MB/s eta 0:00:00
📦 Installation de ngrok...
✅ Tous les outils sont installés !

# === REMPLACE TON_TOKEN_ICI PAR TON VRAI TOKEN ===
NGROK_TOKEN = "3F2N4EwocL37jD4TjG6f7Yv2BI0_5JKf8jJnJGaG3tgeEtPUp"  # ← MODIFIE ICI !

# Configurer ngrok
!./ngrok config add-authtoken {NGROK_TOKEN}

print("✅ ngrok configuré !")
     
Authtoken saved to configuration file: /root/.config/ngrok/ngrok.yml
✅ ngrok configuré !

import subprocess
import os
import time
import threading

print("🚀 DÉMARRAGE DE L'APPLICATION")
print("="*50)

# 1. Démarrer Streamlit en arrière-plan
def run_streamlit():
    os.system("streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true")

thread = threading.Thread(target=run_streamlit)
thread.start()

print("⏳ Démarrage de Streamlit...")
time.sleep(8)

# 2. Démarrer ngrok
print("⏳ Démarrage du tunnel ngrok...")
os.system("./ngrok http 8501 --log=stdout > ngrok.log &")
time.sleep(5)

# 3. Récupérer le lien public
import re
with open('ngrok.log', 'r') as f:
    log = f.read()
    urls = re.findall(r'https://[a-z0-9-]+\.ngrok\.io', log)
    if urls:
        public_url = urls[0]
        print("\n" + "="*60)
        print("🎉 SUCCÈS ! L'application est en ligne !")
        print("="*60)
        print(f"\n📱 LIEN POUR TON TÉLÉPHONE :")
        print(f"\n   {public_url}")
        print("\n" + "="*60)
        print("👉 Ouvre ce lien sur le navigateur de ton téléphone")
        print("👉 L'application doit s'afficher")
        print("="*60)
    else:
        print("\n⚠️ En attente du lien...")
        print("Attends 10 secondes puis exécute la cellule ci-dessous")
     
🚀 DÉMARRAGE DE L'APPLICATION
==================================================
⏳ Démarrage de Streamlit...
⏳ Démarrage du tunnel ngrok...

⚠️ En attente du lien...
Attends 10 secondes puis exécute la cellule ci-dessous


     

# Récupérer le lien manuellement
import re
import time

time.sleep(3)

try:
    with open('ngrok.log', 'r') as f:
        log = f.read()
        print("=== DERNIÈRES LIGNES DU LOG ===")
        print(log[-500:])

        urls = re.findall(r'https://[a-z0-9-]+\.ngrok\.io', log)
        if urls:
            print("\n" + "="*50)
            print(f"✅ LIEN : {urls[0]}")
            print("="*50)
        else:
            print("\n❌ Lien non trouvé. Vérifie que ton token ngrok est correct.")
except:
    print("❌ Fichier log non trouvé. Réessaie.")
     
=== DERNIÈRES LIGNES DU LOG ===
07:20:40+0000 lvl=info msg="FIPS 140 mode" enabled=false
t=2026-08-10T07:20:40+0000 lvl=info msg="starting web service" obj=web addr=127.0.0.1:4040 allow_hosts=[]
t=2026-08-10T07:20:40+0000 lvl=info msg="client session established" obj=tunnels.session
t=2026-08-10T07:20:40+0000 lvl=info msg="tunnel session started" obj=tunnels.session
t=2026-08-10T07:20:40+0000 lvl=info msg="started tunnel" obj=tunnels name=command_line addr=http://localhost:8501 url=https://zookeeper-pronto-ship.ngrok-free.dev


❌ Lien non trouvé. Vérifie que ton token ngrok est correct.

# Nettoyage complet
import os
os.system("pkill -f streamlit 2>/dev/null")
os.system("pkill -f ngrok 2>/dev/null")
print("✅ Nettoyé")
     
✅ Nettoyé

# Lancement simplifié
import subprocess
import os
import time
import threading

print("🚀 Lancement...")

# Lancer Streamlit
def run_streamlit():
    os.system("streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true")

thread = threading.Thread(target=run_streamlit)
thread.start()
time.sleep(6)

# Lancer ngrok
os.system("./ngrok http 8501 > ngrok.log 2>&1 &")
time.sleep(4)

print("✅ En attente du lien...")
     
🚀 Lancement...
✅ En attente du lien...

import requests
import time

for i in range(10):
    time.sleep(2)
    try:
        r = requests.get('http://localhost:4040/api/tunnels')
        data = r.json()
        if data.get('tunnels'):
            url = data['tunnels'][0]['public_url']
            print("\n" + "="*60)
            print(f"🎉 {url}")
            print("="*60)
            print("\n📱 Ouvre ce lien sur ton téléphone !")
            break
    except:
        print(f"Essai {i+1}/10 - En attente...")
     
============================================================
🎉 https://zookeeper-pronto-ship.ngrok-free.dev
============================================================

📱 Ouvre ce lien sur ton téléphone !
