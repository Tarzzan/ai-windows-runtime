"""KPI tracker package."""

__all__ = ["build_kpi_report", "build_dashboard_timeseries"]


def build_kpi_report(*args, **kwargs):
    from compat_runtime.kpi_tracker.cli import build_kpi_report as _impl

    return _impl(*args, **kwargs)


def build_dashboard_timeseries(*args, **kwargs):
    from compat_runtime.kpi_tracker.cli import build_dashboard_timeseries as _impl

    return _impl(*args, **kwargs)
