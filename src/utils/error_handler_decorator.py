
def error_handler_decorator(func):
    
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(e)
            return e
        return func
    return wrapper