from investors.models import Investor
from rest_framework.serializers import ValidationError
from startups.models import Startup

from .mongo_models import NamespaceEnum, Room


def generate_room_name(
    participants: list,
    *,
    error_if_exists: bool = False
) -> str:
    participants = sorted(participants, key=lambda x: x.get("user_id"))
    room_name = ''

    for participant in participants:
        room_name += f"{participant['namespace']}_{participant['namespace_id']}"

    if error_if_exists and Room.objects.filter(name=room_name).first():
        raise ValidationError("Such room already exists.")

    return room_name


def is_namespace_info_correct(namespace_info: dict) -> bool:
    user_id = namespace_info.get("user_id")
    namespace = namespace_info.get("namespace")
    namespace_id = namespace_info.get("namespace_id")

    if namespace == NamespaceEnum.STARTUP.value:
        if not Startup.objects.filter(
            user__user_id=user_id,
            startup_id=namespace_id
        ).exists():
            raise ValidationError("Startup does not exist.")
    elif namespace == NamespaceEnum.INVESTOR.value:
        if not Investor.objects.filter(
            user__user_id=user_id,
            investor_id=namespace_id
        ).exists():
            raise ValidationError("Investor does not exist.")
    else:
        raise ValidationError("Invalid namespace.") 
    
    return True
