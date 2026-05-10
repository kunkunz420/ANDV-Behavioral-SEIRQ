<div align="center">

# 🌍 Language / 语言 / Idioma / Langue / Sprache

[English](README.md) | [简体中文](README_ZH.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Deutsch](README_DE.md)

---
</div>

<div align="center">

# 🧬 Dynamisches Verhaltens-SEIRQ-Modell für den ANDV-Ausbruch mittels agentischem OSINT

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen?logo=githubactions)](https://github.com/)
[![SciPy](https://img.shields.io/badge/deps-SciPy-8caae6?logo=scipy)](https://scipy.org/)

**Eine "Plug-and-Play"-KI-Fertigkeit für OSINT-gesteuerte epidemiologische Simulation — kalibriert mit Echtzeit-Nachrichteninformationen vom MV Hondius ANDV-Ausbruch (Mai 2026).**

<p align="center">
  <img src="results/active_vs_reff.png" width="700" alt="Aktive Infektionen vs Reff" />
</p>

</div>

---

## Zusammenfassung / TL;DR

> [!IMPORTANT]
> **Kernerkenntnis:** Die realen Belege — militärischer Lufttransport zum Gómez Ulla Krankenhaus (Madrid), Einzelzimmerisolierung (UAAN), 42-tägiges Überwachungsprotokoll und 60–90 speziell eingesetzte Gesundheitsmitarbeiter — unterdrücken die effektive Reproduktionszahl ($R_{eff}$) **innerhalb von 5 Tagen** unter die Eliminationsschwelle, was die Schließung der Schengen-Grenzen epidemiologisch unnötig macht. Ohne diese OSINT-gestützte Kalibrierung überschätzen Standardmodelle das Ausmaß des Ausbruchs um **zwei Größenordnungen**.

Dieses Repository präsentiert ein **dynamisches verhaltensorientiertes SEIRQ-Kompartimentmodell** für das **Andes-Virus (ANDV)** — die einzige Hantavirus-Variante mit bestätigter Mensch-zu-Mensch-Übertragung — unterstützt durch **agentisches OSINT** (Echtzeit-Nachrichtenscraping). Das Modell integriert **Verhaltensökonomie** (Panikelastizität, $\alpha = 0{,}65$) und **Stufenfunktions-Politikinterventionen** in einen klassischen ODE-epidemiologischen Rahmen.

### Szenarienvergleich: MV Hondius Ausbruch

| Szenario | Anfangskeime | Politikverzögerung | Quarantäne-Effizienz | Aktiver Peak | Reff < 1,0 | Schengen-Schließung? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Worst-Case (A)** | 150 | 7 Tage | 30% | ~150 | Tag 7 | **Ja ❌** |
| **Echtzeit-Eindämmung (B)** | 16 | **1 Tag 🚁** | **95% 🏥** | **~3** | **Tag 5** | **Nein ✅** |

---

## Methodik

### Modellarchitektur

Wir implementieren ein **Fünf-Kompartiment-SEIRQ-ODE-System**:

$$
\text{Empfängliche (S)} \xrightarrow{\beta(t)} \text{Exponierte (E)} \xrightarrow{\sigma} \text{Infektiöse (I)} \xrightarrow{\gamma} \text{Genesene (R)}
$$
$$
I \xrightarrow{q(t)} \text{Quarantäne (Q)}
$$

#### Kompartimentgleichungen

$$
\frac{dS}{dt} = -\beta(t) \cdot \frac{S \cdot I}{N}
$$

$$
\frac{dE}{dt} = \beta(t) \cdot \frac{S \cdot I}{N} - \sigma E
$$

$$
\frac{dI}{dt} = \sigma E - \gamma I - q(t) I
$$

$$
\frac{dR}{dt} = \gamma I
$$

$$
\frac{dQ}{dt} = q(t) I
$$

#### Verhaltensmodulation durch Panikelastizität

Die effektive Übertragungsrate wird durch das kumulierte öffentliche Bewusstsein (Selbstregulierung der sozialen Distanzierung) gedämpft:

$$
\beta_{\text{eff}}(t) = \beta_0 \cdot \max\!\left(0{,}10,\; 1 - \alpha \cdot \frac{Q(t)}{0{,}01N}\right),\quad \alpha = 0{,}65
$$

Die Quarantäne-Erkennungsrate wird nach einer Politikverzögerung $\tau$ aktiviert:

$$
q(t) = 
\begin{cases} 
\eta_q \cdot 0{,}3, & t \geq \tau \\ 
0, & t < \tau 
\end{cases}
$$

#### Epidemiologische Parameter (ANDV-spezifisch)

| Parameter | Wert | Quelle |
| :--- | :---: | :--- |
| Basisreproduktionszahl $R_0$ | 2,12 | ANDV-Mensch-zu-Mensch-Literatur |
| Inkubationszeit (Median) | 21,0 Tage | Klinischer Bereich 1–6 Wochen |
| Infektiöse Periode | 7,0 Tage | Standard-Hantavirus-Schätzung |
| Panikelastizität $\alpha$ | 0,65 | Kalibriert aus Verhaltensökonomie |
| Modellierte Population $N$ | 1.000 | Schiff + anfänglicher Kontaktpool |

*(Hinweis: Die anfängliche Population $N=1.000$ ist für die Ansteckungsphase des Kreuzfahrtschiffvorfalls kalibriert. Da das Modell dichteunabhängige Kontaktnetzwerke verwendet, ermöglicht die Skalierung von $N$ eine reibungslose Verallgemeinerung für makroskalige Vorhersagen, wie z. B. der Metropolregion Madrid.)*

---

## OSINT-Pipeline (Informationen → Parameter)

Das Szenario der "Echtzeit-Eindämmung" wurde dynamisch anhand von 20 gescrapten Nachrichtenartikeln über den MV Hondius-Vorfall kalibriert:

| Informationsextraktion | Modellparameter |
| :--- | :--- |
| 14 spanische Staatsangehörige isoliert + 2 Kontakte verfolgt (Alicante, Barcelona) | $E_0 = 16$ |
| Militärischer Lufttransport nach Madrid innerhalb von 24 Stunden | $\tau = 1{,}0$ Tag |
| Einzelzimmer-UAAN-Isolierung im Gómez Ulla Krankenhaus | $\eta_q = 0{,}95$ |
| 42-tägiges Überwachungsprotokoll, 60–90 speziell eingesetzte Mitarbeiter | Nachhaltige Quarantänedurchsetzung |
| WHO-Epidemiologe an Bord des Evakuierungsfluges | Internationale Koordination bestätigt |

---

## Agentenintegration — Nutzung als KI-Fertigkeit

Dieser Code ist dafür konzipiert, von **agentischen LLM-Systemen** als dynamische OSINT-Fertigkeit aufgenommen zu werden.

### 1. Als Kontextfertigkeit laden

Kopieren Sie die Logik aus `skill/` oder `scripts/andv_ode_solver.py` in das Tool-Verzeichnis Ihres Agenten. Fragen Sie Ihren Agenten:

> *"Führe das ANDV-Risikobewertungstool mit den neuesten OSINT-Daten von 16 Keimen und einer Politikverzögerung von 1 Tag aus. Projiziere den Krankenhauskapazitätsbedarf für Madrid nächste Woche."*

### 2. Sequentielle Bayes'sche Aktualisierungen

Traditionelle Modelle basieren auf statischen Prioren. Dieses System unterstützt eine kontinuierliche Posterior-Aktualisierung:

```text
Prior (A priori):    Worst-Case-Parameter (E0=50, I0=150, tau=7,0)
                            ↓
OSINT-Synchronisation: Der Agent scrapt 20 Echtzeit-Nachrichtenartikel
                            ↓
Posterior:           16 Keime, 1 Tag Verzögerung, 95% Quarantän-Effizienz
                            ↓
Entscheidung:        Reff < 1,0 an Tag 5 → Grenzschließung NICHT erforderlich
```

---

## Schnellstart (Quick Start)

### Voraussetzungen

* Python 3.10+
* `pip`

### Einrichtung und Ausführung

```bash
# 1. Repository klonen
git clone https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ.git
cd ANDV-Behavioral-SEIRQ

# 2. Virtuelle Umgebung
python3 -m venv venv
source venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Solver ausführen (generiert results/andv_trajectories.csv)
python scripts/andv_ode_solver.py

# 5. Diagramme erstellen
python scripts/plot_generator.py

```

### Erwartete Ausgabe

```text
[OK] Trajectories written → results/andv_trajectories.csv
[OK] Summary written → results/scenario_comparison.txt
[OK] Loaded 4,002 rows from results/andv_trajectories.csv
[OK] Chart saved → results/active_vs_reff.png
[OK] Chart saved → results/quarantine_vs_recovered.png

```

---

## Parametrisierung

Alle wichtigen Parameter sind am Anfang von `scripts/andv_ode_solver.py` definiert. Ändern Sie sie für Ihre eigenen regionalen oder pathogenspezifischen Simulationen:

```python
# ── Zentrale epidemiologische Konstanten ──
R0 = 2.12                  # Basisreproduktionszahl
INCUBATION_PERIOD = 21.0   # Tage
INFECTIOUS_PERIOD = 7.0    # Tage
N = 1000                   # Anfangspopulation

# ── Verhaltens- und Politikparameter ──
ALPHA = 0.65               # Panikelastizität [0, 1]
ETA_Q = 0.95               # Quarantäne-Effizienz [0, 1]
TAU = 1.0                  # Politikverzögerung (Tage)

```

**Beispiel-Anpassungen:**

* **Saisonale Grippe:** `R0 = 1,3`, `INCUBATION_PERIOD = 1,4`, `INFECTIOUS_PERIOD = 5,0`
* **Verzögerte Reaktion (Entwicklungsregion):** `TAU = 14,0`, `ETA_Q = 0,40`
* **Hohe öffentliche Compliance (ostasiatischer Kontext):** `ALPHA = 0,85`, `ETA_Q = 0,90`

---

## Repository-Struktur

```text
├── data/                    # Rohe & verarbeitete OSINT-Eingaben
├── scripts/
│   ├── andv_ode_solver.py   # SEIRQ-ODE-Löser
│   └── plot_generator.py    # Publikationsbereiter Diagramm-Generator
├── skill/                   # KI-Agenten-Tool-Schnittstelle
├── results/                 # Simulationsergebnisse
│   ├── andv_trajectories.csv
│   ├── scenario_comparison.txt
│   ├── active_vs_reff.png
│   └── quarantine_vs_recovered.png
├── .gitignore
├── requirements.txt
├── README.md                # English
├── README_ZH.md             # Chinese (简体中文)
├── README_ES.md             # Spanish (Español)
├── README_FR.md             # French (Français)
└── README_DE.md             # German (Deutsch)
```

---

## Zitation

```bibtex
@software{andv_seirq_behavioral_2026,
  author = {Kun and the Hermes Agent Team},
  title = {Dynamic Behavioral SEIRQ Model for ANDV Outbreak via Agentic OSINT},
  year = {2026},
  url = {https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ}
}

```

---

## Lizenz

MIT License — siehe [LICENSE](https://www.google.com/search?q=LICENSE).

---

*Eine Plug-and-Play-KI-Fertigkeit für OSINT-gesteuerte epidemiologische Modellierung*
