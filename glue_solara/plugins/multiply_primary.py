import solara
import glue_jupyter as gj
from glue.core.message import DataCollectionAddMessage, DataCollectionDeleteMessage
from glue.core.hub import HubListener

__all__ = ['PluginState', 'PluginUI']

# base class inherited by all plugins
class SidebarWidgetState(HubListener):
    def __init__(self, app: gj.JupyterApplication):
        self._app = app
        self._hub = app.session.hub
        self._name = "Multiply PRIMARY Data"
        self._is_relevant = solara.reactive(False)

    @property
    def name(self):
        return self._name

    def show(self):
        solara.display(PluginUI(self))


class PluginState(SidebarWidgetState):
    def __init__(self, app: gj.JupyterApplication):
        super().__init__(app)
        self._multiply_by = solara.reactive(2)
        self._message = solara.reactive("")

        self._hub.subscribe(self, DataCollectionAddMessage, handler=self._on_data_added)
        self._hub.subscribe(self, DataCollectionDeleteMessage, handler=self._on_data_deleted)
        # currently no message for adding/removing viewers

    @property
    def multiply_by(self):
        return self._multiply_by.value

    @multiply_by.setter
    def multiply_by(self, value):
        # NOTE: this is only called when setting from the API, not from the UI
        # If adding any extra logic that should react to a change to multiply_by,
        self._multiply_by.value = value
        if value > 6:
            self._message.value = f"Multiplying by large value ({value})"
        else:
            self._message.value = ""

    @property
    def message(self):
        return self._message.value

    def _on_data_added(self, msg):
        if self._is_relevant.value:
            return
        if msg.data is not None:
            if 'PRIMARY' in [c.label for c in msg.data.components]:
                self._is_relevant.value = True
                return

    def _on_data_deleted(self, msg):
        if not self._is_relevant.value:
            return
        # need to check if 'PRIMARY' in any remaining data collection entry
        for data in self._app.data_collection:
            if 'PRIMARY' in [c.label for c in data.components]:
                # leave is_relevant.value = True
                return
        else:
            self._is_relevant.value = False

    def multiply(self):
        for data in self._app.data_collection:
            if 'PRIMARY' in [c.label for c in data.components]:
                data.update_components({data.get_component('PRIMARY'): self.multiply_by * data['PRIMARY']})
        for viewer in self._app.viewers:
            viewer.state.reset_limits()

@solara.component
def PluginUI(state: PluginState):
    solara.SliderInt("Multiply by", value=state.multiply_by, on_value=lambda value: setattr(state, 'multiply_by', value))  # lambda value: state.multiply_by := value
    solara.Button(label=f"Multiply by {state.multiply_by}", on_click=state.multiply)
    for data in state._app.data_collection:
        if 'PRIMARY' in [c.label for c in data.components]:
            solara.Text(f"* {data.label}")
    if len(state.message):
        solara.Warning(state.message)
