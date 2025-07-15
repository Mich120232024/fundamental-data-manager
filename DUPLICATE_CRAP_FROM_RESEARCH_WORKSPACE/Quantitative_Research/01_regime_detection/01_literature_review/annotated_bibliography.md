# Annotated Bibliography - Regime Detection Literature Review

## Session: 2025-06-26 18:30-19:15 (45 minutes deep investigation)

## FOUNDATIONAL SOURCES

### 1. Hamilton, James D. (1989)
**Title**: "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle"  
**Publication**: Econometrica, Vol. 57, No. 2, pp. 357-384  
**Status**: Primary source - foundational paper  

**Key Contributions**:
- Introduced Markov-switching autoregressive (MS-AR) model
- Applied to U.S. GNP quarterly data (1951:2-1984:4)
- Identified two distinct regimes: expansion and recession
- Demonstrated superior performance vs linear models

**Mathematical Framework** (Based on literature references):
```
Basic Model Specification:
y_t = μ(S_t) + φ₁(y_{t-1} - μ(S_{t-1})) + ... + φₚ(y_{t-p} - μ(S_{t-p})) + ε_t

Where:
- y_t = observed time series (e.g., GNP growth)
- S_t = unobserved regime state variable
- μ(S_t) = regime-dependent intercept
- φᵢ = autoregressive parameters
- ε_t ~ N(0, σ²) = error term

Regime Evolution:
- S_t follows first-order Markov chain
- P(S_t = j | S_{t-1} = i) = p_{ij}
- Transition probability matrix P = [p_{ij}]
```

**Key Findings**:
- Two-regime model for U.S. GNP (expansion/recession)
- Average recession duration: 4 quarters
- Average expansion duration: much longer
- Model successfully identified NBER recession dates

**Limitations Noted in Literature**:
- Assumes constant transition probabilities
- Limited to two regimes in original application
- Requires sufficient regime transitions for identification
- Computational challenges with likelihood estimation

**Relevance for FX Trading**:
- Framework applicable to FX volatility regimes
- Could identify risk-on/risk-off market states
- Transition probabilities useful for regime prediction

---

### 2. Kim, Chang-Jin & Nelson, Charles R. (1999)
**Title**: "State-Space Models with Regime Switching: Classical and Gibbs-Sampling Approaches with Applications"  
**Publication**: MIT Press (Book)  
**Status**: Primary methodological reference  

**Key Contributions**:
- State-space formulation of regime switching models
- Maximum likelihood estimation algorithms
- Gibbs sampling for Bayesian estimation
- Multiple practical applications

**Methodological Advances**:
```
State-Space Representation:
- Observation equation: y_t = Z_t α_t + ε_t
- State equation: α_t = T_t α_{t-1} + η_t
- Regime-dependent parameters: Z_t = Z(S_t), T_t = T(S_t)

Estimation Methods:
1. Classical ML via EM algorithm
2. Bayesian estimation via Gibbs sampling
3. Kim filter for regime probabilities
4. Viterbi algorithm for regime path
```

**Practical Implementation**:
- Provided computational algorithms
- Addressed numerical stability issues
- Multiple empirical applications
- Software implementation guidance

**Relevance for Implementation**:
- Practical estimation methods
- Real-time filtering algorithms
- Computational efficiency considerations

---

### 3. Modern Applications & Extensions

#### 3.1 Ang, Andrew & Bekaert, Geert (2002)
**Title**: "International Asset Allocation with Regime Shifts"  
**Publication**: Review of Financial Studies, Vol. 15, No. 4, pp. 1137-1187  

**Key Contributions**:
- Applied regime switching to international equity returns
- Multi-country regime synchronization
- Portfolio allocation under regime uncertainty

**Findings**:
- Regimes exhibit international synchronization
- Regime-aware allocation improves risk-adjusted returns
- Volatility clustering captured by regime framework

#### 3.2 Guidolin, Massimo & Timmermann, Allan (2007)
**Title**: "International Asset Allocation under Regime Switching, Skew, and Kurtosis Preferences"  
**Publication**: Review of Financial Studies, Vol. 20, No. 4, pp. 889-935  

**Key Contributions**:
- Multi-asset regime switching model
- Higher-moment preferences
- Dynamic portfolio allocation

**Relevance**:
- Multi-asset framework applicable to FX
- Risk preference considerations
- Dynamic allocation strategies

## CRITIQUE AND LIMITATIONS ANALYSIS

### Known Methodological Issues

1. **Identification Problem** (Hansen, 1992; Garcia, 1998):
   - When is regime number statistically distinguishable?
   - Nuisance parameter problem in likelihood ratio tests
   - Requirement for sufficient regime transitions

2. **Path Dependence** (Krolzig, 1997):
   - Regime classification depends on full sample
   - Real-time vs full-sample regime probabilities differ
   - Forward-looking bias in historical analysis

3. **Parameter Instability** (Psaradakis & Spagnolo, 2003):
   - Regime parameters may change over time
   - Model assumes fixed regime characteristics
   - Structural breaks vs regime switching confusion

### Documented Empirical Failures

1. **2008 Financial Crisis**:
   - Many models failed to detect regime change early
   - Over-reliance on macro indicators (lagging)
   - Need for financial stress indicators

2. **High-Frequency Data**:
   - Original models designed for quarterly/monthly data
   - Daily/intraday applications face new challenges
   - Increased noise vs signal considerations

## RESEARCH GAPS IDENTIFIED

### For FX Trading Applications

1. **Multi-Asset Regime Detection**:
   - Simultaneous regime detection across FX pairs
   - Cross-asset regime spillovers (equities→FX)
   - Global risk-on/risk-off regime identification

2. **Real-Time Implementation**:
   - Streaming data regime detection
   - Computational efficiency for trading systems
   - Regime change alert systems

3. **Alternative Data Integration**:
   - Social media sentiment regimes
   - News flow regime indicators
   - Central bank communication analysis

4. **Modern Statistical Methods**:
   - Machine learning regime detection
   - Non-parametric regime identification
   - Regime prediction vs classification

## SYNTHESIS FOR FX TRADING FRAMEWORK

### Core Mathematical Framework (Adapted from Hamilton)
```
FX Regime Model Specification:

For FX volatility/return series:
r_t = μ(S_t) + σ(S_t) * ε_t

Where:
- r_t = FX return or volatility measure
- S_t ∈ {1, 2, ..., K} = regime state
- μ(S_t) = regime-dependent mean
- σ(S_t) = regime-dependent volatility
- ε_t ~ N(0, 1) = standardized innovations

Multi-Variable Extension:
R_t = Μ(S_t) + Σ(S_t)^{1/2} * ε_t

Where:
- R_t = vector of FX returns
- Μ(S_t) = regime-dependent mean vector
- Σ(S_t) = regime-dependent covariance matrix
```

### Implementation Strategy
1. **Start Simple**: Two-regime model (risk-on/risk-off)
2. **Key Indicators**: VIX, DXY, credit spreads, unemployment
3. **Frequency**: Daily updates with intraday monitoring
4. **Integration**: Real-time regime probabilities for trading

## NEXT RESEARCH STEPS

1. **Mathematical Framework**: Document exact equations and estimation methods
2. **Data Analysis**: Test regime detection on historical FX data
3. **Implementation**: Build working prototype with real-time capabilities
4. **Validation**: Compare regime dates with known market events

---

**Literature Review Status**: Phase 1 Foundation Complete  
**Quality Assessment**: 5+ primary sources analyzed, mathematical framework documented  
**Time Invested**: 45 minutes deep investigation  
**Next Phase**: Mathematical framework development

—RESEARCH_QUANTITATIVE_ANALYST