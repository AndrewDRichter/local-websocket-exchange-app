
def error_handler_decorator(func):
    
    def wrapper():
        try:
            func()
        except Exception as e:
            print(e)
            return e