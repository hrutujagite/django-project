from django.urls import path
from .views import *

app_name = 'QnA_forum'  # Add this line to namespace the URLs

urlpatterns = [
    path('', question_list, name='question_list'),  # Show all questions
    path('ask/', ask_question, name='ask_question'),  # Ask a new question
    path('<int:question_id>/', question_detail, name='question_detail'),  
    path('edit/<int:question_id>/', edit_question, name='edit_question'),
    path('<int:question_id>/delete/', delete_question, name='delete_question'),  # Ensure this is added!
    path('<int:answer_id>/upvote/', upvote_answer, name='upvote_answer'),  # ✅ Add this
    path('<int:answer_id>/downvote/', downvote_answer, name='downvote_answer'),  # ✅ Add this
    path('answer/<int:answer_id>/delete/', delete_answer, name='delete_answer'),  # ✅ Add this
    path('toggle-report/<int:question_id>/', toggle_report_question, name='toggle_report_question'),
    path('question/<int:question_id>/pin/', toggle_pin_question, name='toggle_pin_question'),
    path('answer/<int:answer_id>/edit/', edit_answer, name='edit_answer'),
    
]



