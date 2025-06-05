from bookprices.web.service.auth_service import WebUser
from bookprices.web.viewmodels.user import UserEditViewModel


def map_user_view_model(user: WebUser) -> UserEditViewModel:
    return UserEditViewModel(
        id=user.id,
        created=user.created.isoformat(),
        updated=user.updated.isoformat(),
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        is_active=user.is_active,
        image_url=user.image_url,
        access_level=user.access_level.name)
