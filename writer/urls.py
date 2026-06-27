from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("api/files/", views.list_files),
    path("api/read/", views.read_file),
    path("api/save/", views.save_file),
    path("api/rename/", views.rename_file),
    path("api/delete/", views.delete_file),
    path("api/folder/", views.create_folder),
    path("api/ai/", views.ai_assist),
    path("api/references/reload/", views.reload_references),
    path("api/memories/", views.list_memories),
]
