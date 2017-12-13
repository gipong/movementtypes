import movementtypes

df = movementtypes.mvtypes('data/gps-trajectory.csv')
#dataframe obj
print(df.data)

#optbwKDE result
df.optbwKDE()
print(df.result)

#using calVelocity
print(df.calVelocity(df.data.iloc[17], df.data.iloc[18][:-1], df.data.iloc[19]))

df.classifySpeed()
df.export_csv('output.csv')

movementtypes.convert.gpx2csv("https://www.openstreetmap.org/trace/2550408/data", 'osmdata')

df = movementtypes.mvtypes('osmdata.csv')

df.optbwKDE()
print(df.result)