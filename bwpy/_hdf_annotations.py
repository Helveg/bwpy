from functools import wraps


def requires_write_access(f):
    @wraps(f)
    def write_access_required(self, *args, **kwargs):
        if self.mode != "r+":
            raise RuntimeError(f"Missing required write intent on file.")
        f(self, *args, **kwargs)

    return write_access_required
