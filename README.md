# Same Pizza, Different Slices?

Code and data for the paper **"Same Pizza, Different Slices? Putting the No-Tax Assumption of Modigliani–Miller Proposition I on Trial"**
(Lao Xiusheng, Xu Riqi, Wu Kaluk, Jiang Yumeng, Li Jiabao and Li Jingwen; Group D.E. Show&Tell, MH6806 Principles of Finance and Risk Management, Nanyang Technological University, 2026).

The paper relaxes the no-tax assumption of Modigliani–Miller Proposition I and asks whether the interest tax shield turns debt into a free lunch. This repository reproduces every number, table and figure in it.

## Quick start

```bash
pip install -r requirements.txt
jupyter notebook mm_on_trial_report.ipynb      # runs in about 30 seconds using cached results
```

Set `RECOMPUTE = True` in the first code cell to rerun the two slow simulations from scratch (about 2 minutes in total). All random seeds are fixed, so reruns give the same results. The scripts can also be run on their own, in this order:

```bash
python exp1.py            # Section 5.1  -> exp1.json
python tables.py          # Tables 3, C1-C3 -> tcja.json, appC.json (needs exp1.json)
python calib2.py          # Section 6.3, Table 4 -> calib_out.json
python figs.py            # Figures 1, 2, 3 and C1 -> fig/
python fig_firms.py       # Figure E1 -> fig/
python extras.py          # numbers quoted in the text -> extras.json
python independent_check.py
```

The cached `.json` files were produced with Python 3.13, NumPy 2.5 and SciPy 1.18; rerunning with NumPy 1.21 and SciPy 1.7 gives the same numbers to at least 12 significant digits.

## Where each result comes from

| Paper | Content | Code |
|---|---|---|
| Section 3, Table 1, Figure 1a, Eqs. (2)–(4) | Two-state model: benchmark, tax shield, debt capacity *D\** | `model.py`: `gain_fixed`, `d_star_two_state`; `figs.py` |
| Sections 3.3–3.4 | Money-machine trade with taxes; CAPM beta, WACC and VaR reading of the base case | `extras.py` |
| Section 4.1, Figure 2 | One-parameter-at-a-time sensitivity; distress-cost thresholds | `model.py`, `figs.py`, `extras.py` |
| Section 4.2, Figure 1b–c | Lognormal cash flow: interior optimum and default probability | `model.py`: `lognormal_draws`; `figs.py`; checked by `independent_check.py` |
| Section 5.1, Figure C1, Tables C1–C2 | Market-priced (break-even) risky debt | `model.py`: `market_face`, `gain_market`; `exp1.py` → `exp1.json`; `tables.py` → `appC.json` |
| Section 5.2, Figure 3a, Table C3 | Usable share of the shield: loss years and a 30%-of-EBIT interest cap | `model.py`: `usable_share`; `tables.py` → `appC.json` |
| Section 5.3, Table 2, Eq. (5) | Personal taxes (Miller, 1977) | `model.py`: `miller_tstar` |
| Section 5.4, Figure 3b, Table C4, Eqs. (6)–(7) | Multi-period (perpetual) debt | `model.py`: `shield_pv_maturity`, `multi_period_gain` |
| Sections 6.1–6.2, Table 3 | US TCJA and Singapore in the multi-period model | `model.py`: `multi_period_sim`; `tables.py` → `tcja.json`; `extras.py` |
| Section 6.3, Table 4, Figure E1 | Calibration to Singapore Airlines and Sheng Siong | `calib2.py` → `calib_out.json`; `extras.py`; `fig_firms.py`; data in `firms.json` |

Figures are written to `fig/` as PDF (used in the paper) and PNG (shown in the notebook), named after their number in the paper: `fig1_value`, `fig2_sensitivity`, `fig3_shield_multiperiod`, `figC1_market_debt`, `figE1_firms`.

## Files

- `mm_on_trial_report.ipynb`: runs everything in the order of the paper, with outputs saved.
- `model.py`: the model (one-period two-state firm, lognormal and normal cash flows, market-priced debt, usable shield, Miller's T\*, multi-period trade-off).
- `exp1.py`, `tables.py`, `calib2.py`: scripts for the slower results; their outputs are cached as `.json` files.
- `extras.py`: numbers quoted in the text that no table shows (writes `extras.json`).
- `independent_check.py`: re-derives the base results without `model.py`, valuing the lognormal case by numerical integration instead of simulation.
- `figs.py`: Figures 1, 2, 3 and C1; `fig_firms.py`: Figure E1; `style.py`: shared figure style.
- `firms.json`: annual operating profit, interest expense, debt, cash and revenue (S$ million) for Singapore Airlines (FY2009/10–FY2024/25) and Sheng Siong Group (2013–2024).

## Data sources

Firm data were taken from the companies' full-year results announcements filed on SGX: Singapore Airlines Ltd, full-year financial results FY2009/10–FY2024/25, and Sheng Siong Group Ltd, full-year results announcements FY2014–FY2024 (2013 figures from the comparatives in the FY2014 announcement). SIA's debt includes lease liabilities from FY2019/20 (IFRS 16). Sheng Siong had no bank debt; its only borrowing was a S$30 million government term loan in 2020–21, and its interest is lease interest only. All other parameters are illustrative assumptions stated in Appendix A of the paper.

## Requirements

Python 3.9 or later with NumPy, SciPy, pandas and Matplotlib (see `requirements.txt`).
