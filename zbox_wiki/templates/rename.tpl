$def with (config_agent, static_files, title, old_path, **view_settings)
<!-- DO NOT CHANGE THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title> $title </title>

    <style>
    #new_path { width : 400px; }
    </style>

    $static_files

</head>
<body>


<div id="container">

<h2> Rename: $old_path </h2>

<div id="rename">
    <form method="POST" accept-charset="utf-8">
        New name: <input type="text" value="$old_path" name="new_path" id="new_path" /><br />
        <div id="toolbox">
            <input type="submit" value="Rename" />
        </div>
    </form>
</div>

</div>


</body>
</html>