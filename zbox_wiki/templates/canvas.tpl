$def with (config, static_files, button_path, req_path, title, content, paginator = None, **view_settings)
<!-- DO NOT CHANGE THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title> $title </title>
    <link rel="shortcut icon" href="/static/favicon.ico" />

    $static_files

</head>
<body>


<div id="container">
$if view_settings["show_home_link"] or view_settings["show_quick_links"]:
    <div id="quick_links">
        $if view_settings["show_home_link"]:
            $ home_link_name = config.get("frontend", "home_link_name")
            <a href="/"> $home_link_name </a>

        $if view_settings["show_quick_links"]:
            <a href="/~recent"> Recent Changes </a>
            <a href="/~all"> All </a>
            <a href="/~settings"> Settings </a>

        $if not config.getboolean("main", "readonly"):
            <a href="/~new"> Create Page </a>
    </div>

<div id="searchbox">
    <form method="POST" action="/~search" accept-charset="utf-8">
        <input type="text" name="k" class="auto-increase-width-size" />
        <input type="submit" value="Search" />
    </form>
</div>

$if button_path:
    <div id="button_path"> $button_path </div>

$if paginator:
    $if paginator.has_previous_page:
        <div id="previous_page_btn"><a href="$paginator.previous_page_url"> previous </a></div>

    $if paginator.has_next_page:
        <div id="next_page_btn"><a href="$paginator.next_page_url"> next </a></div>


<div id="content"> $content </div>

$if view_settings["show_toolbox"]:
    <div id="toolbox">
        $if view_settings["show_view_source_button"]:
            <a href="/$req_path?action=source"> Source </a>

        $if not config.getboolean("main", "readonly"):
            <a href="/$req_path?action=delete"> Delete </a>
            <a href="/$req_path?action=rename"> Rename </a>
            <a href="/$req_path?action=update"> Update </a>

    </div>


</div>

$if config.getboolean("main", "readonly") and config.get("main", "maintainer_email"):
    $ email = config.get("main", "maintainer_email_prefix") + '<span class="hide">null</span>@' + config.get("main", "maintainer_email_suffix")
    <footer>
        <p> Maintainer: $email </p>
    </footer>

</body>
</html>
