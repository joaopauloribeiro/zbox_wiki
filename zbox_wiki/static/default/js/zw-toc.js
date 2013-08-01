//
// This TOC implementation is inspired by Janko Jovanovic,
// http://www.jankoatwarpspeed.com/post/2009/08/20/Table-of-contents-using-jQuery.aspx
//
var G_SHOW_TOC_IF_HEADERS_COUNT = 2;

var auto_generate_toc = function () {
  var headers_list = document.querySelectorAll('h2, h3, h4, h5, h6');
  if (!headers_list.length || (headers_list.length < G_SHOW_TOC_IF_HEADERS_COUNT)) {
    return;
  }

  var toc_element = $("#toc");
  if (!toc_element.length && headers_list.length) {
    $("#content").before(
      $('<div id="toc" class="draggable" />').append('<p class="bolder">Table of Contents</p><ul />')
    );

    $(".draggable").draggable();
  }


  $("h2, h3, h4, h5, h6").each(function (i) {
    var cur = $(this);
    var new_anchor = cur.text().replace(/ /g, '-').toLowerCase();
    cur.attr("id", new_anchor);

    // var pos = cur.position().top / $("#content").height() * $(window).height();

    var id_ = "link" + i;
    var class_ = cur[0].tagName.toLowerCase();
    var href_ = "#" + new_anchor;
    var title = cur.html();
    var text = cur.html();
    var element = '<li><a id="' + id_ + '" class="' + class_ + '" href="' + href_ + '" title="' + title + '">' + text + '</a></li>';

    $("#toc ul").append(element);

    // $("#link" + i).css("top", pos);
  });

  var zIndexNumber = 10000;
  $("#toc").css('zIndex', zIndexNumber)
    .attr("title", "this is draggable and resizable");
}

$(document).ready(function () {
  auto_generate_toc();
});