import toml  # Импорт библиотеки toml для работы с конфигурационными файлами в формате TOML.
import os  # Импорт модуля os для взаимодействия с операционной системой (например, для работы с путями).
import zipfile  # Импорт модуля zipfile для работы с ZIP-архивами, в которых хранятся пакеты .nupkg.
import xml.etree.ElementTree as ET  # Импорт библиотеки для парсинга XML-документов.

class DependencyVisualizer:  # Определение класса DependencyVisualizer для визуализации зависимостей.
    def __init__(self, config):  # Конструктор класса, принимающий конфигурацию.
        self.program_path = config['program_path']  # Сохранение пути к инструменту визуализации из конфигурации.
        self.package_path = config['package_path']  # Сохранение пути к анализируемому пакету из конфигурации.
        self.output_path = config['output_path']  # Сохранение пути к файлу для вывода графа из конфигурации.
        self.max_depth = config['max_depth']  # Сохранение максимальной глубины анализа зависимостей из конфигурации.
        self.repo_url = config['repo_url']  # Сохранение URL-адреса репозитория из конфигурации.
    # Метод для извлечения зависимостей из пакета.
    def extract_dependencies(self, package_path, depth=0):
        if depth > self.max_depth:  # Проверка, не превышает ли текущая глубина максимальную.
            return {}  # Если превышает, вернуть пустой словарь (нет зависимостей).
        dependencies = {}  # Инициализация словаря для хранения зависимостей.
        try:
            # Открытие ZIP-архива с пакетом.
            with zipfile.ZipFile(package_path) as z:
                # Проверка наличия файла .nuspec в архиве.
                nuspec_file = [f for f in z.namelist() if f.endswith('.nuspec')]
                if not nuspec_file:
                    print(f"Ошибка: файл '.nuspec' не найден в {package_path}.")
                    return dependencies  # Возвращаем пустой словарь, если файл не найден.
                # Открытие файла спецификации пакета (.nuspec).
                with z.open(nuspec_file[0]) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()  # Получение корневого элемента XML.
                    # Пространства имен в файле .nuspec.
                    namespaces = {'ns': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}
                    # Поиск всех элементов зависимости в XML.
                    for dependency in root.findall('.//ns:dependency', namespaces):
                        dep_id = dependency.get('id')  # Получение идентификатора зависимости.
                        dep_version = dependency.get('version')  # Получение версии зависимости.
                        if dep_id is None or dep_version is None:
                            print("Ошибка: Не указаны идентификатор или версия зависимости.")
                            continue  # Пропускаем текущую зависимость, если данные отсутствуют.
                        dependencies[dep_id] = dep_version  # Сохраняем зависимость и её версию в словаре.
        except FileNotFoundError as e:
            print(f"Ошибка: файл не найден - {e}")  # Обработка ошибки, если архив не найден.
        except zipfile.BadZipFile:
            print(f"Ошибка: файл '{package_path}' не является корректным ZIP-архивом.")  # Обработка ошибки для некорректных архивов.
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")  # Общая обработка ошибок.
        return dependencies  # Возврат собранного словаря зависимостей.
    # Метод для создания графа.
    def generate_graph(self, dependencies, depth=0):
        graph = "digraph G {\n"  # Инициализация строки для графа в формате DOT.
        edges = {}  # Словарь для хранения зависимостей
        # Итерация по всем зависимостям
        for dep, version in dependencies.items():
            # Добавление узла для каждой зависимости 
            graph += f'    "{dep}.{version}";\n'
            # Инициализация списка подзависимостей для текущей зависимости
            edges[dep] = []
            if depth < self.max_depth:
            # Путь к .nupkg для подзависимости
                sub_package_path = f"{dep}.{version}.nupkg"
                # Попытка извлечь подзависимости для текущей зависимости
                if os.path.exists(sub_package_path):  # Проверка, существует ли файл подзависимости
                    # Рекурсивное извлечение подзависимостей с учетом глубины
                    sub_dependencies = self.extract_dependencies(sub_package_path, depth=depth + 1)
                    edges[dep].extend(sub_dependencies.keys())  # Добавление подзависимостей в список
                    # Для каждой подзависимости добавляем узел в граф
                    for sub_dep, sub_version in sub_dependencies.items():
                        if depth+1 < self.max_depth:
                        # Добавление стрелочки от зависимости к подзависимости
                            graph += f'    "{dep}.{version}" -> "{sub_dep}.{sub_version}";\n'  # Добавление ребра для зависимости
                else:
                    print(f"Предупреждение: подзависимость '{sub_package_path}' не найдена.")  # Вывод предупреждения, если файл не найден
        graph += "}\n"  # Закрытие графа.
        return graph  # Возврат сгенерированного графа.
    # Метод для визуализации графа.
    def visualize(self):  
        dependencies = self.extract_dependencies(self.package_path)  # Извлечение зависимостей из указанного пакета
        graph_code = self.generate_graph(dependencies)  # Генерация графа в формате DOT
        print(graph_code)  # Вывод графа на экран
        with open(self.output_path, 'w') as f:  # Открытие файла для записи графа
            f.write(graph_code)  # Запись графа в файл
# Главная функция программы.
def main(): 
    # Загрузка конфигурации
    config = toml.load('config.toml')  # Чтение конфигурационного файла в формате TOML
    visualizer = DependencyVisualizer(config)  # Создание экземпляра визуализатора с загруженной конфигурацией
    visualizer.visualize()  # Вызов метода визуализации для отображения зависимостей
if __name__ == "__main__":  # Проверка, является ли данный файл основным исполняемым файлом
    main()  # Вызов главной функции


