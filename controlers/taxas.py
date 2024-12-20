from decimal import Decimal

def calcular_taxa_publicacao(valor_produto: Decimal) -> Decimal:
    """
    Calcula a taxa para publicação de um produto com base no valor do produto.
    """
    if valor_produto <= 100:
        return Decimal("3.0")
    elif 100 < valor_produto <= 200:
        return Decimal("8.0")
    elif 200 < valor_produto <= 500:
        return Decimal("15.0")
    elif 500 < valor_produto <= 1000:
        return Decimal("25.0")
    elif 1000 < valor_produto <= 5000:
        return Decimal("40.0")
    elif 5000 < valor_produto <= 10000:
        return Decimal("100.0")
    elif 10000 < valor_produto <= 50000:
        return Decimal("300.0")
    elif 50000 < valor_produto <= 100000:
        return Decimal("500.0")
    elif 100000 < valor_produto <= 1000000:
        return Decimal("2000.0")
    elif 1000000 < valor_produto <= 10000000:
        return Decimal("5000.0")
    else:
        return Decimal("10000.0")  # Taxa fixa para valores acima de 10 milhões

def calcular_taxa_envio_dinheiro(valor_transferencia: float) -> float:
    """
    Calcula a taxa para envio de dinheiro com base no valor da transferência.
    """
    if valor_transferencia <= 100:
        return 2.0
    elif 100 < valor_transferencia <= 200:
        return 5.0
    elif 200 < valor_transferencia <= 500:
        return 10.0
    elif 500 < valor_transferencia <= 1000:
        return 20.0
    elif 1000 < valor_transferencia <= 5000:
        return 50.0
    elif 5000 < valor_transferencia <= 10000:
        return 100.0
    elif 10000 < valor_transferencia <= 50000:
        return 250.0
    elif 50000 < valor_transferencia <= 100000:
        return 500.0
    elif 100000 < valor_transferencia <= 1000000:
        return 1500.0
    elif 1000000 < valor_transferencia <= 10000000:
        return 3000.0
    else:
        return 5000.0  # Taxa fixa para valores acima de 10 milhões


def calcular_taxa_postar_status() -> float:
    """
    Retorna a taxa fixa para postar status.
    """
    return 9.0  # Taxa fixa para postar status

