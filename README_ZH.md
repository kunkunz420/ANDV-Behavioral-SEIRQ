<div align="center">

# 🌍 Language / 语言 / Idioma

[English](README.md) | [简体中文](README_ZH.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Deutsch](README_DE.md)

---
</div>

<div align="center">

# 🧬 基于智能体OSINT的动态行为SEIRQ模型 — 安第斯病毒(ANDV)疫情推演

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen?logo=githubactions)](https://github.com/)
[![SciPy](https://img.shields.io/badge/deps-SciPy-8caae6?logo=scipy)](https://scipy.org/)

**基于实时情报（OSINT）校准的即插即用AI技能 — MV Hondius 邮轮 ANDV 疫情实证数据驱动（2026年5月）。**

<p align="center">
  <img src="results/active_vs_reff.png" width="700" alt="活跃感染 vs Reff" />
</p>

</div>

---

## 摘要 / TL;DR

> [!IMPORTANT]
> **核心洞见：** 真实世界的干预证据——24小时内军机转运至马德里 Gómez Ulla 医院、单人负压隔离（UAAN）、42天监测协议以及增派的60–90名专职医护——在 **5天内** 就将有效再生数（$R_{eff}$）强行压制到了消除阈值以下。这使得关闭申根边境在流行病学上变得毫无必要。如果没有基于OSINT的情报校准，传统模型会将爆发规模高估**两个数量级**。

本项目实现了一个融合**行为经济学**（恐慌弹性，$\alpha = 0.65$）与**OSINT实时情报更新**（通过 DeepSeek 抓取实时新闻）的动态 SEIRQ 仓室模型，专门针对**安第斯病毒 (ANDV)** —— 汉坦病毒中唯一确认存在人传人能力的变种。该模型将阶跃式政策干预（军事级隔离、边境封锁触发机制）无缝整合进了经典的常微分方程（ODE）框架中。

### 情景对比：MV Hondius 邮轮爆发

| 情景 | 初始种子 | 政策延迟 | 隔离效率 | 峰值感染 | Reff < 1.0 | 申根封关？ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **恶劣压力测试 (A)** | 150 | 7天 | 30% | ~150 | 第7天 | **是 ❌** |
| **实时遏制 (B)** | 16 | **1天 🚁** | **95% 🏥** | **~3** | **第5天** | **否 ✅** |

---

## 方法论

### 模型架构

我们构建了一个**五仓室 SEIRQ 常微分方程 (ODE) 系统**：

$$
\text{易感者 (S)} \xrightarrow{\beta(t)} \text{暴露者 (E)} \xrightarrow{\sigma} \text{传染者 (I)} \xrightarrow{\gamma} \text{康复者 (R)}
$$
$$
I \xrightarrow{q(t)} \text{隔离者 (Q)}
$$

#### 仓室方程组

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

#### 行为经济学组件 — 恐慌弹性

当公众观察到愈来愈多人被隔离时，自发社交疏离会降低接触率：

$$
\beta_{\text{eff}}(t) = \beta_0 \cdot \max\!\left(0.10,\; 1 - \alpha \cdot \frac{Q(t)}{0.01N}\right),\quad \alpha = 0.65
$$

隔离检测率在政策延迟 $\tau$ 后激活：

$$
q(t) = 
\begin{cases} 
\eta_q \cdot 0.3, & t \geq \tau \\ 
0, & t < \tau 
\end{cases}
$$

#### ANDV特异性流行病学参数

| 参数 | 数值 | 来源 |
| :--- | :---: | :--- |
| 基本再生数 $R_0$ | 2.12 | ANDV人传人文献 |
| 潜伏期中位数 | 21.0天 | 临床范围1–6周 |
| 传染期 | 7.0天 | 汉坦病毒标准估计 |
| 恐慌弹性 $\alpha$ | 0.65 | 行为经济学校准 |
| 模拟人口 $N$ | 1,000 | 船舶 + 初始密接池 |

*(注：初始设定 $N=1,000$ 旨在精准模拟邮轮事件的播种期。由于系统基于密度无关的接触网络，通过缩放 $N$，该模型可平滑泛化至如马德里大区等百万级人口级别的宏观预测。)*

---

## OSINT情报管道 (情报 → 参数)

“实时遏制”情景的参数是根据智能体抓取的20篇关于 MV Hondius 事件的实时新闻报道动态校准的：

| 情报提取项 | 模型参数映射 |
| :--- | :--- |
| 14名西班牙乘客隔离 + 2名接触者追踪（阿利坎特、巴塞罗那） | $E_0 = 16$ |
| 24小时内国防部军机转运 | $\tau = 1.0$ 天 |
| 马德里 Gómez Ulla 医院单人 UAAN 隔离 | $\eta_q = 0.95$ |
| 42天监测协议，60–90名增配医护 | 持续的高隔离执行保障 |
| WHO 流行病学家随行撤离航班 | 国际协调机制验证 |

---

## AI Agent 集成 — 作为技能使用

本代码库的设计初衷是供 **Agentic LLM 系统** 作为动态 OSINT 技能直接调用。

### 1. 作为上下文技能加载
将 `skill/` 或 `scripts/andv_ode_solver.py` 的逻辑复制到 Agent 的工具目录中。您可以向 Agent 下达如下指令：
> *"请调用 ANDV Risk Assessment Tool。根据最新 OSINT 抓取的 16 名种子确诊数据和 1 天的政策延迟进行模拟，推演马德里下周的医院床位承载需求。"*

### 2. 序贯贝叶斯更新
传统模型依赖静态先验，而本系统支持连续的后验更新：

```text
先验 (Prior):    恶劣假设 (E0=50, I0=150, tau=7.0)
                         ↓
OSINT更新:       Agent抓取20篇实时新闻报道
                         ↓
后验 (Posterior): 16名种子, 1天延迟, 95%隔离效率
                         ↓
决策输出:        Reff在第5天降至1.0以下 → 边境封锁无必要

```

---

## 上手即用 (Quick Start)

### 前置条件

* Python 3.10+
* `pip`

### 安装与运行

```bash
# 1. 克隆仓库
git clone [https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ.git](https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ.git)
cd ANDV-Behavioral-SEIRQ

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行ODE求解器（生成 results/andv_trajectories.csv）
python scripts/andv_ode_solver.py

# 5. 生成图表
python scripts/plot_generator.py

```

### 预期输出

```text
[OK] Trajectories written → results/andv_trajectories.csv
[OK] Summary written → results/scenario_comparison.txt
[OK] Loaded 4,002 rows from results/andv_trajectories.csv
[OK] Chart saved → results/active_vs_reff.png
[OK] Chart saved → results/quarantine_vs_recovered.png

```

---

## 参数自定义

所有关键参数均定义在 `scripts/andv_ode_solver.py` 的顶部。研究人员可根据特定区域或病原体自由修改：

```python
# ── 核心流行病学常量 ──
R0 = 2.12                  # 基本再生数
INCUBATION_PERIOD = 21.0   # 潜伏期（天）
INFECTIOUS_PERIOD = 7.0    # 传染期（天）
N = 1000                   # 初始人口池

# ── 行为与政策参数 ──
ALPHA = 0.65               # 恐慌弹性 [0, 1]
ETA_Q = 0.95               # 隔离效率 [0, 1]
TAU = 1.0                  # 政策延迟（天）

```

**典型自定义场景：**

* **季节性流感:** `R0 = 1.3`, `INCUBATION_PERIOD = 1.4`, `INFECTIOUS_PERIOD = 5.0`
* **低干预/高延迟社会:** `TAU = 14.0`, `ETA_Q = 0.40`
* **高依从性社会:** `ALPHA = 0.85`, `ETA_Q = 0.90`

---

## 仓库结构

```text
├── data/                    # 原始及处理后的OSINT数据
├── scripts/
│   ├── andv_ode_solver.py   # SEIRQ ODE求解器
│   └── plot_generator.py    # 发表级图表生成器
├── skill/                   # AI Agent 工具接口层
├── results/                 # 模拟输出及图表
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

## 引用 (Citation)

```bibtex
@software{andv_seirq_behavioral_2026,
  author = {Kun and the Hermes Agent Team},
  title = {Dynamic Behavioral SEIRQ Model for ANDV Outbreak via Agentic OSINT},
  year = {2026},
  url = {[https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ](https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ)}
}

```

---

## 许可 (License)

MIT License — 详见 [LICENSE](https://www.google.com/search?q=LICENSE)。

---

*由 OSINT 驱动流行病学建模的即插即用 AI 技能构筑*
