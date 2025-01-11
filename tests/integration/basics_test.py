import playwright.sync_api
from playwright.sync_api import expect


def test_add_data_current_viewer(
    page_session: playwright.sync_api.Page, solara_server, solara_app, assert_solara_snapshot
):
    with solara_app("glue_solara.app"):
        page_session.goto(solara_server.base_url)
        add_data = page_session.locator("button", has_text="load data")
        add_data.wait_for()
        add_data.click()
        expect(page_session.locator("button")).to_have_count(5)
        page_session.locator("button", has_text="add w5 data").click()
        page_session.locator("button", has_text="an image").click()
        page_session.locator("div.bqplot.figure").wait_for()
        add_to_figure = page_session.locator(
            "button.v-btn--icon:not(.v-btn--disabled)", has=page_session.locator("i.mdi-tab-plus")
        )
        expect(add_to_figure).to_have_count(1)
        add_to_figure.click()
        # Tried to assert with screenshot, but seems the graph is not consistent
        # assert_solara_snapshot(page_session.locator("div.bqplot.figure").screenshot())
        expect(page_session.get_by_role("button", disabled=True)).to_have_count(2)


def test_tabbed_viewers(page_session: playwright.sync_api.Page, solara_server, solara_app):
    with solara_app("glue_solara.app"):
        page_session.goto(solara_server.base_url)
        add_data = page_session.locator("button", has_text="load data")
        add_data.wait_for()
        add_data.click()
        page_session.locator("button", has_text="add w5 data").click()
        page_session.locator("button", has_text="an image").click()
        page_session.locator("div.bqplot.figure").wait_for()
        add_figure = page_session.locator("button", has=page_session.locator("i.mdi-tab")).nth(1)
        expect(add_figure).to_be_attached()
        add_figure.click()
        page_session.locator("button", has_text="add").click()
        expect(page_session.locator("div.v-tab")).to_have_count(2)


def test_tabbed_viewer_close(page_session: playwright.sync_api.Page, solara_server, solara_app):
    with solara_app("glue_solara.app"):
        page_session.goto(solara_server.base_url)
        add_data = page_session.get_by_role("button", name="load data")
        add_data.wait_for()
        add_data.click()
        page_session.locator("button", has_text="add w5 data").click()
        page_session.locator("button", has_text="an image").click()
        page_session.locator("div.bqplot.figure").wait_for()
        close_viewer = page_session.locator("button", has=page_session.locator("i.mdi-close"))
        expect(close_viewer).to_have_count(1)
        close_viewer.click()
        expect(page_session.locator("div.bqplot.figure")).not_to_be_attached()
        expect(page_session.get_by_text("What do you want to visualize")).to_be_visible()


def test_mdi_viewers(page_session: playwright.sync_api.Page, solara_server, solara_app):
    with solara_app("glue_solara.app"):
        page_session.goto(solara_server.base_url)
        add_data = page_session.locator("button", has_text="load data")
        add_data.wait_for()
        add_data.click()
        page_session.locator("button", has_text="add w5 data").click()
        page_session.get_by_role("button", name="mdi").click()
        page_session.locator("button", has_text="an image").click()
        page_session.locator("div.glue-solara__window").wait_for()
        expect(page_session.locator("div.glue-solara__window")).to_have_count(1)
        add_figure = page_session.locator("button", has=page_session.locator("i.mdi-tab")).nth(1)
        expect(add_figure).to_be_attached()
        add_figure.click()
        page_session.locator("button", has_text="add").click()
        expect(page_session.locator("div.glue-solara__window")).to_have_count(2)


def test_mdi_viewers_close(page_session: playwright.sync_api.Page, solara_server, solara_app):
    with solara_app("glue_solara.app"):
        page_session.goto(solara_server.base_url)
        add_data = page_session.get_by_role("button", name="load data")
        add_data.wait_for()
        add_data.click()
        page_session.locator("button", has_text="add w5 data").click()
        page_session.get_by_role("button", name="mdi").click()
        page_session.locator("button", has_text="an image").click()
        page_session.locator("div.glue-solara__window").wait_for()
        expect(page_session.locator("div.glue-solara__window")).to_have_count(1)
        close_button = page_session.locator(
            "button", has=page_session.locator("i.mdi-close-circle-outline")
        )
        expect(close_button).to_have_count(1)
        close_button.click()
        expect(page_session.locator("div.glue-solara__window")).not_to_be_attached()
        expect(page_session.get_by_text("What do you want to visualize")).to_be_visible()
