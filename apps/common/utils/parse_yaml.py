# -*- coding: utf-8 -*-
"""
解析yaml文件
"""
import yaml
from pathlib import Path


class ParseYaml(object):

    def __init__(self, file_path):
        self.path = Path(file_path)
        if not self.path.is_file():
            raise ValueError("参数中指定的文件路径不存在。")

    @property
    def dict(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            y = yaml.load(f, Loader=yaml.FullLoader)
            return y


class DictObject(dict):
    def __init__(self, *args, **kwargs):
        super(DictObject, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        value = self.get(key)
        if isinstance(value, dict):
            value = DictObject(value)
        return value


class ProjectConfig(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create_class(cls, class_name: str, class_attr: dict = None, class_parents: tuple = None) -> type:
        # 遍历属性字典，把不是__开头的属性名字变为大写
        new_attr = dict()
        class_name = class_name.title()
        if class_attr:
            for name, value in class_attr.items():
                if not name.startswith("__"):
                    new_attr[name] = value

        # 调用type来创建一个类
        if class_parents:
            for c in class_parents:
                if type(c).__name__ != "type":
                    raise ValueError("class_parents中的元组元素必须为类。")
            new_class = type(class_name, class_parents, new_attr)
        else:
            new_class = type(class_name, (object,), new_attr)
        return new_class

    @staticmethod
    def set_class_attribute(cls: type, **kwargs):
        for key, value in kwargs.items():
            setattr(cls, key, value)
        return cls

    @classmethod
    def get_all_file(cls, config_root: Path):
        all_file_dict = dict()
        for d_ex in config_root.iterdir():
            if d_ex.is_dir():
                sub_file_list = list()
                for d_in in d_ex.iterdir():
                    if d_in.is_file() and d_in.name.endswith(".yaml"):
                        sub_file_list.append({d_in.stem: d_in})
                all_file_dict[d_ex.name] = sub_file_list
            else:
                if d_ex.is_file() and d_ex.name.endswith(".yaml"):
                    all_file_dict[d_ex.stem] = d_ex

        return all_file_dict

    """
    @classmethod
    def get_all_config(cls, config_root: Path) -> dict:
        all_config = dict()
        for directory in config_root.iterdir():
            if directory.is_dir():
                sub_file_list = list()
                for file in directory.iterdir():
                    if file.is_file() and file.name.endswith(".yaml"):
                        sub_file_list.append(file)
                if sub_file_list:
                    all_config[directory.name] = sub_file_list
        return all_config

    @classmethod
    def iterator(cls, value: dict) -> iter:
        if isinstance(value, dict):
            for key, val in value.items():
                yield (key, val)

    @classmethod
    def iterator_plus(cls, value: dict) -> iter:
        for key, val in cls.iterator(value):
            if isinstance(val, (dict, list)):
                for k, v in cls.iterator_plus(val):
                    k = f'{key}.{k}'
                    yield (k, v)
            else:
                yield (key, val)

    @classmethod
    def get_attr_class(cls, config: dict, base_dict: dict) -> dict:
        for x, y in cls.iterator_plus(config):
            base_dict[x] = y
        return base_dict
    """

    @classmethod
    def get_object(cls, env_type: str = None, configuration_path: str = None) -> object:
        import os
        object_dict = dict()
        if configuration_path:
            configuration_path = Path(configuration_path)
            if configuration_path.is_dir():
                all_config = cls.get_all_file(configuration_path)
            else:
                raise ValueError("文件路径非法。")
        else:
            # project_home = Path.cwd().parent.parent.parent
            project_home = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            config_root = Path(project_home, "configuration")
            all_config = cls.get_all_file(config_root)
        for key, value in all_config.items():
            file_object_dict = dict()
            if isinstance(value, list):
                for file_dict in value:
                    for k, v in file_dict.items():
                        file_config = ParseYaml(v).dict
                        if "production" in file_config.keys() or "development" in file_config.keys() or \
                                "testing" in file_config.keys():
                            if env_type:
                                if env_type in ["production", "development", "testing"]:
                                    file_config = file_config.get(env_type)
                                else:
                                    raise ValueError("环境类型非法。")
                            else:
                                if os.getenv("ENV_TYPE"):
                                    file_config = file_config.get(os.getenv("ENV_TYPE"))
                                else:
                                    file_config = file_config.get("development")
                        # 将文件转成字典对象
                        file_config_object = DictObject(file_config)
                        # 将字典对象放入目录列表
                        file_object_dict[k] = file_config_object
                object_dict[key] = cls.create_class(key, file_object_dict)
            else:
                file_config = ParseYaml(value).dict
                if "production" in file_config.keys() or "development" in file_config.keys() or \
                        "testing" in file_config.keys():
                    if env_type:
                        if env_type in ["production", "development", "testing"]:
                            file_config = file_config.get(env_type)
                        else:
                            raise ValueError("环境类型非法。")
                    else:
                        if os.getenv("ENV_TYPE"):
                            file_config = file_config.get(os.getenv("ENV_TYPE"))
                        else:
                            file_config = file_config.get("development")
                file_config_object = DictObject(file_config)
                object_dict[key] = file_config_object
        return cls.create_class("configuration", object_dict)


if __name__ == "__main__":
    from pprint import pprint

    # file = r'E:\git\workflows\configuration\db_config.yaml'
    # pa = ParseYaml(file)
    # pprint(pa.dict)
    config = ProjectConfig.get_object()
    pprint(config.db_config)
