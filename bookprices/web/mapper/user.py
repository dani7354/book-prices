from bookprices.web.service.auth_service import WebUser
from bookprices.web.viewmodels.user import UserInfoViewModel


def map_user_view_model(user: WebUser) -> UserInfoViewModel:
    return UserInfoViewModel(
        id=user.id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        is_active=user.is_active,
        created=user.created.isoformat(),
        updated=user.updated.isoformat())
