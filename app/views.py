from datetime import datetime
from django.db import connection
from django.conf import settings
from django.utils import timezone
from .models import Blog, Comment
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, LoginForm, CommentForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from app.models import GeneralInfo, Service, Testimonials, FrequentlyAskedQuestion, ContactFormLog, Blog

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ви успішно зареєструвалися!')
            return redirect('profile')
        else:
            messages.error(request, 'Виникла помилка при реєстрації. Перевірте введені дані.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')  # Перенаправлення після успішного входу
                return redirect(next_url)
            else:
                form.add_error(None, 'Invalid credentials')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def profile(request):
    user = request.user  # Отримуємо поточного користувача
    return render(request, 'profile.html', {'user': user})

def logout_view(request):
    logout(request)
    return redirect('login')

def write_sql_queries_to_file(file_path):
    with open(file_path, 'w') as file:
        queries = connection.queries
        for query in queries:
            sql = query ['sql']
            file.write(f"{sql}\n")
    
def index(request):
        
    general_info = GeneralInfo.objects.first() #None
    
    all_records = GeneralInfo.objects.all()

    services = Service.objects.all()
    
    testimonials = Testimonials.objects.all()
    
    faqs = FrequentlyAskedQuestion.objects.all()
    
    recent_blogs = Blog.objects.all().order_by("-created_at")[:3]
    
    default_value = ""
    context = {
        "company_name": getattr(general_info, "company_name", default_value),
        "location": getattr(general_info, "location", default_value),
        "email": getattr(general_info, "email", default_value),
        "phone": getattr(general_info, "phone", default_value),
        "open_hours": getattr(general_info, "open_hours", default_value),
        "video_url": getattr(general_info, "video_url", default_value),
        "twitter_url": getattr(general_info, "twitter_url", default_value),
        "facebook_url": getattr(general_info, "facebook_url", default_value),
        "instagram_url": getattr(general_info, "instagram_url", default_value),
        "linkedin_url": getattr(general_info, "linkedin_url", default_value),
        "profile_log": getattr(general_info, "profile_log",default_value),
        
        "services": services,
        "testimonials": testimonials,
        "faqs": faqs,
        "recent_blogs": recent_blogs,
    }
    
    print(f"context: {context}")
    
    return render(request, "index.html", context)

def aboutus(request):
    context = {}
    return render(request, "aboutus", context)

def contact_form(request):
    
    if request.method == 'POST':
        print("\nUser has submit a contact form\n")
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        context = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }
        html_content = render_to_string('email.html', context)
        
        is_success = False
        is_error = False
        error_message = ""
        
        try:
            send_mail(
                subject=subject,
                message=None,
                html_message=html_content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False, #default is True
            )
        except Exception as e:
            is_error = True
            error_message = str(e)
            messages.error(request, "There is an error , could not send email")
        else:
            is_success = True
            messages.success(request, "Email has been sent ")
            
        ContactFormLog.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            action_time=timezone.now(),
            is_success = is_success,
            is_error=is_error,
            error_message=error_message, 
        )

    return redirect('home')

def blogs(request):
    
    all_blogs = Blog.objects.all().order_by("-created_at")
    blogs_per_page = 4
    paginator = Paginator(all_blogs, blogs_per_page)
    
    print(f"paginator: {paginator.num_pages}")
    
    page = request.GET.get('page')
    
    print(f"page: {page}")
    
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages) 
        
    context = {
        "blogs": blogs,
    }
    
    return render(request, "blogs.html", context)

@login_required
def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    comments = blog.comments.all()  # Отримуємо всі коментарі для блогу

    # Якщо запит POST (коли користувач додає новий коментар)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog  # Прив'язуємо коментар до цього блогу
            comment.author = request.user  # Автор коментаря — поточний користувач
            comment.save()
            return redirect('blog_details', blog_id=blog.id)  # Перенаправляємо на ту ж сторінку

    # Якщо запит GET (відображаємо форму коментаря)
    else:
        form = CommentForm()

    # Отримуємо кілька останніх блогів для блоку "Recent Blogs"
    recent_blogs = Blog.objects.all().exclude(id=blog_id).order_by('-created_at')[:2]

    context = {
        'blog': blog,
        'comments': comments,
        'form': form,
        'recent_blogs': recent_blogs,
    }

    return render(request, 'blog_details.html', context)