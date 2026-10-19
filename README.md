# Same Pizza, Different Slices?

Code and data for the paper **"Same Pizza, Different Slices? Putting the No-Tax Assumption of Modigliani–Miller Proposition I on Trial"**
(Lao Xiusheng, Xu Riqi, Wu Kaluk, Jiang Yumeng, Li Jiabao and Li Jingwen; Group D.E. Show&Tell, MH6806 Principles of Finance and Risk Management, Nanyang Technological University, 2026).

The paper relaxes the no-tax assumption of Modigliani–Miller Proposition I and asks whether the interest tax shield turns debt into a free lunch. This repository reproduces every number, table and figure in it.

## Quick start

```bash
pip install -r requirements.txt
jupyter notebook mm_on_trial_report.ipynb      # runs in about 20 seconds using cached results
```

Set `RECOMPUTE = True` in the first code cell to rerun the two slow simulations from scratch (about 5 minutes in total). All random seeds are fixed, so reruns give the same results.

## Where each result comes from

| Paper | Content | Code |
|---|---|---|
| Section 3, Table 1, Figure 1, Eqs. (2)–(4) | Two-state model: benchmark, tax shield, debt capacity *D\** | `model.py`: `gain_fixed`, `d_star_two_state`; `figs.py` |
| Section 4.1, Figure 2 | One-parameter-at-a-time sensitivity | `model.py`, `figs.py` |
| Section 4.2, Figure 3 | Lognormal cash flow: interior optimum and default probability | `model.py`: `lognormal_draws`, `figs.py` |
| Section 5.1, Figure 4, Tables C1–C2 | Market-priced (break-even) risky debt | `model.py`: `market_face`, `gain_market`; `exp1.py` → `exp1.json` |
| Section 5.2, Figure 5a, Table C3 | Usable share of the shield: loss years and a 30%-of-EBIT interest cap | `model.py`: `usable_share` |
| Section 5.3, Table 2, Eq. (5) | Personal taxes (Miller, 1977) | `model.py`: `miller_tstar` |
| Section 5.4, Figure 5b, Table C4, Eqs. (6)–(7) | Multi-period (perpetual) debt | `model.py`: `shield_pv_maturity`, `multi_period_gain` |
| Sections 6.1–6.2, Table 3 | US TCJA and Singapore in the multi-period model | `model.py`: `multi_period_sim`; `tables.py` → `tcja.json`, `appC.json` |
| Section 6.3, Table 4, Figure 6 | Calibration to Singapore Airlines and Sheng Siong | `calib2.py` → `calib_out.json`; `fig5.py`; data in `firms.json` |

Figures are written to `fig/` as `fig1_two_state.png` … `fig6_firms.png`, numbered as in the paper.

## Files

- `mm_on_trial_report.ipynb`: runs everything in the order of the paper, with outputs saved.
- `model.py`: the model (one-period two-state firm, lognormal and normal cash flows, market-priced debt, usable shield, Miller's T\*, multi-period trade-off).
- `exp1.py`, `tables.py`, `calib2.py`: scripts for the slower results; their outputs are cached as `.json` files.
- `figs.py`: Figures 1–5; `fig5.py`: Figure 6.
- `firms.json`: annual operating profit, interest expense, debt, cash and revenue (S$ million) for Singapore Airlines (FY2009/10–FY2024/25) and Sheng Siong Group (2013–2024).

## Data sources

Firm data were taken from the companies' full-year results announcements filed on SGX: Singapore Airlines Ltd, full-year financial results FY2009/10–FY2024/25, and Sheng Siong Group Ltd, full-year results announcements FY2014–FY2024. SIA's debt includes lease liabilities from FY2019/20 (IFRS 16); Sheng Siong's interest is lease interest only. All other parameters are illustrative assumptions stated in Appendix A of the paper.

## Requirements

Python 3.9 or later with NumPy, SciPy, pandas and Matplotlib (see `requirements.txt`).
