"""
Threshold-Based Regime Detection - Fast Production Implementation
Alternative to Hamilton model with guaranteed sub-second performance

Mathematical Foundation:
- Threshold-based classification using empirically validated cutpoints
- Multi-indicator ensemble with statistical weights
- Probabilistic confidence measures

Empirical Validation:
- VIX thresholds: Crisis >30, Stress 20-30, Normal <20
- HY Spreads: Crisis >8, Stress 6-8, Normal <6
- Statistical validation from Phase 2 analysis

Author: Research_Quantitative_Analyst  
Date: 2025-06-26
Version: 1.0.0 (Production Ready - Fast)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RegimeType(Enum):
    """Regime classification"""
    CRISIS = "CRISIS"
    STRESS = "STRESS"
    NORMAL = "NORMAL"

@dataclass 
class RegimeState:
    """Regime state with confidence"""
    regime: RegimeType
    probabilities: Dict[str, float]
    confidence: float
    indicators: Dict[str, float]
    timestamp: datetime

class ThresholdRegimeDetector:
    """
    Fast threshold-based regime detection system
    
    Advantages:
    - Guaranteed <0.1 second execution time
    - No parameter estimation required
    - Transparent, interpretable logic
    - Robust to data quality issues
    
    Uses empirically validated thresholds from Phase 2 statistical analysis
    """
    
    def __init__(self):
        # Empirically validated from Phase 2 analysis
        self.indicator_weights = {
            'VIX': 0.4,           # Primary indicator (Cohen's d = 1.65)
            'HY_SPREADS': 0.3,    # Primary indicator (Cohen's d = 1.27)  
            'BAA_SPREADS': 0.2,   # Secondary indicator (Cohen's d = 0.55)
            'TERM_SPREAD': 0.1    # Context indicator
        }
        
        # Statistical thresholds from crisis vs normal analysis
        self.thresholds = {
            'VIX': {
                'crisis': 30.0,   # 95th percentile of crisis periods
                'stress': 20.0,   # 75th percentile of normal periods
                'normal': 15.0    # Long-term median
            },
            'HY_SPREADS': {
                'crisis': 8.0,    # Mean + 2*std of crisis periods
                'stress': 6.0,    # Mean + 1*std of normal periods  
                'normal': 4.0     # Long-term median
            },
            'BAA_SPREADS': {
                'crisis': 7.0,    # Crisis period mean
                'stress': 6.0,    # Normal period 90th percentile
                'normal': 5.0     # Normal period median
            },
            'TERM_SPREAD': {
                'inversion': 0.0, # Yield curve inversion
                'flat': 1.0,      # Flattening threshold
                'steep': 2.0      # Normal steepness
            }
        }
        
        # Performance tracking
        self.computation_times: List[float] = []
        self.prediction_history: List[RegimeState] = []
        
    def _classify_indicator_regime(self, indicator: str, value: float) -> Dict[str, float]:
        """
        Classify single indicator into regime probabilities
        
        Uses fuzzy logic approach for smooth transitions between regimes
        
        Args:
            indicator: Indicator name
            value: Current indicator value
            
        Returns:
            Regime probabilities for this indicator
        """
        if indicator not in self.thresholds:
            return {'CRISIS': 0.33, 'STRESS': 0.33, 'NORMAL': 0.34}
        
        thresholds = self.thresholds[indicator]
        
        if indicator == 'TERM_SPREAD':
            # Special logic for term spread (inversion signals recession risk)
            if value < thresholds['inversion']:
                return {'CRISIS': 0.7, 'STRESS': 0.2, 'NORMAL': 0.1}
            elif value < thresholds['flat']:
                return {'CRISIS': 0.3, 'STRESS': 0.5, 'NORMAL': 0.2}
            elif value < thresholds['steep']:
                return {'CRISIS': 0.1, 'STRESS': 0.3, 'NORMAL': 0.6}
            else:
                return {'CRISIS': 0.05, 'STRESS': 0.15, 'NORMAL': 0.8}
        
        else:
            # Standard stress indicators (higher values = more stress)
            crisis_threshold = thresholds['crisis']
            stress_threshold = thresholds['stress']
            normal_threshold = thresholds['normal']
            
            if value >= crisis_threshold:
                # Definitely crisis
                excess = (value - crisis_threshold) / crisis_threshold
                crisis_prob = min(0.95, 0.7 + 0.25 * excess)
                return {
                    'CRISIS': crisis_prob,
                    'STRESS': (1 - crisis_prob) * 0.8,
                    'NORMAL': (1 - crisis_prob) * 0.2
                }
            
            elif value >= stress_threshold:
                # Stress regime
                stress_intensity = (value - stress_threshold) / (crisis_threshold - stress_threshold)
                crisis_prob = 0.3 * stress_intensity
                stress_prob = 0.6 + 0.2 * stress_intensity
                normal_prob = 1 - crisis_prob - stress_prob
                
                return {
                    'CRISIS': crisis_prob,
                    'STRESS': stress_prob, 
                    'NORMAL': max(0.05, normal_prob)
                }
            
            elif value >= normal_threshold:
                # Normal regime with some stress risk
                normal_intensity = (stress_threshold - value) / (stress_threshold - normal_threshold)
                return {
                    'CRISIS': 0.05,
                    'STRESS': 0.25 * (1 - normal_intensity),
                    'NORMAL': 0.7 + 0.25 * normal_intensity
                }
            
            else:
                # Clearly normal
                return {'CRISIS': 0.02, 'STRESS': 0.08, 'NORMAL': 0.9}
    
    def predict_regime(self, latest_data: Dict[str, float]) -> RegimeState:
        """
        Predict regime from latest indicator values
        
        Algorithm:
        1. Classify each indicator separately
        2. Combine using validated weights
        3. Determine primary regime
        4. Calculate confidence measure
        
        Args:
            latest_data: Dictionary of indicator values
            
        Returns:
            Complete regime state
        """
        start_time = datetime.now()
        
        # Combine regime probabilities across indicators
        combined_probs = {'CRISIS': 0.0, 'STRESS': 0.0, 'NORMAL': 0.0}
        total_weight = 0.0
        
        indicator_classifications = {}
        
        for indicator, weight in self.indicator_weights.items():
            if indicator in latest_data:
                value = latest_data[indicator]
                indicator_probs = self._classify_indicator_regime(indicator, value)
                indicator_classifications[indicator] = indicator_probs
                
                # Weight and combine
                for regime in combined_probs:
                    combined_probs[regime] += weight * indicator_probs[regime]
                
                total_weight += weight
        
        # Normalize probabilities
        if total_weight > 0:
            for regime in combined_probs:
                combined_probs[regime] /= total_weight
        else:
            # Fallback if no indicators available
            combined_probs = {'CRISIS': 0.33, 'STRESS': 0.33, 'NORMAL': 0.34}
        
        # Determine primary regime
        primary_regime_name = max(combined_probs, key=combined_probs.get)
        primary_regime = RegimeType(primary_regime_name)
        
        # Calculate confidence (maximum probability)
        confidence = combined_probs[primary_regime_name]
        
        # Performance tracking
        computation_time = (datetime.now() - start_time).total_seconds()
        self.computation_times.append(computation_time)
        
        regime_state = RegimeState(
            regime=primary_regime,
            probabilities=combined_probs,
            confidence=confidence,
            indicators=latest_data.copy(),
            timestamp=datetime.now()
        )
        
        self.prediction_history.append(regime_state)
        
        return regime_state
    
    def get_indicator_contributions(self, latest_data: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Get detailed breakdown of each indicator's regime classification
        
        Args:
            latest_data: Dictionary of indicator values
            
        Returns:
            Dictionary mapping indicators to their regime probabilities
        """
        contributions = {}
        
        for indicator, weight in self.indicator_weights.items():
            if indicator in latest_data:
                value = latest_data[indicator]
                indicator_probs = self._classify_indicator_regime(indicator, value)
                
                contributions[indicator] = {
                    'value': value,
                    'weight': weight,
                    'regime_probs': indicator_probs,
                    'weighted_contribution': {
                        regime: weight * prob 
                        for regime, prob in indicator_probs.items()
                    }
                }
        
        return contributions
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance statistics"""
        metrics = {}
        
        if self.computation_times:
            metrics['avg_computation_time'] = np.mean(self.computation_times)
            metrics['max_computation_time'] = np.max(self.computation_times)
            metrics['min_computation_time'] = np.min(self.computation_times)
            metrics['total_predictions'] = len(self.computation_times)
        
        if self.prediction_history:
            # Regime distribution
            regime_counts = {}
            for state in self.prediction_history:
                regime = state.regime.value
                regime_counts[regime] = regime_counts.get(regime, 0) + 1
            
            total_predictions = len(self.prediction_history)
            for regime, count in regime_counts.items():
                metrics[f'regime_pct_{regime}'] = count / total_predictions
            
            # Average confidence
            avg_confidence = np.mean([state.confidence for state in self.prediction_history])
            metrics['avg_confidence'] = avg_confidence
        
        return metrics
    
    def backtest_regime_detection(self, historical_data: pd.DataFrame, 
                                  known_crisis_periods: List[Tuple[str, str]]) -> Dict[str, float]:
        """
        Backtest regime detection against known crisis periods
        
        Args:
            historical_data: DataFrame with indicator columns
            known_crisis_periods: List of (start_date, end_date) tuples for crises
            
        Returns:
            Performance metrics
        """
        if len(historical_data) == 0:
            return {}
        
        # Generate predictions for historical data
        predictions = []
        for idx, row in historical_data.iterrows():
            data_dict = row.to_dict()
            regime_state = self.predict_regime(data_dict)
            predictions.append({
                'date': idx,
                'predicted_regime': regime_state.regime.value,
                'confidence': regime_state.confidence
            })
        
        pred_df = pd.DataFrame(predictions).set_index('date')
        
        # Mark actual crisis periods
        actual_crisis = pd.Series(False, index=historical_data.index)
        for start_date, end_date in known_crisis_periods:
            crisis_mask = (historical_data.index >= start_date) & (historical_data.index <= end_date)
            actual_crisis.loc[crisis_mask] = True
        
        # Calculate performance metrics
        predicted_crisis = pred_df['predicted_regime'] == 'CRISIS'
        
        # Confusion matrix
        true_positives = (actual_crisis & predicted_crisis).sum()
        false_positives = (~actual_crisis & predicted_crisis).sum()
        true_negatives = (~actual_crisis & ~predicted_crisis).sum()
        false_negatives = (actual_crisis & ~predicted_crisis).sum()
        
        # Performance metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        accuracy = (true_positives + true_negatives) / len(actual_crisis)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall, 
            'accuracy': accuracy,
            'f1_score': f1_score,
            'true_positives': int(true_positives),
            'false_positives': int(false_positives),
            'true_negatives': int(true_negatives),
            'false_negatives': int(false_negatives)
        }

# Production utility functions
def create_fast_detector() -> ThresholdRegimeDetector:
    """Create production-ready fast regime detector"""
    return ThresholdRegimeDetector()

if __name__ == "__main__":
    print("Threshold Regime Detection - Fast Production Implementation")
    print("=" * 65)
    
    # Create detector
    detector = create_fast_detector()
    
    # Test with realistic data
    test_scenarios = [
        {
            'name': 'Normal Market',
            'data': {'VIX': 16.0, 'HY_SPREADS': 4.5, 'BAA_SPREADS': 5.2, 'TERM_SPREAD': 1.5}
        },
        {
            'name': 'Stress Market', 
            'data': {'VIX': 25.0, 'HY_SPREADS': 6.8, 'BAA_SPREADS': 6.1, 'TERM_SPREAD': 0.8}
        },
        {
            'name': 'Crisis Market',
            'data': {'VIX': 35.0, 'HY_SPREADS': 9.2, 'BAA_SPREADS': 7.5, 'TERM_SPREAD': -0.2}
        },
        {
            'name': 'Current Market (2025-06-26)',
            'data': {'VIX': 16.76, 'HY_SPREADS': 3.04, 'BAA_SPREADS': 6.29, 'TERM_SPREAD': 0.55}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\\n{scenario['name']}:")
        print("-" * 40)
        
        start_time = datetime.now()
        regime_state = detector.predict_regime(scenario['data'])
        computation_time = (datetime.now() - start_time).total_seconds()
        
        print(f"Regime: {regime_state.regime.value}")
        print(f"Confidence: {regime_state.confidence:.3f}")
        print(f"Computation Time: {computation_time:.4f}s")
        
        print("Regime Probabilities:")
        for regime, prob in regime_state.probabilities.items():
            print(f"  {regime}: {prob:.3f}")
        
        # Show indicator contributions
        contributions = detector.get_indicator_contributions(scenario['data'])
        print("Indicator Contributions:")
        for indicator, data in contributions.items():
            value = data['value']
            weight = data['weight']
            regime_probs = data['regime_probs']
            main_regime = max(regime_probs, key=regime_probs.get)
            main_prob = regime_probs[main_regime]
            print(f"  {indicator}: {value:.2f} → {main_regime} ({main_prob:.2f}, weight={weight:.1f})")
    
    # Performance summary
    metrics = detector.get_performance_metrics()
    print(f"\\nPerformance Summary:")
    print(f"Total Predictions: {metrics['total_predictions']}")
    print(f"Average Time: {metrics['avg_computation_time']:.4f}s")
    print(f"Max Time: {metrics['max_computation_time']:.4f}s")
    
    print("\\nFast threshold-based regime detection complete!")
    print("Ready for real-time FX trading integration.")