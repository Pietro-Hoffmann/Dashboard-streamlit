# Weather Analytics Dashboard

Multi-page Streamlit dashboard exploring a year of real meteorological data from the
**INMET** automated station B825 (Porto Alegre – Belém Novo), covering May to October 2025.

## Pages

| Page | What it covers |
|---|---|
| Principal | Overview and headline indicators for the period |
| Análise Temperatura | Temperature curves, ranges and extremes |
| Precipitação / Umidade | Rainfall accumulation against relative humidity |
| Análise Ventos | Wind speed, gusts and direction distribution |
| Análise Geral | Cross-variable comparisons |
| Dados Detalhados | The underlying records, filterable |

## Stack

**Python** · **Streamlit** · **Pandas** — loading is centralised in `utils/carrega_dados.py`
and cached, so switching pages doesn't re-read the CSV.

## Running locally

```bash
pip install -r requirements.txt
streamlit run "01_🏠_Principal.py"
```

## Data

Public historical series published by INMET (Instituto Nacional de Meteorologia),
included in `dataset/`.

> Built for a data programming course.
