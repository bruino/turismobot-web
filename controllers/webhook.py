# -*- coding: utf-8 -*-
from dialogflow_response.response import *


def call():
    session.forget()
    return service()


# TODO: add DIALOGFLOW_CONSOLE platform to my library dialogflow-response.
def platform_for_request(req):
    platform = req["originalDetectIntentRequest"]["source"]
    if platform == "DIALOGFLOW_CONSOLE" or platform == "google":
        platform = "ACTIONS_ON_GOOGLE"
    if platform == "telegram":
        platform = "TELEGRAM"
    return platform


def recorrido_turistico_1(req):
    platform = platform_for_request(req)
    text = "¿Qué es lo que desea hacer?"
    choices = [row.nombre for row in db().select(db.tipo_turismo.nombre)]

    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [
            ChoicesResponse(text, choices).for_plataform(platform),
        ]
    )
    return response


def recorrido_turistico_2(req):
    req_tipo_turismo__nombre = req["queryResult"]["parameters"]["tipo_turismo"]
    platform = platform_for_request(req)
    row_tipo_turismo = (
        db(db.tipo_turismo.valor == req_tipo_turismo__nombre).select().first()
    )

    if not row_tipo_turismo:
        return [
            SimpleResponse(
                "Por momento no hay actividades de éste tipo ahora"
            ).for_plataform(platform)
        ]

    choices = [
        row.nombre
        for row in db(db.lugar_turistico.tipo == row_tipo_turismo.id).select(
            db.lugar_turistico.nombre
        )
    ]

    text = "Estos son los lugares que tenemos"
    message = ChoicesResponse(text, choices).for_plataform(platform)

    response = FulfillmentResponse(text)
    response.set_fulfillment_messages([message])
    return response


def recorrido_turistico_3(req):
    platform = platform_for_request(req)
    text = "Esperamos que disfrutes tú tiempo aquí en nuestra provincia"

    if platform == "ACTIONS_ON_GOOGLE":
        message = {
            "platform": "ACTIONS_ON_GOOGLE",
            "suggestions": {
                "suggestions": [
                    {"title": "Otras opciones"},
                    {"title": "Muchas gracias"},
                ]
            },
        }
    else:
        message = ChoicesResponse(
            "¿Te pareció útil?", ["Quiero otras opciones", "¡Si! Muchas gracias"]
        ).for_plataform(platform)

    req_lugar_turistico = req["queryResult"]["parameters"]["lugar_turistico"]
    row_lugar_turistico = (
        db(db.lugar_turistico.nombre == req_lugar_turistico).select().first()
    )

    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [
            SimpleResponse(text).for_plataform(platform),
            CardResponse(
                row_lugar_turistico.nombre,
                "subtitle",
                row_lugar_turistico.descripcion,
                URL("default", "download", args=row_lugar_turistico.imagen),
                [
                    ["URL", row_lugar_turistico.url],
                    ["Ubicación", row_lugar_turistico.url_gmaps],
                ],
            ).for_plataform(platform),
            message,
        ]
    )
    return response


# Function Dispatcher:
# { "name action intent": function }
DISPATCHER = {
    "recorrido_turistico_1": recorrido_turistico_1,
    "recorrido_turistico_2": recorrido_turistico_2,
    "recorrido_turistico_3": recorrido_turistico_3,
}


@service.json
def endpoint():
    req = request.post_vars
    name_intent = req["queryResult"]["action"]

    if name_intent not in DISPATCHER:
        return FulfillmentResponse("No lo entiendo mi estimado :/").as_dict()

    response = DISPATCHER[name_intent](req)
    return response.as_dict()
