from django.shortcuts import render
from django.views import View

from .utils import delete_from


class Table(View):
    def get(self, request):
        context = {'segment': 'tables'}
        return render(request, 'table/tables.html', context)

    def post(self, request):
        context = {'segment': 'tables'}
        checked = []
        for key, value in request.POST.dict().items():
            if value == 'on':
                checked.append(key.split('&'))
        delete_from(checked)
        return render(request, 'table/tables.html', context)
