from django.shortcuts import render,get_object_or_404

# Create your views here.
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView
from . models import User

class UserListView(ListView):
    model = User
    template_name = 'users/base.html'

def upload_csv(request):
       data = {}
       if "GET" == request.method:
              return render(request, "bmi_business_case/base.html", data)
    # if not GET, then proceed
       else:    
          try:
               csv_file = request.FILES["csv_file"]
               if not csv_file.name.endswith('.csv'):
                     messages.error(request,'File is not CSV type')
                     return HttpResponseRedirect(reverse("bmi_business_case:upload_csv"))
         #if file is too large, return
               if csv_file.multiple_chunks():
                     messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
                     return HttpResponseRedirect(reverse("bmi_business_case:upload_csv"))

               file_data = csv_file.read().decode("utf-8")		

               lines = file_data.split("\n")
               #loop over the lines and save them in db. If error , store as string and then display
               for line in lines:						
                     fields = line.split(",")
                     data_dict = {}
                     data_dict["Gender"] = fields[0]
                     data_dict["Height"] = fields[1]
                     data_dict["Weight"] = fields[2]
                     data_dict["Index"] = fields[3]
                     try:
                        form = User(data_dict)
                        if form.is_valid():
                           form.save()					
                        else:
                           logging.getLogger("error_logger").error(form.errors.as_json())												
                     except Exception as e:
                        logging.getLogger("error_logger").error(repr(e))					
                        pass

          except Exception as e:
            logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
            messages.error(request,"Unable to upload file. "+repr(e))

            return HttpResponseRedirect(reverse("myapp:upload_csv"))
    	

def users_render_pdf_view(request, *args, **kwargs):
   pk = kwargs.get('pk')
   user = get_object_or_404(User, pk=pk)

   template_path = 'users/generate_pdf.html'
   context = {'user': user}
   # Create a Django response object, and specify content_type as pdf
   response = HttpResponse(content_type='application/pdf')

   # to directly download the pdf we need attachment 
   # response['Content-Disposition'] = 'attachment; filename="report.pdf"'

   # to view on browser we can remove attachment 
   response['Content-Disposition'] = 'filename="report.pdf"'

   # find the template and render it.
   template = get_template(template_path)
   html = template.render(context)

   # create a pdf
   pisa_status = pisa.CreatePDF(
      html, dest=response)
   # if error then show some funy view
   if pisa_status.err:
      return HttpResponse('We had some errors <pre>' + html + '</pre>')
   return response