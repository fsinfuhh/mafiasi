"""
Implementation of a Vaultwarden admin API client
"""
import enum
from typing import TypeVar, Type, TypedDict, List, Mapping, Any, Optional
import requests
from dataclasses import dataclass
from django.conf import settings
from django.utils.timezone import datetime

Self = TypeVar("Self")


@dataclass(frozen=True)
class VwOrganization:
    enabled: bool
    name: str

    @classmethod
    def from_obj(cls: Type[Self], obj: Mapping[str, Any]) -> Self:
        return cls(
            enabled=obj["Enabled"],
            name=obj["Name"],
        )


class UserStatus(enum.IntEnum):
    ENABLED = 0
    INVITED = 1
    DISABLED = 2


@dataclass(frozen=True)
class VwUser:
    created_at: Optional[datetime]
    name: str
    email: str
    email_verified: str
    organizations: List[VwOrganization]
    status: UserStatus

    @classmethod
    def from_obj(cls: Type[Self], obj: Mapping[str, Any]) -> Self:
        return cls(
            created_at=datetime.fromisoformat(obj["CreatedAt"]) if "CreatedAt" in obj.keys() else None,
            name=obj["Name"],
            email=obj["Email"],
            email_verified=obj["EmailVerified"],
            organizations=[VwOrganization.from_obj(obj) for obj in obj["Organizations"]],
            status=obj["_Status"],
        )


class VwAdminClient:
    """
    A client to the Vaultwarden admin API
    """

    def __init__(self, vw_url: str, admin_token: str):
        self.vw_url = vw_url
        self.admin_token = admin_token
        self.session = requests.Session()

    @classmethod
    def init_from_settings(cls: Type[Self]) -> Self:
        return cls(settings.VAULT_URL.rstrip("/"), settings.VAULT_ADMIN_TOKEN)

    def authenticate(self):
        """
        Authenticate this client for future requests
        """
        response = self.session.post(
            url=f"{self.vw_url}/admin/",
            data={"token": self.admin_token},
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
        )
        response.raise_for_status()

    def ensure_authentication(self):
        """
        Ensure that the client is currently authenticated, refreshing the auth cookie if necessary
        """
        self.session.cookies.clear_expired_cookies()
        if self.session.cookies.get("VW_ADMIN") is None:
            self.authenticate()

    def list_users(self) -> List[VwUser]:
        """
        List all existing users
        """
        self.ensure_authentication()
        response = self.session.get(f"{self.vw_url}/admin/users")
        response.raise_for_status()
        return [VwUser.from_obj(obj) for obj in response.json()]

    def invite_user(self, email: str) -> VwUser:
        """
        Invite the user with the given email address
        """
        self.ensure_authentication()
        response = self.session.post(
            url=f"{self.vw_url}/admin/invite/",
            json={"email": email},
        )
        response.raise_for_status()
        return VwUser.from_obj(response.json())
