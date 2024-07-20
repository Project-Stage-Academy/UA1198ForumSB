from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
    TokenError,
)
from rest_framework_simplejwt.tokens import AccessToken
from users.models import CustomUser

AUTH_HEADER_KEY = b'authorization'


@database_sync_to_async
def get_user(user_id: int) -> CustomUser:
    try:
        return CustomUser.objects.get(user_id=user_id)
    except CustomUser.DoesNotExist:
        raise AuthenticationFailed()
    except Exception:
        # TODO: call logging function
        ...


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])

        if AUTH_HEADER_KEY not in headers:
            raise AuthenticationFailed("Auth header was not provided")

        try:
            _, token_key = headers[AUTH_HEADER_KEY].decode().split()
            jwt_payload: dict = AccessToken(token_key).payload

            scope["user"] = await get_user(jwt_payload["user_id"])
        except TokenError:
            raise InvalidToken()
        except Exception:
            # TODO: call logging function
            raise AuthenticationFailed()

        return await super().__call__(scope, receive, send)
