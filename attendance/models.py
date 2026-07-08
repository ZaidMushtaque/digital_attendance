from django.db import models
from django.contrib.auth.models import User

class Class(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateField(auto_now_add=True)
    total_classes = models.IntegerField(default=0)
    last_marked_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    roll = models.CharField(max_length=50)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.roll} - {self.name}"

    class Meta:
        unique_together = ('class_group', 'roll')

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} ({self.date}): {self.status}"

