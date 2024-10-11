import glue.core.hub
import glue.core.message
import glue_jupyter
import solara
from glue.viewers.common.viewer import Viewer


class DummyListener(glue.core.hub.HubListener):
    def notify(self, message):
        pass


# Message indicating a viewer should be closed
class ClosedMessage(glue.core.message.Message):
    def __init__(self, sender):
        super().__init__(sender=sender)


helper = []


def use_glue_watch(hub: glue.core.hub.Hub, msg_class=glue.core.message.Message, on_msg=None):
    # listener = solara.use_memo(lambda: DummyListener(), [])
    counter, set_counter = solara.use_state(0)

    def _on_msg(msg):
        # breakpoint()
        # print("MSG", msg, counter)
        set_counter(lambda counter: counter + 1)

    def connect():
        listener = DummyListener()
        helper.append(listener)
        # breakpoint()
        hub.subscribe(listener, msg_class, handler=on_msg or _on_msg)
        assert listener in hub._subscriptions

        def cleanup():
            hub.unsubscribe(listener, msg_class)
            # print("cleanup", len(hub._subscriptions))

        return cleanup

    solara.use_effect(connect, [id(hub)])


def use_glue_watch_close(app: glue_jupyter.JupyterApplication, on_msg=None):
    counter, set_counter = solara.use_state(0)

    def remove_viewer(msg):
        if on_msg is not None:
            on_msg(msg)
        viewers = app._viewer_refs
        for _viewer in viewers:
            viewer = _viewer()
            if viewer is not None and viewer is msg.sender:
                # TODO: a proper close method should be implemented in glue-jupyter
                viewer.cleanup()
                viewers.remove(_viewer)
        set_counter(lambda counter: counter + 1)

    use_glue_watch(app.session.hub, ClosedMessage, remove_viewer)


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
