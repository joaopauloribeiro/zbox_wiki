# 安装 ZBox Wiki

## 在 OS X 上安装 ZBox Wiki

### 安装基本组件

虽然 OS X 已自带 Python 2.6 环境，但是，我强烈推荐您使用 Python 2.7 (OS X 10.7 环境默认使用只版本) 。

安装一个软件包管理系统，如 [MacPorts](http://www.macports.org)，或 [HomeBrew](http://mxcl.github.com/homebrew/)。

下面以 HomeBrew 为例。HomeBrew 默认安装软件到 /usr/local ，执行命令时不需要带 sudo/su 前缀。

安装 setuptools:

    wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e
    tar xf setuptools-0.6c11.tar.gz
    cd setuptools-0.6c11
    sudo python setup.py install


安装 Zbox Wiki:    

    sudo easy_install zbox_wiki


创建一个 Zbox Wiki 实例:

    zwadmin.py create /tmp/helloworld
    zwd.py --path /tmp/helloworld --port 8080


在浏览器中访问 [http://0.0.0.0:8080/](http://0.0.0.0:8080/) 测试。


### 安装其它可选组队

TeX/LaTeX 特性依赖:

 - TeX Live
 - dvipng 1.13+

安装 [TeXShop] [texshop] (160 M+)

安装 dvipng

    sudo port install dvipng


注意: HomeBrew 仓库并没有收录 dvipng ，所以这里使用 MacPorts 来安装相应软件包。


Graphviz 特性依赖:

 - pygraphviz


安装 pygraphviz

    sudo port install pkg-config
    sudo port install py27-pygraphviz


重启进程启用新特性，访问 [http://0.0.0.0:8080/](http://0.0.0.0:8080/) 查看结果。


## 在 Ubuntu 上安装 Zbox Wiki

### 安装基本组件

安装 setuptools

    sudo apt-get install python-setuptools


安装 ZBox wiki

    sudo easy_install zbox_wiki


创建一个 Zbox Wiki 实例:

    zwadmin.py create /tmp/helloworld
    zwd.py --path /tmp/helloworld --port 8080

在浏览器中访问 [http://0.0.0.0:8080/](http://0.0.0.0:8080/) 测试。


### 安装其它可选组队

TeX/LaTeX 特性依赖:

 - latex
 - dvipng 1.13+


DEB 系统安装软件就是爽:

    sudo apt-get install texlive-latex-base
    sudo apt-get install dvipng

Graphviz 特性依赖:

 - pygraphviz


安装 pygraphviz  (20 M +) 

    sudo apt-get install pkg-config
    sudo apt-get install python-pygraphviz


重启进程启用新特性，访问 [http://0.0.0.0:8080/](http://0.0.0.0:8080/) 查看结果。


[macports]: http://www.macports.org/install.php

[latex]: http://www.tug.org/texlive
[texlive]: http://www.tug.org/texlive
[texshop]: http://pages.uoregon.edu/koch/texshop

[dvipng]: http://savannah.nongnu.org/projects/dvipng

[pygraphviz]: http://networkx.lanl.gov/pygraphviz



----

下一步: [使用 Zbox Wiki](zbox-wiki-usage)