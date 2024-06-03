from django.conf import settings


def global_variable(request):
    return {
        'id_rol': request.session.get('id_rol'),
        'MEDIA_URL': settings.MEDIA_URL,
    }