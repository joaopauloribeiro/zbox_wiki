$def with (config_agent, static_files, req_path, title, content, create_new, **view_settings)
<!-- DO NOT CHANGE THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title> $title </title>

    $static_files

</head>
<body>


<div id="container">

<div id="editor">
    <form method="POST" accept-charset="utf-8">
        <div id="path-widget">
            $if create_new:
                <p>Create</p> 
                <label for="path"> Path :</label>
                <input type="text" id="path" name="path" value="$req_path" />
            $else:
                <p>Update path:</p>
                <p>$req_path</p>
        </div>

        <div class="input-widget">
            <label for="content"> Content </label>
            <textarea cols="80" rows="20" id="content" name="content">$content</textarea>
        </div>

        <div id="toolbox">
            <input type="submit" value="Update" />
        </div>

    </form>
</div>

</div>


</body>
</html>