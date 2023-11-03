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
