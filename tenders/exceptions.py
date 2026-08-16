class TenderError(Exception):
    """Базовая ошибка домена тендеров."""


class TenderNotFoundError(TenderError):
    """Тендер не найден."""


class InvalidStatusTransitionError(TenderError):
    """Недопустимый переход статуса."""

    def __init__(self, current_status: str, requested_status: str) -> None:
        self.current_status = current_status
        self.requested_status = requested_status
        super().__init__(
            f"Переход из '{current_status}' в '{requested_status}' запрещён."
        )