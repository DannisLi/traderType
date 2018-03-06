#-*- coding:utf8 -*-

import numpy as np

class DataSet():
    
    __slots__ = ['n', '__data', 'vari_list']
    
    def __init__(self, n):
        self.n = n
        self.__data = []
        self.vari_list = []
        
    def empty(self):
        if len(self.__data)==0:
            return True
        else:
            return False
    
    def clear(self):
        self.__data.clear()
        self.vari_list = []
    
    def add(self, y, k, R2, settle, month_till_deli, vari):
        self.__data.append([y, k, R2, settle, month_till_deli, vari])
        if vari not in self.vari_list:
            self.vari_list.append(vari)
    
    @property
    def target(self):
        return np.array([row[0] for row in self.__data])
    
    @property
    def target_momentum(self):
        return np.array([1 if row[0]==0 else 0 for row in self.__data])
    
    @property
    def target_reverse(self):
        np.array([1 if row[0]==1 else 0 for row in self.__data])
    
    @property
    def data(self):
        result = []
        dummy_num = len(self.vari_list) - 1
        for row in self.__data:
            tmp = [row[1]]
            if self.n > 2:
                tmp += row[2:5]
            else:
                tmp += row[3:5]
            vari_dummy = [0.] * dummy_num
            index = self.vari_list.index(row[-1])
            if index<dummy_num:
                vari_dummy[index] = 1.
            result.append(tmp + vari_dummy)
        return np.array(result)
    
    @property
    def data_name(self):
        if self.n==2:
            name = ['k', 'settle', 'month_till_deli']
        else:
            name = ['k', 'R2', 'settle', 'month_till_deli']
        name += ['is_'+vari for vari in self.vari_list[:-1]]
        return name
    
    
if __name__=='__main__':
    dataset = DataSet(2)
    dataset.add(1, 0.6, 1., 300, 3, 'rb')
    dataset.add(2, 0.34, 1., 123.6, 0, 'cu')
    print (dataset.target)
    print (dataset.data_name)
    print (dataset.data)
    
    print ()
    
    dataset = DataSet(5)
    dataset.add(1, 0.6, 0.13, 100.5, 3, 'rb')
    dataset.add(2, 0.34, 0.56, 100.5, 0, 'cu')
    dataset.add(0, 123.6, 0.34, 0.56, 0, 'ag')
    print (dataset.target)
    print (dataset.data_name)
    print (dataset.data)
    