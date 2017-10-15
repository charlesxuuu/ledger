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

admin_id = 1

@auth.requires_login()
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

    crew = SQLFORM.grid(db(db.auth_user.id != admin_id), deletable=False, editable=False, create=False, csv=False)
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
    admin = db(db.auth_user.id == admin_id).select()
    #Assume there is only one record
    cost = -1 * admin[0].balance
    grid = SQLFORM.smartgrid(db.auth_user)
    return dict(grid=grid, cost=cost)



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
            
            #send email
            email_list = ['nml.sfu@gmail.com', 'chix@sfu.ca']
            content = 'Hi All, \n\n\nPlease join the dineout on ' + str(form.vars.dine_date) + '.\n\n'

            for i in form.vars.attendee_id:
                attendee = db(db.auth_user.id == int(i)).select()
                #assume there is only one row, attendee -> attendee[0]
                email_list.append(attendee[0].email)
                content = content + attendee[0].first_name + ' ' + attendee[0].last_name + '\tBalance: ' + str(attendee[0].balance) + '\n'
            content = content + ' \n\n\nBest,\nSFU NetMedia Lab'

            #result = mail.send(to=email_list,
            #            subject='Dineout on '+ str(form.vars.dine_date),
            #            # If reply_to is omitted, then mail.settings.sender is used
            #            reply_to='nml.sfu@gmail.com',
            #            message=content)

            session.flash = 'Accepted. ' #+ 'mailed? :' + str(result)
            redirect(URL('ledger','default','index'))
    else:
        response.flash = 'Please fill out the dineout information'

    return locals()

@auth.requires_login()
def history():
    dineout = SQLFORM.grid(db.dineout, deletable=False, editable=False, create=False, csv=False)
    return locals()

@auth.requires_membership('manager')
def payment():
    db.dineout.is_active.readable==False
    #db.dineout.is_active.writable==False
    dineout = SQLFORM.grid(db(db.dineout.is_active==True), deletable=False, editable=True, create=False, csv=False, onvalidation=validate_payment, onupdate=update_payment)
    return locals()

def validate_payment(form):
    if form.vars.amount < 0:
        form.errors.amount = 'Amount cannot be negative'
    if form.vars.amount is None:
        form.errors.amount = 'Please insert amount'


def update_payment(form):
    #<Storage {'dine_date': datetime.date(2017, 10, 12), 
    #'random': "[['5', 'Xiaoqiang', 'Ma'], ['4', 'Yuchi', 'Chen'], ['3', 'Xiaoyi', 'Fan'], ['9', 'Fagnxin', 'Wang'], ['7', 'Jihong', 'Yu'], ['8', 'Lei', 'Zhang'], ['6', 'Siyu', 'Wu']]", 
    #'is_active': True, 'dine_location': '\xe9\xab\x98\xe4\xbd\xb0', 
    #'payer_id': 2, 'attendee_id': ['6', '9', '7', '4'], 
    #'amount': 20.0, 'id': 22L}>

    share_cost = round(form.vars.amount * 0.4 / len(form.vars.attendee_id), 2)
    lab_cost = form.vars.amount - share_cost * len(form.vars.attendee_id)
    non_payer_update = -1 * share_cost
    payer_update = form.vars.amount - share_cost

    for i in form.vars.attendee_id:     
        if int(i) is not form.vars.payer_id:
            db.payment.insert(dineout_id=form.vars.id, user_id=int(i), amount=non_payer_update)
            db(db.auth_user.id == int(i)).update(balance=db.auth_user.balance+non_payer_update, recent_count=db.auth_user.recent_count+1, total_count=db.auth_user.total_count+1)
        else:
            db.payment.insert(dineout_id=form.vars.id, user_id=int(i), amount=payer_update)
            db(db.auth_user.id == int(i)).update(balance=db.auth_user.balance+payer_update, recent_count=db.auth_user.recent_count+1, total_count=db.auth_user.total_count+1)
    rows = db(db.auth_user).select()
    for row in rows:
        if str(row.id) not in form.vars.attendee_id:
            db(db.auth_user.id == row.id).update(recent_count=0)
            #print row.id
    #db( ~(str(db.auth_user.id) in form.vars.attendee_id)).update(recent_count=0)
    db(db.auth_user.id == admin_id).update(balance=db.auth_user.balance - form.vars.amount * 0.6)
    db(db.dineout.id == form.vars.id).update(is_active=False)

    #send email
    email_list = ['nml.sfu@gmail.com', 'chix@sfu.ca']
    content = 'Hi All, \n\n\nThe payment information of the dineout on ' + str(form.vars.dine_date) + ' has been updated.\n\n'

    payer = db(db.auth_user.id == form.vars.payer_id).select()
    content = content + 'The payer is ' + payer[0].first_name + ' ' + payer[0].last_name + '.\n' 
    content = content + 'The amount is ' + str(form.vars.amount) + '.\n\n'

    for i in form.vars.attendee_id:
        attendee = db(db.auth_user.id == int(i)).select()
        #assume there is only one row, attendee -> attendee[0]
        email_list.append(attendee[0].email)
        content = content + attendee[0].first_name + ' ' + attendee[0].last_name + '\tBalance: ' + str(attendee[0].balance) + '\n'
    content = content + ' \n\n\nBest,\nSFU NetMedia Lab'

    #result = mail.send(to=email_list,
    #            subject='Dineout on '+ str(form.vars.dine_date),
    #            # If reply_to is omitted, then mail.settings.sender is used
    #            reply_to='nml.sfu@gmail.com',
    #            message=content)


    session.flash = 'Accpeted.' #+ 'mailed? :' + str(result)
    redirect(URL('ledger','default','index'))
    return



