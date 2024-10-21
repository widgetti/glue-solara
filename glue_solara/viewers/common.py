import ipypopout
import solara
from glue.viewers.common.viewer import Viewer


@solara.component
def ToolBar(viewer: Viewer):
    solara.Row(
        children=[
            viewer.toolbar,
            solara.v.Spacer(),
            ipypopout.PopoutButton.element(
                target=solara.Div(
                    style_="height: calc(100vh - 2px);",
                    children=[viewer.figure_widget],
                ),
                window_features="popup,width=600,height=600",
            ),
        ],
        margin=2,
        style={"align-items": "center"},
    )
