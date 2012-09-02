# 例子： 在 Zbox Wiki 里面使用 Graphviz

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
