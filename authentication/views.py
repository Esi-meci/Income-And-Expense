from django.shortcuts import render
from rest_framework import generics, status,views
from .serializers import (RegisterSerializer, 
EmailVerificationSerializer,LoginSerializer,
RequestPasswordResetEmailSerializer, SetNewPasswordAPIViewSerializer, PasswordTokenSerializer)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode



# Create your views here.
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self,request):
        user = request.data
        serializer = self.serializer_class(data=user)
        # serializer = serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data =serializer.data 
        user= User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user)
        current_site = get_current_site(request).domain
        relativeLink=reverse('verifyemail')
        absurl='http://'+current_site+relativeLink+'?token='+str(token.access_token)
        email_body= 'Hello '+ user.username + ' please use the link below to verify your Email \n'+ absurl
        data = {
           'email_body': email_body, 'to_email': user.email, 'email_subject':'verify your email'
        }
        Util.send_email(data)
        return Response(user_data,status=status.HTTP_201_CREATED)

# the below block of codes is used when swagger is not in play
# class VerifyEmail(generics.GenericAPIView):
#     def get(self, request):
#         token = request.GET.get('token')
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY)
#             user = User.objects.get(id=payload['user_id'])
#             if not user.is_verfied:
#                 user.is_verfied = True
#                 user.save()
#             return Response({'email':'sucessfully activated'},status=status.HTTP_200_OK)
#         except jwt.ExpiredSignatureError as identifier:
#             return Response({'error':'Expired Activation Link'}, status=status.HTTP_400_BAD_REQUEST)
#         except jwt.exceptions.DecodeError as identifier:
#             return Response({'error':'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

# in other to customise a token while using swagger, the below block of codes for verifying Email is needed
class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email':'sucessfully activated'},status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Expired Activation Link'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializer=self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        data={'request':request, 'data': request.data}
        serializer = self.serializer_class(data=request.data)
        # def validate(self, attrs):
        email = request.data['email']            
        if User.objects.filter(email = email).exists():
            user= User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request = request).domain
            relativeLink =reverse('password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
            absurl='http://'+current_site + relativeLink
            email_body= 'Hello \n Use the link below to Reset your password \n'+ absurl
            data = {
            'email_body': email_body, 'to_email': user.email, 'email_subject':'RESET PASSWORD'
            }
            Util.send_email(data)
        return Response({'Success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = PasswordTokenSerializer
    def get(self, request):
        # try:
        #     id = smart_str(urlsafe_base64_decode(uidb64))
        #     user = User.objects.get(id = id)
        #     if PasswordResetTokenGenerator().check_token(user,token) is False:
        #         return Response({'error': 'Token is not valid any more'}, status=status.HTTP_401_UNAUTHORIZED)
        #     return Response({'Success':True, 'message':'Credentiald Valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
        # except DjangoUnicodeDecodeError as identifier:
        #     if not PasswordResetTokenGenerator():
        #         return Response({'error':'Token is not Valid any more'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'Success':True, 'message':'Credentiald Valid', 'data' :serializer.data}, status=status.HTTP_200_OK)
class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class= SetNewPasswordAPIViewSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':'Password Successfully Changed', 'data':serializer.data}, status=status.HTTP_200_OK)