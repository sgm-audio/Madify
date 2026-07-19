"""Domain and application errors with explicit failure modes."""


class MadifyError(Exception):
    """Base error for expected Madify failures."""


class UnsupportedMediaError(MadifyError):
    """Path is not a supported image, PSD, or video file."""


class AssetNotFoundError(MadifyError):
    """Requested catalog asset does not exist."""


class MetadataValidationError(MadifyError):
    """Title, description, or tags failed validation."""


class RenameError(MadifyError):
    """File cannot be renamed (missing title, collision, or filesystem failure)."""


class CatalogError(MadifyError):
    """Catalog store operation failed."""


class ScanError(MadifyError):
    """Scan root is missing or not a directory."""
