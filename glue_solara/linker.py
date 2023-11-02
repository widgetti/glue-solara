import glue.core.message
import solara
from glue.core import DataCollection
from glue.core.link_helpers import LinkSame
from glue_jupyter import JupyterApplication

from .hooks import use_glue_watch


def add_link(data_collection, data1, attribute1, data2, attribute2):
    """
    Add a simple identity link between two attributes.

    Parameters
    ----------
    data1 : `~glue.core.data.Data`
        The dataset containing the first attribute.
    attribute1 : str or `~glue.core.component_id.ComponentID`
        The first attribute to link.
    data2 : `~glue.core.data.Data`
        The dataset containing the first attribute.
    attribute2 : str or `~glue.core.component_id.ComponentID`
        The first attribute to link.
    """
    # For now this assumes attribute1 and attribute2 are strings and single
    # attributes. In future we should generalize this while keeping the
    # simplest use case simple.
    att1 = data1.id[attribute1]
    att2 = data2.id[attribute2]
    link = LinkSame(att1, att2)
    data_collection.add_link(link)


@solara.component
def Linker(app: JupyterApplication, show_list: bool = True):
    selected_data1 = solara.use_reactive(0)
    selected_row1 = solara.use_reactive(0)
    selected_data2 = solara.use_reactive(1)
    selected_row2 = solara.use_reactive(0)
    data_collection = app.data_collection
    # dc_links = solara.use_reactive(data_collection.links)
    # use_glue_watch(data_collection.hub, glue.core.message)
    # use_glue_watch(app.session.hub, glue.core.message.Message)
    use_glue_watch(app.session.hub, glue.core.message.Message)

    def _add_link():
        add_link(
            data_collection,
            data_collection[selected_data1.value],
            data_collection[selected_data1.value].components[selected_row1.value],
            data_collection[selected_data2.value],
            data_collection[selected_data2.value].components[selected_row2.value],
        )
        # dc_links.set(
        #     [
        #         *data_collection.links,
        #         str(data_collection[selected_data1.value].components[selected_row1.value])
        #         + "<->"
        #         + str(data_collection[selected_data2.value].components[selected_row1.value]),
        #     ]
        # )

    # with solara.Card("Link Editor", style="width: fit-content;"):
    with solara.Column():
        with solara.Row():
            data_dict = [
                {"label": data.label, "value": index} for index, data in enumerate(data_collection)
            ]
            with solara.Column():
                # solara.v.Spacer()
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
                        for link in data_collection.links:
                            if "pix" in str(link):
                                continue
                            with solara.v.ListItem():
                                with solara.v.ListItemContent():
                                    solara.v.ListItemTitle(children=[str(link)])

        # with solara.CardActions():


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
        # print(selected_data.value, selected_row.value)
        solara.Text(f"Attributes for {data_dict[selected_data.value]['label']}")
        with solara.v.List(dense=True):
            with solara.v.ListItemGroup(
                v_model=selected_row.value,
                on_v_model=selected_row.set,
                color="primary",
            ):
                for attribute in data_collection[selected_data.value].components:
                    with solara.v.ListItem():
                        with solara.v.ListItemContent():
                            solara.v.ListItemTitle(children=[attribute.label])
