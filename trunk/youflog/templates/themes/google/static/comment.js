function SetCookie(name,value){
	var minute = 100; //保存天数
	var exp = new Date();
	exp.setTime(exp.getTime() + minute*60*1000*60*24);
	document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
}
function getCookie(name){//取cookies函数
	var arr = document.cookie.match(new RegExp("(^| )"+name+"=([^;]*)(;|$)"));
	if(arr != null) return unescape(arr[2]); return null;
}

function backComment(id,author){
	 $('#parentid').val(id)
	 comment =  $('#comment');
    comment.val('@'+author+',');
    return true
}

function post(){
	author = $("#author").val()
	email = $('#email').val()
	url = $('#url').val()
	comment = $('#comment').val()
	
	if(author==""||email==""||comment==""){
		alert("请确认您已经填写了姓名、邮箱和评论内容!");
		return false;
	}
	//检查邮箱地址
	var search_str = /^[\w\-\.]+@[\w\-\.]+(\.\w+)+$/;
	if(!search_str.test(email)){
		alert('请输入正确的邮件地址！');
	    return false;
	}
	
	SetCookie('author',author)
	SetCookie('email',email)
	SetCookie('url',url)
}

$(document).ready(function(){
  	//从cookie载入数据到textfield中	
	author =getCookie('author')
	if(author) $("#author").val(author)
	
    email = getCookie('email')
  	if(email) $('#email').val(email)
  	
  	url = getCookie('url')
    if(url) $('#url').val(url)

    $('#commentform').keypress(function(e){
    	 if(e.ctrlKey && e.which == 13 || e.which == 10) { 
            $("#submit").click();
        }
    })
    
}); 