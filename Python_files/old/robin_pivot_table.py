import pandas as pd
import numpy as np
import os
from tqdm import tqdm


def readRatings(file):
    mylist = []
    for chunk in pd.read_csv(file, chunksize=20000, encoding='utf8',
                             usecols=["userId", "movieId", "rating"]):
        mylist.append(chunk)
    ratings = pd.concat(mylist, axis=0)
    return ratings


def getCustomMovieMat2(chunk_size, file_path):  # issues with store.append :
    # ValueError: cannot match existing table structure for X on appending data
    ratings = pd.read_csv(file_path,
                          usecols=["userId", "movieId", "rating"],
                          chunksize=chunk_size,
                          dtype={"movieId": np.int64,
                                 "rating": np.float64,
                                 "userId": np.int64})
    store = pd.HDFStore("store2.h5", mode="w")
    for chunk in ratings:
        data = chunk.pivot(index='userId', columns='movieId', values='rating')
        print(data.dtypes)
        data.columns = data.columns.astype(np.int64)
        store.append("pivot", data)
    store.close()  # Also store doesn't close since it stops before


def getCustomMovieMat_memoryloss(frame, chunk_size, file_path):  # seems fine, slows gradually and memory dies at ~60%
    chunker = [frame[i:i+chunk_size] for i in range(0, frame.shape[0], chunk_size)]  # pd.read_csv(file_path, chunksize=chunk_size)
    tot = pd.DataFrame()
    for i in tqdm(range(0, len(chunker) - 1)):
        tot = tot.add(chunker[i].pivot('userId', 'movieId', 'rating'), fill_value=0)
    tot.to_csv(file_path)
    return tot


file_path = "csv_files/ml-latest/ratings.csv"
ratings = readRatings(file_path)

# getCustomMovieMat2(10000, file_path)
movieMat = getCustomMovieMat_memoryloss(ratings, 100000, "moviemat.csv")
