import matplotlib.pyplot as plt

# Линейный конгруэнтный генератор (LCG)
def lcg(seed=1, a=1664525, c=1013904223, m=2**32):
    while True:
        seed = (a * seed + c) % m
        yield seed / m  # нормализуем в [0, 1)

# Генерация N чисел
N = 10_000
rng = lcg(seed=12345)
data = [next(rng) for _ in range(N)]

# Проверка качества: гистограмма
plt.hist(data, bins=50, density=True, alpha=0.7, color='blue')
plt.title("Гистограмма псевдослучайных чисел (LCG)")
plt.xlabel("Значение")
plt.ylabel("Плотность")
plt.axhline(1, color='red', linestyle='--', label='Идеальная равномерность')
plt.legend()
plt.show()

# Простая статистика
print(f"Среднее: {sum(data)/N:.4f} (ожидаемо ~0.5)")
print(f"Дисперсия: {sum((x - 0.5)**2 for x in data)/N:.4f} (ожидаемо ~1/12 ≈ 0.0833)")