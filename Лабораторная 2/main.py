import heapq
import os
import pickle
import sys
from collections import Counter, defaultdict

class HuffmanCoding:
    def __init__(self):
        self.codes = {}
        self.reverse_mapping = {}
    
    class HeapNode:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None
        
        def __lt__(self, other):
            return self.freq < other.freq
        
        def __eq__(self, other):
            if not other:
                return False
            if not isinstance(other, HuffmanCoding.HeapNode):
                return False
            return self.freq == other.freq

    def make_frequency_dict(self, text):
        return Counter(text)

    def build_heap(self, frequency):
        heap = []
        for char, freq in frequency.items():
            node = self.HeapNode(char, freq)
            heapq.heappush(heap, node)
        return heap

    def build_tree(self, heap):
        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            
            merged = self.HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            
            heapq.heappush(heap, merged)
        return heap[0] if heap else None

    def make_codes_helper(self, root, current_code):
        if root is None:
            return
        
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        
        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self, root):
        if root is None:
            return
        current_code = ""
        self.make_codes_helper(root, current_code)

    def get_encoded_text(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        if extra_padding == 8:
            extra_padding = 0
        for i in range(extra_padding):
            encoded_text += "0"
        
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Encoded text not padded properly")
            exit(0)
        
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    def compress(self, input_path, output_path):
        print(f"Сжатие файла: {input_path}")
        
        # Чтение исходного файла
        with open(input_path, 'rb') as file:
            text = file.read()
        
        if len(text) == 0:
            print("Файл пустой!")
            return
        
        # Подсчет частот
        frequency = self.make_frequency_dict(text)
        print(f"Различных символов: {len(frequency)}")
        
        # Построение дерева Хаффмена
        heap = self.build_heap(frequency)
        root = self.build_tree(heap)
        
        if root is None:
            print("Не удалось построить дерево Хаффмена")
            return
            
        self.make_codes(root)
        
        # Проверка, есть ли реальная выгода от сжатия
        original_bits = len(text) * 8
        encoded_bits = 0
        for char, freq in frequency.items():
            encoded_bits += len(self.codes[char]) * freq
        
        # Размер дерева (приблизительная оценка)
        tree_size_bits = len(frequency) * (8 + 16)  # символ + примерная длина кода
        
        total_compressed_bits = encoded_bits + tree_size_bits + 100  # +100 для заголовков и padding
        
        if total_compressed_bits >= original_bits:
            print("Предупреждение: Сжатие неэффективно для этого файла")
            print("Файл будет сохранен в несжатом виде с пометкой")
            
            with open(output_path, 'wb') as output:
                # Маркер несжатого файла
                output.write(b'HUFF0')  # 0 означает несжатый
                output.write(text)
            
            print(f"Файл сохранен как несжатый: {output_path}")
            return
        
        # Кодирование текста
        encoded_text = self.get_encoded_text(text)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        
        # Преобразование в байты
        b = self.get_byte_array(padded_encoded_text)
        
        # Сохранение сжатого файла с метаданными
        with open(output_path, 'wb') as output:
            # Маркер сжатого файла
            output.write(b'HUFF1')  # 1 означает сжатый
            
            # Сохраняем дерево кодирования
            tree_data = pickle.dumps(self.reverse_mapping)
            tree_size = len(tree_data)
            
            # Записываем размер дерева (4 байта)
            output.write(tree_size.to_bytes(4, byteorder='big'))
            output.write(tree_data)
            
            # Записываем закодированные данные
            output.write(b)
        
        # Расчет коэффициента сжатия
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Исходный размер: {original_size} байт")
        print(f"Сжатый размер: {compressed_size} байт")
        print(f"Степень сжатия: {compression_ratio:.2f}%")
        print(f"Сжатый файл сохранен как: {output_path}")

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        
        padded_encoded_text = padded_encoded_text[8:]
        if extra_padding > 0:
            encoded_text = padded_encoded_text[:-extra_padding]
        else:
            encoded_text = padded_encoded_text
        
        return encoded_text

    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = bytearray()
        
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                char = self.reverse_mapping[current_code]
                decoded_text.append(char)
                current_code = ""
        
        return decoded_text

    def decompress(self, input_path, output_path):
        print(f"Распаковка файла: {input_path}")
        
        with open(input_path, 'rb') as file:
            # Чтение маркера
            marker = file.read(5)
            
            if marker == b'HUFF0':
                # Несжатый файл
                decompressed_text = file.read()
                with open(output_path, 'wb') as output:
                    output.write(decompressed_text)
                print("Восстановлен несжатый файл")
                return
            elif marker != b'HUFF1':
                print("Ошибка: Неверный формат файла")
                return
            
            # Чтение размера дерева
            tree_size_bytes = file.read(4)
            tree_size = int.from_bytes(tree_size_bytes, byteorder='big')
            
            # Чтение дерева
            tree_data = file.read(tree_size)
            self.reverse_mapping = pickle.loads(tree_data)
            
            # Чтение закодированных данных
            bit_string = ""
            byte = file.read(1)
            while byte:
                byte_val = byte[0]
                bits = bin(byte_val)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
        
        # Удаление дополнения
        encoded_text = self.remove_padding(bit_string)
        
        # Декодирование
        decompressed_text = self.decode_text(encoded_text)
        
        # Сохранение распакованного файла
        with open(output_path, 'wb') as output:
            output.write(decompressed_text)
        
        print(f"Файл распакован как: {output_path}")
        
        # Проверка целостности
        original_size = len(decompressed_text)
        print(f"Размер распакованного файла: {original_size} байт")

def main():
    if len(sys.argv) < 4:
        print("Использование:")
        print("  Для сжатия: python huffman.py compress входной_файл выходной_файл.huf")
        print("  Для распаковки: python huffman.py decompress входной_файл.huf выходной_файл")
        print("\nПримеры:")
        print("  python huffman.py compress document.txt document.huf")
        print("  python huffman.py decompress document.huf document_restored.txt")
        return
    
    action = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    huffman = HuffmanCoding()
    
    if action == "compress":
        if not os.path.exists(input_file):
            print(f"Ошибка: Файл {input_file} не найден!")
            return
        huffman.compress(input_file, output_file)
    
    elif action == "decompress":
        if not os.path.exists(input_file):
            print(f"Ошибка: Файл {input_file} не найден!")
            return
        huffman.decompress(input_file, output_file)
    
    else:
        print("Неизвестное действие. Используйте 'compress' или 'decompress'")

if __name__ == "__main__":
    main()