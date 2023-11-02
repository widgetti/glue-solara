from glue.core.link_helpers import LinkSame
import solara

from glue.core import DataCollection


def add_link(data1, attribute1, data2, attribute2):
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
    dc.add_link(link)


@solara.component
def Linker(data_collection: DataCollection, show_list: bool = True):
    selected_data1 = solara.use_reactive(0)
    selected_row1 = solara.use_reactive(0)
    selected_data2 = solara.use_reactive(1)
    selected_row2 = solara.use_reactive(0)
    dc_links = solara.use_reactive(data_collection.links)

    def _add_link():
        add_link(
            data_collection[selected_data1.value],
            data_collection[selected_data1.value].components[selected_row1.value],
            data_collection[selected_data2.value],
            data_collection[selected_data2.value].components[selected_row2.value],
        )
        dc_links.set(
            [
                *data_collection.links,
                str(data_collection[selected_data1.value].components[selected_row1.value])
                + "<->"
                + str(data_collection[selected_data2.value].components[selected_row1.value]),
            ]
        )

    with solara.Card("Link Editor", style="width: fit-content;"):
        with solara.Row():
            data_dict = [
                {"label": data.label, "value": index} for index, data in enumerate(data_collection)
            ]
            LinkSelector(data_dict, selected_data1, selected_row1)
            LinkSelector(data_dict, selected_data2, selected_row2)
            if show_list:
                with solara.Column():
                    solara.Text("Current Links")
                    with solara.v.List():
                        for link in dc_links.value:
                            with solara.v.ListItem():
                                with solara.v.ListItemContent():
                                    solara.v.ListItemTitle(children=[str(link)])

        with solara.CardActions():
            solara.v.Spacer()
            solara.Button(
                label="Glue Attributes",
                color="primary",
                on_click=_add_link,
            )


@solara.component
def LinkSelector(
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
        print(selected_data.value, selected_row.value)
        solara.Text(f"Attributes for {data_dict[selected_data.value]['label']}")
        with solara.v.List():
            with solara.v.ListItemGroup(
                v_model=selected_row.value,
                on_v_model=selected_row.set,
                color="primary",
            ):
                for attribute in data_collection[selected_data.value].components:
                    with solara.v.ListItem():
                        with solara.v.ListItemContent():
                            solara.v.ListItemTitle(children=[attribute.label])
