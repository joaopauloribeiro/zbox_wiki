# Zbox Wiki Configuration File

There is a MS-Windows ini style configuration file named **default.cfg** in every Zbox Wiki instance,    
you could custom it to satisfy your need.

## Section _main_

|| Option || Default Value || Desc || Note ||
| version | 201204 | _ | DO NOT CHANGE IT |
| debug | 0 | enable output log | _ |
| readonly | 1 | disable anonymous user create/update/delete/rename page via Web interface | _ | 
| maintainer_email | shuge.lee@gmail.com | it will show in read-only warning page and footer | _ |
| repository_url | git://github.com/shuge/zbox_wiki.git | it will show in read-only warning page | _ | 


## Section _paths_

|| Option || Default Value || Desc || Note ||
| instance_full_path | _ | a.k.a. **path prefix** | DO NOT CHANGE IT  | 
| pages_path | path prefix(pass from zwd.py) + "/pages" | _ | _ | 
| static_path | path prefix + "/static" | _ | _ |
| sessions_path | path prefix + "/sessions" | _ | _ |
| tmp_path | path prefix + "/tmp " | _ | _ | 
| templates_path | path prefix + "/templates" | _ | _ |


## Section _cache_

|| Option || Default Value || Desc || Note ||
| cache_update_interval | 60 (1 minute) | interval of updating files list of /path/to/pages | _ |


## Section _pagination_

|| Option || Default Value || Desc || Note ||
| page_limit | 50 | show how much pages in pagination | _ | 
| search_page_limit | 100 | show how much matched items in search result page | _ | 


## Section _frontend_

|| Option || Default Value || Desc || Note ||
| enable_show_full_path | 0 | show full path of page file instead of page title(h1) in the list view  | _ | 
| enable_auto_toc | 1 | show Table Of Content on the top-right | _ | 
| enable_highlight | 1 | highlight source code | see also [Google Code Prettify](http://code.google.com/p/google-code-prettify) | 

|| Option || Default Value || Desc || Note ||
| enable_show_quick_links | 1 | show Quick Links (includes **Home**/**Recent Change**/**All**/**Settings** links) on the header | _ | 
| enable_show_home_link | 1 | show **Home** link on the header | _ | 
| home_link_name | "Home" | the name of **Home** link on the header | _ | 

|| Option || Default Value || Desc || Note ||
| enable_button_mode_path | 1 | Windows 7 Explorer/KDE Dolphin/GNOME Nautilus Location style path | _ | 
| enable_show_source_button | 1 | show view source of page button on the footer | _ | 
| enable_reader_mode | 1 | enable Safari Reader mode for page | _ | 


----

Next: [A Short Guide for Zbox Wiki Markdown](a-short-guide-for-zbox-wiki-markdown)


