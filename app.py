import streamlit as st
from reconcile import load_table, reconcile, to_excel

st.set_page_config(page_title='HigherEd Data Reconciler',page_icon='🎓',layout='wide')
st.title('🎓 HigherEd Data Reconciler')
st.caption('Compare Excel and CSV exports from CRM, SIS, and other systems.')
st.warning('Public demo: upload synthetic or non-sensitive files only. Hosted uploads are processed on the server. For restricted student data, run locally with institutional approval.')
with st.expander('How it works',expanded=False):
    st.markdown('1. Upload Source A and B (.csv or .xlsx).  2. Choose each file’s record ID.  3. Map columns to compare.  4. Run reconciliation and export the report. Duplicate IDs are flagged and excluded from matching.')
ca,cb=st.columns(2)
with ca: file_a=st.file_uploader('Source A',type=['csv','xlsx'],key='a')
with cb: file_b=st.file_uploader('Source B',type=['csv','xlsx'],key='b')
if not (file_a and file_b):
    st.info('Start by uploading two files. Synthetic example workbooks are included in the GitHub repository under sample_data/.')
    st.stop()
try:
    a=load_table(file_a);b=load_table(file_b)
except Exception as exc:
    st.error(f'Unable to read uploaded file: {exc}');st.stop()
st.subheader('1. Select record identifiers')
ca,cb=st.columns(2)
with ca: key_a=st.selectbox('Source A ID',list(a.columns))
with cb: key_b=st.selectbox('Source B ID',list(b.columns),index=list(b.columns).index(key_a) if key_a in b.columns else 0)
st.subheader('2. Map fields')
a_fields=[c for c in a.columns if c!=key_a]
b_fields=[c for c in b.columns if c!=key_b]
if not a_fields or not b_fields:
    st.error('Each file needs at least one non-ID column.');st.stop()
common=[c for c in a_fields if c in b_fields]
default_n=min(len(common),5)
num=st.number_input('Number of fields to compare',min_value=1,max_value=min(len(a_fields),len(b_fields)),value=max(1,default_n))
pairs=[]
for i in range(int(num)):
    c1,c2=st.columns(2)
    with c1: fa=st.selectbox(f'Source A field {i+1}',a_fields,index=min(i,len(a_fields)-1),key=f'fa{i}')
    with c2: fb=st.selectbox(f'Source B field {i+1}',b_fields,index=b_fields.index(fa) if fa in b_fields else min(i,len(b_fields)-1),key=f'fb{i}')
    pairs.append((fa,fb))
ignore_case=st.checkbox('Ignore capitalization differences (not whitespace within values)',value=False)
if st.button('Run reconciliation',type='primary'):
    try:
        metrics,sheets=reconcile(a,b,key_a,key_b,pairs,ignore_case)
    except Exception as exc:
        st.error(str(exc));st.stop()
    st.session_state['result']=(metrics,sheets)
if 'result' not in st.session_state:
    st.stop()
metrics,sheets=st.session_state['result']
st.subheader('3. Results')
c1,c2,c3,c4=st.columns(4)
c1.metric('Matched IDs',metrics['Matched IDs'])
c2.metric('IDs with differences',metrics['IDs with differences'])
c3.metric('Field differences',metrics['Field differences'])
c4.metric('Mismatch rate',f"{metrics['IDs with differences']/metrics['Matched IDs']:.1%}" if metrics['Matched IDs'] else 'N/A')
st.caption(f"Only A: {metrics['Only in Source A']} · Only B: {metrics['Only in Source B']} · Duplicate IDs requiring review: {metrics['Ambiguous duplicate IDs']} · Blank IDs: {metrics['Blank ID rows A']} / {metrics['Blank ID rows B']}")
with st.expander('View discrepancy rows',expanded=True):
    st.dataframe(sheets['Differences'],hide_index=True,use_container_width=True)
with st.expander('Review duplicate and missing IDs'):
    for title in ['Only in A','Only in B','Duplicates A','Duplicates B','Blank IDs A','Blank IDs B']:
        st.markdown(f'**{title}**');st.dataframe(sheets[title],hide_index=True,use_container_width=True)
st.download_button('⬇️ Download Excel report',data=to_excel(sheets),file_name='highered_reconciliation_report.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
st.caption('Comparison is exact after trimming outer whitespace, unless case-insensitive mode is enabled. No automatic term or audience-rule normalization.')
