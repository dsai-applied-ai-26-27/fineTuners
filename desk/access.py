"""Who may write a course.

One question, asked wherever a page lets someone change a course or look at one that
students cannot see yet: the pages for educators (desk/views.py), a course's own pages
(catalog/views/common.py), and the editor.
"""

from .models import Educator


def may_write(user, series):
    """Whether this person may change the course `series`: they write it (the role covers
    every year of the course), or they run the site, whose rights are universal."""
    if not user.is_authenticated:
        return False
    return user.is_staff or Educator.objects.filter(user=user, series=series).exists()
