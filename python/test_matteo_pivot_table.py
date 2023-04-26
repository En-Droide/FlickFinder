# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 21:17:27 2023

@author: MatyG
"""

import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from scipy.sparse import coo_matrix


def readRatings(file):
    mylist = []
    for chunk in pd.read_csv(file, chunksize=20000, encoding='utf8',
                             usecols=["userId", "movieId", "rating"]):
        mylist.append(chunk)
    ratings = pd.concat(mylist, axis=0)
    return ratings


def getCustomMovieMat(chunk_size, file_path):
    ratings = pd.read_csv(file_path,
                          usecols=["userId", "movieId", "rating"],
                          chunksize=chunk_size,
                          dtype={"movieId": np.int64,
                                 "rating": np.float64,
                                 "userId": np.int64})
    writer = pd.ExcelWriter('moviemat.xlsx')
    n = sum(1 for row in open(file_path, 'r'))
    print("chunks :" + str(n/chunk_size))
    for i, chunk in enumerate(ratings):
        print(f"Processing chunk {i}...")
        data = chunk.pivot(index='userId', columns='movieId', values='rating')
        data.columns = data.columns.astype(np.int64)
        # Convert the pivot table to a sparse matrix
        # sparse_matrix = coo_matrix(data)
        # # Save the sparse matrix to a file
        # np.savez(f"npzfiles/sparse_matrix_{i}.npz", data=sparse_matrix.data, row=sparse_matrix.row, col=sparse_matrix.col)
        # Write the chunk to an Excel file
        data.to_excel(writer, sheet_name=f'sheet{i}', index=True)
    writer.save()


file_path = "csv_files/ml-latest-small/ratings.csv"
ratings = readRatings(file_path)
chunk_size = 10000
n = sum(1 for row in open(file_path, 'r'))
getCustomMovieMat(chunk_size, file_path)
xl = pd.read_excel('moviemat.xlsx', sheet_name=None)
moviemat = pd.DataFrame()
for key in list(xl.keys()):
    moviemat = pd.concat([moviemat, xl[key]], ignore_index=True)
