import pytest
import io
import csv
from collections import defaultdict
import main
from main import read_csv_files, report_median_coffee

@pytest.fixture
def sample_csv(tmp_path):
    # Создаем временный CSV с данными
    content = (
        "student,date,coffee_spent,sleep_hours,study_hours,mood,exam\n"
        "Алексей Смирнов,2024-06-01,450,4.5,12,норм,Математика\n"
        "Алексей Смирнов,2024-06-02,500,4.0,14,устал,Математика\n"
        "Алексей Смирнов,2024-06-03,550,3.5,16,зомби,Математика\n"
        "Дарья Петрова,2024-06-01,200,7.0,6,отл,Математика\n"
    )
    file_path = tmp_path / "data.csv"
    file_path.write_text(content, encoding='ANSI')
    return str(file_path)

def test_read_csv_files(sample_csv):
    # Проверка чтения файла
    data = main.read_csv_files([sample_csv])
    assert len(data) == 4
    assert data[0]['student'] == 'Алексей Смирнов'
    assert data[1]['coffee_spent'] == '500'

# Тестируем функцию report_median_coffee
def test_report_median_coffee():
    data = [
        {'student': 'Наталья', 'coffee_spent': '10'},
        {'student': 'Наталья', 'coffee_spent': '20'},
        {'student': 'Сергей', 'coffee_spent': '30'},
        {'student': 'Сергей', 'coffee_spent': '40'},
        {'student': 'Александр', 'coffee_spent': 'NaN'},
        {'student': 'Наталья', 'coffee_spent': 'abc'}  # некорректное
    ]
    result = main.report_median_coffee(data)
    # Проверяем, что
    assert ('Наталья', 15.0) in result
    assert ('Сергей', 35.0) in result
    # Убедимся, что некорректные или NaN пропущены
    assert ('Александр', 0) not in result  # Charlie не должен быть в результате
    # Медианны правильные
    assert any(student == 'Наталья' for student, _ in result)

#тестовая функция, которая проверяет поведение функции report_median_coffee при условии, когда ей передают пустой список данных.
def test_report_median_coffee_empty():
    assert main.report_median_coffee([]) == []

# интеграционный тест, который проверяет работу всей программы целиком (функции main()), имитируя запуск с командной строки.
def test_main_integration(monkeypatch, capsys, sample_csv):
    # Имитация аргументов командной строки
    class Args:
        files = [sample_csv]
        report = 'median-coffee'
    monkeypatch.setattr(main, 'parse_args', lambda: Args())

    # Выполнение main()
    main.main()

    # Проверка вывода
    captured = capsys.readouterr()
    assert 'Алексей Смирнов' in captured.out
    assert 'Дарья Петрова' in captured.out

#  тест, который проверяет, как функция report_median_coffee ведет себя при неправильных данных.
# значение coffee_spent, которое не является числом, а строкой 'абв'
def test_report_with_invalid_coffee():
    data = [
        {'student': 'Сергей', 'coffee_spent': 'абв'} 
    ]
    result = main.report_median_coffee(data)
    assert result == []

# тест, который проверяет возможность чтения файлов с кодировкой, отличной от ANSI
def test_read_csv_files_with_non_ansi(tmp_path):
    # Создать файл с другой кодировкой
    text = "student,coffee_spent\nИван,300"
    f = tmp_path / "latin1.csv"
    f.write_bytes(text.encode('latin1'))

    # Тест
    data = main.read_csv_files([str(f)])
    assert data[0]['student'] == 'Иван'

# Тест на несуществующий файл (чтобы проверить обработку)
def test_read_csv_files_nonexistent(tmp_path):
    with pytest.raises(FileNotFoundError):
        main.read_csv_files([str(tmp_path / 'nofile.csv')])