class SimpleMT:
    def __init__(self, seed=5489):
        self.N = 624
        self.M = 397
        self.MATRIX_A = 0x9908B0DF
        self.state = [0] * self.N
        self.index = self.N

        # Инициализация (упрощённая)
        self.state[0] = seed & 0xFFFFFFFF
        for i in range(1, self.N):
            self.state[i] = (1812433253 * (self.state[i-1] ^ (self.state[i-1] >> 30)) + i) & 0xFFFFFFFF

    def _twist(self):
        for i in range(self.N):
            x = (self.state[i] & 0x80000000) + (self.state[(i+1) % self.N] & 0x7FFFFFFF)
            xA = x >> 1
            if x % 2:
                xA ^= self.MATRIX_A
            self.state[i] = self.state[(i + self.M) % self.N] ^ xA
        self.index = 0

    def rand(self):
        if self.index >= self.N:
            self._twist()

        y = self.state[self.index]
        self.index += 1

        # Темперирование (улучшает статистику)
        y ^= (y >> 11)
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= (y >> 18)

        return y & 0xFFFFFFFF

# Пример использования
mt = SimpleMT(seed=12345)
print([mt.rand() % 100 for _ in range(10)])  # 10 случайных чисел от 0 до 99
