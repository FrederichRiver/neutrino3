#!/usr/bin/python3
import copy
import re

class ProviderBackendMixin(object):
    def get_default_backend(self):
        backend = {}
        provider_name: str = re.findall("[A-Z][^A-Z]*", self.__class__.__name__)[-2]
        # set default storage class
        backend.setdefault("class", f"File{provider_name}Storage")
        # set default storage module
        backend.setdefault("module_path", "qlib.data.storage.file_storage")
        return backend

    def backend_obj(self, **kwargs):
        backend = self.backend if self.backend else self.get_default_backend()
        backend = copy.deepcopy(backend)

        # set default storage kwargs
        backend_kwargs = backend.setdefault("kwargs", {})
        # default provider_uri map
        if "provider_uri" not in backend_kwargs:
            # if the user has no uri configured, use: uri = uri_map[freq]
            freq = kwargs.get("freq", "day")
            provider_uri_map = backend_kwargs.setdefault("provider_uri_map", {freq: C.get_data_path()})
            backend_kwargs["provider_uri"] = provider_uri_map[freq]
        backend.setdefault("kwargs", {}).update(**kwargs)
        return init_instance_by_config(backend)

