"""
pylidc configuration module.

This module provides programmatic configuration for pylidc, allowing users
to set the DICOM path via Python code instead of (or in addition to) config files.

Usage:
    import pylidc as pl
    
    # Option 1: Set path before using any scan methods
    pl.config.set_dicom_path("/path/to/LIDC-IDRI")
    
    # Option 2: Use context manager for temporary path
    with pl.config.dicom_path("/path/to/LIDC-IDRI"):
        scan = pl.query(pl.Scan).first()
        vol = scan.to_volume()
    
    # Option 3: Pass path directly to functions (where supported)
    scan.get_path_to_dicom_files(dicom_path="/path/to/LIDC-IDRI")
"""

import os
from contextlib import contextmanager
from typing import Optional

# Global configuration state
_config = {
    'dicom_path': None,
    'warn_on_missing_path': True,
}


def set_dicom_path(path: str) -> None:
    """
    Set the path to LIDC-IDRI DICOM files programmatically.
    
    This overrides any path set in the config file (~/.pylidcrc or ~/pylidc.conf).
    
    Args:
        path: Path to the LIDC-IDRI directory containing patient folders
              (e.g., "/data/LIDC-IDRI" which contains "LIDC-IDRI-0001/", etc.)
    
    Example:
        import pylidc as pl
        pl.config.set_dicom_path("/path/to/LIDC-IDRI")
        
        scan = pl.query(pl.Scan).first()
        vol = scan.to_volume()  # Now works without config file
    """
    if path is not None:
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        
        if not os.path.isdir(path):
            raise ValueError(f"DICOM path does not exist: {path}")
    
    _config['dicom_path'] = path


def get_dicom_path() -> Optional[str]:
    """
    Get the currently configured DICOM path.
    
    Returns the programmatically set path if available, otherwise None.
    The Scan class will fall back to config file if this returns None.
    
    Returns:
        Path to LIDC-IDRI directory, or None if not set programmatically.
    """
    return _config['dicom_path']


def clear_dicom_path() -> None:
    """
    Clear the programmatically set DICOM path.
    
    After calling this, pylidc will fall back to using the config file.
    """
    _config['dicom_path'] = None


def set_warn_on_missing_path(warn: bool) -> None:
    """
    Set whether to warn when DICOM path is not configured.
    
    Args:
        warn: If True, print warning when path is missing. Default is True.
    """
    _config['warn_on_missing_path'] = warn


def get_warn_on_missing_path() -> bool:
    """Get the current warning setting."""
    return _config['warn_on_missing_path']


@contextmanager
def dicom_path(path: str):
    """
    Context manager for temporarily setting the DICOM path.
    
    Useful when you need to work with DICOM files from a specific location
    without permanently changing the global configuration.
    
    Args:
        path: Path to the LIDC-IDRI directory
        
    Example:
        import pylidc as pl
        
        with pl.config.dicom_path("/path/to/LIDC-IDRI"):
            scan = pl.query(pl.Scan).first()
            vol = scan.to_volume()
        
        # Path is restored to previous value after the block
    """
    old_path = _config['dicom_path']
    try:
        set_dicom_path(path)
        yield
    finally:
        _config['dicom_path'] = old_path


def configure(dicom_path: Optional[str] = None, 
              warn_on_missing_path: bool = True) -> None:
    """
    Configure pylidc settings in one call.
    
    Args:
        dicom_path: Path to LIDC-IDRI DICOM files (optional)
        warn_on_missing_path: Whether to warn when path is not set (default True)
    
    Example:
        import pylidc as pl
        pl.config.configure(
            dicom_path="/path/to/LIDC-IDRI",
            warn_on_missing_path=False
        )
    """
    if dicom_path is not None:
        set_dicom_path(dicom_path)
    set_warn_on_missing_path(warn_on_missing_path)


# For convenience, allow direct attribute access
class _ConfigModule:
    """Wrapper to allow `pl.config.dicom_path = ...` syntax."""
    
    def __init__(self):
        self._funcs = {
            'set_dicom_path': set_dicom_path,
            'get_dicom_path': get_dicom_path,
            'clear_dicom_path': clear_dicom_path,
            'set_warn_on_missing_path': set_warn_on_missing_path,
            'get_warn_on_missing_path': get_warn_on_missing_path,
            'dicom_path': dicom_path,
            'configure': configure,
        }
    
    def __getattr__(self, name):
        if name in self._funcs:
            return self._funcs[name]
        raise AttributeError(f"config has no attribute '{name}'")
    
    @property
    def path(self) -> Optional[str]:
        """Current DICOM path (read-only property)."""
        return get_dicom_path()
