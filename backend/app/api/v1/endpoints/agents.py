from fastapi import APIRouter, HTTPException

from app.services.agents.risk.models import VaRCalculator, StressTester
from app.core.config import DEFILLAMA_YIELDS_URL

router = APIRouter()


@router.post("/trading/execute")
async def execute_trade(strategy: str = "dca", amount: float = 1000.0):
    """Исполнение торговой стратегии."""
    raise HTTPException(
        status_code=501,
        detail="Торговая интеграция (биржа/кошелёк) отключена в демо-режиме. "
               "В боевой версии подключается DEX/CEX API для исполнения ордеров."
    )


@router.get("/risk/var")
async def calculate_var(returns: str = "-2,-1,0.5,1.5,3", confidence: float = 0.95):
    """Value at Risk по историческим доходностям (%)."""
    try:
        series = [float(x.strip()) for x in returns.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(400, "returns должны быть числами через запятую")
    if not series:
        raise HTTPException(400, "Пустой ряд доходностей")
    var = VaRCalculator.calculate(series, confidence)
    return {
        "confidence": confidence,
        "var_percent": round(var, 2),
        "observations": len(series),
        "interpretation": f"С вероятностью {confidence:.0%} суточный убыток не превысит {abs(var):.2f}%"
    }


@router.get("/risk/stress-test")
async def stress_test(total_value: float = 10000.0):
    """Стресс-тест портфеля в сценариях кризиса."""
    scenarios = {
        "flash_crash_-10%": -0.10,
        "correction_-20%": -0.20,
        "bear_market_-40%": -0.40,
        "black_swan_-60%": -0.60,
    }
    results = StressTester.run(total_value, scenarios)
    return {
        "total_value": total_value,
        "scenarios": {name: round(value, 2) for name, value in results.items()},
    }


@router.post("/yield/optimize")
async def optimize_yield(chain: str = "ethereum", limit: int = 5):
    """Оптимизация доходности — топ-пулы по APY (DeFiLlama, без ключей)."""
    import httpx

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(DEFILLAMA_YIELDS_URL)
            resp.raise_for_status()
            pools = resp.json().get("data", [])
        except Exception as e:
            raise HTTPException(502, f"DeFiLlama недоступен: {e}")

    chain_filter = chain.lower()
    candidates = [
        p for p in pools
        if p.get("chain", "").lower() == chain_filter and p.get("apy", 0) and p.get("tvlUsd", 0)
    ]
    candidates.sort(key=lambda p: (p.get("apy", 0), p.get("tvlUsd", 0)), reverse=True)

    top = candidates[:limit]
    return {
        "chain": chain,
        "recommendations": [
            {
                "project": p.get("project"),
                "symbol": p.get("symbol"),
                "apy": round(p.get("apy", 0), 2),
                "tvl_usd": round(p.get("tvlUsd", 0)),
                "pool": p.get("pool"),
            }
            for p in top
        ],
    }
