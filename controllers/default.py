# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
def index():
    return dict()


@auth.requires_login()
def recorrido_turistico():
    db.lugar_turistico._plural = "Lugares Turísticos"
    db.lugar_turistico.id.readable = False
    db.lugar_turistico.tipo.represent = lambda id, r: db.tipo_turismo[id].nombre
    db.lugar_turistico.url.represent = lambda id, r: A(r.url)
    db.lugar_turistico.url_gmaps.represent = lambda id, r: A(r.url_gmaps)

    fields = [
        db.lugar_turistico.nombre,
        db.lugar_turistico.descripcion,
        db.lugar_turistico.tipo,
        db.lugar_turistico.telefono,
    ]

    form = SQLFORM.smartgrid(
        db.lugar_turistico,
        breadcrumbs_class="breadcrumb",
        fields=fields,
        csv=False,
    )
    return dict(form=form)


@auth.requires_login()
def hospedaje():
    form = SQLFORM.smartgrid(
        db.hospedaje,
        breadcrumbs_class="breadcrumb",
        csv=False,
    )

    return dict(form=form)

@auth.requires_login()
def localidad():
    form = SQLFORM.smartgrid(
        db.localidad,
        breadcrumbs_class="breadcrumb",
        csv=False,
    )

    return dict(form=form)

@auth.requires_login()
def restaurante():
    form = SQLFORM.smartgrid(
        db.restaurante,
        breadcrumbs_class="breadcrumb",
        csv=False,
    )

    return dict(form=form)

@auth.requires_login()
def eventos():
    return dict()

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == "GET":
        raise HTTP(403)
    return response.json({"status": "success", "email": auth.user.email})


# ---- Smart Grid (example) -----
@auth.requires_membership("admin")  # can only be accessed by members of admin groupd
def grid():
    response.view = "generic.html"  # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables:
        raise HTTP(403)
    grid = SQLFORM.smartgrid(
        db[tablename], args=[tablename], deletable=False, editable=False
    )
    return dict(grid=grid)


# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu()  # add the wiki to the menu
    return auth.wiki()


# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
