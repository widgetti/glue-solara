from typing import Dict, List

import solara


@solara.component_vue("mdi.vue")
def Mdi(windows: List[Dict], children: List):
    pass


@solara.component
def Panel1(name: str):
    with solara.v.Sheet(style_="height: 100%; padding: 16px"):
        solara.Button(name, color="primary")


@solara.component
def Page():
    content = solara.use_reactive({0: "Aaaa", 1: "Bbbb"})
    windows = solara.use_reactive(
        [
            {
                "id": 0,
            },
            {
                "id": 1,
            },
        ]
    )

    def update_windows(new_windows):
        windows.set(new_windows)
        content.value = {
            k: v for k, v in content.value.items() if k in [e["id"] for e in new_windows]
        }

    def add():
        new_id = max([w["id"] for w in windows.value]) + 1
        content.value = {**content.value, new_id: str(new_id)}
        windows.value = [*windows.value, {"id": new_id}]

    with solara.Div(style="height: 100vh"):
        with solara.Div(style_="height: 100%; display: flex; flex-direction: column"):
            with solara.Div(style_="flex-grow: 1"):
                with Mdi(windows=windows.value, on_windows=update_windows):
                    for w in windows.value:
                        Panel1(content.value[w["id"]]).key(w["id"])
            with solara.Div():
                solara.Button("add window", color="primary", on_click=add)
                solara.Div(children=[str(windows.value)])
