from django.db import models
from django.conf import settings
# Create your models here.

class Task(models.Model):
    class status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
    project = models.ForeignKey("projects.Project",related_name="tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=status.choices, default=status.TODO)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_tasks", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="assigned_tasks", on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["title", "project"],
                name="unique_task_title_per_project"
            )
        ]
        indexes = [models.Index(fields=["project", "status"]), models.Index(fields=["assigned_to", "status"])]
        
    def __str__(self):
        return f"{self.title} ({self.project.name})"
    