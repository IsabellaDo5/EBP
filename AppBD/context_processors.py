def global_variable(request):
    return {
        'id_rol': request.session.get('id_rol')
    }