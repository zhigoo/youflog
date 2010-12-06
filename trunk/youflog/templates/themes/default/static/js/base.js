/*
Author: mg12
Update: 2009/06/24
Author URI: http://www.neoease.com/
*/
(function() {

function $(id) {
	return document.getElementById(id);
}

function setStyleDisplay(id, status) {
	$(id).style.display = status;
}

function goTop(a, t) {
	a = a || 0.1;
	t = t || 16;

	var x1 = 0;
	var y1 = 0;
	var x2 = 0;
	var y2 = 0;
	var x3 = 0;
	var y3 = 0;

	if (document.documentElement) {
		x1 = document.documentElement.scrollLeft || 0;
		y1 = document.documentElement.scrollTop || 0;
	}
	if (document.body) {
		x2 = document.body.scrollLeft || 0;
		y2 = document.body.scrollTop || 0;
	}
	var x3 = window.scrollX || 0;
	var y3 = window.scrollY || 0;

	var x = Math.max(x1, Math.max(x2, x3));
	var y = Math.max(y1, Math.max(y2, y3));

	var speed = 1 + a;
	window.scrollTo(Math.floor(x / speed), Math.floor(y / speed));
	if(x > 0 || y > 0) {
		var f = "MGJS.goTop(" + a + ", " + t + ")";
		window.setTimeout(f, t);
	}
}

window['MGJS'] = {};
window['MGJS']['$'] = $;
window['MGJS']['goTop'] = goTop;

})();

function loadRecentComments(page){
		jQuery.ajax({
		url:'/recentComments',
		data:{page:page},
		beforeSend:function(){
			document.body.style.cursor = 'wait';
			jQuery('#recentcomment_nav').html('<span class="rc_ajax_loader">正在加载.....</span>'); 
		},
		success:function(response){
			result = eval('(' + response + ')')
			if(result[0]){
				$('#recent_comments').fadeOut(function(){
					$(this).html(result[1]).fadeIn()
				})
				document.body.style.cursor = 'auto'; 
			}
		}
	})
}

function randomColor() {
	//16进制方式表示颜色0-F
	var arrHex = ["0","1","2","3","4","5","6","7","8","9",
					"A","B","C","D","E","F"];
	var strHex = "#";
	var index;
	for(var i = 0; i < 6; i++) {
		//取得0-15之间的随机整数
		index = Math.round(Math.random() * 15);
		strHex += arrHex[index];
	}
	return strHex;
}

$(document).ready(function(){
	
	//彩色的标签云
	$(".widget_tag_cloud div a").each(function(i){
		this.style.color=randomColor()
	})

	loadRecentComments(1);
	
	$('#tab-title span').click(function(){
		$(this).addClass("selected").siblings().removeClass();
		$("#tab-content > ul").slideUp('1500').eq($('#tab-title span').index(this)).slideDown('1500');
	});
})