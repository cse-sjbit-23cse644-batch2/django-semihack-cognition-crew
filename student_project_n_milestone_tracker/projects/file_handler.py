"""
File handling utilities for file preview and storage
"""
import os
import mimetypes
from django.conf import settings


class FileHandler:
    """Handles file storage and preview logic"""
    
    PREVIEW_SUPPORTED = ['application/pdf', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']
    
    @staticmethod
    def get_file_preview_url(version):
        """Get preview URL for a version file"""
        if not version.file:
            return None
        
        file_url = version.file.url
        content_type = version.metadata.get('file_type', '')
        
        if content_type in FileHandler.PREVIEW_SUPPORTED:
            return file_url
        
        return None
    
    @staticmethod
    def can_preview_inline(file_path):
        """Check if file can be previewed inline (without download)"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip('.').lower()
        
        preview_extensions = ['pdf', 'ppt', 'pptx']
        return ext in preview_extensions
    
    @staticmethod
    def get_file_icon(file_extension):
        """Return icon class for file type"""
        icons = {
            'pdf': '📄',
            'ppt': '🎤',
            'pptx': '🎤',
        }
        return icons.get(file_extension.lower(), '📎')
    
    @staticmethod
    def get_file_size_display(size_bytes):
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
