from abc import ABC, abstractmethod

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404

from startups.models import Startup
from projects.models import Project, ProjectSubscription
from investors.models import Investor
from .mongo_models import NamespaceInfo, Notification


def send_message(room_name: str, message: str):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        room_name,
        {"type": "chat_message", "message": message}
    )


def send_notification(notification: Notification):
    channel_layer = get_channel_layer()

    for receiver in notification.receivers:
        async_to_sync(channel_layer.group_send)(
            f"notifications_{receiver.user_id}",
            {"type": "notify_user", "message": notification.message}
        )


class NotificationManager(ABC):
    NAMESPACE_NAME: str = None
    NAMESPACE_RECEIVERS_NAME: str = None

    def __init__(self, namespace_obj: Investor | Startup) -> None:
        self.namespace = namespace_obj

    def _create_initiator_namespace(self) -> NamespaceInfo:
        return NamespaceInfo(
            user_id=self.namespace.user.user_id,
            namespace=self.NAMESPACE_NAME,
            namespace_id=self.get_namespace_id()
        )

    @abstractmethod
    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        ...

    @abstractmethod
    def get_namespace_id(self) -> int:
        ...

    def push_notification(self, message: str):
        initiator_namespace = self._create_initiator_namespace()
        receivers_namespaces = self._create_receivers_namespaces()

        notification = Notification(
            initiator=initiator_namespace,
            receivers=receivers_namespaces,
            message=message
        )
        notification.save()

        send_notification(notification)


class StartupNotificationManager(NotificationManager):
    NAMESPACE_NAME = "startup"
    NAMESPACE_RECEIVERS_NAME = "investor"

    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        receivers: list[NamespaceInfo] = []

        project: Project = get_object_or_404(
            Project,
            startup_id=self.namespace.startup_id
        )
        for i in ProjectSubscription.objects.filter(project=project):
            receivers.append(
                NamespaceInfo(
                    user_id=i.investor.user.user_id,
                    namespace=self.NAMESPACE_RECEIVERS_NAME,
                    namespace_id=i.investor.investor_id
                )
            )
            i.investor.investor_id

        return receivers

    def get_namespace_id(self) -> int:
        return self.namespace.startup_id


class InvestorNotificationManager(NotificationManager):
    NAMESPACE_NAME = "investor"
    NAMESPACE_RECEIVERS_NAME = "startup"

    def _create_receivers_namespaces(self) -> list[NamespaceInfo]:
        receivers: list[NamespaceInfo] = []

        for i in ProjectSubscription.objects.filter(investor=self.namespace):
            receivers.append(
                NamespaceInfo(
                    user_id=i.investor.user.user_id,
                    namespace=self.NAMESPACE_RECEIVERS_NAME,
                    namespace_id=i.project.startup.startup_id
                )
            )
            i.investor.investor_id

        return receivers

    def get_namespace_id(self) -> int:
        return self.namespace.investor_id
