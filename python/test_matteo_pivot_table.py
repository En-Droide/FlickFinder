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
    for i, chunk in enumerate(ratings):
        print(f"Processing chunk {i}...")
        data = chunk.pivot(index='userId', columns='movieId', values='rating')
        data.columns = data.columns.astype(np.int64)
        # Convert the pivot table to a sparse matrix
        sparse_matrix = coo_matrix(data.fillna(0))
        # Save the sparse matrix to a file
        np.savez(f"sparse_matrix_{i}.npz", data=sparse_matrix.data, row=sparse_matrix.row, col=sparse_matrix.col)
        # Write the chunk to an Excel file
        data.to_excel(writer, sheet_name=f"chunk_{i}")
    writer.save()


file_path = "csv_files/ml-latest/ratings.csv"
ratings = readRatings(file_path)

getCustomMovieMat(10000, file_path)
