import json
import random
import string
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Class, Student, AttendanceRecord

# --- Template Views ---

@login_required
def home_view(request):
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'signup.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html')

@login_required
def report_view(request):
    return render(request, 'report.html')

# --- Helper Functions ---

def generate_class_code():
    chars = string.ascii_lowercase + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(7))
        if not Class.objects.filter(code=code).exists():
            return code

def parse_date(date_str):
    parts = list(map(int, date_str.split('-')))
    return datetime.date(parts[0], parts[1], parts[2])

def serialize_student(student):
    records_dict = {}
    for record in student.records.all():
        date_key = f"{record.date.year}-{record.date.month}-{record.date.day}"
        records_dict[date_key] = record.status
    return {
        "id": str(student.id),
        "roll": student.roll,
        "name": student.name,
        "records": records_dict
    }

def serialize_class(cls):
    students_list = []
    for student in cls.students.all().order_by('name'):
        students_list.append(serialize_student(student))
    
    return {
        "id": str(cls.id),
        "name": cls.name,
        "code": cls.code,
        "created": cls.created_at.strftime("%d/%m/%y"),
        "totalClass": cls.total_classes,
        "lastMarkedDate": f"{cls.last_marked_date.year}-{cls.last_marked_date.month}-{cls.last_marked_date.day}" if cls.last_marked_date else None,
        "students": students_list
    }

# --- Auth APIs ---

@require_POST
def api_signup(request):
    try:
        data = json.loads(request.body)
        fullName = data.get('fullName', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password')

        if not fullName or not email or not password:
            return JsonResponse({"status": "error", "message": "All fields are required"}, status=400)
        
        if User.objects.filter(username=email).exists():
            return JsonResponse({"status": "error", "message": "An account with this email already exists"}, status=400)
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = fullName
        user.save()
        
        return JsonResponse({"status": "success", "message": "Account created successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
def api_login(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password')

        if not email or not password:
            return JsonResponse({"status": "error", "message": "Email and password are required"}, status=400)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"status": "success", "message": "Logged in successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid email ID or password"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
@login_required
def api_logout(request):
    logout(request)
    return JsonResponse({"status": "success", "message": "Logged out successfully"})

# --- Profile APIs ---

@login_required
def api_profile(request):
    user = request.user
    return JsonResponse({
        "name": user.first_name if user.first_name else user.username,
        "email": user.email,
        "created": user.date_joined.isoformat()
    })

@require_POST
@login_required
def api_profile_update(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({"status": "error", "message": "Name is required"}, status=400)
        
        request.user.first_name = name
        request.user.save()
        return JsonResponse({"status": "success", "message": "Profile updated successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# --- Class APIs ---

@login_required
def api_classes(request):
    user_classes = Class.objects.filter(user=request.user).order_by('-id')
    serialized = [serialize_class(cls) for cls in user_classes]
    return JsonResponse(serialized, safe=False)

@require_POST
@login_required
def api_class_add(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({"status": "error", "message": "Class name is required"}, status=400)
        
        cls = Class.objects.create(
            user=request.user,
            name=name,
            code=generate_class_code()
        )
        return JsonResponse(serialize_class(cls))
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
@login_required
def api_class_rename(request, class_id):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({"status": "error", "message": "Class name is required"}, status=400)
        
        cls = get_object_or_404(Class, id=class_id, user=request.user)
        cls.name = name
        cls.save()
        return JsonResponse(serialize_class(cls))
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
@login_required
def api_class_delete(request, class_id):
    try:
        cls = get_object_or_404(Class, id=class_id, user=request.user)
        cls.delete()
        return JsonResponse({"status": "success", "message": "Class deleted successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# --- Student APIs ---

@require_POST
@login_required
def api_student_add(request, class_id):
    try:
        data = json.loads(request.body)
        roll = data.get('roll', '').strip()
        name = data.get('name', '').strip()
        if not roll or not name:
            return JsonResponse({"status": "error", "message": "Roll number and name are required"}, status=400)
        
        cls = get_object_or_404(Class, id=class_id, user=request.user)
        
        if Student.objects.filter(class_group=cls, roll=roll).exists():
            return JsonResponse({"status": "error", "message": "Roll number already exists in this class"}, status=400)

        student = Student.objects.create(
            class_group=cls,
            roll=roll,
            name=name
        )
        return JsonResponse(serialize_student(student))
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
@login_required
def api_student_edit(request, student_id):
    try:
        data = json.loads(request.body)
        roll = data.get('roll', '').strip()
        name = data.get('name', '').strip()
        if not roll or not name:
            return JsonResponse({"status": "error", "message": "Roll number and name are required"}, status=400)
        
        student = get_object_or_404(Student, id=student_id, class_group__user=request.user)
        
        # Check if roll number is duplicate with another student in the same class
        if Student.objects.filter(class_group=student.class_group, roll=roll).exclude(id=student.id).exists():
            return JsonResponse({"status": "error", "message": "Roll number already exists in this class"}, status=400)
        
        student.roll = roll
        student.name = name
        student.save()
        return JsonResponse(serialize_student(student))
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
@login_required
def api_student_delete(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id, class_group__user=request.user)
        student.delete()
        return JsonResponse({"status": "success", "message": "Student deleted successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# --- Attendance APIs ---

@require_POST
@login_required
def api_student_attendance(request, student_id):
    try:
        data = json.loads(request.body)
        date_str = data.get('date')
        status = data.get('status') # 'present', 'absent', or 'none'
        
        if not date_str or not status:
            return JsonResponse({"status": "error", "message": "Date and status are required"}, status=400)
        
        student = get_object_or_404(Student, id=student_id, class_group__user=request.user)
        record_date = parse_date(date_str)
        cls = student.class_group

        if status == 'none':
            AttendanceRecord.objects.filter(student=student, date=record_date).delete()
        else:
            if status not in ['present', 'absent']:
                return JsonResponse({"status": "error", "message": "Invalid status value"}, status=400)
            
            # Check if this class has any records on this date already
            # (Note: we check records of all students in the class on this date)
            has_records = AttendanceRecord.objects.filter(student__class_group=cls, date=record_date).exists()
            
            record, created = AttendanceRecord.objects.get_or_create(
                student=student,
                date=record_date,
                defaults={'status': status}
            )
            if not created:
                record.status = status
                record.save()
            
            # Register session logic
            if not has_records or cls.last_marked_date != record_date:
                cls.last_marked_date = record_date
                cls.total_classes += 1
                cls.save()

        # Return updated serialized class to refresh state easily
        return JsonResponse(serialize_class(cls))
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

