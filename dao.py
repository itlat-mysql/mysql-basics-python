from os import environ
from typing import List, Optional

import mysql.connector
from mysql.connector import MySQLConnection


def get_db_connection() -> MySQLConnection:
    """
    Инициализация соединения с базой данных (параметры берутся из переменных окружения + см. файл .env)
    """
    return mysql.connector.connect(
        host=environ.get('DB_HOST'),
        port=environ.get('DB_PORT'),
        username=environ.get('DB_USERNAME'),
        password=environ.get('DB_PASSWORD'),
        database=environ.get('DB_DATABASE'),
        charset=environ.get('DB_CHARSET')
    )


class Filtration:
    OPERATION_EQUAL = 1
    OPERATION_LIKE = 2
    OPERATION_GREATER_EQ = 3
    OPERATION_LESS_EQ = 4

    def __init__(self):
        self.filters = []

    def equal(self, name: str, value: str, max_size: Optional[int] = None):
        """
        Применение фильтра для строгого сравнения (=)
        """
        if self.is_valid_filtration_value(value, max_size):
            self.filters.append({'name': name, 'value': value, 'operation': Filtration.OPERATION_EQUAL})
        return self

    def like(self, name: str, value: str, max_size: Optional[int] = None):
        """
        Применение фильтра для нестрогого сравнения (LIKE)
        """
        if self.is_valid_filtration_value(value, max_size):
            self.filters.append({'name': name, 'value': value, 'operation': Filtration.OPERATION_LIKE})
        return self

    def greater_equal(self, name: str, value: str, max_size: Optional[int] = None):
        """
        Применение фильтра для сравнения на больше или равно (>=)
        """
        if self.is_valid_filtration_value(value, max_size):
            self.filters.append({'name': name, 'value': value, 'operation': Filtration.OPERATION_GREATER_EQ})
        return self

    def less_equal(self, name: str, value: str, max_size: Optional[int] = None):
        """
        Применение фильтра для сравнения на меньше или равно (<=)
        """
        if self.is_valid_filtration_value(value, max_size):
            self.filters.append({'name': name, 'value': value, 'operation': Filtration.OPERATION_LESS_EQ})
        return self

    @staticmethod
    def is_valid_filtration_value(value: str, max_size: Optional[int]) -> bool:
        """
        Проверка значения для фильтрации (не должно быть пустой строкой, а его длина не должна превышать лимита)
        """
        if value == '':
            return False

        if max_size is not None and len(value) > max_size:
            return False

        return True


def transform_filtration_to_query_where_data(filtration: Filtration) -> dict:
    """
    Трансформация объекта фильтрации в словарь, содержащий SQL строку (WHERE ... AND ...) и значения для фильтрации
    """
    query_where_data = {'where_query': '', 'where_values': []}

    filters = []
    for rule in filtration.filters:
        if rule['operation'] == Filtration.OPERATION_LIKE:
            filters.append('{} LIKE %s'.format(rule['name']))
            query_where_data['where_values'].append('%{}%'.format(rule['value']))
        elif rule['operation'] == Filtration.OPERATION_EQUAL:
            filters.append('{} = %s'.format(rule['name']))
            query_where_data['where_values'].append(rule['value'])
        elif rule['operation'] == Filtration.OPERATION_GREATER_EQ:
            filters.append('{} >= %s'.format(rule['name']))
            query_where_data['where_values'].append(rule['value'])
        elif rule['operation'] == Filtration.OPERATION_LESS_EQ:
            filters.append('{} <= %s'.format(rule['name']))
            query_where_data['where_values'].append(rule['value'])

    if filters:
        query_where_data['where_query'] = ' WHERE ' + ' AND '.join(filters)
    return query_where_data


class ProductDao:

    @staticmethod
    def get_all_products() -> List:
        """
        Простой запрос на выбор все строк с сортировкой по столбцу created_at (по возрастанию)
        """
        with get_db_connection() as con:
            cursor = con.cursor(dictionary=True)
            query = 'SELECT id, name, ean, price, created_at FROM products ORDER BY created_at ASC;'
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_products_with_limit_and_offset(limit: int, offset: int) -> List:
        """
        Запрос, позволяющий пропустить несколько строк и ограничить количество получаемых строк
        """
        with get_db_connection() as con:
            cursor = con.cursor(dictionary=True)
            query = 'SELECT id, name, ean, price, created_at FROM products ORDER BY created_at ASC LIMIT %s OFFSET %s;'
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()

    @staticmethod
    def get_products_qty() -> int:
        """
        Запрос, подсчитывающий количество строк в таблице
        """
        with get_db_connection() as con:
            cursor = con.cursor()
            query = 'SELECT COUNT(*) FROM products;'
            cursor.execute(query)
            return cursor.fetchone()[0]

    @staticmethod
    def get_single_product(product_id: int) -> Optional[dict]:
        """
        Запрос, возвращающий продукт, который содержит id, равный присланному значению product_id
        """
        with get_db_connection() as con:
            cursor = con.cursor(dictionary=True)
            query = 'SELECT id, name, ean, price, created_at FROM products WHERE id = %s;'
            cursor.execute(query, (product_id,))
            return cursor.fetchone()

    @staticmethod
    def get_products_with_filtration(product_filtration: Filtration) -> List:
        """
        Запрос, который возвращает строки, соответствующие присланным условиям фильтрации
        """
        with get_db_connection() as con:
            cursor = con.cursor(dictionary=True)

            query_where_data = transform_filtration_to_query_where_data(product_filtration)
            query = 'SELECT id, name, ean, price, created_at FROM products {} ORDER BY created_at ASC;' \
                .format(query_where_data['where_query'])

            cursor.execute(query, tuple(query_where_data['where_values']))
            return cursor.fetchall()
