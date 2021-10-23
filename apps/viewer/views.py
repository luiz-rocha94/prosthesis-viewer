from django.shortcuts import render
from django.views import View

from .utils import get_files


class TcView(View):
    def get(self, request):
        context = {'segment': 'view'}
        return render(request, 'viewer/view.html', context)

    def post(self, request):
        name = request.POST.get('name')
        study = request.POST.get('study')
        context = {'segment': 'view'}
        if name and study:
            files, model, meta = get_files(name, study)
            context.update({'meta': meta, 'files': files, 'model': model})
        return render(request, 'viewer/view.html', context)
