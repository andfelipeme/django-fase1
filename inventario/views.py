from django.http import HttpResponse


# Create your views here.
def inicio(request):
    return HttpResponse("Inventario del taller")


def materiales(request):
    return HttpResponse("Lista de materiales")
