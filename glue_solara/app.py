from pathlib import Path
from typing import Callable, Optional, cast

import glue.core.hub
import glue.core.message
import glue_jupyter as gj
import glue_jupyter.app
import glue_jupyter.registries
import solara
import solara.lab
from glue_jupyter.data import require_data

from .hooks import use_glue_watch
from .linker import Linker
from .mdi import Mdi
from .misc import Snackbar, ToolBar

# logging.basicConfig(level="INFO", force=True)
# logging.getLogger("glue").setLevel("DEBUG")

if not Path("w5.fits").exists():
    require_data("Astronomy/W5/w5.fits")
if not Path("w5_psc.csv").exists():
    require_data("Astronomy/W5/w5_psc.csv")


class HubListenerLogger(glue.core.hub.HubListener):
    def notify(self, message):
        print("!!! message", message)


main_color = "#d0413e"
nice_colors = [
    "red",
    "green",
    "blue",
    "purple",
    "orange",
    "yellow",
    "pink",
    "brown",
    "grey",
    "cyan",
    "magenta",
]


@solara.component
def JupyterApp():
    solara.components.applayout.should_use_embed.provide(True)
    with solara.AppLayout(color=main_color):
        Page()


@solara.component
def Page():
    def create_glue_application() -> gj.JupyterApplication:
        app = glue_jupyter.app.JupyterApplication()
        return app

    # make the app only once
    app = solara.use_memo(create_glue_application, [])
    GlueApp(app)


@solara.component
def GlueApp(app: gj.JupyterApplication):
    force_update_counter, set_force_update_counter = solara.use_state(0)
    use_glue_watch(app.session.hub, glue.core.message.Message)
    data_collection = app.data_collection
    viewer_index = solara.use_reactive(None)
    show_error = solara.use_reactive(False)
    error_message = solara.use_reactive("")

    requested_viewer_for_data_index = solara.use_reactive(None)
    requested_viewer_typename = solara.use_reactive("Scatter")

    def add_data_viewer(type: str, data: glue.core.Data):
        if type == "Histogram":
            app.histogram1d(data=data, show=False)
        elif type == "Scatter":
            app.scatter2d(data=data, show=False)
        elif type == "2D Image":
            try:
                app.imshow(data=data, show=False)
            except ValueError as error:
                error_message.set(str(error))
                show_error.set(True)
                return
        if len(data_collection) == 1:
            grid_layout.value = [
                {"h": 18, "i": "0", "moved": False, "w": 12, "x": 0, "y": 0},
            ]
        if len(data_collection) == 2:
            grid_layout.value = [
                *grid_layout.value,
                {"h": 18, "i": "0", "moved": False, "w": 12, "x": 18, "y": 0},
            ]
        className = app.viewers[-1].__class__.__name__
        title = {
            "BqplotScatterView": "2d Scatter",
            "BqplotHistogramView": "1d Histogram",
            "BqplotImageView": "2d Image",
        }.get(className, className)
        mdi_layouts.value = [
            *mdi_layouts.value,
            {"title": title, "width": 800, "height": 600},
        ]
        viewer_index.set(len(app.viewers) - 1)
        set_force_update_counter(lambda x: x + 1)

    def request_viewer_for(data: glue.core.Data):
        if data.ndim > 1:
            default_type = "2D Image"
        else:
            default_type = "Scatter"
        requested_viewer_typename.value = default_type
        requested_viewer_for_data_index.value = data_collection.index(data)

    def add_requested_data_viewer():
        add_data_viewer(
            requested_viewer_typename.value, data_collection[requested_viewer_for_data_index.value]
        )

    def add_to_current_viewer(data: glue.core.Data):
        viewer = app.viewers[viewer_index.value]
        viewer.add_data(data)
        # unclear why this force update is needed
        set_force_update_counter(lambda x: x + 1)

    with solara.Column(
        style={"height": "100%", "background-color": "transparent", "min-height": "800px"}, gap=0
    ):
        # Show an error message if data is attempted to be visualized in a way that the data does not have enough dimensions for
        Snackbar(
            open_value=show_error,
            children=[solara.Text(text=f"Error: {error_message.value}", style={"color": "white"})],
        )
        with solara.lab.ConfirmationDialog(
            open=requested_viewer_for_data_index.value is not None,
            on_close=lambda: requested_viewer_for_data_index.set(None),
            title="Data Viewer",
            ok="Add",
            cancel="Cancel",
            on_ok=add_requested_data_viewer,
        ):
            solara.Select(
                "Data", value=requested_viewer_typename, values=["Histogram", "Scatter", "2D Image"]
            )

        with solara.AppBarTitle():
            (
                solara.v.Html(
                    tag="img",
                    attributes={"src": "https://glueviz.org/images/histogram.png"},
                    style_="height: 32px; padding-right: 10px; margin-bottom: -4px; margin-left: 5px",
                ),
            )
            solara.Text("Glue")
        solara.Title("Glue on Solara")
        if len(data_collection) > 0:
            with solara.Sidebar():
                with solara.Column(align="start"):
                    with solara.Column(classes=["py-4"]):
                        LoadData(app)
                solara.v.Divider()
                with solara.Card("Data", margin="0", elevation=0):
                    DataList(
                        app,
                        active_viewer_index=viewer_index.value,
                        on_add_viewer=request_viewer_for,
                        on_add_data_to_viewer=add_to_current_viewer,
                    )
                if viewer_index.value is not None:
                    viewer = app.viewers[viewer_index.value]
                    solara.v.Divider()
                    with solara.Card(
                        "Plot Layers",
                        children=[
                            viewer.layer_options,
                        ],
                        margin="0",
                        elevation=0,
                    ):
                        pass

                    solara.v.Divider()
                    with solara.Card(
                        "Plot options", children=[viewer.viewer_options], margin="0", elevation=0
                    ):
                        pass

        view_type = solara.use_reactive("tabs")
        grid_layout = solara.use_reactive([])
        mdi_layouts = solara.use_reactive([])
        header_sizes = ["x-small", "small", None, "large", "x-large"]
        header_size = solara.use_reactive(2)
        with solara.AppBar():
            if len(app.viewers) > 0:
                with solara.Row(style={"background-color": "transparent"}):
                    if view_type.value == "mdi":
                        solara.Button(
                            icon_name="mdi-format-size",
                            color=main_color,
                            dark=True,
                            on_click=lambda: header_size.set(header_size.value + 1),
                        )
                    LinkButton(app)
                    with solara.ToggleButtonsSingle(
                        value=view_type,
                        style={"background-color": "transparent", "color": "white"},
                        dense=True,
                    ):
                        solara.Button(
                            "Tabs",
                            value="tabs",
                            style={"background-color": "transparent", "color": "white"},
                        )
                        solara.Button(
                            "Grid",
                            value="grid",
                            style={"background-color": "transparent", "color": "white"},
                        )
                        solara.Button(
                            "MDI",
                            value="mdi",
                            style={"background-color": "transparent", "color": "white"},
                        )

                    def enter_debugger():
                        app.session.hub
                        breakpoint()

                    solara.Button(
                        "debug",
                        icon_name="mdi-bug",
                        color=main_color,
                        dark=True,
                        on_click=enter_debugger,
                    )
        if len(data_collection) == 0:
            with solara.Row(
                style={
                    "align-items": "center",
                    "height": "100%",
                    "background-color": "transparent",
                    "justify-content": "center",
                }
            ):
                LoadData(app)
        elif len(app.viewers) == 0:
            with solara.Column(
                style={
                    "align-items": "center",
                    "height": "100%",
                    "background-color": "transparent",
                    "justify-content": "center",
                }
            ):
                solara.Text("What do you want to visualize", style={"font-size": "2em"})
                with solara.Column(style={"background-color": "transparent"}):
                    for viewer_type in ["Histogram", "Scatter", "2D Image"]:

                        def add(viewer_type=viewer_type):
                            add_data_viewer(viewer_type, data_collection[0])

                        solara.Button(
                            f"A {viewer_type}",
                            on_click=add,
                            block=True,
                            color=main_color,
                            dark=True,
                        )
        elif view_type.value == "tabs":
            with solara.lab.Tabs(
                viewer_index, dark=True, background_color="#d0413e", slider_color="#000000"
            ):
                for viewer in app.viewers:
                    viewer.figure_widget.layout.height = "600px"
                    label = viewer.__class__.__name__
                    label = {
                        "BqplotScatterView": "2d Scatter",
                        "BqplotHistogramView": "1d Histogram",
                        "BqplotImageView": "2d Image",
                    }.get(label, label)
                    with solara.lab.Tab(label, style={"height": "100%"}):
                        toolbar = ToolBar(app, viewer)
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

        elif view_type.value == "grid":
            layouts = []
            with solara.Column(style={"height": "100%", "background-color": "transparent"}):
                for viewer in app.viewers:
                    viewer.figure_widget.layout.height = "600px"
                    layout = solara.Column(
                        children=[
                            ToolBar(app, viewer),
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

                with solara.GridDraggable(
                    items=layouts,
                    grid_layout=grid_layout.value,
                    resizable=True,
                    draggable=True,
                    on_grid_layout=grid_layout.set,
                ):
                    pass

        elif view_type.value == "mdi":
            layouts = []
            with solara.Column(style={"height": "100%", "background-color": "transparent"}):
                for viewer in app.viewers:
                    viewer.figure_widget.layout.height = "100%"
                    toolbar = ToolBar(app, viewer)
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
                    viewer_index.value = sorted[-1][0]

                with Mdi(
                    children=layouts,
                    windows=mdi_layouts.value,
                    on_windows=on_windows,
                    size=header_sizes[header_size.value % len(header_sizes)],
                ):
                    pass


@solara.component
def DataList(
    app: gj.JupyterApplication,
    active_viewer_index: Optional[int],
    on_add_viewer: Callable[[glue.core.Data], None],
    on_add_data_to_viewer: Callable[[glue.core.Data], None],
):
    # TODO: we need to re-render when new data is added to a viewer
    use_glue_watch(app.session.hub, glue.core.message.DataMessage)
    data_collection = app.data_collection
    with solara.v.List(dense=True):
        for index, data in enumerate(data_collection):
            data = cast(glue.core.Data, data)
            color = data.style.color
            with solara.v.ListItem():
                with solara.v.ListItemAvatar():
                    solara.IconButton("mdi-circle", color=color)
                with solara.v.ListItemContent():
                    with solara.v.ListItemTitle(
                        style_="display: flex; justify-content: space-between; align-items: center;"
                    ):
                        solara.Text(data.label)
                        with solara.Row():
                            with solara.Tooltip("Create new viewer"):
                                solara.Button(
                                    "",
                                    icon_name="mdi-tab",
                                    color=color,
                                    text=True,
                                    on_click=lambda index=index: on_add_viewer(
                                        data_collection[index]
                                    ),
                                    icon=True,
                                )
                            with solara.Tooltip("Add data to current viewer"):
                                can_add_viewer = False
                                if active_viewer_index is not None:
                                    viewer = app.viewers[active_viewer_index]
                                    can_add_viewer = (
                                        data not in viewer._layer_artist_container.layers
                                    )

                                solara.Button(
                                    "",
                                    icon_name="mdi-tab-plus",
                                    color=color,
                                    text=True,
                                    on_click=lambda index=index: on_add_data_to_viewer(
                                        data_collection[index]
                                    ),
                                    icon=True,
                                    disabled=not can_add_viewer,
                                )


@solara.component
def LoadData(app: gj.JupyterApplication):
    add = solara.Button(
        "Load data", icon_name="mdi-cloud-outline", color=main_color, dark=True, classes=["my-0"]
    )
    open_load_from_server = solara.use_reactive(False)
    with solara.lab.Menu(activator=add):
        solara.Button(
            "Load data from server",
            on_click=lambda: open_load_from_server.set(True),
            text=True,
            icon_name="mdi-cloud-outline",
        )
        solara.Button("Upload data", text=True, icon_name="mdi-cloud-upload", disabled=True)

        def add_w5():
            data_image = app.load_data("w5.fits")
            data_catalog = app.load_data("w5_psc.csv")
            app.add_link(data_catalog, "RAJ2000", data_image, "Right Ascension")
            app.add_link(data_catalog, "DEJ2000", data_image, "Declination")
            data_catalog.style.color = "purple"
            data_image.style.color = "red"
            # viewer = app.imshow(data=data_image, show=False)
            # viewer.add_data(data_catalog)

        solara.Button(
            "Add W5 data",
            on_click=add_w5,
            text=True,
            icon_name="mdi-brain",
            style={"width": "100%", "justify-content": "left"},
        )
    path = solara.use_reactive(None)
    with solara.v.Dialog(
        v_model=open_load_from_server.value,
        on_close=lambda: open_load_from_server.set(False),
        max_width="800px",
        persistent=True,
        scrollable=True,
        margin="0px",
    ):
        with solara.v.Sheet():
            with solara.Card("Load data from server", margin="0px"):
                solara.FileBrowser(on_file_open=lambda path_value: path.set(path_value))
                with solara.CardActions():
                    solara.v.Spacer()

                    def load():
                        data = app.load_data(str(path.value))
                        data.style.color = nice_colors[len(app.data_collection) % len(nice_colors)]
                        open_load_from_server.value = False

                    solara.Button(
                        "Cancel", on_click=lambda: open_load_from_server.set(False), text=True
                    )
                    solara.Button(
                        "Load",
                        on_click=lambda: load(),
                        disabled=path.value is None or not path.value.exists(),
                        text=True,
                    )


@solara.component
def LinkButton(app: gj.JupyterApplication):
    open_link_editor = solara.use_reactive(False)
    with solara.Div():
        solara.Button(
            "Link data",
            icon_name="mdi-link-variant",
            on_click=lambda: open_link_editor.set(True),
            style={"background-color": "transparent", "color": "white"},
            dark=False,
            text=True,
        )
        with solara.v.Dialog(
            v_model=open_link_editor.value,
            on_v_model=lambda _: open_link_editor.set(False),
            on_close=lambda: open_link_editor.set(False),
            max_width="800px",
            persistent=False,
            scrollable=True,
            margin="0px",
        ):
            with solara.v.Sheet():
                with solara.Card("Link Editor", margin="0px"):
                    Linker(app)
                    with solara.CardActions():
                        solara.v.Spacer()
                        solara.Button(
                            "Close", on_click=lambda: open_link_editor.set(False), text=True
                        )


@solara.component
def Layout(children):
    solara.AppLayout(
        children=children,
        color=main_color,
    )