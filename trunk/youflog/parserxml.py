import xml.etree.ElementTree as et

from blog.models import Entry,Comment,Category

class import_wordpress:
    def __init__(self,source):
        self.categories=[]
        self.tags=[]
        self.entries=[]

        self.source=source
        self.doc=et.fromstring(source)
        #use namespace
        self.wpns='{http://wordpress.org/export/1.0/}'

        self.contentns="{http://purl.org/rss/1.0/modules/content/}"
        self.excerptns="{http://wordpress.org/export/1.0/excerpt/}"
        et._namespace_map[self.wpns]='wp'
        et._namespace_map[self.contentns]='content'
        et._namespace_map[self.excerptns]='excerpt'
        self.channel=self.doc.find('channel')
        self.dict={'category':self.wpns+'category','tag':self.wpns+'tag','item':'item'}
        self.cur_do=None
        
        
    def parse(self):
        self.parseCategory()
        self.parseItem()
        
    def parseCategory(self):
        categories=self.channel.findall(self.wpns+'category')
        for cate in categories:
            slug=cate.findtext(self.wpns+'category_nicename')
            name=cate.findtext(self.wpns+'cat_name')
            #print slug
            cate=Category(name=name,slug=slug,desc=name)
            cate.save()
    
    def parseItem(self):
        items=self.channel.findall('item')
        for item in items:
            title=item.findtext('title')
            date = item.findtext('pubDate')
            entrytype=item.findtext(self.wpns+'post_type')
            content=item.findtext(self.contentns+'encoded')
            excerpt=item.findtext(self.excerptns+'encoded')
            #postid=item.findtext(self.wpns+'post_id')
            slug=item.findtext(self.wpns+'post_name')
            #parent=item.findtext(self.wpns+'post_parent')
            menuorder=item.findtext(self.wpns+'menu_order')
            
            
            tags=[]
            categories=[]
            cats=item.findall('category')
            
            for cat in cats:
                if cat.attrib.has_key('nicename'):
                    nicename=cat.attrib['nicename']
                    cat_type=cat.attrib['domain']
                    if cat_type=='tag' and cat.text:
                        tags.append(cat.text)
                    else:
                        #print nicename
                        #categories.append({'slug':nicename,'name':cat.text})
                        try:
                            category=Category.objects.get(slug=nicename)
                        except:
                            category=Category.objects.get(id=1)
                        categories.append(category)
                        
            #print ','.join(tags)
            #print categories
            post_tags=','.join(tags)
            
            entry=Entry(title=title,date=date,entrytype=entrytype,content=content,excerpt=excerpt,slug=slug,menu_order=menuorder)
            entry.tags=post_tags
            entry.allow_comment=True
            entry.category=categories[0]
            entry.save(True)
            
            comments=item.findall(self.wpns+'comment')
            for com in comments:
                comment=Comment(author=com.findtext(self.wpns+'comment_author'),
                                    content=com.findtext(self.wpns+'comment_content'),
                                    email=com.findtext(self.wpns+'comment_author_email'),
                                    weburl=com.findtext(self.wpns+'comment_author_url'),
                                    date=com.findtext(self.wpns+'comment_date')
                                    )
                comment.content_object=entry
                comment.save()

            
            #c.execute('insert into blog_entry(id,title,content,excerpt,published,entrytype)')
    
            
if __name__=='__main__':
    wp=import_wordpress(open('/opt/micolog.xml').read())
    wp.parseItem()