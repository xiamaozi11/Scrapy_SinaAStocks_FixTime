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
    name = "sinaAStocks"  # 爬虫命名
    start_urls = ['http://guba.sina.com.cn/?s=category&cid=1&page=1']  # 要爬取的页面地址
    #start_urls = ['http://guba.sina.com.cn/?s=thread&tid=2339621&bid=14247'] 
    url = 'http://guba.sina.com.cn'
    index = 1;
    subIndex = 1;

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
                        self.subIndex = 1;
                        yield Request(link, callback=self.parse_Subpage) # 调用parse_Subpage函数

                
                '''responseAdd = HtmlResponse(url=link)

                sel = Selector(response = responseAdd)
                cons = sel.xpath('//div')
                fullTitle = ''
                for each in title:
                    fullTitle += each
                movieInfo = eachPost.xpath('div[@class="bd"]/p/text()').extract()
                star = eachPost.xpath('div[@class="bd"]/div[@class="star"]/span/text()').extract()[0]
                critical = eachPost.xpath('div[@class="bd"]/div[@class="star"]/span/text()').extract()[1]
                quote = eachPost.xpath('div[@class="bd"]/p[@class="quote"]/span/text()').extract()
                # quote可能为空，因此需要先进行判断
                if quote:
                    quote = quote[0]
                else:
                    quote = ''
                item['title'] = fullTitle
                item['movieInfo'] = ';'.join(movieInfo)
                item['star'] = star
                item['critical'] = critical
                item['quote'] = quote
                yield item  # 提交生成csv文件'''
        nextLink = selector.xpath('//div[@class="fy"]/p[@class ="page"]/span[@class = "cur"]/following-sibling::a[1]/@href')
        self.index += 1
        # 第10页是最后一页，没有下一页的链接
        if nextLink and self.index <= 1:
            nextLink = nextLink.extract()[0]
            print (self.url +nextLink)
            yield Request(self.url + nextLink, callback=self.parse)
            # 递归将下一页的地址传给这个函数自己，在进行爬取
            
    def parse_Subpage(self,response): # 提取某个A股页面信息
        
        #item = SinaAStocksItem()
        selector = Selector(response)
        post = selector.xpath('//div[@class="blk_listArea"]/div[@class="table_content"]')[0]
        content = ''         
        temps = post.xpath('table/tbody/tr[@class = "tit_tr"]/following-sibling::tr')        
        for eachTemp in temps:
            link = self.url + eachTemp.xpath('td/a/@href').extract()[0]
            yield Request(link, callback=self.parse_SubpageDetailInfo) # 调用parse_SubpageDetailInfo函数
        nextLink = post.xpath('//div[@class="blk_01_b"]/p[@class ="page"]/span[@class = "cur"]/following-sibling::a[1]/@href')
        #self.subIndex += 1
        # 第10页是最后一页，没有下一页的链接
        c = post.xpath('//div[@class="blk_01_b"]/p[@class ="page"]/span[@class = "cur"]/text()').extract()[0]
        
        if nextLink and int(c) <= 0:
            nextLink = nextLink.extract()[0]
            print (self.url +nextLink)
            yield Request(self.url + nextLink, callback=self.parse_Subpage) 
         
    def parse_SubpageDetailInfo(self,response): # 提取某个A股页面的帖子内容信息
        
        item = SinaAStocksItem()
        selector = Selector(response)
        post = selector.xpath('//div[@class="item_list final_page clearfix"]')[0]
        content = ''
        userIDtemp = post.xpath('//div[@class ="il_txt"]/span[@class="ilt_name"]/a/@title').extract()
        if(len(userIDtemp) > 0):
            userID = userIDtemp[0]
        else:
            userID = post.xpath('normalize-space(//div[@class ="il_txt"]/span[@class="ilt_name"]/text())').extract() 
        #for eachPost in posts:
        #userID = post.xpath('//div[@class ="il_txt"]/span[@class="ilt_name"]/a/@title').extract()[0]
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
            DataTime = tempTime.strftime('%Y-%m-%d %H:%M:%S')
            #DataTime = time.strftime('%Y.%m.%d',time.localtime(time.time())) + DataTime.replace(r'分钟前','')
        else:
            DateTime = DateTime.replace(r'年','-').replace(r'月','-').replace(r'日','')
                #DataTime = time.strptime('2018-' + DataTime,'%Y.%m.%d %H:%M:%S')
            DateTime = '2018-' + DateTime
        item['title'] = title
        item['url'] = link
        item['time'] = DateTime
        item['content'] = ''.join(content)
        item['stockID'] = stockID        
        item['stockName'] = stockName
        item['userID'] = userID
        if Vip:
            item['isVip'] = True
        else:
            item['isVip'] = False       
           
        yield item  # 提交生成   csv文件
        
                
        
        
        