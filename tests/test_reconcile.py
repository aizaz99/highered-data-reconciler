import pandas as pd
from reconcile import reconcile

def test_matching_missing_duplicates_and_differences():
    a=pd.DataFrame({'id':['001','002','003','003','004','','005'], 'status':['Y','N','A','B','Y','X','N']})
    b=pd.DataFrame({'person':['001','002','003','004','006','005'], 'state':['Y','Y','A','Y','Y','N']})
    m,s=reconcile(a,b,'id','person',[('status','state')])
    assert m['Matched IDs']==4
    assert m['IDs with differences']==1
    assert m['Field differences']==1
    assert m['Only in Source A']==0
    assert m['Only in Source B']==1
    assert m['Ambiguous duplicate IDs']==1
    assert m['Blank ID rows A']==1

def test_ignore_case():
    a=pd.DataFrame({'id':['01'],'x':['Admitted']})
    b=pd.DataFrame({'id':['01'],'x':['admitted']})
    assert reconcile(a,b,'id','id',[('x','x')],True)[0]['IDs with differences']==0
