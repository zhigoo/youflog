#!/usr/bin/env python
# *_* encoding=utf-8*_*
import os,logging
import settings
class Theme:
    def __init__(self,name="default"):
        self.name=name
        self.dir=os.path.join(settings.HERE,'templates/themes',self.name)
        logging.info("theme path: %s"%self.dir)

class ThemeIterator:
    def __init__(self):
        self.iterating = False
        theme_path=os.path.join(settings.HERE,'templates/themes')
        self.theme_path = os.path.normcase(theme_path)
        self.list = []

    def __iter__(self):
        return self

    def next(self):
        if not self.iterating:
            self.iterating = True
            self.files = os.listdir(self.theme_path)
            self.cursor = 0
        if self.cursor >= len(self.files):
            self.iterating = False
            raise StopIteration
        else:
            value = self.files[self.cursor]
            self.cursor += 1
            p=os.path.join(self.theme_path,value)
            #判断是否是一个目录
            if os.path.isdir(p):
                self.list.append(value)
                return value
