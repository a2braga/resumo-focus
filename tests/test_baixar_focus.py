"""Testes para src/baixar_focus.py."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Adiciona src/ ao path, igual ao demo.py
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from baixar_focus import baixar, ultima_segunda


# ---------------------------------------------------------------------------
# Testes puros (sem rede) para ultima_segunda
# ---------------------------------------------------------------------------


def test_ultima_segunda_quinta():
    """Quinta-feira 2026-06-11 deve retornar segunda 2026-06-08."""
    quinta = date(2026, 6, 11)  # quinta-feira
    assert ultima_segunda(quinta) == date(2026, 6, 8)


def test_ultima_segunda_terca():
    """Terça-feira 2026-06-09 deve retornar a segunda do dia anterior."""
    terca = date(2026, 6, 9)  # terça-feira
    assert ultima_segunda(terca) == date(2026, 6, 8)


def test_ultima_segunda_quando_hoje_e_segunda():
    """Se a data de entrada for uma segunda, deve recuar para a semana passada."""
    segunda = date(2026, 6, 15)  # segunda-feira
    esperado = date(2026, 6, 8)  # segunda da semana anterior
    assert ultima_segunda(segunda) == esperado


def test_ultima_segunda_domingo():
    """Domingo 2026-06-14 deve retornar a segunda seis dias antes."""
    domingo = date(2026, 6, 14)  # domingo
    assert ultima_segunda(domingo) == date(2026, 6, 8)


def test_ultima_segunda_varredura_60_dias():
    """Para qualquer dia num intervalo de 60 dias, o retorno deve ser
    uma segunda-feira estritamente anterior à data fornecida."""
    inicio = date(2026, 6, 1)
    for i in range(60):
        hoje = inicio + timedelta(days=i)
        resultado = ultima_segunda(hoje)
        # Deve ser uma segunda-feira (weekday == 0)
        assert resultado.weekday() == 0, f"{hoje}: retornou {resultado} (não é segunda)"
        # Deve ser estritamente anterior à data de entrada
        assert resultado < hoje, f"{hoje}: retornou {resultado} (não é anterior)"


# ---------------------------------------------------------------------------
# Teste com rede real
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_baixar_pdf_real(tmp_path):
    """Baixa o Focus mais recente e valida o arquivo resultante."""
    data_pub, caminho = baixar(tmp_path)

    # Arquivo deve ter sido criado em disco
    assert caminho.exists()

    # Primeiros 4 bytes devem conter a assinatura de PDF
    assert caminho.read_bytes()[:4] == b"%PDF"

    # Boletins reais têm centenas de KB; rejeita respostas-lixo pequenas
    assert caminho.stat().st_size > 50 * 1024

    # Nome do arquivo deve corresponder à data de publicação
    assert caminho.name == f"focus_{data_pub.isoformat()}.pdf"

    # Data não pode estar no futuro nem mais de 14 dias no passado
    hoje = date.today()
    assert data_pub <= hoje
    assert (hoje - data_pub).days <= 14
