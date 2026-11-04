"""Download monthly market and industry returns from the Kenneth R. French Data Library.

Sources (Tuck School of Business, Dartmouth):
  F-F_Research_Data_Factors_CSV.zip        -> Mkt-RF, RF (monthly, percent)
  12_Industry_Portfolios_CSV.zip           -> value-weighted industry returns (monthly, percent)
  F-F_Research_Data_Factors_daily_CSV.zip  -> Mkt-RF, RF (daily, percent)

Usage:  python3 tools/fetch_french.py
Writes: data/french_monthly.csv  (date, mkt_rf, rf, and 12 industry returns, all in percent)
        data/french_daily.csv    (date YYYYMMDD, mkt_rf, rf, in percent)
"""
import csv
import io
import os
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
MISSING = {"-99.99", "-999"}


def download(name):
    with urllib.request.urlopen(BASE + name, timeout=60) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    member = next(n for n in z.namelist() if n.lower().endswith(".csv"))
    return z.read(member).decode("latin-1").splitlines()


def first_monthly_block(lines, key_len=6):
    """Return (header, rows) for the first table keyed by YYYYMM (or YYYYMMDD with key_len=8)."""
    header, rows = None, []
    for row in csv.reader(lines):
        cells = [c.strip() for c in row]
        if header is None:
            if len(cells) > 1 and cells[0] == "" and cells[1]:
                header = cells[1:]
            continue
        if len(cells) > 1 and len(cells[0]) == key_len and cells[0].isdigit():
            rows.append(cells)
        elif rows:
            break  # the monthly block has ended (annual block follows)
    return header, rows


def main():
    f_head, f_rows = first_monthly_block(download("F-F_Research_Data_Factors_CSV.zip"))
    i_head, i_rows = first_monthly_block(download("12_Industry_Portfolios_CSV.zip"))
    factors = {r[0]: dict(zip(f_head, r[1:])) for r in f_rows}
    out_rows = []
    for r in i_rows:
        date, vals = r[0], r[1:]
        if date not in factors or any(v in MISSING for v in vals):
            continue
        f = factors[date]
        out_rows.append([date, f["Mkt-RF"], f["RF"]] + vals)
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    path = os.path.join(ROOT, "data", "french_monthly.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "mkt_rf", "rf"] + i_head)
        w.writerows(out_rows)
    print(f"wrote data/french_monthly.csv: {len(out_rows)} months "
          f"({out_rows[0][0]}–{out_rows[-1][0]}), industries: {', '.join(i_head)}")

    d_head, d_rows = first_monthly_block(download("F-F_Research_Data_Factors_daily_CSV.zip"), 8)
    col = {name: i + 1 for i, name in enumerate(d_head)}
    daily = [[r[0], r[col["Mkt-RF"]], r[col["RF"]]] for r in d_rows
             if r[col["Mkt-RF"]] not in MISSING]
    path = os.path.join(ROOT, "data", "french_daily.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "mkt_rf", "rf"])
        w.writerows(daily)
    print(f"wrote data/french_daily.csv: {len(daily)} days ({daily[0][0]}–{daily[-1][0]})")


if __name__ == "__main__":
    main()
