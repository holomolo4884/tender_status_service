from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .exceptions import InvalidStatusTransitionError, TenderNotFoundError


def tender_exception_handler(exc, context):
    if isinstance(exc, TenderNotFoundError):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, InvalidStatusTransitionError):
        return Response(
            {
                "detail": str(exc),
                "current_status": exc.current_status,
                "requested_status": exc.requested_status,
            },
            status=status.HTTP_409_CONFLICT,
        )

    # Остальное отдаём стандартному обработчику DRF.
    response = exception_handler(exc, context)

    # DRF возвращает 400 для ошибок валидации. Приводим к 422.
    if response is not None and response.status_code == status.HTTP_400_BAD_REQUEST:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return response