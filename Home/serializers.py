from rest_framework import serializers
from .models import Task

class TaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','title','completed']

class AddTaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title','user']