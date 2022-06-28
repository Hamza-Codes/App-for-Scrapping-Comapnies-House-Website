
#from crypt import methods
from re import X
from bs4 import BeautifulSoup
import requests
import pandas as pd


from flask import Flask,redirect,url_for,render_template,request,render_template_string

def check_next_account(rq):
    sp = BeautifulSoup(rq.content, 'html.parser')
    X=sp.find_all('p')
    for x in X:
        if x.text.__contains__('Next accounts made up to'):
            return x.strong.text
    return 'no'
        
def check_last_account(rq):
    sp = BeautifulSoup(rq.content, 'html.parser')
    X=sp.find_all('p')
    for x in X:
        if x.text.__contains__('Last accounts made up to'):
            return x.strong.text
    return 'no'
        

def make_request(url):
    req = requests.get(url)
    
    soup = BeautifulSoup(req.content, 'html.parser')
    lst=[l.split(',') for l in soup.text.split("\r\n")]
    for l in lst:
        while len(l)>11:
            l[10]=l[10]+','+l[11]
            l.pop()
    df = pd.DataFrame(lst[1:], columns =lst[0])
    return df
    

def get_companies(name='',address='',day_from='',month_from='',year_from='',day_to='',month_to='',year_to='',sic=''):
    url='https://find-and-update.company-information.service.gov.uk/advanced-search/download?companyNameIncludes={}&companyNameExcludes=&registeredOfficeAddress={}&incorporationFromDay={}&incorporationFromMonth={}&incorporationFromYear={}&incorporationToDay={}&incorporationToMonth={}&incorporationToYear={}&sicCodes={}&dissolvedFromDay=&dissolvedFromMonth=&dissolvedFromYear=&dissolvedToDay=&dissolvedToMonth=&dissolvedToYear='.format(name,address,day_from,month_from,year_from,day_to,month_to,year_to,sic)
    
    return make_request(url)
    

app=Flask(__name__, template_folder='templates')
@app.route('/',methods=['POST','GET'])
def home():
    if request.method=='GET':
        return render_template('index.html')  
    else:
        name=request.form['name']
        address=request.form['address']
        from_date=request.form['from_date']
        to_Date=request.form['to_Date']
        sic=request.form['sic']
        lst_account=request.form['lst_account']
        nxt_account=request.form['nxt_account']
        df=get_companies(name,address,from_date[8:],from_date[5:7],from_date[0:4],to_Date[8:],to_Date[5:7],to_Date[0:4],sic)

        
        
        if lst_account!='':
            df['last_account']=''
            c=0
            for i in df['company_number']:
                url='https://find-and-update.company-information.service.gov.uk/company/{}'.format(i)
                req = requests.get(url)
                if req.status_code == 200:
                    y=check_last_account(req)
                    if y!='no':
                        df.loc[c,'last_account']=y
                c+=1
            df['last_account']=df['last_account'].str.lower()
            lst_account=lst_account.lower()
            df=df[ df['last_account'].str.contains(lst_account)==True]



        if nxt_account!='':
            df['next_account']=''

            c=0
            for i in df['company_number']:
                url='https://find-and-update.company-information.service.gov.uk/company/{}'.format(i)
                req = requests.get(url)
                if req.status_code == 200:
                    x=check_next_account(req)
                    if x!='no':
                        df.loc[c,'next_account']=x
                c+=1
            df['next_account']=df['next_account'].str.lower()
            nxt_account=nxt_account.lower()
            df=df[ df['next_account'].str.contains(nxt_account)==True]


        return render_template('simple.html',  tables=[df.to_html(classes='data',formatters={'url':lambda x:f'<a href="{x}">{x}</a>'})], titles=df.columns.values)
        

    
if __name__ =='main':
    app.run(debug=True)