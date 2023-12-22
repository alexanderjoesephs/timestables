from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, HttpResponse
from .forms import CustomisedUserCreationForm
from .models import Question, Attempt, User, Teacher, Student, Test, Admin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
matplotlib.use('Agg')  # Set the backend to 'Agg'


# Create your views here.
@csrf_exempt
def myview(request):
    """
    for i in range(2,13):
        for j in range(2,13):
            q = Question()
            q.x = i
            q.y = j
            q.save()
    """
    is_student = False
    table_list = []
    if Student.objects.filter(user=request.user.id):
        is_student = True
        tests = Test.objects.filter(user_tested=request.user.id)
        for test in tests:
            if test.set:
                table_list.append(test.table_tested)
        print(table_list)
    is_teacher = False
    if Teacher.objects.filter(user=request.user.id):
        is_teacher = True
    is_admin = False
    if Admin.objects.filter(user=request.user.id):
        is_admin = True
    return render(request, "home.html",{'is_teacher':is_teacher,'is_admin':is_admin,'is_student':is_student,'table_list':table_list})

@csrf_exempt
def create_user(request):
    if Admin.objects.filter(user=request.user.id):
        form = CustomisedUserCreationForm()
        if(request.method=="GET"):
            return render(request, "create_user.html",{'form':form})
        if(request.method=="POST"):
            form = CustomisedUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                user_to_assign_times_tables = User.objects.get(username=username)
                for i in range(2,13):
                    test = Test()
                    test.set = True
                    test.table_tested = i
                    test.user_tested = user_to_assign_times_tables
                    test.save()
                if form.cleaned_data['Teacher_account']:
                    t = Teacher()
                    t.user = user_to_assign_times_tables
                    t.save()
                if form.cleaned_data['Admin_account']:
                    a = Admin()
                    a.user = user_to_assign_times_tables
                    a.save()
                #insert code to add times table objects to the user here.
                return render(request, "create_user.html",{'form':form,'message':f"successfully created user {user_to_assign_times_tables.username}"})

            else:
                return render(request, "create_user.html",{'form':form,'message':"couldn't create user"})
    else:
        return redirect(myview)

def user_login(request):
    if(request.user.is_authenticated):
        return redirect(myview)
    if request.method=='GET':
        return render(request, 'login.html')
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(myview)
        else:
            return render(request, 'login.html',{'message':"couldn't log in user"})

@csrf_exempt        
def logoutview(request):
    if request.method=="POST":
        if request.user.is_authenticated:
            logout(request)
        return redirect(myview)
    else:
        return redirect(myview)

@csrf_exempt
def play(request):
    if request.user.is_authenticated:
        #get all times tables this user should be tested on
        times_tables = Test.objects.filter(user_tested=request.user,set=True)
        times_table_list = []
        for number in times_tables:
            times_table_list.append(number.table_tested)
        return render(request, 'play.html',{'times_table_list':times_table_list})
    else:
        return redirect(myview)

@csrf_exempt
def play_all(request):
    if request.user.is_authenticated:
        #get all times tables this user should be tested on
        times_table_list = [2,3,4,5,6,7,8,9,10,11,12]
        return render(request, 'play_all.html',{'times_table_list':times_table_list})
    else:
        return redirect(myview)




@csrf_exempt  # Only for example. Use CSRF protection in production.
def create_attempt(request):
    if request.method == 'POST':
        a = Attempt()
        correct = request.POST.get('correct', '')
        time_taken = request.POST.get('time_taken','')
        user = request.POST.get('user','')
        x = request.POST.get('x','')
        y = request.POST.get('y','')
        if correct == 'true':
            a.correct = True
            a.time_taken = time_taken
        if correct == 'false':
            a.correct = False
        a.user_asked = User.objects.get(username=user)
        a.question_asked = Question.objects.get(x=x,y=y)
        a.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def teach(request):
    if request.method == "GET":
        if Teacher.objects.filter(user = request.user):
            this_teacher = Teacher.objects.get(user = request.user)
            students = Student.objects.filter(classes=this_teacher)
            array_of_tables = []
            for student in students:
                user = User.objects.get(student=student)
                tables = Test.objects.filter(user_tested=user)
                array_of_tables.append(tables)

            return render(request,'teach.html',{'students':students,'array_of_tables':array_of_tables})
        else:
            return redirect(myview)
    if request.method == "POST":
        results = request.POST.getlist('set')
        this_teacher = Teacher.objects.get(user = request.user)
        students = Student.objects.filter(classes=this_teacher)
        for student in students:
            user_student = User.objects.get(username=student)
            tests_set_to_student = Test.objects.filter(user_tested=user_student)
            for test in tests_set_to_student:
                string = test.user_tested.username + ':' + str(test.table_tested)
                if string in results:
                    test.set = True
                else:
                    test.set = False
                test.save()
        return redirect(myview)
    
@csrf_exempt
def add_students(request):
    if request.method == 'GET':
        teachers = Teacher.objects.all()
        admins = Admin.objects.all()
        students = Student.objects.all()
        student_users = [student.user for student in students]
        teacher_users = [teacher.user for teacher in teachers]
        admin_users = [admin.user for admin in admins]
        students = User.objects.exclude(pk__in=[user.pk for user in teacher_users]).exclude(pk__in=[user.pk for user in admin_users]).exclude(pk__in=[user.pk for user in student_users])
        return render(request,'add_students.html',{'teachers':teachers,'students':students})
    if request.method == 'POST':
        teacher_selected = request.POST.get('teacher_selected')
        user_teaching = User.objects.get(username = teacher_selected)
        teacher_of_class = Teacher.objects.get(user=user_teaching)
        students_selected = request.POST.getlist('students_selected')
        for student_selected in students_selected:
            s = Student()
            user_to_assign = User.objects.get(username = student_selected)
            s.user = user_to_assign
            s.classes = teacher_of_class
            s.save()
            #s.classes.set(teacher_of_class)
        return redirect(myview)

@csrf_exempt
def remove_students(request):
    if request.method == "GET":
        students = Student.objects.all()
        for student in students:
            print(student.classes)
        print(students)
        return render(request, 'remove_students.html',{'students':students})
    if request.method == "POST":
        remove = request.POST.getlist('remove')
        for removee in remove:
            user_of_student = User.objects.get(username = removee)
            s = Student.objects.get(user = user_of_student)
            s.delete()
        return redirect(myview)

@csrf_exempt
def stats(request):
    if not Teacher.objects.filter(user=request.user.id):
        return redirect(myview)
    teacher = Teacher.objects.get(user=request.user.id)
    students = Student.objects.filter(classes=teacher)
    array_of_tables = []
    for student in students:
        user = User.objects.get(student=student)
        tables = Test.objects.filter(user_tested=user).filter(set=True)
        array_of_tables.append(tables)
    return render(request, 'stats.html',{'students':students,'array_of_tables':array_of_tables})

@csrf_exempt
def student_stats(request,student):
    if not Teacher.objects.filter(user=request.user.id):
        return redirect(myview)
    if not User.objects.filter(username=student):
        return render(request, 'student_stats.html',{'message':'Student does not exist','student':student})
    user_to_find = User.objects.get(username=student)
    if not Student.objects.filter(user=user_to_find):
        return render(request, 'student_stats.html',{'message':'User not assigned to class','student':student})
    student_to_find = Student.objects.get(user=user_to_find)
    classes = student_to_find.classes
    if not classes == Teacher.objects.get(user=request.user.id):
        return render(request, 'student_stats.html',{'message':'Student not in your class','student':student})
    query = Attempt.objects.filter(user_asked=user_to_find)
    if not query:
        return render(request, 'student_stats.html',{'message':'Student not used app','student':student})
    df = pd.DataFrame.from_records(query.values())
    x_list = [obj.x for obj in query]
    df['x'] = x_list
    y_list = [obj.y for obj in query]
    df['y'] = y_list
    df_cleaned = df.dropna(subset=['correct'])
    percentage_correct = df_cleaned.groupby(['x', 'y'])['correct'].mean() * 100
    percentage_correct = percentage_correct.reset_index()

    # Create a pivot table
    pivot_table = pd.pivot_table(percentage_correct, values='correct', index='y', columns='x')

    # Display the pivot table
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="RdYlGn", cbar_kws={'label': 'Percentage Correct'})
    plt.title('Percentage Correct Heatmap for x vs y')
    #invert y axis
    ax = plt.gca()
    ax.invert_yaxis()
    # Save the heatmap to a temporary file or buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')

    df_time = df.dropna(subset=['time_taken'])
    average_time = df_time.groupby(['x', 'y'])['time_taken'].mean()
    average_time = average_time.reset_index()

    pivot_table_average_time = pd.pivot_table(average_time, values='time_taken', index='y', columns='x')
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table_average_time, annot=True, fmt=".2f", cmap="RdYlGn_r", cbar_kws={'label': 'Average time'})
    plt.title('Average time Heatmap for x vs y')
    #invert y axis
    ax = plt.gca()
    ax.invert_yaxis()
    img_buffer2 = BytesIO()
    plt.savefig(img_buffer2, format='png')
    img_buffer2.seek(0)
    img_str2 = base64.b64encode(img_buffer2.read()).decode('utf-8')

    
    # Pass the base64-encoded image string to the template



    #get list of 10 worst times tables
    
    grouped = df.groupby('question_asked_id').agg(
    total_questions=pd.NamedAgg(column='id', aggfunc='count'),
    total_correct=pd.NamedAgg(column='correct', aggfunc='sum'),
    mean_time_taken=pd.NamedAgg(column='time_taken', aggfunc='mean')
    ).reset_index()

    # Calculate percentage correct
    grouped['percentage_correct'] = (grouped['total_correct'] / grouped['total_questions']) * 100
    
    #only keep results under 95 correct
    under95 = grouped[grouped['percentage_correct']<95].sort_values(by='percentage_correct')
    print(under95)

    if len(under95)<10:
        rows_needed = 10 - len(under95)
        over95 =  grouped[grouped['percentage_correct']>=95]
        over95_sorted_by_time = over95.sort_values(by='mean_time_taken',ascending=False)
        over_95_rows_needed = over95_sorted_by_time.head(rows_needed)
        print(over_95_rows_needed)
        ten_worst = pd.concat([under95, over_95_rows_needed], axis=0, ignore_index=True)
    else:
        ten_worst = under95.head(10)
    print(ten_worst)
    ten_worst_list = ten_worst['question_asked_id'].to_list()
    
    #prints ten worst in an ordered fasion
    question_list = []
    for i in ten_worst_list:
        q = Question.objects.get(id=i)
        question_list.append(q)

    context = {'heatmap_image': img_str,'heatmap_image2': img_str2,'student':student,'question_list':question_list}
    return render(request, 'student_stats.html',context)

@csrf_exempt
def flash(request,student):

    user_to_find = User.objects.get(username=student)
    query = Attempt.objects.filter(user_asked=user_to_find)
    df = pd.DataFrame.from_records(query.values())
    grouped = df.groupby('question_asked_id').agg(
    total_questions=pd.NamedAgg(column='id', aggfunc='count'),
    total_correct=pd.NamedAgg(column='correct', aggfunc='sum'),
    mean_time_taken=pd.NamedAgg(column='time_taken', aggfunc='mean')
    ).reset_index()

    # Calculate percentage correct
    grouped['percentage_correct'] = (grouped['total_correct'] / grouped['total_questions']) * 100
    
    #only keep results under 95 correct
    under95 = grouped[grouped['percentage_correct']<95].sort_values(by='percentage_correct')
    #print(under95)

    if len(under95)<10:
        rows_needed = 10 - len(under95)
        over95 =  grouped[grouped['percentage_correct']>=95]
        over95_sorted_by_time = over95.sort_values(by='mean_time_taken',ascending=False)
        over_95_rows_needed = over95_sorted_by_time.head(rows_needed)
        #print(over_95_rows_needed)
        ten_worst = pd.concat([under95, over_95_rows_needed], axis=0, ignore_index=True)
    else:
        ten_worst = under95.head(10)
    #print(ten_worst)
    ten_worst_list = ten_worst['question_asked_id'].to_list()
    question_list = []
    answer_list = []
    for i in ten_worst_list:
        q = Question.objects.get(id=i)
        question_string = f"{q.x} x {q.y}"
        answer_string = f"{q.answer}"
        question_list.append(question_string)
        answer_list.append(answer_string)
        
    print('list')
    print(question_list)

    for i in [0,2,4,6,8]:
        mem = answer_list[i]
        answer_list[i] = answer_list[i+1]
        answer_list[i+1] = mem

    print(answer_list)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student}_all_tables.pdf"'


    # Get dimensions of the letter page
    width, height = letter

    # Define the number of columns and rows
    num_columns = 2
    num_rows = 5

    # Set a larger font size for the text (size 45)
    font_size = 55

    # Create a canvas object for the first page
    c = canvas.Canvas(response, pagesize=letter)
    c.setFont("Helvetica", font_size)

    # Draw dotted grids and add text for the first page
    for row in range(num_rows + 1):  # +1 to draw the bottommost horizontal line
        y = row * (height / num_rows)
        c.setStrokeColor(colors.black)
        c.setDash(3, 3)  # Set a 3x3 dot pattern for dotted lines
        c.line(0, y, width, y)

    for col in range(num_columns + 1):  # +1 to draw the rightmost vertical line
        x = col * (width / num_columns)
        c.line(x, 0, x, height)

    
    question_index = 0
    # Add text to each grid cell for the first page
    for row in range(num_rows):
        for col in range(num_columns):
            x_start = col * (width / num_columns)
            x_end = (col + 1) * (width / num_columns)
            y_start = row * (height / num_rows)
            y_end = (row + 1) * (height / num_rows)

            # Calculate the center of the cell to place text
            x_center = (x_start + x_end) / 2
            y_center = (y_start + y_end) / 2
            
            # Generate a unique identifier for each cell
            cell_text = question_list[question_index]
            question_index = question_index + 1

            # Place text in the center of each cell
            c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", font_size) / 2), y_center - (font_size / 2), cell_text)
    small_font_size = 15
    c.setFont("Helvetica", small_font_size)

    #trying to put name of flash card owner
    for row in range(num_rows):
        for col in range(num_columns):
            x_start = col * (width / num_columns)
            x_end = (col + 1) * (width / num_columns)
            y_start = row * (height / num_rows)
            y_end = (row + 1) * (height / num_rows)

            # Calculate the center of the cell to place text
            x_center = (x_start + x_end) / 2
            y_center = ((y_start + y_end) / 2) + 50
            
            # Generate a unique identifier for each cell
            cell_text = student

            # Place text in the center of each cell
            c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", small_font_size) / 2), y_center - (small_font_size / 2), cell_text)

    # Show the first page and start a new page for the second page
    c.showPage()

    # Repeat for the second page
    c.setFont("Helvetica", font_size)

    # Draw dotted grids for the second page
    for row in range(num_rows + 1):  # +1 to draw the bottommost horizontal line
        y = row * (height / num_rows)
        c.setStrokeColor(colors.black)
        c.setDash(3, 3)  # Set a 3x3 dot pattern for dotted lines
        c.line(0, y, width, y)

    for col in range(num_columns + 1):  # +1 to draw the rightmost vertical line
        x = col * (width / num_columns)
        c.line(x, 0, x, height)
    answer_index = 0
    # Add text to each grid cell for the second page
    for row in range(num_rows):
        for col in range(num_columns):
            x_start = col * (width / num_columns)
            x_end = (col + 1) * (width / num_columns)
            y_start = row * (height / num_rows)
            y_end = (row + 1) * (height / num_rows)

            # Calculate the center of the cell to place text
            x_center = (x_start + x_end) / 2
            y_center = (y_start + y_end) / 2

            # Generate a unique identifier for each cell
            cell_text = answer_list[answer_index]
            answer_index = answer_index + 1
            # Place text in the center of each cell
            c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", font_size) / 2), y_center - (font_size / 2), cell_text)

    # Save the PDF
    c.save()

    return response

@csrf_exempt
def student_stats_set(request,student):
    if not Teacher.objects.filter(user=request.user.id):
        return redirect(myview)
    if not User.objects.filter(username=student):
        return render(request, 'student_stats.html',{'message':'Student does not exist','student':student})
    user_to_find = User.objects.get(username=student)
    if not Student.objects.filter(user=user_to_find):
        return render(request, 'student_stats.html',{'message':'User not assigned to class','student':student})
    student_to_find = Student.objects.get(user=user_to_find)
    classes = student_to_find.classes
    if not classes == Teacher.objects.get(user=request.user.id):
        return render(request, 'student_stats.html',{'message':'Student not in your class','student':student})
    
    #find the times tables the student has been set as list
    list_of_tables = []
    tests = Test.objects.filter(user_tested=user_to_find).filter(set=True)
    print('tests')
    print(tests)
    for test in tests:
        list_of_tables.append(test.table_tested)
    print(list_of_tables)

    #get list of set questions
    questions = Question.objects.filter(x__in=list_of_tables)
    print(questions)

    query = Attempt.objects.filter(user_asked=user_to_find).filter(question_asked__in=questions)
    if not query:
        return render(request, 'student_stats.html',{'message':'Student not used app','student':student})
    df = pd.DataFrame.from_records(query.values())
    x_list = [obj.x for obj in query]
    df['x'] = x_list
    y_list = [obj.y for obj in query]
    df['y'] = y_list
    df_cleaned = df.dropna(subset=['correct'])
    percentage_correct = df_cleaned.groupby(['x', 'y'])['correct'].mean() * 100
    percentage_correct = percentage_correct.reset_index()

    # Create a pivot table
    pivot_table = pd.pivot_table(percentage_correct, values='correct', index='y', columns='x')

    # Display the pivot table
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="RdYlGn", cbar_kws={'label': 'Percentage Correct'})
    plt.title('Percentage Correct Heatmap for x vs y')
    #invert y axis
    ax = plt.gca()
    ax.invert_yaxis()
    # Save the heatmap to a temporary file or buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')

    df_time = df.dropna(subset=['time_taken'])
    average_time = df_time.groupby(['x', 'y'])['time_taken'].mean()
    average_time = average_time.reset_index()

    pivot_table_average_time = pd.pivot_table(average_time, values='time_taken', index='y', columns='x')
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table_average_time, annot=True, fmt=".2f", cmap="RdYlGn_r", cbar_kws={'label': 'Average time'})
    plt.title('Average time Heatmap for x vs y')
    #invert y axis
    ax = plt.gca()
    ax.invert_yaxis()
    img_buffer2 = BytesIO()
    plt.savefig(img_buffer2, format='png')
    img_buffer2.seek(0)
    img_str2 = base64.b64encode(img_buffer2.read()).decode('utf-8')

    
    # Pass the base64-encoded image string to the template



    #get list of 10 worst times tables
    
    grouped = df.groupby('question_asked_id').agg(
    total_questions=pd.NamedAgg(column='id', aggfunc='count'),
    total_correct=pd.NamedAgg(column='correct', aggfunc='sum'),
    mean_time_taken=pd.NamedAgg(column='time_taken', aggfunc='mean')
    ).reset_index()

    # Calculate percentage correct
    grouped['percentage_correct'] = (grouped['total_correct'] / grouped['total_questions']) * 100
    
    #only keep results under 95 correct
    under95 = grouped[grouped['percentage_correct']<95].sort_values(by='percentage_correct')
    print(under95)

    if len(under95)<10:
        rows_needed = 10 - len(under95)
        over95 =  grouped[grouped['percentage_correct']>=95]
        over95_sorted_by_time = over95.sort_values(by='mean_time_taken',ascending=False)
        over_95_rows_needed = over95_sorted_by_time.head(rows_needed)
        print(over_95_rows_needed)
        ten_worst = pd.concat([under95, over_95_rows_needed], axis=0, ignore_index=True)
    else:
        ten_worst = under95.head(10)
    print(ten_worst)
    ten_worst_list = ten_worst['question_asked_id'].to_list()
    
    #prints ten worst in an ordered fasion
    question_list = []
    for i in ten_worst_list:
        q = Question.objects.get(id=i)
        question_list.append(q)

    context = {'heatmap_image': img_str,'heatmap_image2': img_str2,'student':student,'question_list':question_list}
    return render(request, 'student_stats.html',context)

@csrf_exempt
def flash_set(request,student):

    user_to_find = User.objects.get(username=student)

    #filter attempts to only questions set

    list_of_tables = []
    tests = Test.objects.filter(user_tested=user_to_find).filter(set=True)
    print('tests')
    print(tests)
    for test in tests:
        list_of_tables.append(test.table_tested)
    print(list_of_tables)

    #get list of set questions
    questions = Question.objects.filter(x__in=list_of_tables)
    print(questions)



    query = Attempt.objects.filter(user_asked=user_to_find).filter(question_asked__in=questions)
    df = pd.DataFrame.from_records(query.values())
    grouped = df.groupby('question_asked_id').agg(
    total_questions=pd.NamedAgg(column='id', aggfunc='count'),
    total_correct=pd.NamedAgg(column='correct', aggfunc='sum'),
    mean_time_taken=pd.NamedAgg(column='time_taken', aggfunc='mean')
    ).reset_index()

    # Calculate percentage correct
    grouped['percentage_correct'] = (grouped['total_correct'] / grouped['total_questions']) * 100
    
    #only keep results under 95 correct
    under95 = grouped[grouped['percentage_correct']<95].sort_values(by='percentage_correct')
    #print(under95)

    if len(under95)<10:
        rows_needed = 10 - len(under95)
        over95 =  grouped[grouped['percentage_correct']>=95]
        over95_sorted_by_time = over95.sort_values(by='mean_time_taken',ascending=False)
        over_95_rows_needed = over95_sorted_by_time.head(rows_needed)
        #print(over_95_rows_needed)
        ten_worst = pd.concat([under95, over_95_rows_needed], axis=0, ignore_index=True)
    else:
        ten_worst = under95.head(10)
    #print(ten_worst)
    ten_worst_list = ten_worst['question_asked_id'].to_list()
    question_list = []
    answer_list = []
    for i in ten_worst_list:
        q = Question.objects.get(id=i)
        question_string = f"{q.x} x {q.y}"
        answer_string = f"{q.answer}"
        question_list.append(question_string)
        answer_list.append(answer_string)
        
    print('list')
    print(question_list)

    for i in [0,2,4,6,8]:
        mem = answer_list[i]
        answer_list[i] = answer_list[i+1]
        answer_list[i+1] = mem

    print(answer_list)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student}_set_tables.pdf"'


    # Get dimensions of the letter page
    width, height = letter

    # Define the number of columns and rows
    num_columns = 2
    num_rows = 5

    # Set a larger font size for the text (size 45)
    font_size = 55

    # Create a canvas object for the first page
    c = canvas.Canvas(response, pagesize=letter)
    c.setFont("Helvetica", font_size)

    # Draw dotted grids and add text for the first page
    for row in range(num_rows + 1):  # +1 to draw the bottommost horizontal line
        y = row * (height / num_rows)
        c.setStrokeColor(colors.black)
        c.setDash(3, 3)  # Set a 3x3 dot pattern for dotted lines
        c.line(0, y, width, y)

    for col in range(num_columns + 1):  # +1 to draw the rightmost vertical line
        x = col * (width / num_columns)
        c.line(x, 0, x, height)

    
    question_index = 0
    # Add text to each grid cell for the first page
    for row in range(num_rows):
        for col in range(num_columns):
            x_start = col * (width / num_columns)
            x_end = (col + 1) * (width / num_columns)
            y_start = row * (height / num_rows)
            y_end = (row + 1) * (height / num_rows)

            # Calculate the center of the cell to place text
            x_center = (x_start + x_end) / 2
            y_center = (y_start + y_end) / 2
            
            # Generate a unique identifier for each cell
            cell_text = question_list[question_index]
            question_index = question_index + 1

            # Place text in the center of each cell
            c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", font_size) / 2), y_center - (font_size / 2), cell_text)
    small_font_size = 15
    c.setFont("Helvetica", small_font_size)

    #trying to put name of flash card owner
    for row in range(num_rows):
        for col in range(num_columns):
            x_start = col * (width / num_columns)
            x_end = (col + 1) * (width / num_columns)
            y_start = row * (height / num_rows)
            y_end = (row + 1) * (height / num_rows)

            # Calculate the center of the cell to place text
            x_center = (x_start + x_end) / 2
            y_center = ((y_start + y_end) / 2) + 50
            
            # Generate a unique identifier for each cell
            cell_text = student

            # Place text in the center of each cell
            c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", small_font_size) / 2), y_center - (small_font_size / 2), cell_text)

    # Show the first page and start a new page for the second page
    c.showPage()

    # Repeat for the second page
    c.setFont("Helvetica", font_size)

    # Draw dotted grids for the second page
    for row in range(num_rows + 1):  # +1 to draw the bottommost horizontal line
        y = row * (height / num_rows)
        c.setStrokeColor(colors.black)
        c.setDash(3, 3)  # Set a 3x3 dot pattern for dotted lines
        c.line(0, y, width, y)

    for col in range(num_columns + 1):  # +1 to draw the rightmost vertical line
        x = col * (width / num_columns)
        c.line(x, 0, x, height)
    answer_index = 0
    # Add text to each grid cell for the second page
    for row in range(num_rows):
        for col in range(num_columns):
            x_start = col * (width / num_columns)
            x_end = (col + 1) * (width / num_columns)
            y_start = row * (height / num_rows)
            y_end = (row + 1) * (height / num_rows)

            # Calculate the center of the cell to place text
            x_center = (x_start + x_end) / 2
            y_center = (y_start + y_end) / 2

            # Generate a unique identifier for each cell
            cell_text = answer_list[answer_index]
            answer_index = answer_index + 1
            # Place text in the center of each cell
            c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", font_size) / 2), y_center - (font_size / 2), cell_text)

    # Save the PDF
    c.save()

    return response

@csrf_exempt
def class_flash(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="class_set_tables.pdf"'

    if not Teacher.objects.filter(user=request.user.id):
        print('not teach')
        return redirect(myview)
    teacher = Teacher.objects.get(user=request.user.id)
    students = Student.objects.filter(classes=teacher)

    # Get dimensions of the letter page
    width, height = letter

    # Define the number of columns and rows
    num_columns = 2
    num_rows = 5

    # Set a larger font size for the text (size 45)
    font_size = 55

    # Create a canvas object for the first page
    c = canvas.Canvas(response, pagesize=letter)

    for student in students:
        list_of_tables = []
        tests = Test.objects.filter(user_tested=student.user).filter(set=True)
        print('tests')
        print(tests)
        for test in tests:
            list_of_tables.append(test.table_tested)
        print(list_of_tables)

        #get list of set questions
        questions = Question.objects.filter(x__in=list_of_tables)
        print(questions)

        
        query = Attempt.objects.filter(user_asked=student.user).filter(question_asked__in=questions)
        df = pd.DataFrame.from_records(query.values())
        df = pd.DataFrame.from_records(query.values())
        grouped = df.groupby('question_asked_id').agg(
        total_questions=pd.NamedAgg(column='id', aggfunc='count'),
        total_correct=pd.NamedAgg(column='correct', aggfunc='sum'),
        mean_time_taken=pd.NamedAgg(column='time_taken', aggfunc='mean')
        ).reset_index()

        # Calculate percentage correct
        grouped['percentage_correct'] = (grouped['total_correct'] / grouped['total_questions']) * 100
        
        #only keep results under 95 correct
        under95 = grouped[grouped['percentage_correct']<95].sort_values(by='percentage_correct')
        #print(under95)

        if len(under95)<10:
            rows_needed = 10 - len(under95)
            over95 =  grouped[grouped['percentage_correct']>=95]
            over95_sorted_by_time = over95.sort_values(by='mean_time_taken',ascending=False)
            over_95_rows_needed = over95_sorted_by_time.head(rows_needed)
            #print(over_95_rows_needed)
            ten_worst = pd.concat([under95, over_95_rows_needed], axis=0, ignore_index=True)
        else:
            ten_worst = under95.head(10)
        #print(ten_worst)
        ten_worst_list = ten_worst['question_asked_id'].to_list()
        question_list = []
        answer_list = []
        for i in ten_worst_list:
            q = Question.objects.get(id=i)
            question_string = f"{q.x} x {q.y}"
            answer_string = f"{q.answer}"
            question_list.append(question_string)
            answer_list.append(answer_string)
            
        print('list')
        print(question_list)

        for i in [0,2,4,6,8]:
            mem = answer_list[i]
            answer_list[i] = answer_list[i+1]
            answer_list[i+1] = mem

        print(answer_list)

    


        
        c.setFont("Helvetica", font_size)

        # Draw dotted grids and add text for the first page
        for row in range(num_rows + 1):  # +1 to draw the bottommost horizontal line
            y = row * (height / num_rows)
            c.setStrokeColor(colors.black)
            c.setDash(3, 3)  # Set a 3x3 dot pattern for dotted lines
            c.line(0, y, width, y)

        for col in range(num_columns + 1):  # +1 to draw the rightmost vertical line
            x = col * (width / num_columns)
            c.line(x, 0, x, height)

        
        question_index = 0
        # Add text to each grid cell for the first page
        for row in range(num_rows):
            for col in range(num_columns):
                x_start = col * (width / num_columns)
                x_end = (col + 1) * (width / num_columns)
                y_start = row * (height / num_rows)
                y_end = (row + 1) * (height / num_rows)

                # Calculate the center of the cell to place text
                x_center = (x_start + x_end) / 2
                y_center = (y_start + y_end) / 2
                
                # Generate a unique identifier for each cell
                cell_text = question_list[question_index]
                question_index = question_index + 1

                # Place text in the center of each cell
                c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", font_size) / 2), y_center - (font_size / 2), cell_text)
        small_font_size = 15
        c.setFont("Helvetica", small_font_size)

        #trying to put name of flash card owner
        for row in range(num_rows):
            for col in range(num_columns):
                x_start = col * (width / num_columns)
                x_end = (col + 1) * (width / num_columns)
                y_start = row * (height / num_rows)
                y_end = (row + 1) * (height / num_rows)

                # Calculate the center of the cell to place text
                x_center = (x_start + x_end) / 2
                y_center = ((y_start + y_end) / 2) + 50
                
                # Generate a unique identifier for each cell
                cell_text = student.user.username

                # Place text in the center of each cell
                c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", small_font_size) / 2), y_center - (small_font_size / 2), cell_text)

        # Show the first page and start a new page for the second page
        c.showPage()

        # Repeat for the second page
        c.setFont("Helvetica", font_size)

        # Draw dotted grids for the second page
        for row in range(num_rows + 1):  # +1 to draw the bottommost horizontal line
            y = row * (height / num_rows)
            c.setStrokeColor(colors.black)
            c.setDash(3, 3)  # Set a 3x3 dot pattern for dotted lines
            c.line(0, y, width, y)

        for col in range(num_columns + 1):  # +1 to draw the rightmost vertical line
            x = col * (width / num_columns)
            c.line(x, 0, x, height)
        answer_index = 0
        # Add text to each grid cell for the second page
        for row in range(num_rows):
            for col in range(num_columns):
                x_start = col * (width / num_columns)
                x_end = (col + 1) * (width / num_columns)
                y_start = row * (height / num_rows)
                y_end = (row + 1) * (height / num_rows)

                # Calculate the center of the cell to place text
                x_center = (x_start + x_end) / 2
                y_center = (y_start + y_end) / 2

                # Generate a unique identifier for each cell
                cell_text = answer_list[answer_index]
                answer_index = answer_index + 1
                # Place text in the center of each cell
                c.drawString(x_center - (c.stringWidth(cell_text, "Helvetica", font_size) / 2), y_center - (font_size / 2), cell_text)
        
        # Show the first page and start a new page for the second page
        c.showPage()

    # Save the PDF
    c.save()

    return response

@csrf_exempt
def class_stats(request):
    if not Teacher.objects.filter(user=request.user.id):
        return redirect(myview)
    
    this_teacher = Teacher.objects.get(user = request.user)
    students = Student.objects.filter(classes=this_teacher)
    list_of_users = []
    for student in students:
        list_of_users.append(student.user.id)
    users = User.objects.filter(id__in=list_of_users)
    print('users')
    print(users)
    query = Attempt.objects.filter(user_asked__in=users)
    df = pd.DataFrame.from_records(query.values())
    print(df)
    x_list = [obj.x for obj in query]
    df['x'] = x_list
    y_list = [obj.y for obj in query]
    df['y'] = y_list
    df_cleaned = df.dropna(subset=['correct'])
    percentage_correct = df_cleaned.groupby(['x', 'y'])['correct'].mean() * 100
    percentage_correct = percentage_correct.reset_index()

    # Create a pivot table
    pivot_table = pd.pivot_table(percentage_correct, values='correct', index='y', columns='x')

    # Display the pivot table
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="RdYlGn", cbar_kws={'label': 'Percentage Correct'})
    plt.title('Percentage Correct Heatmap for x vs y')
    #invert y axis
    ax = plt.gca()
    ax.invert_yaxis()
    # Save the heatmap to a temporary file or buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')

    df_time = df.dropna(subset=['time_taken'])
    average_time = df_time.groupby(['x', 'y'])['time_taken'].mean()
    average_time = average_time.reset_index()

    pivot_table_average_time = pd.pivot_table(average_time, values='time_taken', index='y', columns='x')
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table_average_time, annot=True, fmt=".2f", cmap="RdYlGn_r", cbar_kws={'label': 'Average time'})
    plt.title('Average time Heatmap for x vs y')
    #invert y axis
    ax = plt.gca()
    ax.invert_yaxis()
    img_buffer2 = BytesIO()
    plt.savefig(img_buffer2, format='png')
    img_buffer2.seek(0)
    img_str2 = base64.b64encode(img_buffer2.read()).decode('utf-8')
    context = {'heatmap_image': img_str,'heatmap_image2': img_str2}
    return render(request, 'student_stats.html',context)

"""next steps:

view that shows stats for entire class
function that works out ten worst times table for each student out of the ones they've been set and then returns a pdf of all these flashcards
make time show in seconds, not milliseconds


"""