import React from 'react';
import { motion } from 'framer-motion';

interface RiskMetric {
  label: string;
  value: string;
  change: string;
  trend?: 'up' | 'down' | 'stable';
}

const RiskMetricCard: React.FC<{ metric: RiskMetric }> = ({ metric }) => {
  const isPositive = metric.change.startsWith('+');
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3"
    >
      <p className="text-sm text-gray-600 dark:text-gray-400">{metric.label}</p>
      <p className="text-xl font-bold text-gray-900 dark:text-white">
        {metric.value}
      </p>
      <p className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {metric.change}
      </p>
    </motion.div>
  );
};

export const RiskManagementView: React.FC = () => {
  const riskMetrics: RiskMetric[] = [
    { label: "VaR (95%)", value: "$2.4M", change: "+0.2%" },
    { label: "CVaR", value: "$3.8M", change: "-0.1%" },
    { label: "Beta", value: "1.23", change: "+0.05" },
    { label: "Sharpe Ratio", value: "1.89", change: "+0.12" },
    { label: "Max Drawdown", value: "-12.3%", change: "-0.8%" },
    { label: "Sortino Ratio", value: "2.15", change: "+0.08" }
  ];

  const aiPredictions = [
    { model: "LSTM Risk Model", prediction: "Elevated market volatility expected", confidence: 87 },
    { model: "XGBoost Classifier", prediction: "Low default probability", confidence: 92 },
    { model: "Neural Network", prediction: "Optimal hedge ratio: 0.73", confidence: 78 }
  ];

  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Risk Management</h3>
      
      {/* Risk Metrics Grid - Exact Portfolio style */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        {riskMetrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <RiskMetricCard metric={metric} />
          </motion.div>
        ))}
      </div>

      {/* Risk Analysis Table - Matching Portfolio table style */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-white dark:bg-gray-800">
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">Model</th>
              <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">Prediction</th>
              <th className="text-right py-2 px-3 font-medium text-gray-700 dark:text-gray-300">Confidence</th>
              <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">Status</th>
            </tr>
          </thead>
          <tbody>
            {aiPredictions.map((prediction, index) => (
              <motion.tr
                key={prediction.model}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <td className="py-2 px-3 font-medium text-gray-900 dark:text-white">{prediction.model}</td>
                <td className="py-2 px-3 text-gray-700 dark:text-gray-300">{prediction.prediction}</td>
                <td className={`py-2 px-3 text-right font-medium ${
                  prediction.confidence >= 85 ? 'text-green-600' : 
                  prediction.confidence >= 70 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {prediction.confidence}%
                </td>
                <td className="py-2 px-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    prediction.confidence >= 85 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    prediction.confidence >= 70 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}>
                    {prediction.confidence >= 85 ? 'HIGH' : prediction.confidence >= 70 ? 'MEDIUM' : 'LOW'}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};