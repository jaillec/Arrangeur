# 🎹 Mon Arrangeur Musical (v1.0)

Un clavier arrangeur convivial, réactif et orienté « musiquette » (styles dansants, mélodies, accompagnement automatique et paroles synchronisées), conçu en Python avec **Pygame** et **NumPy**.

---

## 🎯 Philosophie du Projet

* **Plaisir du jeu immédiat :** Privilégier la musicalité et la réactivité plutôt qu'une synthèse sonore complexe.
* **Zéro latence clavier :** Abandon des longues chaînes de `if/elif` au profit d'une **Machine à États (FSM)** et d'un routage par dictionnaires/ensembles en temps constant $O(1)$.
* **Architecture Multi-Pistes :** Une **Horloge Maître (Master Clock)** unique pilote simultanément plusieurs pistes de rythmes, basses, accords et mélodies sans aucun décalage.

---

## 🎼 Flux de Création Naturel (En 3 Temps)

Pour ne jamais casser l'inspiration en obligeant à écrire une partition case par case, l'arrangeur suit le flux naturel d'un musicien :

1. **Étape 0 — Le Support Musical :** Choix d'un tapis rythmique d'ambiance parmi les **Styles Usine** (*Valse Lente, Valse Musette, Cha-cha-cha, Tango Lent/Rapide, Rumba...*) ou un simple métronome.
2. **Étape 1 — La Capture Spontanée (Looper en direct) :** Le support tourne en boucle. Le musicien plaque ses accords à la main gauche et joue sa mélodie à la main droite au feeling. L'arrangeur enregistre en temps réel avec quantification douce (recalage sur la grille) et superposition (*overdub*).
3. **Étape 2 — La Retouche Facile :** Bascule sur la grille visuelle (*Step Sequencer* / *Piano Roll*) pour corriger à la souris ou aux flèches les petites imperfections, régler le mixage et ajouter les paroles.

---

## 🕹️ Ergonomie & Claviers Virtuels

Le clavier d'ordinateur (AZERTY) est divisé en deux zones physiques distinctes pour imiter un orgue à deux manuels :

* **Clavier HAUT (`1234567890°` et `AZERTYUIOP¨`) :** Dédié aux mélodies principales, nappes d'orgue et arpèges.
* **Clavier BAS (`QSDFGHJKLM%` et `WXCVBN?./`) :** Dédié aux accords, aux basses et aux percussions.

### Système d'Accords « Yamaha Single Finger »
Sur le **Clavier BAS** (en mode Accords ou Live), l'arrangeur détecte instantanément l'accord selon le nombre de touches pressées :
* **1 doigt (Fondamentale) :** Accord **Majeur**.
* **2 doigts (Fondamentale + touche noire à gauche) :** Accord **Mineur**.
* **2 doigts (Fondamentale + touche blanche à gauche) :** Accord de **Septième (7)**.
* **3 doigts (Fondamentale + noire + blanche à gauche) :** Accord **Mineur Septième (m7)**.

---

## 🔄 Machine à États (Navigation Clavier)

L'application démarre sur un **Menu à l'ancienne** (style synthétiseur rétro des années 90, navigable aux flèches `↑/↓` et `Entrée`) et bascule entre des états étanches :

| État / Touche | Rôle Principal | Clavier HAUT | Clavier BAS |
| :--- | :--- | :--- | :--- |
| **`MENU_PRINCIPAL`** | Accueil rétro (Styles Usine, Chansons, Atelier, Libre) | Navigation flèches / chiffres | Navigation flèches / chiffres |
| **`RYTHM_SET` (`F1`)** | Enregistrement & édition de percussions + Tap Tempo | Muet (Économie CPU) | Percussions directes (Kick, Snare, Hat...) |
| **`BASS_SET` (`F2`)** | Enregistrement de lignes de basse transposables | **Prolongement aigu** de la basse | **Racine grave** de la basse |
| **`CHORD_SET` (`F3`)** | Saisie et édition de grilles d'accords | Arpèges / Renversements | **Mode Yamaha Single Finger** |
| **`MELODY_SET` (`F4`)** | Enregistrement mélodique solo + encodage syllabique | Mélodie principale | Commandes Rec / Play / Stop |
| **`LIVE_PLAY` (`F5`)** | Console multi-pistes & jeu en direct | Mélodie solo en direct | **Mode Yamaha** (pilote accords + basse auto) |

---

## ⏱️ Horloge Maître, Signatures & Multi-Pistes

* **Signatures rythmiques variables :** L'horloge adapte dynamiquement la longueur de la boucle :
  * `4/4` (Pop, Rock, Cha-cha-cha, Tango, Rumba) : **16 pas** par mesure.
  * `3/4` (Valse Lente *Beau Danube Bleu*, Valse Musette) : **12 pas** par mesure.
  * `6/8` (Ternaire / Blues) : **12 pas** avec accentuation ternaire.
* **Superposition intelligente :** Possibilité d'activer simultanément plusieurs rythmes (ex: *Rumba_Base* + *Maracas*), plusieurs basses et plusieurs mélodies. Toutes les pistes harmoniques se transposent automatiquement sur l'accord joué en mode Yamaha.

---

## 📝 Double Gestion des Paroles Synchronisées

Les paroles sont indexées directement sur les pas de l'Horloge Maître (suivant automatiquement tout changement de tempo BPM) selon deux modes complémentaires :

1. **Mode Prompteur / Documentation (Phrase par phrase) :** Calage rapide par « Tap-Sync » (touche `Espace` au début de chaque phrase). Affiche les repères de structure (`[Couplet]`, `[Refrain]`) et un défilement fluide sur 3 lignes avec balayage progressif façon karaoké.
2. **Mode Encodage Mélodique (Syllabe par note) :** Permet d'attacher une syllabe ou un mot-clé directement sur les rectangles de notes dans le Piano Roll pour servir d'aide-mémoire musical.

---

## 💾 Système de Sauvegarde Hybride

* **Styles Usine (`styles_usine.py`) :** Collection protégée de rythmes et basses classiques prêts à l'emploi.
* **Bibliothèque Globale (`banques/*.json`) :** Stockage réutilisable des créations personnelles (`rythmes.json`, `basses.json`, `accords.json`, `melodies.json`).
* **Dossier Morceaux (`morceaux/*.json`) :** Sauvegarde complète d'une chanson incluant le tempo, la signature rythmique, **les niveaux de mixage (volumes)**, les pistes associées et les paroles synchronisées.

---

## 📂 Arborescence du Projet `Arrangeur/`

```text
Arrangeur/
├── README.md               # Cahier des charges et documentation
├── main.py                 # Point d'entrée, init Pygame (32 canaux) et boucle principale
├── horloge_maitre.py       # Master Clock multi-pistes, signatures et quantification
├── machine_etats.py        # Routeur clavier O(1) et gestion des états (Menu + F1 à F5)
├── clavier_mapping.py      # Séparation Clavier HAUT/BAS et moteur Yamaha Single Finger
├── styles_usine.py         # Rythmes et basses prédéfinis (Valse, Tango, Rumba, Cha-cha-cha...)
├── moteur_audio.py         # Synthèse d'ondes Pygame/NumPy avec mise en cache
├── banques.py              # Chargement/sauvegarde JSON (bibliothèques + morceaux + mixage)
├── interface.py            # Rendu rétro, Step Sequencer, Piano Roll et Prompteur paroles
├── banques/                # Bibliothèques personnelles (rythmes.json, basses.json...)
└── morceaux/               # Chansons complètes sauvegardées
```
# Arrangeur
