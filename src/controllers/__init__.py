"""Слой контроллеров проекта notiocer.

Содержит входные точки, которые связывают внешние триггеры
(запуск из командной строки, локальный файл и т.п.) со сценариями
использования прикладного слоя. Контроллеры отвечают только за
подготовку входных данных и вызов use case — бизнес-логики здесь нет.

Состав пакета:

- :class:`LocalExcelReportController` — читает отчёт Excel с диска,
  оборачивает его в :class:`CreateMailingListCommand` и передаёт
  в :class:`CreateMailingListFromExcelUseCase`.
"""

from .local_excel_report_controller import LocalExcelReportController

__all__ = ['LocalExcelReportController']
