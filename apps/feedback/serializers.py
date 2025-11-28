from rest_framework import serializers
from .models import Feedback, FeedbackCategory, FeedbackAttachment, FeedbackStatusHistory

class FeedbackCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackCategory
        fields = ['id', 'name', 'code', 'description']

class FeedbackAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackAttachment
        fields = ['id', 'file_url', 'file_type']

    def get_file_url(self, obj):
        # Trả về link full domain cho mobile
        request = self.context.get('request')
        if obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None

class FeedbackStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = FeedbackStatusHistory
        fields = ['old_status', 'new_status', 'changed_by_name', 'created_at', 'note']

class FeedbackSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    attachments = FeedbackAttachmentSerializer(many=True, read_only=True)
    history = FeedbackStatusHistorySerializer(source='status_history', many=True, read_only=True)
    
    # Field dùng để upload nhiều file từ mobile (Write-only)
    files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    class Meta:
        model = Feedback
        fields = [
            'id', 'code', 'title', 'description', 'status', 'status_display',
            'priority', 'category', 'category_name', 'created_at', 
            'attachments', 'files', 'history'
        ]
        read_only_fields = ['code', 'status', 'priority', 'resident', 'apartment']

    def create(self, validated_data):
        # Tách files ra khỏi data trước khi tạo Feedback
        files = validated_data.pop('files', [])
        feedback = Feedback.objects.create(**validated_data)
        
        # Lưu từng file vào bảng Attachment
        for file in files:
            FeedbackAttachment.objects.create(feedback=feedback, file=file)
            
        return feedback