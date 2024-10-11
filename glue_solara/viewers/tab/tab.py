from typing import Callable, List, Optional

import solara
from glue.viewers.common.viewer import Viewer

from ..common import ToolBar


@solara.component
def TabLabel(viewer: Viewer, on_close: Callable[[Viewer], None], label_text: str):
    label_action = solara.v.Btn(
        icon=True,
        children=[solara.v.Icon(children=["mdi-close"])],
    )

    solara.Row(
        style={"align-items": "center", "background-color": "transparent"},
        children=[
            label_text,
            label_action,
        ],
    )

    solara.v.use_event(label_action, "click", lambda *_ignore: on_close(viewer))


@solara.component
def TabbedViewers(
    viewers: List[Viewer],
    viewer_index: solara.Reactive[Optional[int]],
    on_close: Callable[[int], None],
    TITLE_TRANSLATIONS: dict[str, str],
):
    # The argument viewer_index is a reactive value for bi-directional communication
    # it can be changed outside of the component (when a new viewer is added)
    # or by the tab component, when the user clicks on a tab

    def close_viewer(viewer):
        index = viewers.index(viewer)
        on_close(index)

    with solara.lab.Tabs(
        viewer_index, dark=True, background_color="#d0413e", slider_color="#000000"
    ):
        for viewer in viewers:
            viewer.figure_widget.layout.height = "calc(100vh - 250px)"
            class_name = viewer.__class__.__name__
            title = TITLE_TRANSLATIONS.get(class_name, class_name)
            label = TabLabel(viewer, close_viewer, title)
            with solara.lab.Tab(label, style={"height": "100%"}):
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

                solara.Column(children=[layout], style={"height": "100%"})
