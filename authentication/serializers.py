from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode



class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=68, min_length=6,write_only=True)

    class Meta:
        model = User
        fields = ['email','username', 'password']

    def validate(self, attrs):
        email=attrs.get('email', '')
        username=attrs.get('username', '')
        
        if not username.isalnum():
            raise serializers.ValidationError('username should contain alphanumeric characters')
        return attrs
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(email + ' is already in use')  
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# the below block of codes is needed while testing withing with swagger
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password =serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=6, read_only=True)
    tokens =serializers.CharField(max_length=68, min_length=6, read_only=True)

    class Meta:
        model = User
        fields=['email','username', 'tokens','password']

    def validate(self,attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid Credentials, Try again')
        if not user.is_active:
            raise AuthenticationFailed(' Account disabled, Contact admin') 
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified, please verify Email')
        return {
            'email':user.email,
            'username':user.username,
            'tokens' : user.tokens
        }

class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields =['email']

    # def validate(self, attrs):
    #         email = attrs['data'].get('email', '')
    #         user = User.objects.filter(email = email)
    #         if user.exists():
    #             uidb64 = urlsafe_base64_encode(user.id)
    #             token = PasswordResetTokenGenerator().make_token(user)
    #             current_site = get_current_site(request = attrs['request']).domain

    #             relativeLink =reverse('password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
    #             absurl='http://'+current_site + relativeLink
    #             email_body= 'Hello \n Use the link below to Reset your password \n'+ absurl
    #             data = {
    #             'email_body': email_body, 'to_email': user.email, 'email_subject':'RESET PASSWORD'
    #             }
    #             Util.send_email(data)
    #             return super().validate(attrs)


class PasswordTokenSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(min_length=1)
    token = serializers.CharField(min_length = 1)
    def validate(self, attrs):
        try:
            uidb64 = attrs.get('uidb64', '')
            token = attrs.get('token', '')
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id = id)
            if PasswordResetTokenGenerator().check_token(user,token) is False:
                raise serializers.ValidationError('Token is not valid any more', 401)
            return {
            'token':token,
            'uidb64':uidb64,
            }
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator():
                return serializers.ValidationError('Token is not Valid any more', status=401)

class SetNewPasswordAPIViewSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields=['password','token','uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if PasswordResetTokenGenerator().check_token(user, token) is False:
                raise serializers.ValidationError('The reset link is inValid',401)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError('The reset link is inValid',401)
