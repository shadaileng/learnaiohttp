#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	*******************
	*       Demo      *
	*******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import aiohttp, asyncio

from aiohttp import web



async def client():
	# 创建ClientSession实例命名为session， 用来访问HTTP服务
	async with aiohttp.ClientSession() as session:
		# session访问HTTP服务得到ClientResponse对象, 命名为response,response可以得到服务器返回的所有信息
		async with session.get('http://www.baidu.com') as response:
			print('status: %s' % response.status)
			html = await response.text()
			print(html)

loop = asyncio.get_event_loop()
loop.run_until_complete(client())

def main():
	loop = asyncio.get_event_loop()
	loop.run_until_complete(client())

def server():
	async def handle(request):
		name = request.match_info.get('name', 'shadaileng')
		text = "hello, %s" % name
		return web.Response(text=text)
	app = web.Application()
	app.add_routes([web.get('/', handle), web.get('/{name}', handle)])
	web.run_app(app)

if __name__ == '__main__':
	print(__doc__ % __author__)
	main()
	# server()