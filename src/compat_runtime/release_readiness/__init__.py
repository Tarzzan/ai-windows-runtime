"""Release readiness package."""

__all__ = [
    "build_compatibility_matrix",
    "build_alpha_release_checklist",
    "build_release_bundle_manifest",
]


def build_compatibility_matrix(*args, **kwargs):
    from compat_runtime.release_readiness.cli import build_compatibility_matrix as _impl

    return _impl(*args, **kwargs)


def build_alpha_release_checklist(*args, **kwargs):
    from compat_runtime.release_readiness.cli import build_alpha_release_checklist as _impl

    return _impl(*args, **kwargs)


def build_release_bundle_manifest(*args, **kwargs):
    from compat_runtime.release_readiness.cli import build_release_bundle_manifest as _impl

    return _impl(*args, **kwargs)
