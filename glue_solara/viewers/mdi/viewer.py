from typing import Callable, List, Optional

import solara
from glue.viewers.common.viewer import Viewer

from ..common import ToolBar
from .mdi import Mdi, MdiWindow


@solara.component
def MdiViewers(
    viewers: List[Viewer],
    mdi_layouts: solara.Reactive[List[MdiWindow]],
    header_size,
    on_viewer_index: Optional[Callable[[int], None]] = None,
    on_close: Optional[Callable[[int], None]] = None,
):
    # in this component, we only emit the index of the viewer that is active
    # it cannot be controlled externally (so not a reactive variable)
    layouts = []
    with solara.Column(style={"height": "100%", "background-color": "transparent"}):
        for viewer in viewers:
            viewer.figure_widget.layout.height = "100%"
            toolbar = ToolBar(viewer)
            layout = solara.Column(
                children=[toolbar, viewer.figure_widget],
                margin=0,
                style={
                    "height": "100%",
                    "box-shadow": "0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;",
                },
                classes=["elevation-2"],
            )
            layouts.append(layout)

        def on_windows(windows_layout):
            mdi_layouts.set(windows_layout)
            sorted = list(enumerate(windows_layout))
            sorted.sort(key=lambda x: x[1]["order"])
            on_viewer_index(sorted[-1][0])

        with Mdi(
            children=layouts,
            windows=mdi_layouts.value,
            on_windows=on_windows,
            event_close=on_close,
            size=header_size,
        ):
            pass
