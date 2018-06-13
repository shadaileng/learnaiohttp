# learnaiohttp

> 学习官方文档，记录学习笔记 [Async HTTP client/server for asyncio and Python (官方)](https://docs.aiohttp.org/en/stable/index.html)

# 安装环境

1. 克隆源码
```
$ git clone https://github.com/shadaileng/learnaiohttp.git
```
2. 安装虚拟环境和相关模块
```
# 安装virtualenv
$ sudo pip3 install virtualenv
# 安装虚拟环境
$ cd learnaiohttp
$ virtualenv --no-site-packages venv
# 进入虚拟环境
$ . venv/bin/activate
# 安装相关模块
(venv) $ pip3 install -r requirements.txt
```

# 客户端

## 发起请求

```
import aiohttp, asyncio

async def client():
	# 创建ClientSession实例命名为session， 用来访问HTTP服务
	async with aiohttp.ClientSession() as session:
		# session访问HTTP服务得到ClientResponse对象, 命名为response,response可以得到服务器返回的所有信息
		async with session.get('http://www.baidu.com') as response:
			print('status: %s' % response.status)
			html = await response.text()
			print(html)
```
> 执行客户端程序，打印返回的结果
```
# 启动服务端
$ python3 src/0001_request.py 0
# 另一终端发起请求
$ python3 src/0001_request.py 1
status: 200
hello, shadaileng
```

> `session`除了`get`方法还有其他访问`HTTP`服务的方法

```
session.post(url, data=b'data')
session.put(url, data=b'data')
session.patch(url, data=b'data')
session.head(url)
session.options(url)
```
> 一般一个客户端应用只需要创建一个`session`,或者每个网站创建对应的`session`

## 解析参数

> `get`请求`URL`添加拼接参数可以使用一下两种方法

- `session.get()`方法中，请求参数以`dict`的形式赋值给`params`

```
{'key1': 'val1', 'key2': 'val2'}
async with session.get('http://localhost:8080/querystring', params=params) as response:
	expect = 'http://localhost:8080/querystring?key1=val1&key2=val2'
	print(str(response.url))
	assert str(response.url) == expect
```
- `session.get()`方法中，请求参数以元组数组的形式赋值给`params`，元组内是请求参数键值

```
params = [('key1', 'val1'), ('key2', 'val2')]
async with session.get('http://localhost:8080/querystring', params=params) as response:
	expect = 'http://localhost:8080/querystring?key1=val1&key2=val2'
	print(str(response.url))
	assert str(response.url) == expect
```

> aiohttp在发送请求之前内部执行URL规范化。如果请求参数中包含特殊字符，默认情况会被转化成base64编码，不可逆转。

> 使用`yarl.URL`构建`url`，并添加参数`encoded=True`禁用URL规范化

```
from yarl import URL
async with session.get(URL('http://localhost:8080/querystring?key+1=val', encoded=True)) as response:
	expect = 'http://localhost:8080/querystring?key+1=val'
	print(str(response.url))
	assert str(response.url) == expect
```

> 测试
```
# 启动服务端
$ python3 src/0001_request.py 0
# 另一终端发起请求
$ python3 src/0001_request.py 2
http://localhost:8080/querystring?key1=val1&key2=val2
http://localhost:8080/querystring?key1=val1&key2=val2
http://localhost:8080/querystring?key+1=val
```

## 响应内容和状态码

> 从响应中可以得到服务器返回的状态码和响应内容等信息

```
async with session.get('http://localhost:8080') as response:
	# 状态码
	print('status: %s' % response.status)
	# 响应内容
	html = await response.text()
	print(html)
```

> 如果读取响应内容乱码，可以指定响应内容的编码方式

```
await response.text(encoding='gbk')
```

> 如果响应内容是二进制文件，使用`read()`方法读取响应内容

```
await response.read()
```

## JSON请求和响应

### 请求


> `request()`, `ClientSession.get()`, `ClientSesssion.post()`等请求方法中可以添加`JSON`参数

```
async with aiohttp.ClientSession() as session:
	async with session.post('http://localhost:8080', json={'test': 'object'}) as response:
```

> 服务器断添加`post`请求路由，并打印接收到的`JSON`参数

```
def server():
	async def json_req_rsp(request):
		print(await request.json())
		# 响应返回
		rep = web.Response(body=json.dumps({'status': 'ok'}, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
		rep.content_type = 'text/json;charset=utf-8'
		return rep
	app = web.Application()
	app.add_routes([web.post('/', handle)])
	web.run_app(app)
```

> 默认情况会使用`python`的标准`json`模块进行序列化。也有可能使用不同序列化的`serializer.ClientSession`接收`json_serialize`参数

```
import ujson
async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
	async with session.post('http://localhost:8080', json={'test': 'object'}) as response:
```

> ujson库比标准json更快，但稍微不兼容。

### 响应

> `response`有一个内置的JSON解码器，可以处理`JSON`数据

```
jsonobj = await response.json()
```

> 如果JSON解码器解码失败，`json()`函数会抛出异常，可以为`json()`函数指定自定义的编码和解码函数。


```
try:
	jsonobj = await response.json()
	print(jsonobj)
except Exception as e:
	print('exception: %s' % e)
	print('===================================')
	print('status: %s' % response.status)
	html = await response.text()
	print(html)
```

> `json()`函数会将整个响应体读入内存，如果读取的是较大的数据，建议使用流式响应函数










---
# 服务端

```
def server():
	async def handle(request):
		name = request.match_info.get('name', 'shadaileng')
		text = "hello, %s" % name
		return web.Response(text=text)
	app = web.Application()
	app.add_routes([web.get('/', handle), web.get('/{name}', handle)])
	web.run_app(app)
```

> 执行服务端程序，监听`8080`端口，根据请求返回结果

```
# 启动服务端
$ python3 src/0001_request.py 1
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
```
