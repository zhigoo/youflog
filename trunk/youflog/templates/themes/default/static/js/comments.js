//js操作cookie
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

function postComment(){
	
	author = $("#author").val()
	email = $('#email').val()
	url = $('#url').val()
	checkret = $('#checkret').val()
	comment = $('#comment').val()
	comments= $('#comments').val()
	key= $('#key').val()
	parentid=$('#parentid').val()
	notify_mail=document.getElementById('reply_notify_mail').value
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
	
	var params ={
		ajax: 1,
		author:author,
		email:email,
		url:url,
		comment:comment,
		comments:comments,
		key:key,
		parentid:parentid,
		reply_notify_mail:notify_mail
	}
	//评论者的信息放到cookie中
	SetCookie('author',author)
	SetCookie('email',email)
	SetCookie('url',url)
	
	$('#submit').val('正在提交...')
	document.getElementById('submit').disabled=true
	$.ajax({
		type:'post',
		url:'/postcomment',
		data:jQuery.param(params),
		success:function(response){
			result = eval('(' + response + ')')
			if(result[0]){
				$('#submit').val('Submit')
				$('#comment').val('')
		   		addComment(result[1])
		   		$('#parentid').val(0)
		   		document.getElementById('submit').disabled=false
                location="#comments";
			}else{
				if(result[1] == -102){
					$('#submit').val('Submit')
					alert('哎呀，出了点小问题!')
				}else if(result[1] == -101){
					alert("检查一下你的用户名啊邮箱啊或者评论是不是写全了?")
				}else if(result[1] == -103){
					alert('spam的禁地! 转道吧')
				}
				document.getElementById('submit').disabled=false
			}
		}
	});
}


function addComment(comment){
	var parentid=$('#parentid').val()
	
	if(parentid != 0){
		$('#comment-' +parentid +" .children").append(comment)
	}else{
		$("#commentlist").append(comment);
	}
}

function backComment(id,author){
	 $('#parentid').val(id)
	 comment =  $('#comment');
     comment.val('@'+author+',');
     return true
}

//应用
function quote(id,author){
	 msg = $('#commentbody-'+id+" p").html();
     comment =  $('#comment');
     comment.val(comment.val()+'引用<a href=\"#comment-'+id+'\">@'+author+'<\/a><blockquote>'+msg+'</blockquote>\n');
     return true;
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
}
$(document).ready(function(){
    $('#commentform').keypress(function(e){
    	 if(e.ctrlKey && e.which == 13 || e.which == 10) { 
            $("#submit").click();
        }
    })
    
}); 