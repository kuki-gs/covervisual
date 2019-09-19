#!/usr/bin/env python
# coding: utf-8

# In[50]:


#-*- coding:utf-8 -*-
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium import plugins


# In[75]:


filename=u'宁波移动开通站点0917.xlsx'

dataset = pd.read_excel(filename,encoding="gbk")
dataset = dataset[['基站名','经度','纬度']]
dataset = dataset.dropna(subset=['经度','纬度']).reset_index().drop(['index'],axis=1)


# In[76]:


def get_convexhull(point_list):

    # 逆时针
    def ccw(points):
        return (points[1][0] - points[0][0]) * (points[2][1] - points[0][1]) > (points[1][1] - points[0][1]) * (points[2][0] - points[0][0])

    n = len(point_list) 
    point_list.sort() 

    #Valid Check:
    if n < 3:
        return None


    upper_hull = point_list[0:1]
    for i in range(2, n):
        upper_hull.append(point_list[i])
        while len(upper_hull) >= 3 and  not ccw(upper_hull[-3:]):
            del upper_hull[-2]


    lower_hull = [point_list[-1], point_list[-2]]
    for i in range(n - 3, -1, -1):  
        lower_hull.append(point_list[i])
        while len(lower_hull) >= 3 and  not ccw(lower_hull[-3:]):
            del lower_hull[-2]

    upper_hull.extend(lower_hull[1:-1])
    if len(upper_hull)<3:
        return None
    else:
        return upper_hull

def dist(a, b):
    return math.sqrt((a[1]-b[1])**2 + (a[2]-b[2])**2)

def DBSCAN(dataset, e, Minpts):
    D = [(i,dataset['经度'].iloc[i],dataset['纬度'].iloc[i]) for i in range(0, dataset.shape[0])]
    T = set(); k = 0; C = []; P = set(D)
    for d in D:
        if len([ i for i in D if dist(d, i) <= e]) >= Minpts:
            T.add(d)
    while len(T):
        P_old = P
        o = list(T)[np.random.randint(0, len(T))]
        Q = []; Q.append(o)
        P = P - set(o)
        while len(Q):
            q = Q[0]
            Q.remove(q)
            Nq = [i for i in D if dist(q, i) <= e]
            if len(Nq) >= Minpts:
                S = P & set(Nq)
                Q += (list(S))
                P = P - S
            
        k += 1
        Ck = list(P_old - P)
        T = T - set(Ck)
        C.append(Ck)

    cluster_dict={}
    for cluster in range(0,len(C)):
        for c in C[cluster]:
            cluster_dict[c[0]]=cluster    
    y_pred = [-1 if i not in cluster_dict else cluster_dict[i] for i in range(dataset.shape[0])]
    return y_pred


# In[77]:


y_pred = DBSCAN(dataset, 0.008, 6)
print(max(y_pred))
dataset = pd.concat([dataset, pd.DataFrame(y_pred, columns=['cluster'])],axis=1)


# In[78]:


map_nb = folium.Map(location=[29.8196,121.53321],
                    zoom_start=10,
                    tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                    attr='&copy; <a href="http://ditu.amap.com/">高德地图</a>')


# In[79]:


list_cluster = dataset['cluster'].drop_duplicates().values.tolist()


# In[80]:


#cols=['red','blue','green','purple','orange']
for cluster in list_cluster:
    data_cluster = dataset[dataset['cluster']==cluster]
    list_point = data_cluster[['纬度','经度']].values.tolist()
    for point in list_point: 
        folium.Circle(point,radius=400,color='#3388ff',opacity=0,fill=True,fill_opacity=0.2).add_to(map_nb)
    if cluster!=-1:
        ch = get_convexhull(list_point)
        #poly_m=[[i[1],i[0]] for i in ch]
        if ch!=None:
            ch = ch + [ch[0]]
            folium.PolyLine(locations=ch,
                            color='pink').add_to(map_nb)    


# In[81]:


map_nb.save('5G.html')


# In[ ]:




