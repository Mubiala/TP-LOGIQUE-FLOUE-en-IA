# -*- coding: utf-8 -*-
"""
SYSTEME EXPERT FLOU POUR L'AIDE A L'ESTIMATION DU RISQUE DE PALUDISME (PROTOTYPE PEDAGOGIQUE)
Modeles de Mamdani (centroide reel par integration numerique) et Sugeno
Implementation manuelle - sans bibliotheque d'inference floue (scikit-fuzzy, etc.)

Auteurs : MUBIALA KIESE SAMUEL, LUVETO DIALUNGANA SALOMON, WABA MPWO EXAUCE
Version corrigee suite aux remarques de l'assistant :
  1) Le modele de Mamdani utilise desormais un VRAI centre de gravite
     (integration numerique sur l'univers de sortie [0,100]), et non une
     simple moyenne ponderee de 3 valeurs fixes (20, 50, 80).
  2) Tous les resultats numeriques du rapport sont regeneres directement
     par ce script -> reproductibilite garantie.
  3) Etude comparative etendue (nombreux scenarios + analyse de sensibilite
     + comparaison des temps d'execution) au lieu de 5 cas isoles.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import time
import random

# ============================================================================
# 1. FONCTIONS D'APPARTENANCE (TRIANGULAIRES)
# ============================================================================

def fonction_triangulaire(x, a, b, c):
    """Fonction d'appartenance triangulaire (degre entre 0 et 1)."""
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:  # b < x < c
        return (c - x) / (c - b)


PARAMS_TEMP = {'Faible': (35, 36, 37), 'Moyenne': (36, 37.5, 39), 'Élevée': (38, 40, 42)}
PARAMS_FATIGUE = {'Faible': (0, 2, 4), 'Moyenne': (3, 5, 7), 'Forte': (6, 8, 10)}
PARAMS_MAUX = {'Faible': (0, 2, 4), 'Moyen': (3, 5, 7), 'Fort': (6, 8, 10)}
PARAMS_RISQUE = {'Faible': (0, 20, 40), 'Moyen': (30, 50, 70), 'Élevé': (60, 80, 100)}


def fuzzification_temp(t):
    return {k: fonction_triangulaire(t, *v) for k, v in PARAMS_TEMP.items()}


def fuzzification_fatigue(f):
    return {k: fonction_triangulaire(f, *v) for k, v in PARAMS_FATIGUE.items()}


def fuzzification_maux(m):
    return {k: fonction_triangulaire(m, *v) for k, v in PARAMS_MAUX.items()}


# ============================================================================
# 2. BASE DE REGLES FLOUES (12 regles, identiques pour Mamdani et Sugeno)
# ============================================================================

REGLES = [
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

# Valeurs numeriques Sugeno associees a chaque niveau de risque (ordre 0 / singleton)
VALEURS_SUGENO = {'Faible': 25, 'Moyen': 50, 'Élevé': 85}

# Univers de sortie discretise finement pour l'integration numerique du centroide
Z = np.linspace(0, 100, 1001)  # pas de 0.1
MU_SORTIE = {nom: np.array([fonction_triangulaire(z, *p) for z in Z])
             for nom, p in PARAMS_RISQUE.items()}


# ============================================================================
# 3. MODELE DE MAMDANI (avec VRAI centre de gravite)
# ============================================================================

def inference_mamdani(temp, fatigue, maux, verbose=False):
    """
    Inference floue selon le modele de Mamdani :
      1. Fuzzification
      2. Activation des regles (AND = min)
      3. Implication : on "ecrete" (clip) chaque ensemble flou de sortie
         a son niveau d'activation (methode du minimum, standard Mamdani)
      4. Agregation des ensembles ecretes par le MAX
      5. Defuzzification par CENTRE DE GRAVITE reel :
            z* = sum(z_i * mu_agrege(z_i)) / sum(mu_agrege(z_i))
         calcule par integration numerique sur l'univers de sortie discretise.
    """
    t_fuzz = fuzzification_temp(temp)
    f_fuzz = fuzzification_fatigue(fatigue)
    m_fuzz = fuzzification_maux(maux)

    # Degre d'activation max par niveau de sortie (pour l'ecretage)
    activation_par_risque = {'Faible': 0.0, 'Moyen': 0.0, 'Élevé': 0.0}
    for (t_c, f_c, m_c, sortie) in REGLES:
        alpha = min(t_fuzz[t_c], f_fuzz[f_c], m_fuzz[m_c])
        if alpha > activation_par_risque[sortie]:
            activation_par_risque[sortie] = alpha

    # Agregation : max, point par point, des fonctions de sortie ecretees
    mu_agrege = np.zeros_like(Z)
    for nom, alpha in activation_par_risque.items():
        if alpha > 0:
            ecrete = np.minimum(MU_SORTIE[nom], alpha)
            mu_agrege = np.maximum(mu_agrege, ecrete)

    denom = np.trapezoid(mu_agrege, Z)
    if denom == 0:
        risque = 0.0
    else:
        risque = np.trapezoid(Z * mu_agrege, Z) / denom

    if verbose:
        print(f"Activations : {activation_par_risque} -> Mamdani = {risque:.2f}%")

    return risque, activation_par_risque


# ============================================================================
# 4. MODELE DE SUGENO (ordre 0, moyenne ponderee)
# ============================================================================

def inference_sugeno(temp, fatigue, maux, verbose=False):
    t_fuzz = fuzzification_temp(temp)
    f_fuzz = fuzzification_fatigue(fatigue)
    m_fuzz = fuzzification_maux(maux)

    num, den = 0.0, 0.0
    for (t_c, f_c, m_c, sortie) in REGLES:
        w = min(t_fuzz[t_c], f_fuzz[f_c], m_fuzz[m_c])
        if w > 0:
            num += w * VALEURS_SUGENO[sortie]
            den += w
    risque = num / den if den > 0 else 0.0
    if verbose:
        print(f"Sugeno = {risque:.2f}%")
    return risque


# ============================================================================
# 5. SCRIPT D'ÉTUDE COMPLÈTE (tableaux, graphiques, benchmark)
# ============================================================================
# Tout ce qui suit ne s'exécute QUE si on lance ce fichier directement
# (python fuzzy_paludisme.py), jamais lors d'un simple `import` — c'est ce
# qui permet à streamlit_app.py d'importer inference_mamdani/inference_sugeno
# sans déclencher de calculs lourds, d'écriture de fichiers ou de tracés au
# démarrage de l'application web.

def etude_complete():
    # --- 5 patients du rapport ---
    patients = [(39, 7, 8), (37, 5, 4), (36, 2, 2), (38, 8, 6), (40, 9, 9)]
    rows = []
    for t, f, m in patients:
        rm, _ = inference_mamdani(t, f, m)
        rs = inference_sugeno(t, f, m)
        rows.append([t, f, m, round(rm, 2), round(rs, 2), round(abs(rm - rs), 2)])

    df5 = pd.DataFrame(rows, columns=["Temp(°C)", "Fatigue", "Maux", "Mamdani(%)", "Sugeno(%)", "Écart"])
    print("=== Tableau des 5 patients (reproductible) ===")
    print(df5.to_string(index=False))

    # --- Étude comparative étendue : grille systématique de scénarios ---
    temps_range = np.arange(35, 42.5, 1.0)
    fatigue_range = np.arange(0, 11, 2)
    maux_range = np.arange(0, 11, 2)

    grid_rows = []
    for t in temps_range:
        for f in fatigue_range:
            for m in maux_range:
                rm, _ = inference_mamdani(t, f, m)
                rs = inference_sugeno(t, f, m)
                grid_rows.append([t, f, m, rm, rs, rm - rs])

    dfgrid = pd.DataFrame(grid_rows, columns=["Temp", "Fatigue", "Maux", "Mamdani", "Sugeno", "Écart"])
    print(f"\n=== Étude comparative étendue : {len(dfgrid)} scénarios ===")
    print(dfgrid[["Mamdani", "Sugeno", "Écart"]].describe().round(2).to_string())

    correlation = dfgrid["Mamdani"].corr(dfgrid["Sugeno"])
    print(f"\nCorrélation Mamdani/Sugeno sur {len(dfgrid)} scénarios : {correlation:.4f}")
    print(f"Écart absolu moyen : {dfgrid['Écart'].abs().mean():.2f} points")
    print(f"Écart absolu max   : {dfgrid['Écart'].abs().max():.2f} points")

    dfgrid.to_csv("etude_comparative_grille.csv", index=False)

    # --- Analyse de sensibilité : faire varier une variable, les autres fixes ---
    fatigue_fixe, maux_fixe = 5, 5
    temps_fins = np.linspace(35, 42, 100)
    mam_curve = [inference_mamdani(t, fatigue_fixe, maux_fixe)[0] for t in temps_fins]
    sug_curve = [inference_sugeno(t, fatigue_fixe, maux_fixe) for t in temps_fins]

    plt.figure(figsize=(7, 4.5))
    plt.plot(temps_fins, mam_curve, label="Mamdani", linewidth=2)
    plt.plot(temps_fins, sug_curve, label="Sugeno", linewidth=2, linestyle="--")
    plt.xlabel("Température (°C)")
    plt.ylabel("Risque de paludisme estimé (%)")
    plt.title("Sensibilité du risque à la température (fatigue=5, maux=5)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("sensibilite_temperature.png", dpi=150)
    plt.close()

    # --- Comparaison des temps d'exécution (Mamdani vs Sugeno) ---
    N = 2000
    random.seed(42)
    scenarios_temps = [(random.uniform(35, 42), random.uniform(0, 10), random.uniform(0, 10))
                        for _ in range(N)]

    t0 = time.perf_counter()
    for t, f, m in scenarios_temps:
        inference_mamdani(t, f, m)
    t_mamdani = time.perf_counter() - t0

    t0 = time.perf_counter()
    for t, f, m in scenarios_temps:
        inference_sugeno(t, f, m)
    t_sugeno = time.perf_counter() - t0

    print(f"\n=== Temps d'exécution sur {N} inférences ===")
    print(f"Mamdani : {t_mamdani*1000:.1f} ms total  ({t_mamdani/N*1e6:.1f} µs/inférence)")
    print(f"Sugeno  : {t_sugeno*1000:.1f} ms total  ({t_sugeno/N*1e6:.1f} µs/inférence)")
    print(f"Facteur de vitesse Sugeno / Mamdani : {t_mamdani/t_sugeno:.1f}x plus rapide")

    # --- Graphique des fonctions d'appartenance (pour le rapport) ---
    fig, axes = plt.subplots(1, 4, figsize=(18, 4))
    x_temp = np.linspace(34, 43, 200)
    for nom, p in PARAMS_TEMP.items():
        axes[0].plot(x_temp, [fonction_triangulaire(x, *p) for x in x_temp], label=nom)
    axes[0].set_title("Température corporelle"); axes[0].set_xlabel("°C"); axes[0].legend(); axes[0].grid(alpha=.3)

    x_f = np.linspace(0, 10, 200)
    for nom, p in PARAMS_FATIGUE.items():
        axes[1].plot(x_f, [fonction_triangulaire(x, *p) for x in x_f], label=nom)
    axes[1].set_title("Fatigue"); axes[1].set_xlabel("/10"); axes[1].legend(); axes[1].grid(alpha=.3)

    x_m = np.linspace(0, 10, 200)
    for nom, p in PARAMS_MAUX.items():
        axes[2].plot(x_m, [fonction_triangulaire(x, *p) for x in x_m], label=nom)
    axes[2].set_title("Maux de tête"); axes[2].set_xlabel("/10"); axes[2].legend(); axes[2].grid(alpha=.3)

    x_r = np.linspace(0, 100, 200)
    for nom, p in PARAMS_RISQUE.items():
        axes[3].plot(x_r, [fonction_triangulaire(x, *p) for x in x_r], label=nom)
    axes[3].set_title("Risque de paludisme (sortie)"); axes[3].set_xlabel("%"); axes[3].legend(); axes[3].grid(alpha=.3)

    plt.tight_layout()
    plt.savefig("fonctions_appartenance.png", dpi=150)
    plt.close()

    # Exemple détaillé patient 1 (pour vérification pas-à-pas dans le rapport)
    print("\n=== Détail patient 1 (39°C, fatigue 7, maux 8) ===")
    inference_mamdani(39, 7, 8, verbose=True)
    inference_sugeno(39, 7, 8, verbose=True)

    df5.to_csv("resultats_5_patients.csv", index=False)
    print("\nFichiers générés : resultats_5_patients.csv, etude_comparative_grille.csv,")
    print("sensibilite_temperature.png, fonctions_appartenance.png")


if __name__ == "__main__":
    etude_complete()
