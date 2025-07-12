
# JsonIO

A base class that enables serialization and deserialization of Python object member variables to and from JSON files.
* Multiple class data can be managed in one file.
* Lists or tuples containing objects are not supported.

## Usage
### Inherit JsonIO in own classes
```python
from json_io import JsonIO

class MyConfig(JsonIO):
    def __init__(self):
        super().__init__()
        self.name = "example"
        self.count = 10
        self.options = {"enable": True, "mode": "fast"}

    def _get_root_key(self):
        return "MyConfig"
```
### Save and load json
```py
config = MyConfig()
config.save("config.json")
config.load("config.json")
```