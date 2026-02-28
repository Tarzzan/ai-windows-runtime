"""Trend report generation package."""

__all__ = ["build_trend_report"]


def build_trend_report(*args, **kwargs):
    from compat_runtime.trend_report.cli import build_trend_report as _impl

    return _impl(*args, **kwargs)
