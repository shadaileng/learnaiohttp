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

> 默认的超时对象

```
aiohttp.ClientTimeout(total=5*60, connect=None,
                      sock_connect=None, sock_read=None)
```
- `total`: 整个操作时间包括连接建立，请求发送和响应读取

- `connect`: 从池中获取连接的总超时时间。时间包括建立新连接的连接或等待池中的空闲连接

- `sock_connect`: 新建连接的超时时间，而不是从连接池中取

- `sock_read`: 最大允许读取超时时间

---

# 客户端高级应用

## ClientSession

> `ClientSession`是客户端`API`核心部分。

> 首先创建`session`，使用该实例执行`HTTP`请求和初始化`WebSocket`连接

> `session`包含`cookie`存储和连接池，因此同一个`session`中`HTTP`请求的`cookie`和连接是共享的

## 自定义请求头

> 通过将一个包含请求头信息的`dict`赋值给`headers`参数

```
url = 'http://example.com/image'
payload = b'GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00'
          b'\x00\x00\x01\x00\x01\x00\x00\x02\x00;'
headers = {'content-type': 'image/gif'}

await session.post(url, data=payload, headers=headers)
```

## 自定义cookies

> 创建`session`时，将`cookies`信息以`dict`的形式赋值给`cookies`参数

```
url = 'http://httpbin.org/cookies'
cookies = {'cookies_are': 'working'}
async with ClientSession(cookies=cookies) as session:
    async with session.get(url) as resp:
        assert await resp.json() == {
           "cookies": {"cookies_are": "working"}}
```
## Response中信息

### headers

> `response.headers`的值是`dict`形式的`headers`

```
assert resp.headers == {
    'ACCESS-CONTROL-ALLOW-ORIGIN': '*',
    'CONTENT-TYPE': 'application/json',
    'DATE': 'Tue, 15 Jul 2014 16:49:51 GMT',
    'SERVER': 'gunicorn/18.0',
    'CONTENT-LENGTH': '331',
    'CONNECTION': 'keep-alive'}
```

### cookies

> `response.cookies`的值是`dict`形式的`cookies`

```
url = 'http://example.com/some/cookie/setting/url'
async with session.get(url) as resp:
    print(resp.cookies['example_cookie_name'])
```

### 转发历史

> 如果请求是转发的，可以通过`response.history`得到转发信息

```
resp = await session.get('http://example.com/some/redirect/')
assert resp.status == 200
assert resp.url = URL('http://example.com/some/other/url/')
assert len(resp.history) == 1
assert resp.history[0].status == 301
assert resp.history[0].url = URL(
    'http://example.com/some/redirect/')
```
    
    


---
# 服务端

## 实例

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

## 测试

```
# 启动服务端
$ python3 src/0001_request.py 1
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
```

## 一个简单的服务器

> 请求处理函数`handle`必须是接收`Request`实体作为唯一参数并返回`Response`实体的协同程序。

```
async def handle(request):
	name = request.match_info.get('name', 'shadaileng')
	text = "hello, %s" % name
	return web.Response(text='hello world')
```

> 创建`Application`实例，并为请求处理函数注册特定的`HTTP`方法和路径

```
app = web.Application()
app.add_routes([web.get('/', handle), web.get('/{name}', handle)])
```

> 访问`http://localhost:8080/`可以得到返回结果

> 调用`run_app()`方法启动应用。

```
web.run_app(app)
```
> 另一种注册路由的方法是使用路由装饰器创建路由表和注册`web`处理器

```
routes = web.RouteTableDef()

@routes.get('/')
async def handle(request):
	return web.Response(text='hello world')
app = web.Application()
app.add_routes(routes)
web.run_app(app)
```
## 命令行接口(CLI)

> `aiohttp.web`实现了一个基本的命令行接口，通过`TCP/IP`协议快速提供应用开发服务。

```
$ python -m aiohttp.web -H localhost -P 8080 package.module:init_server
```

> `package.module:init_server`是一个可导入可执行对象，可以接收任何未解析的参数列表并返回设置完成的`Application`实体

```
def init_server(arg):
	app = web.Application()
	app.router.add_get('/', handle)
	return app
```

## 处理函数

> 请求处理函数`handle`必须是接收`Request`实体作为唯一参数并返回`StreamResponse`子类(如`Response`)实体的协同程序。

```
async def handle(request):
	return web.Response()
```

> 调用`Application.add_routes()`函数路由列表，列表元素是特定`HTTP`函数(`get()`或`post()`)和路径的路由

```
app = web.Application()
app.add_routes([web.get('/', handle), web.post('/post', handle), web.put('/put', handle)])
```

> 使用路由修饰器

```
routes = web.RouteTableDef()

@routes.get('/')
async def get_handle(request):
	return web.Response()

@routes.post('/')
async def post_handle(request):
	return web.Response()


@routes.put('/')
async def put_handle(request):
	return web.Response()
	
app.add_routes(routes)
```

> 使用通配符`HTTP`函数

```
app.add_routes([web.route('*', '/', handle)])
```

## 路由和资源

> 路由是一个资源列表，通过调用`web`处理函数处理`HTTP`方法

> 资源是路由表中请求`URL`对应的实体，资源至少有一个对应的路由

> 同一路径所有HTTP方法的路由会合并为唯一资源。

> 指向资源的路径是可变的，路径中使用`{identify}`占位符，处理函数中读取匹配参数`Request.match_info`

```
@routes.get('/{name}')
async def variable_handler(request):
    return web.Response(
        text="Hello, {}".format(request.match_info['name']))
```

> 占位符中可以使用正则表达式`{identifier:regex}`

> 路由命名,从路由表中取出路由，并为资源构建`URL`

```
@routes.get('/root', name='root')
async def handler(request):
	route =request.app.router['root']
	url = route.url_for().with_query({"a": 1, "b": 2})
	assert(url == URL('/root?a=1&b=2'))
	return web.Response(text="Hello"))
```

> 如果路径中有占位符需要先指定占位符的值，`route.url_for(name=val)`

```
@routes.get('/root/{name}', name='root')
async def varHandle(request):
	route = request.app.router['root']
	name = request.match_info.get('name', 'shadaileng')
	print(route.url_for(name=name).with_query({"a": "b", "c": "d"}))
	return web.Response(text='hello, %s' % name)
```

> 可以使用`UrlDispatcher.resources()`方法查看路由器中的所有注册资源

```
for resource in app.router.resources():
    print(resource)
```

> 可以使用UrlDispatcher.named_resources（）方法查看使用名称注册的资源子集

```
for name, resource in app.router.named_resources().items():
    print(name, resource)
```

## Handler类

> 在类中组织`handle`函数

```
class Handler:
	def __init__(self):
		pass
	async def handle_get(self, request):
		return web.Response(text="hello get")
	
	async def handle_post(self, request):
		return web.Response(text="hello post")

handle = Handler()
app = web.Application()
app.add_routes([web.get('/get', handle.handle_get), web.get('/post', handle.handle_post)])
```

## 基于视图的类

> `aiohttp.web`支持基于视图的类，`web.View`的派生类和处理请求的函数，

```
class MyView(web.View):
    async def get(self):
        return await get_resp(self.request)

    async def post(self):
        return await post_resp(self.request)
```

> 注册路由

```
web.view('/path/to', MyView)
```
> 或者

```
@routes.view('/path/to')
class MyView(web.View):
    ...
```

## 返回`JSON`响应

> 请求处理函数返回`aiohttp.web.json_response()`

```
async def handler(request):
    data = {'some': 'data'}
    return web.json_response(data)
```

## 会话

> `aiohttp.web`没有会话的内置概念，但是，有一个第三方库，`aiohttp_session`，它增加了会话支持

```
import asyncio
import time
import base64
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

async def handler(request):
    session = await get_session(request)
    last_visit = session['last_visit'] if 'last_visit' in session else None
    text = 'Last visited: {}'.format(last_visit)
    return web.Response(text=text)

async def make_app():
    app = web.Application()
    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    app.add_routes([web.get('/', handler)])
    return app

web.run_app(make_app())
```

## HTTP表单

> `GET`: 表单的`HTTP`函数是`GET`方法(`<form method="get">`)，使用`Request.query`得到请求数据

> `POST`:表单的`HTTP`函数是`POST`方法(`<form method="post">`)，使用`Request.post()`或者`Request.multipart()`方法

> `Request.post()`接受`application/x-www-form-urlencoded`和`multipart/form-data`表单的数据编码（例如`<form enctype =“multipart/form-data”>`。它将文件数据存储在临时目录中。
如果指定了client_max_size，则会引发ValueError异常。为了提高效率，使用`Request.multipart()`，它对上传大文件（文件上传）特别有效。

```
<form action="/login" method="post" accept-charset="utf-8"
      enctype="application/x-www-form-urlencoded">

    <label for="login">Login</label>
    <input id="login" name="login" type="text" value="" autofocus/>
    <label for="password">Password</label>
    <input id="password" name="password" type="password" value=""/>

    <input type="submit" value="login"/>
</form>
```
> 服务器接受数据
```
async def do_login(request):
    data = await request.post()
    login = data['login']
    password = data['password']
```

## 文件上传

> `aiohttp.web`内置了对处理从浏览器上传的文件的支持。首先，确保`HTML <form>`元素的`enctype`属性设置为`enctype =“multipart / form-data”`。

```
<form action="/store/mp3" method="post" accept-charset="utf-8"
      enctype="multipart/form-data">

    <label for="mp3">Mp3</label>
    <input id="mp3" name="mp3" type="file" value=""/>

    <input type="submit" value="submit"/>
</form>
```

> 然后，在请求处理程序中，您可以作为`FileField`实例访问文件输入字段。`FileField`只是该文件的一个容器以及它的一些元数据：

```
async def store_mp3_handler(request):

    # WARNING: don't do that if you plan to receive large files!
    data = await request.post()

    mp3 = data['mp3']

    # .filename contains the name of the file in string format.
    filename = mp3.filename

    # .file contains the actual file data that needs to be stored somewhere.
    mp3_file = data['mp3'].file

    content = mp3_file.read()

    return web.Response(body=content,
                        headers=MultiDict(
                            {'CONTENT-DISPOSITION': mp3_file}))
```

> 分块读取上传文件

```
async def store_mp3_handler(request):

    reader = await request.multipart()

    # /!\ Don't forget to validate your inputs /!\

    # reader.next() will `yield` the fields of your form

    field = await reader.next()
    assert field.name == 'name'
    name = await field.read(decode=True)

    field = await reader.next()
    assert field.name == 'mp3'
    filename = field.filename
    # You cannot rely on Content-Length if transfer is chunked.
    size = 0
    with open(os.path.join('/spool/yarrr-media/mp3/', filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    return web.Response(text='{} sized of {} successfully stored'
                             ''.format(filename, size))
```

## WebSockets

> 请求处理函数返回`WebSocketResponse`实体，与对等设备进行通信

```
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws
```

## 转向

> 将用户重定向到另一个端点 - 使用绝对URL，相对URL或视图名称（来自路由器的参数）来引发HTTPFound：

```
async def handler(request):
    location = request.app.router['login'].url_for()
    raise web.HTTPFound(location=location)
router.add_get('/handler', handler)
router.add_get('/login', login_handler, name='login')
```

























