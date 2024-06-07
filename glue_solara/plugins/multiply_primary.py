import solara
import glue_jupyter as gj
from glue.core.message import Message, DataCollectionAddMessage, DataCollectionDeleteMessage
from glue.core.hub import HubListener

__all__ = ['PluginState', 'PluginUI']

# base class inherited by all plugins
class SidebarWidgetState(HubListener):
    def __init__(self, app: gj.JupyterApplication):
        self._app = app
        self._hub = app.session.hub
        self.name = "Multiply PRIMARY Data"
        self.icon = "fa fa-plus"
        self.is_relevant = solara.reactive(False)


class PluginState(SidebarWidgetState):
    def __init__(self, app: gj.JupyterApplication):
        super().__init__(app)
        self.multiply_by = solara.reactive(2)

        self._hub.subscribe(self, DataCollectionAddMessage, handler=self._on_data_added)
        self._hub.subscribe(self, DataCollectionDeleteMessage, handler=self._on_data_deleted)
        # currently no message for adding/removing viewers

    def _on_data_added(self, msg):
        if self.is_relevant.value:
            return
        if msg.data is not None:
            if 'PRIMARY' in [c.label for c in msg.data.components]:
                self.is_relevant.value = True
                return

    def _on_data_deleted(self, msg):
        if not self.is_relevant.value:
            return
        # need to check if 'PRIMARY' in any remaining data collection entry
        for data in self._app.data_collection:
            if 'PRIMARY' in [c.label for c in data.components]:
                # leave is_relevant.value = True
                return
        else:
            self.is_relevant.value = False

    def multiply(self):
        for data in self._app.data_collection:
            if 'PRIMARY' in [c.label for c in data.components]:
                print(f"multiplying by {self.multiply_by.value}")
                data.update_components({data.get_component('PRIMARY'): self.multiply_by.value * data['PRIMARY']})
        for viewer in self._app.viewers:
            viewer.state.reset_limits()

@solara.component
def PluginUI(state: PluginState):
    solara.SliderInt("Multiply by", value=state.multiply_by)
    solara.Button(label=f"Multiply by {state.multiply_by.value}", on_click=state.multiply)  # adding icon='fas fa-multiply' gives a cryptic error
    for data in state._app.data_collection:
        if 'PRIMARY' in [c.label for c in data.components]:
            solara.Text(f"* {data.label}")
