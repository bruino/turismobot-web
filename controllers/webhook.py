# -*- coding: utf-8 -*-
from dialogflow_response.response import *
import requests

configuration = AppConfig(reload=True)

def call():
    session.forget()
    return service()


# TODO: add DIALOGFLOW_CONSOLE platform to my library dialogflow-response.
def platform_for_request(req):  # rename to get_platform()
    platform = req["originalDetectIntentRequest"]["source"]
    if platform == "DIALOGFLOW_CONSOLE" or platform == "google":
        platform = "ACTIONS_ON_GOOGLE"
    if platform == "telegram":
        platform = "TELEGRAM"
    return platform


def recorrido_turistico_1(req):
    platform = platform_for_request(req)
    text = "Tenemos muchas opciones interesantes para ofrecerte sobre lo que podes hacer o conocer en la provincia. Seleccioná una opción para conocer más."
    choices = [row.nombre for row in db().select(db.tipo_turismo.nombre)]

    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [
            ChoicesResponse(text, choices).for_platform(platform),
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
            ).for_platform(platform)
        ]

    choices = [
        row.nombre
        for row in db(db.lugar_turistico.tipo == row_tipo_turismo.id).select(
            db.lugar_turistico.nombre
        )
    ]

    text = "Excelente selección. Te muestro algunas de las opciones disponibles."
    message = ChoicesResponse(text, choices).for_platform(platform)

    response = FulfillmentResponse(text)
    response.set_fulfillment_messages([message])
    return response


def recorrido_turistico_3(req):
    platform = platform_for_request(req)
    text = "Espero que disfrutes tu tiempo en la provincia."

    if platform == "ACTIONS_ON_GOOGLE":
        message = {
            "platform": "ACTIONS_ON_GOOGLE",
            "suggestions": {
                "suggestions": [
                    {"title": "Comenzar de nuevo"},
                    {"title": "Muchas gracias"},
                ]
            },
        }
    else:
        message = ChoicesResponse(
            "¿Te pareció útil?", ["Volver al inicio", "¡Si! Muchas gracias"]
        ).for_platform(platform)

    req_lugar_turistico = req["queryResult"]["parameters"]["lugar_turistico"]
    row_lugar_turistico = (
        db(db.lugar_turistico.nombre == req_lugar_turistico).select().first()
    )
    card = CardResponse(
                row_lugar_turistico.nombre,
                "Tucumán",
                row_lugar_turistico.descripcion,
                URL("default", "download", scheme='https', args=row_lugar_turistico.imagen),
                [
                    ["URL", row_lugar_turistico.url],
                ],
            ).for_platform(platform)
    if platform == 'ACTIONS_ON_GOOGLE':
        card['basicCard']['image']['accessibilityText'] = 'alt'

    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [
            SimpleResponse(text).for_platform(platform),
            card,
            message,
        ]
    )
    return response


def get_hospedajes(platform, localidad):
    localidad = db(db.localidad.nombre == localidad).select(db.localidad.id, db.localidad.nombre).first()

    if not localidad:
        text = 'No disponemos de hospedaje en ésta zona.'
        
        messages = list()
        messages.append(
            ChoicesResponse(
                f"{text} \n¿Te pareció útil?", ["Volver al inicio", "No, muchas gracias 👌"]
            ).for_platform(platform)
        )
        
        response = FulfillmentResponse(text)
        response.set_fulfillment_messages(messages)
        return response


    text = "Disponemos de estos hoteles"
    response = FulfillmentResponse(text)

    messages = list()
    messages.append(SimpleResponse(text).for_platform(platform))
    messages.append(
        CardResponse(
            f"Hoteles en {localidad.nombre}",
            None,
            "Lo invitamos a que observe nuestra selección de hoteles de confianza.",
            buttons=[['Ver hoteles', f"https://{request.env.http_host}/turismobot/hospedaje/index/{localidad.id}"]]
        ).for_platform(platform)
    )
    if platform == "ACTIONS_ON_GOOGLE":
        messages.append(
            {
                "platform": "ACTIONS_ON_GOOGLE",
                "suggestions": {
                    "suggestions": [
                        {"title": "Volver al inicio"},
                        {"title": "Muchas gracias"},
                    ]
                },
            }
        )
    else:
        messages.append(
            ChoicesResponse(
                "¿Te pareció útil?", ["Volver al inicio", "¡Si! Muchas gracias"]
            ).for_platform(platform)
        )

    response.set_fulfillment_messages(messages)
    return response


def hospedaje_1(req):
    platform = platform_for_request(req)
    text = "Tenemos muchas opciones interesantes para ofrecerte sobre dónde dormir en la provincia"
    choices = ["📍 Opciones cercanas", "San Miguel de Tucumán", "Tafí del Valle", "Cadillal"]
    choices += db().select(db.localidad.nombre).to_list()

    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [
            ChoicesResponse(text, choices).for_platform(platform),
        ]
    )
    return response


def hospedaje_2_hospedajes(req):
    platform = platform_for_request(req)
    localidad = req["queryResult"]["parameters"]["geo-city"]
    response = get_hospedajes(platform, localidad)
    return response


def hospedaje_2_ubicacion(req):
    platform = platform_for_request(req)
    text = "Permítame su ubicación para buscar hoteles alrededor."
    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [RequestLocationResponse(text).for_platform(platform)]
    )
    return response


def hospedaje_3_ubicacion_aog(req):
    platform = platform_for_request(req)
    print(req["originalDetectIntentRequest"])
    if not "device" in req["originalDetectIntentRequest"]["payload"]:
        text = 'No podemos encontrar hoteles si no disponemos de tu ubicación.'
        
        messages = list()
        messages.append(
            ChoicesResponse(
                f"{text}", ["Entendido", "Otras opciones"]
            ).for_platform(platform)
        )
        
        response = FulfillmentResponse(text)
        response.set_fulfillment_messages(messages)
        return response


    lat = req["originalDetectIntentRequest"]["payload"]["device"]["location"][
        "coordinates"
    ]["latitude"]
    lng = req["originalDetectIntentRequest"]["payload"]["device"]["location"][
        "coordinates"
    ]["longitude"]

    # print(f'{lat} {lng}')
    # pip install geocoder --target site-packages/
    # import geocoder
    # g = geocoder.osm([lat,lng], method='reverse')

    r = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={configuration.get('google.place')}")
    address = r.json()['results'][0]['formatted_address'].split(',')[0].split(' ', 1)[1]
    
    choices = list()
    if not address:
        text = "No podemos precisar su localidad."
        choices.append("Entendido")
        response = FulfillmentResponse(text)
        response.set_fulfillment_messages(
            [
                ChoicesResponse(text, choices).for_platform(platform),
            ]
        )
    choices = [address, "Ninguna opción"]

    text = "¿En qué lugar se desea hospedar?"
    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [
            ChoicesResponse(text, choices).for_platform(platform),
        ]
    )
    return response


def hospedaje_4_ubicacion_aog_hospedajes(req):
    platform = platform_for_request(req)
    localidad = req["queryResult"]["parameters"]["geo-city"]
    response = get_hospedajes(platform, localidad)
    return response


def restaurantes_1(req):
    platform = platform_for_request(req)
    text = "Comparte tu ubicación para poder recomendarte opciones cercanas para comer"
    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(
        [RequestLocationResponse(text).for_platform(platform)]
    )
    return response


def restaurantes_2_ubicacion_aog_si(req):
    platform = platform_for_request(req)

    if not "device" in req["originalDetectIntentRequest"]["payload"]:
        text = 'No podemos encontrar restaurantes si no disponemos de tu ubicación.'
        
        messages = list()
        messages.append(
            ChoicesResponse(
                f"{text}", ["Entendido", "Otras opciones"]
            ).for_platform(platform)
        )
        
        response = FulfillmentResponse(text)
        response.set_fulfillment_messages(messages)
        return response

    text = "Éstos restaurantes tienes a tu alrededor."
    lat = req["originalDetectIntentRequest"]["payload"]["device"]["location"][
        "coordinates"
    ]["latitude"]
    lng = req["originalDetectIntentRequest"]["payload"]["device"]["location"][
        "coordinates"
    ]["longitude"]

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1500&type=restaurant&key={configuration.get('google.place')}"
    print(url)
    r = requests.get(
        url
    )

    messages = list()

    if len(r.json()["results"]) < 5:
        messages.append(
            ChoicesResponse(
                f"{text} \nNo hay restaurantes cerca tuyo ahora", ["Volver al inicio", "Muchas gracias 👌"]
            ).for_platform(platform)
        )
        response = FulfillmentResponse(text)
        response.set_fulfillment_messages(messages)
        return response

    if platform == "ACTIONS_ON_GOOGLE":
        items = []
        for restaurant in r.json()["results"][:5]: # TODO: resolver cuando no hay lugares a disposición.
            items.append(
                {
                    "title": restaurant["name"],
                    "openUrlAction": {
                        "url": f"https://www.google.com/maps/search/?api=1&query={restaurant['geometry']['location']['lat']},{restaurant['geometry']['location']['lng']}"
                    },
                    "description": f"Rating /5",
                    "footer": restaurant["vicinity"],
                    "image": {
                        "url": 'https://e7.pngegg.com/pngimages/554/203/png-clipart-restaurant-computer-icons-food-menu-menu-text-eating.png',
                        "accessibilityText": "alt",
                    },
                }
            )
        messages.append(
            {
                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": text,
                                    }
                                },
                                {"carouselBrowse": {"items": items}},
                            ]
                        },
                    }
                }
            },
        )
    # else:
    #     response_messages = list()
    #     for restaurant in r.json()["results"][:5]:    
    #         response_messages.append(
    #             f'''
    #             🍴*{restaurant["name"]}*
    #             - 📍{restaurant["vicinity"]}
    #             - Link: https://www.google.com/maps/search/?api=1&query={restaurant['geometry']['location']['lat']},{restaurant['geometry']['location']['lng']}

    #             '''
    #         )

    #     messages.append(
    #         SimpleResponse(
    #             ''.join(response_messages)
    #         ).for_platform(platform)
    #     )

    # AÑADIDO
    messages.append(
            ChoicesResponse(
                f"{text} \n¿Te pareció útil?", ["Volver al inicio", "Muchas gracias 👌"]
            ).for_platform(platform)
        )
    # text = "¿Tenés antojo de algun plato en especial?"
    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(messages)
    return response

def eventos(req):
    platform = platform_for_request(req)
    text = "Éstas son las opciones disponibles éste mes."


    messages = list()
    if platform == "ACTIONS_ON_GOOGLE":
        items = []
        for row in db().select(db.evento.ALL):
            items.append(
                {
                    "title": row.nombre,
                    "openUrlAction": {
                        "url": row.url
                    },
                    "description": row.descripcion,
                    "footer": row.fecha,
                    "image": {
                        "url": f"{ URL('default', 'download', scheme='https', args=row.imagen) }",
                        "accessibilityText": "alt",
                    },
                }
            )
        messages.append(
            {
                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": text,
                                    }
                                },
                                {"carouselBrowse": {"items": items}},
                            ]
                        },
                    }
                }
            },
        )
    else:
        response_messages = list()
        for row in db().select(db.evento.ALL):
            response_messages.append(
                f'''
                🍴*{row.nombre}*
                - {row.descripcion}
                - {row.fecha}
                - {row.url}
                '''
            )

        messages.append(
            SimpleResponse(
                ''.join(response_messages)
            ).for_platform(platform)
        )

    # AÑADIDO
    messages.append(
            ChoicesResponse(f"{text} \n¿Te pareció útil?", ["Volver al inicio", "No, muchas gracias 👌"]
            ).for_platform(platform)
        )
    # text = "¿Tenés antojo de algun plato en especial?"
    response = FulfillmentResponse(text)
    response.set_fulfillment_messages(messages)
    return response

# Function Dispatcher:
# { "name action intent": function }
DISPATCHER = {
    "recorrido_turistico_1": recorrido_turistico_1,
    "recorrido_turistico_2": recorrido_turistico_2,
    "recorrido_turistico_3": recorrido_turistico_3,
    "hospedaje_1": hospedaje_1,
    "hospedaje_2_hospedajes": hospedaje_2_hospedajes,
    "hospedaje_2_ubicacion": hospedaje_2_ubicacion,
    "hospedaje_3_ubicacion_aog": hospedaje_3_ubicacion_aog,
    "hospedaje_4_ubicacion_aog_hospedajes": hospedaje_4_ubicacion_aog_hospedajes,
    "restaurantes_1": restaurantes_1,
    "restaurantes_2_ubicacion_aog_si": restaurantes_2_ubicacion_aog_si,
    "eventos": eventos,
}


@service.json
def endpoint():
    req = request.post_vars
    name_intent = req["queryResult"]["action"]
    print(f"{name_intent}")
    if name_intent not in DISPATCHER:
        return FulfillmentResponse("No lo entiendo mi estimado :/").as_dict()

    response = DISPATCHER[name_intent](req)
    return response.as_dict()