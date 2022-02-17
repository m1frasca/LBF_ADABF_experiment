import numpy as np
import pandas as pd
from sklearn.utils import murmurhash3_32
import random
import serialize
import argparse


'''
def hashfunc(m):
    ss = random.randint(1, 99999999)
    def hash_m(x):
        return murmurhash3_32(x,seed=ss)%m
    return hash_m
'''

class hashfunc(object):
    def __init__(self, m):
        self.m = m
        self.ss = random.randint(1, 99999999)
    def __call__(self, x):
        return murmurhash3_32(x,seed = self.ss) % self.m

'''
Class for Standard Bloom filter
'''
class BloomFilter():
    def __init__(self, n, hash_len):
        self.n = n
        self.hash_len = int(hash_len)
        if (self.hash_len == 0):
            raise SyntaxError('The hash table is empty')
        if (self.n > 0) & (self.hash_len > 0):
            self.k = max(1,int(self.hash_len/n*0.6931472))
        elif (self.n==0):
            self.k = 1
        self.h = []
        for i in range(self.k):
            self.h.append(hashfunc(self.hash_len))
        self.table = np.zeros(self.hash_len, dtype=int)
        
    def insert(self, key):
        if self.hash_len == 0:
            raise SyntaxError('cannot insert to an empty hash table')
        for i in key:
            for j in range(self.k):
                t = self.h[j](i)
                self.table[t] = 1
    # def test(self, key):
    #     test_result = 0
    #     match = 0
    #     if self.hash_len > 0:
    #         for j in range(self.k):
    #             t = self.h[j](key)
    #             match += 1*(self.table[t] == 1)
    #         if match == self.k:
    #             test_result = 1
    #     return test_result

    def test(self, keys, single_key = True):
        if single_key:
            test_result = 0
            match = 0
            if self.hash_len > 0:
                for j in range(self.k):
                    t = self.h[j](keys)
                    match += 1 * (self.table[t] == 1)
                if match == self.k:
                    test_result = 1
        else:
            test_result = np.zeros(len(keys))
            ss=0
            if self.hash_len > 0:
                for key in keys:
                    match = 0
                    for j in range(self.k):
                        t = self.h[j](key)
                        match += 1*(self.table[t] == 1)
                    if match == self.k:
                        test_result[ss] = 1
                    ss += 1
        return test_result

'''Run Bloom filter'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', action="store", dest="data_path", type=str, required=True, help="path of the dataset")
    parser.add_argument('--size_of_BF', action="store", dest="R_sum", type=int, required=True, help="size of the BF")
    parser.add_argument('--pos_ratio', action="store", dest="pos_ratio", type=float, required=True, help="size of the BF", default = 0.7)
    parser.add_argument('--neg_ratio', action="store", dest="neg_ratio", type=float, required=True, help="size of the BF", default = 0.7)
    parser.add_argument("--negTest_ratio", action = "store", dest = "negTest_ratio", type = float, default = 1.0)
    seed= 22012022
    rs = np.random.RandomState(seed)
    random.seed(seed)
    results = parser.parse_args()
    DATA_PATH = results.data_path
    R_sum = results.R_sum
    pos_ratio = results.pos_ratio
    neg_ratio = results.neg_ratio
    negTest_ratio = results.negTest_ratio
    dataset = serialize.load_dataset(DATA_PATH)
    data,other = serialize.divide_dataset(dataset, pos_ratio,neg_ratio,rs)
    query_negative, _ = serialize.divide_dataset(other, 0, negTest_ratio, rs)

    negative_sample = data.loc[(data.iloc[:,-1] == -1)]
    positive_sample = data.loc[(data.iloc[:,-1] == 1)]
    query = positive_sample.iloc[:,0]
    n = len(query)
    bloom_filter = BloomFilter(n, R_sum)
    bloom_filter.insert(query)
    n1 = bloom_filter.test(query_negative, single_key=False)
    print('False positive rate: ', sum(n1)/n)
