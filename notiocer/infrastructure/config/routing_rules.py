from pathlib import Path

import yaml
from pydantic import ValidationError
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from notiocer.domain.models.invoice_routing_rules import InvoiceRoutingRules


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Безопасный YAML-загрузчик, запрещающий повторные ключи."""

    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict:
        """Проверяет ключи до преобразования YAML в словарь."""
        self.flatten_mapping(node)
        seen_keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                if key in seen_keys:
                    raise ConstructorError(
                        None, None, f'Повторный ключ: {key}', key_node.start_mark
                    )
                seen_keys.add(key)
            except TypeError as error:
                raise ConstructorError(
                    None,
                    None,
                    'Ключ должен быть простым значением',
                    key_node.start_mark,
                ) from error
        return super().construct_mapping(node, deep=deep)


def load_routing_rules(path: Path) -> InvoiceRoutingRules:
    """Читает и проверяет YAML с правилами маршрутизации.

    Args:
        path: Путь к файлу правил в UTF-8.

    Returns:
        Проверенные правила для доменного маршрутизатора.

    Raises:
        OSError: Файл отсутствует или недоступен для чтения.
        ValueError: YAML повреждён или не соответствует структуре правил.
    """
    try:
        raw_rules = yaml.load(
            path.read_text(encoding='utf-8'), Loader=_UniqueKeySafeLoader
        )
    except yaml.YAMLError as error:
        raise ValueError(f'Ошибка YAML в файле правил {path}: {error}') from error
    try:
        return InvoiceRoutingRules.model_validate(raw_rules)
    except ValidationError as error:
        raise ValueError(f'Некорректные правила в файле {path}: {error}') from error
