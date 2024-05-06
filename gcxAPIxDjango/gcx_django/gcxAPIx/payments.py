import os
import json
import base64
import pdfkit
import stripe
import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from pyvirtualdisplay import Display
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .functions import sendEmail
from .factory import getConnection
from .auth import bearer_auth
from gcx_django.gcx_django.settings import STATIC_ROOT
#from flask import Blueprint, Response, request, jsonify, render_template, send_file

################################################################################################
# STRIPE PAYMENTS by Muneeb Ahmed
################################################################################################


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def getSubscriptionStatus(request):
    try:
        content = request.data
        user_id = content['user_id']
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        jsonResponse = {'response': 'Please Provide all parameters.', 'status': "Failed", 'code': "400"}
        return Response(jsonResponse, status.HTTP_206_PARTIAL_CONTENT)
    if user_id:
        conn = getConnection()
        curr = conn.cursor()
        query = "SELECT subscription_status FROM auth_user where id = '%s';" % user_id
        curr.execute(query)
        subStatus = curr.fetchone()
        conn.close()
    else:
        subStatus = 'free_mode'
    return Response({'response': subStatus}, status.HTTP_200_OK)


#==>>+Get+Products+Details+<<==#
@api_view(['GET'])
@bearer_auth
def getProductsDetails(request):
    conn = getConnection()
    curr = conn.cursor()
    query = "SELECT name, description, currency, price, pl.stripe_id, type FROM products as pr INNER JOIN plans as pl ON pr.stripe_id = pl.product_id WHERE pr.active = 'true' AND pl.active = 'true' AND type = 'day';"
    curr.execute(query)
    products = curr.fetchall()
    listOfProducts = []
    for product in products:
        listOfProducts.append({
            'name': product[0],
            'description': product[1],
            'currency': product[2],
            'price': product[3]/100,
            'price_id': product[4],
            'type': product[5]
        })
    conn.close()
    return Response({"response": listOfProducts}, status.HTTP_200_OK)


#==>>+Generate+Payment+Link+<<==#
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def createCheckoutSession(request):
    try:
        content = request.data
        user_id = content['user_id']
        price_id = content['price_id']
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        jsonResponse = {'response': 'Please Provide all parameters.', 'status': "Failed", 'code': "400"}
        return Response(jsonResponse, status.HTTP_206_PARTIAL_CONTENT)
    allowed_users = ["846", "892", "823"]
    if user_id not in allowed_users:
        return Response({"response": 'You are not eligible for premium.', 'status': "Failed", 'code': "401"}, status.HTTP_401_UNAUTHORIZED)
    conn = getConnection()
    curr = conn.cursor()
    # Add the column named 'subscription_status' in the 'auth_user' Table.
    # Change the column name from 'subscription_status' to 'account_status' when deploying as it makes more sense.
    # Update all instances of subscription_status.
    query = "SELECT name FROM products as pr INNER JOIN plans as pl ON pr.stripe_id = pl.product_id WHERE pl.stripe_id = '%s' AND pr.active = 'true' AND pl.active = 'true';" % price_id
    curr.execute(query)
    pName = curr.fetchone()
    if pName:
        pName = pName[0]
    else:
        reply = 'Sorry, this subscription is not able. Please select another one.'
        return Response({'response': reply, 'status': "Failed", 'code': "403"}, status.HTTP_403_FORBIDDEN)
    query = "SELECT cus_id, login_from, email, subscription_status FROM auth_user where id = '%s';" % user_id
    curr.execute(query)
    user_data = curr.fetchone()
    if user_data[3] != 'premium_user':
        #if 'grammarin' == user_data[1]:
        email = user_data[2]
        #else:
        #    email = ''
        cus_id = user_data[0]
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        # Add relevant path to follow when transaction is successful or canceled
        checkout = stripe.checkout.Session.create(
            success_url="https://beta.grammarin.com/success",
            cancel_url="https://beta.grammarin.com/failure",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            client_reference_id=user_id,
            metadata={
                "user_ID": user_id,
                "mail": email,
                "product_Name": pName,
                "price": price_id,
            },
            consent_collection={
                "promotions": 'auto'
            },
            customer=cus_id
        )
        # print('===>>>CHECKOUT+SESSION+COMPLETED<<<===')
        return Response({'url': checkout['url'], 'status':"Success"}, status.HTTP_200_OK)
    else:
        reply = 'User is already subscribed. Please cancel previous subscription before getting new Subscription.'
        return Response({'response': reply, 'status': "Failed", 'code': "403"}, status.HTTP_403_FORBIDDEN)


#==>>+Susbcription+Details<<==#
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def subscriptionDetails(request):
    try:
        content = request.data
        user_id = content['user_id']
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        jsonResponse = {'response': 'Please Provide all parameters.', 'status': "Failed", 'code': "400"}
        return Response(jsonResponse, status.HTTP_206_PARTIAL_CONTENT)
    subs_history = []
    conn = getConnection()
    curr = conn.cursor()
    query = ("SELECT name, description, email, price, currency, type, period_start, period_end, allSub.stripe_id FROM products AS pr INNER JOIN"
             " (SELECT email, price, currency, type, period_start, period_end, user_id, product_id, sub.stripe_id FROM subscriptions AS sub INNER JOIN plans ON sub.plan_id = plans.stripe_id WHERE user_id = '%s')"
             " AS allSub ON pr.stripe_id = allsub.product_id ORDER BY period_start DESC;" % user_id)
    try:
        curr.execute(query)
        subscriptions = curr.fetchall()
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        for val in subscriptions:
            #stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            #sub_detail = stripe.Subscription.retrieve(val[1])
            #price = sub_detail['items']['data'][0]['price']
            #subs_history.append({
            #    'email': val[0],
            #    'price': sub_detail['plan']['amount']/100,
            #    'currency': sub_detail['plan']['currency'],
            #    'type': price['recurring']['interval'] if price['recurring'] else price['type'],
            #    'start': val[2],
            #    'end': val[3]
            #})
            sub_id = val[8]
            subObj = stripe.Subscription.retrieve(sub_id)
            invID = subObj["latest_invoice"]
            invObj = stripe.Invoice.retrieve(invID)
            subs_history.append({
                'name': val[0],
                'description': val[1],
                'email': val[2],
                'price': val[3]/100,
                'currency': val[4],
                'type': val[5],
                'start': val[6],
                'end': val[7],
                'inv_url': invObj["hosted_invoice_url"],
            })
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        return Response({'success': False, 'msg': 'Error while fetching subscription details'}, status.HTTP_422_UNPROCESSABLE_ENTITY)
    finally:
        conn.close()
    return Response({'success': True, 'subscription_history': subs_history}, status.HTTP_200_OK)


#==>>+Billing+History<<==#
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def getBillingHistory(request):
    try:
        content = request.data
        user_id = content['user_id']
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        jsonResponse = {'response': 'Please Provide all parameters.', 'status': "Failed", 'code': "400"}
        return Response(jsonResponse, status.HTTP_206_PARTIAL_CONTENT)
    plan_detail = {}
    billing_history = []
    conn = getConnection()
    curr = conn.cursor()
    query = (("SELECT invoice_number, inv.period_start, name, currency, price, type FROM invoices AS inv "
              "INNER JOIN plans AS pl ON inv.price_id = pl.stripe_id "
              "INNER JOIN subscriptions AS sub ON inv.sub_id = sub.stripe_id "
              "INNER JOIN products AS pr ON inv.prod_id = pr.stripe_id "
              "WHERE user_id = '%s' AND inv.active "
              "ORDER BY period_start DESC;") % user_id)
    try:
        curr.execute(query)
        subscriptions = curr.fetchall()
        #stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        for val in subscriptions:
            billing_history.append({
                'name': val[2],
                'price': val[4]/100,
                'currency': val[3],
                'type': val[5],
                'start': val[1],
                'inv_no': val[0],
            })
        query = (("SELECT name, period_start, period_end FROM subscriptions AS sub "
                  "INNER JOIN plans AS pl ON sub.plan_id = pl.stripe_id "
                  "INNER JOIN products AS pr ON pr.stripe_id = pl.product_id "
                  "WHERE user_id = '%s' AND sub_status = 'complete';") % user_id)
        curr.execute(query)
        row = curr.fetchone()
        if row:
            plan_detail = {
                "name": row[0],
                "start_date": row[1],
                "expiry_data": row[2],
            }
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        return Response({'success': False, 'msg': 'Error while fetching Billing details'}, status.HTTP_422_UNPROCESSABLE_ENTITY)
    finally:
        conn.close()
    return Response({'success': True, 'subscription_history': billing_history, 'plan_details': plan_detail}, status.HTTP_200_OK)


#==>>+Cancel+Susbcription+<<==#
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def cancelSubscription(request):
    try:
        content = request.data
        user_id = content['user_id']
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        jsonResponse = {'response': 'Please Provide all parameters.', 'status': "Failed", 'code': "400"}
        return Response(jsonResponse, status.HTTP_206_PARTIAL_CONTENT)
    conn = getConnection()
    curr = conn.cursor()
    query = "SELECT stripe_id, cus_id FROM subscriptions WHERE user_id = '%s' AND payment_status = 'paid' ORDER BY id DESC;" % user_id
    try:
        curr.execute(query)
        row = curr.fetchone()
        if not (row):
            return Response({'success': False, 'msg': 'User is not Subscribed to any Subscription'}, status.HTTP_403_FORBIDDEN)
        sub_id = row[0]
        #cus_id = row[1]
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        stripe.Subscription.delete(sub_id)
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        return Response({'success': False, 'msg': 'Error in Cancel Subscription'}, status.HTTP_304_NOT_MODIFIED)
    finally:
        conn.close()
    return Response({'success': True, 'msg': 'Subscription has been Canceled'}, status.HTTP_200_OK)

#==>>+Generate+Invoice+PDF+<<==#


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def generate_invoice(request):
    try:
        content = request.data
        inv_no = content['invoice_id']
    except Exception:
        #loglogger.error("Error Happend in execution.", exc_info=1)
        jsonResponse = {'response': 'Please Provide all parameters.', 'status': "Failed", 'code': "400"}
        return Response(jsonResponse, status.HTTP_206_PARTIAL_CONTENT)
    conn = getConnection()
    curr = conn.cursor()
    query = ("SELECT u.email, u.first_name||' '|| u.last_name as user_name, inv.period_start, pr.name, pl.currency, pl.price FROM invoices AS inv "
             "INNER JOIN plans AS pl ON inv.price_id = pl.stripe_id "
             "INNER JOIN subscriptions AS sub ON inv.sub_id = sub.stripe_id "
             "INNER JOIN products AS pr ON inv.prod_id = pr.stripe_id "
             "INNER JOIN auth_user AS u ON u.id = sub.user_id "
             "WHERE inv.invoice_number = '%s' "
             "ORDER BY period_start DESC;" % inv_no)
    try:
        curr.execute(query)
        row = curr.fetchone()
        cdetail = row[0]
        cname = row[1]
        inv_date = row[2].strftime('%Y-%m-%d')
        price = row[5]/100
        items = {
                'name': row[3],
                'qyt': 1,
                'prc': price,
        }
        currency = row[4]
    except Exception:
        return Response({'success': False, 'msg': 'Error in getting invoice data'})
    finally:
        conn.close()
    css = open(f"{STATIC_ROOT}/payments/styles.css", 'r')
    logo = open(f"{STATIC_ROOT}/payments/logo.png", 'rb')
    context = {
        'logo': base64.b64encode(logo.read()).decode("utf-8"),
        'items': items,
        'total_final': price,
        'currency': currency.upper(),
        'invoice_id': inv_no,
        'invoice_date': inv_date,
        'client_name': cname,
        'client_detail': cdetail,
        'company_name': "Content Arcade",
        'company_detail': "Hamad Ben Mohammed St<br>Creative Tower<br>United Arab Emirates<br>+971-56-8927183<br>info@contentarcade.com",
        'footer_note': "ThankYou for purchasing Subscription to Grammarin.com",
        'css': css.read(),
    }
    rendered_Template = render_to_string('invoice.html', context)
    logo.close()
    css.close()
    options = {
        'page-size': 'A4',
        'margin-top': '0.25in',
        'margin-right': '0.25in',
        'margin-bottom': '0.25in',
        'margin-left': '0.25in',
        'encoding': "UTF-8",
        'quiet': '',
        'no-outline': None
    }
    inv_name = '%s.pdf' % inv_no
    display = Display(visible=False, size=(1366, 768))
    display.start()
    pdf_inv = pdfkit.from_string(rendered_Template, options=options)
    response = HttpResponse(pdf_inv, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + inv_name + '"'
    display.stop()
    return response


#==>>+Payment+Confirmation+WebHook+<<==#
# Here we have configured these webhooks events that are called by stripe API
# Following are the eventns handeled by this : checkout.session.completed, invoice.payment_failed and customer.subscription.deleted
@api_view(['POST'])
def ipnConfirm(request):
    event = None
    payload = request.body
    endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET')
    # To skip verification, un comment the two lines below
    #endpoint_secret = None
    #event = request.data
    sig_header = request.headers.get('STRIPE_SIGNATURE')
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    print("BODY\n", payload)
    if endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            print('ValueError==>>\t\t', e)
            # loglogger.error("Error Happend in execution.", exc_info=1)
            return Response({'success': False, 'reason': 'Invalid Format'}, status.HTTP_401_UNAUTHORIZED)
        except stripe.error.SignatureVerificationError as e:
            print('SignatureVerificationError==>>\t', e)
            # loglogger.error("Error Happend in execution.", exc_info=1)
            return Response({'success': False, 'reason': 'Verification Failed'}, status.HTTP_401_UNAUTHORIZED)
    # Handle the event
    # Checkout.Session.Completed
    if event['type'] == 'checkout.session.completed':
        data = event['data']['object']
        if data['payment_status'] == 'paid':
            user_id = data['client_reference_id']
            cus_id = data['customer']
            email = data['customer_details']['email']
            sub_id = data['subscription']
            sub_status = data['status']
            pay_status = data['payment_status']
            country = data['customer_details']['address']['country']
            isLive = data['livemode']
            product_name = data['metadata']['product_Name']
            price_id = data['metadata']['price']
            conn = getConnection()
            curr = conn.cursor()
            try:
                query = (
                    "SELECT subscription_status, email, first_name, last_name from auth_user where id = '%s';" % (user_id))
                curr.execute(query)
                row = curr.fetchone()
                # To prevent duplicate entries into the table.
                if row[0] == 'premium_user':
                    return Response({'success': False, 'reason': 'Duplicate Entry'})
                else:
                    user_email = row[1]
                    fName = row[2]
                    lName = row[3]
                    query = ("INSERT INTO subscriptions (user_id, cus_id, stripe_id, sub_status, payment_status, country, live_mode, email, plan_id) "
                             "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'); "
                             % (user_id, cus_id, sub_id, sub_status, pay_status, country, isLive, email, price_id))
                    curr.execute(query)
                    sub_details = stripe.Subscription.retrieve(sub_id)
                    p_start = datetime.datetime.utcfromtimestamp(
                        sub_details['current_period_start']).strftime('%Y-%m-%d %H:%M:%S')
                    p_end = datetime.datetime.utcfromtimestamp(
                        sub_details['current_period_end']).strftime('%Y-%m-%d %H:%M:%S')
                    query = "UPDATE subscriptions SET period_start= '%s', period_end= '%s' WHERE stripe_id = '%s';" % (
                        p_start, p_end, sub_id)
                    curr.execute(query)
                    query = "UPDATE auth_user SET subscription_status = 'premium_user', cus_id='%s' WHERE id = '%s';" % (
                        cus_id, user_id)
                    curr.execute(query)
                    conn.commit()
                    from_address = 'gcx@grammarin.com'
                    subject = 'GrammarIn - '+product_name+' Subscription'
                    message = '<!DOCTYPE html> <html> <head> <title></title> <style> @import url(\'https://fonts.googleapis.com/css?family=Quicksand:500,600,700&display=swap\');</style> </head> <body><table align="center" style="width:605px;background:#FCD98E;padding:28px;margin:70px 0;" border="0" cellspacing="0" cellpadding="20"><tbody><tr><td align="left" valign="top" style="display:inline-block;background:#fff;text-align:center;box-shadow:0 0 3px 1px #a9a5a5;padding-bottom:0"><img src="https://www.grammarin.com/assets/images/logo.png" style="margin:16px 0"><h6 style="color:#000;font-family: \'Quicksand\', sans-serif;margin:16px 0 0 0;font-size:35px;line-height:40px"> Welcome to GrammarIn </h6><img src="https://www.grammarin.com/assets/images/paymentemail.png" style="margin:16px 0"><p style="font-family: \'Quicksand\', sans-serif;padding: 22px 50px;font-size:18px;margin-top:8px;color:#000"><b>'+fName.capitalize()+' '+lName.capitalize()+'</b><br> Thank you for Subscribing to Grammarin\'s '+product_name+' Subscription! <br> <br> <br></p><a style="font-family: \'Quicksand\', sans-serif;background: linear-gradient(to bottom, #6a6a6a 0%,#404040 100%);border:1px solid #4f4f4f;color:#fff;font-weight:500;padding:10px 35px;border-radius:4px;text-decoration:none;margin-bottom:45px;display:inline-block;font-size:16px;cursor:pointer" href="https://beta.grammarin.com"> Go to GrammarIn</a></td></tr></tbody></table></body> </html>'
                    sendEmail(from_address, user_email, subject, message)
                    sendEmail(from_address, 'muneebahmed.ca@gmail.com', subject, message)
            except Exception:
                #loglogger.error("Error Happend in execution.", exc_info=1)
                conn.rollback()
                return Response({'success': False, 'reason': 'Error updating user status.'})
            finally:
                conn.close()
        else:
            return Response({'success': False, 'reason': 'Payment Status is UNPAID'}, status.HTTP_200_OK)

    # Invoice.Payment_Failed
    elif event['type'] == 'invoice.payment_failed':
        data = event['data']['object']
        sub_id = data['subscription']
        p_end = datetime.datetime.utcfromtimestamp(
            data['period_end']).strftime('%Y-%m-%d %H:%M:%S')
        query = "SELECT user_id, cus_id FROM subscriptions WHERE stripe_id = '%s';" % sub_id
        conn = getConnection()
        curr = conn.cursor()
        try:
            curr.execute(query)
            row = curr.fetchone()
            user_id = row[0]
            cid = row[1]
            query = "UPDATE subscriptions SET payment_status= 'failed', period_end= '%s' WHERE stripe_id = '%s';" % (
                p_end, sub_id)
            curr.execute(query)
            query = "UPDATE auth_user SET subscription_status = 'failed_payment' WHERE id = '%s';" % (
                user_id)
            curr.execute(query)
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            stripe.Subscription.delete(sub_id)
            conn.commit()
            conn.close()
        except Exception:
            #loglogger.error("Error Happend in execution.", exc_info=1)
            conn.rollback()
            conn.close()
            return Response({'success': False, 'reason': 'Update query failed'})

    # Customer.Subscription.Deleted
    elif event['type'] == 'customer.subscription.deleted':
        data = event['data']['object']
        sub_id = data['id']
        query = "SELECT user_id, cus_id FROM subscriptions WHERE stripe_id = '%s';" % sub_id
        conn = getConnection()
        curr = conn.cursor()
        try:
            curr.execute(query)
            row = curr.fetchone()
            user_id = row[0]
            cid = row[1]
        except Exception:
            #loglogger.error("Error Happend in execution.", exc_info=1)
            return Response({'success': False, 'reason': 'No Subscription Exist'})
        end_date = datetime.datetime.utcfromtimestamp(
            data['ended_at']).strftime('%Y-%m-%d %H:%M:%S')
        try:
            query = ("UPDATE subscriptions SET sub_status = 'canceled', canceled_at = '%s', payment_status = 'canceled'"
                     " WHERE stripe_id = '%s';" % (end_date, sub_id))
            curr.execute(query)
            query = "UPDATE auth_user SET subscription_status = 'canceled_sub' WHERE id = '%s';" % (
                user_id)
            curr.execute(query)
            query = ("SELECT email from auth_user where cus_id = '%s'" % cid)
            curr.execute(query)
            row = curr.fetchone()
            user_email = row[0]
            from_address = 'gcx@grammarin.com'
            subject = 'GrammarIn Subscription Canceled!'
            message = '<!DOCTYPE html><html><head><title></title><style>@import url(\'https://fonts.googleapis.com/css?family=Quicksand:500,600,700&display=swap\');</style></head><body><table align="center" style="width:605px;background:#FCD98E;padding:28px;margin:70px 0;" border="0" cellspacing="0" cellpadding="20"><tbody><tr><td align="left" valign="top" style="display:inline-block;background:#fff;text-align:center;box-shadow:0 0 3px 1px #a9a5a5;padding-bottom:0"><img src="https://www.grammarin.com/assets/images/logo.png" style="margin:16px 0"><h6 style="color:#000;font-family: \'Quicksand\', sans-serif;margin:16px 0 0 0;font-size:35px;line-height:40px">Subscription Canceled!</h6><img src="https://www.grammarin.com/assets/images/paymentemail.svg" style="margin:16px 0"><p style="font-family: \'Quicksand\', sans-serif;padding: 22px 50px;font-size:18px;margin-top:8px;color:#000">Dear User, Your subscription to GrammarIN has been canceled.<br><br><br></p><a style="font-family: \'Quicksand\', sans-serif;background: linear-gradient(to bottom, #6a6a6a 0%,#404040 100%);border:1px solid #4f4f4f;color:#fff;font-weight:500;padding:10px 35px;border-radius:4px;text-decoration:none;margin-bottom:45px;display:inline-block;font-size:16px;cursor:pointer" href="https://beta.grammarin.com">Go to GrammarIn</a></td></tr></tbody></table></body></html>'
            sendEmail(from_address, user_email, subject, message)
            conn.commit()
        except Exception:
            #loglogger.error("Error Happend in execution.", exc_info=1)
            conn.rollback()
            return Response({'success': False, 'reason': 'Error updating user data.'})
        finally:
            conn.close()
    elif event['type'] == 'product.created':
        data = event['data']['object']
        id = data['id']
        name = data['name']
        description = data['description']
        active = data['active']
        conn = getConnection()
        curr = conn.cursor()
        query = ("INSERT INTO products(name, description, stripe_id, active) VALUES('%s', '%s', '%s', '%s');"
                 % (name, description, id, active))
        try:
            curr.execute(query)
            conn.commit()
        except Exception:
            conn.rollback()
            #loglogger.error("Error Happend in execution.", exc_info=1)
            return Response({'success': False, 'reason': 'Error inserting Products'})
        finally:
            conn.close()
    elif event['type'] == 'price.created':
        data = event['data']['object']
        id = data['id']
        prod_id = data['product']
        currency = data['currency']
        price = data['unit_amount']
        type = data['recurring']['interval'] if data['recurring'] else data['type']
        active = data['active']
        live_mode = data['livemode']
        conn = getConnection()
        curr = conn.cursor()
        query = ("INSERT INTO plans(stripe_id, product_id, currency, price, type, active, live_mode) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s');"
                 % (id, prod_id, currency, price, type[0], active, live_mode))
        try:
            curr.execute(query)
            conn.commit()
        except Exception:
            conn.rollback()
            #loglogger.error("Error Happend in execution.", exc_info=1)
            return Response({'success': False, 'reason': 'Error inserting Plans'})
        finally:
            conn.close()
    elif event['type'] == 'invoice.payment_succeeded':
        data = event['data']['object']
        id = data['id']
        bill = data["billing_reason"]
        cus_id = data["customer"]
        period = data["lines"]["data"][0]["period"]
        sub_ID = data["subscription"]
        prod_ID = data["lines"]["data"][0]["plan"]["product"]
        price_ID = data["lines"]["data"][0]["plan"]["id"]
        inv_num = data['number']
        p_start = datetime.datetime.utcfromtimestamp(
            period['start']).strftime('%Y-%m-%d %H:%M:%S')
        p_end = datetime.datetime.utcfromtimestamp(
            period['end']).strftime('%Y-%m-%d %H:%M:%S')
        conn = getConnection()
        curr = conn.cursor()
        query = ("INSERT INTO invoices(stripe_id, reason, cus_id, period_start, period_end, sub_id, prod_id, price_id, invoice_number) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"
                 % (id, bill, cus_id, p_start, p_end, sub_ID, prod_ID, price_ID, inv_num))
        try:
            curr.execute(query)
            if bill == "subscription_cycle":
                query = ("UPDATE subscriptions SET period_end = '%s'"
                         " WHERE stripe_id = '%s';" % (p_end, sub_ID))
                curr.execute(query)
                query = (
                    "SELECT email from auth_user where cus_id = '%s'" % cus_id)
                curr.execute(query)
                row = curr.fetchone()
                user_email = row[0]
                from_address = 'gcx@grammarin.com'
                subject = 'GrammarIn Subscription Renewed!'
                message = '<!DOCTYPE html> <html> <head> <title></title> <style> @import url(\'https://fonts.googleapis.com/css?family=Quicksand:500,600,700&display=swap\');</style> </head> <body><table align="center" style="width:605px;background:#FCD98E;padding:28px;margin:70px 0;" border="0" cellspacing="0" cellpadding="20"><tbody><tr><td align="left" valign="top" style="display:inline-block;background:#fff;text-align:center;box-shadow:0 0 3px 1px #a9a5a5;padding-bottom:0"><img src="https://www.grammarin.com/assets/images/logo.png" style="margin:16px 0"><h6 style="color:#000;font-family: \'Quicksand\', sans-serif;margin:16px 0 0 0;font-size:35px;line-height:40px"> Welcome to GrammarIn </h6><img src="https://www.grammarin.com/assets/images/paymentemail.png" style="margin:16px 0"><p style="font-family: \'Quicksand\', sans-serif;padding: 22px 50px;font-size:18px;margin-top:8px;color:#000"> Your subscription to GrammaIn has been renewed! <br><br><br></p><a style="font-family: \'Quicksand\', sans-serif;background: linear-gradient(to bottom, #6a6a6a 0%,#404040 100%);border:1px solid #4f4f4f;color:#fff;font-weight:500;padding:10px 35px;border-radius:4px;text-decoration:none;margin-bottom:45px;display:inline-block;font-size:16px;cursor:pointer" href="https://beta.grammarin.com"> Go to GrammarIn</a></td></tr></tbody></table></body> </html>'
                sendEmail(from_address, user_email, subject, message)
                sendEmail(from_address, 'muneebahmed.ca@gmail.com', subject, message)
            conn.commit()
        except Exception:
            conn.rollback()
            #loglogger.error("Error Happend in execution.", exc_info=1)
            return Response({'success': False, 'reason': 'Error inserting into invoice or updating subscription'})
        finally:
            conn.close()
    else:
        #loglogger.info('Unexpected event type : ' + event['type'])
        return Response({'success': False, 'reason': 'Unhandled event type {}'.format(event['type'])})
    #print("=======>>> ", event['type'], " <<<>>> Completed",  " <<<=======")
    # print("======================>>>>>>>>>>>>DONE<<<<<<<<<<<======================")
    return Response({'success': True, 'reason': 'Webhook Executed Accordingly'}, status.HTTP_200_OK)
################################################################################################
