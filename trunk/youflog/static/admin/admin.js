admin= {
	decode:function(msg){
		return eval('('+msg+')')
	},
	
	del_post:function(id){
		var k = this
		$.ajax({
			type:'POST',
			url:'/admin/delpost',
			data:{'id':id},
			success:function(msg){
				msg = k.decode(msg)
				if(msg[0]){
					$('#post-'+id).remove()
				}else{
					alert(msg[1])
				}
			}
		});
	},
	
	del_comment:function(id){
		var k = this
		$.ajax({
			type: "POST",
			url: "/admin/del_comment/"+id,
			success:function(msg){
				msg = k.decode(msg)
				if(msg){
					$('#comment-'+id).remove()
				}else{
					alert(msg[1])
				}
			}
		});
	},
	comment_flag_spam:function(id,approve){
		var k = this;
		$.ajax({
			url: "/admin/flag_spam_comment/"+id,
			data:{'approve':approve},
			success:function(msg){
				msg = k.decode(msg)
				if(msg){
					$('#comment-'+id).remove()
				}else{
					alert(msg[1])
				}
			}
		});
	}
}