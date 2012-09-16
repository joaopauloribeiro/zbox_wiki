# 使用 Zbox Wiki

## 使用 Zbox Wiki 自带实用脚本

|| 脚本名 || 描述 ||
| zwadmin.py | 创建或升级一个 Zbox Wiki 实例 |
| zwd.py | 以 Debug 模式，在指定 IP地址/端口及实例目录，运行一个简单的 Web server |


创建一个 Zbox Wiki 实例

    zwadmin.py --create /tmp/my_blog


升级一个 Zbox Wiki 实例

    zwadmin.py --upgrade /tmp/my_blog


理解实例的文件布局

    $ find /tmp/my_blog -maxdepth 1


大概这样：

    /tmp/my_blog
    /tmp/my_blog/nginx-debian.conf   # 用于在 NGINX 上部署 
    /tmp/my_blog/stop_fcgi.sh   # 用于在 NGINX 上部署 
    /tmp/my_blog/start_fcgi.sh   # 用于在 NGINX 上部署 
    /tmp/my_blog/fcgi_main.py   # 用于在 NGINX 上部署 
    /tmp/my_blog/static/  # CSS/JavaScript 文件目录
    /tmp/my_blog/tmp/  
    /tmp/my_blog/pages/  # Markdown 源文件 保存目录
    /tmp/my_blog/templates/  # HTML 模板文件
    /tmp/my_blog/sessions/  # HTTP Session 保存目录


运行实例

    zwd.py --path /tmp/my_blog --port 8000


## 创建，访问，更新和删除页面

默认地，匿名用户可以通过 Web 界面创建，访问，更新和删除任何页面。

每个实例下有一个名为 pages 的目录，所有的 Markdown 文件都会保存到此目录下。
它是实例里最重要的目录。

从一个程序员的角度看，为 folder 增加版本控制是个好主意。

     mv /tmp/my_blog/pages /tmp/my_blog/pages.bak
     git init /tmp/my_blog/pages
     cd /tmp/my_blog/pages
     git remote add origin git://github.com/your_name/my_blog.git
     ...


## 定制某个页面的 CSS/JavaScript 

Zbox 渲染每个 Markdown 文件为 HTML 文件时，会遵循以下规则：

 - 如果某个 Markdown 文件所在的目录下包含 *.css 文件，则自动包含它们，并且不包含系统默认的 CSS 文件
 - 如果某个 Markdown 文件所在的目录下包含 *.js 文件，则自动包含它们，并且不包含系统默认的 JavaScript 文件

或者

 - 只包含系统默认的 CSS 文件，full/path/to/instance/static/css/*.css
 - 只包含系统默认的 JavaScript 文件，full/path/to/instance/static/css/*.js


如果您想使用自定义 CSS 的同时包含系统默认 CSS，则添加以下内容到某个页面所在目录的主 CSS 文件里面：

    @import url(/static/default/css/zw-base.css);
    @import url(/static/default/css/zw-reader.css);
    @import url(/static/default/css/zw-toc.css);
    @import url(/static/default/js/prettify/prettify.css");


类似地，将以下内容添加到某个页面对应的 Markdown 文件顶部(每行前面不带空格)：

    <script type="text/javascript" src="/static/default/js/jquery.js"></script>
    <script type="text/javascript" src="/static/default/js/jquery-ui.js"></script>

    <script type="text/javascript" src="/static/default/js/zw-base.js"></script>
    <script type="text/javascript" src="/static/default/js/zw-toc.js"></script>

    <script type="text/javascript" src="/static/default/js/prettify/prettify.js"></script>
    <script type="text/javascript" src="/static/default/js/highlight.js"></script>


## 示例：使用 Zbox Wiki 作为 个人博客

待完成。


## 示例：使用 Zbox Wiki 作为 应用程序接口文档 内容管理系统

待完成。


## 示例：使用 Zbox Wiki 作为 维基系统

待完成。


----

下一步: [部署 Zbox Wiki](zbox-wiki-deploy)

