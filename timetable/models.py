""" Module for models about timetable. """

from django.db import models
from lectures.models import Section
from accounts.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Timetable(models.Model):
    """ Represents a timetable.

    Attributes:
        title: title of a timetable.
        user: user of a timetable.
        sections: sections in a timetable.
        _default: boolean variable telling the default timetable when user access to timetable page firstly.
            This field is true only when the other timetables of a user is not true.
        modified_date: the last date when a timetable is modified.

    """
    title = models.CharField(max_length=20, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    sections = models.ManyToManyField(Section)
    _default = models.BooleanField(null=False, default=False)
    modified_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        raise AttributeError("You cannot set 'default' attribute directly")

    def set_as_default(self):
        """
        Set a timetable as the default timetable among user's timetables. It will set "_default" field
        of the other timetables of a user as false, and then set "_default" field of this timetable as true.
        """
        current_default = None
        for user_timetable in Timetable.objects.filter(user=self.user):
            if user_timetable.default and user_timetable is not self:
                current_default = user_timetable
                break

        if current_default is not None:
            Timetable.objects.filter(id=current_default.id).update(_default=False)
            current_default.refresh_from_db()

        Timetable.objects.filter(id=self.id).update(_default=True)
        self.refresh_from_db()


@receiver(post_save, sender=Timetable)
def set_new_timetable_as_default(sender, instance, **kwargs):
    """
    If a new timetable is created, set the timetable as a default timetable.
    :param sender: sender of the signal. In this function, "Timetable" model will be sender.
    :param instance: instance of the signal, In this function, a new "Timetable" object will be an instance.
    """
    instance.set_as_default()


@receiver(post_delete, sender=Timetable)
def set_recent_timetable_as_default_when_default_deleted(sender, instance, **kwargs):
    """
    If a default timetable is deleted, set the recently modified timetable as a default timetable.
    :param sender: sender of the signal. In this function, "Timetable" model will be sender.
    :param instance: instance of the signal, In this function, the deleted "Timetable" object will be an instance.
    """
    if len(Timetable.objects.filter(user=instance.user)) == 0:
        return

    if instance.default is False:
        return

    recent = Timetable.objects.filter(user=instance.user).order_by('-modified_date')[0]
    recent.set_as_default()
