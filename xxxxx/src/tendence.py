#-*- coding:utf8 -*-


class Tendence(object):
    __slots__ = ['__beta0', '__beta1', '__R2']
    
    def __init__(self, p):
        n = len(p)
        p_bar = sum(p) / n
        
        self.__beta1 = 0
        for i in range(1,n+1):
            self.__beta1 += (i-(n+1)/2)*(p[i-1]-p_bar)
        self.__beta1 /= n*(n-1)*(n+1)/12
        
        self.__beta0 = p_bar - self.__beta1*(n+1)/2
        
        tmp1 = 0
        tmp2 = 0
        for i in range(1,n+1):
            tmp1 += (self.__beta1*i + self.__beta0 - p_bar)**2
            tmp2 += (p[i-1] - p_bar)**2
        if tmp2>0:
            self.__R2 = tmp1 / tmp2
        else:
            self.__R2 = 1.
        
    @property
    def beta0(self):
        return self.__beta0
    
    @property
    def beta1(self):
        return self.__beta1
    
    @property
    def R2(self):
        return self.__R2
    
if __name__=='__main__':
    p = [3124, 3131, 3153, 3157, 3281, 3338, 3330, 3287, 3234, 3286, 3303, 3270, 3246, 3258, 3233, 3175]
    tend = Tendence(p)
    print(tend.beta0, tend.beta1, tend.R2)
    