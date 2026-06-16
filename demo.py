"""Pipeline local: baixa o Focus do BCB e extrai o texto."""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

# Adiciona src/ ao path para que as importações funcionem sem instalar o pacote
sys.path.insert(0, str(Path(__file__).parent / "src"))

from baixar_focus import baixar
from extrair_texto import extrair


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baixa o Focus do BCB e extrai o texto."
    )
    parser.add_argument(
        "--abrir",
        action="store_true",
        help="Abre o .txt gerado no navegador padrão ao final.",
    )
    args = parser.parse_args()

    pasta_data = Path(__file__).parent / "data"

    # Passo 1: baixar o PDF mais recente
    data_pub, pdf_path = baixar(pasta_data)
    tamanho_kb = pdf_path.stat().st_size / 1024
    print(f"[1/2] PDF baixado: {pdf_path.name} ({tamanho_kb:.1f} KB)")

    # Passo 2: extrair o texto do PDF
    txt_path = extrair(pdf_path)
    print(f"[2/2] Texto extraído: {txt_path}")

    # Abre o .txt no navegador se a flag --abrir foi passada
    if args.abrir:
        webbrowser.open(txt_path.resolve().as_uri())


if __name__ == "__main__":
    main()
