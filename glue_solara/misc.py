from typing import Callable, Union

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


@solara.component
def Snackbar(open_value: Union[bool, solara.Reactive[bool]], children: list[solara.Element] = []):
    open_value = solara.use_reactive(open_value)

    def cleanup(*ignore_args):
        open_value.value = False

    action = solara.Button(icon_name="mdi-close", color="white", on_click=cleanup, text=True)
    _children = children + [solara.v.Spacer(), action]

    solara.v.Snackbar(
        children=_children,
        timeout=3000,
        color="error",
        v_model=open_value.value,
        on_v_model=cleanup,
    )


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
