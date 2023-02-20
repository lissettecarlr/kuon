

from bs4 import BeautifulSoup
from . import utils
import re
from loguru import logger

baseURL = "https://www.36dm.club"


# 爬取网页，返回解析后的soup
def searchAnimation(keyword , pageNum = None):
    """ 通过关键词搜索 返回搜索页的soup """
    if pageNum == None :
        pageNum =1 
    page = pageFormate(pageNum)
    keyword = keywordFormat(keyword)
    keywordURL = baseURL + keyword + page
    keywordResponse = utils.requestsGet(keywordURL)
    if(keywordResponse == None):
        #print("搜索失败")
        return None, None

    soup = utils.soupGet(keywordResponse.text)
    htmlText = keywordResponse.text
    keywordResponse.close()
    return (soup, htmlText)

# 通过解析后的soup，提取搜索结果中的页码
def getSearchPageNum(soup) -> int:
    # 保存搜索出来的内容
    listInfos = soup.select("#data_list > tr > td")
    if len(listInfos) > 0:
        text = listInfos[0].get_text()
        if text == "没有可显示资源":
            #print(text)
            return None

    #但页码过多时需要用这个 例如： 1 2 3 4 5 .....  12
    pageLastInfos = soup.select("#btm > div.main > div.pages.clear > a.pager-last.active")
    #但页码数量少时，匹配pages.clear的第三个元素
    pageInfos = soup.select("#btm > div.main > div.pages.clear > a:nth-child(3)")
    # print(pageLastInfos)
    # print(pageInfos)

    if pageLastInfos == None and pageInfos == None:
        logger.warning("没获取到页码")
        return None

    if len(pageLastInfos) > 0:
        pageNum = pageLastInfos[0].get_text() or 1
        return pageNum
    elif len(pageInfos) > 0:
        pageNum = pageInfos[0].get_text() or 1
        return pageNum
    else:
        return 1

# 得到搜索出资源的总数量
def getSearchTotalNum(soup) -> int:
    resultCountInfos = soup.select("#btm > div.main > div > h2 > span")
    #print(resultCountInfos)
    if len(resultCountInfos) == 0:
        return 0
    resultCountText = resultCountInfos[0].get_text()

    try:
        resultCountText = resultCountText[resultCountText.rindex("-") + 1 : len(resultCountText)]
    except:
        logger.warning("resultCountText 截取错误")
        return None
    
    resultCounts = re.search(r"\d+",resultCountText)
    resultCount = resultCounts.group()
    if resultCount == 0 or resultCount == None:
        return None
    return resultCount


# 获取此页资源数量
def getSearchOnePageListCount(soup) -> int:
    """ 每一页的列表的数量 """
    dataListInfos = soup.select("#data_list")
    if len(dataListInfos) == 0:
        return 0

    dataList = dataListInfos[0]
    dataText = dataList.get_text()
    # 判断资源为空不能通过dataList.contents来进行区别,以为数据为空的时候,这数组还是有值的而且大于0
    if "没有可显示资源" in dataText:
        return 0
    else:
        contents= dataList.contents
        del contents[0]
        count = int(len(contents) / 2)
        return count


# 获取搜索结果的链接
def getSearchUrl(soup,index):
    urlInfo = soup.select(detailUrlSelectFormat(index))
    if(len(urlInfo) > 0):
        return baseURL + urlInfo[0].get("href") 
    else:
        return None


# 爬取子页面的下载信息
def getDownloadInfo(url):
    """ 获取单个文件的信息 """
    detailResponse = utils.requestsGet(url)
    if(detailResponse == None):
        logger.warning("请求页面失败")
        return None
    soup = utils.soupGet(detailResponse.text)
    detailResponse.close()
    contentInfos = soup.select("#btm > div.main > div > div")
    contentInfoText = contentInfos[0].get_text()
    if contentInfoText == "种子文件不存在！":
        logger.warning("页面异常,没有种子,网址是: {}".format(url))
        return None

    # 种子
    downloadInfosSend = soup.select("#download")
    downloadUrl = ""
    if len(downloadInfosSend) > 0:
        href = downloadInfosSend[0].get("href")
        downloadUrl = baseURL + href

    '''
    href的格式:
    down.php?date=1556390414&hash=d8e9125797a795c6888e62b6f952b5d6e38265ba
    '''

    #磁力
    downloadInfosMagnet = soup.select("#magnet")
    if len(downloadInfosMagnet) > 0:
        magent = downloadInfosMagnet[0].get("href")
    else:
        magent = "磁力链接未获取成功"

    # 获取详细页面的标题
    infos = soup.select("#btm > div.main > div.slayout > div > div.c2 > div:nth-child(2) > div.torrent_files > ul > li > img")
    if len(infos) > 0:
        title = infos[0].nextSibling
    else:
        title = "标题没有成功获取"

    # 获取时间戳
    dateInfo = soup.select("#btm > div.main > div.slayout > div > div.c1 > div:nth-child(1) > div.basic_info > p:nth-child(4)")
    if len(dateInfo) > 0:
        date = dateInfo[0].get_text()
        date = date[ date.index(' ') + 1 : len( date ) ]
    else:
        date = "时间戳没有成功获取"

    # 获取文件大小
    Sizeinfo = soup.select("#btm > div.main > div.slayout > div > div.c2 > div:nth-child(2) > div.torrent_files > ul > li > span")
    if len(Sizeinfo) > 0:
        text = Sizeinfo[0].get_text()
        size = text.replace("(","").replace(")","")
    else:
        size = "文件大小没有成功获取"

    # print("标题：{}".format(title))
    # print("时间：{}".format(date))
    # print("文件大小：{}".format(size))
    # print("下载地址：{}".format(downloadUrl))
    # print("磁力链接：{}".format(magent))
  
    downloadInfo={"title": title, "downloadUrl": downloadUrl, "magent":magent,"size": size,"time":date}
    #print(downloadInfo)
    logger.info(downloadInfo)
    return downloadInfo

#getDownloadInfo("https://www.36dm.club/show-88878e07fd0e172d12c50ac3356239dda83708f2.html")

# page格式化
def pageFormate(pageNum = None) -> str:
    return "&page={}".format(pageNum or 1)

# 搜索格式化
def keywordFormat(keyword) -> str:
    return "/search.php?keyword=" + keyword

# 详细url的copy-selector格式化
def detailUrlSelectFormat(index) -> str:
    return "#data_list > tr:nth-child({}) > td:nth-child(3) > a".format(index)

""" 下面是想通过搜索列表获取其文件大小 种子数量 正在下载 完成 发布者 通过lxml框架进行 """

# 列表的单个文件大小
def listSizeSelectFormat(index) -> str:
    return '//*[@id="data_list"]/tr[{}]/td[4]'.format(index)

# 列表的做种梳理 有问题
def listMakeSeedNumSelectFormat(index) -> str:
    return '//*[@id="data_list"]/tr[{}]/td[5]/span/text'.format(index)

# 列表下载数量 有问题
def listDownloadingSelectFormat(index) -> str:
    return '//*[@id="data_list"]/tr[{}]/td[6]/span/text'.format(index)

# 列表完成的数量 有问题
def listFinishedSelectFormat(index) -> str:
    return '//*[@id="data_list"]/tr[{}]/td[7]/span/text'.format(index)

# 列表发布者
def listPushSelectFormat(index) -> str:
    return '//*[@id="data_list"]/tr[{}]/td[8]/a'.format(index)
