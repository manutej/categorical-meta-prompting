"""
Example 1: Recursive Portfolio Optimization with Categorical Meta-Prompting
============================================================================

This example demonstrates:
- RMP (Recursive Meta-Prompting) monad for iterative portfolio refinement
- Quality-enriched categories for risk-return tracking
- Comonad for extracting market context
- Real data from Yahoo Finance

Categorical Structures Used:
- Monad: Portfolio improvement iterations with Kleisli composition
- Enriched Category: [0,1] quality tracking through Sharpe ratio
- Comonad: Context extraction from market history

Data Source: Yahoo Finance (yfinance) - Free, real market data
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Optional
from datetime import datetime, timedelta
import json

# For real data - install with: pip install yfinance pandas numpy
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False
    print("Note: Install yfinance for real data: pip install yfinance pandas numpy")


# =============================================================================
# CATEGORICAL FOUNDATIONS
# =============================================================================

@dataclass
class QualityScore:
    """
    Quality in [0,1]-enriched category.

    For portfolios, quality combines:
    - risk_adjusted_return: Sharpe ratio normalized to [0,1]
    - diversification: How well distributed across assets
    - volatility_target: How close to target volatility
    """
    value: float
    risk_adjusted_return: float = 0.0
    diversification: float = 0.0
    volatility_alignment: float = 0.0

    def __post_init__(self):
        assert 0 <= self.value <= 1, f"Quality must be in [0,1], got {self.value}"

    @classmethod
    def from_components(cls, rar: float, div: float, vol: float) -> 'QualityScore':
        """Aggregate components with weights."""
        # Weights for different objectives
        value = 0.5 * rar + 0.3 * div + 0.2 * vol
        return cls(value=min(1.0, max(0.0, value)),
                   risk_adjusted_return=rar,
                   diversification=div,
                   volatility_alignment=vol)


@dataclass
class Portfolio:
    """
    Portfolio as an object in our category.

    Morphisms between portfolios represent rebalancing operations.
    """
    weights: Dict[str, float]  # ticker -> weight (sum to 1.0)
    expected_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0

    def __post_init__(self):
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            # Normalize weights
            self.weights = {k: v/total for k, v in self.weights.items()}


@dataclass
class MonadPortfolio:
    """
    Monad wrapper for portfolio in refinement context.

    Laws:
    - return: Portfolio → MonadPortfolio
    - bind: MonadPortfolio → (Portfolio → MonadPortfolio) → MonadPortfolio
    """
    portfolio: Portfolio
    quality: QualityScore
    iteration: int = 0
    history: List['MonadPortfolio'] = field(default_factory=list)

    @staticmethod
    def unit(portfolio: Portfolio, quality: QualityScore) -> 'MonadPortfolio':
        """Return: lift portfolio into monadic context."""
        return MonadPortfolio(portfolio=portfolio, quality=quality, iteration=0)

    def bind(self, f: Callable[[Portfolio], 'MonadPortfolio']) -> 'MonadPortfolio':
        """Bind: apply improvement function, tracking history."""
        improved = f(self.portfolio)
        improved.iteration = self.iteration + 1
        improved.history = self.history + [self]
        return improved


@dataclass
class MarketContext:
    """
    Comonad for market context extraction.

    extract: Context → CurrentState
    extend: (Context → A) → Context → Context[A]
    """
    returns: pd.DataFrame  # Historical returns
    correlation: pd.DataFrame  # Correlation matrix
    current_prices: Dict[str, float]
    volatilities: Dict[str, float]
    market_regime: str  # "bull", "bear", "neutral"

    def extract(self) -> Dict[str, float]:
        """Extract current market state."""
        return {
            'avg_return': self.returns.mean().mean(),
            'avg_volatility': np.mean(list(self.volatilities.values())),
            'regime': self.market_regime
        }

    def extend(self, f: Callable[['MarketContext'], 'MarketContext']) -> 'MarketContext':
        """Apply context-aware transformation."""
        return f(self)


# =============================================================================
# REAL DATA FETCHING
# =============================================================================

def fetch_market_data(
    tickers: List[str],
    period: str = "2y"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch real market data from Yahoo Finance.

    Returns:
        - prices: Daily adjusted close prices
        - returns: Daily returns
    """
    if not HAS_YFINANCE:
        # Return mock data for demonstration
        return _mock_market_data(tickers)

    print(f"Fetching data for {tickers}...")
    data = yf.download(tickers, period=period, progress=False)['Adj Close']

    if isinstance(data, pd.Series):
        data = data.to_frame()

    returns = data.pct_change().dropna()

    print(f"Fetched {len(returns)} days of data")
    return data, returns


def _mock_market_data(tickers: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate mock data when yfinance unavailable."""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=500, freq='D')

    # Generate correlated returns
    n = len(tickers)
    mean_returns = np.random.uniform(0.0005, 0.001, n)
    volatilities = np.random.uniform(0.01, 0.03, n)

    returns_data = {}
    for i, ticker in enumerate(tickers):
        returns_data[ticker] = np.random.normal(
            mean_returns[i], volatilities[i], len(dates)
        )

    returns = pd.DataFrame(returns_data, index=dates)
    prices = (1 + returns).cumprod() * 100

    return prices, returns


def build_market_context(
    returns: pd.DataFrame,
    prices: pd.DataFrame
) -> MarketContext:
    """
    Build comonadic market context from data.

    Categorical interpretation: Extract rich context from raw observations.
    """
    correlation = returns.corr()
    volatilities = {col: returns[col].std() * np.sqrt(252) for col in returns.columns}
    current_prices = {col: prices[col].iloc[-1] for col in prices.columns}

    # Determine market regime (simple momentum-based)
    recent_return = returns.mean(axis=1).tail(30).sum()
    if recent_return > 0.02:
        regime = "bull"
    elif recent_return < -0.02:
        regime = "bear"
    else:
        regime = "neutral"

    return MarketContext(
        returns=returns,
        correlation=correlation,
        current_prices=current_prices,
        volatilities=volatilities,
        market_regime=regime
    )


# =============================================================================
# PORTFOLIO QUALITY EVALUATION (Enriched Category Morphism)
# =============================================================================

def evaluate_portfolio_quality(
    portfolio: Portfolio,
    context: MarketContext,
    risk_free_rate: float = 0.05
) -> QualityScore:
    """
    Evaluate portfolio quality in [0,1]-enriched category.

    This is a functor: Portfolio × Context → QualityScore
    """
    weights = np.array([portfolio.weights.get(t, 0) for t in context.returns.columns])

    # Calculate portfolio metrics
    expected_return = (context.returns.mean() * weights).sum() * 252
    portfolio_vol = np.sqrt(
        weights @ context.returns.cov() @ weights * 252
    )

    # Sharpe ratio (risk-adjusted return)
    sharpe = (expected_return - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0

    # Normalize sharpe to [0,1] (typical range -1 to 3)
    normalized_sharpe = min(1.0, max(0.0, (sharpe + 1) / 4))

    # Diversification score (entropy of weights)
    non_zero_weights = weights[weights > 0.01]
    if len(non_zero_weights) > 0:
        entropy = -np.sum(non_zero_weights * np.log(non_zero_weights + 1e-10))
        max_entropy = np.log(len(non_zero_weights))
        diversification = entropy / max_entropy if max_entropy > 0 else 0
    else:
        diversification = 0

    # Volatility alignment (how close to target 15% annualized)
    target_vol = 0.15
    vol_diff = abs(portfolio_vol - target_vol)
    vol_alignment = max(0, 1 - vol_diff / target_vol)

    # Update portfolio metrics
    portfolio.expected_return = expected_return
    portfolio.volatility = portfolio_vol
    portfolio.sharpe_ratio = sharpe

    return QualityScore.from_components(
        rar=normalized_sharpe,
        div=diversification,
        vol=vol_alignment
    )


# =============================================================================
# RMP IMPROVEMENT FUNCTIONS (Kleisli Arrows)
# =============================================================================

def improve_for_sharpe(
    portfolio: Portfolio,
    context: MarketContext,
    learning_rate: float = 0.2
) -> Portfolio:
    """
    Kleisli arrow: Portfolio → MonadPortfolio

    Improves portfolio by shifting weight toward high Sharpe assets.
    """
    tickers = list(portfolio.weights.keys())

    # Calculate individual asset Sharpe ratios
    asset_sharpes = {}
    for ticker in tickers:
        if ticker in context.returns.columns:
            ret = context.returns[ticker].mean() * 252
            vol = context.returns[ticker].std() * np.sqrt(252)
            asset_sharpes[ticker] = (ret - 0.05) / vol if vol > 0 else 0

    # Adjust weights toward higher Sharpe assets
    new_weights = portfolio.weights.copy()
    avg_sharpe = np.mean(list(asset_sharpes.values()))

    for ticker in tickers:
        if ticker in asset_sharpes:
            sharpe_diff = asset_sharpes[ticker] - avg_sharpe
            adjustment = learning_rate * sharpe_diff / 10  # Scale adjustment
            new_weights[ticker] = max(0.01, new_weights[ticker] + adjustment)

    # Renormalize
    total = sum(new_weights.values())
    new_weights = {k: v/total for k, v in new_weights.items()}

    return Portfolio(weights=new_weights)


def improve_for_diversification(
    portfolio: Portfolio,
    context: MarketContext,
    strength: float = 0.3
) -> Portfolio:
    """
    Kleisli arrow improving diversification.

    Moves weights toward equal distribution.
    """
    tickers = list(portfolio.weights.keys())
    equal_weight = 1.0 / len(tickers)

    new_weights = {}
    for ticker in tickers:
        current = portfolio.weights[ticker]
        # Move toward equal weight
        new_weights[ticker] = current + strength * (equal_weight - current)

    return Portfolio(weights=new_weights)


def improve_for_volatility_target(
    portfolio: Portfolio,
    context: MarketContext,
    target_vol: float = 0.15,
    strength: float = 0.3
) -> Portfolio:
    """
    Kleisli arrow targeting specific volatility.

    Scales position sizes to hit target volatility.
    """
    weights = np.array([portfolio.weights.get(t, 0) for t in context.returns.columns])

    # Current portfolio volatility
    current_vol = np.sqrt(weights @ context.returns.cov() @ weights * 252)

    if current_vol > 0:
        # Scale factor to hit target
        scale = target_vol / current_vol
        # Dampen the adjustment
        adjusted_scale = 1 + strength * (scale - 1)

        new_weights = {
            t: portfolio.weights[t] * adjusted_scale
            for t in portfolio.weights
        }
        # Renormalize
        total = sum(new_weights.values())
        new_weights = {k: max(0.01, v/total) for k, v in new_weights.items()}
        return Portfolio(weights=new_weights)

    return portfolio


# =============================================================================
# RECURSIVE META-PROMPTING ENGINE
# =============================================================================

class PortfolioRMPEngine:
    """
    Categorical Meta-Prompting Engine for Portfolio Optimization.

    Integrates:
    - Monad: Recursive improvement with Kleisli composition
    - Enriched Category: Quality tracking in [0,1]
    - Comonad: Market context extraction
    """

    def __init__(
        self,
        tickers: List[str],
        quality_threshold: float = 0.85,
        max_iterations: int = 10
    ):
        self.tickers = tickers
        self.quality_threshold = quality_threshold
        self.max_iterations = max_iterations

        # Fetch market data
        self.prices, self.returns = fetch_market_data(tickers)
        self.context = build_market_context(self.returns, self.prices)

        print(f"\nMarket Context:")
        print(f"  Regime: {self.context.market_regime}")
        print(f"  Avg Volatility: {np.mean(list(self.context.volatilities.values())):.2%}")

    def optimize(
        self,
        initial_weights: Optional[Dict[str, float]] = None
    ) -> Tuple[Portfolio, List[MonadPortfolio]]:
        """
        Execute RMP optimization loop.

        Returns:
            - Optimized portfolio
            - Full history of refinements (for provenance)
        """
        # Initialize with equal weights if not provided
        if initial_weights is None:
            initial_weights = {t: 1.0/len(self.tickers) for t in self.tickers}

        initial_portfolio = Portfolio(weights=initial_weights)
        initial_quality = evaluate_portfolio_quality(
            initial_portfolio, self.context
        )

        print(f"\n{'='*60}")
        print("RECURSIVE META-PROMPTING OPTIMIZATION")
        print(f"{'='*60}")
        print(f"Initial Quality: {initial_quality.value:.4f}")
        print(f"  Sharpe Component: {initial_quality.risk_adjusted_return:.4f}")
        print(f"  Diversification:  {initial_quality.diversification:.4f}")
        print(f"  Vol Alignment:    {initial_quality.volatility_alignment:.4f}")

        # Initialize monad
        current = MonadPortfolio.unit(initial_portfolio, initial_quality)
        history = [current]

        # RMP Loop
        for iteration in range(self.max_iterations):
            if current.quality.value >= self.quality_threshold:
                print(f"\n✓ Quality threshold {self.quality_threshold} reached!")
                break

            # Compose improvement functions (Kleisli composition)
            def combined_improve(p: Portfolio) -> MonadPortfolio:
                # Apply improvements in sequence
                p1 = improve_for_sharpe(p, self.context, learning_rate=0.15)
                p2 = improve_for_diversification(p1, self.context, strength=0.1)
                p3 = improve_for_volatility_target(p2, self.context, strength=0.1)

                quality = evaluate_portfolio_quality(p3, self.context)
                return MonadPortfolio.unit(p3, quality)

            # Apply monadic bind
            current = current.bind(combined_improve)
            history.append(current)

            quality_change = current.quality.value - history[-2].quality.value
            print(f"\nIteration {iteration + 1}:")
            print(f"  Quality: {current.quality.value:.4f} ({'+' if quality_change >= 0 else ''}{quality_change:.4f})")
            print(f"  Sharpe: {current.portfolio.sharpe_ratio:.3f}")
            print(f"  Vol: {current.portfolio.volatility:.2%}")

        print(f"\n{'='*60}")
        print("FINAL OPTIMIZED PORTFOLIO")
        print(f"{'='*60}")
        for ticker, weight in sorted(
            current.portfolio.weights.items(),
            key=lambda x: -x[1]
        ):
            print(f"  {ticker}: {weight:.2%}")

        print(f"\nMetrics:")
        print(f"  Expected Return: {current.portfolio.expected_return:.2%}")
        print(f"  Volatility: {current.portfolio.volatility:.2%}")
        print(f"  Sharpe Ratio: {current.portfolio.sharpe_ratio:.3f}")
        print(f"  Quality Score: {current.quality.value:.4f}")
        print(f"  Iterations: {len(history)}")

        return current.portfolio, history


# =============================================================================
# MAIN: Run the optimization with real data
# =============================================================================

def main():
    """
    Demonstrate categorical portfolio optimization with real data.
    """
    print("="*60)
    print("CATEGORICAL META-PROMPTING: PORTFOLIO OPTIMIZATION")
    print("="*60)
    print("\nUsing real market data from Yahoo Finance")

    # Diverse set of ETFs representing different asset classes
    tickers = [
        "SPY",   # S&P 500
        "QQQ",   # NASDAQ 100
        "IWM",   # Russell 2000 (small cap)
        "EFA",   # International developed
        "EEM",   # Emerging markets
        "TLT",   # Long-term treasury
        "GLD",   # Gold
        "VNQ",   # REITs
    ]

    engine = PortfolioRMPEngine(
        tickers=tickers,
        quality_threshold=0.85,
        max_iterations=15
    )

    optimized_portfolio, history = engine.optimize()

    # Demonstrate comonadic context extraction
    print(f"\n{'='*60}")
    print("COMONADIC CONTEXT EXTRACTION")
    print(f"{'='*60}")

    extracted = engine.context.extract()
    print(f"Current Market State:")
    print(f"  Average Return: {extracted['avg_return']:.4f}")
    print(f"  Average Volatility: {extracted['avg_volatility']:.2%}")
    print(f"  Market Regime: {extracted['regime']}")

    # Show quality improvement trajectory
    print(f"\n{'='*60}")
    print("QUALITY IMPROVEMENT TRAJECTORY")
    print(f"{'='*60}")

    for i, mp in enumerate(history):
        bar_length = int(mp.quality.value * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"  {i:2d}: [{bar}] {mp.quality.value:.4f}")

    return optimized_portfolio, history


if __name__ == "__main__":
    portfolio, history = main()
