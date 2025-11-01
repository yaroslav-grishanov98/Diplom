from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthorViewSet, BookViewSet, UserViewSet, RegisterView,
    BookIssueViewSet, book_list, author_list,
    book_detail, author_detail, CommentViewSet,
    RatingViewSet, RegisterPageView, visitor_login,
    book_create, book_edit, author_create, author_edit,
    book_delete, author_delete, add_comment, book_issue_create,
    profile
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register('authors', AuthorViewSet)
router.register('books', BookViewSet)
router.register('users', UserViewSet)
router.register('issues', BookIssueViewSet, basename='issues')
router.register('comments', CommentViewSet)
router.register('ratings', RatingViewSet)

urlpatterns = [
    path('login/visitor/', visitor_login, name='visitor_login'),
    path('login/staff/', auth_views.LoginView.as_view(template_name='library_app/staff_login.html'), name='staff_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),
    path('books-list/', book_list, name='book_list'),
    path('login/', auth_views.LoginView.as_view(template_name='library_app/login.html'), name='login'),
    path('authors-list/', author_list, name='author_list'),
    path('books/<int:pk>/', book_detail, name='book_detail'),
    path('authors/<int:pk>/', author_detail, name='author_detail'),
    path('books/<int:book_id>/rent/', book_issue_create, name='book_issue_create'),
    path('books/add/', book_create, name='book_create'),
    path('authors/add/', author_create, name='author_create'),
    path('books/<int:pk>/edit/', book_edit, name='book_edit'),
    path('authors/<int:pk>/edit/', author_edit, name='author_edit'),
    path('books/<int:pk>/delete/', book_delete, name='book_delete'),
    path('authors/<int:pk>/delete/', author_delete, name='author_delete'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register-page/', RegisterPageView.as_view(), name='register_page'),
    path('books/<int:book_id>/add-comment/', add_comment, name='add_comment'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
