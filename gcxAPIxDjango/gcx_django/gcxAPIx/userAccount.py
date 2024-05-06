import json
import numpy as np
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .auth import bearer_auth
from .factory import getConnection
from .functions import initializeFilters
from .functions import sendEmail
from .models import User

@api_view(['GET', 'POST'])
def accountConfirm(request):
    """Get data returned from the server."""
    if 'conf_code' in request.data:
        conf_code = request.data['conf_code']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    conn = getConnection()
    cur = conn.cursor()
    cur. execute(
        "SELECT id FROM auth_user WHERE conf_code = '%s' """ % conf_code)
    result = cur.fetchall()
    response = ''
    code = ''
    if len(result) > 0:
        cur. execute(
            "SELECT id FROM auth_user WHERE active = 'FALSE' AND conf_code = '%s' """ % conf_code)
        result2 = cur.fetchall()
        if len(result2) > 0:
            try:
                cur.execute(
                    "UPDATE auth_user SET active = 'TRUE' WHERE conf_code = '%s' """ % conf_code)
                conn.commit()
            except Exception:
                # loglogger.error("Error Happend in execution.", exc_info=1)
                conn.rollback()
                json_response = 'Account Activation failed'
                return Response(json_response, status=400)
            finally:
                conn.close()
            code = 200
            response = dict()
            response['confirmation'] = 1
            response['confirmation_message'] = 'Account Activated Successfully, Please Sign In to Continue'
            initializeFilters(result2[0][0], 'account', status='aftersignup')
        else:
            code = 200
            response = dict()
            response['Already_confirmed'] = 1
            response['Already_confirmed_message'] = 'You already have confirmed your account'
    else:
        code = 200
        response = dict()
        response['Ivalid_code'] = 1
        response['Invalid_Code_message'] = 'Sorry Invalid Confirmation Code'
    conn.close()
    return Response({'response': response, 'code': code}, status.HTTP_200_OK)
################################################################################################
#---#------------------------------------------------------------------------------------------#
#--- ACCOUNT DE-ACTIVATION SECTION #
#----------------------------------------------------------------------------------------------#
#   Language :  Form Save & Resend Frsh Data   (US / UK)
################################################################################################


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def deleteUserByProfileID(request):
    """ Language """
    if 'profile_id' in request.data:
        user_id = request.data['profile_id']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    conn = getConnection()
    cur = conn.cursor()
    # NOW UPDATE IN THE USER-META TABLE AGAINST USER-ID,
    try:
        cur.execute(
            """UPDATE auth_user SET active = 'FALSE' WHERE id=%s """ % user_id)
        conn.commit()
        cur. execute("""SELECT active FROM auth_user WHERE id=%s """ % user_id)
        rows = cur.fetchall()
    except Exception:
        # loglogger.error("Error Happend in execution.", exc_info=1)
        conn.rollback()
        json_response = 'Account deletion failed'
        return Response(json_response, status=400)
    finally:
        conn.close()
    # AND SELECT AGAIN DATA FROM THE DATABASE AND RETURN TO THE USER
    data = {'deleteUserByProfileID': '1', 'contents': rows[0][0]}
    #json_response = json.dumps(data)
    return Response(data, status=200)

################################################################################################
#---#------------------------------------------------------------------------------------------#
#--- FORGOT PASSWORD SECTION #
#----------------------------------------------------------------------------------------------#
################################################################################################


@api_view(['POST'])
@bearer_auth
def resetPassword(request):
    if 'fp_email' in request.data:
        fp_email = request.data['fp_email']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    # loglogger.info("User %s called resetPassword." % fp_email)
    conn = getConnection()
    cur = conn.cursor()
    while True:
        # Here we're generating a string key to send, when user press on reset password button to reset password.
        chars = np.array(
            list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
        np_Code = np.random.choice(chars, 20)
        reset_password_code = ''.join([val for val in np_Code])
        # print(reset_password_code)
        cur. execute(
            "SELECT id FROM auth_user WHERE reset_password_code = '%s' """ % reset_password_code)
        result = cur.fetchall()
        if len(result) > 0:
            # If record found in database, while loop will run again until the unique key is generated.
            continue
        else:
            # If record not found in database loop will break and run next of the statements.
            break
    cur. execute(
        """SELECT id, login_from FROM auth_user WHERE LOWER(email) = LOWER('%s'); """ % fp_email)
    result = cur.fetchall()
    if len(result) > 0:
        if result[0][1] == "grammarin":
            user_id = result[0][0]
            try:
                cur.execute("""UPDATE auth_user SET reset_password_code='%s' WHERE id =%s """ % (
                    reset_password_code, user_id))
                conn.commit()
            except Exception:
                # loglogger.error("Error Happend in execution.", exc_info=1)
                conn.rollback()
                json_response = 'Reseting Password failed'
                conn.close()
                return Response(json_response, status=400)
            from_address = 'esubmit@grammarin.com'
            subject = 'GrammarIn - Reset Password Email'
            #message = "Your New Password is 12345, You can change this in the Account section later."
            #message = 'Hi <b>' + fp_email.capitalize() + '</b><br>You recently requested to reset your password for your GrammarIn account. Tap the button below to reset your password.</br><br> This password reset request is valid only for the next 24 hours.<br> <a href="https://www.grammarin.com/resetpassword/'+ reset_password_code +'"><button>Tap here to reset your password</button></a>'
            message = '<!DOCTYPE html><html><head><title></title><style>@import url(\'https://fonts.googleapis.com/css?family=Quicksand:500,600,700&display=swap\');body {font-family: Quicksand, sans-serif;}.full-view {display: flex;justify-content: center}.banner-outer {position:relative;width:605px;background:#FCD98E;padding:28px;margin:70px 0;}.logo {margin: 36px 0}.lock-banner img{margin: 30px 0 48px;width: 210px;}.banner-inner {width: 100%;display: inline-block;background: #fff;height: 100%;text-align: center;box-shadow: 0 0 3px 1px #A9A5A5}.banner-inner p {font-size: 15px;font-weight:600;margin:0;text-align:justify;}.banner-inner span {font-size: 17px;font-weight: 600;padding-top: 18px;float: left;width: 100%;}.banner-inner a {background: linear-gradient(to bottom, #6A6A6A 0%,#404040 100%);border:1px solid #4F4F4F;color: #fff;font-weight: 700;padding: 10px 35px;border-radius:4px;text-decoration:none;margin:45px 0;display:inline-block;font-size:18px}.banner-bottom{background: #F4F4F4;padding: 30px;margin: 0 48px 48px;}h3 {margin:0;font-size: 28px}</style></head><body><div class="full-view"><div class="banner-outer"><div class="banner-inner"><div class="logo"><img src="https://www.grammarin.com/assets/images/logo.png"></div><div class="lock-banner"><img src="https://www.grammarin.com/assets/images/lock-banner.png"></div><h3>Forgot <br> Your Passcode?</h3><span>Not to worry, we got  you! Let’s get you a new password.</span><a href="https://www.grammarin.com/resetpassword/' + reset_password_code + '"> Reset Password</a></div></div></div></body> </html>'
            sendEmail(from_address, fp_email, subject, message)
            data = {'updateUserPassword': '1', 'contents': '1', 'message': 'Reset Email sent'}
        elif result[0][1] == "google":
            data = {'updateUserPassword': '1', 'contents': '-2', 'message': 'Loged in using google'}
        elif result[0][1] == "facebook":
            data = {'updateUserPassword': '1', 'contents': '-3', 'message': 'Loged in using facebook'}
    else:
        data = {'updateUserPassword': '1', 'contents': '-1', 'message': 'Email not found'}
    conn.close()
    #json_response = json.dumps(data, indent=4, sort_keys=True, default=str)
    return Response(data, status=200)
################################################################################################
# ADDED BY HASEEB
# USER RESET PASSWORD THROUGH EMAIL
################################################################################################


@api_view(['GET', 'POST'])
#@bearer_auth
def updateUserForgotPassword(request):
    """ Account """
    if 'reset_password_code' in request.data and 'new_password' in request.data:
        reset_password_code = request.data['reset_password_code']
        new_password = request.data['new_password']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    conn = getConnection()
    cur = conn.cursor()
    cur. execute(
        "SELECT id FROM auth_user WHERE reset_password_code = '%s' """ % reset_password_code)
    result = cur.fetchall()
    response = dict()
    code = '200'
    if len(result) > 0:
        cur. execute(
            """SELECT temp_password FROM auth_user WHERE reset_password_code = '%s' """ % reset_password_code)
        rows = cur.fetchall()
        old_temp_password = rows[0][0]
        if new_password != old_temp_password:
            try:
                ussr = User.objects.get(reset_password_code=reset_password_code)
                ussr.set_password(new_password)
                ussr.temp_password = new_password
                ussr.reset_password_code = None
                ussr.save()
                #cur.execute("UPDATE auth_user SET temp_password = '%s' WHERE reset_password_code = '%s' """ % (
                #    new_password, reset_password_code))
                #cur.execute(
                #    """UPDATE auth_user SET reset_password_code='NULL' WHERE password = '%s'  """ % new_password)
                #conn.commit()
            except Exception:
                # loglogger.error("Error Happend in execution.", exc_info=1)
                conn.rollback()
                json_response = 'Updating user forgot password failed'
                conn.close()
                return Response(json_response, status=400)
            response['updated_password'] = 1
            response['updated_password_message'] = 'Your password has been updated successfully. Please sign in to your account'
        else:
            response['old_password'] = 1
            response['old_password_message'] = 'You have entered an old password. Please try another one'
    else:
        response['Ivalid_code'] = 1
        response['Invalid_confirmation_code_message'] = 'Record does not exist'
    conn.close()
    return Response({'response': response, 'code': code}, status.HTTP_200_OK)
#---#------------------------------------------------------------------------------------------#
#--- CHANGE PASSWORD SECTION #
#----------------------------------------------------------------------------------------------#
# ADDED BY HASEEB
# CHANGE PASSWORD
################################################################################################
#   Account :    Form Save & Resend Frsh Data (Change Password)
################################################################################################


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def updateUserPassword(request):
    """ Account """
    conn = getConnection()
    cur = conn.cursor()
    content = request.data
    if 'user_id' in content and 'section' in content and 'current_password' in content and 'new_password1' in content:
        user_id = content['user_id']
        section = content['section']
        current_password = content['current_password']
        new_password1 = content['new_password1']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    data = {}
    if section == "update_password":
        ussr = User.objects.get(id=user_id)
        if ussr.check_password(current_password):
            if ussr.check_password(new_password1):
                data = {
                    'updateUserPassword': '1',
                    'password_update_message': 'You have entered an old password. Please try another one.',
                    'contents': '1'
                }
            else:
                try:
                    ussr.set_password(new_password1)
                    ussr.temp_password = new_password1
                    ussr.save()
                    data = {
                        'updateUserPassword': '1',
                        'password_update_message': 'Your password has been changed successfully!',
                        'contents': '-1'
                    }
                except Exception:
                    # loglogger.error("Error Happend in execution.", exc_info=1)
                    conn.rollback()
                    json_response = 'Update User Password failed'
                    conn.close()
                    return Response(json_response, status=400)
        else:
            data = {
                'updateUserPassword': '1',
                'password_update_message': 'You have entered a wrong password. Please try another one.',
                'contents': '-1'
            }
    return Response(data, status.HTTP_200_OK)
################################################################################################
#   Profile :   Form Save & Resend Frsh Data   (Block Keywords)
################################################################################################


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def updateProfileContents(request):
    """ Profile """
    conn = getConnection()
    cur = conn.cursor()
    if 'profile_id' in request.data and 'firstname' in request.data and 'lastname' in request.data:
        profile_id = request.data['profile_id']
        firstname = request.data['firstname']
        lastname = request.data['lastname']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    # NOW UPDATE IN THE USER-META TABLE AGAINST USER-ID,
    try:
        cur.execute("""UPDATE auth_user SET first_name = %s, last_name = %s WHERE id =%s """,
                    (firstname, lastname, profile_id))
        conn.commit()
    except Exception:
        # loglogger.error("Error Happend in execution.", exc_info=1)
        conn.rollback()
        json_response = 'Updating profile contents failed'
        conn.close()
        return Response(json_response, status=400)
    # AND SELECT AGAIN DATA FROM THE DATABASE AND RETURN TO THE USER
    cur.execute(
        """SELECT first_name, last_name FROM auth_user WHERE id = %s """ % profile_id)
    rows = cur.fetchall()
    updated_first_name = rows[0][0]
    updated_last_name = rows[0][1]
    if firstname == updated_first_name and lastname == updated_last_name:
        data = {'updateProfile': '1', 'contents': '1'}
    else:
        data = {'updateProfile': '1', 'contents': '0'}
    conn.close()
    #json_response = json.dumps(data)
    return Response(data, status=200)
################################################################################################

#---#------------------------------------------------------------------------------------------#
#--- AMERICAN/BRITISH LANGUAGE SECTION #
#----------------------------------------------------------------------------------------------#
#   Language :  Form Save & Resend Frsh Data   (US / UK)


@api_view(['GET', 'POST'])
# @permission_classes([permissions.IsAuthenticated])
@bearer_auth
def updateUserLanguage(request):
    """ Language """
    if 'profile_id' in request.data and 'pref_language' in request.data:
        user_id = request.data['profile_id']
        pref_language = request.data['pref_language']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)

    conn = getConnection()
    cur = conn.cursor()
    # NOW UPDATE IN THE USER-META TABLE AGAINST USER-ID,
    try:
        cur.execute("""UPDATE user_meta SET meta_value=%s WHERE meta_name = 'preferred_language' AND user_id=%s """,
                    (pref_language, user_id))
        conn.commit()
    except Exception:
        # loglogger.error("Error Happend in execution.", exc_info=1)
        conn.rollback()
        json_response = 'Language update failed'
        conn.close()
        return Response(json_response, status=400)
    # AND SELECT AGAIN DATA FROM THE DATABASE AND RETURN TO THE USER
    cur. execute(
        """SELECT meta_value FROM user_meta WHERE meta_name = 'preferred_language' AND user_id=%s """ % user_id)
    rows = cur.fetchall()
    if len(rows) <= 0:
        data = {'updateUserLanguage': '1', 'contents': 'us'}
    else:
        data = {'updateUserLanguage': '1', 'contents': rows[0][0]}
    conn.close()
    #json_response = json.dumps(data)
    return Response(data, status=200)

################################################################################################


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def updateuserfiltersAccount(request):
    content = request.data
    if 'user_id' in content and 'filters' in content:
        user_id = content['user_id']
        docURL = "account"
        filters = content['filters']
    else:
        # loglogger.error("Error Happend in execution.", exc_info=1)
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    conn = getConnection()
    curr = conn.cursor()
    try:
        query = ("UPDATE user_filters set filters='%s' WHERE user_id = '%s' AND doc_id = '%s' RETURNING filters;") % (
            json.dumps(filters), user_id, docURL)
        curr.execute(query)
        results = curr.fetchone()
        conn.commit()
    except Exception:
        conn.rollback()
        # loglogger.error("Error Happend in execution.", exc_info=1)
        return Response({'response': 'Unable to update filters', 'status': "Failed"}, status.HTTP_200_OK)
    finally:
        conn.close()
    return Response({'msg': 'Filters Updated', 'resp_code': 200, 'filters': results[0]}, status.HTTP_200_OK)
################################################################################################


@api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
@bearer_auth
def updateuserfilters(request):
    content = request.data
    if 'user_id' in content and 'doc_url' in content and 'filters' in content:
        user_id = content['user_id']
        docURL = content['doc_url']
        filters = content['filters']
    else:
        # loglogger.error("Error Happend in execution.", exc_info=1)
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    conn = getConnection()
    curr = conn.cursor()
    try:
        query = ("UPDATE user_filters set filters='%s' WHERE user_id = '%s' AND doc_id = '%s' RETURNING filters;") % (
            json.dumps(filters), user_id, docURL)
        curr.execute(query)
        results = curr.fetchone()
        conn.commit()
    except Exception:
        conn.rollback()
        # loglogger.error("Error Happend in execution.", exc_info=1)
        return Response({'response': 'Unable to update filters', 'status': "Failed"}, status.HTTP_200_OK)
    finally:
        conn.close()
    return Response({'msg': 'Filters Updated', 'resp_code': 200, 'filters': results[0]}, status.HTTP_200_OK)
################################################################################################


@api_view(['POST'])
#@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def submitEForm(request):
    """Get data returned from the server."""
    if 'form_name' in request.data and 'form_email' in request.data and 'form_subject' in request.data and 'form_message' in request.data:
        form_name = request.data['form_name']
        form_email = request.data['form_email']
        form_subject = request.data['form_subject']
        form_message = request.data['form_message']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    ##################################################
    from_address = 'esubmit@grammarin.com'
    to_address = 'aliraja.fsd@gmail.com'
    subject = 'GrammarIn - Email'
    message = "From Name: '%s', From Email: '%s', Subject: '%s', Message:  '%s'" % (form_name, form_email, form_subject, form_message)
    output = sendEmail(from_address, to_address, subject, message)
    ##################################################
    #json_response = json.dumps(output, indent=4, sort_keys=True, default=str)
    return Response(output, status.HTTP_200_OK)
################################################################################################


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def submitSupportForm(request):
    conn = getConnection()
    cur = conn.cursor()
    """Get data returned from the server."""
    if 'profile_id' in request.data and 'doc_id' in request.data and 'version' in request.data and 'form_subject' in request.data and 'form_message':
        profile_id = request.data['profile_id']
        doc_id = request.data['doc_id']
        version = request.data['version']
        form_subject = request.data['form_subject']
        form_message = request.data['form_message']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    ##################################################
    from_address = 'esubmit@grammarin.com'
    to_address = 'aliraja.fsd@gmail.com'
    subject = 'GrammarIn - Support Email'
    message = "<b>Profile: '%s', DocID: '%s', Subject: '%s', Message:  '%s'</b>" % (
        profile_id, doc_id, form_subject, form_message)
    output = sendEmail(from_address, to_address, subject, message)
    ##################################################
    sql = "INSERT INTO support_form(user_id, version, form_subject, form_message) VALUES(%s, %s, %s, %s)"
    try:
        cur.execute(sql, (profile_id, version, form_subject, form_message))
        conn.commit()
    except Exception:
        # loglogger.error("Error Happend in execution.", exc_info=1)
        conn.rollback()
        json_response = 'Form submission failed'
        return Response(json_response, status=400)
    finally:
        conn.close()
    #json_response = json.dumps(output, indent=4, sort_keys=True, default=str)
    return Response(output, status.HTTP_200_OK)
    ##################################################
