import unittest  # Импортируем модуль для написания тестов
from unittest.mock import patch  # Импортируем инструмент для создания мок-объектов
import zipfile  # Импортируем модуль для работы с ZIP-архивами
import io  # Импортируем модуль для работы с потоками
import xml.etree.ElementTree as ET  # Импортируем модуль для работы с XML
import os
from hw2 import DependencyVisualizer  # Импортируем класс DependencyVisualizer из файла hw2.py

class TestDependencyVisualizer(unittest.TestCase):  # Создаем класс тестов, наследуемый от unittest.TestCase

    def setUp(self):
        # Создаем фиктивный конфигурационный файл
        self.config = {
            'program_path': 'C:/Program Files/Graphviz/bin/dot.exe',
            'package_path': 'MyPackage.1.0.0.nupkg',
            'output_path': 'my_output.dot',
            'max_depth': 1,
            'repo_url': 'https://github.com/Lisenkaz/homework_2'
        }
        # Инициализируем экземпляр DependencyVisualizer с фиктивными данными конфигурации
        self.visualizer = DependencyVisualizer(self.config)

    @patch('zipfile.ZipFile')  # Патч для замены zipfile.ZipFile на мок-объект
    def test_extract_dependencies(self, mock_zip):
        # Настройка мок-объекта для zip-файла
        mock_zip.return_value.__enter__.return_value.namelist.return_value = ['package.nuspec']
        mock_zip.return_value.__enter__.return_value.open.return_value = self.create_mock_nuspec()

        # Тестируем функцию extract_dependencies
        dependencies = self.visualizer.extract_dependencies('MyPackage.1.0.0.nupkg')
        expected_dependencies = {
            'Newtonsoft.Json': '13.0.1',
            'System.Text.Json': '6.0.0'
        }
        # Проверяем, что извлеченные зависимости соответствуют ожидаемым
        self.assertEqual(dependencies, expected_dependencies)

    def create_mock_nuspec(self):
        # Создаем фиктивный nuspec-файл для тестирования
        nuspec_xml = """<?xml version="1.0"?>
        <package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
            <dependencies>
                <dependency id="Newtonsoft.Json" version="13.0.1" />
                <dependency id="System.Text.Json" version="6.0.0" />
            </dependencies>
        </package>
        """
        # Возвращаем объект BytesIO, чтобы имитировать файл
        return io.BytesIO(nuspec_xml.encode('utf-8'))

    def test_generate_graph(self):
        # Тестируем метод генерации графа
        dependencies = {
            'Newtonsoft.Json': '13.0.1',
            'System.Text.Json': '6.0.0'
        }
        graph_code = self.visualizer.generate_graph(dependencies, depth=0)  # Генерируем граф
        expected_graph = (
            'digraph G {\n'
            '    "Newtonsoft.Json.13.0.1";\n'
            '    "System.Text.Json.6.0.0";\n'
            '}\n'
        )
        # Проверяем, что сгенерированный граф соответствует ожидаемому
        self.assertEqual(graph_code, expected_graph)

    @patch('builtins.print')  # Патч для подавления вывода на консоль
    @patch('hw2.DependencyVisualizer.extract_dependencies')  # Патч для замены метода extract_dependencies
    def test_visualize(self, mock_extract_dependencies, mock_print):
        # Настройка возврата для mock_extract_dependencies
        mock_extract_dependencies.return_value = {
            'Newtonsoft.Json': '13.0.1',
            'System.Text.Json': '6.0.0'
        }

        # Вызываем метод visualize
        self.visualizer.visualize()

        # Проверяем, что файл записывается корректно
        expected_output = (
            'digraph G {\n'
            '    "Newtonsoft.Json.13.0.1";\n'
            '    "System.Text.Json.6.0.0";\n'
            '}\n'
        )

        # Читаем содержимое выходного файла и проверяем его
        with open(self.config['output_path'], 'r') as f:
            written_content = f.read()
        
        self.assertEqual(written_content, expected_output)  # Проверяем, что содержимое файла соответствует ожидаемому

        # Удаляем выходной файл после проверки
        os.remove(self.config['output_path'])

if __name__ == '__main__':
    unittest.main()  # Запускаем тесты
