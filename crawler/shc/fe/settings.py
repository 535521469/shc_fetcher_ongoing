BOT_NAME = 'SHCSpider'
#SPIDER_MODULES = ['crawler.shc.fe.spiders_picture']
SPIDER_MODULES = ['crawler.shc.fe.spiders']
LOG_LEVEL = 'DEBUG'
#DOWNLOAD_DELAY = 2
LOG_ENCODING = u'UTF-8'

RETRY_TIMES = 10

DOWNLOADER_MIDDLEWARES = {'crawler.shc.fe.middlewares.ProxyRetryMiddleWare':450,
                          'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware':None
                           }


