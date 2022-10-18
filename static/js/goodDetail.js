$(".buyCount").on('click', function () {
    $this = $(this)
    nowCount = parseInt($("#num_show").val())
    // console.log($this)
    if ($this.hasClass("add")) {
        nowCount = nowCount + 1
    } else {
        if (nowCount > 0) {
            nowCount = nowCount - 1
        }
    }
    $("#num_show").val(nowCount)
    getTotlaPrice(nowCount)
})

function getTotlaPrice(count) {
    var price = $("#price").text()
    var total = parseFloat(price) * count
    $(".total em").text(total.toFixed(2) + "元")
}

var $add_x = $('#add_cart').offset().top;
var $add_y = $('#add_cart').offset().left;

var $to_x = $('#show_count').offset().top;
var $to_y = $('#show_count').offset().left;

$(".add_jump").css({'left': $add_y + 80, 'top': $add_x + 10, 'display': 'block'})
$('#add_cart').click(function () {
    $(".add_jump").stop().animate({
            'left': $to_y + 7,
            'top': $to_x + 7
        },
        "fast", function () {
            $(".add_jump").fadeOut('fast', function () {
                $('#show_count').html(2);
            });

        });
})

//添加购物车方法
function addCar() {
    var goodId = $("#add_cart").data("goodid")
    var goodCount = $("#num_show").val()
    csrf = $("#add_cart").prev().val()
    console.log(goodId, goodCount)
    $.ajax({
        'url': '/car/addCar',
        dataType: 'json',
        method: 'POST',
        data: {"goodId": goodId, "goodCount": goodCount, "csrfmiddlewaretoken": csrf},
        success: function (data) {
            if (data.code == 1) {
                //添加成功！
                // 修改购物车商品数量
                $(".add_jump").css({'left': $add_y + 80, 'top': $add_x + 10, 'display': 'block'})
                $(".add_jump").stop().animate({
                        'left': $to_y + 7,
                        'top': $to_x + 7
                    },
                    "fast", function () {
                        $(".add_jump").fadeOut('fast', function () {
                            // 重新设置用户购物车中商品的条目数
                            data=data.data
                            // console.log(data)
                            $('#show_count').html(data.nowCount);
                        });
                    });

            } else {
                alert(data.msg)
            }

        }
    })
}

