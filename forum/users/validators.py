import re
from string import punctuation
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

class CustomUserValidator:
    @staticmethod
    def validate_passwords_match(password, password2):
        if password != password2:
            raise serializers.ValidationError({"Error": "Passwords don't match"})
        
    @staticmethod
    def validate_password(password):
        try:
            min_length = 8
            char_types = {
                'digit': re.compile(r'\d'),
                'upper': re.compile(r'[A-Z]'),
                'lower': re.compile(r'[a-z]'),
                'symbol': re.compile(r'[{}]'.format(re.escape(punctuation)))
            }

            errors = []
            if len(password) < min_length:
                errors.append('Password must be at least 8 characters long.')

            for char_type, pattern in char_types.items():
                if not pattern.search(password):
                    errors.append(f'Password must contain at least one {char_type}.')

            if errors:
                raise ValidationError(' '.join(errors))
            return password 
        except ValidationError as e:
            raise serializers.ValidationError({"Error": e.detail})

    @staticmethod
    def validate_user_phone(user_phone):
        try:
            pattern = re.compile(r'^\+[0-9]{1,3}[0-9]{9}$')
            if not pattern.match(user_phone):
                raise ValidationError('Invalid phone number. \
                                      Enter a valid phone number in the format +XXXXXXXXXXXX')
            return user_phone
        except ValidationError as e:
            raise serializers.ValidationError({"Error": e.detail})
