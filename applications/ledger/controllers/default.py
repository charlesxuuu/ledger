# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from time import sleep
import random
from pprint import pprint
from gluon.tools import Mail


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    db.auth_user.id.readable=False
    db.auth_user.id.writable=False
    db.auth_user.email.readable=False
    db.auth_user.email.writable=False
    db.auth_user.balance.readable=True
    db.auth_user.balance.writable=False

    db.auth_user.recent_count.readable=True
    db.auth_user.recent_count.writable=False
    db.auth_user.total_count.readable=True
    db.auth_user.total_count.writable=False

    crew = SQLFORM.grid(db.auth_user, deletable=False, editable=False, create=False, csv=False)
    images = db().select(db.image.ALL, orderby=db.image.title)
    return dict(message=T('Ledger'),crew=crew,images=images)


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

@auth.requires_login()
def show():
    image = db.image(request.args(0, cast=int)) or redirect(URL('index'))
    db.post.image_id.default = image.id
    db.post.author.default = auth.user.first_name
    form = SQLFORM(db.post, fields=['reply'])
    if form.process().accepted:
        response.flash = 'Your comment is posted'
    comments = db(db.post.image_id == image.id).select()
    return dict(image=image, comments=comments, form=form)



@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.smartgrid(db.image, linked_tables=['post'])
    return dict(grid=grid)

@auth.requires_membership('manager')
def crew():
    grid = SQLFORM.smartgrid(db.auth_user)
    return dict(grid=grid)

@auth.requires_membership('manager')
def candidate():
    db.auth_user.id.readable=True
    db.auth_user.id.writable=False
    db.auth_user.first_name.readable=True
    db.auth_user.first_name.writable=False
    db.auth_user.last_name.readable=True
    db.auth_user.last_name.writable=False
    db.auth_user.email.readable=False
    db.auth_user.email.writable=False
    db.auth_user.password.readable=False
    db.auth_user.password.writable=False

    db.auth_user.vehicle.readable=True
    db.auth_user.vehicle.writable=True
    db.auth_user.available.readable=True
    db.auth_user.available.writable=True
    db.auth_user.recent_count.readable=True
    db.auth_user.recent_count.writable=True

    candidate = SQLFORM.grid(db.auth_user, deletable=False, editable=True, create=False, csv=False)
    
    return dict(candidate=candidate)



@auth.requires_membership('manager')
def dineout():
    db.auth_user.id.readable=True
    db.auth_user.id.writable=False
    db.auth_user.first_name.readable=True
    db.auth_user.first_name.writable=False
    db.auth_user.last_name.readable=True
    db.auth_user.last_name.writable=False
    db.auth_user.email.readable=False
    db.auth_user.email.writable=False
    db.auth_user.password.readable=False
    db.auth_user.password.writable=False

    db.auth_user.vehicle.readable=True
    db.auth_user.vehicle.writable=True
    db.auth_user.available.readable=True
    db.auth_user.available.writable=True
    db.auth_user.recent_count.readable=True
    db.auth_user.recent_count.writable=True
    
    mail = auth.settings.mailer
    mailinfo = str(vars(mail))
    
    #rows
    pool = db((db.auth_user.available == True) & (db.auth_user.recent_count <= 1)).select()   


    #All
    #candidate = SQLFORM.grid(db.auth_user, deletable=False, editable=False, create=False, csv=False)
    
    #Filtered
    candidate = SQLFORM.grid(db((db.auth_user.available == True) & (db.auth_user.recent_count <= 1)), deletable=False, editable=False, create=False, csv=False)
    
    
    selected = random.sample(range(0, len(pool)), len(pool))
    selected_person = list()
    selected_person_id_set = set()
    for i in selected:
        selected_person.append([str(pool[selected[i]].id), pool[selected[i]].first_name, pool[selected[i]].last_name])
        selected_person_id_set.add(str(pool[selected[i]].id))
    form = SQLFORM(db.dineout, fields=['dine_date','dine_location','attendee_id'])
    form.add_button('BACK', URL('ledger', 'default', 'candidate'))

    if form.process().accepted:
        try :
            for i in form.vars.attendee_id: 
                if i in selected_person_id_set:   
                    continue            
                    #db.payment.insert(dineout_id=form.vars.id, user_id=int(i), amount=0)
                else:
                    if i is "":
                        raise Exception("Insert Error (NULL value)")
                    else:
                        raise Exception("Insert Error (invalid person id)")
        except Exception, e:
            response.flash = "Insert Error (%s)" % e.message
            db(db.dineout.id == form.vars.id).delete()
            #db(db.payment.dineout_id == form.vars.id).delete()
        else: 
            db(db.dineout.id == form.vars.id).update(is_active=True, random=str(selected_person))
            result = mail.send(to=['nml.sfu@gmail.com'],
                        subject='Dineout on '+ str(form.vars.dine_date),
                        # If reply_to is omitted, then mail.settings.sender is used
                        reply_to='nml.sfu@gmail.com',
                        message='Test')
            session.flash = 'Accepted. ' + 'mailed? :' + str(result) #+ str(vars(form))
            redirect(URL('ledger','default','index'))
    else:
        response.flash = 'Please fill out the dineout information'

    return locals()

@auth.requires_membership('manager')
def payment():

    dineout = SQLFORM.grid(db(db.dineout.is_active==True), deletable=False, editable=True, create=False, csv=False, onupdate=update_payment)
    return locals()

def update_payment(form):
    response.flash = str(form.vars)
    return



