# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    ("Inicio", False, URL("default", "index"), []),
]

if auth.user:
    response.menu.append(
        (
        "Módulos",
        False,
        False,
        [
            (
                "Recorrido turístico - ¿Qué hacer?",
                False,
                URL("default", "recorrido_turistico"),
            ),
            ("Hospedaje - ¿Dónde dormir?", False, URL("default", "hospedaje")),
            ("Restaurante - ¿Dónde comer?", False, URL("default", "restaurante")),
            ("Eventos", False, URL("default", "eventos")),
        ],
    ),
    )