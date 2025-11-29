"""
Quality-Enriched Monitoring for Categorical Meta-Prompting.

Implements [0,1]-enriched category monitoring with:
- Tensor product quality tracking (min operation)
- Quality degradation detection
- Prometheus metrics export (optional)
- Execution trace analysis

Mathematical Foundation:
    - Quality scores form [0,1]-enriched category
    - Morphism composition via tensor product: q1 ⊗ q2 = min(q1, q2)
    - Quality degradation when successive iterations have declining scores

References:
    - de Wynter et al. (arXiv:2312.06562): Enriched categories for meta-prompting
    - L5 Meta-Prompt: Quality monitoring requirements
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import statistics
import logging

from ..categorical.types import QualityScore

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """
    Quality metrics for monitoring.

    Tracks:
        - Current quality and historical trends
        - Quality degradation indicators
        - Component-level quality breakdown
        - Statistical summaries
    """
    # Current state
    current_quality: float
    quality_components: Dict[str, float]

    # Historical trends
    quality_history: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)

    # Degradation detection
    degradation_detected: bool = False
    degradation_threshold: float = 0.1
    consecutive_degradations: int = 0

    # Statistics
    mean_quality: float = 0.0
    std_quality: float = 0.0
    min_quality: float = 1.0
    max_quality: float = 0.0

    # Metadata
    sample_count: int = 0
    last_update: Optional[datetime] = None

    def __post_init__(self):
        """Compute initial statistics."""
        self._update_statistics()

    def _update_statistics(self):
        """Update statistical metrics."""
        if self.quality_history:
            self.mean_quality = statistics.mean(self.quality_history)
            self.std_quality = (
                statistics.stdev(self.quality_history)
                if len(self.quality_history) > 1
                else 0.0
            )
            self.min_quality = min(self.quality_history)
            self.max_quality = max(self.quality_history)
            self.sample_count = len(self.quality_history)


class QualityMonitor:
    """
    Monitor for quality-enriched categorical meta-prompting.

    Tracks quality scores across executions and detects:
        - Quality degradation trends
        - Component-level quality issues
        - Statistical anomalies

    Uses [0,1]-enriched category theory:
        - Quality scores as morphisms in [0,1]
        - Composition via tensor product (min)
        - Degradation when successive min decreases

    Usage:
        ```python
        monitor = QualityMonitor(window_size=100)

        # Record quality
        monitor.record_quality(quality_score, execution_id="exec_001")

        # Check for degradation
        if monitor.is_degrading():
            print("Quality degradation detected!")

        # Get metrics
        metrics = monitor.get_metrics()
        print(f"Mean quality: {metrics.mean_quality}")
        ```
    """

    def __init__(
        self,
        window_size: int = 100,
        degradation_threshold: float = 0.1,
        alert_on_degradation: bool = True,
        export_prometheus: bool = False
    ):
        """
        Initialize quality monitor.

        Args:
            window_size: Number of recent samples to track
            degradation_threshold: Quality drop threshold for alerts
            alert_on_degradation: Log warnings on degradation
            export_prometheus: Export Prometheus metrics (requires prometheus_client)
        """
        self.window_size = window_size
        self.degradation_threshold = degradation_threshold
        self.alert_on_degradation = alert_on_degradation
        self.export_prometheus = export_prometheus

        # Circular buffers for windowed tracking
        self._quality_window = deque(maxlen=window_size)
        self._timestamp_window = deque(maxlen=window_size)
        self._components_window = deque(maxlen=window_size)

        # Global tracking
        self._all_qualities: List[float] = []
        self._all_timestamps: List[datetime] = []
        self._execution_ids: List[str] = []

        # Degradation tracking
        self._consecutive_degradations = 0
        self._last_quality: Optional[float] = None

        # Prometheus metrics (optional)
        self._prometheus_metrics = None
        if export_prometheus:
            self._init_prometheus()

        logger.info(
            f"QualityMonitor initialized: "
            f"window_size={window_size}, "
            f"degradation_threshold={degradation_threshold}"
        )

    def record_quality(
        self,
        quality_score: QualityScore,
        execution_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a quality score.

        Args:
            quality_score: Quality score to record
            execution_id: Optional execution identifier
            timestamp: Optional timestamp (defaults to now)
        """
        ts = timestamp or datetime.now()
        quality_value = quality_score.value

        # Add to windows
        self._quality_window.append(quality_value)
        self._timestamp_window.append(ts)
        self._components_window.append(quality_score.components)

        # Add to global tracking
        self._all_qualities.append(quality_value)
        self._all_timestamps.append(ts)
        if execution_id:
            self._execution_ids.append(execution_id)

        # Check for degradation
        if self._last_quality is not None:
            # Tensor product composition: q1 ⊗ q2 = min(q1, q2)
            composed_quality = min(self._last_quality, quality_value)

            # Degradation if composed quality significantly lower
            degradation = self._last_quality - quality_value

            if degradation > self.degradation_threshold:
                self._consecutive_degradations += 1

                if self.alert_on_degradation:
                    logger.warning(
                        f"Quality degradation detected: "
                        f"{self._last_quality:.3f} → {quality_value:.3f} "
                        f"(degradation={degradation:.3f}, "
                        f"consecutive={self._consecutive_degradations})"
                    )
            else:
                self._consecutive_degradations = 0

        self._last_quality = quality_value

        # Update Prometheus metrics if enabled
        if self._prometheus_metrics:
            self._update_prometheus(quality_score)

        logger.debug(
            f"Quality recorded: {quality_value:.3f} "
            f"(execution_id={execution_id}, timestamp={ts.isoformat()})"
        )

    def is_degrading(self, threshold: Optional[float] = None) -> bool:
        """
        Check if quality is degrading.

        Args:
            threshold: Optional custom threshold (uses config if not provided)

        Returns:
            True if consecutive degradations detected
        """
        thresh = threshold or self.degradation_threshold
        return self._consecutive_degradations >= 2

    def get_metrics(self) -> QualityMetrics:
        """
        Get current quality metrics.

        Returns:
            QualityMetrics with statistics and trends
        """
        if not self._quality_window:
            return QualityMetrics(
                current_quality=0.0,
                quality_components={}
            )

        # Current state
        current_quality = self._quality_window[-1]
        current_components = self._components_window[-1] if self._components_window else {}

        # Create metrics
        metrics = QualityMetrics(
            current_quality=current_quality,
            quality_components=current_components,
            quality_history=list(self._quality_window),
            timestamps=list(self._timestamp_window),
            degradation_detected=self.is_degrading(),
            degradation_threshold=self.degradation_threshold,
            consecutive_degradations=self._consecutive_degradations,
            last_update=self._timestamp_window[-1] if self._timestamp_window else None
        )

        return metrics

    def get_quality_trend(self, window: Optional[int] = None) -> str:
        """
        Analyze quality trend over window.

        Args:
            window: Number of recent samples (uses full window if not provided)

        Returns:
            "improving", "degrading", "stable", or "insufficient_data"
        """
        win = window or self.window_size

        if len(self._quality_window) < 3:
            return "insufficient_data"

        recent = list(self._quality_window)[-win:]

        # Simple linear regression
        n = len(recent)
        x = list(range(n))
        y = recent

        # Compute slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # Classify trend
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "degrading"
        else:
            return "stable"

    def get_component_breakdown(self) -> Dict[str, Dict[str, float]]:
        """
        Get quality component statistics.

        Returns:
            Dict mapping component name to statistics (mean, std, min, max)
        """
        if not self._components_window:
            return {}

        # Collect all component values
        component_values: Dict[str, List[float]] = {}

        for components in self._components_window:
            for name, value in components.items():
                if name not in component_values:
                    component_values[name] = []
                component_values[name].append(value)

        # Compute statistics per component
        breakdown = {}
        for name, values in component_values.items():
            breakdown[name] = {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0.0,
                'min': min(values),
                'max': max(values),
                'current': values[-1]
            }

        return breakdown

    def reset(self):
        """Reset monitoring state."""
        self._quality_window.clear()
        self._timestamp_window.clear()
        self._components_window.clear()
        self._all_qualities.clear()
        self._all_timestamps.clear()
        self._execution_ids.clear()
        self._consecutive_degradations = 0
        self._last_quality = None

        logger.info("QualityMonitor reset")

    def _init_prometheus(self):
        """
        Initialize Prometheus metrics.

        Requires prometheus_client package.
        """
        try:
            from prometheus_client import Counter, Histogram, Gauge

            self._prometheus_metrics = {
                'quality': Histogram(
                    'categorical_meta_prompting_quality',
                    'Quality score distribution',
                    buckets=[0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
                ),
                'degradations': Counter(
                    'categorical_meta_prompting_degradations_total',
                    'Total quality degradations detected'
                ),
                'current_quality': Gauge(
                    'categorical_meta_prompting_current_quality',
                    'Current quality score'
                )
            }

            logger.info("Prometheus metrics initialized")

        except ImportError:
            logger.warning(
                "prometheus_client not installed. "
                "Install with: pip install prometheus-client"
            )
            self.export_prometheus = False

    def _update_prometheus(self, quality_score: QualityScore):
        """Update Prometheus metrics."""
        if not self._prometheus_metrics:
            return

        metrics = self._prometheus_metrics

        # Update histogram
        metrics['quality'].observe(quality_score.value)

        # Update gauge
        metrics['current_quality'].set(quality_score.value)

        # Update degradation counter
        if self._consecutive_degradations > 0:
            metrics['degradations'].inc()


def create_quality_monitor(
    window_size: int = 100,
    degradation_threshold: float = 0.1,
    **kwargs
) -> QualityMonitor:
    """
    Factory function for quality monitor.

    Args:
        window_size: Number of recent samples to track
        degradation_threshold: Quality drop threshold
        **kwargs: Additional config options

    Returns:
        QualityMonitor instance
    """
    return QualityMonitor(
        window_size=window_size,
        degradation_threshold=degradation_threshold,
        **kwargs
    )
