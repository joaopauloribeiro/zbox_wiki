# Zbox Wiki Usage

## Using Util Scripts

|| script name || description ||
| zwadmin.py | create or upgrade a Zbox Wiki instance |
| zwd.py | run a simple debug web server with specify ip/port and instance path |

Create a Zbox Wiki instance

    zwadmin.py --create /tmp/my_blog


Upgrade a Zbox Wiki instance

    zwadmin.py --upgrade /tmp/my_blog


Understand the layout of instance

    $ find /tmp/my_blog -maxdepth 1


It should be

    /tmp/my_blog
    /tmp/my_blog/nginx-debian.conf
    /tmp/my_blog/stop_fcgi.sh
    /tmp/my_blog/start_fcgi.sh
    /tmp/my_blog/fcgi_main.py
    /tmp/my_blog/static/
    /tmp/my_blog/tmp/
    /tmp/my_blog/pages/
    /tmp/my_blog/templates/
    /tmp/my_blog/sessions/


Run instance

    zwd.py --path /tmp/my_blog --port 8000


## Create, Read, Update and Delete Page

Anonymous user could create, read, update and delete page via Web interface by default.

There is a folder named **pages** in every instance, all markdown page files in it, and it is the most important thing.

From a programmer perspective, it a good idea that put whole folder pages under version control:

     mv /tmp/my_blog/pages /tmp/my_blog/pages.bak
     git init /tmp/my_blog/pages
     cd /tmp/my_blog/pages
     git remote add origin git://github.com/your_name/my_blog.git
     ...


## Custom CSS/JavaScript for Specify Page

ZBox follows this rules

 - includes full/path/to/page/*.css if they exist
 - includes full/path/to/page/*.js if they exist

or

 - includes full/path/to/instance/static/css/*.css
 - includes full/path/to/instance/static/js/*.js

If you want to include both CSS/JavaScript files in the folder of specify page and system's

append these lines into your CSS file header

    @import url(/static/default/css/zw-base.css);
    @import url(/static/default/css/zw-reader.css);
    @import url(/static/default/css/zw-toc.css);
    @import url(/static/default/js/prettify/prettify.css");


insert these lines into your Markdown page header

    <script type="text/javascript" src="/static/default/js/jquery.js"></script>
    <script type="text/javascript" src="/static/default/js/jquery-ui.js"></script>

    <script type="text/javascript" src="/static/default/js/zw-base.js"></script>
    <script type="text/javascript" src="/static/default/js/zw-toc.js"></script>

    <script type="text/javascript" src="/static/default/js/prettify/prettify.js"></script>
    <script type="text/javascript" src="/static/default/js/highlight.js"></script>


## Using Zbox Wiki as Personal Blog

TBD.


## Using Zbox Wiki as API Documentation CMS

TBD.


## Using Zbox Wiki as Wiki System

TBD.


----

Next: [Zbox Wiki Deployment](zbox-wiki-deploy)


