from typing import cast
import solara
import solara.lab
import glue_jupyter as gj
import glue_jupyter.app
import glue.core.message
import glue.core.hub
import numpy as np
import logging
import glue_jupyter.registries
from .linker import Linker
from .hooks import use_glue_watch
from .mdi import Mdi

import ipypopout

# logging.basicConfig(level="INFO", force=True)
# logging.getLogger("glue").setLevel("DEBUG")


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

app_reactive = solara.reactive(None)

@solara.component
def Page():
    # refs = solara.use_ref([])
    def make() -> gj.JupyterApplication:
        print("LOAD APP")
        # gauss1 = gj.example_data_xyz(loc=60, scale=30, N=10*1000)
        # gauss2 = gj.example_data_xyz(loc=60, scale=30, N=10*1000)
        d1 = glue.core.Data(label="D1", x=np.random.random(100), y=np.random.random(100))
        d2 = glue.core.Data(label="D2", a=np.random.random(100), b=np.random.random(100))        

        # dc = glue.core.DataCollection([d1, d2])
        dc = glue.core.DataCollection([])
        app = glue_jupyter.app.JupyterApplication(data_collection=dc)
        # app.scatter2d(data=dc[1], show=False)

        if 0:
            data_catalog = app.load_data("/Users/maartenbreddels/github/widgetti/glue-solara/w5_psc.csv")
            data_image = app.load_data("/Users/maartenbreddels/github/widgetti/glue-solara/w5.fits")
            app.add_link(data_catalog, 'RAJ2000', data_image, 'Right Ascension')
            app.add_link(data_catalog, 'DEJ2000', data_image, 'Declination')
            data_catalog.style.color = "purple"
            data_image.style.color = "red"
            viewer = app.imshow(data=data_image, show=False)
            viewer.add_data(data_catalog)
        # app = gj.jglue(gauss1=gauss1, gauss2=gauss2)
        # logger = HubListenerLogger()
        # refs.current.append(logger)
        # # breakpoint()
        # app.data_collection.hub.subscribe(logger, glue.core.message.Message)
        # app.data_collection.hub.subscribe(logger, glue.core.message.DataCollectionAddMessage)
        
        # return app
        print(app)
        # breakpoint()
        app_reactive.value = app
    # app : gj.JupyterApplication = solara.use_memo(make, [])
    solara.use_effect(make, [])
    if app_reactive.value is None:
        print("RENDER !!!")
        solara.Warning("loading")
    else:
        print("RENDER ???")
        # solara.Warning("loaded")
        App(app_reactive.value)

@solara.component
def App(app: gj.JupyterApplication):
    use_glue_watch(app.session.hub, glue.core.message.Message)
    data_collection = app.data_collection

    # selected_row = solara.use_reactive(0)
    add_data_index = solara.use_reactive(None)
    data_viewer = solara.use_reactive("Scatter")
    viewer_index = solara.use_reactive(None)
    with solara.Column(style={"height": "100%", "background-color": "transparent"}, gap=0):
        solara.Title("Glue")
        with solara.Sidebar():
            with solara.Column(align="left"):
                LoadData(app)
                AddData(app)
            solara.v.Divider()
            with solara.Card("Data", margin="0", elevation=0):
                with solara.v.List(dense=True):
                # solara.v.Subheader(children=["Data"])
                # # with solara.v.ListItemGroup(
                # #     v_model=selected_row.value,
                # #     on_v_model=lambda i: selected_row.set(i),
                # #     color="primary",
                # # ):
                # if 1:
                    for index, data in enumerate(data_collection):
                        data = cast(glue.core.Data, data)
                        color = data.style.color
                        print(color)
                        with solara.v.ListItem():
                            with solara.v.ListItemAvatar():
                                solara.IconButton("mdi-circle", color=color)
                            with solara.v.ListItemContent():
                                with solara.v.ListItemTitle(style_="display: flex; justify-content: space-between; align-items: center;"):
                                    solara.Text(data.label)
                                    # solara.v.Spacer()
                                    # icon = solara.v.Icon(children=["mdi-plus"], color=color)
                                    solara.Button("", icon_name="mdi-plus", color=color, text=True, on_click=lambda index=index: add_data_index.set(index))
            if viewer_index.value is not None:
                viewer = app.viewers[viewer_index.value]
                solara.v.Divider()
                with solara.Card("Plot Layers", children=[viewer.layer_options,], margin="0", elevation=0):
                    pass
                    
                    # solara.display(viewer.layer_options)
                    # breakpoint()
                solara.v.Divider()
                with solara.Card("Plot options", children=[viewer.viewer_options], margin="0", elevation=0):
                    pass
            # print(add_data_index)
            print("RENDER", add_data_index.value, data_viewer.value)

        def add_data_viewer():
            print("Adding", add_data_index.value, data_viewer.value)
            if data_viewer.value == "Histogram":
                app.histogram1d(data=data_collection[add_data_index.value], show=False)
            elif data_viewer.value == "Scatter":
                viewer = app.scatter2d(data=data_collection[add_data_index.value], show=False)
            elif data_viewer.value == "2D Image":
                viewer = app.imshow(data=data_collection[add_data_index.value], show=False)
                viewer.add_data(data_collection[add_data_index.value-1])
            if len(data_collection) == 1:
                grid_layout.value = [{"h": 18, "i": "0", "moved": False, "w": 12, "x": 0, "y": 0},]
            if len(data_collection) == 2:
                grid_layout.value = [*grid_layout.value, {"h": 18, "i": "0", "moved": False, "w": 12, "x": 18, "y": 0}]
            mdi_layouts.value = [*mdi_layouts.value, {"id": len(mdi_layouts.value)}]
        with solara.lab.ConfirmationDialog(open=add_data_index.value is not None, on_close=lambda: add_data_index.set(None), title="Data Viewer", ok="Add", cancel="Cancel", on_ok=add_data_viewer):
            solara.Select("Data", value=data_viewer, values=["Histogram", "Scatter", "2D Image"])
            
        print(app.viewers)
        view_type = solara.use_reactive("tabs")
        grid_layout_initial = [
                # {"h": 18, "i": "0", "moved": False, "w": 12, "x": 0, "y": 0},
                # {"h": 18, "i": "0", "moved": False, "w": 12, "x": 18, "y": 0}
                # {"h": 5, "i": "1", "moved": False, "w": 5, "x": 3, "y": 0},
                # {"h": 11, "i": "2", "moved": False, "w": 4, "x": 8, "y": 0},
                # {"h": 12, "i": "3", "moved": False, "w": 5, "x": 0, "y": 5},
                # {"h": 6, "i": "4", "moved": False, "w": 3, "x": 5, "y": 5},
                # {"h": 6, "i": "5", "moved": False, "w": 7, "x": 5, "y": 11},
        ]

        grid_layout = solara.use_reactive(grid_layout_initial)
        mdi_layouts = solara.use_reactive([])
        print("grid_layout", grid_layout.value)
        with solara.AppBar():
            LinkButton(app)
            with solara.ToggleButtonsSingle(value=view_type, style={"background-color": "transparent", "color": "white"}):
                solara.Button("Tabs", value="tabs", style={"background-color": "transparent", "color": "white"})
                solara.Button("Grid", value="grid", style={"background-color": "transparent", "color": "white"})
                solara.Button("MDI", value="mdi", style={"background-color": "transparent", "color": "white"})
            
            def lala():
                hub = app.session.hub
                breakpoint()
            solara.Button("debug", icon_name="mdi-bug", color=main_color, dark=True, on_click=lala)
        if view_type.value == "tabs":
            with solara.lab.Tabs(viewer_index, dark=True, background_color="#d0413e", slider_color="#000000"):
                for viewer in app.viewers:
                    # with solara.lab.Tab(str(type(viewer))):
                    label = viewer.__class__.__name__
                    label = {
                        "BqplotScatterView": "2d Scatter",
                        "BqplotHistogramView": "1d Histogram",
                        "BqplotImageView": "2d Image",

                    }.get(label, label)
                    with solara.lab.Tab(label, style={"height": "100%"}):
                        toolbar = solara.Row(children=[viewer.toolbar, solara.v.Spacer(), ipypopout.PopoutButton.element(target=viewer._layout,
                                                                                                                         window_features='popup,width=600,height=600',
                                                                                                                         )], margin=2)
                        layout = solara.Column(children=[toolbar, viewer.figure_widget], margin=0, style={"height": "100%",
                            "box-shadow": "0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;"
                        }, classes=["elevation-2"])

                        solara.Column(children=[layout], style={"height": "100%"})

                        # solara.display(viewer._layout)
        if view_type.value == "grid":
            layouts = []
            with solara.Column(style={"height": "100%", "background-color": "transparent"}):
                
                for viewer in app.viewers:
                    # layouts.append(solara.Card("lala", children=[viewer._layout], style={"height": "100%"}))
                    viewer.figure_widget.layout.height = "600px"
                    layout = solara.Column(children=[solara.Row(children=[viewer.toolbar], margin=2), viewer.figure_widget], margin=0, style={"height": "100%",
                        "box-shadow": "0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;"
                    }, classes=["elevation-2"])
                    layouts.append(layout)


                with solara.GridDraggable(items=layouts, grid_layout=grid_layout.value, resizable=True, draggable=True, on_grid_layout=grid_layout.set):
                    pass


        if view_type.value == "mdi":
            layouts = []
            with solara.Column(style={"height": "100%", "background-color": "transparent"}):
                for viewer in app.viewers:
                    # layouts.append(solara.Card("lala", children=[viewer._layout], style={"height": "100%"}))
                    viewer.figure_widget.layout.height = "100%"
                    # lala = solara.
                    toolbar = solara.Row(children=[viewer.toolbar, solara.v.Spacer(), ipypopout.PopoutButton.element(target=viewer.figure_widget,
                                                                                                                        window_features='popup,width=600,height=600',
                                                                                                                        )], margin=2)
                    layout = solara.Column(children=[solara.Row(children=[toolbar], margin=2), viewer.figure_widget], margin=0, style={"height": "100%",
                        "box-shadow": "0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;"
                    }, classes=["elevation-2"])
                    layouts.append(layout)


                def on_windows(windows_layout):
                    mdi_layouts.set(windows_layout)
                    viewer_index.value = windows_layout[-1]["id"]

                children = [layouts[spec["id"]] for spec in mdi_layouts.value]
                with Mdi(children=children, windows=mdi_layouts.value, on_windows=on_windows):
                    pass



            # solara.Button("Add subset")
            # solara.Button("Add link")


@solara.component
def LoadData(app: gj.JupyterApplication):
    add = solara.Button("Load data", icon_name="mdi-cloud-outline", color=main_color, dark=True, classes=["my-4"])
    open_load_from_server = solara.use_reactive(False)
    with solara.lab.Menu(activator=add):
        solara.Button("Load data from server", on_click=lambda: open_load_from_server.set(True), text=True, icon_name="mdi-cloud-outline")
        solara.Button("Upload data", text=True, icon_name="mdi-cloud-upload", disabled=True)
    path = solara.use_reactive(None)
    with solara.v.Dialog(v_model=open_load_from_server.value, on_close=lambda: open_load_from_server.set(False), max_width="800px", persistent=True, scrollable=True, margin="0px"):
        with solara.v.Sheet():
            with solara.Card("Load data from server", margin="0px"):
                solara.FileBrowser(on_file_open=lambda path_value: path.set(path_value))
                with solara.CardActions():
                    solara.v.Spacer()
                    def load():
                        print("Load", path.value)
                        data = app.load_data(str(path.value))
                        data.style.color = nice_colors[len(app.data_collection) % len(nice_colors)]
                        open_load_from_server.value = False
                    solara.Button("Cancel", on_click=lambda: open_load_from_server.set(False), text=True)
                    solara.Button("Load", on_click=lambda: load(), disabled=path.value is None or not path.value.exists(), text=True)


@solara.component
def AddData(app: gj.JupyterApplication):
    add = solara.Button("Add data", text=True, icon_name="mdi-plus")
    with solara.lab.Menu(activator=add):
        def add_d1():
            d1 = glue.core.Data(label="D1", x=np.random.random(100), y=np.random.random(100))
            app.session.data_collection.append(d1)
        solara.Button("Add gaussian blob", add_d1, text=True)

        def add_w5():
            data_catalog = app.load_data("/Users/maartenbreddels/github/widgetti/glue-solara/w5_psc.csv")
            data_image = app.load_data("/Users/maartenbreddels/github/widgetti/glue-solara/w5.fits")
            app.add_link(data_catalog, 'RAJ2000', data_image, 'Right Ascension')
            app.add_link(data_catalog, 'DEJ2000', data_image, 'Declination')
            data_catalog.style.color = "purple"
            data_image.style.color = "red"
            # viewer = app.imshow(data=data_image, show=False)
            # viewer.add_data(data_catalog)
        solara.Button("Add w5", on_click=add_w5, text=True, block=True)


@solara.component
def LinkButton(app: gj.JupyterApplication):
    open_link_editor = solara.use_reactive(False)
    with solara.Div():
        solara.Button("Link data", icon_name="mdi-link-variant", on_click=lambda: open_link_editor.set(True), style={"background-color": "transparent", "color": "white"}, dark=False, text=True)
        with solara.v.Dialog(v_model=open_link_editor.value, on_v_model=lambda _: open_link_editor.set(False), on_close=lambda: open_link_editor.set(False), max_width="800px", persistent=False, scrollable=True, margin="0px"):
            with solara.v.Sheet():
                with solara.Card("Link Editor", margin="0px"):
                    Linker(app)
                    with solara.CardActions():
                        solara.v.Spacer()
                        # def load():
                        #     app.load_data(str(path.value))
                        #     open_link_editor.value = False
                        solara.Button("Close", on_click=lambda: open_link_editor.set(False), text=True)
                        # solara.Button("Load", on_click=lambda: load(), disabled=path.value is None or not path.value.exists(), text=True)


@solara.component
def Layout(children):
    return solara.AppLayout(
        children=children,
    )
