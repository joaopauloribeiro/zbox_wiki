# Zbox Wiki 的配置文件

每个 Zbox Wiki 实例中都会有一个叫 default.cfg 的配置文件。
通过修改它可以满足您很多需求。

## _main_ 节点

|| 选项名 || 默认值 || 描述 || 备注 ||
| version | 201204 | _ | 不要乱改，除非你知道在做什么！ |
| debug | 0 | 是否输出日志 | _ |
| readonly | 0 | 不允许匿名通过浏览器用户创建/更新/删除/重命名页面 | _ | 
| maintainer_email | shuge.lee@gmail.com | 在只读警告页面及每个页面页脚显示的 E-mail | _ |
| repository_url | git://github.com/shuge/zbox_wiki.git | 在只读页面显示的版本仓库 URL | _ | 


## _paths_ 节点

|| 选项名 || 默认值 || 描述 || 备注 ||
| instance_full_path | _ | 实例的绝对路径，也称为 **path prefix** | 不要乱改，除非你知道在做什么！ | 
| pages_path | path prefix(pass from zwd.py) + "/pages" | _ | _ | 
| static_path | path prefix + "/static" | _ | _ |
| sessions_path | path prefix + "/sessions" | _ | _ |
| tmp_path | path prefix + "/tmp " | _ | _ | 
| templates_path | templates + "/tmp " | _ | _ |


## _cache_  节点

|| 选项名 || 默认值 || 描述 || 备注 ||
| cache_update_interval | 60 (1 分钟) | 更新（不存在则自动创建） pages/ 目录下文件列表时间间隔 | _ |


## _pagination_  节点

|| 选项名 || 默认值 || 描述 || 备注 ||
| page_limit | 50 | 分页里 页面数 上限 | _ | 
| search_page_limit | 100 | 搜索页面里 匹配页面数 上限 | _ | 


## _frontend_  节点

|| 选项名 || 默认值 || 描述 || 备注 ||
| enable_show_full_path | 0 | 在列表页，显示 页面的 相对路径，代替 页面的 h1 标题 | 
| enable_auto_toc | 1 | 在页面右上角显示 内容索引表（Table Of Content) | _ | 
| enable_highlight | 1 | 高亮代码 | 具体实现见 [Google Code Prettify](http://code.google.com/p/google-code-prettify) | 

|| 选项名 || 默认值 || 描述 || 备注 ||
| enable_show_quick_links | 1 | 在页首显示快速链接栏（包含 Home，Recent Change，All 和 Settings 链接） | _ | 
| enable_show_home_link | 1 | 在页首显示 Home 链接 | _ | 
| home_link_name | "Home" | 页首 Home 链接的名称 | _ | 

|| 选项名 || 默认值 || 描述 || 备注 ||
| enable_button_mode_path | 1 | 使用 Windows 7 文件管理器/KDE Dolphin/GNOME Nautilus 地址栏式 按钮路径 | _ | 
| enable_show_source_button | 1 | 在页脚显示查看页面源代码的“Source”按钮 | _ | 
| enable_reader_mode | 1 | 为页面启用 Safari 阅读模式 | _ | 


----

下一步: [Zbox Wiki Markdown 简明指南](a-short-guide-for-zbox-wiki-markdown)


