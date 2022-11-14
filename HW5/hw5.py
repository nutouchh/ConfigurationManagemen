import os
import zlib
from collections import defaultdict, namedtuple
from pathlib import Path

from graphviz import Digraph


class GitParser:
    def __init__(self, rep: str, res: str) -> None:  # Загадка, почему "конструктор" возвращает None
        self.path_to_rep = rep + "\\.git\\objects"  # Путь к репозиторию
        self.path_to_res = res  # Путь к файлу, где будет лежать результат
        self.digraph = Digraph(comment=f'Git Log for {self.path_to_rep}')  # будущий граф

        # структура каждой записи коммита:
        # {commit_id : [[parents_id], tree_id, message]}
        self.commits = defaultdict(list)

        # структура каждой записи дерева:
        # {tree_id : [[blob_id, name, is_dir], ...]}
        self.trees = defaultdict(list)

        self.blobs = defaultdict(list)

        # словарь для быстрого определения обработчика для каждой записи
        self.handlers = {
            "commit": self.parse_commit,
            "tree": self.parse_tree,
            "blob": self.parse_blob
        }

        # словарь для быстрого определения типа записи
        self.database = {
            "commit": self.commits,
            "tree": self.trees,
            "blob": self.blobs
        }

        # словарь для стилей ноды
        self.styles = {
            "commit": {"shape": "cylinder", "color": "#FF9200", "style": "rounded, filled"},
            "tree": {"shape": "folder", "color": "#36D792", "style": "rounded, filled"},
            "blob": {"shape": "note", "color": "#7373D9", "style": "rounded, filled"},
        }

    def parse(self) -> None:
        for path, directories, files in os.walk(self.path_to_rep):
            if files:
                for file in files:
                    with open(path + "\\" + file, 'rb') as f:
                        data = zlib.decompress(f.read())
                    # определяем тип записи и вызываем соответствующий обработчик
                    obj_type = data.split(b" ")[0].decode()
                    parsed_info = self.handlers[obj_type](data[data.find(b'\x00') + 1:])
                    # добавляем обработанную запись в соответствующую структуру
                    self.database[obj_type][path[-2:] + file] = parsed_info
        self.generate_tree_graph()  # генерируем граф файловых систем
        self.generate_commit_graph()  # генерируем граф коммитов

    def generate_tree_graph(self) -> None:
        # получили id дерева и его содержимое
        for tree_id, blobs in self.trees.items():
            tree_id = tree_id[:8]
            # добавили ноду дерева
            self.digraph.node(tree_id, **self.styles["tree"])
            for blob in blobs:
                # распаковали информацию об объекте файловой системе
                blob_id, name, is_dir = blob
                blob_id = blob_id[:8]
                # определилили внешний вид ноды: файл или директория
                if is_dir:
                    self.digraph.node(blob_id, name, **self.styles["tree"])
                else:
                    self.digraph.node(blob_id, name, **self.styles["blob"])
                # добавили ребро между деревом и файлом/директорией
                self.digraph.edge(tree_id, blob_id, label=name)

    def generate_commit_graph(self) -> None:
        # получили id коммита и его содержимое
        for commit_id, commit_info in self.commits.items():
            commit_id = commit_id[:8]
            # распаковали информацию о коммите
            parents, tree_id, message = commit_info
            self.digraph.node(commit_id, message, **self.styles["commit"])
            if not parents: # случай первого коммита
                self.digraph.edge("START", commit_id, label=message)
            for parent in parents: # проходимся по коммитам-родителям
                parent = parent[:8]
                # создали ноду родительского коммита
                self.digraph.node(parent, **self.styles["commit"])
                # добавили ребро между родительским и текущим коммитом
                self.digraph.edge(parent, commit_id, label=message)
                # добавили ребро между деревом и коммитом
            self.digraph.edge(commit_id, tree_id[:8], label="tree")
        # сохраняем граф в файл
        self.digraph.render(self.path_to_res + "\\result.gv", view=True)

    def parse_commit(self, data: bytes) -> list:
        # структура коммита:
        # [tree_id, [parents_id], author, committer, '', message, '']
        commit_info = data.split(b'\n')
        parents = [parent.split(b" ")[-1].decode() for parent in commit_info if parent.startswith(b"parent")]
        tree_id = commit_info[0].split(b" ")[-1].decode()
        message = commit_info[-2].decode()
        return [parents, tree_id, message]

    def parse_tree(self, data: bytes) -> list:
        # структура дерева:
        # [mode] [name]\x00[SHA-1 in binary (20 bytes)]
        # mode - 040000 для директории, 100644 для файла
        blobs_id = []
        while data:
            delim = data.find(b'\x00')
            mode, name = data[:delim].split(b" ")

            is_dir = mode.decode() == "40000"

            blob_id = data[delim + 1:delim + 21].hex()
            blobs_id.append([blob_id, name.decode(), is_dir])
            data = data[delim + 21:]

        return blobs_id

    def parse_blob(self, data: bytes) -> list:
        pass


if __name__ == '__main__':
    # path_to_rep = Path(input() + "\.git\objects")  # Путь к репозиторию
    # path_to_result = Path(input())  # Путь к файлу, где будет лежать результат
    # path_to_rep = "C:\\WorkFolder\\Git_WorkFolder\\test_repo.git"
    path_to_rep = "C:\\Users\\vera3\\PycharmProjects\\ConfigManager5"
    # path_to_res = "C:\\WorkFolder\\Python\\PyCharm_WorkFolder\\Config\\hmw_5"
    path_to_res = "C:\\Users\\vera3\\PycharmProjects\\ConfigManager5"

    git_parser = GitParser(path_to_rep, path_to_res)
    git_parser.parse()
