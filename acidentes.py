# -*- coding: utf-8 -*-
"""
Created on Thu May  5 18:26:16 2022

@author: diogo.borges
"""
import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

# from PIL import Image
# img = Image.open(r'C:\Users\diogo.borges\Documents\Acidentes\car-crash-icon.png')


from PIL import Image
import requests
from io import BytesIO

response = requests.get('https://i.imgur.com/hPQDels.jpeg', stream=True)
img = Image.open(BytesIO(response.content))

#img.show()


st.set_page_config(layout="wide",page_title='Acidentes Lisboa 2019',page_icon=img)

url = 'https://drive.google.com/file/d/1TLKwhn7ihET-3f4L7Zokl77qlODm1GtY/view?usp=sharing'
path = 'https://drive.google.com/uc?id='+url.split('/')[-2]
@st.cache
def load_acidentes(path):
    return pd.read_csv(path)
localizacao = load_acidentes(path)
localizacao.rename(columns={'Latitude GPS':'latitude','Longitude GPS':'longitude','cluster':'Número do Ponto Negro'},inplace=True)
localizacao=localizacao[localizacao['Número do Ponto Negro']!=-1]
remap=dict(zip(np.unique(localizacao['Número do Ponto Negro']),range(1,len(np.unique(localizacao['Número do Ponto Negro']))+1)))
localizacao=localizacao.replace({"Número do Ponto Negro": remap})
#display(df)
url = 'https://drive.google.com/file/d/1MPMEP2a2rEHjhfu2nIf48srsqb2I3GCt/view?usp=sharing'
path = 'https://drive.google.com/uc?id='+url.split('/')[-2]    
@st.cache
def load_acidentes2 (path):
    df = pd.read_csv(path,index_col=0,infer_datetime_format=True,parse_dates=['Datahora'],encoding='latin1')
    return df.rename(columns={'Latitude GPS':'latitude','Longitude GPS':'longitude'})
df_acidentes = load_acidentes2(path)

#st.title("Identificação de pontos de incidência dos acidentes rodoviários e da sua correlação com outros fatores")
st.markdown("<h1 style='text-align: center; '>Identificação de pontos de incidência dos acidentes rodoviários e da sua correlação com outros fatores</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns((0.2,0.6,0.2))
with col2:
    st.write("""
             ## Identificação de Pontos Negros
             Pode clicar nos pontos para saber a que Ponto Negro pertence cada acidente.
             """)
    
    def   map_clusters (localizacao):       
        pt_inicial = localizacao['latitude'].mean(), localizacao['longitude'].mean()
        m=folium.Map(location=pt_inicial,zoom_start=12)
        folium.TileLayer('cartodbpositron').add_to(m)
        colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928',
                  '#890404','#BB5348','#8F7370','#A47245','#DBB65A','#FFD600','#CFC705','#B9CF05','#D7F44B','#75BB03','#498D38','#7EC685','#45F495','#1CEDAE','#029B84','#06FAF3','#0FA1CF','#0664C6','#02129D','#423C86','#C08CF4','#C647D6','#ED04BA','#F45DBC','#9B4B6A','#DB5A79','#FA0421','#CF9199',
                  'aqua','silver','lime','tomato','olive','yellow','lawngreen','darkgreen','lightseagreen','teal','steelblue','blue','deeppink','crimson','pink']
        for i in range(0,len(localizacao)):
            colouridx = localizacao['Número do Ponto Negro'].iloc[i]
            if colouridx == -1:
                pass
            else:
                col = colors[colouridx%len(colors)]
                folium.CircleMarker([localizacao['latitude'].iloc[i],localizacao['longitude'].iloc[i]],popup="Ponto Negro "+str(colouridx), radius = 2, color = col, fill = col).add_to(m)
        
        return folium_static(m)
    
    map_clusters (localizacao)
    black_spot_number = st.number_input('Se quiser ver em detalhe algum dos pontos negros digite o seu número:',max_value = max(localizacao['Número do Ponto Negro']),step=1,format='%i')
    
    merged_df = pd.merge(localizacao[localizacao['Número do Ponto Negro']==black_spot_number][['IdAcidente','Número do Ponto Negro']],df_acidentes,on='IdAcidente',how='inner')
    st.write(merged_df.set_index('IdAcidente').sort_values(by='Datahora'))
    
    
    st.write(""" ## Identificação de Pontos Negros tendo em conta fatores
             """)
    
    # @st.cache
    # def load_distances(path):
    #     df_distances = pd.read_csv(path,sep=';',decimal=',',usecols=[1, 5],encoding='latin1')
    #     separa=df_distances['Name'].str.split(' - ', expand=True)
        
    #     df_distances['IdOrigem'],df_distances['IdDestino']=separa[0], separa[1]
    #     df_distances.drop('Name',axis=1,inplace=True)
    #     df_distances.rename(columns = {'Total_Length':'Distancia'}, inplace = True)
    #     df_distances['IdOrigem'],df_distances['IdDestino']=df_distances['IdOrigem'].astype('int64'),df_distances['IdDestino'].astype('int64')
    #     return df_distances
    # df_distances = load_distances(r'C:\Users\diogo.borges\Documents\Acidentes\distances.txt')
    url = 'https://drive.google.com/file/d/13iSF0l3u1rCHjBv9HsWJrBn81tKFApjS/view?usp=sharing'
    path = 'https://drive.google.com/uc?id='+url.split('/')[-2]
    @st.cache
    def load_distances (path):
        return pd.read_csv(path)
    df_distances = load_distances (path)
    
    #@st.cache
    def filtra_acidentes (column,value):
        #column = 'Natureza'
        #value = 'Colisão com fuga'
        filt_acidentes=df_acidentes[(df_acidentes[column]==value)&(df_acidentes['latitude'].notnull())].copy()
        list_id=filt_acidentes['IdAcidente']
        #filt_distances = df_distances[(df_distances.IdOrigem.isin(list_id))&(df_distances.IdDestino.isin(list_id))]
        #matriz = pd.pivot_table(filt_distances,values='Distancia',index=['IdOrigem'],columns=['IdDestino'])
        matriz = pd.pivot_table(df_distances,values='Distancia',index=['IdOrigem'],columns=['IdDestino'])
        matriz=matriz.filter(items=list_id.to_list(), axis=1)
        matriz=matriz.filter(items=list_id.to_list(), axis=0)
        if matriz.empty or matriz.isnull().all().all():
            st.write( 'Não existe nenhum ponto negro com %s = %s' % (column,value))
            #print('Não existe nenhum ponto negro com %s = %s' % (column,value))
        else:
            v_max = round(np.max(np.max(matriz)))+100
            for i in list_id.to_list():
                if i not in matriz.columns:
                    matriz[i]=v_max
                    matriz.loc[i]=v_max
            
            matriz.fillna(v_max,inplace=True)
            
            #DBSCAN
            eps=100 #metros
            n=5 #minimo de acidentes
            dbscan = DBSCAN(eps=eps,min_samples=n,metric='precomputed')
            labels=dbscan.fit_predict(matriz.values)
            if len(np.unique(labels))-1 > 0:
                st.write('Existem %d pontos negros com %s = %s' % (len(np.unique(labels))-1,column,value))
                blackspot_df = pd.DataFrame.from_dict(dict(zip(matriz.index,labels)),columns=['Número do Ponto Negro'],orient='index').reset_index().rename(columns={'index':'IdAcidente'})   
                filt_acidentes = pd.merge(filt_acidentes,blackspot_df,on='IdAcidente',how='inner')
                #filt_acidentes['Número do Ponto Negro']=labels
                st.write(filt_acidentes[filt_acidentes['Número do Ponto Negro']!=-1].set_index('IdAcidente').sort_values(by=['Número do Ponto Negro','Datahora']))
                return map_clusters(filt_acidentes)
            else:
                st.write( 'Não existe nenhum ponto negro com %s = %s' % (column,value) )
    
    factor_columns = ['','Natureza','Inclinação do Traçado','Berma do Traçado','Localização do Traçado','Estado Conservação',
                      'Marca Via','Obstáculos','Sinais','Sinais Luminosos','Factores Atmosféricos','Luminosidade',
                      'Periodo','Hora','Dia da Semana','Mês','Automóvel ligeiro','Automóvel pesado',
                      'Motociclos/Ciclomotores','Outros Veículos','Velocípedes','Peões'] + [c for c in df_acidentes.columns if 'Inf/Ação' in c]       
    make_choice = st.selectbox('Selecione um fator:', factor_columns,index=0)  
    if make_choice:
        choose_value = st.radio(f'Selecione um valor para o/a {make_choice}:',sorted(df_acidentes[make_choice].unique()))
        filtra_acidentes (make_choice,choose_value)
    else:
        st.write('Ainda não foi selecionada nenhuma opção')

