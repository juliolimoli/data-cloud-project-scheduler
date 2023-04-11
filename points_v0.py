import geopy.distance
import math
import pandas as pd
import folium

# ponto inicial central do nosso quadrado
lat = -22.00823399737311
lon = -47.885274860218
radius = 1
lista = []
pontos = []
lista_int = []
pontos_int = []
latitude = []
longitude = []

# buscando ponto à extremidade do quadrado
extreme_point = geopy.distance.distance(kilometers=9*math.sqrt(2)*radius).destination((lat, lon), bearing=315)
extreme_point_int = geopy.distance.distance(kilometers=8*math.sqrt(2)*radius).destination((lat, lon), bearing=315)
lista.append(list(extreme_point))
lista_int.append(list(extreme_point_int))


# Pontos externos
i = 1
while i < 10:
  lista.append(list(geopy.distance.distance(kilometers=2*i*radius).destination((extreme_point[0], extreme_point[1]), bearing=90)))
  lista[i-1] = list(lista[i-1])
  i = i+1
pontos = pontos + lista

for i in lista:
  j = 1
  while j < 10:
      pontos.append(geopy.distance.distance(kilometers=2*j*radius).destination((i[0], i[1]), bearing=180))
      pontos[j-1] = list(pontos[j-1])
      j = j+1

for i in pontos:
  latitude.append(i[0])
  longitude.append(i[1])

# Pontos internos
i = 1
while i < 9:
  lista_int.append(list(geopy.distance.distance(kilometers=2*i*radius).destination((extreme_point_int[0], extreme_point_int[1]), bearing=90)))
  lista_int[i-1] = list(lista_int[i-1])
  i = i+1
pontos_int = pontos_int + lista_int

for i in lista_int:
  j = 1
  while j < 9:
      pontos_int.append(geopy.distance.distance(kilometers=2*j*radius).destination((i[0], i[1]), bearing=180))
      pontos_int[j-1] = list(pontos_int[j-1])
      j = j+1

for i in pontos_int:
  latitude.append(i[0])
  longitude.append(i[1])


# Criando df
lista_de_tuplas = list(zip(latitude, longitude))
df = pd.DataFrame(lista_de_tuplas, columns=['Latitude', 'Longitude'])
df = df.drop_duplicates()
print(df)