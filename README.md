# learnaiohttp

> 学习官方文档，记录学习笔记 [Async HTTP client/server for asyncio and Python (官方)](https://docs.aiohttp.org/en/stable/index.html)

---

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
	# ClientSession对象创建session会话,用来访问HTTP服务
	async with aiohttp.ClientSession() as session:
		# session访问url,服务器返回ClientResponse对象response, response可以得到服务器返回的所有信息
		async with session.get('http://www.baidu.com') as response:
			print('status: %s' % response.status)
			html = await response.text()
			print(html)
```
> 执行客户端程序，打印返回的结果

> `ClientSession`对象创建session会话,用来访问HTTP服务

> `session`使用`get()`方法访问服务器, 服务器返回`ClientResponse`对象`response`, response可以得到服务器返回的所有信息

> `session`除了`get()`方法还有其他访问`HTTP`服务的方法

```
session.post(url, data=b'data')
session.put(url, data=b'data')
session.patch(url, data=b'data')
session.head(url)
session.options(url)
```
> 一般一个客户端应用只需要创建一个`session`就可以执行所有的请求,或者每个网站创建对应的`session`

> 测试

```
# 启动服务端
$ python3 src/0001_request.py 0
# 另一终端发起请求
$ python3 src/0001_request.py 1
status: 200
hello, shadaileng
```

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
- `session.get()`方法中，请求参数以元组数组的形式赋值给`params`，元组内是请求参数键值。同键不同值的并联字典(`MultiDict`)可以使用这种方法。

```
params = [('key1', 'val1'), ('key2', 'val2'), ('key2', 'val3')]
async with session.get('http://localhost:8080/querystring', params=params) as response:
	expect = 'http://localhost:8080/querystring?key1=val1&key2=val2&key2=val3'
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
http://localhost:8080/querystring?key1=val1&key2=val2&key2=val3
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

### 测试
```
# 启动服务端
$ python3 src/0001_request.py 0
{'test': 'object'}

# 另一终端发起请求
$ python3 src/0001_request.py 3
status: 200
exception: 0, message='Attempt to decode JSON with unexpected mimetype: text/json;charset=utf-8'
===================================
status: 200
{"status": "ok"}
```

## 响应流

> `read()`, `json()`, `text()`等方法会把响应内容全部读入内存，如果响应内容太大容易造成内存溢出

> 使用响应`ClientResponse`对象的`content`属性可以分块读入响应流。`content`属性是`aiohttp.StreamReader`类的实例

```
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
```

## POST请求

### form-data

> 如果要类似`HTML`表单那样发送表单数据，将一个`dict`赋值给`data`参数即可。

```
data={'key1': 'val1', 'key2': 'val2'}
async with session.post('http://localhost:8080', data=data) as response:
```

> 传入的`dict`将在请求完成时自动进行表格编码。

```
{
  ...
  "form": {
    "key2": "value2",
    "key1": "value1"
  },
  ...
}
```

### 字节

> 如果需要发送的请求数据不是不是表单编码的，可以将数据以字节的形式赋值给`data`参数。传入的数据会被直接发送，并且将`Content-Type`默认设置为`application/octet-stream`

```
data=b"{'key1': 'val1', 'key2': 'val2'}"
async with session.post('http://localhost:8080', data=data) as response:
```

### json

> 如果需要发送的数据是`json`数据，可以将`json`数据赋值给`json`参数

```
data={'key1': 'val1', 'key2': 'val2'}
async with session.post('http://localhost:8080', json=data) as response:
```

### 字符

> 将字符数据赋值给参数`text`, 可以发送字符数据

```
data="{'key1': 'val1', 'key2': 'val2'}"
async with session.post('http://localhost:8080', text=data) as response:
```

### 多编码文件(`Multipart-Encoded File`)

> 上传多编码文件,将文件对象赋值给`data`参数，`aiohttp`会自动将文件发送到服务器

```
data={'file': open(path, 'rb')}
await session.post('http://localhost:8080', data=data)
```

> 使用`FormData`对象，设置`filename`和`content-type`

```
data = FormData()
data.add_field('file', open(path, 'rb'), filename='xxx.xls', content-type='application/vnd.ms-excel')
await session.post('http://localhost:8080', data=data)
```

## 流式上传

> `aiohttp`支持多种流式上传，上传大文件可以不用读入内存。

```
with open(path, 'rb') as file:
	await session.post(url, data=file)
```

## websockets

> `aiohttp.ClientSession.ws_connect()`获取`ClientWebSocketResponse`对象 -- `websocket`连接

```
async with session.ws_connect('http://example.org/ws') as ws:
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close cmd':
                await ws.close()
                break
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
```

> 使用`await ws.receive()`或者`async for msg in ws`读取`websocket `任务

> `await ws.send_str('data')`写入`websocket`任务

## 超时

> 超时设置储存在`ClientTimeout`数据结构中，`aiohttp`默认的超时时间是5分钟

> 设置`ClientSession`的`timeout`参数可以设置超时时间

```
timeout = aiohttp.ClientTimeout(total=60)
async with aiohttp.ClientSession(timeout=timeout) as session:
```

> `ClientSession.get()`方法也可以设置超时时间

```
timeout = aiohttp.ClientTimeout(total=60)
async with aiohttp.ClientSession(timeout=timeout) as session:
	async with session.get(url, timeout=timeout) as resp:
```





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
