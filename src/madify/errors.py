"""Domain and application errors with explicit failure modes.

All expected Madify failures subclass :class:`MadifyError` so the CLI can
map them to a non-zero exit without catching unexpected exceptions.
"""


class MadifyError(Exception):
    """Base error for expected Madify failures."""


class UnsupportedMediaError(MadifyError):
    """Raised when a path is not a supported image, PSD, or video file."""


class AssetNotFoundError(MadifyError):
    """Raised when a requested catalog asset does not exist or is ambiguous."""


class MetadataValidationError(MadifyError):
    """Raised when title, description, or tags fail validation rules."""


class RenameError(MadifyError):
    """Raised when a file cannot be renamed (missing title, collision, FS)."""


class CatalogError(MadifyError):
    """Raised when a catalog store operation fails."""


class ScanError(MadifyError):
    """Raised when a scan root is missing or not a directory."""
