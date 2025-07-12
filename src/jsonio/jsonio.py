import os
import json
import copy
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

"""
Jsonファイルのエンコーダー/デコーダー
"""
class JsonIO(ABC):
    """
    辞書は値にオブジェクトを持つことを許す
    リスト, タプルがオブジェクトを含む場合は未対応
    """
    def __init__(self):
        pass

    def save(self, path):
        """
        自身のメンバの変数名と値をjsonファイルに保存する
        """
        json_dict = self._serialize_to_dict()
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    json_dict_old = json.load(f)
                except Exception as e:
                    logger.warning("Failed to load existing JSON file %s: %s", path, str(e))
                    json_dict_old = {}

            # 別のクラスのデータ(rootkeyが異なるブロック)は変更せずに, 
            # 自クラスのデータを上書きする
            # 自クラス内でメンバの変更があった場合、古いメンバのデータは消す
            rootkey = self._get_root_key()
            for key in json_dict_old:
                if not key == rootkey:
                    json_dict[key] = json_dict_old[key]

        with open(path, "w") as f:
            json.dump(json_dict, f,  ensure_ascii=False, indent=4,  separators=(',', ': '))

    def load(self, path):
        """
        jsonファイルを開き, 自身のメンバに値を設定する
        """
        if not os.path.exists(path):
            logger.error("File not found: %s", path)
            return

        with open(path, "r") as f:
            try:
                json_dict = json.load(f)
            except Exception as e:
                logger.error("Failed to parse JSON from file %s: %s", path, str(e))
                json_dict = {}

        rootkey = self._get_root_key()
        if not rootkey in json_dict.keys():
            logger.error("Root key not found")
            return
        
        self._update_from_json(self.__dict__, json_dict[rootkey])

    @abstractmethod
    def _get_root_key(self):
        """ jsonファイルのルートキーをここで設定する """
        pass

    def _is_constant(self, val):
        """ valが定数かどうか. 辞書とオブジェクトはFalse
        list, tupleはTrue. list, tupleはオブジェクトを値に持たないとする
        """
        if isinstance(val, (int, float, bool, str, list, tuple)):
            return True
        return False

    def _expand_dict(self, targetdict):
        """
        辞書が保持するオブジェクトを辞書に変換する
        """
        for key in targetdict:
            if self._is_constant(targetdict[key]):
                # 定数データ
                continue

            if isinstance(targetdict[key], dict):
                # 辞書として保持しているパラメータ. 
                # 値にオブジェクトを参照している可能性があるため, 最後の定数値までチェック
                self._expand_dict(targetdict[key]) 
            else:
                # __dict__の中で, オブジェクトメンバは辞書に変換するので, deepcopyする必要がある
                newsubdict = copy.deepcopy(targetdict[key].__dict__)
                self._expand_dict(newsubdict) 
                targetdict[key] = newsubdict

    def _serialize_to_dict(self):
        """
        自身のメンバを辞書に変換. メンバのオブジェクトは展開する
        """
        rootkey = self._get_root_key()
        json_dict = {rootkey: {}}
        json_dict[rootkey] = copy.deepcopy(self.__dict__)
        self._expand_dict(json_dict)
        return json_dict

    def _get_dict_from_json(self, path):
        """
        jsonファイルを開き, 辞書に変換する
        """
        if not os.path.exists(path):
            return {}

        with open(path, "r") as f:
            json_dict = json.load(f)

        rootkey = self._get_root_key()
        if not rootkey in json_dict.keys():
            return {}

        return json_dict
    
    def _is_type_consistent(self, val, val_from_file):
        """
        型の一致をチェック
        """
        if isinstance(val, (int, float)):
            if isinstance(val_from_file, (int, float)):
                return True
        elif isinstance(val, bool):
            if isinstance(val_from_file, (int, bool)):
                return True
        elif isinstance(val, (list, tuple)):
            if isinstance(val_from_file, (list, tuple)):
                return True
        elif isinstance(val, str):
            if isinstance(val_from_file, str):
                return True
        elif isinstance(val_from_file, dict):
                return True

        return False

    def _update_from_json(self, member_dict, json_dict):
        """
        member_dict: オブジェクトの__dict__
        member_dictをjson_dictの値で更新
        """
        for key in member_dict.keys():
            if not key in json_dict.keys():
                continue

            if self._is_constant(member_dict[key]):
                # 定数データ
                if not self._is_type_consistent(member_dict[key], json_dict[key]):
                    # jsonファイルのデータと型の不一致
                    logger.warning("Failed to update data: %s", key)
                    continue
                
                # メンバを更新
                member_dict[key] = json_dict[key]
            else:
                if not isinstance(json_dict[key], dict):
                    # 型の不一致
                    logger.warning("Failed to update data: %s", key)
                    continue

                if isinstance(member_dict[key], dict):
                    # 辞書データ
                    # 辞書の内部にオブジェクトを持っている可能性があるので, 
                    # 一つ一つの定数値毎に更新する
                    self._update_from_json(member_dict[key], json_dict[key])
                else:
                    # オブジェクト
                    self._update_from_json(member_dict[key].__dict__, json_dict[key])
