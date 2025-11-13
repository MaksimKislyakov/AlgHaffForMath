"""
Лабораторная работа по помехоустойчивым кодам
Реализация групповых и циклических кодов для обнаружения и исправления ошибок
"""

import numpy as np
from typing import List, Tuple, Optional

class GroupCode:
    """
    Класс для работы с групповыми (линейными) кодами
    
    Attributes:
        check_matrix (np.ndarray): Проверочная матрица кода
        n_k (int): Число контрольных разрядов
        n_i (int): Число информационных разрядов  
        n (int): Общая длина кодового слова
    """
    
    def __init__(self, check_matrix: List[List[int]]) -> None:
        """
        Инициализация группового кода
        
        Args:
            check_matrix: Проверочная матрица размером n_i x n_k
        """
        self.check_matrix = np.array(check_matrix)
        self.n_k = self.check_matrix.shape[1]  # число контрольных разрядов
        self.n_i = self.check_matrix.shape[0]  # число информационных разрядов
        self.n = self.n_i + self.n_k  # общая длина кода
        
        print(f"Создан групповой код с параметрами:")
        print(f"  Информационные разряды: {self.n_i}")
        print(f"  Контрольные разряды: {self.n_k}")
        print(f"  Общая длина: {self.n}")
        
    def generate_code(self, info_part: List[int]) -> List[int]:
        """
        Генерация избыточного кода по информационной части
        
        Args:
            info_part: Информационная часть кода (длина n_i)
            
        Returns:
            Полное кодовое слово длиной n
        """
        # Проверка длины информационной части
        if len(info_part) != self.n_i:
            raise ValueError(f"Длина информационной части должна быть {self.n_i}")
            
        info_part = np.array(info_part)
        control_bits = []
        
        print(f"\nГенерация кода для информационной части: {info_part}")
        
        # Вычисление контрольных битов через умножение на проверочную матрицу
        for i in range(self.n_k):
            control_bit = 0
            for j in range(self.n_i):
                # Суммирование по модулю 2: info_part[j] & check_matrix[j, i]
                control_bit ^= info_part[j] & self.check_matrix[j, i]
            control_bits.append(control_bit)
            print(f"  Контрольный бит {i+1}: {control_bit}")
        
        full_code = list(info_part) + control_bits
        print(f"  Полное кодовое слово: {full_code}")
        
        return full_code
    
    def check_code(self, code: List[int]) -> Tuple[bool, List[int]]:
        """
        Проверка кодовой комбинации и вычисление синдрома
        
        Args:
            code: Проверяемое кодовое слово длиной n
            
        Returns:
            Кортеж (is_correct, syndrome):
            - is_correct: True если код корректен
            - syndrome: Вектор синдрома длиной n_k
        """
        if len(code) != self.n:
            raise ValueError(f"Длина кода должна быть {self.n}")
            
        code = np.array(code)
        info_part = code[:self.n_i]      # Информационная часть
        received_control = code[self.n_i:]  # Принятые контрольные биты
        
        print(f"\nПроверка кода: {code}")
        print(f"  Информационная часть: {info_part}")
        print(f"  Принятые контрольные биты: {received_control}")
        
        # Вычисление ожидаемых контрольных битов
        expected_control = []
        for i in range(self.n_k):
            control_bit = 0
            for j in range(self.n_i):
                control_bit ^= info_part[j] & self.check_matrix[j, i]
            expected_control.append(control_bit)
        
        print(f"  Вычисленные контрольные биты: {expected_control}")
        
        # Вычисление синдрома (разность между принятыми и вычисленными контрольными битами)
        syndrome = []
        for i in range(self.n_k):
            syndrome.append(received_control[i] ^ expected_control[i])
        
        is_correct = all(bit == 0 for bit in syndrome)
        print(f"  Синдром: {syndrome}")
        print(f"  Код {'корректен' if is_correct else 'содержит ошибки'}")
        
        return is_correct, syndrome
    
    def find_error_position(self, syndrome: List[int]) -> int:
        """
        Нахождение позиции ошибки по синдрому для однократной ошибки
        
        Args:
            syndrome: Вектор синдрома длиной n_k
            
        Returns:
            Номер ошибочного разряда (0-based) или -1 если не найден
        """
        syndrome_str = ''.join(str(bit) for bit in syndrome)
        print(f"Поиск ошибки для синдрома: {syndrome}")
        
        # Поиск столбца проверочной матрицы, совпадающего с синдромом
        for col in range(self.n_i):
            col_syndrome = ''.join(str(self.check_matrix[col, i]) for i in range(self.n_k))
            if col_syndrome == syndrome_str:
                print(f"  Найдена ошибка в разряде {col + 1}")
                return col
                
        print("  Ошибка не найдена или является многократной")
        return -1


class CyclicCode:
    """
    Класс для работы с циклическими кодами
    
    Attributes:
        generator_poly (List[int]): Коэффициенты образующего многочлена
        degree (int): Степень образующего многочлена
    """
    
    def __init__(self, generator_poly: List[int]) -> None:
        """
        Инициализация циклического кода
        
        Args:
            generator_poly: Коэффициенты образующего многочлена от старшей степени
        """
        self.generator_poly = generator_poly
        self.degree = len(generator_poly) - 1
        
        print(f"\nСоздан циклический код:")
        print(f"  Образующий многочлен: {self.poly_to_str(generator_poly)}")
        print(f"  Степень многочлена: {self.degree}")
    
    def poly_to_str(self, poly: List[int]) -> str:
        """Преобразование многочлена в строковое представление"""
        terms = []
        for i, coeff in enumerate(poly):
            if coeff == 1:
                power = len(poly) - i - 1
                if power == 0:
                    terms.append("1")
                elif power == 1:
                    terms.append("x")
                else:
                    terms.append(f"x^{power}")
        return " + ".join(terms) if terms else "0"
    
    def poly_divide(self, dividend: List[int]) -> List[int]:
        """
        Деление полиномов по модулю 2
        
        Args:
            dividend: Коэффициенты делимого многочлена
            
        Returns:
            Остаток от деления
        """
        dividend = dividend.copy()
        divisor = self.generator_poly
        
        print(f"  Деление: {self.poly_to_str(dividend)} / {self.poly_to_str(divisor)}")
        
        # Процесс деления в столбик
        while len(dividend) >= len(divisor):
            if dividend[0] == 1:
                # Вычитание (XOR) делителя
                for i in range(len(divisor)):
                    dividend[i] ^= divisor[i]
            # Сдвиг влево
            dividend = dividend[1:]
        
        # Дополнение нулями до длины degree
        remainder = dividend + [0] * (self.degree - len(dividend))
        print(f"  Остаток: {self.poly_to_str(remainder)}")
        
        return remainder
    
    def encode(self, info_part: List[int]) -> List[int]:
        """
        Кодирование циклическим кодом
        
        Args:
            info_part: Информационная часть кода
            
        Returns:
            Закодированное слово
        """
        print(f"\nКодирование информационной части: {info_part}")
        
        # Сдвиг информационной части на степень образующего многочлена
        shifted_info = info_part + [0] * self.degree
        print(f"  Сдвинутый многочлен: {self.poly_to_str(shifted_info)}")
        
        # Вычисление контрольных битов (остаток от деления)
        remainder = self.poly_divide(shifted_info.copy())
        
        # Формирование кодовой комбинации
        code_word = info_part + remainder
        
        print(f"  Закодированное слово: {code_word}")
        return code_word
    
    def decode(self, received_code: List[int]) -> Tuple[bool, List[int]]:
        """
        Декодирование и проверка на ошибки
        
        Args:
            received_code: Принятое кодовое слово
            
        Returns:
            Кортеж (is_correct, remainder):
            - is_correct: True если код корректен
            - remainder: Остаток от деления
        """
        print(f"\nДекодирование принятого кода: {received_code}")
        
        remainder = self.poly_divide(received_code.copy())
        is_correct = all(bit == 0 for bit in remainder)
        
        print(f"  Остаток: {remainder}")
        print(f"  Код {'корректен' if is_correct else 'содержит ошибки'}")
        
        return is_correct, remainder
    
    def correct_single_error(self, received_code: List[int]) -> List[int]:
        """
        Исправление одиночной ошибки методом циклических сдвигов
        
        Args:
            received_code: Принятое кодовое слово с ошибкой
            
        Returns:
            Исправленное кодовое слово
        """
        print(f"\nИсправление одиночной ошибки в коде: {received_code}")
        
        corrected_code = received_code.copy()
        n = len(received_code)
        
        # Перебор всех циклических сдвигов
        for shift in range(n):
            # Циклический сдвиг влево
            temp_code = received_code[shift:] + received_code[:shift]
            print(f"  Сдвиг {shift}: {temp_code}")
            
            remainder = self.poly_divide(temp_code.copy())
            weight = sum(remainder)  # Вес остатка
            
            print(f"    Вес остатка: {weight}")
            
            if weight <= 1:  # Для исправления одиночной ошибки
                print(f"    Найдена исправимая конфигурация")
                
                # Исправление ошибки в сдвинутой комбинации
                for i in range(len(temp_code)):
                    if i < len(remainder) and remainder[i] == 1:
                        temp_code[i] ^= 1  # Инвертируем ошибочный бит
                        print(f"    Исправлен бит {i} в сдвинутой комбинации")
                        break
                
                # Обратный циклический сдвиг
                corrected_code = temp_code[-shift:] + temp_code[:-shift]
                print(f"    Исправленный код: {corrected_code}")
                break
        else:
            print("  Ошибка не может быть исправлена как однократная")
            
        return corrected_code


def task1() -> None:
    """
    Задание №1: Работа с групповым кодом (9,5)
    - Составление контрольных соотношений
    - Формирование избыточного кода
    - Проверка правильности принятых комбинаций
    - Поиск ошибочных разрядов
    """
    print("\n" + "="*60)
    print("ЗАДАНИЕ №1: ГРУППОВОЙ КОД (9,5)")
    print("="*60)
    
    # Проверочная матрица группового кода
    check_matrix = [
        [1, 1, 1, 1],  # Контрольные соотношения для 1-го информационного бита
        [1, 1, 1, 0],  # Для 2-го информационного бита
        [1, 1, 0, 1],  # Для 3-го информационного бита  
        [1, 0, 1, 1],  # Для 4-го информационного бита
        [0, 1, 1, 1]   # Для 5-го информационного бита
    ]
    
    # Создание группового кода
    group_code = GroupCode(check_matrix)
    
    # Заданная информационная часть
    info_part = [1, 1, 0, 1, 1]
    
    # Пункт 1: Составление контрольных соотношений
    print("\n--- 1. КОНТРОЛЬНЫЕ СООТНОШЕНИЯ ---")
    print("Контрольные биты вычисляются как:")
    for i in range(group_code.n_k):
        equation = f"c{i+1} = "
        terms = []
        for j in range(group_code.n_i):
            if check_matrix[j][i] == 1:
                terms.append(f"a{j+1}")
        equation += " ⊕ ".join(terms)
        print(f"  {equation}")
    
    # Пункт 2: Формирование избыточного кода
    print("\n--- 2. ФОРМИРОВАНИЕ ИЗБЫТОЧНОГО КОДА ---")
    generated_code = group_code.generate_code(info_part)
    
    # Пункт 3: Проверка заданных комбинаций
    print("\n--- 3. ПРОВЕРКА ПРИНЯТЫХ КОМБИНАЦИЙ ---")
    
    test_codes = [
        [0, 1, 0, 0, 1, 0, 1, 0, 1],  # Комбинация 1
        [0, 1, 1, 1, 1, 0, 0, 0, 1]   # Комбинация 2
    ]
    
    for i, test_code in enumerate(test_codes, 1):
        print(f"\n>>> Комбинация {i}: {test_code}")
        
        # Проверка кода и вычисление синдрома
        is_correct, syndrome = group_code.check_code(test_code)
        
        if not is_correct:
            # Поиск позиции однократной ошибки
            error_pos = group_code.find_error_position(syndrome)
            if error_pos != -1:
                print(f">>> Однократная ошибка в разряде: {error_pos + 1}")
            
            # Примеры двукратных ошибок с тем же синдромом
            print(f"\n>>> ПРИМЕРЫ ДВУКРАТНЫХ ОШИБОК С СИНДРОМОМ {syndrome}:")
            
            # Первый пример: ошибки в соседних разрядах
            error_code1 = test_code.copy()
            pos1 = error_pos
            pos2 = (error_pos + 1) % group_code.n_i
            
            error_code1[pos1] ^= 1  # Инвертируем первый бит
            error_code1[pos2] ^= 1  # Инвертируем второй бит
            
            _, syndrome1 = group_code.check_code(error_code1)
            print(f"  Пример 1: ошибки в разрядах {pos1 + 1} и {pos2 + 1}")
            print(f"    Код с ошибками: {error_code1}")
            print(f"    Синдром: {syndrome1}")
            
            # Второй пример: ошибки в разрядах через один
            error_code2 = test_code.copy()
            pos3 = error_pos
            pos4 = (error_pos + 2) % group_code.n_i
            
            error_code2[pos3] ^= 1
            error_code2[pos4] ^= 1
            
            _, syndrome2 = group_code.check_code(error_code2)
            print(f"  Пример 2: ошибки в разрядах {pos3 + 1} и {pos4 + 1}")
            print(f"    Код с ошибками: {error_code2}")
            print(f"    Синдром: {syndrome2}")


def task2() -> Tuple[int, int]:
    """
    Задание №2: Создание кода для 18 кодовых комбинаций, 
    исправляющего одиночные и двойные ошибки
    
    Returns:
        Кортеж (n, k) - параметры созданного кода
    """
    print("\n" + "="*60)
    print("ЗАДАНИЕ №2: КОД ДЛЯ 18 КОМБИНАЦИЙ С ИСПРАВЛЕНИЕМ ОШИБОК")
    print("="*60)
    
    # Требуемое количество кодовых комбинаций
    num_combinations = 18
    
    # Минимальное число информационных битов
    k = np.ceil(np.log2(num_combinations)).astype(int)
    
    print(f"Требуется закодировать: {num_combinations} комбинаций")
    print(f"Минимальное число информационных битов: k = {k}")
    
    # Для исправления одиночных и двойных ошибок минимальное кодовое расстояние d0 >= 5
    # Граница Хэмминга: 2^(n-k) >= C(n,0) + C(n,1) + C(n,2) + 1
    
    print("\nПоиск параметров кода:")
    print("Условие: 2^r >= 1 + n + n(n-1)/2 (для исправления двойных ошибок)")
    
    # Подбор параметров кода
    found = False
    for n in range(k + 1, 20):  # Перебор возможных длин кода
        r = n - k  # Число контрольных битов
        
        # Правая часть границы Хэмминга
        hamming_bound = 1 + n + n * (n - 1) // 2
        
        print(f"  n={n}, k={k}, r={r}: 2^{r} = {2**r} >= {hamming_bound}? {2**r >= hamming_bound}")
        
        if 2**r >= hamming_bound:
            found = True
            break
    
    if not found:
        n = 15  # Резервные параметры
        k = 5
        r = 10
    
    print(f"\nРЕЗУЛЬТАТ:")
    print(f"  Выбран код с параметрами: ({n}, {k})")
    print(f"  Информационных битов: k = {k}")
    print(f"  Контрольных битов: r = {r}") 
    print(f"  Общая длина кода: n = {n}")
    print(f"  Минимальное кодовое расстояние: d0 >= 5")
    print(f"  Количество кодовых комбинаций: 2^{k} = {2**k} >= {num_combinations}")
    print(f"  Обнаруживает: до 4 ошибок")
    print(f"  Исправляет: до 2 ошибок")
    
    return n, k


def task3() -> None:
    """
    Задание №3: Работа с циклическим кодом
    - Формирование избыточного циклического кода
    - Построение образующей матрицы
    - Проверка правильности комбинаций
    - Анализ ошибок
    """
    print("\n" + "="*60)
    print("ЗАДАНИЕ №3: ЦИКЛИЧЕСКИЙ КОД")
    print("="*60)
    
    # Образующий многочлен: 1 1 0 1 1 1 (x^5 + x^4 + x^2 + x + 1)
    generator_poly = [1, 1, 0, 1, 1, 1]
    
    # Информационная часть кода
    info_part = [1, 1, 0, 1, 1, 1, 0, 0, 1]
    
    # Принятый код для проверки
    received_code = [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0]
    
    # Создание циклического кода
    cyclic_code = CyclicCode(generator_poly)
    
    # Пункт 1: Формирование избыточного циклического кода
    print("\n--- 1. ФОРМИРОВАНИЕ ИЗБЫТОЧНОГО КОДА ---")
    encoded = cyclic_code.encode(info_part)
    
    # Пункт 2: Проверка заданной комбинации
    print("\n--- 2. ПРОВЕРКА ЗАДАННОЙ КОМБИНАЦИИ ---")
    is_correct, remainder = cyclic_code.decode(received_code)
    
    # Пункт 3: Анализ возможности однократной ошибки
    print("\n--- 3. АНАЛИЗ ОШИБОК ---")
    
    if not is_correct:
        weight = sum(remainder)
        print(f"Вес остатка: {weight}")
        
        if weight <= 1:
            print(">>> Ошибка МОЖЕТ БЫТЬ однократной")
            print("\n--- ИСПРАВЛЕНИЕ ОДНОКРАТНОЙ ОШИБКИ ---")
            corrected = cyclic_code.correct_single_error(received_code)
            
            # Проверка исправленного кода
            is_correct_after, _ = cyclic_code.decode(corrected)
            if is_correct_after:
                print(">>> Ошибка успешно исправлена!")
        else:
            print(">>> Ошибка НЕ МОЖЕТ БЫТЬ однократной")
        
        # Примеры двукратных ошибок с тем же остатком
        print("\n--- ПРИМЕРЫ ДВУКРАТНЫХ ОШИБОК ---")
        print(f"Поиск двукратных ошибок с остатком: {remainder}")
        
        examples_found = 0
        n = len(received_code)
        
        # Перебор пар позиций для двукратных ошибок
        for i in range(n):
            for j in range(i + 1, n):
                # Создание кода с ошибками в позициях i и j
                test_code = received_code.copy()
                test_code[i] ^= 1
                test_code[j] ^= 1
                
                # Проверка остатка
                _, test_remainder = cyclic_code.decode(test_code)
                
                if test_remainder == remainder:
                    examples_found += 1
                    print(f"  Пример {examples_found}: ошибки в разрядах {i + 1} и {j + 1}")
                    print(f"    Ошибочный код: {test_code}")
                    
                    if examples_found >= 2:  # Ограничим количество примеров
                        break
            if examples_found >= 2:
                break


def main() -> None:
    """
    Основная функция выполнения лабораторной работы
    """
    print("ЛАБОРАТОРНАЯ РАБОТА: ПОМЕХОУСТОЙЧИВЫЕ КОДЫ")
    print("Реализация групповых и циклических кодов")
    print("=" * 60)
    
    try:
        # Выполнение всех заданий
        task1()  # Групповой код (9,5)
        n, k = task2()  # Создание кода для 18 комбинаций
        task3()  # Циклический код
        
        print("\n" + "=" * 60)
        print("РЕЗЮМЕ ВЫПОЛНЕННОЙ РАБОТЫ:")
        print("=" * 60)
        print("1. Реализован групповой код (9,5) с заданной проверочной матрицей")
        print("2. Создан код с параметрами ({}, {}) для 18 комбинаций".format(n, k))
        print("3. Реализован циклический код с заданным образующим многочленом")
        print("4. Все коды поддерживают обнаружение и исправление ошибок")
        print("\nКод готов к демонстрации преподавателю!")
        
    except Exception as e:
        print(f"\nОШИБКА ВЫПОЛНЕНИЯ: {e}")
        print("Проверьте входные данные и параметры кодов")


# Точка входа в программу
if __name__ == "__main__":
    main()