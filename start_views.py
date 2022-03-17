from komarova_framework.templator import render
from patterns.structural_patterns import TimeMetric


class Contacts:
    @TimeMetric(name_cls="Contacts")
    def __call__(self, request):
        return '200 OK', render("contact.html")


class Page:
    @TimeMetric(name_cls="Page")
    def __call__(self, request):
        return '200 OK', render("page.html", date=request.get('date', None))