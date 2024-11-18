import random

from django import template

register = template.Library()


possible_texts = [
    "Du bist die Brandmauer gegen Rechts",
    "„Unpolitisch“ ist politisch",
    "Die AfD ist die mit Abstand größte Gefahr für unsere Gesellschaft! #AfDVerbotJetzt",
    "Sich an Antifaschismus stören ist so 1933",
    "Dieser Service wird nicht von Faschisten betrieben",
    "Menschenrechte statt rechte Menschen",
    "Kein Mensch ist illegal",
    "„Nie wieder“ ist immer, nicht nur alle 4 Jahre beim Kreuzchen machen",
    "Kein Platz für Rassismus",
    "Trans rights are human rights",
    "Trans rights or riot nights",
    "Die Brandmauer ist überall. Auch im Studium!",
    "Nazis morden, der Staat schiebt ab – das ist das gleiche Rassistenpack",
    "AfDler verpisst euch – keiner vermisst euch",
    "Seenotrettung ist kein Verbrechen",
    "Nein heißt Nein, No means No, wer das sagt der meints auch so",
]


@register.simple_tag
def stabile_message() -> str:
    return random.choice(possible_texts)
