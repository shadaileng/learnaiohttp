#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	*******************
	*       Demo      *
	*******************
	     Powered By %s
'''

__author__ = 'Shadaileng'
_usage = '''
Usage: python3 src/demo.py option
	0 - server
	1 - client
	2 - query string parameter
	3 - json request and response
	4 - stream response
'''

import aiohttp, asyncio, sys, json

from aiohttp import web
from yarl import URL


def main(func):
	loop = asyncio.get_event_loop()
	loop.run_until_complete(func())

async def client():
	# 创建ClientSession实例命名为session， 用来访问HTTP服务
	async with aiohttp.ClientSession() as session:
		# session访问HTTP服务得到ClientResponse对象, 命名为response,response可以得到服务器返回的所有信息
		async with session.get('http://localhost:8080') as response:
			print('status: %s' % response.status)
			html = await response.text()
			print(html)
		async with session.get('http://localhost:8080') as response:
			print('status: %s' % response.status)
			html = await response.content.read()
			print(html)

def server():
	print('==================================')
	print('server')
	async def handle(request):
		# match_info中查找参数name，默认值shadaileng
		name = request.match_info.get('name', 'shadaileng')
		text = "hello, %s" % name
		print('response: %s' % text)
		# 响应返回
		return web.Response(text=text)
	async def json_req_rsp(request):
		print(await request.json())
		# 响应返回
		rep = web.Response(body=json.dumps({'status': 'ok'}, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
		rep.content_type = 'text/json;charset=utf-8'
		return rep
	app = web.Application()
	app.add_routes([web.get('/', handle), web.get('/{name}', handle), web.post('/json', json_req_rsp)])
	web.run_app(app)


async def querystring():
	async with aiohttp.ClientSession() as session:
		params = {'key1': 'val1', 'key2': 'val2'}
		async with session.get('http://localhost:8080/querystring', params=params) as response:
			expect = 'http://localhost:8080/querystring?key1=val1&key2=val2'
			print(str(response.url))
			assert str(response.url) == expect
		# 元组数组方式拼接参数
		params = [('key1', 'val1'), ('key2', 'val2'), ('key2', 'val3')]
		async with session.get('http://localhost:8080/querystring', params=params) as response:
			expect = 'http://localhost:8080/querystring?key1=val1&key2=val2&key2=val3'
			print(str(response.url))
			assert str(response.url) == expect
		# 请求参数中包含特殊字符，禁用转码
		async with session.get(URL('http://localhost:8080/querystring?key+1=val', encoded=True)) as response:
			expect = 'http://localhost:8080/querystring?key+1=val'
			print(str(response.url))
			assert str(response.url) == expect

async def json_():
	async with aiohttp.ClientSession() as session:
		async with session.post('http://localhost:8080/json', json={'test': 'object'}) as response:
			print('status: %s' % response.status)
			try:
				jsonobj = await response.json()
				print(jsonobj)
			except Exception as e:
				print('exception: %s' % e)
				print('===================================')
				print('status: %s' % response.status)
				html = await response.text()
				print(html)

async def streamrep():
	async with aiohttp.ClientSession() as session:
		async with session.get('http://localhost:8080') as response:
			print('status: %s' % response.status)
			size = 1024
			with open('./tmp/localhost.html', 'wb') as file:
				while True:
					chunk = await response.content.read(size)
					if not chunk:
						break
					print(chunk)
					file.write(chunk)


if __name__ == '__main__':
	print(__doc__ % __author__)
	argv = sys.argv[1:]
	print(argv)
	if len(argv) < 1:
		print(_usage)
	else:
		option = argv[0]
		print('option: %s' % option)
		if option == '0':
			server()
		elif option == '1':
			main(client)
		elif option == '2':
			main(querystring)
		elif option == '3':
			main(json_)
		elif option == '4':
			main(streamrep)
