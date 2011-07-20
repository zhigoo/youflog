#!/usr/bin/env python
#coding=utf-8
from django.http import HttpResponse
from blog.models import OptionSet
import random,cStringIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from settings import CAPTCHA_FONT

_letter_cases = "abcdefghjkmnpqrstuvwxy" # 小写字母，去除可能干扰的i，l，o，z
_upper_cases = _letter_cases.upper() # 大写字母
_numbers = ''.join(map(str, range(3, 10))) # 数字
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
 
def create_validate_code(size=(80, 20),
                         chars=init_chars,
                         img_type="GIF",
                         mode="RGB",
                         bg_color=(255, 255, 255),
                         fg_color=(0, 0, 255),
                         font_size=18,
                         font_type=CAPTCHA_FONT,
                         length=4,
                         draw_lines=True,
                         n_line=(1, 2),
                         draw_points=True,
                         point_chance = 2):

    width, height = size # 宽， 高
    img = Image.new(mode, size, bg_color) # 创建图形
    draw = ImageDraw.Draw(img) # 创建画笔
 
    def get_chars():
        '''生成给定长度的字符串，返回列表格式'''
        return random.sample(chars, length)
 
    def create_lines():
        '''绘制干扰线'''
        line_num = random.randint(*n_line) # 干扰线条数
 
        for i in range(line_num):
            # 起始点
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            #结束点
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))
 
    def create_points():
        '''绘制干扰点'''
        chance = min(100, max(0, int(point_chance))) # 大小限制在[0, 100]
         
        for w in xrange(width):
            for h in xrange(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))
 
    def create_strs():
        '''绘制验证码字符'''
        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars) # 每个字符前后以空格隔开
        font = ImageFont.truetype(font_type, font_size)
        draw.text((0,0),strs, font=font, fill=fg_color)
        return ''.join(c_chars)
    
    def draw_arithmetic():
        font = ImageFont.truetype(font_type, font_size)
        first=random.randint(1,10)
        second=random.randint(2,12)
        draw.text((0,0), str(first)+'+'+str(second),font=font,fill=(100,211, 90))
        return first+second
    
    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    tp=OptionSet.get('safecode_type', 1);
    if tp == str(1):
        strs = create_strs()
    else:
        strs = draw_arithmetic()

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE) # 滤镜，边界加强（阈值更大）
 
    return img, strs

def validate(request):
    
    buf = cStringIO.StringIO()
    img,str = create_validate_code()
    img.save(buf, "GIF")
     
    request.session['safecode'] =str
    return HttpResponse(buf.getvalue(), "image/gif")