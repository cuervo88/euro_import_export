import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
iso_to_name = json.load(open("iso_to_name.json","r"))
iso_to_iso = json.load(open("iso_to_iso.json","r"))
iso_eu = json.load(open("iso_eu.json","r"))
euro_map = json.load(open("europe.json","r"))

mydb = mysql.connector.connect(
    host="database-1.cwmqo7r4n6wf.us-east-1.rds.amazonaws.com",
    user="tester",
    password="tester_pass",
    database="eurostat"
)
def map_year_imp_exp(year):
    mycursor = mydb.cursor()
    mycursor.execute("""
    SELECT iso2, flow , sum(value_"""+year+""") as sum_ 
    FROM full_"""+year+"""
    where product_nc = "TOTAL"
    group by iso2, flow;
    """)
    data = mycursor.fetchall()
    df = pd.DataFrame(data, columns=['iso2','flow','sum_'])
    return df
def total_trade_per_country(year):
    mycursor = mydb.cursor()
    mycursor.execute("""select iso2,partner_iso2, flow, sum(value_"""+year+""") as sum_
    from full_"""+year+"""
    where product_nc = "TOTAL"
    group by iso2, partner_iso2, flow""")
    data = mycursor.fetchall()
    df = pd.DataFrame(data, columns=["iso2","partner_iso2","flow","sum"])
    return df
def product_year_country(year,country):
    mycursor = mydb.cursor()
    mycursor.execute("""
    SELECT iso2,partner_iso2,SUBSTR( product_nc, 1, 2 ),SUBSTR( product_nc, 1, 4 ),product_nc,flow,sum(value_"""+year+""") as sum_ 
    FROM full_"""+year+"""
    Where product_nc != "TOTAL" and iso2 = '"""+country+"""' AND product_nc not like '%SS%'
    group by iso2, partner_iso2,flow, product_nc
    """)
    data = mycursor.fetchall()
    df = pd.DataFrame(data, columns=['iso2','partner_iso2','product_nc2','product_nc4','product_nc8','flow','sum'])
    return df

def product_year_country_10(year,country,flow1):
    if flow1 == "imp":
        flow1="1"
    elif flow1 =="exp":
        flow1="2"
    mycursor = mydb.cursor()
    mycursor.execute("""
    SELECT iso2,SUBSTR( product_nc, 1, 2 ) as nc_2,sum(value_"""+year+""") as sum_ 
    FROM full_"""+year+"""
    Where product_nc != "TOTAL" and iso2 = '"""+country+"""' AND product_nc not like '%SS%' and flow = """+flow1+"""
    group by iso2, nc_2
    order by sum_ desc
    limit 10;
    """)
    data = mycursor.fetchall()
    df = pd.DataFrame(data, columns=['iso2','product_nc2','sum'])
    return df

def all_countries_10(year,flow):
    df3 = pd.DataFrame()
    mydb = mysql.connector.connect(
      host="database-1.cwmqo7r4n6wf.us-east-1.rds.amazonaws.com",
      user="tester",
      password="tester_pass",
      database="eurostat"
    )
    mycursor = mydb.cursor()
    mycursor.execute("""
    SELECT iso2
    from full_"""+year+"""
    group by iso2
    """)
    data = mycursor.fetchall()
    df = pd.DataFrame(data, columns=['iso2'])
    for i in df["iso2"]:
        df2 = pd.DataFrame()
        df2 = product_year_country_10(year,str(i),flow)
        df3 = df3.append(df2)
    return df3

def top_products(year,country):
    df = product_year_country(year,country)
    df_exp = df[df['flow']=='2']
    df_imp = df[df['flow']=='1']
    p= df_imp.groupby('product_nc2').sum().sort_values('sum',ascending=False)[0:5]
    p.reset_index(inplace=True)
    a2 = list(p['product_nc2'])
    q = df_imp.groupby('product_nc4').sum().sort_values('sum',ascending=False)
    q.reset_index(inplace=True)
    a1 = list(q[q.product_nc4.str.startswith(tuple(a2))]['product_nc4'])
    df_imp_select = df_imp.loc[df_imp['product_nc4'].isin(a1)]
    p= df_exp.groupby('product_nc2').sum().sort_values('sum',ascending=False)[0:5]
    p.reset_index(inplace=True)
    a2 = list(p['product_nc2'])
    q = df_exp.groupby('product_nc4').sum().sort_values('sum',ascending=False)
    q.reset_index(inplace=True)
    a1 = list(q[q.product_nc4.str.startswith(tuple(a2))]['product_nc4'])
    df_exp_select = df_exp.loc[df_exp['product_nc4'].isin(a1)]
    return df_imp_select,df_exp_select

def build_hierarchical_dataframe(df):
    levels = ['product_nc8', 'product_nc4', 'product_nc2'] # levels used for the hierarchical chart
    value_column = 'sum'
    df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value'])
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value'])
        dfg = df.groupby(levels[i:]).sum()
        dfg = dfg.reset_index()
        df_tree['id'] = dfg[level].copy()
        if i < len(levels) - 1:
            df_tree['parent'] = dfg[levels[i+1]].copy()
        else:
            df_tree['parent'] = ''
        df_tree['value'] = dfg[value_column]
#        df_tree['color'] = dfg[level].astype(int)/ dfg[color_columns[1]]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)
    total = pd.Series(dict(id='', parent='',
                              value=df[value_column].sum()))
    df_all_trees = df_all_trees.append(total, ignore_index=True)
#    df_all_trees['name'] = df_all_trees['id'].apply(lambda x:product[x])
    return df_all_trees