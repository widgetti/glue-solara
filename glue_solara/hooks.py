import glue.core.hub
import glue.core.message
import solara
from glue.viewers.common.viewer import Viewer


class DummyListener(glue.core.hub.HubListener):
    def notify(self, message):
        pass


helper = []


def use_glue_watch(hub: glue.core.hub.Hub, msg_class=glue.core.message.Message):
    # listener = solara.use_memo(lambda: DummyListener(), [])
    counter, set_counter = solara.use_state(0)

    def on_msg(msg):
        # breakpoint()
        # print("MSG", msg, counter)
        set_counter(lambda counter: counter + 1)

    def connect():
        listener = DummyListener()
        helper.append(listener)
        # breakpoint()
        hub.subscribe(listener, msg_class, handler=on_msg)
        assert listener in hub._subscriptions
        # def clean
        # return lambda: hub.unsubscribe(listener, msg_class)

    solara.use_effect(connect, [id(hub)])


def use_layers_watch(viewers: list[Viewer]):
    """Using this hook causes the component to rerender when one of the viewers layers changes"""
    # we use this in DataList, and we need to trigger *after* _layer_artist_container changes
    # which is the reason we listen to that instead of state.layers
    force_update_counter, set_force_update_counter = solara.use_state(0)

    def listen_to_layers():
        def force_update(*ignore_arguments):
            set_force_update_counter(lambda x: x + 1)

        for viewer in viewers:
            viewer._layer_artist_container.change_callbacks.append(force_update)

        def cleanup():
            for viewer in viewers:
                viewer._layer_artist_container.change_callbacks.remove(force_update)

        return cleanup

    solara.use_effect(listen_to_layers, viewers)
