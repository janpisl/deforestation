
import ee
import geetools
from geetools import tools

import pdb 

ee.Initialize()


bbox = ee.Geometry.Polygon(
        [[[-54.2,-6.35],
          [-53.2,-6.35],
          [-53.2,-5.65],
          [-54.2,-5.65]]], proj="epsg:4326", geodesic=False)


start = ee.Date("2019-01-01")
finish = ee.Date("2019-12-31")


s2 = ee.ImageCollection("COPERNICUS/S2_SR")\
    .filterBounds(bbox).filterDate(start,finish)\
    .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 50))\
    .map(lambda image: image.clip(bbox))\

s2 = s2.select(['B2', 'B3', 'B4', 'SCL'])

print(s2)
print(f"Number of images in collection: {len(s2.getInfo()['features'])}")

same_day_mosaic = tools.imagecollection.mosaicSameDay(s2)
name_pattern = '{system_date}'
date_pattern = 'ddMMMy'
#same_day_mosaic.getInfo()['features'][0]['properties']['system:time_start']


print(f"Number of images in daily collection: {len(same_day_mosaic.getInfo()['features'])}")


tasks = geetools.batch.Export.imagecollection.toDrive(
            collection=same_day_mosaic,
            folder="s2_daily_mosaic_cloud_lte_50",
            region=bbox,
            namePattern=name_pattern,
            datePattern=date_pattern,
            scale=10,
            verbose=True,
            maxPixels=int(1e13)
        )



'''

cld = require('users/fitoprincipe/geetools:cloud_masks')
batch = require('users/fitoprincipe/geetools:batch')



bbox = ee.Geometry.Polygon(
        [[[-54.2,-6.35],
          [-53.2,-6.35],
          [-53.2,-5.65],
          [-54.2,-5.65]]])


start = ee.Date("2019-01-01")
finish = ee.Date("2019-01-07")

s2 = ee.ImageCollection("COPERNICUS/S2_SR")
          .filterBounds(bbox)
          .filterDate(start,finish)
          .map(function(image){return image.clip(bbox)})
          #.mosaic()
        #.filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 25))
        
s2rgb = {"opacity":1,"bands":["B4","B3","B2"],"max":1595.3890649236328,"gamma":1};




# Difference in days between start and finish
diff = finish.difference(start, 'day')

# Make a list of all dates
range = ee.List.sequence(0, diff.subtract(1)).map(function(day){return start.advance(day,'day')})

# Funtion for iteraton over the range of dates
day_mosaics = function(date, newlist) {
  # Cast
  date = ee.Date(date)
  newlist = ee.List(newlist)

  # Filter collection between date and the next day
  filtered = s2.filterDate(date, date.advance(1,'day'))

  # Make the mosaic
  image = ee.Image(filtered.mosaic())
  
  masked = cld.sclMask(['cloud_low', 'cloud_medium', 'cloud_high', 'shadow'])(image)



  # Add the mosaic to a list only if the collection has images
  return ee.List(ee.Algorithms.If(filtered.size(), newlist.add(masked), newlist))
}

# Iterate over the range to make a new list, and then cast the list to an imagecollection
newcol = ee.ImageCollection(ee.List(range.iterate(day_mosaics, ee.List([]))))
print(newcol)



batch.Download.ImageCollection.toDrive(newcol, 's2_masked', 
                {scale: 10, 
                 type: 'float'})







'''