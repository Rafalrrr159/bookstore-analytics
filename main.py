import base64, io, os, re, warnings, matplotlib.pyplot as plt, networkx as nx, pandas as pd, yaml
from datetime import datetime
from dateutil import parser

warnings.simplefilter('ignore')

tabs, panes = "", ""


def parse_smart(x, is_eu):
    try:
        dt = parser.parse(str(x).replace(',', ' ').replace(';', ' ').strip(), fuzzy=True, dayfirst=is_eu,
                          default=datetime(1000, 1, 1))
        return dt.strftime('%Y-%m-%d') if dt.year > 1980 else None
    except:
        return None


for i, d in enumerate(['DATA1', 'DATA2', 'DATA3']):
    try:
        if not os.path.exists(d): continue
        u = pd.read_csv(f'{d}/users.csv').drop_duplicates()
        o = pd.read_parquet(f'{d}/orders.parquet').drop_duplicates()
        with open(f'{d}/books.yaml', encoding='utf-8') as f:
            y = yaml.safe_load(f)
            b = pd.DataFrame(y.values() if isinstance(y, dict) else y)
            b.columns = [c.replace(':', '') for c in b.columns]

        b['aset'] = b['author'].apply(lambda x: frozenset(str(x).split(', ') if x else []))
        o['val'] = o.apply(
            lambda r: r.quantity * float(re.search(r"[\d.]+", str(r.unit_price).replace(',', '.')).group()) * (
                1.2 if '€' in str(r.unit_price) else 1) if pd.notnull(r.unit_price) else 0, axis=1)

        o['ts'] = o.timestamp.astype(str)
        is_eu = any(int(re.split(r'[/\-.]', x)[0]) > 12 for x in o.ts.head(500).tolist() if
                    re.search(r'\d+[/\-.]\d+', x) and re.split(r'[/\-.]', x)[0].isdigit())
        o['day'] = o.ts.apply(lambda x: parse_smart(x, is_eu))
        o = o.dropna(subset=['day'])

        G = nx.Graph()
        G.add_nodes_from(u.id)
        [nx.add_path(G, ids) for c in ['email', 'phone'] for _, ids in u.groupby(c)['id'] if len(ids) > 1]
        umap = {n: list(c)[0] for c in nx.connected_components(G) for n in c}
        o['rid'] = o.user_id.astype(str).map({str(k): v for k, v in umap.items()})

        top_days = o.groupby('day')['val'].sum().nlargest(5).reset_index()
        top_days.columns = ['Date', 'Revenue']

        best_real = o.groupby('rid')['val'].sum().idxmax()
        best_buy = ", ".join([str(k) for k, v in umap.items() if v == best_real])
        top_auth = ", ".join(sorted(o.merge(b, left_on='book_id', right_on='id').groupby('aset')[
                                        'quantity'].sum().idxmax())) if not o.empty else "N/A"

        plt.figure(figsize=(8, 3))
        o.groupby('day')['val'].sum().sort_index().plot(title=d)
        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png')
        b64 = base64.b64encode(img.getvalue()).decode()
        plt.close()

        act = 'active' if i == 0 else ''
        tabs += f'<li class="nav-item"><button class="nav-link {act}" data-bs-toggle="tab" data-bs-target="#{d}">{d}</button></li>'
        panes += f'''<div class="tab-pane fade show {act} p-3" id="{d}"><div class="row text-center">
        <div class="col card p-2">Users: {nx.number_connected_components(G)}</div><div class="col card p-2">Authors: {b.aset.nunique()}</div>
        <div class="col card p-2">Top: {top_auth}</div></div><div class="row mt-3"><div class="col-5">{top_days.to_html(index=False, classes='table table-sm table-striped')}
        <div class="alert alert-info mt-2"><small>Best Buyer: {best_buy}</small></div></div><div class="col-7"><img src="data:image/png;base64,{b64}" class="img-fluid"></div></div></div>'''
    except Exception as e:
        print(f"Err {d}: {e}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(f'''<!DOCTYPE html><head><title>BI Report</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>th, td {{ text-align: left !important; }}</style></head><body class="container mt-4"><h3>Bookstore BI</h3>
    <ul class="nav nav-tabs">{tabs}</ul><div class="tab-content border p-3 bg-white">{panes}</div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script></body></html>''')