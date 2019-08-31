# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re


class DangdangPipeline(object):
    def process_item(self, item, spider):
        if spider.name == "dd":
            item["b_cate"] = ''.join([i.strip() for i in item["b_cate"]])
            item["m_cate"] = ''.join([i.strip() for i in item["m_cate"]])
            print(item)
        return item


class AmazonPipeline(object):
    def process_item(self, item, spider):
        if spider.name == "amazon":
            item["book_cate"] = [i.strip() for i in item["book_cate"]]
            item["book_desc"] = item["book_desc"][0].split("</div>")[0].strip().split("<div>")[-1].split("<br><br>")[0]
            item["book_desc"] = re.sub(r'<br />|\s+|<div>|</div>|<em>|</em>|<br>', '', item["book_desc"])
            print(item)
        return item
