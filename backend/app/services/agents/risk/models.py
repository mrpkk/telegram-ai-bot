import numpy as np
from typing import List, Dict

class VaRCalculator:
    """Расчёт Value at Risk (VaR)."""

    @staticmethod
    def calculate(returns: List[float], confidence: float = 0.95) -> float:
        return -np.percentile(returns, 100 * (1 - confidence))

class StressTester:
    """Стресс-тестирование портфеля."""

    @staticmethod
    def run(total_value: float, scenarios: Dict[str, float]) -> Dict[str, float]:
        results = {}
        for name, change in scenarios.items():
            results[name] = total_value * (1 + change)
        return results