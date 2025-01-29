# Add the viewer as a plugin to glue-jupyter, see
# https://glue-jupyter.readthedocs.io/en/latest/developer_notes.html#adding-new-viewers-via-plug-ins
def setup():
    from glue_jupyter.registries import viewer_registry

    from .tools import XRHullSelectionTool as XRHullSelectionTool
    from .viewer import XRBaseView

    viewer_registry.add("xr", XRBaseView)
