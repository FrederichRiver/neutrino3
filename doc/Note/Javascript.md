# Javascript

## Javascript语言

### 变量的声明

构造变量名称（唯一标识符）的通用规则是：

* 名称可包含字母、数字、下划线和美元符号
* 名称必须以字母开头
* 名称也可以 $ 和 _ 开头（但是在本教程中我们不会这么做）
* 名称对大小写敏感（y 和 Y 是不同的变量）
* 保留字（比如 JavaScript 的关键词）无法用作变量名称
* 如需赋值给变量，请使用等号
* 以 var 作为语句的开头，并以逗号分隔变量

### 函数

#### JavaScript 函数语法

* JavaScript 函数通过 function 关键词进行定义，其后是函数名和括号 ()。
* 函数名可包含字母、数字、下划线和美元符号（规则与变量名相同）。
* 圆括号可包括由逗号分隔的参数：
* (参数 1, 参数 2, ...)
由函数执行的代码被放置在花括号中：{}
* function name(参数 1, 参数 2, 参数 3) {
    要执行的代码
}
* 函数参数（Function parameters）是在函数定义中所列的名称。
* 函数参数（Function arguments）是当调用函数时由函数接收的真实的值。
* 在函数中，参数是局部变量。
* 在其他编程语言中，函数近似程序（Procedure）或子程序（Subroutine）。

#### 函数调用

函数中的代码将在其他代码调用该函数时执行：
* 当事件发生时（当用户点击按钮时）
* JavaScript 代码调用时
* 自动的（自调用）

#### 函数返回

当 JavaScript 到达 return 语句，函数将停止执行。
如果函数被某条语句调用，JavaScript 将在调用语句之后“返回”执行代码。
函数通常会计算出返回值。这个返回值会返回给调用者。

## JS DOM

## jQuery

jQuery支持的事件

|||
|--|--|
|bind()|	向匹配元素附加一个或更多事件处理器|
|blur()|	触发、或将函数绑定到指定元素的 blur 事件|
|change()|	触发、或将函数绑定到指定元素的 change 事件|
|click()|	触发、或将函数绑定到指定元素的 click 事件|
|dblclick()|	触发、或将函数绑定到指定元素的 double click 事件|
|delegate()|	向匹配元素的当前或未来的子元素附加一个或多个事件处理器|
|die()|	移除所有通过 live() 函数添加的事件处理程序。|
|error()|	触发、或将函数绑定到指定元素的 error 事件|
|event.isDefaultPrevented()|	返回 event 对象上是否调用了 event.preventDefault()。|
|event.pageX|	相对于文档左边缘的鼠标位置。|
|event.pageY|	相对于文档上边缘的鼠标位置。|
|event.preventDefault()|	阻止事件的默认动作。|
|event.result|	包含由被指定事件触发的事件处理器返回的最后一个值。|
|event.target|	触发该事件的 DOM 元素。|
|event.timeStamp|	该属性返回从 1970 年 1 月 1 日到事件发生时的毫秒数。|
|event.type|	描述事件的类型。|
|event.which|	指示按了哪个键或按钮。|
|focus()|	触发、或将函数绑定到指定元素的 focus 事件|
|keydown()|	触发、或将函数绑定到指定元素的 key down 事件|
|keypress()|	触发、或将函数绑定到指定元素的 key press 事件|
|keyup()|	触发、或将函数绑定到指定元素的 key up 事件|
|live()|	为当前或未来的匹配元素添加一个或多个事件处理器|
|load()|	触发、或将函数绑定到指定元素的 load 事件|
|mousedown()|	触发、或将函数绑定到指定元素的 mouse down 事件|
|mouseenter()|	触发、或将函数绑定到指定元素的 mouse enter 事件|
|mouseleave()|	触发、或将函数绑定到指定元素的 mouse leave 事件|
|mousemove()|	触发、或将函数绑定到指定元素的 mouse move 事件|
|mouseout()|	触发、或将函数绑定到指定元素的 mouse out 事件|
|mouseover()|	触发、或将函数绑定到指定元素的 mouse over 事件|
|mouseup()|	触发、或将函数绑定到指定元素的 mouse up 事件|
|one()|	向匹配元素添加事件处理器。每个元素只能触发一次该处理器。|
|ready()|	文档就绪事件（当 HTML 文档就绪可用时）|
|resize()|	触发、或将函数绑定到指定元素的 resize 事件|
|scroll()|	触发、或将函数绑定到指定元素的 scroll 事件|
|select()|	触发、或将函数绑定到指定元素的 select 事件|
|submit()|	触发、或将函数绑定到指定元素的 submit 事件|
|toggle()|	绑定两个或多个事件处理器函数，当发生轮流的 click 事件时执行。|
|trigger()|	所有匹配元素的指定事件|
|triggerHandler()	第一个被匹配元素的指定事件|
|unbind()|	从匹配元素移除一个被添加的事件处理器|
|undelegate()|	从匹配元素移除一个被添加的事件处理器，现在或将来|
|unload()|	触发、或将函数绑定到指定元素的 unload 事件|



