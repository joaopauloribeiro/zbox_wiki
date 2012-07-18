# Zbox Wiki Usage

## Util Scripts

|| script name || description ||
| zwadmin.py | create or upgrade a zbox wiki instance |
| zwd.py | run a simple debug web server with specify ip/port and instance path |


## Customization

There is a MS-Windows ini style configuration file named default.cfg in every Zbox Wiki instance,    
you should custom it to satisfy your need.

section _main_

|| Option || Default Value || desc || Note ||
| version | 201204 | _ | DO NOT CHANGE IT |
| debug | 0 | output log | _ |
| error_log_path | None | _ |  _ |
| readonly | 1 | disable create/update/delete/rename page via Web interface anonymous | _ | 
| maintainer_email | shuge.lee@gmail.com | this E-Mail will show in readonly warning page and footer | _ |
| repository_url | git://github.com/shuge/zbox_wiki.git | it will show in readonly warning page | _ | 


section _paths_

|| Option || Default Value || desc || Note ||
| instance_full_path | _ | a.k.a. **path prefix** | DO NOT CHANGE IT  | 
| pages_path | path prefix(pass from zwd.py) + "/pages" | _ | _ | 
| static_path | path prefix + "/static" | _ | _ |
| sessions_path | path prefix + "/sessions" | _ | _ |
| tmp_path | path prefix + "/tmp " | _ | _ | 
| templates_path | templates + "/tmp " | _ | _ |


section _cache_

|| Option || Default Value || desc || Note ||
| cache_update_interval | 60 (1 minute) | craete a flat file to save the files list of /path/to/pages | _ |


section _pagination_

|| Option || Default Value || desc || Note ||
| page_limit | 50 | _ | _ | 
| search_page_limit | 100 | _ | _ | 


section _frontend_

|| Option || Default Value || desc || Note ||
| enable_show_full_path | 0 | show full path of page file instead of page title(h1) in the list view  | _ | 
| enable_auto_toc | 1 | show table of content on the top-right | _ | 
| enable_highlight | 1 | highlight source code | see also [Google Code Prettify](http://code.google.com/p/google-code-prettify) | 

|| Option || Default Value || desc || Note ||
| enable_show_quick_links | 1 | show Home/Recent Change/All/Settings link on the header | _ | 
| enable_show_home_link | 1 | show Home link on the header | _ | 
| home_link_name | Home | the name of Home link on the header | _ | 

|| Option || Default Value || desc || Note ||
| enable_button_mode_path | 1 | | _ | 
| enable_show_source_button | 1 | show view source of page button on the footer | _ | 
| enable_reader_mode | 1 | enable Safari Reader mode for page | _ | 


Next: [A Short Guide for Markdown](a-short-guide-for-markdown)