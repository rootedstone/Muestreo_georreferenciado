

## Librerias
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

## Seleccion de puntos totales para enumerarlos
shape = gpd.read_file("D:/Proyectos Cartograficos/Pruebas/muestra001.shp")


def sel2 (shape,npuntos):
    param=shape.bounds
    puntos=np.zeros([npuntos*param.shape[0],4])
    
    for index,row in param.iterrows():
        for i in range(npuntos):
            punto=Point(0,0)
            
            while(not shape.contains(punto)[index]):
                newx=(row['maxx']-row['minx'])*np.random.random(1)+row['minx']
                newy=(row['maxy']-row['miny'])*np.random.random(1)+row['miny']
                punto=Point(newx,newy)
                
            puntos[index*npuntos+i,0]=index
            puntos[index*npuntos+i,1]=int(i)
            puntos[index*npuntos+i,2]=newx
            puntos[index*npuntos+i,3]=newy
            
    return puntos

## Enumerar los puntos en funcion de (distancia euclidiana, o X y Y)
def sel3 (puntos,npuntos):
    orden1=pd.DataFrame(puntos,columns=['Poligono','Orden_1','CoordX','CoordY'])
    orden2=orden1.sort_values(by=['Poligono','CoordX','CoordY']).reset_index().drop(['index'],axis=1)
    orden2['Orden_2']=np.repeat([range(npuntos)],np.unique(orden2['Poligono']).size,axis=0).reshape(orden2.shape[0])
    
    
    orden2['geometry']=orden2.apply(lambda row: Point(row.CoordX,row.CoordY),axis=1) 
    shapefile = gpd.GeoDataFrame(orden2, geometry=orden2.geometry)
    
    n=orden2['Poligono'].unique().size
    
    orden3=pd.DataFrame(columns=['Poligono','Orden_1','CoordX','CoordY','Orden_2','geometry','Distancia'])
    
    for i in range(n):
        datos=shapefile[shapefile['Poligono']==i].reset_index()
        datos=datos.drop(['index'],axis=1)
        punto0=datos.loc[0,'geometry']
        datos['Distancia']=datos.distance(punto0)
        datos1=datos.sort_values(by=['Poligono','Distancia']).reset_index()
        datos1=datos1.drop(['index'],axis=1)
        
        orden3=pd.concat([orden3,datos1])

    orden3['Orden_3']=np.repeat([range(npuntos)],np.unique(orden3['Poligono']).size,axis=0).reshape(orden3.shape[0])
    
    return orden3

## Seleeccion sistematica final
def sel4(puntos1,npuntos,n):
    seleccion=np.linspace(0,npuntos-1,n)
    seleccion=np.around(seleccion,0)
    puntos2=puntos1[puntos1['Orden_3'].isin(seleccion)]
    
    puntos_final = gpd.GeoDataFrame(puntos2, geometry=puntos2.geometry)
    return puntos_final

## Pruebas
#i=1
npuntos=10000
n=30
puntos=sel2(shape,npuntos)
puntos1=sel3(puntos,npuntos)
puntos_final=sel4(puntos1,npuntos,n)

## Guardar shapefile
puntos_final.to_file('D:/Proyectos Cartograficos/Muestreo Georreferenciado/Output/puntos_final.shp', driver='ESRI Shapefile')
