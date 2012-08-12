# Zbox Wiki Markdown 简明指南

> Markdown is intended to be as easy-to-read and easy-to-write as is feasible.

> Markdown 的目标是灵活、易读易写。

官方网站： http://daringfireball.net/projects/markdown/syntax#philosophy


## 粗体及斜体

代码：

    死**胖子**和 _Geek_ 女


结果：

死**胖子**和 _Geek_ 女


注意：英文与中文排版的习惯差异，中文不应该使用任何斜体，因为它会降低可读性。


## 链接

代码：

```
这是 [维基百科](http://en.wikipedia.org/wiki) HTML 链接。
```


结果：

这是 [维基百科](http://en.wikipedia.org/wiki) HTML 链接。


## 引用式链接

代码：

```
这是 [维基百科] [wp] HTML 链接.

这是 [维基百科 英文版] [wp] HTML 链接.

[wp]: http://en.wikipedia.org/wiki
```


结果：

这是 [维基百科] [wp] HTML 链接.

这是 [维基百科 英文版] [wp] HTML 链接.

[wp]: http://en.wikipedia.org/wiki


## 图片

代码：

```
![如果图片无法显示，用此文字代替](../Kubuntu-logo.png "鼠标停留在图片上时显示的文字")
```


引用不正常时的结果：

![如果图片无法显示，用此文字代替](../Kubuntu-logo-not-exists.png "鼠标停留在图片上时显示的文字")


引用正常时的结果：

![如果图片无法显示，用此文字代替](../Kubuntu-logo.png "鼠标停留在图片上时显示的文字")


## 标题

代码：

```
# header level 1
## header level 2
### header level 3
#### header level 4
##### header level 5
```

结果就不显示了。


## 高亮行内代码


代码：

```
输出 `hello world`.
```


结果：

输出 `hello world`


## 高亮多行代码

代码：

    ```
    int main(int argc, char *argv[])
    {
        printf("hello world \n");
        return 0;
    }
    ```
      
结果：

```
int main(int argc, char *argv[])
{
    printf("hello world \n");
    return 0;
}
```


## 表格

代码：

```
!|| 名称 || 描述 ||
!| SIP | Session Initial Protocol |
!| SIP-C | Session Initial Protocol compact version |
```

结果：

|| 名称 || 描述 ||
| SIP | Session Initial Protocol |
| SIP-C | Session Initial Protocol compact version |


## Graphviz/dot 宏

代码：

```{{{#!graphviz
digraph arch {
    rankdir = "LR"

    webpy [ label = "Web.py" ]
    py [ label = "Python" ]
    zbwiki [ label = "ZBoxWiki" ]

    webpy -> py
    zbwiki -> webpy
    
    Markdown -> zbwiki
    Graphviz -> zbwiki
    TeX -> zbwiki
}
}}}
```

结果：

{{{#!graphviz
digraph arch {
    rankdir = "LR"

    webpy [ label = "Web.py" ]
    py [ label = "Python" ]
    zbwiki [ label = "ZBoxWiki" ]

    webpy -> py
    zbwiki -> webpy
    
    Markdown -> zbwiki
    Graphviz -> zbwiki
    TeX -> zbwiki
}
}}}



## TeX 宏

代码：

```{{{#!tex
E_k = \frac{1}{2}m_0 v^2 + \cdots
}}}
```


结果：

{{{
#!tex
E_k = \frac{1}{2}m_0 v^2 + \cdots

...

E = m c^2
}}}


## ls 宏

列出指定目录的文件列表

代码：

```{{{#!zw
ls("zbox-wiki_zh_CN/", maxdepth=3)
}}}
```

结果：

{{{#!zw
ls("zbox-wiki_zh_CN/", maxdepth=3)
}}}


## 参考链接

 - http://daringfireball.net/projects/markdown/syntax



