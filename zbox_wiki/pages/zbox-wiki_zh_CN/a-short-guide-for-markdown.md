# A Short Guide For Markdown

> Markdown is intended to be as easy-to-read and easy-to-write as is feasible.

http://daringfireball.net/projects/markdown/syntax#philosophy


## Inline/Span Elements

### Bold, Italic

source:

    a **fat boy**, a _thin girl_


Result:

a **fat boy**, a _thin girl_


### Link

source:

```
This is [Wikipedia](http://en.wikipedia.org/wiki) link.
```


Result:

This is [Wikipedia](http://en.wikipedia.org/wiki) HTML link.


### Reference-style Link

source:

```
This is [Wikipedia] [wp] link.

This is another [Wikipedia in English] [wp] link.

[wp]: http://en.wikipedia.org/wiki
```


Result:

This is [Wikipedia] [wp] link.

This is another [Wikipedia in English] [wp] link.

[wp]: http://en.wikipedia.org/wiki


### Image

source:

```
![Alt text](/path/to/img.jpg "Optional title")
```



## Block Elements


### Header/Title

source:

```
# header level 1
## header level 2
### header level 3
#### header level 4
##### header level 5
```


### Source Code I

Inline source code.


source:

```
it prints `hello world`.
```


Result:

it prints `hello world`


### Source Code II

Multiple line source code.

source:

    ```
    int
    main(void)
    {
        printf("hello");
        return 0;
    }
    ```

      
Result:

```
int 
main( void )
{
    printf( "hello" );
    return 0;
}
```


### Table

source:

```
!|| name || desc ||
!| SIP | Session Initial Protocol |
!| SIP-C | Session Initial Protocol compact version |
```

Result:

|| name || desc ||
| SIP | Session Initial Protocol |
| SIP-C | Session Initial Protocol compact version |


## Macro

### Graphviz/dot

```{{{#!dot
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


{{{#!dot
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





### TeX

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



### List files

list all files of specify path


Source:

```{{{#!zw
ls("docs/", maxdepth=3)
}}}
```


## References

 - http://daringfireball.net/projects/markdown/syntax