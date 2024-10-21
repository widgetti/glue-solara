from typing import Union

import solara


@solara.component
def Snackbar(open_value: Union[bool, solara.Reactive[bool]], children: list[solara.Element] = []):
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
