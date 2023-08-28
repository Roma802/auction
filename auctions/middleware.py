from django.http import HttpResponse


# class HelloMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#
#         # Добавляем заголовок к ответу
#         # response['X-Hello'] = 'Hello, World!'
#         print('Hello')
#
#         return response
#
#     def process_exception(self, request, exception):
#         print(f'Exception is {exception}')
#         return HttpResponse('Exception')