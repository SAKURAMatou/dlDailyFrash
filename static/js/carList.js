/**
 * 购物车列表的js
 */
const crsfToken = $("input[name=csrfmiddlewaretoken]").val()
/**
 * 购物车全选的事件
 */
$(".settlements").find(':checkbox').change(function () {
    //checkbox的checked属性，attr获取结果一直是checked；需要prop获取具体的值
    var checked = $(this).prop('checked')
    // console.log($(this).attr("checked"))
    $(".cart_list_td").find(":checkbox").each(function (i, t) {
        $(t).prop('checked', checked)
    })
})

/**
 * 单行商品的勾选改变事件
 */

$(".cart_list_td").find(":checkbox").change(function () {
    if (initAllCheck()) {
        //真说明全选了
        $("#lefPrice").text($("#totalPrice").val())
    } else {
        checkdGoodChanged();
    }
})

/**
 * 初始化全选状态
 */
function initAllCheck() {
    var checkLen = $(".cart_list_td").find(':checked').length
    var goodsCount = $(".cart_list_td").length
    var res = checkLen == goodsCount
    $(".settlements").find(':checkbox').prop('checked', res)
    return res;

}

/**
 * 勾选中的商品变化时同步调整合计;不修改默认的总件数
 */
function checkdGoodChanged() {
    var totalPrice = parseFloat($("#totalPrice").val())
    var totalCount = parseInt($("#totalCount").val())
    var unchecked = $(".cart_list_td").find("input[name='checkId']:not(:checked)")
    var goodUl = $(unchecked).parents('ul')
    // console.log(totalPrice, unchecked, goodUl)
    //没被选中的可能是多个
    var amount = $(goodUl).find("li[class='col07']")
    $(amount).each(function (i, t) {
        var np = parseFloat($(t).text().replace("元", ''))
        var count = parseInt($(t).prev().find(".num_show").val())
        totalCount -= count;
        totalPrice -= np;
    })
    // var leftPrice = totalPrice - parseFloat(amount)
    // console.log(totalPrice, amount)
    $("#lefPrice").text(totalPrice.toFixed(2))
    $("#leftCount").text(totalCount)

    // TODO 修改共计商品数量


}

$(".num_add").on('click', 'a', function () {
    var $this = $(this)
    var $pul = $this.parent().parent().parent();
    let num_show = $this.parent().find(".num_show");
    var nowCount = parseInt(num_show.val())
    // 获取当前商品id
    var goodId = $pul.attr("id")
    // console.log($pul.attr("id"))
    // console.log($this, num_show, nowCount)
    if ($this.hasClass('add')) {
        nowCount += 1
    } else if ($this.hasClass('minus')) {
        if (nowCount > 1) {
            nowCount -= 1
        } else {
            //当购物车数量为1时再减-变为零执行删除商品操作
            return goodCountDelete(goodId)
        }
    }
    var totalPrice = $("#totalPrice")
    //请求后台，修改数据库信息，如果成功则修改页面数据，失败则不调整
    $.ajax({
        url: "/car/goodInCarCountChange",
        method: "post",
        data: {
            "goodid": goodId,
            "newcount": nowCount,
            "totalPrice": totalPrice.val(),
            "csrfmiddlewaretoken": crsfToken
        },
        success: function (data) {
            // console.log(data)
            if (data.code == 1) {
                //修改计数器中的值
                num_show.val(nowCount);
                data = data.data;
                $("#totalCount").val(data.totalCount)
                $("#total_count_text").text(data.totalCount)
                totalPrice.val(data.totalPrice)
                //修改选中的商品总数，总价
                checkdGoodChanged()
            }
            // alert(data.msg)
        }
    });
})

/**
 * 购物车中商品数量变为0或者删除商品时请求后端数据
 */
function goodCountDelete(goodId) {
    var totalPrice = $("#totalPrice")
    var d = {
        "goodid": goodId,
        "totalPrice": totalPrice.val(),
        "csrfmiddlewaretoken": crsfToken
    }
    $.post('/car/deleteGood', d, function (data) {
        console.log(data)
        if (data.code == 1) {
            //修改总数，总价的隐藏域
            data = data.data
            totalPrice.val(data.totalPrice)
            $("#totalCount").val(data.totalCount)
            $("#total_count_text").text(data.totalCount)
            //页面元素的移除
            $("#" + goodId).remove()
            //重新计算选中的商品的总计，运费
            checkdGoodChanged()

        }
    })

}

//删除商品触发事件
$(".good_delete").on('click', 'a', function () {
    console.log($(this))
    var goodId = $(this).parent().parent().attr("id")
    goodCountDelete(goodId)
})