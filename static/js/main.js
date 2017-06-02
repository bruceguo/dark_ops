layui.define(["jquery", "layer"],
function(exports) {
    var $ = layui.jquery,
    layer = layui.layer;
    var api = {
        open: function(url, title, btn, area, full, topFull) {
            var param = {
                type: 2,
                title: title,
                closeBtn: 1,
                shade: 0.1,
                maxmin: true,
                move: false,
                area: area ? area: ["600px", "90%"],
                btn: btn ? btn: ["提交", "重置"],
                content: url,
                yes: function(index, layero) {
                    var array = layer.getChildFrame("form").serializeArray();
                    var fd = {};
                    $.each(array,function() {
                        fd[this.name] = this.value
                    });
                    api.submit(url, fd)
                },
                btn2: function(index, layero) {
                    var formObj = layer.getChildFrame("form");
                    formObj[0].reset();
                    return false
                }
            };
            if (topFull) {
                top.layer.full(top.layer.open(param))
            } else {
                if (full) {
                    layer.full(layer.open(param))
                } else {
                    layer.open(param)
                }
            }
        },
        submit: function(url, data,st) {
            $.ajax({
                type: "post",
                url: url,
                data: data,
                dataType: "json",
                success: function(result) {
                console.log(result.error)
                if (result.error == 0) {
                    st.remove();
                    api.alert("已删除")
                    }else{
                        api.alert(result.msg);
                        }
              }
            })
        },
        alert: function(msg) {
            layer.alert(msg, {
                title: "提示",
                move: false
            })
        },
        jsonStringToObj: function(jsonString) {
            try {
                var json = eval("(" + jsonString + ")")
            } catch(e) {
                return ""
            }
            return json
        },
        selectTrData: function() {
            var st = $(".table-list").find(".layui-table tbody .tableTrSelect");
            if (st.length < 1) {
                return {
                    s: 1,
                    msg: "请选中操作行"
                }
            }
            var mid = st.data("mid");
            console.log(mid);
            if (!mid) {
                return {
                    s: 1,
                    msg: "无法获取mid"
                }
            }else{
                return {
                    mid:mid,
                    msg:"获取mid成功",
                    st:st
                }
            }
        },
        urlDataValue: function(name) {
            var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return unescape(r[2])
            }
            return null
        }
    };
    exports("main", api)
});
