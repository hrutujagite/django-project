from django.urls import path
from .views import question_list, ask_question,question_detail,edit_question,delete_question,upvote_answer,downvote_answer,delete_answer,edit_answer

urlpatterns = [
    path('', question_list, name='question_list'),  # Show all questions
    path('ask/', ask_question, name='ask_question'),  # Ask a new question
    path('<int:question_id>/', question_detail, name='question_detail'),  
    path('edit/<int:question_id>/', edit_question, name='edit_question'),
    path('<int:question_id>/delete/', delete_question, name='delete_question'),  # Ensure this is added!
    path('<int:answer_id>/upvote/', upvote_answer, name='upvote_answer'),  # ✅ Add this
    path('<int:answer_id>/downvote/', downvote_answer, name='downvote_answer'),  # ✅ Add this
    path('<int:answer_id>/edit/', edit_answer, name='edit_answer'),  # ✅ Add this
    path('<int:answer_id>/delete/', delete_answer, name='delete_answer'),  # ✅ Add this
]


