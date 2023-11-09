import glue.core.message
import solara
from glue.core import DataCollection
from glue_jupyter import JupyterApplication

from .hooks import use_glue_watch


def stringify_links(link):
    return str(link._cid1) + " <-> " + str(link._cid2)


@solara.component
def Linker(app: JupyterApplication, show_list: bool = True):
    selected_data1 = solara.use_reactive(0)
    selected_row1 = solara.use_reactive(0)
    selected_data2 = solara.use_reactive(1)
    selected_row2 = solara.use_reactive(0)
    data_collection = app.data_collection
    use_glue_watch(app.session.hub, glue.core.message.Message)

    if len(data_collection.data) == 0:
        return solara.Text("No data loaded")

    def _add_link():
        app.add_link(
            data_collection[selected_data1.value],
            data_collection[selected_data1.value].components[selected_row1.value],
            data_collection[selected_data2.value],
            data_collection[selected_data2.value].components[selected_row2.value],
        )

    with solara.Column():
        with solara.Row():
            data_dict = [
                {"label": data.label, "value": index} for index, data in enumerate(data_collection)
            ]
            with solara.Column():
                with solara.Row(style={"align-items": "start"}):
                    if len(data_collection) > 1:
                        LinkSelector(data_collection, data_dict, selected_data1, selected_row1)
                        LinkSelector(data_collection, data_dict, selected_data2, selected_row2)
                solara.Button(
                    label="Glue Attributes",
                    color="primary",
                    on_click=_add_link,
                )
            if show_list:
                with solara.Column():
                    solara.Text("Current Links")
                    with solara.v.List(dense=True):
                        for link in data_collection.external_links:
                            with solara.v.ListItem():
                                with solara.v.ListItemContent():
                                    solara.v.ListItemTitle(children=[stringify_links(link)])


@solara.component
def LinkSelector(
    data_collection: DataCollection,
    data_dict: list[dict],
    selected_data: solara.Reactive[int],
    selected_row: solara.Reactive[int],
):
    with solara.Column():
        solara.v.Select(
            label="Data 1",
            v_model=selected_data.value,
            on_v_model=selected_data.set,
            items=data_dict,
            item_text="label",
            item_value="value",
        )
        solara.Text(f"Attributes for {data_dict[selected_data.value]['label']}")
        with solara.v.List(dense=True, style_="max-height: 50vh; overflow-y: scroll;"):
            with solara.v.ListItemGroup(
                v_model=selected_row.value,
                on_v_model=selected_row.set,
                color="primary",
            ):
                for attribute in data_collection[selected_data.value].components:
                    with solara.v.ListItem():
                        with solara.v.ListItemContent():
                            solara.v.ListItemTitle(children=[attribute.label])
