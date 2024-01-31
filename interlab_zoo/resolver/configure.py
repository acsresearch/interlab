import ipywidgets as widgets

from .resolver import Experiment


def _person_form(person):
    w = widgets.Text(
        value=person.name,
        description="Name:",
        disabled=False,
    )
    return w


def configure(exp: Experiment):
    w = widgets.Accordion(children=[_person_form(person) for person in exp.people])
    for i, person in enumerate(exp.people):
        w.set_title(i, person.name)
    return w
