from django.dispatch import Signal

comment_sendEmail = Signal(providing_args=["subject","msg","reveivers"])

comment_was_submit=Signal(providing_args=['comment'])

comment_save = Signal(providing_args=["comment", "object"])

comment_was_posted = Signal(providing_args=["comment", "request"])