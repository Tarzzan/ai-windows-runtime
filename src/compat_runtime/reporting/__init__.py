"""Execution report generation package."""

__all__ = ["build_execution_report"]


def build_execution_report(*args, **kwargs):
    from compat_runtime.reporting.cli import build_execution_report as _impl

    return _impl(*args, **kwargs)
