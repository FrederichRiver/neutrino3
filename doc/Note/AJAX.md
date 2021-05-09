# AJAX

## What is AJAX?

AJAX is Asynchronous JavaScript and XML

## XMLHttpRequest

创建XMLHttpRequest对象

```javascript
xmlhttp=new XMLHttpRequest();
```

XMLHttpRequest向服务器发送请求

```javascript
xmlhttp.open("GET","test1.txt",true);
xmlhttp.send();
```

|方法|描述|
|--|--|
|open(method,url,async)|规定请求的类型、URL 以及是否异步处理请求。<br>method：请求的类型；GET 或 POST<br>url：文件在服务器上的位置<br>async：true（异步）或 false（同步）|
|send(string)|将请求发送到服务器。<br>string：仅用于 POST 请求|

使用setRequestHeader()方法添加HTTP头

```javascript
xmlhttp.open("POST","ajax_test.asp",true);
xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
xmlhttp.send("fname=Bill&lname=Gates");
```

|方法|描述|
|--|--|
|setRequestHeader(header,value)|向请求添加 HTTP 头。<br>header: 规定头的名称<br>value: 规定头的值|