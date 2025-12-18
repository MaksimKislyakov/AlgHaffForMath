import random
import math

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
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    while p == q:
        q = generate_prime(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    # Выбираем открытую экспоненту e
    e = 65537  # стандартное значение (2^16 + 1), простое и эффективное
    if math.gcd(e, phi) != 1:
        # Редкий случай — выберем другое небольшое простое
        e = 3
        if math.gcd(e, phi) != 1:
            e = 17

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

# === Пример использования ===
if __name__ == "__main__":
    # Генерация ключей
    pub, priv = generate_rsa_keys(bits=128)  # 128 бит — только для демонстрации!
    print("Открытый ключ (e, n):", pub)
    print("Закрытый ключ (d, n):", priv)

    # Сообщение — должно быть целым числом < n
    message = 42
    print(f"\nИсходное сообщение: {message}")

    # Шифрование
    ciphertext = rsa_encrypt(message, pub)
    print(f"Шифротекст: {ciphertext}")

    # Расшифрование
    decrypted = rsa_decrypt(ciphertext, priv)
    print(f"Расшифровано: {decrypted}")

    assert message == decrypted, "Ошибка расшифровки!"
    print("\n✅ Шифрование/расшифрование прошло успешно!")