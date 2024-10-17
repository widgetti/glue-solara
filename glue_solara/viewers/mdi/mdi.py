from typing import Callable, List, Optional, TypedDict

import solara
from typing_extensions import NotRequired

MDI_HEADER_SIZES = ["x-small", "small", None, "large", "x-large"]


class MdiWindow(TypedDict):
    title: str
    width: int
    height: int
    x: NotRequired[int]
    y: NotRequired[int]
    order: NotRequired[int]


@solara.component_vue("mdi.vue")
def Mdi(
    windows: List[MdiWindow],
    on_windows: Callable[[List[MdiWindow]], None],
    children: List,
    size: Optional[str] = None,
    event_close: Optional[Callable[[int], None]] = None,
):
    """
    :param size: size of header, options "x-small" | "small" | None | "large" | "x-large"
    """
    pass


@solara.component
def Panel1(name: str):
    with solara.v.Sheet(style_="height: 100%; padding: 16px"):
        solara.Button(name, color="primary")


@solara.component
def Page():
    size = solara.use_reactive(None)
    content = solara.use_reactive(["Aaaa", "Bbbb"])
    windows = solara.use_reactive([{"title": f"title for {t}"} for t in ["Aaaa", "Bbbb"]])
    name_counter = solara.use_reactive(1)

    def add():
        content.value = [*content.value, str(name_counter.value)]
        windows.value = [*windows.value, {"title": f"title for {name_counter.value}"}]
        name_counter.value += 1

    def remove(index: Optional[int]):
        if index is not None:
            content.value = [e for i, e in enumerate(content.value) if i != index]
            windows.value = [e for i, e in enumerate(windows.value) if i != index]

    with solara.Div(style="height: 100vh"):
        with solara.Div(style_="height: 100%; display: flex"):
            with solara.Div(style_="width: 444px; min-width: 444px; border: 2px dashed green"):
                solara.Text("Some space")
            with solara.Div(
                style_="height: 100%; display: flex; flex-direction: column; flex-grow: 1"
            ):
                with solara.Div(style_="flex-grow: 1"):
                    with Mdi(
                        windows=windows.value,
                        on_windows=windows.set,
                        size=size.value,
                        event_close=remove,
                    ):
                        for c in content.value or []:
                            Panel1(c).key(c)
                with solara.Div():
                    with solara.ToggleButtonsSingle(value=size, on_value=size.set):
                        solara.Button("x-small", value="x-small")
                        solara.Button("small", value="small")
                        solara.Button("None", value=None)
                        solara.Button("large", value="large")
                        solara.Button("x-large", value="x-large")
                    solara.Button("add window", color="primary", on_click=add)
                    solara.Div(children=[str(windows.value)])
