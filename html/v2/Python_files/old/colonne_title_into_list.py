# -*- coding: utf-8 -*-
"""
Created on Thu May  4 16:29:09 2023

@author: MatyG
"""

import pandas as pd

# Load the dataset into a pandas dataframe
df = pd.read_csv("out_big_data.csv")
# df["title_wt_date"] = df["title"].str.replace(r"\s\(\d{4}\)$", "",
#                                                   regex=True)
# df.to_csv("out_big_data.csv", index=False)

# Extract the "title" column
titles = df["title_wt_date"]

# Convert the "title" column to a list of strings
titles_list = list(titles)

# file = open('tags_movie_latest_small.txt','w')
# for movie in titles_list:
# 	file.write(movie+",\n")
# file.close()