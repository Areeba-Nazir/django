import time
import datetime
import numpy as np
from django.contrib.auth import logout
#from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .auth import bearer_auth
from .factory import getConnection
from .functions import sendEmail, initializeFilters
from .models import User


@api_view(['GET', 'POST'])
def testing(request):
    data = request.json
    print("BluePrint active and Responding...")
    data = {'Yeh lo data': data}
    return Response(data, status=200)


################################################################################################
#   ADDED BY HASEEB
################################################################################################


@api_view(['POST'])
@bearer_auth
def signupFormProcesses(request):
    """View function for signup view."""
    if 'firstname' in request.data and 'lastname' in request.data and 'email' in request.data and 'password' in request.data:
        firstname = request.data['firstname']
        lastname = request.data['lastname']
        email = request.data['email']
        password = request.data['password']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    # FIRST WE WILL VERIFY IF THE USER ALREADY THERE, IF YES, THEN JUST LOG HIM IN.
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        """SELECT active, login_from, login_count FROM auth_user WHERE email = LOWER('%s') """ % email)
    result = cur.fetchall()
    if len(result) > 0:
        active = result[0][0]
        login_from = result[0][1]
        login_count = result[0][2]
        if not (bool(active)) and login_count is None:
            #code = 401  # Unauthorized
            code = status.HTTP_409_CONFLICT  # Unauthorized
            response = dict()
            data = {
                'signup': '0', 'signup_message': 'Please verify your account first.', 'user_id': 0}
            response['errors'] = data
        elif bool(active) and login_count is None:
            #code = 401
            code = status.HTTP_405_METHOD_NOT_ALLOWED
            response = dict()
            data = {
                'signup': '0', 'signup_message': 'You have verified your account. Please log in to use your account',
                'user_id': 0}
            response['errors'] = data
        elif login_from == 'facebook' or login_from == 'google':
            #code = 401
            code = status.HTTP_409_CONFLICT
            response = dict()
            data = {
                'signup': '0',
                'signup_message': 'Sorry! this account already exists. Please log in from your social account',
                'user_id': 0}
            response['errors'] = data
        else:
            code = 400
            # code = status.HTTP_409_CONFLICT
            response = dict()
            data = {
                'signup': '0', 'signup_message': 'Sorry! this account already exists.', 'user_id': 0}
            response['errors'] = data
    else:
        active = False
        ts = time.time()
        doc = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        # cipher_password = encrypt(encdcr_key, password)
        # plain_password = decrypt(encdcr_key, cipher_password)
        cipher_password = password
        while True:
            # Here we're generating a string key to send it, when user press on confirm email button to confirm account on signup.
            chars = np.array(
                list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
            np_Code = np.random.choice(chars, 20)
            conf_code = ''.join([val for val in np_Code])
            cur.execute(
                "SELECT id FROM auth_user WHERE conf_code = '%s' """ % conf_code)
            result = cur.fetchall()
            if len(result) > 0:
                # If record found in database, while loop will run again until the unique key is generated.
                continue
            else:
                # If record not found in database loop will break and run next of the statements.
                break
        ############# ADD CODE HERE #############
        try:
            new_user = User.objects.create_user(
                username=email,
                email=email,
                password=cipher_password,
                first_name=firstname,
                last_name=lastname,
                active=active,
                created_at=doc,
                login_from='grammarin',
                conf_code=conf_code,
                temp_password=password
            )
            user_id = new_user.id
            cur.execute("INSERT INTO user_meta(user_id, meta_name, meta_value) VALUES(%s, %s, %s) RETURNING id;",
                        (user_id, 'preferred_language', 'us'))
            code = 200
            response = dict()
            response['signup'] = 1
            response['signup_message'] = 'Account Created Successfully, Please Sign In to Continue'
            response['user_id'] = user_id
            from_address = 'gcx@grammarin.com'
            subject = 'GrammarIn - Account Activation Email'
            message = '<!DOCTYPE html> <html> <head> <title></title> <style> @import url(\'https://fonts.googleapis.com/css?family=Quicksand:500,600,700&display=swap\');</style> </head> <body><table align="center" style="width:605px;background:#FCD98E;padding:28px;margin:70px 0;" border="0" cellspacing="0" cellpadding="20"><tbody><tr><td align="left" valign="top" style="display:inline-block;background:#fff;text-align:center;box-shadow:0 0 3px 1px #a9a5a5;padding-bottom:0"><img src="https://www.grammarin.com/assets/images/logo.png" style="margin:16px 0"><h1 style="color:#000;font-family: \'Quicksand\', sans-serif;margin:16px 0 0 0;font-size:45px;line-height:54px"> Welcome </h1><h3 style="margin:0;font-size:22px;color:#000;font-family: \'Quicksand\', sans-serif;">to GrammarIn</h3><p style="font-family: \'Quicksand\', sans-serif;padding: 22px 50px;font-size:18px;margin-top:8px;color:#000"> Hi <b>' + firstname.capitalize() + '</b><br> Thank you for creating a Grammarin account.<br> To confirm your email address, please click on the following button and sign in to your account.<br> Thank you for choosing Grammarin!<br></p><a style="font-family: \'Quicksand\', sans-serif;background: linear-gradient(to bottom, #6a6a6a 0%,#404040 100%);border:1px solid #4f4f4f;color:#fff;font-weight:500;padding:10px 35px;border-radius:4px;text-decoration:none;margin-bottom:45px;display:inline-block;font-size:16px;cursor:pointer" href="https://www.grammarin.com/accountConfirm/' + conf_code + '">Confirm E-Mail</a></td></tr></tbody></table></body> </html>'
            sendEmail(from_address, email, subject, message)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
            error_response = {'response': 'Account creation failed', 'status': 'Failed'}
            return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
            # loglogger.error("Error Happend in execution.", exc_info=1)
    conn.close()
    return Response(response, status=code)


class userLogin(ObtainAuthToken):

    @method_decorator(bearer_auth)
    def post(self, request, *args, **kwargs):
        # return Response("Bas kr bhai")
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user.active:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "response": {
                        'Login-Token': token.key,
                        'id': user.pk,
                        'email': user.email,
                    },
                    "meta": {
                        "code": 200
                    }
                })
            else:
                return Response({'messsage': 'Please verify your account first.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            email = request.data['username']
            checkUser = User.objects.filter(email=email)
            if checkUser:
                if checkUser[0].login_from in ['facebook', 'google']:
                    return Response(
                        {'messsage': 'Please login from your social login account.'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                else:
                    return Response({'message': 'Wrong email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'message': 'User does not exist, please sign up.'},
                                status=status.HTTP_401_UNAUTHORIZED)


################################################################################################
# Added by Haseeb = TESTED FUNCTIONALITY
################################################################################################

class GoogleLogin(ObtainAuthToken):

    @method_decorator(bearer_auth)
    def post(self, request, *args, **kwargs):
        if 'firstname' in request.data and 'lastname' in request.data and 'email' in request.data:
            # firstname_base64_decoded = base64.b64decode(request.data['firstname'])
            # firstname = firstname_base64_decoded.decode('UTF-8')
            firstname = request.data['firstname']
            # lastname_base64_decoded = base64.b64decode(request.data['lastname'])
            # lastname = lastname_base64_decoded.decode('UTF-8')
            lastname = request.data['lastname']
            # email_base64_decoded = base64.b64decode(request.data['email'])
            # email = email_base64_decoded.decode('UTF-8')
            email = request.data['email']
            password = '123455678'
        else:
            error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
            return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
        # return Response("Bas kr bhai")
        data = {
            "username": email,
            "password": password,
        }
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user.active:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "response": {
                        'Login-Token': token.key,
                        'id': user.pk,
                        'email': user.email,
                    },
                    "meta": {
                        "code": 200
                    }
                })
            else:
                return Response({"response": "Account Disabled or Deleted."}, status=status.HTTP_403_FORBIDDEN)
        user = User.objects.filter(email=email)
        if user:
            if user[0].login_from not in ['google', 'facebook']:
                response = {"response": "You have already registered your account from web."}
                return Response(response, status=status.HTTP_403_FORBIDDEN)
        ts = time.time()
        doc = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        user = User.objects.create_user(
            username=email,
            password=password,
            email=email,
            first_name=firstname,
            last_name=lastname,
            active=True,
            created_at=doc,
            login_from='google',
        )
        user.is_superuser = False
        user.is_staff = False
        user.save()
        conn = getConnection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_meta(user_id, meta_name, meta_value) VALUES(%s, %s, %s) RETURNING id;",
                    (user.pk, 'preferred_language', 'us'))
        conn.commit()
        initializeFilters(user.pk, 'account', status='aftersignup')
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "response": {
                'Login-Token': token.key,
                'id': user.pk,
                'email': user.email,
            },
            "meta": {
                "code": 200
            }
        })
        #return Response({'Unable to log in with provided credentials.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class FacebookLogin(ObtainAuthToken):

    @method_decorator(bearer_auth)
    def post(self, request, *args, **kwargs):
        if 'firstname' in request.data and 'lastname' in request.data and 'email' in request.data:
            # firstname_base64_decoded = base64.b64decode(request.data['firstname'])
            # firstname = firstname_base64_decoded.decode('UTF-8')
            firstname = request.data['firstname']
            # lastname_base64_decoded = base64.b64decode(request.data['lastname'])
            # lastname = lastname_base64_decoded.decode('UTF-8')
            lastname = request.data['lastname']
            # email_base64_decoded = base64.b64decode(request.data['email'])
            # email = email_base64_decoded.decode('UTF-8')
            email = request.data['email']
            password = '123455678'
        else:
            error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
            return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
        # return Response("Bas kr bhai")
        data = {
            "username": email,
            "password": password,
        }
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user.active:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "response": {
                        'Login-Token': token.key,
                        'id': user.pk,
                        'email': user.email,
                    },
                    "meta": {
                        "code": 200
                    }
                })
            else:
                return Response({"response": "Account Disabled or Deleted."}, status=status.HTTP_403_FORBIDDEN)
        user = User.objects.filter(email=email)
        if user:
            if user[0].login_from not in ['google', 'facebook']:
                response = {"response": "You have already registered your account from web."}
                return Response(response, status=status.HTTP_403_FORBIDDEN)
        ts = time.time()
        doc = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        user = User.objects.create_user(
            username=email,
            password=password,
            email=email,
            first_name=firstname,
            last_name=lastname,
            active=True,
            created_at=doc,
            login_from='facebook',
        )
        user.is_superuser = False
        user.is_staff = False
        user.save()
        conn = getConnection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_meta(user_id, meta_name, meta_value) VALUES(%s, %s, %s) RETURNING id;",
                    (user.pk, 'preferred_language', 'us'))
        conn.commit()
        initializeFilters(user.pk, 'account', status='aftersignup')
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "response": {
                'Login-Token': token.key,
                'id': user.pk,
                'email': user.email,
            },
            "meta": {
                "code": 200
            }
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@bearer_auth
def logoutuser(request, *args, **kwargs):
    """Logout the currently loged in user."""
    logout(request)
    key = request.headers["Authorization"].split()[1]
    # print(key)
    old_token = Token.objects.get(pk=key)
    old_token.delete()
    return Response({"response": 'user logged out successfully'}, status=status.HTTP_200_OK)
