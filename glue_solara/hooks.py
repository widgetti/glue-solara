import glue.core.hub
import glue.core.message
import solara


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
