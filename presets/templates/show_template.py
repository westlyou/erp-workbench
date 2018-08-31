SHOW_TAMPLATE = """
yaml-path:
----------
%(base_path)s/yaml

app sequence:
-------------
This sequence defines the loading order.
A lower sequenc means loaded first.
A handler can assume, that the objects created by the 
handlers with lower seguence number than itself are created
and available.

%(app_sequence)s

base presets:
-------------
These are the presets that always will be installed
and every handler can count on

%(base_presets)s

"""