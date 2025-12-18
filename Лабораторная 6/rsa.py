'''RSA — это асимметричный алгоритм шифрования, названный по первым буквам фамилий его создателей'''


import random
import math
import os

# упрощённая эмуляция PKCS#1 v1.5
def simple_pad(message: bytes, k: int) -> int:
    """Упрощённый паддинг: добавляем случайные байты спереди."""
    if len(message) > k - 10:
        raise ValueError("Сообщение слишком длинное")
    padding = os.urandom(k - len(message) - 1)  # случайные байты
    padded = b'\x00' + padding + b'\x01' + message
    return int.from_bytes(padded, 'big')

def simple_unpad(padded_int: int, k: int) -> bytes:
    padded = padded_int.to_bytes(k, 'big')
    if padded[0] != 0:
        raise ValueError("Неверный паддинг")
    idx = padded.rfind(b'\x01')
    if idx == -1:
        raise ValueError("Разделитель не найден")
    return padded[idx+1:]

def is_prime(n, k=5):
    """Тест Миллера–Рабина на простоту (вероятностный)."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Представляем n-1 как d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    """Генерирует случайное простое число заданной битности."""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # делаем нечётным и нужной длины
        if is_prime(n):
            return n

def extended_gcd(a, b):
    """Расширенный алгоритм Евклида: возвращает (g, x, y), где a*x + b*y = g = gcd(a, b)"""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1

def modinv(a, m):
    """Находит обратное a по модулю m."""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError('Обратный элемент не существует')
    return x % m

def generate_rsa_keys(bits=512):
    """Генерирует пару ключей RSA."""
    # Функция generate_prime(bits) генерирует случайное простое число длиной bits бит
    # Чтобы убедиться, что число простое, используется тест Миллера–Рабина (is_prime)
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    while p == q:
        q = generate_prime(bits // 2)

    # n это публичная часть ключа
    n = p * q
    # Вычисление функции Эйлера. это количество чисел, меньших n, взаимно простых с ним
    # Это секретное значение, нужно только для генерации ключей
    phi = (p - 1) * (q - 1)

    # Выбираем открытую экспоненту e, должно быть взаимно просто с phi
    e = 65537  # стандартное значение (2^16 + 1), простое и эффективное
    if math.gcd(e, phi) != 1:
        # Редкий случай — выберем другое небольшое простое
        e = 3
        if math.gcd(e, phi) != 1:
            e = 17

    # Обратное число к e по модулю phi. Вычисляется с помощью расширенного алгоритма Евклида
    d = modinv(e, phi)

    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key

def rsa_encrypt(message: int, public_key):
    """Шифрует целое число message с помощью открытого ключа."""
    e, n = public_key
    return pow(message, e, n)

def rsa_decrypt(ciphertext: int, private_key):
    """Расшифровывает целое число ciphertext с помощью закрытого ключа."""
    d, n = private_key
    return pow(ciphertext, d, n)


def int_to_bytes(x: int):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def bytes_to_int(b):
    return int.from_bytes(b, 'big')


if __name__ == "__main__":
    # Генерация ключей
    pub, priv = generate_rsa_keys(bits=512)  
    print("Открытый ключ (e, n):", pub)
    print("Закрытый ключ (d, n):", priv)
    k = 256

    msg = "Меня зовут Максим! Hi".encode('utf-8')
    print(f"Закодированное сообщение в байтах: {msg}")
    padded_int = simple_pad(msg, k)
    # print(f'"С солью": {padded_int}')

    msg_int = bytes_to_int(msg)
    #RSA работает только с целыми числами, а не со строками или байтами
    print(f'Байты, преобразованные в число: {msg_int}')

    if msg_int >= pub[1]:
        raise ValueError("Сообщение слишком длинное для текущего ключа")
    
    # Это зашифрованное сообщение — большое целое число, которое выглядит как случайный набор цифр
    cipher_int = rsa_encrypt(msg_int, pub)
    print(f'Зашифрованное слово {cipher_int}')
    decrypted_int = rsa_decrypt(cipher_int, priv)
    print(f'Расшифрованное слово: {decrypted_int}')
    decrypted_msg = int_to_bytes(decrypted_int).decode('utf-8')
    print(f'Восстановленное исходное сообщение: {decrypted_msg}')

    # assert message == decrypted, "Ошибка расшифровки!"
    # print("\n Шифрование/расшифрование прошло успешно!")