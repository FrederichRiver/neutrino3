# XML可扩展标记语言

XML（EXtensible Markup Language）
XML 被设计用来传输和存储数据。
HTML 被设计用来显示数据。

## XML格式

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<note>
<to>George</to>
<from>John</from>
<heading>Reminder</heading>
<body>Don't forget the meeting!</body>
</note>
```

* 第一行是 XML 声明。它定义 XML 的版本 (1.0) 和所使用的编码 (ISO-8859-1 = Latin-1/西欧字符集)。
* XML 文档必须包含根元素。该元素是所有其他元素的父元素。
* 所有 XML 元素都须有关闭标签
* XML 标签对大小写敏感
* XML 必须正确地嵌套
* XML 的属性值须加引号
* 实体引用，使用转义字符来表达
* XML 中的注释
* 在 XML 中，空格会被保留
* XML 以 LF 存储换行

