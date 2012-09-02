# Example Graphviz in Zbox Wiki

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