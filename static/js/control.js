layui.config({base: "/static/js/"}).use(["main", "laypage", "form"],
function() {
    var o = layui.jquery,
    m = layui.main,
    l = o(".table-list"),
    b = o(".handle-btn"),
    s = o(".content-search"),
    tb = "#tabletree",
    tp = "#table-pages";
    o(window).scroll(function() {
        var fh = (s.length ? s.height() : 0) + (b.length ? b.height() : 0);
        fh && o(window).scrollTop() > fh ? b.addClass("listTopFixed") : b.removeClass("listTopFixed")
    });
    if (o(tb).length) {
        layui.tabletree({
            elem: tb
        })
    }
    b.on("click", "button",
    function() {
        var t = o(this);
        var url = t.data("url");
        if (t.hasClass("layui-btn-danger") || t.hasClass("layui-btn-normal")) {
            var urlParam = m.selectTrData();
            if (urlParam.s == 1) {
                m.alert(urlParam.msg);
                return false
            }
            if (t.hasClass("layui-btn-danger")) {
                layer.confirm("确认要删除吗?", {
                      btn: ['yes','no']
                },
                function(index) {
                  var deleteid={"mid":urlParam.mid};
                  var url ="/api/del_host";
                  m.submit(url,deleteid,urlParam.st);
                  layer.close(index);
                },
                function() {
                    layer.msg('已取消', {icon: 1});
                });
            }
        }
        if (t.hasClass("layui-btn-normal")) {
        if (url){
            var urlParamchange = m.selectTrData();
            if (urlParamchange.s == 1) {
                m.alert(urlParamchange.msg);
                return false
            }
             m.open(url, t.html(),"alarmswitch")
            }
        }

    })
});
