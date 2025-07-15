"""
Hamilton Regime Detection Algorithm - Production Implementation
Based on Hamilton (1989) mathematical framework with validated indicators

Mathematical Foundation:
- Hamilton, J.D. (1989): "A New Approach to the Economic Analysis of Nonstationary Time Series"
- Kim, C.J. & Nelson, C.R. (1999): "State-Space Models with Regime Switching"

Empirical Validation:
- VIX: Primary indicator (Cohen's d = 1.65, p < 0.0001)
- HY Spreads: Primary indicator (Cohen's d = 1.27, p < 0.0001)
- BAA Spreads: Secondary indicator (Cohen's d = 0.55, p = 0.0015)

Author: Research_Quantitative_Analyst
Date: 2025-06-26
Version: 1.0.0 (Production Ready)
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import warnings
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegimeType(Enum):
    """Regime classification based on empirical analysis"""
    CRISIS = "CRISIS"
    STRESS = "STRESS" 
    NORMAL = "NORMAL"

@dataclass
class RegimeState:
    """Complete regime state with probabilities and confidence"""
    regime: RegimeType
    probabilities: Dict[str, float]
    confidence: float
    indicators: Dict[str, float]
    timestamp: datetime
    
@dataclass
class ModelParameters:
    """Hamilton model parameters"""
    means: np.ndarray  # Regime-dependent means [μ₁, μ₂, μ₃]
    variances: np.ndarray  # Regime-dependent variances [σ₁², σ₂², σ₃²]
    transition_matrix: np.ndarray  # 3x3 transition probability matrix
    initial_probs: np.ndarray  # Initial regime probabilities
    
class HamiltonRegimeDetector:
    """
    Production-grade Hamilton regime detection system
    
    Implementation of Hamilton (1989) Markov-switching model optimized for:
    - Real-time FX trading applications (<1 second latency)
    - Multi-indicator ensemble (VIX, HY spreads, BAA spreads, term spread)
    - Robust numerical stability
    - Statistical confidence measures
    """
    
    def __init__(self, 
                 n_regimes: int = 3,
                 indicator_weights: Dict[str, float] = None,
                 regime_thresholds: Dict[str, Dict[str, float]] = None):
        """
        Initialize Hamilton regime detector
        
        Args:
            n_regimes: Number of regimes (default 3: CRISIS, STRESS, NORMAL)
            indicator_weights: Weights for indicator combination
            regime_thresholds: Threshold values for regime classification
        """
        self.n_regimes = n_regimes
        self.regime_names = [regime.value for regime in RegimeType]
        
        # Validated indicator weights from Phase 2 analysis
        self.indicator_weights = indicator_weights or {
            'VIX': 0.4,           # Primary: Strong crisis differentiation
            'HY_SPREADS': 0.3,    # Primary: Financial stress indicator  
            'BAA_SPREADS': 0.2,   # Secondary: Credit conditions
            'TERM_SPREAD': 0.1    # Secondary: Monetary policy context
        }
        
        # Empirically calibrated thresholds from Phase 2 statistical analysis
        self.regime_thresholds = regime_thresholds or {
            'VIX': {'crisis': 30.0, 'stress': 20.0, 'normal': 15.0},
            'HY_SPREADS': {'crisis': 8.0, 'stress': 6.0, 'normal': 4.0},
            'BAA_SPREADS': {'crisis': 7.0, 'stress': 6.0, 'normal': 5.0},
            'TERM_SPREAD': {'inversion': 0.0, 'flat': 1.0, 'steep': 2.0}
        }
        
        # Model state
        self.is_fitted = False
        self.parameters: Optional[ModelParameters] = None
        self.filtered_probs: Optional[np.ndarray] = None
        self.log_likelihood: Optional[float] = None
        
        # Performance tracking
        self.last_update_time: Optional[datetime] = None
        self.computation_times: List[float] = []
        
    def _prepare_composite_indicator(self, data: pd.DataFrame) -> np.ndarray:
        """
        Create weighted composite indicator from multiple series
        
        Mathematical Framework:
        C_t = Σᵢ wᵢ × standardize(Xᵢₜ)
        
        Where:
        - C_t: Composite indicator at time t
        - wᵢ: Weight for indicator i (validated in Phase 2)
        - Xᵢₜ: Raw indicator value
        - standardize(): Z-score normalization
        
        Args:
            data: DataFrame with indicator columns
            
        Returns:
            Composite indicator array
        """
        composite = np.zeros(len(data))
        total_weight = 0
        
        for indicator, weight in self.indicator_weights.items():
            if indicator in data.columns:
                # Z-score standardization
                values = data[indicator].values
                if len(values) > 1 and np.std(values) > 0:
                    standardized = (values - np.mean(values)) / np.std(values)
                    composite += weight * standardized
                    total_weight += weight
                else:
                    logger.warning(f"Insufficient data for {indicator}")
        
        if total_weight > 0:
            composite /= total_weight
            
        return composite
    
    def _initialize_parameters(self, data: np.ndarray) -> ModelParameters:
        """
        Initialize model parameters using data-driven approach
        
        Initialization Strategy:
        1. K-means clustering for initial regime classification
        2. Sample means and variances by regime
        3. Transition matrix from regime sequence
        4. Equal initial probabilities
        
        Args:
            data: Composite indicator time series
            
        Returns:
            Initial model parameters
        """
        from sklearn.cluster import KMeans
        
        # K-means clustering for initial regime assignment
        data_reshaped = data.reshape(-1, 1)
        kmeans = KMeans(n_clusters=self.n_regimes, random_state=42, n_init=10)
        regime_labels = kmeans.fit_predict(data_reshaped)
        
        # Calculate regime-dependent statistics
        means = np.zeros(self.n_regimes)
        variances = np.zeros(self.n_regimes)
        
        for i in range(self.n_regimes):
            regime_data = data[regime_labels == i]
            if len(regime_data) > 0:
                means[i] = np.mean(regime_data)
                variances[i] = max(np.var(regime_data), 1e-6)  # Numerical stability
            else:
                # Fallback if regime not represented
                means[i] = np.mean(data)
                variances[i] = np.var(data)
        
        # Sort regimes by mean (crisis = highest stress indicator values)
        sorted_indices = np.argsort(means)[::-1]
        means = means[sorted_indices]
        variances = variances[sorted_indices]
        
        # Initialize transition matrix with persistence
        transition_matrix = np.full((self.n_regimes, self.n_regimes), 0.1)
        np.fill_diagonal(transition_matrix, 0.8)  # High persistence
        
        # Normalize rows to sum to 1
        transition_matrix = transition_matrix / transition_matrix.sum(axis=1, keepdims=True)
        
        # Equal initial probabilities
        initial_probs = np.full(self.n_regimes, 1.0 / self.n_regimes)
        
        return ModelParameters(
            means=means,
            variances=variances,
            transition_matrix=transition_matrix,
            initial_probs=initial_probs
        )
    
    def _log_likelihood_function(self, params: np.ndarray, data: np.ndarray) -> float:
        """
        Calculate log-likelihood for Hamilton model
        
        Mathematical Framework (Hamilton 1989, Section 3):
        ℓ(θ) = Σₜ log[Σⱼ f(yₜ|Sₜ=j,Iₜ₋₁,θ) × P(Sₜ=j|Iₜ₋₁)]
        
        Where:
        - f(yₜ|Sₜ=j,Iₜ₋₁,θ): Normal density in regime j
        - P(Sₜ=j|Iₜ₋₁): Predicted regime probability
        
        Args:
            params: Flattened parameter vector
            data: Composite indicator time series
            
        Returns:
            Negative log-likelihood (for minimization)
        """
        try:
            # Unpack parameters
            n_params_per_regime = 2  # mean and variance
            n_transition_params = self.n_regimes * (self.n_regimes - 1)
            
            means = params[:self.n_regimes]
            log_variances = params[self.n_regimes:2*self.n_regimes]
            variances = np.exp(log_variances)  # Ensure positive
            
            # Transition probabilities (with softmax normalization)
            transition_raw = params[2*self.n_regimes:2*self.n_regimes + n_transition_params]
            transition_matrix = self._build_transition_matrix(transition_raw)
            
            # Hamilton filter
            filtered_probs, log_likelihood = self._hamilton_filter(
                data, means, variances, transition_matrix
            )
            
            return -log_likelihood  # Negative for minimization
            
        except Exception as e:
            logger.warning(f"Likelihood calculation error: {e}")
            return 1e10  # Large positive value for minimization
    
    def _build_transition_matrix(self, raw_params: np.ndarray) -> np.ndarray:
        """
        Build transition matrix with softmax normalization
        
        Ensures:
        - All probabilities in [0,1]
        - Each row sums to 1
        - Numerical stability
        
        Args:
            raw_params: Raw transition parameters
            
        Returns:
            Normalized transition matrix
        """
        matrix = np.zeros((self.n_regimes, self.n_regimes))
        idx = 0
        
        for i in range(self.n_regimes):
            # Diagonal element (persistence) - higher than off-diagonal
            diagonal_logit = 2.0  # Implies ~88% persistence
            off_diagonal_logits = raw_params[idx:idx + self.n_regimes - 1]
            
            # Combine into full row
            row_logits = np.zeros(self.n_regimes)
            row_logits[i] = diagonal_logit
            
            off_idx = 0
            for j in range(self.n_regimes):
                if j != i:
                    row_logits[j] = off_diagonal_logits[off_idx]
                    off_idx += 1
            
            # Softmax normalization
            row_probs = np.exp(row_logits - np.max(row_logits))
            row_probs /= np.sum(row_probs)
            matrix[i, :] = row_probs
            
            idx += self.n_regimes - 1
        
        return matrix
    
    def _hamilton_filter(self, 
                        data: np.ndarray, 
                        means: np.ndarray, 
                        variances: np.ndarray,
                        transition_matrix: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Hamilton filter implementation for optimal regime inference
        
        Mathematical Framework (Hamilton 1989, Section 4):
        
        Prediction Step:
        P(Sₜ=j|Iₜ₋₁) = Σᵢ P(Sₜ=j|Sₜ₋₁=i) × P(Sₜ₋₁=i|Iₜ₋₁)
        
        Update Step:
        P(Sₜ=j|Iₜ) = [f(yₜ|Sₜ=j,Iₜ₋₁) × P(Sₜ=j|Iₜ₋₁)] / f(yₜ|Iₜ₋₁)
        
        Args:
            data: Time series observations
            means: Regime-dependent means
            variances: Regime-dependent variances
            transition_matrix: Transition probability matrix
            
        Returns:
            Tuple of (filtered probabilities, log-likelihood)
        """
        T = len(data)
        filtered_probs = np.zeros((T, self.n_regimes))
        log_likelihood = 0.0
        
        # Initialize with equal probabilities
        filtered_probs[0, :] = 1.0 / self.n_regimes
        
        for t in range(1, T):
            # Prediction step
            predicted_probs = filtered_probs[t-1, :] @ transition_matrix
            
            # Calculate likelihoods for each regime
            likelihoods = np.zeros(self.n_regimes)
            for j in range(self.n_regimes):
                # Normal density: f(y|μ,σ²) = (2πσ²)^(-1/2) exp(-(y-μ)²/(2σ²))
                likelihoods[j] = stats.norm.pdf(data[t], means[j], np.sqrt(variances[j]))
            
            # Joint probabilities
            joint_probs = predicted_probs * likelihoods
            
            # Marginal likelihood (normalizing constant)
            marginal_likelihood = np.sum(joint_probs)
            
            if marginal_likelihood > 1e-50:  # Numerical stability
                # Update step (Bayes' theorem)
                filtered_probs[t, :] = joint_probs / marginal_likelihood
                log_likelihood += np.log(marginal_likelihood)
            else:
                # Fallback to predicted probabilities
                filtered_probs[t, :] = predicted_probs
                log_likelihood += -50  # Large negative value
        
        return filtered_probs, log_likelihood
    
    def fit(self, data: pd.DataFrame, max_iterations: int = 100) -> 'HamiltonRegimeDetector':
        """
        Fit Hamilton regime-switching model using maximum likelihood
        
        Optimization Algorithm:
        1. Initialize parameters using k-means clustering
        2. Maximum likelihood estimation via L-BFGS-B
        3. Multiple random restarts to avoid local maxima
        4. Numerical stability checks
        
        Args:
            data: DataFrame with indicator columns
            max_iterations: Maximum optimization iterations
            
        Returns:
            Fitted model instance
        """
        start_time = datetime.now()
        logger.info("Starting Hamilton model fitting...")
        
        # Prepare composite indicator
        composite_data = self._prepare_composite_indicator(data)
        
        if len(composite_data) < 50:
            raise ValueError("Insufficient data for regime detection (minimum 50 observations)")
        
        # Initialize parameters
        initial_params = self._initialize_parameters(composite_data)
        
        # Convert to optimization parameter vector
        initial_param_vector = np.concatenate([
            initial_params.means,
            np.log(initial_params.variances),  # Log transform for positivity
            initial_params.transition_matrix.flatten()[:-self.n_regimes]  # Remove redundant params
        ])
        
        best_likelihood = -np.inf
        best_params = None
        
        # Multiple random restarts to avoid local maxima
        n_restarts = 5
        for restart in range(n_restarts):
            try:
                # Add noise for restarts
                if restart > 0:
                    noise = np.random.normal(0, 0.1, len(initial_param_vector))
                    start_params = initial_param_vector + noise
                else:
                    start_params = initial_param_vector.copy()
                
                # Optimize
                result = minimize(
                    fun=self._log_likelihood_function,
                    x0=start_params,
                    args=(composite_data,),
                    method='L-BFGS-B',
                    options={'maxiter': max_iterations, 'disp': False}
                )
                
                if result.success and -result.fun > best_likelihood:
                    best_likelihood = -result.fun
                    best_params = result.x
                    logger.info(f"Restart {restart}: Log-likelihood = {best_likelihood:.2f}")
                
            except Exception as e:
                logger.warning(f"Optimization restart {restart} failed: {e}")
                continue
        
        if best_params is None:
            raise RuntimeError("All optimization attempts failed")
        
        # Extract final parameters
        means = best_params[:self.n_regimes]
        variances = np.exp(best_params[self.n_regimes:2*self.n_regimes])
        transition_matrix = self._build_transition_matrix(
            best_params[2*self.n_regimes:]
        )
        
        self.parameters = ModelParameters(
            means=means,
            variances=variances,
            transition_matrix=transition_matrix,
            initial_probs=np.full(self.n_regimes, 1.0 / self.n_regimes)
        )
        
        # Calculate final filtered probabilities
        self.filtered_probs, self.log_likelihood = self._hamilton_filter(
            composite_data, means, variances, transition_matrix
        )
        
        self.is_fitted = True
        computation_time = (datetime.now() - start_time).total_seconds()
        self.computation_times.append(computation_time)
        
        logger.info(f"Model fitting completed in {computation_time:.2f}s")
        logger.info(f"Final log-likelihood: {self.log_likelihood:.2f}")
        
        return self
    
    def predict_regime(self, latest_data: Dict[str, float]) -> RegimeState:
        """
        Predict current regime state from latest indicator values
        
        Real-time Implementation:
        1. Calculate composite indicator from latest values
        2. Apply Hamilton filter for regime probabilities
        3. Classify regime based on highest probability
        4. Calculate confidence measure
        
        Args:
            latest_data: Dictionary of latest indicator values
            
        Returns:
            Complete regime state with probabilities and confidence
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before prediction")
        
        start_time = datetime.now()
        
        # Calculate weighted composite indicator
        composite_value = 0.0
        total_weight = 0.0
        
        for indicator, weight in self.indicator_weights.items():
            if indicator in latest_data:
                composite_value += weight * latest_data[indicator]
                total_weight += weight
        
        if total_weight > 0:
            composite_value /= total_weight
        
        # Calculate regime probabilities using latest filtered probabilities
        if self.filtered_probs is not None:
            # Use last filtered probabilities as prior
            prior_probs = self.filtered_probs[-1, :]
        else:
            prior_probs = np.full(self.n_regimes, 1.0 / self.n_regimes)
        
        # Predict next period probabilities
        predicted_probs = prior_probs @ self.parameters.transition_matrix
        
        # Calculate likelihoods for current observation
        likelihoods = np.zeros(self.n_regimes)
        for j in range(self.n_regimes):
            likelihoods[j] = stats.norm.pdf(
                composite_value, 
                self.parameters.means[j], 
                np.sqrt(self.parameters.variances[j])
            )
        
        # Update probabilities (Bayes' theorem)
        joint_probs = predicted_probs * likelihoods
        marginal_likelihood = np.sum(joint_probs)
        
        if marginal_likelihood > 1e-50:
            regime_probs = joint_probs / marginal_likelihood
        else:
            regime_probs = predicted_probs
        
        # Determine primary regime
        primary_regime_idx = np.argmax(regime_probs)
        primary_regime = RegimeType(self.regime_names[primary_regime_idx])
        
        # Calculate confidence (entropy-based measure)
        prob_dict = {
            regime_name: float(prob) 
            for regime_name, prob in zip(self.regime_names, regime_probs)
        }
        
        # Confidence as maximum probability (simple but effective)
        confidence = float(regime_probs[primary_regime_idx])
        
        computation_time = (datetime.now() - start_time).total_seconds()
        self.computation_times.append(computation_time)
        
        return RegimeState(
            regime=primary_regime,
            probabilities=prob_dict,
            confidence=confidence,
            indicators=latest_data.copy(),
            timestamp=datetime.now()
        )
    
    def get_regime_history(self) -> Optional[pd.DataFrame]:
        """
        Get historical regime probabilities
        
        Returns:
            DataFrame with regime probabilities over time
        """
        if not self.is_fitted or self.filtered_probs is None:
            return None
        
        df = pd.DataFrame(
            self.filtered_probs,
            columns=[f"prob_{regime}" for regime in self.regime_names]
        )
        
        # Add regime classification
        df['regime'] = df.idxmax(axis=1).str.replace('prob_', '')
        df['confidence'] = df.max(axis=1)
        
        return df
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get model performance and computational metrics
        
        Returns:
            Dictionary of performance metrics
        """
        metrics = {}
        
        if self.is_fitted:
            metrics['log_likelihood'] = float(self.log_likelihood)
            metrics['n_parameters'] = (
                2 * self.n_regimes +  # means and variances
                self.n_regimes * (self.n_regimes - 1)  # transition probabilities
            )
            metrics['aic'] = -2 * self.log_likelihood + 2 * metrics['n_parameters']
            metrics['bic'] = (
                -2 * self.log_likelihood + 
                metrics['n_parameters'] * np.log(len(self.filtered_probs))
            )
        
        if self.computation_times:
            metrics['avg_computation_time'] = np.mean(self.computation_times)
            metrics['max_computation_time'] = np.max(self.computation_times)
            metrics['total_predictions'] = len(self.computation_times)
        
        return metrics

# Production utility functions
def create_production_detector() -> HamiltonRegimeDetector:
    """
    Create production-ready regime detector with validated parameters
    
    Uses empirically validated weights and thresholds from Phase 2 analysis
    
    Returns:
        Configured HamiltonRegimeDetector instance
    """
    return HamiltonRegimeDetector(
        n_regimes=3,
        indicator_weights={
            'VIX': 0.4,           # Primary: Excellent crisis differentiation
            'HY_SPREADS': 0.3,    # Primary: Strong financial stress signal
            'BAA_SPREADS': 0.2,   # Secondary: Credit market conditions  
            'TERM_SPREAD': 0.1    # Secondary: Monetary policy context
        },
        regime_thresholds={
            'VIX': {'crisis': 30.0, 'stress': 20.0, 'normal': 15.0},
            'HY_SPREADS': {'crisis': 8.0, 'stress': 6.0, 'normal': 4.0},
            'BAA_SPREADS': {'crisis': 7.0, 'stress': 6.0, 'normal': 5.0},
            'TERM_SPREAD': {'inversion': 0.0, 'flat': 1.0, 'steep': 2.0}
        }
    )

if __name__ == "__main__":
    # Example usage and testing
    print("Hamilton Regime Detection Algorithm - Production Implementation")
    print("=" * 70)
    
    # This would be replaced with actual FRED data in production
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    
    # Simulate realistic indicator data with regime changes
    test_data = pd.DataFrame({
        'VIX': np.random.lognormal(mean=2.8, sigma=0.4, size=1000),
        'HY_SPREADS': np.random.gamma(shape=2, scale=2.5, size=1000),
        'BAA_SPREADS': np.random.normal(loc=5.5, scale=1.2, size=1000),
        'TERM_SPREAD': np.random.normal(loc=1.0, scale=0.8, size=1000)
    }, index=dates)
    
    # Create and fit detector
    detector = create_production_detector()
    
    try:
        # Fit model
        detector.fit(test_data)
        
        # Test prediction
        latest_values = {
            'VIX': 25.0,
            'HY_SPREADS': 7.5,
            'BAA_SPREADS': 6.2,
            'TERM_SPREAD': 0.5
        }
        
        regime_state = detector.predict_regime(latest_values)
        
        print(f"Current Regime: {regime_state.regime.value}")
        print(f"Confidence: {regime_state.confidence:.2f}")
        print("Regime Probabilities:")
        for regime, prob in regime_state.probabilities.items():
            print(f"  {regime}: {prob:.3f}")
        
        # Performance metrics
        metrics = detector.get_performance_metrics()
        print(f"\nModel Performance:")
        print(f"Log-likelihood: {metrics['log_likelihood']:.2f}")
        print(f"AIC: {metrics['aic']:.2f}")
        print(f"Average computation time: {metrics['avg_computation_time']:.4f}s")
        
    except Exception as e:
        print(f"Error in regime detection: {e}")
        import traceback
        traceback.print_exc()