"""Testes para src/gerar_resumo.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gerar_resumo import gerar


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEXTO_FAKE = """\
Boletim Focus — Relatório de Mercado
Data: 2026-06-09

IPCA
Mediana 2026: 5,00%
Mediana 2027: 4,00%

Selic
Mediana 2026: 14,75%
"""

_RESUMO_FAKE = "# Resumo Focus 2026-06-09\n\nIPCA mediana 2026: 5,00%."


# ---------------------------------------------------------------------------
# Testes unitários (sem rede / sem API real)
# ---------------------------------------------------------------------------


def _mock_anthropic(resumo: str = _RESUMO_FAKE):
    """Retorna um patch que intercepta anthropic.Anthropic e devolve resumo fake."""
    content_block = MagicMock()
    content_block.text = resumo

    mensagem_mock = MagicMock()
    mensagem_mock.content = [content_block]

    cliente_mock = MagicMock()
    cliente_mock.messages.create.return_value = mensagem_mock

    return patch("gerar_resumo.anthropic.Anthropic", return_value=cliente_mock)


def test_gerar_cria_arquivo_md(tmp_path, monkeypatch):
    """gerar() deve criar o arquivo .md em output/focus/ dentro da raiz."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    # Cria estrutura data/ com um .txt fake
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    txt_path = data_dir / "focus_2026-06-09.txt"
    txt_path.write_text(_TEXTO_FAKE, encoding="utf-8")

    with _mock_anthropic():
        md_path = gerar(txt_path)

    assert md_path.exists()
    assert md_path.suffix == ".md"
    assert md_path.name == "focus_2026-06-09.md"
    assert md_path.parent == tmp_path / "output" / "focus"


def test_gerar_conteudo_correto(tmp_path, monkeypatch):
    """O conteúdo do .md deve ser exatamente o retorno da API."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    txt_path = data_dir / "focus_2026-06-09.txt"
    txt_path.write_text(_TEXTO_FAKE, encoding="utf-8")

    with _mock_anthropic(_RESUMO_FAKE):
        md_path = gerar(txt_path)

    assert md_path.read_text(encoding="utf-8") == _RESUMO_FAKE


def test_gerar_passa_texto_para_api(tmp_path, monkeypatch):
    """O texto do .txt deve ser incluído na mensagem enviada à API."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    txt_path = data_dir / "focus_2026-06-09.txt"
    txt_path.write_text(_TEXTO_FAKE, encoding="utf-8")

    content_block = MagicMock()
    content_block.text = _RESUMO_FAKE
    mensagem_mock = MagicMock()
    mensagem_mock.content = [content_block]
    cliente_mock = MagicMock()
    cliente_mock.messages.create.return_value = mensagem_mock

    with patch("gerar_resumo.anthropic.Anthropic", return_value=cliente_mock):
        gerar(txt_path)

    call_kwargs = cliente_mock.messages.create.call_args
    # O texto do Focus deve aparecer no conteúdo da mensagem do usuário
    mensagens = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
    usuario_content = next(m["content"] for m in mensagens if m["role"] == "user")
    assert "IPCA" in usuario_content
    assert "Selic" in usuario_content


def test_gerar_sem_api_key_levanta_erro(tmp_path, monkeypatch):
    """Sem ANTHROPIC_API_KEY no ambiente, a chamada deve falhar."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    txt_path = data_dir / "focus_2026-06-09.txt"
    txt_path.write_text(_TEXTO_FAKE, encoding="utf-8")

    with pytest.raises((KeyError, Exception)):
        gerar(txt_path)


# ---------------------------------------------------------------------------
# Teste com API real
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_gerar_resumo_real(tmp_path):
    """Chama a API do Claude com texto real e valida o markdown gerado."""
    import os

    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY não configurada")

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    txt_path = data_dir / "focus_2026-06-09.txt"
    txt_path.write_text(_TEXTO_FAKE, encoding="utf-8")

    md_path = gerar(txt_path)

    assert md_path.exists()
    conteudo = md_path.read_text(encoding="utf-8")
    # Resumo real deve ter pelo menos um título markdown
    assert "#" in conteudo
    assert len(conteudo) > 100
