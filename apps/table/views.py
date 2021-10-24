from django.shortcuts import render
from django.views import View


class Table(View):
    def get(self, request):
        context = {'segment': 'tables'}
        return render(request, 'table/tables.html', context)
