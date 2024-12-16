from django.contrib import admin
from app.models import GeneralInfo, Service, Testimonials, FrequentlyAskedQuestion, ContactFormLog, Blog, Author

@admin.register(GeneralInfo)
class GeneralInfoAdmin(admin.ModelAdmin):
    
    list_display = [
        'company_name',
        'location',
        'email',
        'phone',
        'open_hours',
    ]
    
#def has_add_permission(self, request, obj=None):
#    return False

readonly_fields = [
    'email'
]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "tittle",
        "description"
    ]
    
    search_fields = [
        "tittle",
        "description"
    ] 

@admin.register(Testimonials)
class TestimonialsAdmin(admin.ModelAdmin):
    
    list_display = [
        "username",
        "user_job_title",
        "display_rating_count",
    ]
    
    def display_rating_count(self, obj):
        return '*' * obj.rating_count
    
    display_rating_count.short_description = "Rating"
    
@admin.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):

    list_display = [
        'question',
        'answer',
    ]
    
@admin.register(ContactFormLog)
class ContactFormLogAdmin(admin.ModelAdmin):
    
    list_display = [
        'email',
        'is_success',
        'is_error',
        'action_time'
    ]
    
    def has_add_permission(self, request, obj= None):
        return False
    
    def has_change_permission(self, request, obj = None):
        return False
    
    def has_delete_permission(self, request, obj = None):
        return False
    
@admin.register(Author)
class AuhtorAdmin(admin.ModelAdmin):
    
    list_display = [
        'first_name',
        'last_name',
    ]
    
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    
    list_display = [
        'category',
        'author',
        'tittle',
        'blog_image',
        'created_at',
    ]
    
