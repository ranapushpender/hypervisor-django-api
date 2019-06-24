from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def vmlist_view(request):

    return render(request,'virtualmachines/vmhome.html')