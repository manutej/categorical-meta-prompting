"""
Monitoring and observability for categorical meta-prompting.

Provides quality-enriched metrics tracking with:
- Prometheus metrics export
- Quality degradation detection
- Execution trace logging
- Performance monitoring
"""

from .enriched_quality import (
    QualityMonitor,
    QualityMetrics,
    create_quality_monitor
)

__all__ = [
    "QualityMonitor",
    "QualityMetrics",
    "create_quality_monitor",
]
