from typing import List

import solara
from glue.viewers.common.viewer import Viewer

from ..common import ToolBar


@solara.component
def GridViewers(viewers: List[Viewer], grid_layout: solara.Reactive[List]):
    # this component does not have the concept of an active viewer
    layouts = []
    for viewer in viewers:
        viewer.figure_widget.layout.height = "100%"
        layout = solara.Column(
            children=[
                ToolBar(viewer),
                viewer.figure_widget,
            ],
            margin=0,
            style={
                "height": "100%",
                "box-shadow": "0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;",
            },
            classes=["elevation-2"],
        )
        layouts.append(layout)
    with solara.Column(style={"height": "100%", "background-color": "transparent"}):
        with solara.GridDraggable(
            items=layouts,
            grid_layout=grid_layout.value,
            resizable=True,
            draggable=True,
            on_grid_layout=grid_layout.set,
        ):
            pass
