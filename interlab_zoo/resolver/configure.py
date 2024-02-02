import ipywidgets as widgets

from .resolver import Experiment, Person


def on_change_set_attribute(widget, obj, name):
    def on_change(change):
        setattr(obj, name, change["new"])

    widget.observe(on_change, names="value")


def textarea(description, obj, name):
    layout = {"width": "95%", "height": "150px"}
    w = widgets.Textarea(
        value=getattr(obj, name),
        description=description,
        layout=layout,
    )
    on_change_set_attribute(w, obj, name)
    return w


def text(description, obj, name):
    w = widgets.Text(
        value=getattr(obj, name),
        description=description,
        layout={"description_width": "200px"},
    )
    on_change_set_attribute(w, obj, name)
    return w


def inttext(description, obj, name):
    w = widgets.IntText(
        value=getattr(obj, name),
        description=description,
        layout={"description_width": "200px"},
    )
    on_change_set_attribute(w, obj, name)
    return w


def _person_form(person: Person, on_change_name):
    items = []
    w = widgets.Text(
        value=person.name,
        description="Name:",
    )
    w.observe(on_change_name, names="value")
    items.append(w)

    items.append(textarea("Public info:", person, "public"))
    items.append(textarea("Private info:", person, "private"))

    return widgets.VBox(children=items, layout={"width": "900px", "height": "355px"})


def _prompt_form(exp: Experiment):
    items = [
        text("Expr name:", exp, "experiment_name"),
        text("Topic:", exp, "agreement_topic"),
        textarea("Prompt:", exp, "prompt"),
        text("Message:", exp, "message_header"),
        inttext("Max msgs:", exp, "max_messages"),
    ]
    return widgets.VBox(children=items, layout={"width": "900px", "height": "355px"})


def configure(exp: Experiment):
    def create_on_change_name(i):
        def on_change(change):
            value = change["new"]
            exp.people[i].name = value
            w.set_title(i, value)

        return on_change

    tabs = []
    tab_names = []
    w = widgets.Accordion(
        children=[
            _person_form(person, create_on_change_name(i))
            for i, person in enumerate(exp.people)
        ]
    )
    for i, person in enumerate(exp.people):
        w.set_title(i, person.name)
    tabs.append(w)
    tab_names.append("People")

    tabs.append(_prompt_form(exp))
    tab_names.append("Config")
    return widgets.Tab(children=tabs, titles=tab_names)
