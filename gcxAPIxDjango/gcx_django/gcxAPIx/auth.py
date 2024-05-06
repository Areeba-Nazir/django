import os
from functools import wraps
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import User


class LoginAuth(TokenAuthentication):
    keyword = "Login-Token"

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Login Required.')

        if not token.user.active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        return token.user, token


def grammarin(fname=None, lname=None, mail=None, pswd=None, **kwargs):
    new_user = User(
        first_name=fname,
        last_name=lname,
        email=mail,
        login_from='grammarin',
    )
    new_user.set_password([pswd])
    return new_user


def bearer_auth(f_req):
    @wraps(f_req)
    def check_auth(request, *args, **kwargs):
        if ('Authentication-Token' in request.headers) and (
                request.headers['Authentication-Token'] == os.getenv("API_ACCESS_KEY")):
            return f_req(request, *args, **kwargs)
        else:
            print('Headers=>', request.headers)
            print('os value=>', os.getenv("API_ACCESS_KEY"))
            json_response = {"error_response": "You do not have the authorization to make this request."}
            return Response(json_response, status=status.HTTP_401_UNAUTHORIZED)

    return check_auth


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    # AuditEntry.objects.create(action='user_logged_in', ip=ip, username=user.username)
    user_obj = User.objects.get_by_natural_key(user.email)
    print(user.email, "logged in with IP", ip, "and user ID", user.id)
    user_obj.login_count += 1
    user_obj.save()


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    # AuditEntry.objects.create(action='user_logged_out', ip=ip, username=user.username)
    print(user.email, "logged out from IP", ip, "and user ID", user.id)


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    # AuditEntry.objects.create(action='user_login_failed', username=credentials.get('username', None))
    print("Login failed for", credentials.get('username', None))

# class EmailAuth(ModelBackend):
#    def authenticate(self, request, username=None, password=None, **kwargs):
#        UserModel = get_user_model()
#        try:
#            user = UserModel.objects.get_by_natural_key(username)
#        except UserModel.DoesNotExist:
#            return None
#        else:
#            if user.check_password(password):
#                return user
#        return None
