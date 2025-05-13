from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def global_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        'NotFound': _handle_not_found_error,
        'DoesNotExist': _handle_not_exist,
        'AttributeError': _handle_not_exist,
        'ValidationError': _handle_generic_error,
        'IntegrityError': _handle_integrity_error
    }

    exception_class = exc.__class__.__name__
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)

    return response


def _handle_integrity_error(exc, context, response):
    error_message = str(exc)

    # Look for unique constraint violation in the error string
    if "unique constraint" in error_message.lower() or "unique violation" in error_message.lower() or "duplicate" in error_message.lower():
        return Response({
            "error": "A record with this value already exists. Please use a different value."
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "error": error_message
    }, status=status.HTTP_400_BAD_REQUEST)


def _handle_generic_error(exc, context, response):
    if response is None:
        return Response({
            'non_field_errors': exc.messages
        }, status=status.HTTP_400_BAD_REQUEST)

    return response


def _handle_not_found_error(exc, context, response):
    view = context.get('view', None)

    if view and hasattr(view, 'queryset') and view.queryset is not None:
        error_key = view.queryset.model._meta.verbose_name

        response.data = {
            error_key: response.data['detail']
        }

    else:
        response = _handle_generic_error(exc, context, response)

    return response


def _handle_not_exist(exc, context, response):
    if response is None:
        return Response({
            'non_field_errors': exc.args
        }, status=status.HTTP_400_BAD_REQUEST)

    return response
