def index():
    localidad_id = request.args(0)
    rows = db(db.hospedaje.localidad == localidad_id).select()
    return dict(rows=rows)