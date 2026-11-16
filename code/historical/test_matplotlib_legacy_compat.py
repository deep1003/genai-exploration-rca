"""Smoke tests without creating figures or producing image output."""
from pathlib import Path
import json
import matplotlib
import numpy as np
from matplotlib import cm
from matplotlib_legacy_compat import install_legacy_colormap_api, legacy_get_cmap

install_legacy_colormap_api()
installed = cm.get_cmap
install_legacy_colormap_api()
assert cm.get_cmap is installed
expected = np.array([
    [31,119,180], [255,127,14], [44,160,44], [214,39,40],
    [148,103,189], [140,86,75], [227,119,194], [127,127,127],
    [188,189,34], [23,190,207],
], dtype=float) / 255
actual = cm.get_cmap('tab10')(np.arange(10))
np.testing.assert_allclose(actual[:,:3], expected, rtol=0, atol=1e-15)
np.testing.assert_array_equal(actual[:,3], np.ones(10))
np.testing.assert_array_equal(cm.get_cmap('tab10')(np.arange(10)), matplotlib.colormaps['tab10'](np.arange(10)))
np.testing.assert_array_equal(cm.get_cmap()(np.linspace(0,1,9)), matplotlib.colormaps[matplotlib.rcParams['image.cmap']](np.linspace(0,1,9)))
cmap = matplotlib.colormaps['tab10']
np.testing.assert_array_equal(legacy_get_cmap(cmap)(np.arange(10)), cmap(np.arange(10)))
assert cm.get_cmap('viridis', 5).N == 5
np.testing.assert_array_equal(cm.get_cmap('viridis',5)(np.arange(5)), matplotlib.colormaps['viridis'].resampled(5)(np.arange(5)))
try:
    cm.get_cmap('not_a_real_colormap_123')
except ValueError:
    pass
else:
    raise AssertionError('Unknown colormap must raise ValueError')
result = {'status':'passed','matplotlib_version':matplotlib.__version__,'checks':['tab10 exact RGBA values','registered palette equivalence','default palette','Colormap object input','LUT resampling','unknown-name error','idempotent installation'],'figures_created':0,'archived_notebook_modified':False}
root=Path(__file__).resolve().parents[1]
(root/'00_admin/matplotlib_compat_smoke.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
