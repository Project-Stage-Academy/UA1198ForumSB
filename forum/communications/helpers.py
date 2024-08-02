from rest_framework.serializers import ValidationError
from .mongo_models import Room
from startups.models import Startup
from investors.models import Investor


def generate_room_name(participants: list) -> str:
    room_name = ''

    for participant in participants:
        room_name += f"{participant['namespace']}_{participant['namespace_id']}"

    room_exists = Room.objects.filter(name=room_name).first()
    if room_exists:
        raise ValidationError("Such room already exists.")
    
    return room_name


def is_namespace_info_correct(namespace_info: dict):
    user_id = namespace_info.get("user_id")
    namespace = namespace_info.get("namespace")
    namespace_id = namespace_info.get("namespace_id")
    
    if namespace == "startup":
        return Startup.objects.filter(
            user__user_id=user_id,
            startup_id=namespace_id
        ).first()
    
    if namespace == "investor":
        return Investor.objects.filter(
            user__user_id=user_id,
            investor_id=namespace_id
        ).first()
    
    return None