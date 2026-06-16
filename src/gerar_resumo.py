"""Gera resumo executivo em markdown a partir do texto extraído do Focus."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import anthropic

_MODELO = "claude-sonnet-4-6"

_PROMPT_SISTEMA = """\
Você é um economista sênior especializado em política monetária brasileira.
Sua tarefa é produzir um resumo executivo do Boletim Focus do Banco Central do Brasil.

Regras obrigatórias:
1. NUNCA invente números — cite apenas medianas e estatísticas presentes no texto.
2. Use markdown limpo: títulos (#, ##), listas com marcadores e negrito para destaques.
3. O resumo deve ter as seções: Visão Geral, Indicadores Principais, Destaques e Tendências.
4. Seja objetivo e conciso — máximo de 600 palavras.
5. Escreva em português do Brasil.
"""

_PROMPT_USUARIO = """\
Gere o resumo executivo do Boletim Focus abaixo:

---
{texto}
---
"""


def gerar(txt_path: str | Path) -> Path:
    """Lê o arquivo .txt, chama a API do Claude e salva o resumo em output/focus/.

    Retorna o caminho do arquivo .md gerado.
    """
    txt_path = Path(txt_path)
    texto = txt_path.read_text(encoding="utf-8")

    # Monta o caminho de saída espelhando o nome do arquivo de entrada
    nome_base = txt_path.stem  # ex.: focus_2024-06-10
    raiz = txt_path.parent.parent
    saida_dir = raiz / "output" / "focus"
    saida_dir.mkdir(parents=True, exist_ok=True)
    md_path = saida_dir / f"{nome_base}.md"

    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    mensagem = cliente.messages.create(
        model=_MODELO,
        max_tokens=1024,
        system=_PROMPT_SISTEMA,
        messages=[
            {"role": "user", "content": _PROMPT_USUARIO.format(texto=texto)},
        ],
    )

    resumo = mensagem.content[0].text
    md_path.write_text(resumo, encoding="utf-8")
    return md_path


def main() -> None:
    """Interface de linha de comando para geração de resumo."""
    parser = argparse.ArgumentParser(
        description="Gera resumo executivo do Focus em markdown via Claude API."
    )
    parser.add_argument(
        "--txt",
        type=Path,
        default=None,
        help="Caminho para um .txt específico. Se omitido, usa o mais recente em data/.",
    )
    args = parser.parse_args()

    if args.txt:
        txt_path = args.txt
    else:
        pasta_data = Path(__file__).parent.parent / "data"
        txts = sorted(pasta_data.glob("focus_*.txt"))

        if not txts:
            print(
                "Erro: nenhum .txt encontrado em data/. "
                "Execute src/extrair_texto.py primeiro.",
                file=sys.stderr,
            )
            sys.exit(1)

        txt_path = txts[-1]

    md_path = gerar(txt_path)
    print(f"Resumo gerado : {md_path}")
    print(f"Tamanho       : {md_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
