# *_* encoding=utf-8 *_*
from django.conf.urls.defaults import *
from django.conf import settings
from blog.views import admin

urlpatterns = patterns('',
    url(r'^admin$',admin.index,name="admin_index"), # 后台管理页面
    #post
    url(r'^admin/quick_post',admin.quick_post,name="quick_post"),#快速发布
    url(r'^admin/allposts',admin.all_posts,name='all posts'),
    url(r'^admin/pubposts',admin.all_pub_posts,name='all publish posts'),
    url(r'^admin/unpubposts',admin.unpub_posts,name='all unpublish posts'),
    url(r'^admin/post$',admin.admin_addpost,name="add post"), #跳转到文章添加页面
    url(r'^admin/submit_post',admin.submit_post,name='submit_post_page'), #提交文章 或者页面
    url(r'^admin/editpost/(?P<id>\d+)',admin.edit_post,name="editor post"),#文章火着页面的编辑
    url(r'^admin/delpost',admin.delpost),
    url(r'^admin/post_delete$',admin.post_delete,name="delete post"), #删除文章或者页面
    url(r'admin/page$',admin.addPage,name='add page '), #跳转到页面添加
    url(r'admin/pages$',admin.pages,name='show all pages'),#分页显示所有的页面
    url(r'admin/posts_cate/(?P<slug>[-\w]+)$',admin.posts_by_category),
    #comment
    url(r'^admin/comments',admin.comments,name="show all comments"), #分页显示所有的评论
    url(r'^admin/spam_comment',admin.spam_comment,name='spam comment'),
    url(r'^admin/comment_delete',admin.comment_delete,name="delete comment"), #批量删除评论信息
    url(r'^admin/flag_spam_comment/(?P<id>\d+)$',admin.flag_comment_for_spam),
    url(r'^admin/del_comment/(?P<id>\d+)$',admin.delete_single_comment),
    url(r'^admin/edit_comment/(?P<id>\d+)$',admin.edit_comment),
    url(r'^admin/save_comment$',admin.save_comment),
    url(r'^admin/replycomment$',admin.reply_comment,name="reply comment"),
    
    #category
    url(r'^admin/categories',admin.categories,name='show all categories'),
    url(r'^admin/category/add$',admin.addCategory,name='add category'),
    url(r'^admin/editcategory/(?P<id>\d+)$',admin.editCategory,name='editor category'),
    url(r'^admin/category/delete$',admin.deleteCategory,name='delete category'),
    
    #links
    url(r'^admin/links',admin.links,name='show all links'),
    url(r'^admin/link/add$',admin.addLink,name='add link'),
    url(r'^admin/editlink/(?P<id>\d+)$',admin.editlink,name='editor link'), #编辑连接
    url(r'^admin/link/delete$',admin.deleteLink,name='delete links'), #删除连接
    #settings
    url(r'^admin/settings$',admin.settings,name='settings'), #基本设置页面
    url(r'^admin/settings/save$',admin.save_setting,name='save settings'), #保持设置
    url(r'^admin/comment_setting$',admin.setting_comment),
    url(r'^admin/save_commentOption$',admin.save_commentOption),
    url(r'^admin/permalink$',admin.permalink),
    url(r'^admin/save_permalink',admin.save_permalink),
    url(r'^admin/backup_db$',admin.backup_db),
    
    url(r'^admin/users$',admin.users),
    url(r'^admin/profile',admin.profile),
    url(r'^admin/saveprofile',admin.saveprofile),
    
    #media
    url(r'^admin/media$',admin.media,name='show all media'),
    
    #login logout
    url(r'^accounts/login', admin.login,name="login"), #登录
    url(r'^accounts/logout$',admin.logout,name='logout'), #退出
)