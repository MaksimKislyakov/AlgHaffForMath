"""
huffman.py — архиватор и дезархиватор файлов методом Хаффмена.
==============================================================

Автор: Кисляков Максим

---------------------------------------------------------------
Описание:
---------------------------------------------------------------
Данная программа реализует сжатие и восстановление файлов по
алгоритму Хаффмена. Программа работает с любыми файлами (в том
числе бинарными) и поддерживает весь набор байтов 0–255.

Формат сжатого файла (*.huf):
    0..3    : "HUF1" — магическая сигнатура (4 байта)
    4       : версия формата (1 байт, сейчас = 1)
    5..12   : исходный размер файла (uint64, little-endian)
    13..2060: 256 частот символов (по 8 байт на частоту, uint64 LE)
    далее   : битовый поток закодированных данных (MSB → первый бит)

Алгоритм:
1. Подсчитать частоты встречаемости всех байтов (0–255).
2. Построить бинарное дерево Хаффмена:
   - листья содержат символы;
   - у каждого узла частота = сумма частот потомков;
   - самый редкий символ получает длинный код, частый — короткий.
3. Построить таблицу кодов: 0/1-последовательность для каждого символа.
4. Записать заголовок + битовый поток сжатых данных.
5. При декодировании дерево восстанавливается по таблице частот.
"""

import heapq
import os
import pickle
import sys
from collections import Counter

class HuffmanCoding:
    """
    Класс для сжатия и распаковки файлов с использованием алгоритма Хаффмена.
    
    Attributes:
        codes (dict): Словарь для хранения кодов Хаффмена (символ -> код)
        reverse_mapping (dict): Обратный словарь для декодирования (код -> символ)
    """
    
    def __init__(self):
        """Инициализация архиватора Хаффмена."""
        self.codes = {}  # Словарь: символ -> код Хаффмена
        self.reverse_mapping = {}  # Словарь: код Хаффмена -> символ
    
    class HeapNode:
        """
        Узел бинарного дерева Хаффмена.
        
        Attributes:
            char (int/None): Символ (байт) или None для внутренних узлов
            freq (int): Частота встречаемости символа
            left (HeapNode): Левый потомок
            right (HeapNode): Правый потомок
        """
        
        def __init__(self, char, freq):
            """
            Инициализация узла дерева Хаффмена.
            
            Args:
                char: Символ (байт) или None для внутренних узлов
                freq: Частота встречаемости
            """
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None
        
        # Методы сравнения для работы с кучей
        def __lt__(self, other):
            """Сравнение узлов по частоте (для работы с кучей)."""
            return self.freq < other.freq
        
        # Определение равенства узлов
        def __eq__(self, other):
            """Проверка равенства узлов."""
            if not other:
                return False
            if not isinstance(other, HuffmanCoding.HeapNode):
                return False
            return self.freq == other.freq

    def make_frequency_dict(self, text):
        """
        Создание словаря частот встречаемости символов.
        
        Args:
            text (bytes): Входные данные для анализа
            
        Returns:
            Counter: Словарь с частотами символов
        """
        return Counter(text)

    def build_heap(self, frequency):
        """
        Построение минимальной кучи из символов и их частот.
        
        Args:
            frequency (dict): Словарь частот символов
            
        Returns:
            list: Минимальная куча узлов Хаффмена
        """
        heap = []
        for char, freq in frequency.items():
            node = self.HeapNode(char, freq)
            heapq.heappush(heap, node)
        return heap

    def build_tree(self, heap):
        """
        Построение дерева Хаффмена из кучи узлов.
        
        Процесс построения:
        1. Берутся два узла с наименьшей частотой
        2. Создается новый узел с суммой частот
        3. Новый узел добавляется обратно в кучу
        4. Процесс повторяется пока в куче не останется один узел (корень)
        
        Args:
            heap (list): Минимальная куча узлов
            
        Returns:
            HeapNode: Корень дерева Хаффмена или None если куча пуста
        """
        while len(heap) > 1:
            # Извлечение двух узлов с наименьшей частотой
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            
            # Создание нового узла с суммой частот
            merged = self.HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            
            # Добавление нового узла обратно в кучу
            heapq.heappush(heap, merged)
        
        # Возврат корня дерева (последний оставшийся узел)
        return heap[0] if heap else None

    def make_codes_helper(self, root, current_code):
        """
        Рекурсивный помощник для генерации кодов Хаффмена.
        
        Args:
            root (HeapNode): Текущий узел дерева
            current_code (str): Текущий формируемый код
        """
        if root is None:
            return
        
        # Если достигли листа (символа), сохраняем код
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        
        # Рекурсивный обход левого поддерева (добавляем '0')
        self.make_codes_helper(root.left, current_code + "0")
        # Рекурсивный обход правого поддерева (добавляем '1')
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self, root):
        """
        Генерация кодов Хаффмена для всех символов.
        
        Args:
            root (HeapNode): Корень дерева Хаффмена
        """
        if root is None:
            return
        current_code = ""
        self.make_codes_helper(root, current_code)

    def get_encoded_text(self, text):
        """
        Кодирование текста с использованием сгенерированных кодов.
        
        Args:
            text (bytes): Исходные данные для кодирования
            
        Returns:
            str: Закодированная битовая строка
        """
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        """
        Добавление padding к закодированному тексту для выравнивания по байтам.
        
        Args:
            encoded_text (str): Закодированная битовая строка
            
        Returns:
            str: Выровненная битовая строка с информацией о padding
        """
        # Расчет необходимого дополнения
        extra_padding = 8 - len(encoded_text) % 8
        if extra_padding == 8:
            extra_padding = 0
        
        # Добавление нулей в конец
        for i in range(extra_padding):
            encoded_text += "0"
        
        # Добавление информации о количестве padding битов
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        """
        Преобразование битовой строки в массив байтов.
        
        Args:
            padded_encoded_text (str): Выровненная битовая строка
            
        Returns:
            bytearray: Массив байтов для записи в файл
        """
        if len(padded_encoded_text) % 8 != 0:
            print("Ошибка: Закодированный текст не выровнен правильно")
            exit(0)
        
        b = bytearray()
        # Разбиение на байты (по 8 бит)
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    def compress(self, input_path, output_path):
        """
        Сжатие файла методом Хаффмена.
        
        Процесс сжатия:
        1. Чтение и анализ частот символов
        2. Построение дерева Хаффмена
        3. Генерация кодов
        4. Проверка эффективности сжатия
        5. Кодирование и сохранение
        
        Args:
            input_path (str): Путь к исходному файлу
            output_path (str): Путь для сохранения сжатого файла
        """
        print(f"Сжатие файла: {input_path}")
        
        # Чтение исходного файла в бинарном режиме
        with open(input_path, 'rb') as file:
            text = file.read()
        
        if len(text) == 0:
            print("Файл пустой!")
            return
        
        # Этап 1: Подсчет частот символов
        frequency = self.make_frequency_dict(text)
        print(f"Различных символов: {len(frequency)}")
        
        # Этап 2: Построение дерева Хаффмена
        heap = self.build_heap(frequency)
        root = self.build_tree(heap)
        
        if root is None:
            print("Не удалось построить дерево Хаффмена")
            return
            
        # Этап 3: Генерация кодов
        self.make_codes(root)
        
        # Проверка эффективности сжатия
        original_bits = len(text) * 8  # Исходный размер в битах
        encoded_bits = 0
        for char, freq in frequency.items():
            encoded_bits += len(self.codes[char]) * freq
        
        # Оценка размера дерева (символ + примерная длина кода)
        tree_size_bits = len(frequency) * (8 + 16)
        
        # Общий размер сжатых данных (коды + дерево + заголовки)
        total_compressed_bits = encoded_bits + tree_size_bits + 100
        
        # Если сжатие неэффективно, сохраняем как несжатый файл
        if total_compressed_bits >= original_bits:
            print("Предупреждение: Сжатие неэффективно для этого файла")
            print("Файл будет сохранен в несжатом виде с пометкой")
            
            with open(output_path, 'wb') as output:
                # Маркер несжатого файла
                output.write(b'HUFF0')  # 0 означает несжатый
                output.write(text)
            
            print(f"Файл сохранен как несжатый: {output_path}")
            return
        
        # Этап 4: Кодирование данных
        encoded_text = self.get_encoded_text(text)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        
        # Преобразование в байты
        b = self.get_byte_array(padded_encoded_text)
        
        # Сохранение сжатого файла с метаданными
        with open(output_path, 'wb') as output:
            # Маркер сжатого файла
            output.write(b'HUFF1')  # 1 означает сжатый
            
            # Сохраняем дерево кодирования (сериализованное)
            tree_data = pickle.dumps(self.reverse_mapping)
            tree_size = len(tree_data)
            
            # Записываем размер дерева (4 байта в big-endian)
            output.write(tree_size.to_bytes(4, byteorder='big'))
            output.write(tree_data)
            
            # Записываем закодированные данные
            output.write(b)
        
        # Расчет и вывод статистики сжатия
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Исходный размер: {original_size} байт")
        print(f"Сжатый размер: {compressed_size} байт")
        print(f"Степень сжатия: {compression_ratio:.2f}%")
        print(f"Сжатый файл сохранен как: {output_path}")

    def remove_padding(self, padded_encoded_text):
        """
        Удаление padding из закодированного текста.
        
        Args:
            padded_encoded_text (str): Битовая строка с padding
            
        Returns:
            str: Оригинальная закодированная строка без padding
        """
        # Извлечение информации о padding (первые 8 бит)
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        
        # Удаление информации о padding
        padded_encoded_text = padded_encoded_text[8:]
        
        # Удаление добавленных нулей
        if extra_padding > 0:
            encoded_text = padded_encoded_text[:-extra_padding]
        else:
            encoded_text = padded_encoded_text
        
        return encoded_text

    def decode_text(self, encoded_text):
        """
        Декодирование битовой строки в исходные данные.
        
        Args:
            encoded_text (str): Закодированная битовая строка
            
        Returns:
            bytearray: Распакованные данные
        """
        current_code = ""
        decoded_text = bytearray()
        
        # Последовательное чтение битов и поиск соответствующих кодов
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                char = self.reverse_mapping[current_code]
                decoded_text.append(char)
                current_code = ""  # Сброс текущего кода
        
        return decoded_text

    def decompress(self, input_path, output_path):
        """
        Распаковка сжатого файла.
        
        Процесс распаковки:
        1. Чтение метки файла
        2. Загрузка дерева кодирования
        3. Чтение и декодирование данных
        4. Сохранение распакованного файла
        
        Args:
            input_path (str): Путь к сжатому файлу
            output_path (str): Путь для сохранения распакованного файла
        """
        print(f"Распаковка файла: {input_path}")
        
        with open(input_path, 'rb') as file:
            # Чтение маркера типа файла
            marker = file.read(5)
            
            if marker == b'HUFF0':
                # Обработка несжатого файла
                decompressed_text = file.read()
                with open(output_path, 'wb') as output:
                    output.write(decompressed_text)
                print("Восстановлен несжатый файл")
                return
            elif marker != b'HUFF1':
                print("Ошибка: Неверный формат файла")
                return
            
            # Чтение размера дерева кодирования
            tree_size_bytes = file.read(4)
            tree_size = int.from_bytes(tree_size_bytes, byteorder='big')
            
            # Чтение и десериализация дерева кодирования
            tree_data = file.read(tree_size)
            self.reverse_mapping = pickle.loads(tree_data)
            
            # Чтение закодированных данных и преобразование в битовую строку
            bit_string = ""
            byte = file.read(1)
            while byte:
                byte_val = byte[0]
                bits = bin(byte_val)[2:].rjust(8, '0')  # Преобразование в 8-битную строку
                bit_string += bits
                byte = file.read(1)
        
        # Удаление padding
        encoded_text = self.remove_padding(bit_string)
        
        # Декодирование данных
        decompressed_text = self.decode_text(encoded_text)
        
        # Сохранение распакованного файла
        with open(output_path, 'wb') as output:
            output.write(decompressed_text)
        
        print(f"Файл распакован как: {output_path}")
        
        # Вывод информации о размере распакованного файла
        original_size = len(decompressed_text)
        print(f"Размер распакованного файла: {original_size} байт")

def main():
    """
    Главная функция программы.
    
    Обрабатывает аргументы командной строки и запускает соответствующий режим работы.
    """
    if len(sys.argv) < 4:
        print("Huffman Archiver - Программа для сжатия и распаковки файлов")
        print("\nИспользование:")
        print("  Для сжатия: python huffman.py compress входной_файл выходной_файл.huf")
        print("  Для распаковки: python huffman.py decompress входной_файл.huf выходной_файл")
        print("\nПримеры:")
        print("  python huffman.py compress document.txt document.huf")
        print("  python huffman.py decompress document.huf document_restored.txt")
        print("\nПримечание:")
        print("  - Программа автоматически определяет эффективность сжатия")
        print("  - Маленькие файлы могут сохраняться в несжатом виде")
        print("  - Поддерживаются все типы файлов (текст, бинарные, исполняемые)")
        return
    
    action = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Создание экземпляра архиватора
    huffman = HuffmanCoding()
    
    if action == "compress":
        # Проверка существования входного файла
        if not os.path.exists(input_file):
            print(f"Ошибка: Файл {input_file} не найден!")
            return
        huffman.compress(input_file, output_file)
    
    elif action == "decompress":
        # Проверка существования входного файла
        if not os.path.exists(input_file):
            print(f"Ошибка: Файл {input_file} не найден!")
            return
        huffman.decompress(input_file, output_file)
    
    else:
        print("Неизвестное действие. Используйте 'compress' или 'decompress'")
        print("Запустите программу без аргументов для просмотра справки")

if __name__ == "__main__":
    """
    Точка входа в программу.
    """
    main()