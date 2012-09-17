# A Short Guide For Zbox Wiki Markdown

> Markdown is intended to be as easy-to-read and easy-to-write as is feasible.

http://daringfireball.net/projects/markdown/syntax#philosophy


**Zbox Wiki Markdown** means Markdown with Zbox Wiki extenstions.


## Bold & Italic

Source:

    a **fat** boy, a _thin_ girl


Result:

a **fat** boy, a _thin_ girl


## List

Source:

```
- item A
- item B
```

Result:

- item A
- item B


## Link

Source:

```
This is [Wikipedia](http://en.wikipedia.org/wiki) HTML link.
```


Result:

This is [Wikipedia](http://en.wikipedia.org/wiki) HTML link.


## Reference-style Link

Source:

```
This is [Wikipedia] [wp] HTML link.

This is another [Wikipedia in English] [wp] HTML link.

[wp]: http://en.wikipedia.org/wiki
```


Result:

This is [Wikipedia] [wp] link.

This is another [Wikipedia in English] [wp] link.

[wp]: http://en.wikipedia.org/wiki


## Image

Source:

```
![show this if the image does not exists](../Kubuntu-logo.png "display this if cursor over the image")
```


Result I:

![show this if the image does not exists](../Kubuntu-logo-not-exists.png "display this if cursor over the image")


Result II:

![show this if the image does not exists](../Kubuntu-logo.png "display this if cursor over the image")


## Title

Source:

```
# header level 1
## header level 2
### header level 3
#### header level 4
##### header level 5
```

There results are ugly, here ignore them.


## Highlight Inline Source Code

Source:

```
it prints `hello world`.
```


Result:

it prints `hello world`


## Highlight Multiple Lines Source Code

Source:

    ```
    int main(nt argc, char *argv[])
    {
        printf("hello world \n");
        return 0;
    }
    ```

      
Result:

```
int main(int argc, char *argv[])
{
    printf("hello world \n");
    return 0;
}
```


## Table

Source:

```
!|| name || desc ||
!| SIP | Session Initial Protocol |
!| SIP-C | Session Initial Protocol compact version |
```

Result:

|| name || desc ||
| SIP | Session Initial Protocol |
| SIP-C | Session Initial Protocol compact version |


## Macro graphviz

Source:

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


Result:

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


## Macro tex

Source:

```{{{#!tex
E_k = \frac{1}{2}m_0 v^2 + \cdots
}}}
```


Result:

{{{
#!tex
E_k = \frac{1}{2}m_0 v^2 + \cdots

...

E = m c^2
}}}


## Macro ls

list all files of specify path


Source:

```{{{#!zw
ls("zbox-wiki/", maxdepth=3)
}}}
```

Result：

{{{#!zw
ls("zbox-wiki/", maxdepth=3)
}}}


## Macro cat

show file content of specify file(s)

Source:

```{{{#!zw
cat("*.c")
}}}
```




## References

 - http://daringfireball.net/projects/markdown/syntax



