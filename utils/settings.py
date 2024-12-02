# utils/settings.py
import importlib
from config import settings


class LazySettings:
    def __getattr__(self, name):
        value = getattr(settings, name, None)
        if value and "." in value:
            try:
                import_path, obj = value.rsplit(".", 1)
                print(import_path, obj)
                module = importlib.import_module(import_path)
                return getattr(module, obj)
            except ImportError as e:
                raise ImportError(f"Could not import module {import_path}") from e
            except AttributeError as e:
                # Handle circular import gracefully
                raise AttributeError(
                    f"Module {import_path} has no attribute {obj}"
                ) from e
        return value

    def __call__(self, *args, **kwds):
        return self.__getattr__(*args, **kwds)


lazy_settings = LazySettings()
