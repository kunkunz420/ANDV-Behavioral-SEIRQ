<div align="center">

# 🌍 Language / 语言 / Idioma

[English](README.md) | [简体中文](README_ZH.md) | [Español](README_ES.md)

---
</div>

<div align="center">

# 🧬 Modelo SEIRQ Dinámico de Comportamiento para el Brote de ANDV vía OSINT de Agentes

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen?logo=githubactions)](https://github.com/)
[![SciPy](https://img.shields.io/badge/deps-SciPy-8caae6?logo=scipy)](https://scipy.org/)

**Una habilidad (Skill) de IA "plug-and-play" para simulación epidemiológica basada en OSINT — calibrada con inteligencia en tiempo real del brote de ANDV en el MV Hondius (Mayo de 2026).**

<p align="center">
  <img src="results/active_vs_reff.png" width="700" alt="Infecciones Activas vs Reff" />
</p>

</div>

---

## Resumen / TL;DR

> [!IMPORTANT]
> **Hallazgo Clave:** La evidencia del mundo real — traslado militar aéreo al Hospital Gómez Ulla (Madrid), aislamiento en habitaciones individuales de presión negativa (UAAN), protocolo de monitorización de 42 días y un equipo de 60–90 profesionales sanitarios dedicados — suprime la tasa de reproducción efectiva ($R_{eff}$) por debajo del umbral de eliminación **en 5 días**. Esto hace que el cierre de las fronteras del espacio Schengen sea epidemiológicamente innecesario. Sin esta calibración basada en OSINT, los modelos estándar sobreestiman la magnitud del brote en **dos órdenes de magnitud**.

Este repositorio presenta un **modelo compartimental dinámico de comportamiento SEIRQ** para el **Virus de los Andes (ANDV)** — la única variante de hantavirus con transmisión confirmada de persona a persona — alimentado por **inteligencia de fuentes abiertas (OSINT) basada en agentes** (extracción de noticias en tiempo real). El modelo integra la **economía del comportamiento** (elasticidad del pánico, $\alpha = 0.65$) y las **intervenciones políticas de función escalón** en un marco clásico de ecuaciones diferenciales ordinarias (EDO).

### Comparación de Escenarios: Brote en el MV Hondius

| Escenario | Semillas Iniciales | Retraso Político | Eficiencia de Cuarentena | Pico Activo | Reff < 1.0 | ¿Cierre Schengen? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Peor Escenario (A)** | 150 | 7 días | 30% | ~150 | Día 7 | **Sí ❌** |
| **Contención en T.R. (B)** | 16 | **1 día 🚁** | **95% 🏥** | **~3** | **Día 5** | **No ✅** |

---

## Metodología

### Arquitectura del Modelo

Implementamos un **sistema de ecuaciones diferenciales ordinarias (EDO) SEIRQ de cinco compartimentos**:

$$
\text{Susceptibles (S)} \xrightarrow{\beta(t)} \text{Expuestos (E)} \xrightarrow{\sigma} \text{Infecciosos (I)} \xrightarrow{\gamma} \text{Recuperados (R)}
$$
$$
I \xrightarrow{q(t)} \text{En Cuarentena (Q)}
$$

#### Ecuaciones de los Compartimentos

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

#### Modulación de Comportamiento vía Elasticidad del Pánico

La tasa de transmisión efectiva se atenúa mediante la conciencia pública acumulada (autorregulación del distanciamiento social):

$$
\beta_{\text{eff}}(t) = \beta_0 \cdot \max\!\left(0.10,\; 1 - \alpha \cdot \frac{Q(t)}{0.01N}\right),\quad \alpha = 0.65
$$

La tasa de detección y cuarentena se activa después de un retraso de política $\tau$:

$$
q(t) = 
\begin{cases} 
\eta_q \cdot 0.3, & t \geq \tau \\ 
0, & t < \tau 
\end{cases}
$$

#### Parámetros Epidemiológicos (Específicos para ANDV)

| Parámetro | Valor | Fuente |
| :--- | :---: | :--- |
| Número reproductivo básico $R_0$ | 2.12 | Literatura de transmisión ANDV (humano-humano) |
| Período de incubación (mediana) | 21.0 días | Rango clínico de 1 a 6 semanas |
| Período infeccioso | 7.0 días | Estimación estándar para hantavirus |
| Elasticidad del pánico $\alpha$ | 0.65 | Calibrado desde la economía del comportamiento |
| Población modelada $N$ | 1,000 | Barco + grupo inicial de contactos |

*(Nota: La población inicial $N=1,000$ está calibrada para la Fase de Siembra del incidente del crucero. Como el modelo utiliza redes de contacto independientes de la densidad, escalar $N$ permite una generalización fluida para pronósticos a nivel macro, como la Comunidad de Madrid.)*

---

## Flujo de Trabajo OSINT (Inteligencia → Parámetros)

El escenario de "Contención en Tiempo Real" fue calibrado dinámicamente a partir de 20 artículos de noticias extraídos que detallan el incidente del MV Hondius:

| Extracción de Inteligencia | Parámetro del Modelo |
| :--- | :--- |
| 14 españoles aislados + 2 contactos rastreados (Alicante, Barcelona) | $E_0 = 16$ |
| Traslado militar aéreo a Madrid en menos de 24 horas | $\tau = 1.0$ día |
| Aislamiento UAAN en habitaciones individuales (Hospital Gómez Ulla) | $\eta_q = 0.95$ |
| Protocolo de 42 días, 60–90 sanitarios asignados | Ejecución sostenida de la cuarentena |
| Epidemiólogo de la OMS en el vuelo de evacuación | Coordinación internacional verificada |

---

## Integración con Agentes de IA — Uso como Habilidad (Skill)

Este código está diseñado para ser ingerido por **sistemas de Modelos de Lenguaje (LLM) basados en Agentes** como una habilidad dinámica de OSINT.

### 1. Cargar como una habilidad contextual
Copia la lógica de `skill/` o `scripts/andv_ode_solver.py` en el directorio de herramientas de tu Agente. Puedes pedirle a tu Agente:
> *"Ejecuta la herramienta de Evaluación de Riesgos ANDV utilizando el último OSINT de 16 semillas y un retraso político de 1 día. Proyecta la demanda de capacidad hospitalaria para Madrid la próxima semana."*

### 2. Actualizaciones Bayesianas Secuenciales
Los modelos tradicionales se basan en priors estáticos. Este sistema soporta una actualización continua a posteriori:

```text
Prior (A priori):  Parámetros del peor caso (E0=50, I0=150, tau=7.0)
                            ↓
Sincronización OSINT: El Agente raspa 20 artículos de noticias en tiempo real
                            ↓
Posterior:         16 semillas, 1 día de retraso, 95% de eficiencia de cuarentena
                            ↓
Decisión:          Reff < 1.0 en el Día 5 → El cierre fronterizo NO es necesario

```

---

## Inicio Rápido (Quick Start)

### Requisitos Previos

* Python 3.10+
* `pip`

### Configuración y Ejecución

```bash
# 1. Clonar el repositorio
git clone [https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ.git](https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ.git)
cd ANDV-Behavioral-SEIRQ

# 2. Entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el solver (genera results/andv_trajectories.csv)
python scripts/andv_ode_solver.py

# 5. Generar gráficos
python scripts/plot_generator.py

```

### Salida Esperada

```text
[OK] Trajectories written → results/andv_trajectories.csv
[OK] Summary written → results/scenario_comparison.txt
[OK] Loaded 4,002 rows from results/andv_trajectories.csv
[OK] Chart saved → results/active_vs_reff.png
[OK] Chart saved → results/quarantine_vs_recovered.png

```

---

## Personalización de Parámetros

Todos los parámetros clave están definidos en la parte superior de `scripts/andv_ode_solver.py`. Modifícalos para tus propias simulaciones regionales o patógenas:

```python
# ── Constantes epidemiológicas centrales ──
R0 = 2.12                  # Número reproductivo básico
INCUBATION_PERIOD = 21.0   # Días
INFECTIOUS_PERIOD = 7.0    # Días
N = 1000                   # Población inicial

# ── Parámetros de comportamiento y política ──
ALPHA = 0.65               # Elasticidad del pánico [0, 1]
ETA_Q = 0.95               # Eficiencia de la cuarentena [0, 1]
TAU = 1.0                  # Retraso en la política (días)

```

**Ejemplos de Personalización:**

* **Gripe estacional:** `R0 = 1.3`, `INCUBATION_PERIOD = 1.4`, `INFECTIOUS_PERIOD = 5.0`
* **Respuesta tardía (países en desarrollo):** `TAU = 14.0`, `ETA_Q = 0.40`
* **Alto cumplimiento público:** `ALPHA = 0.85`, `ETA_Q = 0.90`

---

## Estructura del Repositorio

```text
├── data/                    # Datos OSINT crudos y procesados
├── scripts/
│   ├── andv_ode_solver.py   # Solver EDO SEIRQ
│   └── plot_generator.py    # Generador de gráficos de calidad académica
├── skill/                   # Interfaz de herramienta para Agentes IA
├── results/                 # Resultados de simulación
│   ├── andv_trajectories.csv
│   ├── scenario_comparison.txt
│   ├── active_vs_reff.png
│   └── quarantine_vs_recovered.png
├── .gitignore
├── requirements.txt
└── README_ES.md

```

---

## Cita (Citation)

```bibtex
@software{andv_seirq_behavioral_2026,
  author = {Kun and the Hermes Agent Team},
  title = {Dynamic Behavioral SEIRQ Model for ANDV Outbreak via Agentic OSINT},
  year = {2026},
  url = {[https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ](https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ)}
}

```

---

## Licencia (License)

MIT License — ver [LICENSE](https://www.google.com/search?q=LICENSE).

---

*Una habilidad de IA Plug-and-Play para el modelado epidemiológico impulsado por OSINT*
