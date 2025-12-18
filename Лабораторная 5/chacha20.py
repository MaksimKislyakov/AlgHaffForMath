'''
ChaCha20 — это потоковый шифр, который можно использовать как криптографически стойкий генератор случайных чисел (CSPRNG).
Он берёт секретный ключ, одноразовый номер (nonce) и счётчик, 
и превращает их в очень длинную последовательность псевдослучайных байтов.
'''


import os
import time
import hashlib


def rotl32(v, n):
    """32-битный циклический сдвиг влево."""
    return ((v << n) & 0xFFFFFFFF) | (v >> (32 - n))

def chacha20_block(key, counter, nonce):
    """Генерирует один блок (64 байта) ChaCha20."""
    # Константа "expand 32-byte k"
    # массив из 16 чисел по 32 бита — это внутреннее состояние алгоритма
    state = [
        0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
        *key,               # 8 x 32-bit words = 256-bit key
        counter,            # 1 x 32-bit word
        *nonce              # 3 x 32-bit words = 96-bit nonce
    ]  # Итого: 16 слов

    # Работаем с копией состояния
    x = state[:]

    # 10 раундов ChaCha (каждый раунд = 4 quarter-rounds)
    # ChaCha20 делает 20 раундов перемешивания
    # Каждая операция — это комбинация из трёх действий:
    
    # Сложение по модулю 2³² → a = (a + b) & 0xFFFFFFFF
    # XOR → c = c ^ a
    # Циклический сдвиг влево → rotl32(value, n)
    for _ in range(10):
        # Сначала — 4 колонки (column rounds)
        x[0] = (x[0] + x[4]) & 0xFFFFFFFF; x[12] = rotl32(x[12] ^ x[0], 16)
        x[8] = (x[8] + x[12]) & 0xFFFFFFFF; x[4] = rotl32(x[4] ^ x[8], 12)
        x[0] = (x[0] + x[4]) & 0xFFFFFFFF; x[12] = rotl32(x[12] ^ x[0], 8)
        x[8] = (x[8] + x[12]) & 0xFFFFFFFF; x[4] = rotl32(x[4] ^ x[8], 7)

        x[1] = (x[1] + x[5]) & 0xFFFFFFFF; x[13] = rotl32(x[13] ^ x[1], 16)
        x[9] = (x[9] + x[13]) & 0xFFFFFFFF; x[5] = rotl32(x[5] ^ x[9], 12)
        x[1] = (x[1] + x[5]) & 0xFFFFFFFF; x[13] = rotl32(x[13] ^ x[1], 8)
        x[9] = (x[9] + x[13]) & 0xFFFFFFFF; x[5] = rotl32(x[5] ^ x[9], 7)

        x[2] = (x[2] + x[6]) & 0xFFFFFFFF; x[14] = rotl32(x[14] ^ x[2], 16)
        x[10] = (x[10] + x[14]) & 0xFFFFFFFF; x[6] = rotl32(x[6] ^ x[10], 12)
        x[2] = (x[2] + x[6]) & 0xFFFFFFFF; x[14] = rotl32(x[14] ^ x[2], 8)
        x[10] = (x[10] + x[14]) & 0xFFFFFFFF; x[6] = rotl32(x[6] ^ x[10], 7)

        x[3] = (x[3] + x[7]) & 0xFFFFFFFF; x[15] = rotl32(x[15] ^ x[3], 16)
        x[11] = (x[11] + x[15]) & 0xFFFFFFFF; x[7] = rotl32(x[7] ^ x[11], 12)
        x[3] = (x[3] + x[7]) & 0xFFFFFFFF; x[15] = rotl32(x[15] ^ x[3], 8)
        x[11] = (x[11] + x[15]) & 0xFFFFFFFF; x[7] = rotl32(x[7] ^ x[11], 7)

        # Потом — 4 диагонали
        x[0] = (x[0] + x[5]) & 0xFFFFFFFF; x[15] = rotl32(x[15] ^ x[0], 16)
        x[10] = (x[10] + x[15]) & 0xFFFFFFFF; x[5] = rotl32(x[5] ^ x[10], 12)
        x[0] = (x[0] + x[5]) & 0xFFFFFFFF; x[15] = rotl32(x[15] ^ x[0], 8)
        x[10] = (x[10] + x[15]) & 0xFFFFFFFF; x[5] = rotl32(x[5] ^ x[10], 7)

        x[1] = (x[1] + x[6]) & 0xFFFFFFFF; x[12] = rotl32(x[12] ^ x[1], 16)
        x[11] = (x[11] + x[12]) & 0xFFFFFFFF; x[6] = rotl32(x[6] ^ x[11], 12)
        x[1] = (x[1] + x[6]) & 0xFFFFFFFF; x[12] = rotl32(x[12] ^ x[1], 8)
        x[11] = (x[11] + x[12]) & 0xFFFFFFFF; x[6] = rotl32(x[6] ^ x[11], 7)

        x[2] = (x[2] + x[7]) & 0xFFFFFFFF; x[13] = rotl32(x[13] ^ x[2], 16)
        x[8] = (x[8] + x[13]) & 0xFFFFFFFF; x[7] = rotl32(x[7] ^ x[8], 12)
        x[2] = (x[2] + x[7]) & 0xFFFFFFFF; x[13] = rotl32(x[13] ^ x[2], 8)
        x[8] = (x[8] + x[13]) & 0xFFFFFFFF; x[7] = rotl32(x[7] ^ x[8], 7)

        x[3] = (x[3] + x[4]) & 0xFFFFFFFF; x[14] = rotl32(x[14] ^ x[3], 16)
        x[9] = (x[9] + x[14]) & 0xFFFFFFFF; x[4] = rotl32(x[4] ^ x[9], 12)
        x[3] = (x[3] + x[4]) & 0xFFFFFFFF; x[14] = rotl32(x[14] ^ x[3], 8)
        x[9] = (x[9] + x[14]) & 0xFFFFFFFF; x[4] = rotl32(x[4] ^ x[9], 7)

    # После всех раундов делается финальное сложение
    out = [(x[i] + state[i]) & 0xFFFFFFFF for i in range(16)]

    # Результат — 16 чисел по 4 байта. Их нужно превратить в байтовую строку:
    block = b''
    for word in out:
        # Little-endian: младший байт идёт первым. Это часть стандарта ChaCha20
        block += word.to_bytes(4, 'little')
    return block

class ChaCha20RNG:
    '''Использование алгоритма, чтобы можно было генерировать не только по 64 байта, а например 4'''
    def __init__(self, key: bytes, nonce: bytes = b'\x00' * 12):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes (96 bits)")
        self.key = [int.from_bytes(key[i:i+4], 'little') for i in range(0, 32, 4)]
        self.nonce = [int.from_bytes(nonce[i:i+4], 'little') for i in range(0, 12, 4)]
        self.counter = 0
        self.buffer = b''
        self.pos = 0

    def _refill(self):
        block = chacha20_block(self.key, self.counter, self.nonce)
        self.buffer = block
        self.pos = 0
        self.counter = (self.counter + 1) & 0xFFFFFFFF

    def read(self, n: int) -> bytes:
        result = b''
        while len(result) < n:
            if self.pos >= len(self.buffer):
                self._refill()
            need = min(n - len(result), len(self.buffer) - self.pos)
            result += self.buffer[self.pos:self.pos + need]
            self.pos += need
        return result

    def rand32(self) -> int:
        """Возвращает одно 32-битное случайное число."""
        return int.from_bytes(self.read(4), 'little')

if __name__ == "__main__":
    input_data = f"{time.time()}_{os.getpid()}".encode('utf-8')
    key = hashlib.sha256(input_data).digest()
    rng = ChaCha20RNG(key)

    print("Случайные числа от ChaCha20:")
    for _ in range(10):
        print(rng.rand32())