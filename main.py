import argparse
import csv
import statistics
from collections import defaultdict
from tabulate import tabulate


def parse_args():
    parser = argparse.ArgumentParser(description='Генерация отчетов по тратам студентов')
    parser.add_argument('--files', nargs='+', required=True, help='Пути к CSV файлам')
    parser.add_argument('--report', required=True, help='Тип отчета (например, median-coffee)')
    return parser.parse_args()


# Регистрация отчетов — удобно через словарь
REPORTS = {}


def register_report(name):
    def decorator(func):
        REPORTS[name] = func
        return func
    return decorator


def read_csv_files(file_list):
    """
    Читает все файлы и возвращает список словарей с данными
    """
    data = []
    for file_path in file_list:
        with open(file_path, newline='', encoding='ANSI') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    return data


@register_report('median-coffee')
def report_median_coffee(data):
    """
    Расчет медианных затрат на кофе по каждому студенту.
    Возвращает список (имя, медиана), отсортированный по убыванию по медиане.
    """
    coffee_spent_by_student = defaultdict(list)

    for row in data:
        student = row['student']
        try:
            coffee_spent = float(row['coffee_spent'])
        except ValueError:
            continue  # пропускаем некорректные записи
        coffee_spent_by_student[student].append(coffee_spent)

    # Расчет медианы для каждого
    median_list = []
    for student, expenses in coffee_spent_by_student.items():
        med = statistics.median(expenses)
        median_list.append((student, med))

    # Сортировка по убыванию медианы
    median_list.sort(key=lambda x: x[1], reverse=True)
    return median_list


def main():
    args = parse_args()

    # Получаем нужную функцию отчета
    report_func = REPORTS.get(args.report)
    if not report_func:
        print(f"Отчет '{args.report}' не найден.")
        return

    # Чтение данных
    data = read_csv_files(args.files)

    # Формируем отчет
    report_data = report_func(data)

    # Выводим таблицу
    headers = ['student', 'median_coffee']
    table = [(student, f"{median:.2f}") for student, median in report_data]
    print(tabulate(table, headers=headers, tablefmt='grid'))


if __name__ == '__main__':
    main()