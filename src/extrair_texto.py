"""Extrai o texto de um PDF do Focus e salva como arquivo .txt."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pdfplumber


def extrair(pdf_path: str | Path) -> Path:
    """Abre o PDF com pdfplumber, une o texto de todas as páginas e salva como .txt (UTF-8).

    Retorna o caminho do arquivo .txt gerado.
    """
    pdf_path = Path(pdf_path)
    txt_path = pdf_path.with_suffix(".txt")

    paginas: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                paginas.append(texto)

    # Une as páginas com linha em branco para preservar a separação visual
    txt_path.write_text("\n\n".join(paginas), encoding="utf-8")
    return txt_path


def main() -> None:
    """Interface de linha de comando para extração de texto."""
    parser = argparse.ArgumentParser(
        description="Extrai o texto de um PDF do Focus e salva como .txt."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=None,
        help="Caminho para um PDF específico. Se omitido, usa o mais recente em data/.",
    )
    args = parser.parse_args()

    if args.pdf:
        pdf_path = args.pdf
    else:
        # Busca todos os PDFs do Focus em data/ e ordena pelo nome
        # Como o nome segue o padrão focus_AAAA-MM-DD.pdf (ISO 8601),
        # a ordenação alfabética é equivalente à cronológica
        pasta_data = Path(__file__).parent.parent / "data"
        pdfs = sorted(pasta_data.glob("focus_*.pdf"))

        if not pdfs:
            print(
                "Erro: nenhum PDF encontrado em data/. "
                "Execute src/baixar_focus.py primeiro.",
                file=sys.stderr,
            )
            sys.exit(1)

        # O último da lista ordenada é o mais recente
        pdf_path = pdfs[-1]

    txt_path = extrair(pdf_path)
    print(f"Texto extraído : {txt_path}")
    print(f"Tamanho        : {txt_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
