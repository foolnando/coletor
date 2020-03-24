# -*- coding: utf-8 -*-
import urllib
import re
import scrapy
from scrapy.crawler import CrawlerProcess
import scipy.cluster.hierarchy as sch
from stack import stack
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import AgglomerativeClustering 


class ScraperWithDuplicateRequests(scrapy.Spider):
    name = "getbid"
    allowed_domains = ['nerdstickers.com.br']
    start_urls = [
        'https://www.nerdstickers.com.br/'
    ]
    

    custom_settings = {
        'DEPTH_LIMIT': 15
    }
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 800
    }
    


    def createMatrix(self,A,B):
        '''cria e preenche uma matriz de i linhas e j colunas'''
        matrix = []
        count=0
        for i in A:
            matrix.append([])
            for j in B:
                matrix[count].append(None)
            if(count==(len(A)-1)):
                return matrix
            else:
                count+=1

    def penalty(self,x,y):
        '''penalizacao da comparacao dos pares 1 para match, -1 para mismatch, -2 para gap'''
        if(x==y):
            return 1
        elif(x!=y and (x=="-" or y=="-")):
            return -2
        else:
            return -1

    def finalScore(self,A,B):
        '''calcula o score final do alinhamento consultando a funcao finalScore'''
        i=len(A)
        count=0
        for element in range(0,i):
            count+=self.penalty(A[element],B[element])
        return count


    def miss(self,A,B):
        i=len(A)
        missesA = ''
        missesB = ''
        for element in range(0, i):
            if(A[element]!=B[element]):
                for c in range(element, len(A)):
                    missesA+=A[c]
                for d in range(element,len(B)):
                    missesB+=B[d]

        return missesA,missesB

    def matches(self,A,B):
        i = len(A)
        word = ''
        for element in range(0,i):
            if(A[element]==B[element]):
                word += A[element]
            else:
                break
        return word


    def align(self,A,B):
        '''alinha duas sequencias'''

        #Cria a matriz F e define o valor do gap
        F=self.createMatrix(A,B)
        #GAP
        d=-2

        #preenchendo a primeira linha da matriz F
        for i in range(len(A)):
            F[i][0] = d*i
        #preenchendo a primeira coluna da matriz F
        for j in range(len(B)):
            F[0][j] = d*j

        #preenchendo as outras posicoes da matriz F com o maior valor entre as cedulas de cima, esquerda e diagonal.
        for i in range(1,len(A)):
            for j in range(1,len(B)):
                choice1 = F[i-1][j-1] + self.penalty(A[i-1],B[j-1])
                choice2 = F[i-1][j] + d
                choice3 = F[i][j-1] + d
                F[i][j] = max(choice1,choice2,choice3)

        AlignmentA=""
        AlignmentB=""

        i=len(A)-1
        j=len(B)-1
        #alinhando as sequencias A,B
        while(i>0 and j>0):
            #calcula os scores da posicao atual e de seus vizihos. Comecando da ultima posicao da matriz.
            score = F[i][j]
            scoreDiag = F[i-1][j-1]
            scoreUp = F[i][j-1]
            scoreLeft = F[i-1][j]
            if(score==scoreDiag + self.penalty(A[i-1],B[j-1])):
                if(AlignmentA=="" and AlignmentB==""):
                    AlignmentA = A[i]+AlignmentA
                    AlignmentB = B[j]+AlignmentB
                AlignmentA = A[i-1]+AlignmentA
                AlignmentB = B[j-1]+AlignmentB
                i = i-1
                j = j-1
            elif(score==scoreLeft + d):
                AlignmentA = A[i-1]+AlignmentA
                AlignmentB = "-"+AlignmentB
                i = i-1
            elif(score==scoreUp + d):
                AlignmentA = "-"+AlignmentA
                AlignmentB = B[j-1]+AlignmentB
                j = j-1
        while(i>0):
            AlignmentA = A[i-1]+AlignmentA
            AlignmentB = "-"+AlignmentB
            i = i-1
        while(j>0):
            AlignmentA = "-"+AlignmentA
            AlignmentB = B[j-1]+AlignmentB
            j = j-1

        retorno = []
        retorno.append(self.finalScore(AlignmentA,AlignmentB))
        retorno.append(len(self.matches(AlignmentA,AlignmentB)))
        return [self.finalScore(AlignmentA,AlignmentB),len(self.matches(AlignmentA,AlignmentB))]




    def parse(self, response):
        target = response.url
        
        url = []
        followLink = stack()
        x = []
        #print('fetch')
        #print(response.meta['depth'])
        print('iniciou')
        #print(len(url))
       for next_page in response.css('a::attr(href)').extract():
            #print('next:')
            #print(response.meta['depth'])
            if next_page is not None:
                depth = response.meta['depth']
                #next_page = response.urljoin(next_page)
                score = self.align(target,next_page)
                if(score[1]>12):
                    url.append(next_page)
                    followLink.push(next_page)
                    x.append(score)
                    yield{'path': next_page, 'score': score}

                print('numero de páginas resgatadas:')
                print(len(url))
                
                
                
                #if (score[1]>=38) and (score[0]>=19):
                    #path.append(next_page)
                    #yield{'path': next_page, 'score': score}

                    #yield {'target': next_page, 'depth': response.meta['depth'], 'tam': len(url)}
                    #yield response.follow(next_page, self.parse_path, dont_filter = True)
                
                print(next_page)
                print(response.meta['depth']) 
                yield scrapy.Request(response.urljoin(next_page),callback=self.parse)

        
        

        #dendograma do processo de clustering
        dendrogram = sch.dendrogram(sch.linkage(x, method  = "ward"))
        plt.title('Dendrogram')
        lt.xlabel('Customers')
        plt.ylabel('Euclidean distances')
        #plt.show()


        #print dos clustring
        #o primeiro clsutering sempre vai ser o maior ????
        hc = AgglomerativeClustering(n_clusters = 5, affinity = 'euclidean', linkage ='ward')
        y_hc=hc.fit_predict(x)
        y = np.array(x)
        #plt.scatter(y[y_hc==0, 0], y[y_hc==0, 1], s=100, c='red', label ='Cluster 1')
        #plt.scatter(y[y_hc==1, 0], y[y_hc==1, 1], s=100, c='blue', label ='Cluster 2')
        #plt.scatter(y[y_hc==2, 0], y[y_hc==2, 1], s=100, c='green', label ='Cluster 3')
        #plt.scatter(y[y_hc==3, 0], y[y_hc==3, 1], s=100, c='cyan', label ='Cluster 4')
        #plt.scatter(y[y_hc==4, 0], y[y_hc==4, 1], s=100, c='magenta', label ='Cluster 5')
        #plt.title('Clusters of Customers (Hierarchical Clustering Model)')
        #plt.xlabel('Score do alinhamento')
        #plt.ylabel('minimo radical comum')
        #plt.show()
            
    