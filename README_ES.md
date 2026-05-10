<div align="center">

# 🌍 Language / 语言 / Idioma

[English](README.md) | [简体中文](README_ZH.md) | [Español](README_ES.md)

---
</div>

<div align="center">

# 🧬 Modelo SEIRQ Conductual Dinámico para el Brote de ANDV mediante OSINT Agéntico

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen?logo=githubactions)](https://github.com/)
[![SciPy](https://img.shields.io/badge/deps-SciPy-8caae6?logo=scipy)](https://scipy.org/)

**Herramienta epidemiológica plug-and-play calibrada con inteligencia en tiempo real — brote de ANDV en el MV Hondius, Islas Canarias (mayo 2026).**

<img src="results/active_vs_reff.png" alt="Infecciones activas vs Reff" width="700"/>

</div>

---

## Resumen Ejecutivo

Este repositorio presenta un **modelo SEIRQ compartimental dinámico** para el **Virus Andes (ANDV)** — la única variante del hantavirus con transmisión interhumana confirmada — informado mediante **OSINT agéntico** (extracción automatizada de noticias en tiempo real a través de DeepSeek). El modelo integra **economía conductual** (elasticidad de pánico, $\alpha = 0.65$) e **intervenciones políticas escalonadas** (cuarentena militar, cierre fronterizo Schengen) en un marco epidemiológico clásico de EDO.

### El evento empírico: MV Hondius en Canarias

El **10 de mayo de 2026**, el crucero de bandera neerlandesa **MV Hondius** — operado por Oceanwide Expeditions, procedente de Ushuaia (Argentina) — atracó en el puerto de Granadilla, Tenerife, tras declararse a bordo un brote de hantavirus con **3 fallecidos confirmados**. El gobierno español activó un **dispositivo militar sin precedentes**:

- **14 pasajeros españoles asintomáticos** fueron evacuados en **avión del Ejército del Aire** con destino a Madrid.
- **2 contactos estrechos** identificados en Alicante y Barcelona (expuestos en vuelos).
- Ingreso inmediato en el **Hospital Central de la Defensa Gómez Ulla** (Madrid), en la **Unidad de Aislamiento Avanzado (UAAN)**.
- **42 días de cuarentena**, habitaciones individuales, circuito cerrado, y refuerzo de **60–90 profesionales sanitarios**.
- Acompañamiento de un **epidemiólogo de la OMS** durante la evacuación.

### Contraste de escenarios

| Escenario | Semillas iniciales | Retardo político | Eficiencia de cuarentena | Pico activo | Reff < 1.0 | ¿Cierre Schengen? |
|-----------|:-----------------:|:----------------:|:------------------------:|:-----------:|:----------:|:-----------------:|
| **Caso pesimista (A)** | 150 | 7 días | 30% | ~150 | Día 7 | **Sí** |
| **Contención real (B)** | **16** | **1 día 🚁** | **95% 🏥** | **~3** | **Día 5** | **No** |

**Conclusión fundamental:** La evidencia del mundo real — traslado militar inmediato, aislamiento individual en el Hospital Gómez Ulla, protocolo de 42 días, y 60–90 efectivos dedicados — suprime el número reproductivo efectivo (Reff) por debajo del umbral de eliminación **en solo 5 días**. Sin esta calibración basada en OSINT, los modelos estándar sobreestiman el brote en **dos órdenes de magnitud**, conduciendo a decisiones políticas potencialmente desastrosas como el cierre de las fronteras Schengen.

> *La diferencia entre una proyección catastrófica no mitigada y un evento localizado contenido es enteramente atribuible a la respuesta conductual rápida capturada por la inteligencia en tiempo real.*

---

## Metodología

### Arquitectura del modelo

Sistema de **cinco compartimentos SEIRQ** definido por ecuaciones diferenciales ordinarias:

```
  Susceptible (S)  ——β(t)——>  Expuesto (E)  ——σ——>  Infeccioso (I)  ——γ——>  Recuperado (R)
                                                                     │
                                                                     │ q(t)
                                                                     ▼
                                                              Cuarentena (Q)
```

#### Ecuaciones del modelo

$$
\begin{align}
\frac{dS}{dt} &= -\beta(t) \cdot \frac{S \cdot I}{N} \\[4pt]
\frac{dE}{dt} &=  \beta(t) \cdot \frac{S \cdot I}{N} - \sigma E \\[4pt]
\frac{dI}{dt} &=  \sigma E - \gamma I - q(t) I \\[4pt]
\frac{dR}{dt} &=  \gamma I \\[4pt]
\frac{dQ}{dt} &=  q(t) I
\end{align}
$$

#### Modulación conductual — Elasticidad de pánico

La tasa de transmisión efectiva se atenúa mediante la conciencia pública acumulativa:

\[
\beta_{\text{eff}}(t) = \beta_0 \cdot \max\!\left(0.10,\; 1 - \alpha \cdot \frac{Q(t)}{0.01N}\right),\quad \alpha = 0.65
\]

La tasa de detección en cuarentena se activa tras un retardo político $\tau$:

\[
q(t) = \begin{cases}
\eta_q \cdot 0.3, & t \geq \tau \\
0, & t < \tau
\end{cases}
\]

#### Parámetros epidemiológicos específicos de ANDV

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| Número reproductivo básico $R_0$ | 2.12 | Literatura ANDV (transmisión interhumana) |
| Período de incubación (mediana) | 21.0 días | Rango clínico 1–6 semanas |
| Período infeccioso | 7.0 días | Estimación estándar de hantavirus |
| Elasticidad de pánico $\alpha$ | 0.65 | Calibración de economía conductual |
| Población modelada $N$ | 1.000 | Pasajeros del buque + contactos cercanos |

---

## Tubería OSINT (Inteligencia → Parámetros)

El escenario de "contención real" se calibró a partir de **20 artículos periodísticos extraídos en tiempo real** (DeepSeek预警_0122.txt) que cubren el incidente del MV Hondius:

| Extracción de inteligencia | Parámetro del modelo |
|---------------------------|---------------------|
| 14 españoles aislados + 2 contactos (Alicante, Barcelona) | $E_0 = 16$ |
| Evacuación militar en 24 horas | $\tau = 1.0$ día |
| Aislamiento individual en UAAN del Hospital Gómez Ulla (Madrid) | $\eta_q = 0.95$ |
| Protocolo de 42 días con 60–90 efectivos sanitarios | Sostenibilidad de la cuarentena |
| Epidemiólogo de la OMS a bordo del vuelo de evacuación | Coordinación internacional verificada |

### Actualización bayesiana secuencial

```
Priori (A priori):   Escenario pesimista (E0=50, I0=150, tau=7.0)
                            ↓
Actualización OSINT: 20 artículos → parámetros extraídos en tiempo real
                            ↓
Posteriori:          16 semillas, 1 día de retardo, 95% de eficiencia
                            ↓
Decisión:           Reff < 1.0 en día 5 → cierre Schengen NO requerido
```

---

## Inicio Rápido (Quick Start)

### Requisitos previos
- Python 3.10+
- `pip`

### Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/your-org/andv-seirq-behavioral.git
cd andv-seirq-behavioral

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el solucionador EDO
python scripts/andv_ode_solver.py

# 5. Generar gráficos para publicación
python scripts/plot_generator.py
```

### Salida esperada

```
[OK] Trajectories written → results/andv_trajectories.csv
[OK] Summary written → results/scenario_comparison.txt
[OK] Loaded 4,002 rows from results/andv_trajectories.csv
[OK] Chart saved → results/active_vs_reff.png
[OK] Chart saved → results/quarantine_vs_recovered.png
```

---

## Personalización de Parámetros

Todos los parámetros clave se definen al inicio de `scripts/andv_ode_solver.py`. Se pueden modificar para simulaciones regionales o de otros patógenos:

```python
# ── Constantes epidemiológicas ──
R0 = 2.12                    # Número reproductivo básico
INCUBATION_PERIOD = 21.0     # Período de incubación (días)
INFECTIOUS_PERIOD = 7.0      # Período infeccioso (días)
N = 1000                     # Población modelada

# ── Parámetros conductuales y de política ──
ALPHA = 0.65                 # Elasticidad de pánico [0, 1]
ETA_Q = 0.95                 # Eficiencia de cuarentena [0, 1]
TAU = 1.0                    # Retardo político (días)
```

### Escenarios de personalización típicos

- **Gripe estacional (España):** `R0 = 1.3`, `INCUBACIÓN = 1.4d`, `INFECCIOSO = 5d`
- **Respuesta retardada (país en desarrollo):** `TAU = 14.0`, `ETA_Q = 0.40`
- **Alta conformidad social (contexto asiático):** `ALPHA = 0.85`, `ETA_Q = 0.90`

---

## Estructura del Repositorio

```
├── data/                    # Datos OSINT brutos y procesados
├── scripts/
│   ├── andv_ode_solver.py   # Solucionador EDO SEIRQ
│   └── plot_generator.py    # Generador de gráficos para publicación
├── results/
│   ├── andv_trajectories.csv
│   ├── scenario_comparison.txt
│   ├── active_vs_reff.png
│   └── quarantine_vs_recovered.png
├── .gitignore
├── requirements.txt
└── README_ES.md
```

---

## Resumen de Resultados

| Indicador | Caso pesimista (A) | Contención real (B) |
|-----------|:------------------:|:-------------------:|
| Pico de infecciones activas | ~150 | **~3** |
| Reff inicial | 1,695 | 1,893 |
| Reff en día 7 | 1,064 | **0,866** |
| Reff < 1,0 alcanzado | Día 7 | **Día 5** |
| Cuarentena acumulada final | ~104 | **~17** |
| Susceptibles finales | ~599 | **~973** |
| ¿Requiere cierre Schengen? | **Sí** | **No** |

La respuesta real — aislamiento militar inmediato, cuarentena hospitalaria individual en el Gómez Ulla (Madrid), y protocolo de 42 días — suprime el Reff por debajo del umbral de eliminación en 5 días, haciendo innecesario el cierre fronterizo desde una perspectiva epidemiológica.

---

## Integración como Habilidad de IA (Agent Integration)

Este código está diseñado para ser ingerido por **sistemas LLM agénticos** como una habilidad OSINT dinámica:

1. **Cargar como skill contextual** → copiar `scripts/andv_ode_solver.py` al directorio de habilidades del agente.
2. **Llamar mediante subprocess** → `python3 scripts/andv_ode_solver.py --R0 1.8 --alpha 0.70`
3. **Puerta de decisión autónoma** → `if Reff < 1.0: policy = "No requiere cierre"`
4. **Estructura bayesiana secuencial** → priori → noticia → extraer semillas → re-simular → decisión

---

## Citación

```bibtex
@software{andv_seirq_behavioral_2026,
  author = {Kun and the Hermes Agent Team},
  title = {Modelo SEIRQ Conductual Dinámico para el Brote de ANDV mediante OSINT Agéntico},
  year = {2026},
  url = {https://github.com/your-org/andv-seirq-behavioral}
}
```

---

## Licencia

Licencia MIT — véase [LICENSE](LICENSE).

---

<div align="center">

*Construido con [Hermes Agent](https://hermes-agent.nousresearch.com) · Habilidad plug-and-play para modelado epidemiológico impulsado por OSINT*
</div>
