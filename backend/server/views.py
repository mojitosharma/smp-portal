from io import StringIO
from django.shortcuts import render, HttpResponse
from django.core import serializers
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import csv
from datetime import datetime
from django.shortcuts import get_list_or_404


# Create your views here.
def get_all_admins(request):
    # returns list of json ; [{details},{details},...]
    if request.method == "GET":
        admins = Admin.objects.all()  # Fetch all Admin objects from the database.
        return JsonResponse(list(admins), safe=False)
    else:
        return JsonResponse({"message": "Invalid request method"})

def get_admin_by_id(request):
    # returns list of json with one element; [{details}]
    if request.method == "GET":
        id_to_search = json.loads(request.body.decode('utf-8')).get('id')
        admin = Admin.objects.filter(id=id_to_search)
        return JsonResponse(list(admin), safe=False)
    else:
        return JsonResponse({"message": "Invalid request method"})

def get_all_mentors(request):
    # returns list of json ; [{details}, {details}, ...]
    if request.method == "GET":
        mentors_from_candidates = Candidate.objects.filter(status=3).values()
        for mentor in mentors_from_candidates:
            # adding other 'goodiesStatus' and 'reimbursement' details
            id_to_search = mentor['id']
            other_details = Mentor.objects.filter(id=id_to_search).values()
            mentor.update({'goodiesStatus': other_details[0]['goodiesStatus'],
                           'reimbursement': other_details[0]['reimbursement']})
            mentor.pop("imgSrc")
            # adding menteesToMentors list
            menteesToMentors = []
            mentees = Mentee.objects.filter(mentorId=str(id_to_search)).values()
            
            for mentee in mentees:
                menteesToMentors.append([mentee['id'], mentee['name'], mentee['email']])
            mentor.update({'menteesToMentors': menteesToMentors})
        return JsonResponse(list(mentors_from_candidates), safe=False)
    else:
        return JsonResponse({"message": "Invalid request method"})

# Done
@csrf_exempt 
def get_mentor_by_id(request):
    # returns list of json with one element; [{details}]
    if request.method == "POST":
        id_to_search = json.loads(request.body.decode('utf-8')).get('id')
        mentor = Candidate.objects.filter(status=3, id=id_to_search).values()

        # adding 'goodiesStatus' and 'reimbursement' details
        other_details = Mentor.objects.filter(id=id_to_search).values()
        if len(mentor) == 0: 
            return JsonResponse({"message": "Mentor Not Found"})
        mentor[0].update({'goodiesStatus': other_details[0]['goodiesStatus'],
                        'reimbursement': other_details[0]['reimbursement']})
        mentor[0].pop("imgSrc")
        # adding menteesToMentors list
        menteesToMentors = []
        mentees = Mentee.objects.filter(mentorId=str(id_to_search)).values()
        for mentee in mentees:
            menteesToMentors.append([mentee['id'], mentee['name'], mentee['email']])
        mentor[0].update({'menteesToMentors': menteesToMentors})
        return JsonResponse(mentor[0], safe=False)
    else:
        return JsonResponse({"message": "Invalid request method"})

# Done
def get_all_mentees(request):
    # returns list of json ; [{details}, {details}, ...]
    if request.method == "GET":
        mentees = Mentee.objects.all().values()
        for mentee in mentees:
            # adding other 'mentorName' and 'mentorEmail' details
            mentor_id_to_search = mentee['mentorId']
            mentor = Candidate.objects.filter(id=mentor_id_to_search).values()
            if len(mentor): 
                 mentee.update({'mentorId': mentor[0]['id'],
                            'mentorName': mentor[0]['name'],
                            'mentorEmail': mentor[0]['email']})
            else: 
                mentee.update({'mentorId': 'NULL',
                           'mentorName': 'NULL',
                           'mentorEmail': 'NULL'})
        return JsonResponse(list(mentees), safe=False)
    else:
        return JsonResponse({"message": "Invalid request method"})

def get_mentee_by_id(request):
    # returns list of json with one element; [{details}]
    if request.method == "GET":
        id_to_search = json.loads(request.body.decode('utf-8')).get('id')
        mentees = Mentee.objects.filter(id=id_to_search).values()
        for mentee in mentees:
            # adding other 'mentorName' and 'mentorEmail' details
            mentor_id_to_search = mentee['mentorId']
            mentor = Candidate.objects.filter(id=mentor_id_to_search).values()
            if len(mentor): 
                 mentee.update({'mentorId': mentor[0]['id'],
                            'mentorName': mentor[0]['name'],
                            'mentorEmail': mentor[0]['email']})
            else: 
                mentee.update({'mentorId': 'NULL',
                           'mentorName': 'NULL',
                           'mentorEmail': 'NULL'})
        return JsonResponse(list(mentees), safe=False)
    else:
        return JsonResponse({"message": "Invalid request method"})


@csrf_exempt 
def get_id_by_email(request):
    if request.method == "POST":
        email = json.loads(request.body.decode('utf-8')).get('email')
        role = json.loads(request.body.decode('utf-8')).get('role')
        try: 
            if not email or not role:
                return JsonResponse({'error': 'Invalid email or role'}, status=400)
            
            if role == "admin":
                entry = Admin.objects.filter(email=email).values()
            elif role == "mentor":
                entry = Candidate.objects.filter(email=email).values()
            elif role == "mentee":
                entry = Mentee.objects.filter(email=email).values()
                for mentee in entry:
            # adding other 'mentorName' and 'mentorEmail' details
                    mentor_id_to_search = mentee['mentorId']
                    mentor = Candidate.objects.filter(id=mentor_id_to_search).values()
                    if len(mentor): 
                        mentee.update({'mentorId': mentor[0]['id'],
                                    'mentorName': mentor[0]['name'],
                                    'mentorEmail': mentor[0]['email']})
                    else: 
                        mentee.update({'mentorId': 'NULL',
                                'mentorName': 'NULL',
                                'mentorEmail': 'NULL'})

                print(entry)

            if(len(entry) == 0):
                data_dict = {
                    'id': -1
                }
                serialized_data = json.dumps(data_dict)
                return JsonResponse(serialized_data, safe=False)
            return JsonResponse(entry[0], safe=False)
        except: 
            data_dict = {
                'id': -1
            }
            serialized_data = json.dumps(data_dict)
            return JsonResponse(serialized_data, safe=False)
    else: 
        return JsonResponse({"message": "Invalid request method"})



def delete_all_admins(request):
    # returns json ; {"message": "//message//"}
    if request.method == "GET":
        deleted = Admin.objects.all().delete()
        return JsonResponse({"message": "deleted "+str(deleted[0])+" database entries"})
    else:
        return JsonResponse({"message": "Invalid request method"})

def delete_admin_by_id(request):
    # returns json ; {"message": "//message//"}
    if request.method == "GET":
        id_to_search = json.loads(request.body.decode('utf-8')).get('id')
        deleted = Admin.objects.filter(id=id_to_search).delete()
        return JsonResponse({"message": "deleted "+str(deleted[0])+" database entries"})
    else:
        return JsonResponse({"message": "Invalid request method"})

def delete_all_mentors(request):
    # returns json ; {"message": "//message//"}
    if request.method == "GET":
        deleted = Candidate.objects.filter(status=3).delete()
        deleted = Mentor.objects.all().delete()
        return JsonResponse({"message": "deleted "+str(deleted[0])+" database entries"})
    else:
        return JsonResponse({"message": "Invalid request method"})

# Done   
@csrf_exempt
def delete_mentor_by_id(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        mentor_id = data.get('id')
        try:
            """
            mentor same department ka hona cahiye
            """
            highest_score_mentor = Candidate.objects.filter(status=1).order_by('-score').values()
            if(len(highest_score_mentor) == 0):
                return JsonResponse({"message": "No new mentor to replace"})
            highest_score_mentor = highest_score_mentor[0]
            Mentee.objects.filter(mentorId=mentor_id).update(mentorId=highest_score_mentor["id"])
            deleted = Mentor.objects.filter(id=mentor_id).delete()
            candidate = Candidate.objects.get(id=mentor_id)
            candidate.status = -1
            candidate.save()
            highest_score_mentor_id = highest_score_mentor["id"]
            candidate_new = Candidate.objects.get(id=highest_score_mentor_id)
            candidate_new.status = 3
            candidate_new.save()
            mentor = Mentor(id = highest_score_mentor["id"], goodiesStatus = 0, reimbursement = 0 )
            mentor.save()
            return JsonResponse({"message": f"Repalced Mentor ID: {highest_score_mentor_id}"})
        except Mentor.DoesNotExist:
            return JsonResponse({"message": "Mentor not found"})
    else:
        return JsonResponse({"message": "No new mentor to replace"})

# Done
def delete_all_mentees(request):
    # returns json ; {"message": "//message//"}
    if request.method == "GET":
        deleted = Mentee.objects.all().delete()
        return JsonResponse({"message": "deleted "+str(deleted[0])+" database entries"})
    else:
        return JsonResponse({"message": "Invalid request method"})

# Done
@csrf_exempt
def delete_mentee_by_id(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        id_to_search = json.loads(request.body.decode()).get('id')
        deleted = Mentee.objects.filter(id=str(id_to_search)).delete()
        return JsonResponse({"message": "deleted "+str(deleted[0])+" database entries"})
    else:
        return JsonResponse({"message": "Invalid request method"})

@csrf_exempt
def add_admin(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        new_admin = Admin(id=data.get('id'), name=data.get('name'), email=data.get('email'),
                          department=data.get('department'), phone=data.get('phone'),
                          address=data.get('address'), imgSrc=data.get('imgSrc'))
        new_admin.save()
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})

@csrf_exempt
def add_mentor(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        new_candidate = Candidate(id=data.get('id'), name=data.get('name'), email=data.get('email'),
                          department=data.get('department'), year=data.get('year'),
                          size=data.get('size'), score=data.get('score'),
                          status=3, imgSrc=data.get('imgSrc'))
        new_candidate.save()
        
        new_mentor = Mentor(id=data.get('id'), goodiesStatus=data.get('goodiesStatus'),
                            reimbursement=data.get('reimbursement'))
        new_mentor.save()
        
        for mentee_id in data.get('menteesToMentors'):
            mentee = Mentee.objects.get(id=mentee_id)
            mentee.mentorId = data.get('id')
            mentee.save()
        
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})

# Done
@csrf_exempt
def add_mentee(request):
    # returns json ; {"message": "//message//"}
    """
    check if there departmente is same or not
    """
    existing_mentee = Mentee.objects.filter(id=data.get('id')).first()
    if existing_mentee:
        raise JsonResponse({"message": "Mentee with this ID"})

    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        new_mentee = Mentee(id=data.get('id'), name=data.get('name'), email=data.get('email'),
                          department=data.get('department'))

        mentor = Candidate.objects.filter(status=3, id=str(data.get('mentorId')))
        if(data.get('imgSrc')):
            new_mentee.imgSrc = data.get('imgSrc')
        if len(mentor) == 0: 
            return JsonResponse({"message": "Mentor Not Found"})
        new_mentee.mentorId = mentor[0].id
        new_mentee.save()
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})


# Done
@csrf_exempt
def add_candidate(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        new_candidate = Candidate(id=data.get('id'), name=data.get('name'), email=data.get('email'),
                          department=data.get('department'), year=data.get('year'),
                          size=data.get('size'), score=data.get('score'),
                          status=1)
        if(data.get('imgSrc')):
            new_candidate.imgSrc = data.get('imgSrc')
        new_candidate.save()
        
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})


@csrf_exempt
def edit_admin_by_id(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        admin = Admin.objects.get(id=data.get('id'))
        
        if(data.get('fieldName')=="name"):
            admin.name = data.get('newValue')
        elif(data.get('fieldName')=="email"):
            admin.email = data.get('newValue')
        elif(data.get('fieldName')=="department"):
            admin.department = data.get('newValue')
        elif(data.get('fieldName')=="phone"):
            admin.phone = data.get('newValue')
        elif(data.get('fieldName')=="address"):
            admin.address = data.get('newValue')
        elif(data.get('fieldName')=="imgSrc"):
            admin.imgSrc = data.get('newValue')

        admin.save()
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})

@csrf_exempt
def edit_mentor_by_id(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        candidate = Candidate.objects.get(id=data.get('id'))
        mentor = Mentor.objects.get(id=data.get('id'))

        if(data.get('fieldName')=="name"):
            candidate.name = data.get('newValue')
        elif(data.get('fieldName')=="email"):
            candidate.email = data.get('newValue')
        elif(data.get('fieldName')=="department"):
            candidate.department = data.get('newValue')
        elif(data.get('fieldName')=="imgSrc"):
            candidate.imgSrc = data.get('newValue')
        elif(data.get('fieldName')=="year"):
            candidate.year = data.get('newValue')
        elif(data.get('fieldName')=="size"):
            candidate.size = data.get('newValue')
        elif(data.get('fieldName')=="score"):
            candidate.score = data.get('newValue')
        elif(data.get('fieldName')=="goodiesStatus"):
            mentor.goodiesStatus = data.get('newValue')
        elif(data.get('fieldName')=="reimbursement"):
            mentor.reimbursement = data.get('newValue')
        elif(data.get('fieldName')=="menteesToMentors"):
            for mentee_id in data.get('newValue'):
                mentee = Mentee.objects.get(id=mentee_id)
                mentee.mentorId = data.get('id')

        candidate.save()
        mentor.save()
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})

@csrf_exempt
def edit_mentee_by_id(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        mentee = Mentee.objects.get(id=data.get('id'))

        if(data.get('fieldName')=="name"):
            mentee.name = data.get('newValue')
        elif(data.get('fieldName')=="email"):
            mentee.email = data.get('newValue')
        elif(data.get('fieldName')=="department"):
            mentee.department = data.get('newValue')
        elif(data.get('fieldName')=="imgSrc"):
            mentee.imgSrc = data.get('newValue')
        elif(data.get('fieldName')=="mentorId"):
            mentee.mentorId = data.get('newValue')            

        mentee.save()
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})

# Done
@csrf_exempt
def upload_CSV(request):
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'csvFile' in request.FILES:
            
            uploaded_file = request.FILES['csvFile']
            file_contents = uploaded_file.read()
            csv_data = file_contents.decode('iso-8859-1')
            # Use StringIO to simulate a file-like object for csv.reader
            csv_io = StringIO(csv_data)
            # Parse the CSV data
            csv_reader = csv.reader(csv_io)
            csv_list = [row for row in csv_reader]
            # Convert the CSV data to a list of dictionaries
            header = csv_list[0]
            csv_data_list = [dict(zip(header, row)) for row in csv_list[1:]]
            Mentee.objects.all().delete()
            for item in csv_data_list:
                mentee = Mentee(
                    id=item['id'],
                    email=item['email'],
                    name=item['name'],
                    department=item['department']
                )
                mentee.save()

            return JsonResponse({'message': 'File uploaded and processed successfully'})
        else:
            return JsonResponse({'message': 'No file was uploaded'}, status=400)
    else:
        return JsonResponse({'message': 'Unsupported HTTP method'}, status=405)
    
def index(request):
    return HttpResponse("home")

# Done
@csrf_exempt
def add_meeting(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        scheduler_id = data.get('schedulerId')
        date = data.get('date')
        time = data.get('time')
        attendeelist=data.get('attendee')
        attendeevalue = -1
        if "Mentees" in attendeelist and "Mentors" in attendeelist:
            attendeevalue = 3
        elif "Mentors" in attendeelist:
            attendeevalue = 1
        elif "Mentees" in attendeelist:
            attendeevalue = 2

        # Check if a meeting with the same scheduler_id, date, and time already exists
        existing_meeting = Meetings.objects.filter(
            schedulerId=scheduler_id,
            date=date,
            time=time
        ).first()

        if existing_meeting:
            return JsonResponse({"message": "Meeting already scheduled at the same date and time"})
        else:
            new_meeting = Meetings(
                schedulerId=scheduler_id,
                date=date,
                time=time,
                attendee=attendeevalue,
                description=data.get('description')
            )
            new_meeting.save()
            return JsonResponse({"message": "Data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})

@csrf_exempt
def edit_meeting_by_id(request):
    # returns json ; {"message": "//message//"}
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        data = data[0]
        meeting = Meetings.objects.get(meetingId=data.get('id'))
        meeting.schedulerId = data.get('schedulerId')
        meeting.date = data.get('date')
        meeting.time = data.get('time')
        meeting.attendee = data.get('attendee')
        meeting.description = data.get('description')
        
        meeting.save()
        return JsonResponse({"message": "data added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"})
    
@csrf_exempt
def delete_meeting_by_id(request):
    if request.method == "POST":
        id_to_search = json.loads(request.body.decode('utf-8')).get('meetingId')
        deleted = Meetings.objects.filter(meetingId=id_to_search).delete()
        return JsonResponse({"message": "deleted "+str(deleted[0])+" database entries"})
    else:
        return JsonResponse({"message": "Invalid request method"})

@csrf_exempt
def get_meetings(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        user_type = data.get('role')
        user_id = data.get('id')
        current_datetime = datetime.now()
        
        if user_type == "admin":
            all_meetings = Meetings.objects.all().values()
        elif user_type == "mentor":
            # Return meetings organized by the mentor, and meetings where the mentor is an attendee (1 or 3)
            organized_meetings = Meetings.objects.filter(schedulerId=user_id)
            attendee_meetings = Meetings.objects.filter(attendee__in=[1, 3])  # Include 1 (mentor) and 3 (both mentor and mentee)
            all_meetings = organized_meetings | attendee_meetings
        elif user_type == "mentee":
            # Return meetings organized by the mentee's mentor and meetings where the mentee is an attendee
            mentor = Mentee.objects.get(id=user_id).mentorId
            mentor_meetings = Meetings.objects.filter(schedulerId=mentor)
            attendee_meetings = Meetings.objects.filter(attendee__in=[2, 3])  # Include 2 (mentee) and 3 (both mentor and mentee)
            all_meetings = mentor_meetings | attendee_meetings
        else:
            return JsonResponse({"message": "Invalid user type"})

        # Create lists for previous, next, and upcoming meetings
        previous_meetings = []
        upcoming_meetings = []

        # Categorize meetings based on their date and time
        for meeting in all_meetings:
            meeting_date = datetime.strptime(f"{meeting['date']} {meeting['time']}", '%Y-%m-%d %H:%M')
            if meeting_date < current_datetime:
                previous_meetings.append(meeting)
            elif meeting_date > current_datetime:
                upcoming_meetings.append(meeting)

        meetings_data = {
            "previousMeeting":  previous_meetings,
            "upcomingMeeting": upcoming_meetings
        }
        return JsonResponse(meetings_data)
    else:
        return JsonResponse({"message": "Invalid request method"})
    
'''
Mentor mentee mapping karni hai
list of dep - then get mentees - then btta 5 - then top n candidates with status 1 - send consent form - then do the matching - update status
repeat 
mentor delete and add mei department check krna h 
form wala check krna h 
mentor ke details ke sath login pr form status bhi add kr de 
iiitd id check kr lo 
'''
# def mentor_mentee_mapping(request):
#     # Initialize dictionaries to track mentors and their assigned mentees
#     mentors = {}
#     assigned_mentees = {}
#     mentees_per_mentor = 5

#     # Get a list of all candidates, sorted by department and score in descending order
#     candidates = Candidate.objects.order_by('-department', '-score')

#     for candidate in candidates:
#         if candidate.department not in mentors:
#             # If there are no mentors for this department, add one
#             mentors[candidate.department] = [candidate]
#             assigned_mentees[candidate.id] = candidate.department
#         else:
#             # Check if the mentor already has enough mentees
#             mentor_department = assigned_mentees[candidate.id]
#             if len(mentors[mentor_department]) < mentees_per_mentor:
#                 mentors[mentor_department].append(candidate)
#             else:
#                 # If the mentor has enough mentees, assign the mentee to another mentor in the same department
#                 for mentor_id in mentors[mentor_department]:
#                     if len(mentors[mentor_department]) < mentees_per_mentor:
#                         mentors[mentor_department].append(candidate)
#                         assigned_mentees[candidate.id] = mentor_department
#                         break

#     # Return the mentor-mentee mapping
#     return mentors
