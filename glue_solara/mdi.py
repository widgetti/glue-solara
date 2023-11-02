import solara


@solara.component_vue("mdi.vue")
def Mdi():
    pass


@solara.component
def Page():
    Mdi()
