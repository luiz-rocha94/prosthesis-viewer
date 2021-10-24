from django.shortcuts import render
from django.views import View

from . import utils


class New(View):
    def get(self, request):
        context = {'segment': 'new'}
        return render(request, 'insert/new.html', context)

    def post(self, request):
        context = {'segment': 'new'}
        file = request.FILES.get('zipfile')
        if file:
            utils.insert_data(file)
        else:
            angle0 = int(request.POST.get('angle-0', 5))
            angle1 = int(request.POST.get('angle-1', 30))
            center_y = int(request.POST.get('center-y', 256))
            center_x = int(request.POST.get('center-x', 256))
            name = request.POST.get('name')
            study = request.POST.get('study')
            utils.create_data(name, study, (angle0, angle1), (center_y, center_x))
        return render(request, 'insert/new.html', context)
