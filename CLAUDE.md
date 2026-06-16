# Focus BCB — Briefing do Projeto

## Objetivo

Baixar automaticamente toda segunda-feira o Boletim Focus do Banco Central do Brasil (PDF), extrair o texto e gerar um resumo executivo em markdown.

## Fonte

- Página oficial: https://www.bcb.gov.br/publicacoes/focus
- Padrão de URL do PDF: `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`
  - Exemplo: `https://www.bcb.gov.br/content/focus/focus/R20240101.pdf`

## Convenções de Nomenclatura e Estrutura

- Arquivos nomeados com o padrão `focus_AAAA-MM-DD` (data da publicação do boletim)
- `data/` — armazena os PDFs baixados e os textos extraídos (`.txt`)
- `output/focus/` — armazena os resumos executivos gerados (`.md`)

## Estrutura de Pastas

```
.
├── src/                  # Código-fonte principal
├── tests/                # Testes automatizados
├── data/                 # PDFs e textos extraídos
├── output/
│   └── focus/            # Resumos em markdown
└── .github/
    └── workflows/        # CI/CD e automação semanal
```

## Regras de Negócio

1. **Nunca inventar números** — toda mediana ou estatística citada no resumo deve estar presente no texto extraído do PDF. Sem inferências ou aproximações.
2. **Feriados** — quando a segunda-feira for feriado, o BCB publica o Focus na terça-feira (ou dia útil seguinte). O download deve retroceder dia a dia a partir da segunda até encontrar um PDF disponível.
3. **Frequência** — download toda segunda-feira; o boletim é referente à semana anterior.

## Fluxo Esperado

1. Identificar a data de publicação (segunda-feira, ou próximo dia útil após feriado)
2. Montar a URL com o padrão `R{AAAAMMDD}.pdf` e tentar o download
3. Se o PDF não existir (HTTP 404), retroceder um dia e tentar novamente
4. Salvar o PDF em `data/focus_AAAA-MM-DD.pdf`
5. Extrair o texto e salvar em `data/focus_AAAA-MM-DD.txt`
6. Gerar o resumo executivo e salvar em `output/focus/focus_AAAA-MM-DD.md`
