from django.dispatch import Signal

comment_was_submit=Signal(providing_args=['comment'])

comment_was_posted = Signal(providing_args=["comment", "request"])