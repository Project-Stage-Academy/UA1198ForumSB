from drf_yasg import openapi

userRegisterView_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
        ),
        "password2": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
        ),
        "user_phone": openapi.Schema(type=openapi.TYPE_STRING),
        "description": openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=["first_name", "last_name", "email", "password", "password2"],
    example={
        "first_name": "test",
        "last_name": "test",
        "email": "your_email+2@gmail.com",
        "password": "Pass_12345",
        "password2": "Pass_12345",
        "description": "desc"
    },
)

userRegisterView_responses = {
    200: openapi.Response(
        description="Verification link was sent",
        schema=openapi.Schema(type=openapi.TYPE_STRING),
    ),
    400: openapi.Response(
        description="Bad request",
        schema=openapi.Schema(type=openapi.TYPE_STRING)
    )
}

sendEmailConfirmationView_responses = {
    201: openapi.Response(
        description="User created successfully",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=39),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="test3"),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="test3"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="your_email@gmail.com"),
                "user_phone": openapi.Schema(type=openapi.TYPE_STRING, example=None),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example=None),
            }
        ),
    ),
    400: openapi.Response(
        description="Bad request",
        schema=openapi.Schema(type=openapi.TYPE_STRING),
    ),
}