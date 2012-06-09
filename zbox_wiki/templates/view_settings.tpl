$def with (enable_show_full_path, enable_auto_toc, enable_highlight, static_files)
<!-- DON NOT CHANGE IT UNLESS YOU KNOW WHAT YOU ARE DOING -->
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


            <label for="enable_show_full_path">show full path</label>

            $if enable_show_full_path:
                <input type="checkbox" id="enable_show_full_path" name="enable_show_full_path" checked="checked" />
            $else:
                <input type="checkbox" id="enable_show_full_path" name="enable_show_full_path" />
            <br />


            <label for="enable_auto_toc">auto <b>T</b>able <b>O</b>f <b>C</b>ontent</label>

            $if enable_auto_toc:
                <input type="checkbox" id="enable_auto_toc" name="enable_auto_toc" checked="checked" />
            $else:
                <input type="checkbox" id="enable_auto_toc" name="enable_auto_toc" />
            <br />


            <label for="enable_highlight">highlight source code</label>

            $if enable_highlight:
                <input type="checkbox" id="enable_highlight" name="enable_highlight" checked="checked" />
            $else:
                <input type="checkbox" id="enable_highlight" name="enable_highlight" />
            <br />



            <div id="toolbox">
                <input type="submit" value="Save" />
            </div>
        </form>
    </div>

</div>


</body>
</html>