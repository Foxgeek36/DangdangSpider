# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from copy import deepcopy


class DdSpider(RedisSpider):
    name = 'dd'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://book.dangdang.com/']
    redis_key = "dangdang"

    def parse(self, response):
        div_list = response.xpath('//div[@class="con flq_body"]/div')[1:-1]
        # print(div_list)
        for div in div_list:
            item = {}
            # 大分类的名字
            item["b_cate"] = div.xpath('.//dl[contains(@class,"primary_dl")]/dt//text()').extract()

            # 获取中间分类分组
            dl_list = div.xpath('.//dl[@class="inner_dl"]')
            for dl in dl_list:
                item["m_cate"] = dl.xpath('./dt//text()').extract()

                # 获取小分类分组
                a_list = dl.xpath('./dd/a')
                for a in a_list:
                    item["s_cate"] = a.xpath('./text()').extract_first()
                    item["s_href"] = a.xpath('./@href').extract_first()
                    # print(item)
                    # 发送小分类url地址的请求 , 到达列表页
                    yield scrapy.Request(
                        item["s_href"],
                        callback=self.parse_book_list,
                        meta={"item": deepcopy(item)}
                    )

    def parse_book_list(self, response):  # 提取列表页数据
        item = response.meta["item"]
        # 获取列表页图书的分组
        li_list = response.xpath('//ul[@class="bigimg"]/li')
        for li in li_list:
            item["book_name"] = li.xpath('./a/@title').extract_first()
            item["book_href"] = li.xpath('./a/@href').extract_first()
            item["book_author"] = li.xpath('.//p[@class="search_book_author"]/span[1]/a/text()').extract()
            item["book_press"] = li.xpath('.//p[@class="search_book_author"]/span[3]/a/text()').extract_first()
            item["book_publish_date"] = li.xpath('.//p[@class="search_book_author"]/span[2]/text()').extract_first()
            item["book_desc"] = li.xpath('.//p[@class="detail"]/text()').extract_first()
            item["book_price"] = li.xpath('.//span[@class="search_now_price"]/text()').extract_first()
            item["book_store_name"] = li.xpath('.//p[@class="search_shangjia"]/a/text()').extract_first()
            item["book_store_name"] = "当当自营" if item["book_store_name"] is None else item["book_store_name"]
            # print(item)
            yield item

        # 实现列表页翻页
        next_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_url is not None:
            yield response.follow(
                next_url,
                callback=self.parse_book_list,
                meta={"item": item}
            )
