from unittest.mock import MagicMock

import ipyvuetify as v
import solara
from glue.core.message import Message
from glue_jupyter.app import JupyterApplication

from glue_solara.hooks import ClosedMessage, use_glue_watch, use_glue_watch_close


def test_use_glue_watch():
    glue_app = JupyterApplication()
    handler = MagicMock()

    class CustomMessage(Message):
        def __init__(self):
            super().__init__(MagicMock())

    @solara.component
    def TestComponent():
        use_glue_watch(glue_app.session.hub, CustomMessage, on_msg=handler)

    box, rc = solara.render(TestComponent(), handle_error=False)
    assert len(glue_app.session.hub._subscriptions) == 5
    assert handler.call_count == 0
    glue_app.session.hub.broadcast(CustomMessage())
    assert handler.call_count == 1
    box.close()


def test_use_glue_watch_close():
    glue_app = JupyterApplication()
    handler = MagicMock()

    @solara.component
    def TestComponent():
        use_glue_watch_close(glue_app, on_msg=handler)

        def create_viewer():
            # There has to be some data added before we can create a viewer
            glue_app.load_data("w5.fits")
            glue_app.scatter2d(show=False)

        def close_viewer():
            msg = ClosedMessage(glue_app.viewers[0])
            glue_app.session.hub.broadcast(msg)

        solara.Button("open", on_click=create_viewer)
        solara.Button("close", on_click=close_viewer)

    box, rc = solara.render(TestComponent(), handle_error=False)
    assert len(glue_app.session.hub._subscriptions) == 5
    assert len(glue_app._viewer_refs) == 0
    assert handler.call_count == 0
    open_button, close_button = rc.find(v.Btn)
    open_button.widget.click()
    assert len(glue_app._viewer_refs) == 1
    assert handler.call_count == 0
    close_button.widget.click()
    assert len(glue_app._viewer_refs) == 0
    assert handler.call_count == 1
    box.close()
