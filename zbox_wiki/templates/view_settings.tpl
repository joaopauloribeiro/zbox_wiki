$def with (static_files, **view_settings)
<!-- DO NOT CHANGE THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>View Settings</title>

    <style>
        #new_path { width : 400px; }
    </style>

    $if static_files:
        $static_files

</head>
<body>


<div id="container">

    <h1>View Settings</h1>

    <div id="view-settings">
        <form method="POST" action="/~settings">


            <label for="show_full_path">show full path</label>

            $if view_settings["show_full_path"]:
                <input type="checkbox" id="show_full_path" name="show_full_path" checked="checked" />
            $else:
                <input type="checkbox" id="show_full_path" name="show_full_path" />
            <br />


            <label for="auto_toc">auto <b>T</b>able <b>O</b>f <b>C</b>ontent</label>

            $if view_settings["auto_toc"]:
                <input type="checkbox" id="auto_toc" name="auto_toc" checked="checked" />
            $else:
                <input type="checkbox" id="auto_toc" name="auto_toc" />
            <br />


            <label for="highlight_code">highlight source code</label>

            $if view_settings["highlight_code"]:
                <input type="checkbox" id="highlight_code" name="highlight_code" checked="checked" />
            $else:
                <input type="checkbox" id="highlight_code" name="highlight_code" />
            <br />



            <div id="toolbox">
                <input type="submit" value="Save" />
            </div>
        </form>
    </div>

</div>


</body>
</html>