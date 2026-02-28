"""Productization readiness package."""

__all__ = ["build_productization_readiness_report"]


def build_productization_readiness_report(*args, **kwargs):
    from compat_runtime.productization.cli import build_productization_readiness_report as _impl

    return _impl(*args, **kwargs)
