# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 08:54:28 2018

@author: maojin.xia
"""
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from items import SinaAStocksItem
from scrapy.http import HtmlResponse 
import time
import datetime



class SinaAStocks(CrawlSpider):  # Douban是一个类，继承自CrawlSpider
    name = "sinaAStocksTest"  # 爬虫命名
    start_urls = ['http://guba.sina.com.cn/?s=category&cid=1&page=1']  # 要爬取的页面地址
    #start_urls = ['http://guba.sina.com.cn/?s=bar&name=sz002064'] 
    url = 'http://guba.sina.com.cn'
    index = 1;
    subIndex = 1;
    #sIndex = 1;
    urltemp = 'http://guba.sina.com.cn'
    earlyTime = datetime.datetime.strptime("2018-8-27", "%Y-%m-%d")
    mid1Time = datetime.datetime.strptime("2018-9-04", "%Y-%m-%d")
    mid2Time = datetime.datetime.strptime("2018-9-25", "%Y-%m-%d")
    def parse(self, response):
        # print response.body
        #item = SinaAStocksItem()
        
        selector = Selector(response)
        posts = selector.xpath('//div[@class="wrap main clearfix"]')
        for eachPost in posts:
            temps = eachPost.xpath('div[@id="sort"]/div[@id="s2"]/table/tr')            
            for eachTemp in temps:
                subpageLinkList = eachTemp.xpath('td/a/@href').extract()
                if(len(subpageLinkList)>0):
                    for subpageLink in subpageLinkList:
                        link =  self.url + subpageLink
                #title = eachTemp.xpath('a/text()').extract()[0]
                #time =  eachTemp.xpath('font/text()').extract()[0]
                        #self.subIndex = 1;
                        yield Request(link, callback=self.parse_Subpage) # 调用parse_Subpage函数
                        

                
        nextLink = selector.xpath('//div[@class="fy"]/p[@class ="page"]/span[@class = "cur"]/following-sibling::a[1]/@href')
        self.index += 1
        # 第10页是最后一页，没有下一页的链接
        if nextLink and self.index <= 31:
            nextLink = nextLink.extract()[0]
            print (self.url +nextLink)
            yield Request(self.url + nextLink, callback=self.parse)
            # 递归将下一页的地址传给这个函数自己，在进行爬取
            
    def parse_Subpage(self,response): # 提取某个A股页面信息
        #
        #item = SinaAStocksItem()
        selector = Selector(response)
        post = selector.xpath('//div[@class="blk_listArea"]/div[@class="table_content"]')[0]
        lastTime = ''
        bo = True
        content = ''         
        temps = post.xpath('table/tbody/tr[@class = "tit_tr"]/following-sibling::tr')  
        #link = self.url + temps[0].xpath('td/a/@href').extract()[0]
        #yield Request(link, callback=self.parse_SubpageDetailInfo) # 调用parse_SubpageDetailInfo函数
        for eachTemp in temps:
            self.index += 1
            x = self.index
            lastTime = '2018-' +  eachTemp.xpath('td/text()').extract()[-1].replace(r'年','-').replace(r'月','-').replace(r'日','')
            if "分钟" not in lastTime and "秒" not in lastTime and "今天" not in lastTime:
                curTime = datetime.datetime.strptime(lastTime.strip(), "%Y-%m-%d")
                if curTime < self.earlyTime or (curTime > self.mid1Time and curTime < self.mid2Time):
                    bo = False             
            if bo:
                link = self.url + eachTemp.xpath('td/a/@href').extract()[0]
                yield Request(link, callback=self.parse_SubpageDetailInfo) # 调用parse_SubpageDetailInfo函数
        nextLink = post.xpath('//div[@class="blk_01_b"]/p[@class ="page"]/span[@class = "cur"]/following-sibling::a[1]/@href')
        #self.subIndex += 1
        # 第10页是最后一页，没有下一页的链接
        c = post.xpath('//div[@class="blk_01_b"]/p[@class ="page"]/span[@class = "cur"]/text()').extract()[0]
        
        if nextLink and datetime.datetime.strptime(lastTime.strip(), "%Y-%m-%d") >= self.earlyTime:
            nextLink = nextLink.extract()[0]
            print (self.url +nextLink)
            yield Request(self.url + nextLink, callback=self.parse_Subpage) 
         
    def parse_SubpageDetailInfo(self,response): # 提取某个A股页面的帖子内容信息
        try:
            #self.sIndex += 1
            item = SinaAStocksItem()
            selector = Selector(response)
            self.urltemp = response.url
            posts = selector.xpath('//div[@class="item_list final_page clearfix"]')
            if len(posts) > 0:
                post = posts[0]
                content = ''
                y = self.subIndex
                #for eachPost in posts:
                userIDtemp = post.xpath('//div[@class ="il_txt"]/span[@class="ilt_name"]/a/@title').extract()
                if(len(userIDtemp) > 0):
                    userID = userIDtemp[0]
                else:
                    userID = post.xpath('normalize-space(//div[@class ="il_txt"]/span[@class="ilt_name"]/text())').extract()
                
                
                Vip = post.xpath('//div[@class ="il_txt"]/span[@class="ilt_name"]/a[@href="http://guba.sina.com.cn/?s=user&a=apply_vip"]')
                title = post.xpath('//div[@class ="il_txt"]/h4[@class="ilt_tit"]/text()').extract()[0]
                content = post.xpath('//div[@class ="il_txt"]/div[@id="thread_content"]')
                temp = post.xpath('//div[@class ="il_txt"]/div[@id="thread_content"]/p')
                if(len(temp)>0):
                    content = post.xpath('//div[@class ="il_txt"]/div[@id="thread_content"]/p//text()').extract()
                else:
                    content = post.xpath('//div[@class ="il_txt"]/div[@id="thread_content"]//text()').extract()            
                link = response.url
                postStocks = selector.xpath('//div[@class="blk_stock_info clearfix"]/div[@class="bsi_tit"]/span[@id="hqSummary"]')
                stockName = postStocks.xpath('//span[@class="bsit_name"]/a/text()').extract()[0]
                stockID =  postStocks.xpath('//span[@class="bsit_code"]/text()').extract()[0]
                Time = post.xpath('//div[@class="ilt_panel clearfix"]/div[@class="fl_left iltp_time"]/span/text()').extract()
                #http://guba.sina.com.cn/?s=user&a=apply_vip
                #http://guba.sina.com.cn/?s=user&a=apply_vip
                #link = response
                #tps =post.xpath('//div[@class ="ilt_p"]')
                #for tp in tps:
                    #content =  tp.xpath('string()').extract()[0]
                    #temps = tps("/p/string()")
                    #temps = tps.xpath('p')
                    #ttt = temps.xpath('span')
                DateTime = post.xpath('//div[@class = "fl_left iltp_time"]/span/text()').extract()[0]
                if "今天" in DateTime:
                    DateTime = datetime.datetime.now().strftime('%Y-%m-%d') + '-' + DateTime.replace(r'今天','')
                elif "分钟前" in DateTime:
                    tempTime = datetime.datetime.now()-datetime.timedelta(minutes=int(DateTime.replace(r'分钟前','')))
                    DateTime = tempTime.strftime('%Y-%m-%d %H:%M:%S')
                    #DataTime = time.strftime('%Y.%m.%d',time.localtime(time.time())) + DataTime.replace(r'分钟前','')
                elif "秒" in lastTime:
                    tempTime = datetime.datetime.now()-datetime.timedelta(seconds=int(DateTime.replace(r'秒前','')))
                    DateTime = tempTime.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    DateTime = DateTime.replace(r'年','-').replace(r'月','-').replace(r'日','')
                        #DataTime = time.strptime('2018-' + DataTime,'%Y.%m.%d %H:%M:%S')
                    DateTime = '2018-' + DateTime
                #self.subIndex += 1
                item['title'] = title
                item['url'] = link
                item['time'] = DateTime
                item['content'] = ''.join(content)
                item['stockID'] = stockID        
                item['stockName'] = stockName.strip()
                item['userID'] = userID
                #item['num'] = self.subIndex
                #item['snum'] = self.sIndex
                if Vip:
                    item['isVip'] = True
                else:
                    item['isVip'] = False       
                   
                yield item  # 提交生成   csv文件
        except:
            print( self.urltemp)
        
                
        
        
        