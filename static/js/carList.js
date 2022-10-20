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
 * 勾选中的商品变化时同步调整合计
 */
function checkdGoodChanged() {
    var totalPrice = parseFloat($("#totalPrice").val())
    var unchecked = $(".cart_list_td").find("input[name='checkId']:not(:checked)")
    var goodUl = $(unchecked).parents('ul')
    // console.log(totalPrice, unchecked, goodUl)
    //没被选中的可能是多个
    var amount = $(goodUl).find("li[class='col07']")
    $(amount).each(function (i, t) {
        var np = parseFloat($(t).text().replace("元", ''))
        totalPrice -= np;
    })
    // var leftPrice = totalPrice - parseFloat(amount)
    // console.log(totalPrice, amount)
    $("#lefPrice").text(totalPrice.toFixed(2))

    // TODO 修改共计商品数量

}

$(".num_add").on('click', 'a', function () {
    var $this = $(this)
    let num_show = $this.parent().find(".num_show");
    var nowCount = parseInt(num_show.val())
    // console.log($this, num_show, nowCount)
    if ($this.hasClass('add')) {
        nowCount += 1
    } else if ($this.hasClass('minus')) {
        if (nowCount > 1) {
            nowCount -= 1
        }
    }
    num_show.val(nowCount)
    goodCountChanged()
})

/**
 * 商品数量调整时触发后台同步减少商品数量
 */
function goodCountChanged() {
    //TODO 调用后台接口

}