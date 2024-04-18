from django.db import connection


def execute_raw_query(query, params={}, flat=False):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    if flat:
        return [
            row[0]
            for row in rows
        ]
    return rows
