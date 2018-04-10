from django.db import models
from lectures.models import Section
from accounts.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Timetable(models.Model):
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
        current_default = None
        user_timetables = Timetable.objects.filter(user=self.user)
        for i in range(len(user_timetables)):
            if user_timetables[i].default and user_timetables[i] is not self:
                current_default = user_timetables[i]
                break

        if current_default is not None:
            Timetable.objects.filter(id=current_default.id).update(_default=False)
            current_default.refresh_from_db()

        Timetable.objects.filter(id=self.id).update(_default=True)
        self.refresh_from_db()


@receiver(post_save, sender=Timetable)
def set_new_timetable_as_default(sender, instance, **kwargs):
    instance.set_as_default()


@receiver(post_delete, sender=Timetable)
def set_recent_timetable_as_default_when_default_deleted(sender, instance, **kwargs):
    if len(Timetable.objects.filter(user=instance.user)) == 0:
        return

    if instance.default is False:
        return

    recent = Timetable.objects.filter(user=instance.user).order_by('-modified_date')[0]
    print(recent)
    recent.set_as_default()
