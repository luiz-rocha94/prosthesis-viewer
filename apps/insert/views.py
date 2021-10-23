from django.shortcuts import render
from django.views import View

from . import utils


class New(View):
    def get(self, request):
        context = {'segment': 'new'}

        return render(request, 'insert/new.html', context)

    def post(self, request):
        context = {'segment': 'new'}
        utils.insert_data(request.FILES.get('zipfile'))
        return render(request, 'insert/new.html', context)
