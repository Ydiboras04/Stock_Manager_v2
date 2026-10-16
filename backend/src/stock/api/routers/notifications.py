from fastapi import APIRouter

from stock.api.deps import CurrentUserDep, ReposDep
from stock.api.schemas import NotificationOut
from stock.core.use_cases import notifications as uc

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(user: CurrentUserDep, repos: ReposDep):
    """Notifications of the current user's role, newest first."""
    return uc.list_notifications(repos.notifications, user.role)


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, user: CurrentUserDep, repos: ReposDep):
    return uc.mark_notification_read(repos.notifications, notification_id, user.role)
