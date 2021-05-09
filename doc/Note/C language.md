# C Language

## 程序编译过程

### 编译流程

1. 预处理
宏定义展开，头文件展开，条件编译
2. 编译
检查语法，编译后生成汇编文件
3. 汇编
汇编生成二进制文件
4. 链接
把库链接到成可执行文件中

### 编译命令

gcc -o file file.c

## stdlib库

### system函数

```c
include <stdlib.h>
int main(void)
{
    system("calc");
    return 0;
}
```

