## Docker 管理与应用

### Docker的安装

[参考资料：菜鸟教程](https://www.runoob.com/docker/ubuntu-docker-install.html)

1. 先更新系统并安装相关依赖包

   ```sh
   sudo apt update
   sudo apt install apt-transport-https ca-certificates curl software-properties-common
   ```
2. 新建并编辑etc/apt/sources.list.d/docker.list文件

   ```sh
   sudo vi /etc/apt/sources.list.d/docker.list
   ```

   文件内容如下：

   ```sh
   deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable
   ```
3. 添加秘钥

   ```sh
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   ```
4. 更新docker源apt仓库信息

   ```sh
   sudo apt update
   ```
5. 安装docker-ce并验证

   ```sh
   sudo apt install docker-ce
   docker --version
   ```

### Docker管理

[参考教程：菜鸟教程](https://www.runoob.com/docker/docker-mirror-acceleration.html)

#### Docker Hello world

[Guide to Docker Hello World](https://www.runoob.com/docker/docker-hello-world.html)

#### Docker基本命令

1. 获取本地镜像列表

   ```sh
   docker images
   ```
2. 获取云端镜像

   ```sh
   docker pull [image]:[version]
   docker pull ubunut:18.04
   ```
3. 获取docker container列表

   ```sh
   docker ps -a
   ```
4. 运行Docker镜像

   ```sh
   docker run -it --name=[container_name] [image]:[version] /bin/bash
   ```
5. 存储和读取Docker镜像

   ```sh
   docker save -o [(output docker image file name).tar] [from docker image name]:[tag]
   docker export -o [(output docker image file name).tar] [from docker container id]
   docker import [docer_file.tar] [from docker image name]:[tag]
   ```
6. 读取Docker镜像

### Docker云计算应用

#### 系统架构

#### 数据卷

#### Apache服务器

#### MySQL服务器

#### 程序服务器

## 

## HTML

### 基础

### HTML初始代码

```html
<!DOCTYPE html>
<html>
    <head> 
        <meta charset="utf-8"> 
        <title>文档标题</title>
    </head>
 
    <body>
    文档内容......
    </body>
 </html>
```

### head标签

#### title元素

#### base

#### link

#### style

#### meta

#### script

### Body

#### 布局

##### div布局

##### table布局

#### 框架iframe

##### height和width

##### 移除边框

```html
<iframe src="demo_iframe.htm" frameborder="0"></iframe>
```

##### 显示目标链接页面

```html
<iframe src="demo_iframe.htm" name="iframe_a"></iframe>
<p>
    <a href="http://www.runoob.com" target="iframe_a" rel="noopener">RUNOOB.COM</a>
</p>
```

#### 段落

##### 标题

标题（Heading）是通过 h1 - h6 标签进行定义的

##### 水平线hr

hr 标签在 HTML 页面中创建水平线。hr 元素可用于分隔内容。

##### 注释

```html
<!-- 这是一个注释 -->
```

##### p标签

#### 标签

#### 表格

##### table标签

##### th,tr和td

##### caption

##### colgroup

##### col

##### thead

##### tbody

##### tfoot

##### 案例

###### 案例1

###### 案例2

###### 案例3

#### 列表

##### 无序列表ul

##### 有序列表ol

##### 自定义列表dl

#### 图像

##### img

##### map和area

&lt;area&gt; 标签定义图像映射内部的区域（图像映射指的是带有可点击区域的图像）。

&lt;area&gt; 元素始终嵌套在 &lt;map&gt; 标签内部。

注释： &lt;img&gt; 标签中的 usemap 属性与 &lt;map&gt; 元素中的 name 相关联，以创建图像与映射之间的关系。

##### 案例

###### 案例1

点击图片上的不同区域（不同天体），可以打开各自天体的图片。

```html
<img loading="lazy" src="planets.gif" width="145" height="126" alt="Planets" usemap="#planetmap">
 
<map name="planetmap">
  <area shape="rect" coords="0,0,82,126" alt="Sun" href="sun.htm">
  <area shape="circle" coords="90,58,3" alt="Mercury" href="mercur.htm">
  <area shape="circle" coords="124,58,8" alt="Venus" href="venus.htm">
</map>
```

#### 锚点

#### 表单

##### 表单创建

表单是一个包含表单元素的区域。

表单元素是允许用户在表单中输入内容,比如：文本域(textarea)、下拉列表、单选框(radio-buttons)、复选框(checkboxes)等等。

表单使用表单标签 form 来设置:

##### form标签和input标签

```html
<form>
.
input 元素
.
</form>
```


```mermaid
graph TD  
    A[input]-->B[type=text]
    A-->C[type=password]
    A-->D[type=radio]
    A-->E[type=checkbox]
    A-->F[type=submit]
```


| type | 功能 |
| - | - |
| button | 按钮 |
| checkbox |   |
| color |   |
| date |   |
| datetime |   |
| datetime-local |   |
| email | 限定输入域为email地址，并做相应检查 |
| file |   |
| hidden |   |
| image | 图片 |
| month |   |
| number | 限定输入域为数字 |
| password | 输入域为密码 |
| radio |   |
| range | 滑动条 |
| reset |   |
| search | 搜索栏 |
| submit | 提交按钮 |
| tel | 输入电话号码 |
| text | 输入文本 |
| time | 输入时间数据 |
| url |   |
| week |   |

###### 滑动条的实现

```html
<input type="range" name="points" min="1" max="10" />
```

###### 搜索框的实现

```html
<!--action定义了将来要调用/search/这个子程序，类型为get-->
<form action="/search/" methord="get" class="search-style" target="_blank">
            <input type="search" name="query" id="" autocomplete="on" required class="search-style">
            <input type="submit" value="提交" class="search-style">
</form>
```

* form的action定义了将来执行的子程序，即搜索的核心程序。
* input采用search类型，为搜索样式
* 需要自己添加搜索按钮，可以是submit、image等样式
* 样式通过css来实现

##### textarea标签[HTML5]

form
input
textarea
label
fieldset
legend
select
optgroup
option
button
datalist
keygen
output

#### 链接


## HTTP协议

### OS7层网络模型与TCP/IP网络模型

### http头


| 协议头 | 说明 | 示例 | 状态 |
| - | - | - | - |
| Accept | 可接受的响应内容类型（Content-Types）。 | Accept: text/plain | 固定 |
| Accept-Charset | 可接受的字符集 | Accept-Charset: utf-8 | 固定 |
| Accept-Encoding | 可接受的响应内容的编码方式。 | Accept-Encoding: gzip, deflate | 固定 |
| Accept-Language | 可接受的响应内容语言列表。 | Accept-Language: en-US | 固定 |
| Accept-Datetime | 可接受的按照时间来表示的响应内容版本 | Accept-Datetime: Sat, 26 Dec 2015 17:30:00 GMT | 临时 |
| Authorization | 用于表示HTTP协议中需要认证资源的认证信息 | Authorization: Basic OSdjJGRpbjpvcGVuIANlc2SdDE== | 固定 |
| Cache-Control | 用来指定当前的请求/回复中的，是否使用缓存机制。 | Cache-Control: no-cache | 固定 |
| Connection | 客户端（浏览器）想要优先使用的连接类型 | Connection: keep-alive Connection: Upgrade | 固定 |
| Cookie | 由之前服务器通过Set-Cookie（见下文）设置的一个HTTP协议Cookie | Cookie: $Version=1; Skin=new; | 固定：标准 |
| Content-Length | 以8进制表示的请求体的长度 | Content-Length: 348 | 固定 |
| Content-MD5 | 请求体的内容的二进制 MD5 散列值（数字签名），以 Base64 编码的结果 | Content-MD5: oD8dH2sgSW50ZWdyaIEd9D== | 废弃 |
| Content-Type | 请求体的MIME类型 （用于POST和PUT请求中） | Content-Type: application/x-www-form-urlencoded | 固定 |
| Date | 发送该消息的日期和时间（以RFC 7231中定义的"HTTP日期"格式来发送） | Date: Dec, 26 Dec 2015 17:30:00 GMT | 固定 |
| Expect | 表示客户端要求服务器做出特定的行为 | Expect: 100-continue | 固定 |
| From | 发起此请求的用户的邮件地址 | From: user@itbilu.com | 固定 |
| Host | 表示服务器的域名以及服务器所监听的端口号。如果所请求的端口是对应的服务的标准端口（80），则端口号可以省略。 | Host: www.itbilu.com:80<br>Host: www.itbilu.com | 固定 |
| If-Match | 仅当客户端提供的实体与服务器上对应的实体相匹配时，才进行对应的操作。主要用于像 PUT 这样的方法中，仅当从用户上次更新某个资源后，该资源未被修改的情况下，才更新该资源。 | If-Match: "9jd00cdj34pss9ejqiw39d82f20d0ikd" | 固定 |
| If-Modified-Since | 允许在对应的资源未被修改的情况下返回304未修改 | If-Modified-Since: Dec, 26 Dec 2015 17:30:00 GMT | 固定 |
| If-None-Match | 允许在对应的内容未被修改的情况下返回304未修改（ 304 Not Modified ），参考 超文本传输协议 的实体标记 | If-None-Match: "9jd00cdj34pss9ejqiw39d82f20d0ikd" | 固定 |
| If-Range | 如果该实体未被修改过，则向返回所缺少的那一个或多个部分。否则，返回整个新的实体 | If-Range: "9jd00cdj34pss9ejqiw39d82f20d0ikd" | 固定 |
| If-Unmodified-Since | 仅当该实体自某个特定时间以来未被修改的情况下，才发送回应。 | If-Unmodified-Since: Dec, 26 Dec 2015 17:30:00 GMT | 固定 |
| Max-Forwards | 限制该消息可被代理及网关转发的次数。 | Max-Forwards: 10 | 固定 |
| Origin | 发起一个针对跨域资源共享的请求（该请求要求服务器在响应中加入一个Access-Control-Allow-Origin的消息头，表示访问控制所允许的来源）。 | Origin: http://www.itbilu.com | 固定: 标准 |
| Pragma | 与具体的实现相关，这些字段可能在请求/回应链中的任何时候产生。 | Pragma: no-cache | 固定 |
| Proxy-Authorization | 用于向代理进行认证的认证信息。 | Proxy-Authorization: Basic IOoDZRgDOi0vcGVuIHNlNidJi2== | 固定 |
| Range | 表示请求某个实体的一部分，字节偏移以0开始。 | Range: bytes=500-999 | 固定 |
| Referer | 表示浏览器所访问的前一个页面，可以认为是之前访问页面的链接将浏览器带到了当前页面。Referer其实是Referrer这个单词，但RFC制作标准时给拼错了，后来也就将错就错使用Referer了。 | Referer: http://itbilu.com/nodejs | 固定 |
| TE | 浏览器预期接受的传输时的编码方式：可使用回应协议头Transfer-Encoding中的值（还可以使用"trailers"表示数据传输时的分块方式）用来表示浏览器希望在最后一个大小为0的块之后还接收到一些额外的字段。 | TE: trailers,deflate | 固定 |
| User-Agent | 浏览器的身份标识字符串 | User-Agent: Mozilla/…… | 固定 |
| Upgrade | 要求服务器升级到一个高版本协议。 | Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11 | 固定 |
| Via | 告诉服务器，这个请求是由哪些代理发出的。 | Via: 1.0 fred, 1.1 itbilu.com.com (Apache/1.1) | 固定 |
| Warning | 一个一般性的警告，表示在实体内容体中可能存在错误。 | Warning: 199 Miscellaneous warning | 固定 |

### Cookie

### HTTP状态码


| 状态码 | 含义 |
| - | - |
| 2xx | 成功 |
| 200 | 正常；请求已完成。 |
| 201 | 正常；紧接 POST 命令。 |
| 202 | 正常；已接受用于处理，但处理尚未完成。 |
| 203 | 正常；部分信息 — 返回的信息只是一部分。 |
| 204 | 正常；无响应 — 已接收请求，但不存在要回送的信息。 |
| 3xx | 重定向 |
| 301 | 已移动 — 请求的数据具有新的位置且更改是永久的。 #永久移动 |
| 302 | 已找到 — 请求的数据临时具有不同 URI。   #临时移动 |
| 303 | 请参阅其它 — 可在另一 URI 下找到对请求的响应，且应使用 GET 方法检索此响应。 |
| 304 | 未修改 — 未按预期修改文档。 |
| 305 | 使用代理 — 必须通过位置字段中提供的代理来访问请求的资源。 |
| 306 | 未使用 — 不再使用；保留此代码以便将来使用。 |
| 4xx | 客户机中出现的错误 |
| 400 | 错误请求 — 请求中有语法问题，或不能满足请求。 |
| 401 | 未授权 — 未授权客户机访问数据。 |
| 401.1 | 未授权：登录失败 |
| 401.2 | 未授权：服务器配置问题导致登录失败 |
| 401.3 | ACL 禁止访问资源 |
| 401.4 | 未授权：授权被筛选器拒绝 |
| 401.5 | 未授权：ISAPI 或 CGI 授权失败 |
| 402 | 需要付款 — 表示计费系统已有效。 |
| 403 | 禁止 — 即使有授权也不需要访问。<br> 对 Internet 服务管理器 (HTML) 的访问仅限于 Localhost |
| 403.1 | 禁止访问：禁止可执行访问 |
| 403.2 | - 禁止访问：禁止读访问 |
| 403.3 | - 禁止访问：禁止写访问 |
| 403.4 | - 禁止访问：要求 SSL |
| 403.5 | - 禁止访问：要求 SSL 128 |
| 403.6 | - 禁止访问：IP 地址被拒绝 |
| 403.7 | - 禁止访问：要求客户证书 |
| 403.8 | - 禁止访问：禁止站点访问 |
| 403.9 | - 禁止访问：连接的用户过多 |
| 403.10 | - 禁止访问：配置无效 |
| 403.11 | - 禁止访问：密码更改 |
| 403.12 | - 禁止访问：映射器拒绝访问 |
| 403.13 | - 禁止访问：客户证书已被吊销 |
| 403.15 | - 禁止访问：客户访问许可过多 |
| 403.16 | - 禁止访问：客户证书不可信或者无效 |
| 403.17 | - 禁止访问：客户证书已经到期或者尚未生效 |
| 404 | 找不到 — 服务器找不到给定的资源；文档不存在。 |
| 405 | 资源被禁止 |
| 406 | 无法接受 |
| 407 | 要求代理身份验证 |
| 407 | 代理认证请求 — 客户机首先必须使用代理认证自身。 |
| 410 | 永远不可用 |
| 412 | 先决条件失败 |
| 414 | 请求 - URI 太长 |
| 415 | 介质类型不受支持 — 服务器拒绝服务请求，因为不支持请求实体的格式。 |
| 5xx | 服务器中出现的错误 |
| 500 | 内部错误 — 因为意外情况，服务器不能完成请求。 |
| 500-11 | 服务器关闭 |
| 500-12 | 应用程序重新启动 |
| 500-13 | - 服务器太忙 |
| 500-14 | - 应用程序无效 |
| 500-15 | - 不允许请求 global.asa |
| 501 | 未执行 — 服务器不支持请求的工具。 |
| 502 | 错误网关 — 服务器接收到来自上游服务器的无效响应。 |
| 503 | 无法获得服务 — 由于临时过载或维护，服务器无法处理请求。 |


## Bootstrap

### 输入框组

Bootstrap 输入框组
本章将讲解 Bootstrap 支持的另一个特性，输入框组。输入框组扩展自 表单控件。使用输入框组，您可以很容易地向基于文本的输入框添加作为前缀和后缀的文本或按钮。

通过向输入域添加前缀和后缀的内容，您可以向用户输入添加公共的元素。例如，您可以添加美元符号，或者在 Twitter 用户名前添加 @，或者应用程序接口所需要的其他公共的元素。

向 .form-control 添加前缀或后缀元素的步骤如下：

1. 把前缀或后缀元素放在一个带有 class .input-group 的 &lt;div&gt; 中。
2. 接着，在相同的 &lt;div&gt; 内，在 class 为 .input-group-addon 的 &lt;span&gt; 内放置额外的内容。
3. 把该 &lt;span&gt; 放置在 &lt;input&gt; 元素的前面或者后面。

```text
为了保持跨浏览器的兼容性，请避免使用 <select> 元素，因为它们在 WebKit 浏览器中不能完全渲染出效果。也不要直接向表单组应用输入框组的 class，输入框组是一个孤立的组件。
```


Bootstrap

### 输入框组

Bootstrap 输入框组
本章将讲解 Bootstrap 支持的另一个特性，输入框组。输入框组扩展自 表单控件。使用输入框组，您可以很容易地向基于文本的输入框添加作为前缀和后缀的文本或按钮。

通过向输入域添加前缀和后缀的内容，您可以向用户输入添加公共的元素。例如，您可以添加美元符号，或者在 Twitter 用户名前添加 @，或者应用程序接口所需要的其他公共的元素。

向 .form-control 添加前缀或后缀元素的步骤如下：

1. 把前缀或后缀元素放在一个带有 class .input-group 的 &lt;div&gt; 中。
2. 接着，在相同的 &lt;div&gt; 内，在 class 为 .input-group-addon 的 &lt;span&gt; 内放置额外的内容。
3. 把该 &lt;span&gt; 放置在 &lt;input&gt; 元素的前面或者后面。

```text
为了保持跨浏览器的兼容性，请避免使用 <select> 元素，因为它们在 WebKit 浏览器中不能完全渲染出效果。也不要直接向表单组应用输入框组的 class，输入框组是一个孤立的组件。
```
