# ZBox Wiki Installation

## ZBox Wiki Installation for OS X

### Basics

OS X ships Python 2.6 by default, I strongly recommend 2.7 to you.

Install a package management system on OS X, such as [MacPorts](http://www.macports.org/), or [HomeBrew](http://mxcl.github.com/homebrew/), then use it to install other required packages.

NOTE: HomeBrew is cool, but I failed to install some packages with HomeBrew on OS X 10.6.

I do example with MacPorts following.


Install setuptools:

    wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e
    tar xf setuptools-0.6c11.tar.gz
    cd setuptools-0.6c11
    sudo python setup.py install


Install Zbox Wiki:    

    sudo easy_install -U zbox_wiki


Create a Zbox Wiki instance:

    zwadmin.py create /tmp/helloworld
    zwd.py --path /tmp/helloworld --port 8080


Visit [http://0.0.0.0:8080/](http://0.0.0.0:8080/)


### Advanced

Simple TeX feature requires:

 - TeX Live
 - dvipng 1.13+

Install [TeXShop] [texshop] (160 M+)

Install dvipng

    sudo port install dvipng


Simple Graphviz feature requires:

 - pygraphviz


Install pygraphviz

    sudo port install pkg-config
    sudo port install py27-pygraphviz


Install pygraphviz (20 M +) on Debian/Ubuntu

    sudo apt-get install pkg-config
    sudo apt-get install python-pygraphviz


Restart the process for enabling new features, visit [http://0.0.0.0:8080/](http://0.0.0.0:8080/)


## Zbox Wiki Installation for Ubuntu

### Basics

Install setuptools

    sudo apt-get install python-setuptools


Install ZBox wiki

    sudo easy_install -U zbox_wiki


Create a Zbox Wiki instance:

    zwadmin.py create /tmp/helloworld
    zwd.py --path /tmp/helloworld --port 8080


Visit [http://0.0.0.0:8080/](http://0.0.0.0:8080/)


### Advanced

Simple TeX feature requires:

 - latex
 - dvipng 1.13+

Install them

    sudo apt-get install texlive-latex-base
    sudo apt-get install dvipng


Simple Graphviz feature requires:

 - pygraphviz

Install pygraphviz (20 M +) 

    sudo apt-get install pkg-config
    sudo apt-get install python-pygraphviz

Restart the process for enabling new features, visit [http://0.0.0.0:8080/](http://0.0.0.0:8080/)


[macports]: http://www.macports.org/install.php

[latex]: http://www.tug.org/texlive
[texlive]: http://www.tug.org/texlive
[texshop]: http://pages.uoregon.edu/koch/texshop

[dvipng]: http://savannah.nongnu.org/projects/dvipng

[pygraphviz]: http://networkx.lanl.gov/pygraphviz



----

Next: [Zbox Wiki Usage](zbox-wiki-usage)


