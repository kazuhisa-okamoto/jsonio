import os
import pytest
from jsonio import JsonIO

class MySubConfig():
    def __init__(self):
        self.listdata = []

class MyConfig(JsonIO):
    """
    Test class
    """
    def __init__(self):
        super().__init__()
        self.strdata = ""
        self.numdata = 0 
        self.dictdata = {"bool_value": True, "float_value": 1.23, "sub_config": MySubConfig()}

    def _get_root_key(self):
        return "MyConfig"

class AnotherConfig(JsonIO):
    """
    Another test class
    """
    def __init__(self):
        super().__init__()
        self.name = ""
        self.count = 0
        self.items = []
        self.settings = {"enabled": False, "timeout": 30}

    def _get_root_key(self):
        return "AnotherConfig"

def test_jsonio():
    config = MyConfig()
    another_config = AnotherConfig()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "test.json")

    # Prepare test data
    config.strdata = "strdata"
    config.numdata = 42
    config.dictdata["bool_value"] = False
    config.dictdata["float_value"] = 3.14
    config.dictdata["sub_config"].listdata = [1, 2, 3, 4, 5]

    another_config.name = "TestApp"
    another_config.count = 100
    another_config.items = ["item1", "item2", "item3"]
    another_config.settings["enabled"] = True
    another_config.settings["timeout"] = 60

    # Test save and load
    try:
        config.save(json_path)
        another_config.save(json_path)

        loaded_config = MyConfig()
        loaded_another_config = AnotherConfig()
        
        loaded_config.load(json_path)
        loaded_another_config.load(json_path)

        assert loaded_config.strdata == "strdata"
        assert loaded_config.numdata == 42
        assert loaded_config.dictdata["bool_value"] == False
        assert loaded_config.dictdata["float_value"] == 3.14
        assert loaded_config.dictdata["sub_config"].listdata == [1, 2, 3, 4, 5]

        assert loaded_another_config.name == "TestApp"
        assert loaded_another_config.count == 100
        assert loaded_another_config.items == ["item1", "item2", "item3"]
        assert loaded_another_config.settings["enabled"] == True
        assert loaded_another_config.settings["timeout"] == 60

    finally:
        pass