import re
from string import punctuation
from rest_framework import serializers

PHONE_PATTERN = re.compile(r'^\+[0-9]{1,3}[0-9]{9}$')
CHAR_TYPES = {
    'digit': re.compile(r'\d'),
    'upper': re.compile(r'[A-Z]'),
    'lower': re.compile(r'[a-z]'),
    'symbol': re.compile(r'[{}]'.format(re.escape(punctuation)))
}

class CustomUserValidator:
    @staticmethod
    def validate_password(password):
        min_length = 8
        errors = []
        if len(password) < min_length:
            errors.append('Password must be at least 8 characters long.')

        for char_type, pattern in CHAR_TYPES.items():
            if not pattern.search(password):
                errors.append(f'Password must contain at least one {char_type}.')

        if errors:
            raise serializers.ValidationError(errors)

        return password

    @staticmethod
    def validate_user_phone(user_phone):
        if not PHONE_PATTERN.match(user_phone):
            raise serializers.ValidationError('Invalid user\'s phone. Format: +XXXXXXXXXXXX')

        return user_phone
