import copy
from pathlib import Path
from typing import Callable, Dict, List, Optional, cast

import glue.core.hub
import glue.core.message as msg
import glue_jupyter as gj
import glue_jupyter.app
import glue_jupyter.bqplot.histogram
import glue_jupyter.bqplot.image
import glue_jupyter.bqplot.scatter
import glue_jupyter.registries
import solara
import solara.lab
from glue.viewers.common.viewer import Viewer
from glue_jupyter.data import require_data
from glue_jupyter.registries import viewer_registry
from solara import Reactive

from .hooks import ClosedMessage, use_glue_watch, use_glue_watch_close, use_layers_watch
from .linker import Linker
from .misc import Snackbar
from .viewers import GridViewers, MdiViewers, TabbedViewers
from .viewers.mdi import MDI_HEADER_SIZES, MdiWindow

# logging.basicConfig(level="INFO", force=True)
# logging.getLogger("glue").setLevel("DEBUG")

if not Path("w5.fits").exists():
    require_data("Astronomy/W5/w5.fits")
if not Path("w5_psc.csv").exists():
    require_data("Astronomy/W5/w5_psc.csv")


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

VIEWER_TYPES = list(map(lambda k: k.title(), viewer_registry.members.keys()))

VIEWER_METHODS = {"Histogram": "histogram1d", "Scatter": "scatter2d", "Image": "imshow"}

TITLE_TRANSLATIONS = {
    "BqplotScatterView": "2d Scatter",
    "BqplotHistogramView": "1d Histogram",
    "BqplotImageView": "2d Image",
}


@solara.component
def JupyterApp():
    """Best used in the notebook"""
    with solara.AppLayout(color=main_color):
        Page()


@solara.component
def Page():
    """This component is used by default in solara server (standalone app)"""

    def create_glue_application() -> gj.JupyterApplication:
        app = glue_jupyter.app.JupyterApplication()
        return app

    # make the app only once
    app = solara.use_memo(create_glue_application, [])
    GlueApp(app)


@solara.component
def GlueApp(app: gj.JupyterApplication):
    # TODO: check if we can limit the messages we listen to
    # for better performance (less re-renders)
    use_glue_watch(app.session.hub, msg.DataCollectionMessage)
    use_glue_watch_close(app)
    data_collection = app.data_collection
    viewer_index: Reactive[Optional[int]] = solara.use_reactive(None)
    show_error = solara.use_reactive(False)
    error_message = solara.use_reactive("")

    requested_viewer_for_data_index = solara.use_reactive(None)
    requested_viewer_typename = solara.use_reactive("Scatter")

    view_type = solara.use_reactive("tabs")  # tabs, grid, mdi
    mdi_layouts: Reactive[List[MdiWindow]] = solara.use_reactive([])
    grid_layout: Reactive[List[Dict]] = solara.use_reactive([])
    mdi_header_size_index = solara.use_reactive(2)

    def add_data_viewer(type: str, data: glue.core.Data):
        if type in VIEWER_METHODS:
            try:
                getattr(app, VIEWER_METHODS[type])(data=data, show=False)
            except ValueError as error:
                error_message.set(str(error))
                show_error.set(True)
                return
        else:
            # manual approach...
            viewer_cls = viewer_registry.members[type.lower()]["cls"]
            viewer_state_obj = viewer_cls._state_cls()
            # NOTE: some viewers should set x_att or have other checks which this skips
            app.new_data_viewer(viewer_cls, data=data, state=viewer_state_obj, show=False)
        new_viewer_index = len(app.viewers) - 1
        grid_layout.value = [
            *grid_layout.value,
            {
                "h": 18,
                "i": str(new_viewer_index),
                "moved": False,
                "w": 12,
                "x": 0,
                "y": 12 * new_viewer_index,
            },
        ]
        class_name = app.viewers[-1].__class__.__name__
        title = TITLE_TRANSLATIONS.get(class_name, class_name)
        mdi_layouts.value = [
            *mdi_layouts.value,
            {"title": title, "width": 800, "height": 600},
        ]
        viewer_index.set(new_viewer_index)

    def request_viewer_for(data: glue.core.Data):
        if data.ndim > 1:
            default_type = "Image"
        else:
            default_type = "Scatter"
        requested_viewer_typename.value = default_type
        requested_viewer_for_data_index.value = data_collection.index(data)

    def add_requested_data_viewer():
        add_data_viewer(
            requested_viewer_typename.value, data_collection[requested_viewer_for_data_index.value]
        )

    def add_to_current_viewer(data: glue.core.Data):
        viewer: Viewer = app.viewers[viewer_index.value]
        viewer.add_data(data)

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
            solara.Select("Data", value=requested_viewer_typename, values=VIEWER_TYPES)

        with solara.AppBarTitle():
            (
                solara.v.Html(
                    tag="img",
                    attributes={"src": "https://glueviz.org/images/histogram.png"},
                    style_="height: 32px; padding-right: 10px; margin-bottom: -4px; margin-left: 5px",
                ),
            )
            solara.Text("glue")
        solara.Title("glue on solara")
        if len(data_collection) > 0:
            with solara.Sidebar():
                with solara.Card(margin=0, elevation=0):
                    LoadData(app)
                    with solara.Row(style={"align-items": "center"}, classes=["mt-3"]):
                        solara.Text(
                            "Subset mode:", style={"font-size": "1.2em", "font-weight": "bold"}
                        )
                        solara.Row(children=[app.widget_subset_mode])
                solara.v.Divider()
                with solara.Card("Data", margin="0", elevation=0):
                    DataList(
                        app,
                        active_viewer_index=viewer_index.value,
                        on_add_viewer=request_viewer_for,
                        on_add_data_to_viewer=add_to_current_viewer,
                    )
                if viewer_index.value is not None and view_type.value != "grid":
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

        with solara.AppBar():
            if len(data_collection) > 0:
                with solara.Row(style={"background-color": "transparent"}):
                    if view_type.value == "mdi":
                        solara.Button(
                            icon_name="mdi-format-size",
                            color=main_color,
                            dark=True,
                            on_click=lambda: mdi_header_size_index.set(
                                (mdi_header_size_index.value + 1) % len(MDI_HEADER_SIZES)
                            ),
                        )
                    LinkButton(app, disabled=len(data_collection) < 2)
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
                            "MDI",
                            value="mdi",
                            style={"background-color": "transparent", "color": "white"},
                        )
                        solara.Button(
                            "Grid",
                            value="grid",
                            style={"background-color": "transparent", "color": "white"},
                        )

                # def enter_debugger():
                #     app.session.hub
                #     breakpoint()

                # solara.Button(
                #     "debug",
                #     icon_name="mdi-bug",
                #     color=main_color,
                #     dark=True,
                #     on_click=enter_debugger,
                # )
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
                solara.Text("What do you want to visualize?", style={"font-size": "2em"})
                with solara.Column(style={"background-color": "transparent"}):
                    for viewer_type in VIEWER_TYPES:

                        def add(viewer_type=viewer_type):
                            add_data_viewer(viewer_type, data_collection[0])

                        solara.Button(
                            f"{'An' if viewer_type[0] in ('AEOIU') else 'A'} {viewer_type}",
                            on_click=add,
                            block=True,
                            color=main_color,
                            dark=True,
                        )
        else:
            Viewers(
                view_type,
                app.viewers,
                mdi_layouts,
                grid_layout,
                mdi_header_size_index,
                viewer_index,
            )


@solara.component
def Viewers(
    view_type: solara.Reactive[str],
    viewers: List[Viewer],
    mdi_layouts: Reactive[List[MdiWindow]],
    grid_layout: Reactive[List[Dict]],
    mdi_header_size_index: solara.Reactive[int],
    viewer_index: solara.Reactive[Optional[int]],
):
    def on_viewer_close(index: int):
        # Remove the viewer from MDI layouts
        new_mdi_layouts = copy.deepcopy(mdi_layouts.value)
        new_mdi_layouts.pop(index)
        mdi_layouts.set(new_mdi_layouts)

        # Remove the viewer from grid layouts
        new_grid_layout = copy.deepcopy(grid_layout.value)
        new_grid_layout.pop(index)
        # We need to update the indices of the viewers in the grid layout, otherwise we get placeholder elements
        for layout in new_grid_layout:
            if int(layout["i"]) > index:
                layout["i"] = str(int(layout["i"]) - 1)
        grid_layout.set(new_grid_layout)

        # Pick either the last viewer (after we close) or None
        viewer_to_activate = None if len(viewers) <= 1 else (len(viewers) - 2)
        viewer_index.set(viewer_to_activate)
        # Close the viewer
        message = ClosedMessage(viewers[index])
        viewers[index].session.hub.broadcast(message)

    if view_type.value == "tabs":
        TabbedViewers(viewers, viewer_index, on_viewer_close, TITLE_TRANSLATIONS)
    elif view_type.value == "grid":
        GridViewers(viewers, grid_layout)
    elif view_type.value == "mdi":
        header_size = MDI_HEADER_SIZES[mdi_header_size_index.value]
        MdiViewers(
            viewers,
            mdi_layouts,
            header_size,
            on_viewer_index=viewer_index.set,
            on_close=on_viewer_close,
        )


@solara.component
def DataList(
    app: gj.JupyterApplication,
    active_viewer_index: Optional[int],
    on_add_viewer: Callable[[glue.core.Data], None],
    on_add_data_to_viewer: Callable[[glue.core.Data], None],
):
    # this makes the component re-render when data is added or removed
    use_glue_watch(app.session.hub, msg.DataCollectionMessage)
    # this makes the component re-render when layers are added or removed
    use_layers_watch(app.viewers)
    # these two hooks (starting with use_) are needed because the data that is changing
    # is external to solara. These hooks 'hook' up to glue to get notified when state changes
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
def LinkButton(app: gj.JupyterApplication, disabled: bool = False):
    open_link_editor = solara.use_reactive(False)
    with solara.Div():
        solara.Button(
            "Link data",
            icon_name="mdi-link-variant",
            on_click=lambda: open_link_editor.set(True),
            style={"background-color": "transparent", "color": "white"},
            dark=False,
            text=True,
            disabled=disabled,
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
                # Avoid loading the linker component, since it listens to messages causing extra re-renders
                if open_link_editor.value:
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
        style="height: 100%; overflow: auto;",
    )
