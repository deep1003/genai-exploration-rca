"""Compatibility for archived notebooks without modifying their source cells."""
import matplotlib
from matplotlib import cm


def legacy_get_cmap(name=None, lut=None):
    """Preserve the legacy name/default/Colormap and optional LUT interface."""
    cmap = matplotlib.colormaps.get_cmap(name)
    return cmap.resampled(lut) if lut is not None else cmap


def install_legacy_colormap_api():
    if not callable(getattr(cm, 'get_cmap', None)):
        cm.get_cmap = legacy_get_cmap

