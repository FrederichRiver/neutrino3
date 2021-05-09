# Python3

## 内置函数

### super函数

super() 函数是用于调用父类(超类)的一个方法。

super() 是用来解决多重继承问题的，直接用类名调用父类方法在使用单继承的时候没问题，但是如果使用多继承，会涉及到查找顺序（MRO）、重复调用（钻石继承）等种种问题。

MRO 就是类的方法解析顺序表, 其实也就是继承父类方法时的顺序表。

```python
super(type[, object-or-type])
super(Class, self).__init__()
super().__init__()
```

## Requests库

### requests.get方法

* timeout: 超时设定
* headers: 请求头
* cookies: cookie

### Response对象

* status_code
* text：文本内容
* encoding: 文本编码
* content: 二进制内容
* headers: 响应头
* cookies: cookie
* raw: 原始响应内容
* json: json解码器

## Pandas

### pandas.read_html

```python
pandas.read_html(io, match='.+', flavor=None, header=None, index_col=None, skiprows=None, attrs=None, parse_dates=False, thousands=',', encoding=None, decimal='.', converters=None, na_values=None, keep_default_na=True, displayed_only=True)
```

Parameters:

* io: str, path object or file-like object
A URL, a file-like object, or a raw string containing HTML. Note that lxml only accepts the http, ftp and file url protocols. If you have a URL that starts with 'https' you might try removing the 's'.

* match: str or compiled regular expression, optional
The set of tables containing text matching this regex or string will be returned. Unless the HTML is extremely simple you will probably need to pass a non-empty string here. Defaults to ‘.+’ (match any non-empty string). The default value will return all tables contained on a page. This value is converted to a regular expression so that there is consistent behavior between Beautiful Soup and lxml.

* flavorstr, optional
The parsing engine to use. ‘bs4’ and ‘html5lib’ are synonymous with each other, they are both there for backwards compatibility. The default of None tries to use lxml to parse and if that fails it falls back on bs4 + html5lib.

* header: int or list-like, optional
The row (or list of rows for a MultiIndex) to use to make the columns headers.

* index_col: int or list-like, optional
The column (or list of columns) to use to create the index.

* skiprows: int, list-like or slice, optional
Number of rows to skip after parsing the column integer. 0-based. If a sequence of integers or a slice is given, will skip the rows indexed by that sequence. Note that a single element sequence means ‘skip the nth row’ whereas an integer means ‘skip n rows’.

* attrs: dict, optional
This is a dictionary of attributes that you can pass to use to identify the table in the HTML. These are not checked for validity before being passed to lxml or Beautiful Soup. However, these attributes must be valid HTML table attributes to work correctly. For example,

attrs = {'id': 'table'}
is a valid attribute dictionary because the ‘id’ HTML tag attribute is a valid HTML attribute for any HTML tag as per this document.

attrs = {'asdf': 'table'}
is not a valid attribute dictionary because ‘asdf’ is not a valid HTML attribute even if it is a valid XML attribute. Valid HTML 4.01 table attributes can be found here. A working draft of the HTML 5 spec can be found here. It contains the latest information on table attributes for the modern web.

parse_datesbool, optional
See read_csv() for more details.

thousandsstr, optional
Separator to use to parse thousands. Defaults to ','.

encodingstr, optional
The encoding used to decode the web page. Defaults to None.``None`` preserves the previous encoding behavior, which depends on the underlying parser library (e.g., the parser library will try to use the encoding provided by the document).

decimalstr, default ‘.’
Character to recognize as decimal point (e.g. use ‘,’ for European data).

convertersdict, default None
Dict of functions for converting values in certain columns. Keys can either be integers or column labels, values are functions that take one input argument, the cell (not column) content, and return the transformed content.

na_valuesiterable, default None
Custom NA values.

keep_default_nabool, default True
If na_values are specified and keep_default_na is False the default NaN values are overridden, otherwise they’re appended to.

displayed_onlybool, default True
Whether elements with “display: none” should be parsed.

Returns
dfs
A list of DataFrames.

## SQLAlChemy

### ORM语法

* 查询
```python
# query from a class
results = session.query(User).filter_by(name='ed').all()

# query with multiple classes, returns tuples
results = session.query(User, Address).join('addresses').filter_by(name='ed').all()

# query using orm-columns, also returns tuples
results = session.query(User.name, User.fullname).all()
```

## Image

skimage即是Scikit-Image。基于python脚本语言开发的数字图片处理包，比如PIL,Pillow, opencv, scikit-image等。

     PIL和Pillow只提供最基础的数字图像处理，功能有限；opencv实际上是一个c++库，只是提供了python接口，更新速度非常慢。scikit-image是基于scipy的一款图像处理包，它将图片作为numpy数组进行处理，正好与matlab一样，因此，我们最终选择scikit-image进行数字图像处理。
      skimage包的全称是scikit-image SciKit (toolkit for SciPy) ，它对scipy.ndimage进行了扩展，提供了更多的图片处理功能。它是由python语言编写的，由scipy 社区开发和维护。skimage包由许多的子模块组成，各个子模块提供不同的功能。主要子模块列表如下：
子模块名称　                主要实现功能
io                            读取、保存和显示图片或视频
data                       提供一些测试图片和样本数据
color                           颜色空间变换
filters             图像增强、边缘检测、排序滤波器、自动阈值等
draw               操作于numpy数组上的基本图形绘制，包括线条、矩形、圆和文本等
transform          几何变换或其它变换，如旋转、拉伸和拉东变换等
morphology          形态学操作，如开闭运算、骨架提取等
exposure              图片强度调整，如亮度调整、直方图均衡等
feature                        特征检测与提取等
measure                  图像属性的测量，如相似性或等高线等
segmentation                          图像分割
restoration                           图像恢复
util                                  通用函数
