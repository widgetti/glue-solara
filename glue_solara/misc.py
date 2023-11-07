import glue_jupyter as gj
import ipypopout
import solara


@solara.component
def ToolBar(app: gj.JupyterApplication, viewer):
    solara.Row(
        children=[
            viewer.toolbar,
            app.widget_subset_mode,
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
def Snackbar(open_value: bool | solara.Reactive[bool], children: list[solara.Element] = []):
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
