from django.shortcuts import redirect


def redirection(request, id):
    return redirect(
        request.build_absolute_uri().replace(
            f's/{id}', f'recipes/{id}'
        )
    )
