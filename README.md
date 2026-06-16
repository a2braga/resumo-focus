# Focus BCB Pipeline

Pipeline que baixa semanalmente o Boletim Focus do Banco Central do Brasil,
extrai o texto e — numa automação agendada separada — envia um resumo executivo
como rascunho de e-mail no Gmail para revisão humana antes do envio.

## Como funciona

```
PDF (BCB) ──► src/baixar_focus.py ──► data/focus_AAAA-MM-DD.pdf
                                              │
                                   src/extrair_texto.py
                                              │
                                   data/focus_AAAA-MM-DD.txt
                                              │
                                   agente de resumo (LLM)
                                              │
                                   output/focus/focus_AAAA-MM-DD.md
                                              │
                                   rascunho no Gmail (para revisão)
```

Os scripts Python fazem apenas download e extração de texto.
O resumo executivo é gerado por um agente que lê o `.txt` extraído —
nenhum número é inventado; toda mediana citada precisa estar no texto original.

## Estrutura de pastas

```
.
├── src/
│   ├── baixar_focus.py      # download do PDF
│   └── extrair_texto.py     # extração de texto
├── tests/
│   └── test_baixar_focus.py
├── data/                    # PDFs e textos (gerados, não versionados)
├── output/
│   └── focus/               # resumos em markdown (versionados)
├── .github/
│   └── workflows/
│       └── focus-download.yml
├── demo.py                  # roda o pipeline localmente
├── requirements.txt
├── pytest.ini
└── CLAUDE.md
```

## Como rodar localmente

```bash
pip install -r requirements.txt
python demo.py          # baixa e extrai
python demo.py --abrir  # idem, abre o .txt no navegador ao final
```

## Como rodar os testes

```bash
# testes offline (rápidos, sem rede)
pytest -m "not network"

# todos os testes, incluindo download real
pytest
```

## Agendamento

O GitHub Action em `.github/workflows/focus-download.yml` roda toda segunda-feira
às 9h15 BRT (12h15 UTC) e commita os arquivos gerados de volta ao repositório.
Quando segunda é feriado, o script recua dia a dia até encontrar o PDF disponível.
