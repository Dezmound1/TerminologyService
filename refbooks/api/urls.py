from django.urls import path

from refbooks.api.views import CheckElementView, RefBookElementsView, RefBooksListView

urlpatterns = [
    path("refbooks/", RefBooksListView.as_view(), name="refbooks-list"),
    path("refbooks/<int:id>/elements/", RefBookElementsView.as_view(), name="refbook-elements"),
    path("refbooks/<int:id>/check_element/", CheckElementView.as_view(), name="check-element"),
]
