$def with (static_files, title, keywords, content)
<!-- DO NOT CHANGE THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title> $title </title>

    <style>
    #keywords { width : 400px; }
    </style>

    $static_files

</head>
<body>


<div id="container">

<div id="quick_links">
    <a href="/"> Home </a>
</div>


<h2>Search</h2>

<div id="searchbox-not-right">
    <form method="POST" action="/~search" accept-charset="utf-8">
        <input type="text" value="$keywords" name="k" id="keywords" />
        <input type="submit" value="Search" />
    </form>
</div>


<div id="result">
    $content
</div>

</div>


</body>
</html>