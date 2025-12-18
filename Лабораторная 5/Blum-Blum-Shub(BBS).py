def bbs_generator(seed, p, q, num_bits):
    M = p * q
    x = (seed * seed) % M
    bits = []
    for _ in range(num_bits):
        x = (x * x) % M
        bits.append(x & 1)  # младший бит
    return bits

# Выбор безопасных простых p и q: p ≡ q ≡ 3 (mod 4)
p = 7  # 7 % 4 = 3
q = 11 # 11 % 4 = 3
seed = 5  # должен быть взаимно прост с M = p*q

bits = bbs_generator(seed, p, q, 20)
print("Сгенерированные биты:", bits)