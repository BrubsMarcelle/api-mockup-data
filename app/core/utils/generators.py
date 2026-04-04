import random

def generate_cpf() -> str:
    """Simple random CPF generator."""
    def calc_digit(digits):
        n = len(digits) + 1
        s = sum(int(d) * (n - i) for i, d in enumerate(digits))
        rem = s % 11
        return '0' if rem < 2 else str(11 - rem)

    base = [str(random.randint(0, 9)) for _ in range(9)]
    d1 = calc_digit(base)
    d2 = calc_digit(base + [d1])
    return "".join(base + [d1, d2])

def generate_cod_associado() -> str:
    """Random code for associate."""
    return f"AS-{random.randint(100000, 999999)}"
