from datetime import date, timedelta
from calendar import LocaleHTMLCalendar

from blog.models import Entry
from django.core.urlresolvers import reverse

class YouflogCalendar(LocaleHTMLCalendar):
    
    def formatday(self, day, weekday):
        if day and day in self.day_entries:
            day_date = date(self.current_year, self.current_month, day)
            archive_day_url = reverse('entry_by_calendar',
                                      args=[day_date.strftime('%Y'),
                                            day_date.strftime('%m'),
                                            day_date.strftime('%d')])
            return '<td class="%s entry"><a href="%s">%d</a></td>' % (
                self.cssclasses[weekday], archive_day_url, day)
        
        return super(YouflogCalendar, self).formatday(day, weekday)
    
    def formatmonth(self, theyear, themonth, withyear=True):
        self.current_year = theyear
        self.current_month = themonth
        self.day_entries = [entries.date.day for entries in
                            Entry.objects.get_post_by_date(theyear, themonth)]
        return super(YouflogCalendar, self).formatmonth(theyear, themonth, withyear)
    
