"""Pure reconciliation functions; no network or Streamlit dependency."""
import io
import pandas as pd


def load_table(upload):
    name = upload.name.lower()
    if name.endswith('.csv'):
        df = pd.read_csv(upload, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    elif name.endswith('.xlsx'):
        df = pd.read_excel(upload, dtype=str, keep_default_na=False, engine='openpyxl')
    else:
        raise ValueError('Upload a CSV or XLSX file.')
    df.columns = [str(c).strip() for c in df.columns]
    if len(df.columns) != len(set(df.columns)):
        raise ValueError('Duplicate column headers are not supported.')
    for c in df.columns:
        df[c] = df[c].fillna('').astype(str).str.strip()
    return df


def reconcile(a, b, key_a, key_b, field_pairs, ignore_case=False):
    if not field_pairs:
        raise ValueError('Choose at least one field to compare.')
    if not key_a or not key_b:
        raise ValueError('Choose an ID column in each source.')
    if len({x for x, _ in field_pairs}) != len(field_pairs) or len({y for _, y in field_pairs}) != len(field_pairs):
        raise ValueError('Comparison columns must be mapped one-to-one.')
    a = a.copy(); b = b.copy()
    for frame, key in ((a,key_a),(b,key_b)):
        frame[key] = frame[key].fillna('').astype(str).str.strip()
    blank_a = a[a[key_a] == ''].copy()
    blank_b = b[b[key_b] == ''].copy()
    a = a[a[key_a] != ''].copy(); b = b[b[key_b] != ''].copy()
    dup_a = a[a.duplicated(key_a, keep=False)].copy()
    dup_b = b[b.duplicated(key_b, keep=False)].copy()
    ambiguous = set(dup_a[key_a]) | set(dup_b[key_b])
    a = a[~a[key_a].isin(ambiguous)].copy()
    b = b[~b[key_b].isin(ambiguous)].copy()
    a_ids = set(a[key_a]); b_ids = set(b[key_b])
    only_a = a[a[key_a].isin(a_ids - b_ids)].copy()
    only_b = b[b[key_b].isin(b_ids - a_ids)].copy()
    matched_ids = sorted(a_ids & b_ids)
    ai = a.set_index(key_a); bi = b.set_index(key_b)
    differences = []
    mismatch_ids = set()
    for ident in matched_ids:
        for fa, fb in field_pairs:
            va, vb = ai.at[ident,fa], bi.at[ident,fb]
            ca, cb = (va.casefold(),vb.casefold()) if ignore_case else (va,vb)
            if ca != cb:
                mismatch_ids.add(ident)
                differences.append({'Record ID':ident,'Source A Column':fa,'Source B Column':fb,
                                    'Source A Value':va,'Source B Value':vb})
    diff = pd.DataFrame(differences,columns=['Record ID','Source A Column','Source B Column','Source A Value','Source B Value'])
    metrics = {'Matched IDs':len(matched_ids),'Matching IDs':len(matched_ids)-len(mismatch_ids),
               'IDs with differences':len(mismatch_ids),'Field differences':len(diff),
               'Only in Source A':len(only_a),'Only in Source B':len(only_b),
               'Ambiguous duplicate IDs':len(ambiguous),'Duplicate rows A':len(dup_a),
               'Duplicate rows B':len(dup_b),'Blank ID rows A':len(blank_a),'Blank ID rows B':len(blank_b)}
    summary = pd.DataFrame(metrics.items(),columns=['Metric','Count'])
    return metrics, {'Summary':summary,'Differences':diff,'Only in A':only_a,'Only in B':only_b,
                     'Duplicates A':dup_a,'Duplicates B':dup_b,'Blank IDs A':blank_a,'Blank IDs B':blank_b}


def to_excel(sheets):
    output = io.BytesIO()
    with pd.ExcelWriter(output,engine='openpyxl') as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer,index=False,sheet_name=name)
            ws = writer.sheets[name]
            ws.freeze_panes = 'A2'
            ws.auto_filter.ref = ws.dimensions
            for column in ws.columns:
                letter = column[0].column_letter
                max_width = max((len(str(cell.value)) for cell in list(column)[:200] if cell.value is not None),default=10)
                ws.column_dimensions[letter].width = min(max(max_width+2,12),50)
    return output.getvalue()
