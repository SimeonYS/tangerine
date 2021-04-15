import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TtangerineItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.tangerine.ca/forwardthinking/viewrecentstories?vgnNextStartIndex={}'

class TtangerineSpider(scrapy.Spider):
	name = 'tangerine'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//div[contains(@class,"card card--")]/a[contains(@class,"card--")]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 7:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="contentCard--largeTransparent__content--contentSmall"]/text()').get().strip()
		date = re.findall(r'\w+\s\d+(?:th|nd|st|rd)?\,\s\d+', date)
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@id="blogcontent"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TtangerineItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
