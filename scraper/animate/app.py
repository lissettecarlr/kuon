import os
import time
from loguru import logger
import random
import shutil
#爬取36dm网站
from . import spiderTo36dm

def getSearchPageNum(soup) -> int:
    return spiderTo36dm.getSearchPageNum(soup)
    
def searchAnimation(keyword , pageNum = None):
    return spiderTo36dm.searchAnimation(keyword, pageNum)
    
# 获取此页资源数量
def getSearchOnePageListCount(soup) -> int:
    return spiderTo36dm.getSearchOnePageListCount(soup)

class spiderAnimate:
    def __init__(self):
        pass

    async def task(self,sol):
        animateName = sol["name"]
        animateKey = sol["key"]

        # 每次还是全部集数都来来一遍，万一有更好的源呢
        searchKey = animateName + " " + animateKey
        (soup, htmlText) = searchAnimation(keyword = searchKey)
        if(soup == None):
            logger.warning("{} 爬取失败".format(searchKey))
            return None

        # 该关键字搜索出的页码
        pageNum = getSearchPageNum(soup)
        logger.info("关键字：{}，共有：{} 页".format(searchKey,pageNum))
        if pageNum == None:
            logger.warning("搜索：{}，没有找到资源".format(searchKey))
            return None

        # 该关键字搜索出的数据总数
        resultCount = spiderTo36dm.getSearchTotalNum(soup)
        if resultCount == 0 or resultCount == None:
            logger.warning("该页没有资源.")
            return None
        logger.info("共搜索出资源：{}".format(resultCount)) 

        
        # 循环爬取每一页的数据
        self.result = []
        for page in range(1, int(pageNum)+1):
            if(page != 1):
                (soup, htmlText) = searchAnimation(searchKey,page)  

            downInfo = self.searchSolPage(soup)
            self.result +=downInfo
            logger.info("第{}页 处理完成".format(page))
        logger.info("{} 处理结束，结果".format(animateName))
        return self.result
        # return msg
 

    # 对搜索出来的页面进行操作
    def searchSolPage(self,soup):
        #获取本页数量
        pageListCount = getSearchOnePageListCount(soup)
        logger.info("当前页面有 {} 个资源".format(pageListCount))
        # 获取所有资源子链接的url
        urlList = []
        for index in range(1, pageListCount+1):
            url = spiderTo36dm.getSearchUrl(soup,index)
            if(url != None):
                urlList.append(url)
        downloadInfos = []
        num = 1
        for url in urlList:
            logger.info("总共需要处理{}个资源，目前以进行{}个".format(len(urlList),num))
            num = num + 1
            downloadInfo = spiderTo36dm.getDownloadInfo(url)
            #{'title': '[Isekai Ojisan][10].mp4', 'downloadUrl': 'https://', 'magent': 'magnet:?', 'size': '369.6MB', 'time': '2022/12/19 23:22:17'}
            if downloadInfo == None:
                logger.info("{} 子页面获取失败".format(url))
                continue
            # 将所有下载信息添加到列表中
            downloadInfos.append(downloadInfo)
            # 每次结束后随机延迟
            time.sleep(random.uniform(1.1,5.4)) 
        return downloadInfos    

    
if __name__ == '__main__':
    app = spiderAnimate()
    #app.loop()
    sec = {"name":"冰海战记","key":"s2 06"}
    print(app.task(sec))
