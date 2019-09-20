

# covervisual 蜂窝网络覆盖可视化

## 1，简介
画基站，画扇区，画覆盖包络。

## 2，用例
### 2.1 数据初始化

工参数据至少需要包含['ECI','eNBID','跟踪区','经度','纬度','频段','方位角']信息。

```python
filename=u'工参_yy.xlsx'
dataset = pd.read_excel(filename,encoding="gbk")
dataset = dataset[['ECI','eNBID','跟踪区','经度','纬度','频段','站型','方位角','站高','半功率角']]
dataset = dataset.dropna(subset=['经度','纬度'])
cells = dataset[(dataset['跟踪区']==22344) & (dataset['频段']=='F1')].reset_index().drop(['index'],axis=1)
sites = cells.drop_duplicates(subset=['eNBID'],keep='first').reset_index().drop(['index','ECI'],axis=1)
```

预处理后：

![1568966228581](https://github.com/kuki-gs/covervisual/blob/master/1.png)

![1568966259413](https://github.com/kuki-gs/covervisual/blob/master/2.png)

### 2.2 初始化

给一个初始经纬度。

```python
cv=covervisual(location=[30.2640,121.0587])
```

### 2.3 画基站

```python
cv.plotpoints_df(sites,radius=300,color='#3388ff')
cv.basemap
```

![1568966555891](https://github.com/kuki-gs/covervisual/blob/master/3.png)

### 2.4 画扇区

```python
cv.plotcells_df(cells,color='#3388ff')
cv.basemap
```

![1568966620678](https://github.com/kuki-gs/covervisual/blob/master/4.png)

### 2.5 画覆盖包络

```python
cv.plotdbscan(sites,color='red',e=0.008, Minpts=2)
cv.basemap
```

![1568966662262](https://github.com/kuki-gs/covervisual/blob/master/5.png)

### 2.6 保存页面

```python
cv.save('XXX.html')
```

### 2.7 tostring

```python
str(cv)
```

![1568966803536](https://github.com/kuki-gs/covervisual/blob/master/6.png)
