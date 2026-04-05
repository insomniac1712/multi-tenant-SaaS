from django.db import models
from django.conf import settings
# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organization = models.ForeignKey("orgs.Organization", related_name="projects", on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_projects", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "organization"],
                name="unique_project_name_per_org"
            )
        ]
        indexes = [models.Index(fields=["organization", "created_at"])]
        
    def __str__(self):
        return f"{self.name} ({self.organization.name})"