"""Baixa o Boletim Focus mais recente do Banco Central do Brasil."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import requests

# User-Agent de navegador para evitar bloqueio pelo servidor do BCB
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

_URL_TEMPLATE = "https://www.bcb.gov.br/content/focus/focus/R{data}.pdf"

# Cobre até uma semana de feriados consecutivos
_MAX_TENTATIVAS = 7


def ultima_segunda(hoje: date) -> date:
    """Retorna a segunda-feira mais recente estritamente anterior a `hoje`.

    Se `hoje` já for segunda-feira, retrocede para a segunda da semana passada.
    """
    # Recua pelo menos um dia; continua até encontrar uma segunda (weekday == 0)
    candidata = hoje - timedelta(days=1)
    while candidata.weekday() != 0:
        candidata -= timedelta(days=1)
    return candidata


def baixar(dest: str | Path) -> tuple[date, Path]:
    """Baixa o PDF mais recente do Focus e salva em `dest`.

    Parte da última segunda-feira e recua dia a dia até _MAX_TENTATIVAS,
    cobrindo feriados em que o BCB publica na terça ou dia útil seguinte.
    Valida que o conteúdo recebido é um PDF real antes de salvar.

    Retorna (data_da_publicacao, caminho_do_arquivo).
    Levanta RuntimeError se nenhuma tentativa encontrar o PDF.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    data_tentativa = ultima_segunda(date.today())

    for _ in range(_MAX_TENTATIVAS):
        url = _URL_TEMPLATE.format(data=data_tentativa.strftime("%Y%m%d"))

        resposta = requests.get(url, headers=_HEADERS, timeout=30)

        # Aceita somente HTTP 200 com conteúdo que começa com a assinatura PDF
        if resposta.status_code == 200 and resposta.content[:4] == b"%PDF":
            nome = f"focus_{data_tentativa.isoformat()}.pdf"
            caminho = dest / nome
            caminho.write_bytes(resposta.content)
            return data_tentativa, caminho

        # PDF não disponível nesta data; recua um dia e tenta novamente
        data_tentativa -= timedelta(days=1)

    raise RuntimeError(
        f"Nenhum PDF do Focus encontrado após {_MAX_TENTATIVAS} tentativas."
    )


def main() -> None:
    """Baixa o Focus para data/ e exibe caminho e tamanho em KB."""
    pasta = Path(__file__).parent.parent / "data"
    data_pub, caminho = baixar(pasta)
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Publicado em : {data_pub.isoformat()}")
    print(f"Arquivo      : {caminho}")
    print(f"Tamanho      : {tamanho_kb:.1f} KB")


if __name__ == "__main__":
    main()
