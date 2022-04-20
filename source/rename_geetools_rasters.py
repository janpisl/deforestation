'''
Works only with the naming convention used in geetools:

YYYYmmmdd where YYYY is year (e.g. 2020), mmm is month in letters (e.g. Jan) and dd is day (e.g. 01)

Example of use:

python source/rename_geetools_rasters.py data/aoi_1/raster/2019_2021/

'''

import sys
import os
import pdb

months_mapping = {"Jan" : "01",
                 "Feb" : "02",
                 "Mar" : "03",
                 "Apr" : "04",
                 "May" : "05",
                 "Jun" : "06",
                 "Jul" : "07",
                 "Aug" : "08",
                 "Sep" : "09",
                 "Oct" : "10",
                 "Nov" : "11",
                 "Dec" : "12"
                 }
  

def main(input_dir):

    for file in os.listdir(input_dir):

        src = os.path.join(input_dir, file)
        filename = file[:4] + "_" + file[4:7] + "_" + file[7:]
        for key in months_mapping.keys():
            filename = filename.replace(key, months_mapping[key])
        dst = os.path.join(input_dir, filename)
        os.rename(src, dst)


if __name__ == "__main__":

    input_dir = sys.argv[1]


    main(input_dir)