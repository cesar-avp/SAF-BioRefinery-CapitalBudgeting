# SAF Bio-Refinery | Capital Budgeting & Risk Analysis
## Reporte de Proyecto de Portafolio — War-Time Scenario, Marzo 2026

**Autor:** César A. V. P.  
**Perfil:** Ingeniero Petrolero | Data Analyst Junior  
**Especialización:** Finanzas Corporativas — Coursera (UNAM, 2025)  
**Versión del modelo:** 5.0 — Jupyter / Spyder Edition  
**Fecha de análisis:** 19 de marzo de 2026  
**Escenario evaluado:** Conflicto armado en Medio Oriente — Disrupciones en el Estrecho de Ormuz

---

## Tabla de Contenidos

1. [Objetivo y Justificación](#1-objetivo-y-justificación)
2. [Premisas del Modelo](#2-premisas-del-modelo)
3. [Desarrollo Técnico](#3-desarrollo-técnico)
4. [Análisis de Resultados](#4-análisis-de-resultados)
5. [Conclusiones](#5-conclusiones)
6. [Áreas de Mejora y Hoja de Ruta de Aprendizaje](#6-áreas-de-mejora-y-hoja-de-ruta-de-aprendizaje)
7. [Anexo A — Glosario de Términos Financieros y Técnicos](#anexo-a--glosario-de-términos)
8. [Anexo B — Diccionario de Variables](#anexo-b--diccionario-de-variables)

---

## 1. Objetivo y Justificación

### 1.1 Objetivo general

Construir un modelo cuantitativo de **Capital Budgeting y Gestión de Riesgo** en Python para evaluar la viabilidad financiera de reconvertir una refinería convencional en una planta de **Combustible de Aviación Sostenible (SAF)** mediante tecnología HEFA (*Hydroprocessed Esters and Fatty Acids*), bajo un escenario de alta volatilidad geopolítica (Marzo 2026).

### 1.2 Objetivos específicos

- Calcular los indicadores canónicos de evaluación de proyectos: **NPV, IRR, Payback Period y Break-Even Price**.
- Cuantificar la exposición al riesgo mediante **Simulación de Montecarlo** con 6 variables estocásticas.
- Diseñar y valorar una estrategia de cobertura **Zero-Cost Collar Dual** (UCO Leg + SAF Leg) usando el modelo de **Black-Scholes**.
- Producir un conjunto de visualizaciones de nivel institucional exportables en alta resolución, adecuadas para presentaciones ejecutivas y portafolio profesional.

### 1.3 Justificación y contexto de mercado

El SAF representa la principal palanca de descarbonización del sector de aviación comercial bajo los marcos regulatorios **ReFuelEU** (Unión Europea) y **CORSIA** (OACI). A marzo de 2026, el conflicto armado en Medio Oriente —con el cierre efectivo del Estrecho de Ormuz al tráfico de tanqueros— ha generado una disrupción sin precedentes en el mercado global de combustibles:

- El **Brent** cotiza alrededor de $108/bbl, con un incremento del ~80% desde el inicio del conflicto el 28 de febrero de 2026.
- El **Jet Fuel** y, por correlación directa, el **SAF HEFA CIF NWE** han alcanzado precios históricamente elevados (~$380/bbl, estimación derivada).
- El **UCO CIF ARA** ha subido por estrés logístico (rutas marítimas alternativas más largas) a ~$210/bbl.

Este contexto convierte al proyecto en un caso de estudio dual: un escenario de rentabilidad extraordinaria en el caso base, simultáneamente con un riesgo de cola extremo que justifica el análisis de cobertura.

### 1.4 Relevancia para el perfil del autor

Este proyecto integra conocimientos de tres disciplinas:

| Disciplina | Aplicación en el modelo |
|---|---|
| **Ingeniería Petrolera** | Comprensión de paros no programados, capacidad en bpd, tecnología HEFA, dinámica de precios de commodities |
| **Finanzas Corporativas** | WACC/CAPM, FCF, DSCR, NPV/IRR, estrategias de cobertura con opciones |
| **Ciencia de Datos** | Vectorización con NumPy/Pandas, Montecarlo estocástico, visualización institucional con Matplotlib/Seaborn, API de datos financieros vía yfinance |

---

## 2. Premisas del Modelo

### 2.1 INPUT A — Parámetros Operativos y Estructura de Capital

| Parámetro | Valor | Categoría |
|---|---|---|
| CAPEX | $450M USD | Inversión |
| SAF Price | $380/bbl | Mercado — ingresos |
| UCO Cost | $210/bbl | Mercado — costos |
| OPEX | $20/bbl | Operacional |
| Capacity | 15,000 bpd | Operacional |
| Operating Days | 310 días/año | Operacional |
| Project Life | 15 años | Horizonte |
| Tax Rate | 25% | Fiscal |
| NWC | 7% del Revenue | Capital de trabajo |
| Depreciation | Straight-Line | Contable |
| Kd Pre-Tax | 14% | Financiero |
| Weight Equity / Debt | 60% / 40% | Estructura de capital |
| WACC | Dinámico — CAPM vía yfinance | Financiero |
| Amortization | Linear | Financiero |

**Nota sobre los precios de mercado:** Los valores de SAF ($380/bbl) y UCO ($210/bbl) son estimaciones derivadas de datos de mercado reales a fecha de análisis, usando los factores de conversión estándar (SAF: ~7.9 bbl/MT; UCO: ~7.1 bbl/MT). No representan cotizaciones en firme de terminales Platts, Fastmarkets o Argus, las cuales requieren suscripción comercial. Deben interpretarse como valores de referencia para análisis de estrés.

### 2.2 INPUT B — Parámetros de Riesgo (Escenario de Guerra)

| Variable | σ aplicada | Distribución | Justificación |
|---|---|---|---|
| SAF Price | 40% | Log-normal | Volatilidad histórica SAF ×2 por conflicto |
| UCO Cost | 30% | Log-normal | Estrés logístico rutas marítimas |
| OPEX/bbl | 18% | Normal | Incertidumbre en costos energéticos |
| Operating Days | 10% | Normal | Mayor probabilidad de paros no programados |
| CAPEX Overrun | 15% | Normal | Inflación de materiales y equipos |
| WACC | 250 bps | Normal | Endurecimiento de mercados de crédito |
| N Simulations | 10,000 | — | Convergencia estadística verificada |

### 2.3 INPUT C — Parámetros del Collar de Cobertura

| Leg | Floor ($/bbl) | Cap ($/bbl) | σ aplicada |
|---|---|---|---|
| UCO (Raw Material) | $168 | $252 | 30% |
| SAF (Product) | $329 | $430 | 38% |
| Option Term | 1 año | — | — |

Los strikes fueron calibrados manualmente con referencia a 1σ de volatilidad sobre el precio base, como punto de partida para negociación. La referencia automática calculada por el modelo fue:

```
UCO Floor ref: $147  |  UCO Cap ref: $273
SAF Floor ref: $236  |  SAF Cap ref: $524
```

Los strikes seleccionados son más conservadores (más cercanos al precio spot), lo que genera una prima neta negativa (ver Sección 4.4).

---

## 3. Desarrollo Técnico

### 3.1 Arquitectura del modelo

El modelo está implementado en un único archivo Python (`SAF_BioRefinery_v5.py`) estructurado en 16 celdas ejecutables independientemente con separadores `# %%`, compatible con Spyder y Jupyter Notebook.

```
Celda 0  — Instalación de librerías
Celda 1  — Imports y configuración de estilo global
Celda 2  — INPUT A: Proyecto y estructura de capital
Celda 3  — Extracción de datos macroeconómicos (yfinance API) + WACC
Celda 4  — Modelo financiero: FCF, P&L, DSCR, KPIs
Celda 5  — Gráfica 1: J-Curve
Celda 6  — INPUT B: Riesgo y Montecarlo
Celda 7  — Gráfica 2: Heatmap de Sensibilidad
Celda 8  — Gráfica 3: Montecarlo NPV
Celda 9  — Gráfica 4: Tornado Chart
Celda 10 — INPUT C: Collar strikes
Celda 11 — Valoración Black-Scholes
Celda 12 — Gráfica 5: Collar UCO
Celda 13 — Gráfica 6: Collar SAF
Celda 14 — Gráfica 7: Fan Chart
Celda 15 — Gráfica 8: DSCR Timeline
Celda 16 — Tabla ejecutiva de resumen
```

### 3.2 Motor financiero (Módulo 2)

#### 3.2.1 WACC dinámico vía CAPM

El modelo extrae en tiempo real tres parámetros de mercado mediante la API de Yahoo Finance:

- **Beta apalancada** de Valero Energy (VLO) como empresa proxy del sector refinery/biofuels en EE.UU.
- **Risk-Free Rate (Rf):** Yield del Tesoro USA a 10 años (^TNX).
- **Market Return (Rm):** CAGR geométrico del S&P 500 a 10 años (^GSPC).

```
Ke = Rf + β × (Rm − Rf)      [CAPM]
Kd_net = Kd_pre × (1 − t)    [Tax Shield]
WACC = We × Ke + Wd × Kd_net
```

Resultado obtenido el 19/03/2026:

| Parámetro | Valor |
|---|---|
| Beta (VLO) | 0.73x |
| Rf (10Y Treasury) | 4.28% |
| Rm (S&P 500 CAGR) | 12.41% |
| Ke (CAPM) | 10.24% |
| Kd After-Tax | 10.50% |
| **WACC** | **10.35%** |

**Nota metodológica:** El uso de VLO como proxy beta es práctica estándar en Project Finance para refinerías. La Beta de 0.73x refleja riesgo sistemático moderado — menor que el mercado — lo que resulta en un Ke del 10.24%, próximo al Kd neto. Esto produce un WACC equilibrado pero que podría subestimar el riesgo específico de un proyecto greenfield de biocombustibles, donde el riesgo tecnológico y regulatorio no está capturado en la beta de una refinería convencional.

#### 3.2.2 Modelo FCF con ΔNWC

El Free Cash Flow se construye sobre el P&L vectorizado en Pandas:

```
Revenues = Annual Volume × SAF Price
COGS_UCO = Annual Volume × UCO Cost
EBITDA   = Revenues − COGS_UCO − OPEX
EBIT     = EBITDA − Depreciation (D&A)
Taxes    = EBIT × t   (solo cuando EBIT > 0)
NOPAT    = EBIT − Taxes
FCF      = NOPAT + D&A − CAPEX − ΔNWC
```

El **ΔNWC** (cambio en Capital de Trabajo Neto) es un componente frecuentemente omitido en modelos simplificados. Su inclusión en este modelo asegura que el FCF refleje el consumo real de caja en el Año 1 (buildup de NWC) y la liberación terminal en el Año 15 (recuperación completa del NWC acumulado).

#### 3.2.3 Tabla de Deuda y DSCR

```
Debt = CAPEX × Weight_Debt
DSCR = EBITDA / Debt_Service
```

El DSCR mínimo de 18.75x en Año 1 es extraordinariamente alto incluso para este escenario de guerra, consecuencia directa de los elevados márgenes operativos. El covenant bancario estándar es DSCR ≥ 1.20x.

### 3.3 Motor de riesgo (Módulo 3)

#### 3.3.1 Sensibilidad 2D — np.meshgrid

La matriz de sensibilidad NPV vs (SAF Price × UCO Cost) se calcula mediante `np.meshgrid`, evaluando todas las combinaciones posibles sin loops. Los rangos del heatmap son **dinámicos**: se calculan como ±40% (stress) alrededor de los precios base, asegurando que el precio spot siempre quede al centro de la matriz.

#### 3.3.2 Montecarlo extendido — 6 variables estocásticas

Las distribuciones fueron seleccionadas según criterio financiero:

- **Log-normal para precios (SAF, UCO):** Los precios de commodities no pueden ser negativos. La distribución log-normal es asimétrica positiva y preserva la media exacta mediante el ajuste `μ_LN = ln(media) − σ²/2`.
- **Normal para variables operativas:** Los errores en OPEX, días operativos, CAPEX overrun y WACC se distribuyen simétricamente alrededor del valor base.

El Montecarlo usa un **WACC estocástico por escenario** (factor de anualidad variable), lo que representa una mejora metodológica significativa respecto a modelos que fijan el WACC como constante.

#### 3.3.3 Black-Scholes para Collar Dual

```
d1 = [ln(S/K) + (r + σ²/2)·T] / (σ·√T)
d2 = d1 − σ·√T
Call = S·N(d1) − K·e^(−rT)·N(d2)
Put  = K·e^(−rT)·N(−d2) − S·N(−d1)
```

La valoración asume opciones europeas sobre el precio spot. Para mayor precisión en commodities energéticos, el modelo Black-76 (sobre futuros) sería más apropiado, pero Black-Scholes es el estándar aceptado para análisis de portafolio y screening de estrategias.

---

## 4. Análisis de Resultados

### 4.1 Capital Budgeting — Caso Base

| KPI | Valor | Interpretación |
|---|---|---|
| **NPV** | **$3,423.5M** | Proyecto crea valor masivo bajo precios de guerra |
| **IRR** | **103.91%** | Muy superior al hurdle rate de 10.35% |
| **Payback** | **1.08 años** | Recuperación en ~13 meses — excepcional |
| **Break-Even SAF** | **$245.2/bbl** | El proyecto es viable con SAF 35% por debajo del spot actual |
| **Min DSCR** | **18.75x** | Muy por encima del covenant mínimo 1.20x |

**Interpretación ejecutiva:** El caso base bajo precios de guerra muestra un proyecto extraordinariamente rentable. Un NPV de $3,423M sobre un CAPEX de $450M representa un múltiplo de inversión (MOIC) de 8.6x. Sin embargo, estos resultados deben contextualizarse como un escenario de pico de ciclo — no como la rentabilidad estructural del proyecto.

El Break-Even SAF de $245.2/bbl es el dato más importante para la toma de decisiones de largo plazo: significa que el proyecto es viable incluso si el precio del SAF cae un 35.5% desde los niveles de guerra actuales, lo cual otorga un margen de seguridad considerable frente a la normalización post-conflicto.

### 4.2 Análisis de Sensibilidad — Heatmap

La matriz de sensibilidad confirma la robustez del proyecto incluso bajo escenarios pesimistas:

- Con SAF a $329/bbl (−13.4% del spot) y UCO a $266/bbl (+26.6%), el NPV sería de −$693M — el único escenario de destrucción de valor cercano a los precios actuales requiere una caída simultánea extrema del SAF y un alza extrema del UCO.
- El **Crack Spread mínimo para NPV positivo** a los precios base ocurre alrededor de SAF $329/bbl con UCO $210/bbl, coherente con el Break-Even calculado.

### 4.3 Montecarlo — Análisis de Riesgo

| Métrica | Valor |
|---|---|
| Mean NPV | $3,434.9M |
| P(NPV > 0) | 79.2% |
| VaR (5%) | −$3,325.0M |
| VaR (10%) | −$1,835.7M |

La dicotomía entre el NPV base ($3,424M) y el VaR(5%) (−$3,325M) es la firma característica de proyectos evaluados en pico de ciclo de commodities con alta volatilidad. La distribución del NPV tiene una **cola izquierda extremadamente larga**, consecuencia directa de σSAF=40%.

La raíz matemática de este fenómeno es el **Crack Spread estocástico**:

```
σ(Crack Spread) ≈ √[(SAF × σSAF)² + (UCO × σUCO)²]
                = √[(380 × 0.40)² + (210 × 0.30)²]
                ≈ $165/bbl
```

La desviación estándar del Crack Spread ($165/bbl) supera el Crack Spread base ($150/bbl), lo que implica que la distribución tiene probabilidad material de producir márgenes negativos en escenarios extremos.

**Limitación metodológica conocida:** El Montecarlo genera un solo FCF anual por escenario, replicado durante los 15 años mediante el factor de anualidad. Esto asume precios constantes durante todo el horizonte, subestimando la *path dependency* real del proyecto. Un modelo más sofisticado requeriría simulación de caminos estocásticos año a año (Geometric Brownian Motion), lo que está fuera del alcance de este análisis.

### 4.4 Tornado Chart — Drivers de Riesgo

| Rank | Variable | Δ NPV (±10%) | Implicación estratégica |
|---|---|---|---|
| 1 | **SAF Price** | $1,977M | Riesgo #1 — Estructurar cobertura prioritaria |
| 2 | UCO Cost | $1,092M | Riesgo #2 — UCO Collar justificado |
| 3 | Op. Days | $780M | Riesgo operacional — no cobertura financiera |
| 4 | WACC | $463M | Riesgo financiero — fijación de tasa en deuda |
| 5 | OPEX/bbl | $104M | Riesgo menor — gestión operativa interna |
| 6 | CAPEX | $79M | Riesgo mínimo — ya invertido en t=0 |

El Tornado confirma que las dos primeras barras (SAF Price y UCO Cost) representan el 88% del riesgo total del NPV, lo que justifica plenamente la estrategia de Collar Dual. Los días operativos en tercer lugar reflejan la experiencia del autor como Ingeniero Petrolero: los paros no programados son un destructor de caja silencioso en proyectos de proceso continuo.

### 4.5 Estrategia de Cobertura — Zero-Cost Collar Dual

#### Estructura implementada

| Leg | Instrumento | Strike | Prima B-S |
|---|---|---|---|
| UCO | Compra Put (piso de costo) | $168/bbl | $5.64/bbl |
| UCO | Venta Call (financia Put) | $252/bbl | $14.03/bbl |
| SAF | Compra Put (piso de ingreso) | $329/bbl | $26.10/bbl |
| SAF | Venta Call (financia Put) | $430/bbl | $45.01/bbl |

#### Resultado financiero

```
Net Collar Cost: −$27.29/bbl  ($−126.91M/año)
```

El costo neto **negativo** indica que el modelo está recibiendo más prima de la que paga — la estructura es un **"premium collar"**, no un zero-cost estricto. Esto ocurre por la asimetría de la distribución log-normal con σSAF=38%: la cola derecha es tan gruesa que los Calls valen significativamente más que los Puts al mismo porcentaje OTM.

Dos interpretaciones son válidas:

1. **Interpretación conservadora:** Los strikes están mal calibrados — el Cap SAF en $430 está demasiado cerca del spot actual ($380), generando una prima de Call muy alta. Se debería subir el Cap.

2. **Interpretación de estrés:** En escenario de guerra, el mercado está pagando primas extraordinarias por opciones. La estructura actual "vende volatilidad cara" — puede ser intencional si la tesis es que los precios se normalizarán.

#### Crack Spread mínimo garantizado (hedged floor)

```
Min Crack Spread = SAF Floor − UCO Cap − OPEX
                 = $329 − $252 − $20 = $57/bbl
```

Con el Collar activo, el margen operativo nunca cae por debajo de $57/bbl bajo los supuestos del modelo, lo que garantiza EBITDA positivo en cualquier escenario dentro de la banda de cobertura.

### 4.6 Fan Chart — Bankabilidad

El Fan Chart muestra que el **P10 cae por debajo de la línea de Debt Service Acumulado**, activando la alerta de "Covenant Breach / Review Structure". Sin embargo, el Debt Service Año 1 es solo $37M sobre un EBITDA de ~$700M, lo que sugiere que la alerta P10 está siendo generada por los escenarios extremos del Montecarlo (cola izquierda), no por un problema estructural de apalancamiento.

El P50 (mediana) se mantiene muy por encima del Debt Service en todo el horizonte, confirmando que la mediana del proyecto es sólida. La alerta P10 debe interpretarse en el contexto de la alta volatilidad del Montecarlo, no como indicador de un proyecto fundamentalmente no bankable.

### 4.7 DSCR Timeline

El DSCR mínimo de 18.75x en Año 1 es un outlier extremo frente al covenant de 1.20x. Esta fortaleza financiera es consecuencia directa de los precios de guerra: el EBITDA proyectado de ~$700M anual sobre una deuda de $180M genera ratios de cobertura de otra magnitud. El gráfico confirma que no existe riesgo de covenant breach en ningún año del horizonte.

---

## 5. Conclusiones

### 5.1 Sobre el proyecto SAF en escenario de guerra

**Conclusión 1 — Rentabilidad excepcional pero dependiente del ciclo**  
El NPV de $3,424M e IRR del 104% son métricas de pico de ciclo, no estructurales. El Break-Even de $245/bbl proporciona un margen de seguridad real de 35% frente a una posible normalización post-conflicto. La decisión de inversión debe basarse en proyecciones de precio a largo plazo (P50 de la curva forward de SAF), no en el spot de guerra.

**Conclusión 2 — La cobertura es necesaria aunque el caso base sea robusto**  
El VaR(5%) de −$3,325M evidencia que el proyecto tiene riesgo de cola extremo bajo alta volatilidad. La estrategia Collar protege el Crack Spread mínimo en $57/bbl, eliminando los escenarios de quiebra técnica incluso si el SAF cae a $329/bbl simultáneamente con el UCO subiendo a $252/bbl.

**Conclusión 3 — El Collar requiere recalibración antes de implementación real**  
El costo neto de −$27.29/bbl indica que la estructura actual vende volatilidad cara. Para una negociación real con un banco o dealer de commodities, los strikes deberían ajustarse iterativamente hasta alcanzar el Zero-Cost genuino, utilizando volatilidades implícitas del mercado (no históricas).

### 5.2 Sobre el modelo y sus limitaciones

| Limitación | Impacto | Mejora futura |
|---|---|---|
| FCF constante en Montecarlo | Subestima path dependency | Geometric Brownian Motion por año |
| Beta proxy (VLO) | Subestima riesgo greenfield | Desampalancar beta sectorial y re-apalancar |
| Black-Scholes vs Black-76 | Primas ligeramente imprecisas | Implementar Black-76 para futuros |
| DSCR = EBITDA / DS | Sobreestima levemente cobertura | Usar CFADS (EBITDA − Taxes − ΔNWC) |
| Precios spot como caso base | No captura mean-reversion | Agregar escenario P50 de forward curve |
| Strikes hardcodeados | Dependencia del analista | Optimización automática con scipy |

### 5.3 Sobre el perfil del autor

Este proyecto demuestra capacidad para **integrar conocimiento de dominio (ingeniería) con herramientas cuantitativas avanzadas** — una combinación genuinamente diferenciadora para roles de Commercial Operations o Risk Analytics en el sector energético. Los puntos de mayor fortaleza observados:

- Comprensión del negocio de biocombustibles que va más allá de los datos: identificar los días operativos como tercer riesgo en el Tornado refleja intuición de ingeniero de proceso, no solo manejo de herramientas.
- Vectorización correcta del Montecarlo con distribuciones financieramente justificadas (log-normal para precios).
- Criterio para cuestionar resultados automáticos (el Collar no era Zero-Cost, se detectó y documentó).

Los puntos de desarrollo más urgentes están en la Sección 6.

---

## 6. Áreas de Mejora y Hoja de Ruta de Aprendizaje

Esta sección refleja una evaluación honesta de los gaps identificados durante el desarrollo del proyecto, con recomendaciones de recursos específicos.

### 6.1 Gaps financieros — alta prioridad

**Gap 1 — Curvas de futuros y forward pricing**  
El modelo usa precios spot como caso base. En Project Finance real, el caso base se construye sobre la **forward curve** del commodity (precio a plazo contractual), no el spot de guerra. Para SAF, la forward curve tiene muy poca liquidez (contratos líquidos solo hasta 18 meses), pero el Brent sí tiene curva completa y actúa como proxy.

*Recurso recomendado:* Hilary Till & Joseph Eagleeye — "Commodity Trading Advisors" (capítulos de forward curves). También el curso "Energy Trading and Risk Management" de Coursera (University of Geneva).

**Gap 2 — Optimización de strikes de Collar**  
Los strikes se calibraron manualmente. Un modelo institucional usa optimización numérica para encontrar los strikes que minimizan el costo neto del Collar dado un nivel de protección objetivo.

*Recurso recomendado:* `scipy.optimize.minimize` — documentación oficial. Concepto a estudiar: "cost-optimal collar".

**Gap 3 — CFADS vs EBITDA en DSCR**  
El DSCR del modelo usa EBITDA como numerador. Los bancos usan **CFADS** (Cash Flow Available for Debt Service = EBITDA − Taxes − ΔNWC − Maintenance CAPEX). Conocer esta diferencia y poder calcular ambos es indispensable para presentaciones a bancos.

### 6.2 Gaps técnicos — media prioridad

**Gap 4 — Simulación de caminos estocásticos (GBM)**  
El Montecarlo actual genera un solo valor por escenario. Simular la trayectoria de precios año a año requiere implementar **Geometric Brownian Motion**, que es el estándar en pricing de opciones y simulación de proyectos en energía.

*Recurso recomendado:* "Python for Finance" de Yves Hilpisch (O'Reilly) — Capítulo 12.

**Gap 5 — Black-76 para commodities**  
El modelo Black-Scholes es correcto para opciones sobre el spot. Para mercados con futuros líquidos (Brent, Gas Natural), **Black-76** sobre el precio de futuros es más preciso porque elimina el costo de carry.

*Recurso recomendado:* John Hull — "Options, Futures and Other Derivatives" — Capítulo 18.

**Gap 6 — Manejo de APIs financieras de pago**  
Los precios de SAF y UCO se estimaron porque no hay API pública para estos mercados. En entornos operativos reales se usan las APIs de **Platts (S&P Global Commodity Insights)**, **Argus Media** o **Fastmarkets**. Familiarizarse con su estructura de datos es un diferenciador de mercado laboral.

### 6.3 Gaps de programación — desarrollo continuo

**Gap 7 — Manejo de errores robusto**  
El modelo usa `try/except` amplio. En producción se prefieren excepciones específicas con logging estructurado.

*Recurso recomendado:* Python Logging Module — documentación oficial.

**Gap 8 — Testing unitario**  
No existe ningún test automático que valide que el WACC calculado sea razonable o que el NPV sea internamente consistente. En un entorno institucional, los modelos tienen tests de validación.

*Recurso recomendado:* `pytest` — 30 minutos de tutorial en la documentación oficial.

### 6.4 Hoja de ruta sugerida (6 meses)

| Mes | Foco | Herramienta / Recurso |
|---|---|---|
| 1–2 | Forward curves y pricing de commodities | Hilpisch "Python for Finance", Capítulos 12–14 |
| 2–3 | Simulación GBM y path-dependent options | scipy, numpy random walk |
| 3–4 | SQL avanzado para manejo de datos de mercado | PostgreSQL + pandas read_sql |
| 4–5 | Black-76, Greeks, optimización de Collar | John Hull Caps. 18–19 |
| 5–6 | Dashboard interactivo con Streamlit o Dash | Streamlit docs + Plotly |

---

## Anexo A — Glosario de Términos

| Término | Definición |
|---|---|
| **SAF** | Sustainable Aviation Fuel. Combustible de aviación producido a partir de fuentes renovables. |
| **HEFA** | Hydroprocessed Esters and Fatty Acids. Proceso de conversión de aceites vegetales/grasas en combustibles mediante hidrogenación. |
| **UCO** | Used Cooking Oil. Aceite de cocina usado, principal feedstock del proceso HEFA. |
| **Crack Spread** | Diferencia entre el precio del producto refinado (SAF) y el precio de la materia prima (UCO) menos los costos operativos. Es el margen operativo unitario. |
| **CAPEX** | Capital Expenditure. Inversión inicial en activos de larga duración. |
| **OPEX** | Operational Expenditure. Costos operativos recurrentes por unidad producida. |
| **NPV** | Net Present Value. Valor Presente Neto. Suma de los FCFs descontados al WACC menos la inversión inicial. |
| **IRR** | Internal Rate of Return. Tasa de descuento que hace NPV = 0. |
| **Payback Period** | Período de recuperación de la inversión inicial. |
| **Break-Even Price** | Precio mínimo de venta del producto para que NPV = 0. |
| **WACC** | Weighted Average Cost of Capital. Costo promedio ponderado del capital (equity + deuda). |
| **CAPM** | Capital Asset Pricing Model. Modelo que calcula el costo del equity usando Beta, Rf y Rm. |
| **Beta** | Medida del riesgo sistemático de una empresa relativo al mercado. β>1 = más volátil que el mercado. |
| **Rf** | Risk-Free Rate. Tasa libre de riesgo. Proxy: rendimiento del Tesoro USA a 10 años. |
| **Rm** | Market Return. Retorno esperado del mercado. Proxy: CAGR del S&P 500. |
| **Ke** | Cost of Equity. Costo del capital propio calculado con CAPM. |
| **Kd** | Cost of Debt. Costo de la deuda antes de impuestos. |
| **Tax Shield** | Escudo fiscal. Reducción del costo efectivo de la deuda por la deducibilidad de intereses. |
| **FCF** | Free Cash Flow. Flujo de Efectivo Libre disponible para todos los proveedores de capital. |
| **NOPAT** | Net Operating Profit After Tax. EBIT × (1 − t). |
| **NWC** | Net Working Capital. Capital de Trabajo Neto. Activos corrientes menos pasivos corrientes operativos. |
| **ΔNWC** | Cambio en el Capital de Trabajo Neto. Uso de caja cuando el negocio requiere más capital circulante. |
| **DSCR** | Debt Service Coverage Ratio. EBITDA / Debt Service. Mide la capacidad de pago de la deuda. |
| **CFADS** | Cash Flow Available for Debt Service. DSCR más preciso: EBITDA − Taxes − ΔNWC − Maintenance CAPEX. |
| **Covenant** | Condición contractual en un préstamo. El incumplimiento del DSCR mínimo activa un "Event of Default". |
| **Annuity Factor** | Factor de anualidad. PV de $1/año durante N años al WACC. Simplifica el cálculo del NPV de flujos constantes. |
| **Monte Carlo** | Técnica de simulación que genera N escenarios aleatorios para estimar la distribución de un resultado. |
| **Log-normal** | Distribución estadística donde el logaritmo de la variable sigue una distribución normal. Adecuada para precios de activos (no negativos, asimétrica positiva). |
| **VaR** | Value at Risk. El peor resultado esperado dentro de un nivel de confianza dado (e.g., VaR 5% = percentil 5 de la distribución). |
| **OAT** | One-At-a-Time. Método de análisis de sensibilidad que varía una sola variable manteniendo el resto constante. |
| **Tornado Chart** | Gráfico de barras horizontales divergentes que muestra el impacto OAT ordenado de mayor a menor. |
| **Fan Chart** | Gráfico de percentiles acumulados a lo largo del tiempo que muestra cómo se expande la incertidumbre. |
| **Collar** | Estrategia de cobertura que combina la compra de una opción Put y la venta de una opción Call (o viceversa) para acotar el precio efectivo dentro de una banda. |
| **Zero-Cost Collar** | Collar donde la prima recibida por el Call vendido financia exactamente la prima pagada por el Put comprado. Costo neto ≈ $0. |
| **Floor** | Strike del Put comprado. Precio mínimo garantizado. |
| **Cap** | Strike del Call vendido. Precio máximo al que se renuncia el upside. |
| **OTM** | Out-of-The-Money. Opción cuyo strike está alejado del precio spot actual. |
| **Black-Scholes** | Modelo matemático (1973) para valorar opciones europeas sobre el precio spot. |
| **Black-76** | Extensión del modelo Black-Scholes para opciones sobre futuros. Más preciso para commodities con mercados de futuros líquidos. |
| **MACRS** | Modified Accelerated Cost Recovery System. Método de depreciación fiscal acelerada de EE.UU. (IRS Pub. 946). |
| **ReFuelEU** | Regulación de la UE que obliga a los aeropuertos europeos a suministrar mezclas crecientes de SAF. |
| **CORSIA** | Carbon Offsetting and Reduction Scheme for International Aviation. Esquema de compensación de carbono de la OACI. |
| **CAGR** | Compound Annual Growth Rate. Tasa de crecimiento anual compuesta (geométrica). |
| **bpd** | Barriles por día. Unidad de capacidad en refinería. |
| **bbl** | Barrel. Barril. 1 bbl = 158.987 litros. |
| **MT** | Metric Tonne. Tonelada métrica. |
| **CIF NWE** | Cost, Insurance and Freight North West Europe. Precio de entrega incluye flete y seguro hasta Europa Noroccidental. |
| **ARA** | Amsterdam-Rotterdam-Antwerp. Hub principal de commodities en Europa. |
| **Brent** | Crudo de referencia del mercado europeo, extraído del Mar del Norte. |

---

## Anexo B — Diccionario de Variables

### B.1 Variables de entrada (INPUT A, B, C)

| Variable | Tipo | Valor escenario guerra | Fuente |
|---|---|---|---|
| `CAPEX_M_USD` | Input manual | 450 M USD | Supuesto del modelo |
| `SAF_PRICE_BBL` | Input manual | 380 $/bbl | Estimación derivada de Platts CIF NWE |
| `UCO_COST_BBL` | Input manual | 210 $/bbl | Estimación derivada de Fastmarkets CIF ARA |
| `OPEX_BBL` | Input manual | 20 $/bbl | Supuesto ajustado por inflación energética |
| `CAPACITY_BPD` | Input manual | 15,000 bpd | Supuesto del modelo |
| `OPERATING_DAYS` | Input manual | 310 días/año | Ajustado por disrupciones logísticas |
| `PROJECT_LIFE` | Input manual | 15 años | Supuesto del modelo |
| `TAX_RATE_PCT` | Input manual | 25% | Supuesto — tasa corporativa EE.UU. |
| `NWC_PCT_REVENUE` | Input manual | 7% | Supuesto ajustado por ciclos de cobro más largos |
| `DEPRECIATION` | Input manual | Straight-Line | Selección del usuario |
| `KD_PRETAX_PCT` | Input manual | 14% | Supuesto — mercado de crédito en guerra |
| `WEIGHT_EQUITY_PCT` | Input manual | 60% | Supuesto del modelo |
| `WEIGHT_DEBT_PCT` | Input manual | 40% | Supuesto del modelo |
| `SIGMA_SAF_PCT` | Input manual | 40% | Estimación — σ histórica SAF ×2 por conflicto |
| `SIGMA_UCO_PCT` | Input manual | 30% | Estimación — estrés logístico Mar Rojo |
| `SIGMA_OPEX_PCT` | Input manual | 18% | Supuesto |
| `SIGMA_DAYS_PCT` | Input manual | 10% | Supuesto |
| `SIGMA_CAPEX_PCT` | Input manual | 15% | Supuesto |
| `SIGMA_WACC_BPS` | Input manual | 250 bps | Supuesto — endurecimiento de crédito |
| `UCO_FLOOR_BBL` | Input manual calibrado | $168/bbl | Calibrado ~20% OTM |
| `UCO_CAP_BBL` | Input manual calibrado | $252/bbl | Calibrado ~20% OTM |
| `SAF_FLOOR_BBL` | Input manual calibrado | $329/bbl | Calibrado ~13% OTM |
| `SAF_CAP_BBL` | Input manual calibrado | $430/bbl | Calibrado ~13% OTM |

### B.2 Variables obtenidas vía API (yfinance)

| Variable | Ticker | Descripción | Valor obtenido 19/03/2026 |
|---|---|---|---|
| `beta` | VLO | Beta apalancada de Valero Energy | 0.73x |
| `risk_free_rate` | ^TNX | Yield del Tesoro USA 10 años | 4.28% |
| `market_return` | ^GSPC | CAGR geométrico S&P 500 (10 años) | 12.41% |

### B.3 Variables calculadas por el modelo

| Variable | Fórmula | Valor |
|---|---|---|
| `annual_volume` | capacity_bpd × operating_days | 4,650,000 bbl/año |
| `ke` | Rf + β × (Rm − Rf) | 10.24% |
| `kd_after_tax` | Kd_pre × (1 − t) | 10.50% |
| `wacc` | We × Ke + Wd × Kd_net | 10.35% |
| `ebitda_annual` | annual_vol × (SAF − UCO − OPEX) | ~$695M |
| `avg_depreciation` | CAPEX / N (Straight-Line) | $30M/año |
| `annuity_factor` | (1 − (1+WACC)^(−N)) / WACC | ~7.55 |
| `npv` | npf.npv(WACC, FCF_array) | $3,423.5M |
| `irr` | npf.irr(FCF_array) | 103.91% |
| `payback` | Interpolación lineal Cumulative_FCF | 1.08 años |
| `breakeven_saf` | brentq(_npv_at_saf, 50, 600) | $245.2/bbl |
| `dscr_min` | min(EBITDA_t / Debt_Service_t) | 18.75x |
| `mean_npv_mc` | mc_npv.mean() | $3,434.9M |
| `prob_success` | (mc_npv > 0).mean() × 100 | 79.2% |
| `var_5` | np.percentile(mc_npv, 5) | −$3,325.0M |
| `var_10` | np.percentile(mc_npv, 10) | −$1,835.7M |
| `put_uco` | Black-Scholes Put @ $168 | $5.64/bbl |
| `call_uco` | Black-Scholes Call @ $252 | $14.03/bbl |
| `put_saf` | Black-Scholes Put @ $329 | $26.10/bbl |
| `call_saf` | Black-Scholes Call @ $430 | $45.01/bbl |
| `net_cost_bbl` | (put_uco − call_uco) + (put_saf − call_saf) | −$27.29/bbl |
| `min_crack_spread` | SAF_Floor − UCO_Cap − OPEX | $57/bbl |

---

*Reporte generado el 19 de marzo de 2026.*  
*Modelo: SAF_BioRefinery_v5.py — Capital Budgeting & Risk Analysis, War-Time Scenario.*  
*Para uso de portafolio y referencia académica. No constituye asesoría de inversión.*
