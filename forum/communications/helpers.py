from rest_framework.serializers import ValidationError
from .mongo_models import Room, NamespaceEnum
from startups.models import Startup
from investors.models import Investor


def generate_room_name(participants: list) -> str:
    if not participants:
        raise ValidationError("Participants list cannot be empty.")
    
    room_name = ''.join([
        f"{participant['namespace']}_{participant['namespace_id']}"
        for participant in participants
    ])
    
    room_exists = Room.objects.filter(name=room_name).first()
    if room_exists:
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