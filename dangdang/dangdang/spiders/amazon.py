# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
import re


class AmazonSpider(RedisCrawlSpider):
    name = 'amazon'
    allowed_domains = ['amazon.cn']
    # start_urls = ['http://amazon.cn/']
    redis_key = "amazon"

    rules = (
        # 实现提取大分类url地址, 同时提取小分类url地址
        Rule(LinkExtractor(
            restrict_xpaths=("//ul[contains(@class, 'a-unordered-list a-nostyle a-vertical s-ref-indent-')]/div/li",)),
            follow=True),
        # 实现图书详情页的url地址
        Rule(LinkExtractor(
            restrict_xpaths=("//ul[contains(@class, 'a-unordered-list a-nostyle a-vertical s-ref-indent-')]/div/li",)),
            follow=True),
        Rule(LinkExtractor(
            restrict_xpaths=('//div[@id="mainResults"]/ul/li//h2/..',)),
            callback="parse_item"),
        # 实现列表页的翻页
        Rule(LinkExtractor(
            restrict_xpaths=('//div[@id="pagn"]//a',)),
            follow=True),
    )

    def parse_item(self, response):
        item = {}
        item["book_name"] = response.xpath('//span[contains(@id, "roductTitle")]/text()').extract_first()
        item["book_author"] = response.xpath('//div[@id="bylineInfo"]/span[@class="author notFaded"]/a/text()').extract()
        item["book_press"] = response.xpath('//b[text()="出版社:"]/../text()').extract_first()
        item["book_cate"] = response.xpath('//div[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[not(@class)]//a/text()').extract()
        # item["book_img"] = response.xpath('//div[@id="img-canvas"]/img/@src').extract_first()
        item["book_desc"] = re.findall(r"\s+<noscript>(.*?)</noscript>\n.*?<div id=\"outer_postBodyPS\"", response.body.decode(), re.S)
        item["is_ebook"] = "Kindle电子书" in response.xpath('//title/text()').extract_first()
        if item["is_ebook"]:
            item["book_price"] = response.xpath('//td[@class="a-color-price a-size-medium a-align-bottom"]/text()').extract_first()
        else:
            item["book_price"] = response.xpath('//span[contains(@class,"price3P")]/text()').extract_first()
        # print(item)
        # return item
        yield item


# <noscript>
#  	<div> 为纪念安徒生诞辰200周年，布拉格Brio出版社开启捷克史上超大规模童书插画，打造一套珍藏的安徒生童话全集。邀请世界艺术家、国际安徒生大奖得主——杜桑‧凯利及其妻子卡米拉·什坦茨洛娃共同绘制，书中插画皆艺术品级，精美瑰丽。历时三年，针对156篇安徒生童话，绘制上千幅插画。<br>译文选用叶君健经典译文，无删节，由叶君健在世70年间再三修订，保持安徒生的诗情、幽默和生动活泼的形象。整套书印刷精美，典藏级装帧，附赠156篇叶君健亲撰导读。</div>
#  	<em></em>
#  </noscript>