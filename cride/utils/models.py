"""django models utilities"""

# django
from django.db import models

class CRideModel(models.Model):
    """Comparte ride base model

    CRideModel acts as an abstract base class from which every other model in 
    the project will inherit. This class provides every table with the following attributes
        +created(DateTime): Store the datetime the object was created
        +modified(DateTime): Store the las datetime the object was modified
    """
    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Date time on which the project was created'
    )

    modified = models.DateTimeField(
        'created at',
        auto_now=True,
        help_text='Date time on which the project was modified'
    )

    class Meta:
        # abstract means this model will not be on the bd
        abstract = True

        get_latest_by = 'created'
        ordering = ['-created','-modified']

"""
    proxy models like abstract models they will not be shown on the bd
class Person(models.model):
    first_name = models.CharField()
    last_name = models.CharField()

class MyPerson(Person):
    class Meta:
        proxy = True

    def say_hi(name):
        pass

MyPerson.objects.all()
ricardo = MyPerson.objects.get(pk=1)    THIS WORKS
ricardo.say_hi('hola')

rulo = MyPerson.objects.get(pk=1) THIS DOSENT
rulo.say_hi('hola')

"""
