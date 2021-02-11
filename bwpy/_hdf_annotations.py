from functools import wraps


def _checkpoint(decorator):
    def dispatcher(given):
        if callable(given):
            r = decorator(given)
            return r
        else:

            def wrapper(inner):
                def decoration(self, *args, **kwargs):
                    file = getattr(self, given)
                    decorator(lambda s: None)(file)
                    return inner(self, *args, **kwargs)

                return decoration

            return wrapper

    return dispatcher


def requires_write_access(f):
    @wraps(f)
    def write_access_required(self, *args, **kwargs):
        if self.mode != "r+":
            raise RuntimeError(f"Missing required write intent on file.")
        return f(self, *args, **kwargs)

    return write_access_required


@_checkpoint
def requires_bxr(f):
    @wraps(f)
    def bxr_required(self, *args, **kwargs):
        if self.type != "bxr":
            raise RuntimeError(f"File type must be BXR to use this feature.")
        return f(self, *args, **kwargs)

    return bxr_required
