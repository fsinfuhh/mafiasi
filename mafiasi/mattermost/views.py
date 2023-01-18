from django.http import JsonResponse
from oauth2_provider.decorators import protected_resource


@protected_resource()
def get_user_info(request):
    user = request.resource_owner

    return JsonResponse(
        {
            "id": user.id,
            "username": user.get_username(),
            "login": user.get_username(),
            "email": user.email,
            "name": user.get_full_name(),
        }
    )
