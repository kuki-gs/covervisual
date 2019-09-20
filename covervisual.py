# -*- coding: utf-8 -*-
import math
import numpy as np
import pandas as pd
import folium

class covervisual(object):
    def __init__(self, location=[29.8196,121.53321]):
        self.basemap=folium.Map(location=location,
                                zoom_start=10,
                                tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                                attr='&copy; <a href="http://ditu.amap.com/">高德地图</a>')
        self.basemap.add_child(folium.LatLngPopup())
        self.basemap.add_child(folium.LayerControl())
    
    def get_convexhull(self,point_list):
    
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
        
    def dist(self,a, b):
        return math.sqrt((a[1]-b[1])**2 + (a[2]-b[2])**2)
        
    def DBSCAN(self,dataset, e=0.008, Minpts=6):
        D = [(i,dataset['经度'].iloc[i],dataset['纬度'].iloc[i]) for i in range(0, dataset.shape[0])]
        T = set(); k = 0; C = []; P = set(D)
        for d in D:
            if len([ i for i in D if self.dist(d, i) <= e]) >= Minpts:
                T.add(d)
        while len(T):
            P_old = P
            o = list(T)[np.random.randint(0, len(T))]
            Q = []; Q.append(o)
            P = P - set(o)
            while len(Q):
                q = Q[0]
                Q.remove(q)
                Nq = [i for i in D if self.dist(q, i) <= e]
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
        
    def plotpoint(self,point,radius=100,color='#3388ff'):
        self.basemap.add_child(folium.Circle(point,radius,color,opacity=0,fill=True,fill_opacity=0.6))
    
    def plotpoints(self,list_point,radius=100,color='#3388ff'):
        for point in list_point: 
            self.plotpoint(point,radius,color)
            
    def plotpoints_df(self,dataset,radius=100,color='#3388ff'):
        list_point = dataset[['纬度','经度']].values.tolist()
        self.plotpoints(list_point,radius,color)
            
    def plotpolygon(self,poly,color='red'):
        if len(poly)<3:
            return
        if poly[0]!=poly[-1]:
            poly = poly + [poly[0]]
        self.basemap.add_child(folium.PolyLine(locations=poly,color=color))
        
    def plotmarker(self,point,color='red',popup=''):
        self.basemap.add_child(folium.PolyLine(locations=list_point,color=color))
        self.basemap.add_child(folium.Marker(point,color,popup))
        
    def plotconvexhull(self,list_point,color='red'):
        ch = self.get_convexhull(list_point)
        if ch!=None:
            self.plotpolygon(ch,color)
        
    def plotdbscan(self,dataset,color='red',e=0.008, Minpts=6):
        y_pred = self.DBSCAN(dataset, e, Minpts)
        #print(max(y_pred))
        dataset = pd.concat([dataset, pd.DataFrame(y_pred, columns=['cluster'])],axis=1)        
        list_cluster = dataset['cluster'].drop_duplicates().values.tolist()
        for cluster in list_cluster:
            data_cluster = dataset[dataset['cluster']==cluster]
            list_point = data_cluster[['纬度','经度']].values.tolist()
            #self.plotpoints(list_point,radius=10,color='#3388ff')
            if cluster!=-1:
                self.plotconvexhull(list_point,color)
                
    '''
    point:[纬度，经度]
    radius: 扇区半径，0.5km
    HPBW: 半功率角，单位度
    direction: 方位角，正北方为0度
    '''
    def cell2sector(self,point,direction,radius=0.5,HPBW=50):
        # 地球每度的弧长km，地球半径*2pi/360
        EARTH_ARC = 111.199
        direction=int(direction)%360
        direction=direction*math.pi/180
        HPBW=HPBW*math.pi/180
        sector = []
        sector.append(point)
        angle_step=10*math.pi/180
        for i in range(int(HPBW/angle_step)):
            sector_angle = direction - HPBW/2 + angle_step*i
            sector_point = [point[0] + radius*math.cos(sector_angle)/EARTH_ARC,
                            point[1] + radius*math.sin(sector_angle)/(EARTH_ARC*math.cos(point[0]*math.pi/180))]
            sector.append(sector_point)
            
        sector = sector + [sector[0]]
        return sector
    
    def plotcells_df(self,dataset,color='#3388ff'):
        for index,row in dataset.iterrows():
            point = [row['纬度'],row['经度']]
            direction = row['方位角']
            sector = self.cell2sector(point=point, direction=direction, radius=0.5, HPBW=50)
            self.plotpolygon(sector,color)
            
    def save(self,filename='cell.html'):
        self.basemap.save(filename)
        
    def __str__(self):
        return self.basemap._repr_html_()
            
            
if __name__ == 'main':
    
    filename=u'工参_yy.xlsx'
    dataset = pd.read_excel(filename,encoding="gbk")
    dataset = dataset[['ECI','eNBID','跟踪区','经度','纬度','频段','站型','方位角','站高','半功率角']]
    dataset = dataset.dropna(subset=['经度','纬度'])
    cells = dataset[(dataset['跟踪区']==22344) & (dataset['频段']=='F1')].reset_index().drop(['index'],axis=1)
    sites = cells.drop_duplicates(subset=['eNBID'],keep='first').reset_index().drop(['index','ECI'],axis=1)
    cv=covervisual()
    cv.plotpoints_df(sites,radius=100,color='#3388ff')
    cv.plotcells_df(cells,color='#3388ff')
    cv.plotdbscan(sites,color='red',e=0.008, Minpts=2)
    cv.save()