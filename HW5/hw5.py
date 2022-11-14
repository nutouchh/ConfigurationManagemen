import os
import zlib

from graphviz import Digraph

# чтение файла с обработкой байтов
def get_data(path, file):
    with open(path + "\\" + file, 'rb') as f:
        return zlib.decompress(f.read())

def parse(path_g):
    for path, directories, files in os.walk(path_g):  # Рекурсивное получение имен файлов в дереве каталогов.
        if files:
            for file in files:
                data = get_data(path, file)
                # декодировка и обрезаем лишнее получая тип объекта
                obj_type = data.split(b" ")[0].decode()
                if obj_type == "commit":
                    # структура коммита:
                    # [tree_id, [parents_id], author, committer, '', message, '']
                    data = data[data.find(b'\x00') + 1:]
                    commit_info = data.split(b'\n')
                    parents = [parent.split(b" ")[-1].decode() for parent in commit_info if
                               parent.startswith(b"parent")]
                    tree_id = commit_info[0].split(b" ")[-1].decode()
                    message = commit_info[-2].decode()
                    parsed_info = [parents, tree_id, message]
                    # parsed_info = parsing_commit(data[data.find(b'\x00') + 1:])
                elif obj_type == "tree":
                    # parsed_info = parsing_tree(data[data.find(b'\x00') + 1:])
                    # tree: [mode] [name]\x00[SHA-1]
                    # mode: 040000 - директория, 100644 - файл
                    data = data[data.find(b'\x00') + 1:]
                    blobs_id = []
                    while data:
                        delim = data.find(b'\x00')
                        mode, name = data[:delim].split(b" ")

                        is_dir = mode.decode() == "40000"

                        blob_id = data[delim + 1:delim + 21].hex()
                        blobs_id.append([blob_id, name.decode(), is_dir])
                        data = data[delim + 21:]

                        parsed_info = blobs_id
                else:
                    parsed_info = data[data.find(b'\x00') + 1:]
                # добавляем обработанную запись в соответствующую структуру
                database[obj_type][path[-2:] + file] = parsed_info

def graph_tree():
    # получили id дерева и его содержимое
    for tree_id, blobs in trees.items():
        tree_id = tree_id[:8]
        # добавили ноду дерева
        dot.node(tree_id, **styles["tree"])
        for blob in blobs:
            # распаковали информацию об объекте файловой системе
            blob_id, name, is_dir = blob
            blob_id = blob_id[:8]
            # определилили внешний вид ноды: файл или директория
            if is_dir:
                dot.node(blob_id, name, **styles["tree"])
            else:
                dot.node(blob_id, name, **styles["blob"])
            # добавили ребро между деревом и файлом/директорией
            dot.edge(tree_id, blob_id, label=name)


def graph_commit():
    # получили id коммита и его содержимое
    for commit_id, commit_info in commits.items():
        commit_id = commit_id[:8]
        # распаковали информацию о коммите
        parents, tree_id, message = commit_info
        # dot.node(commit_id, message, [style=" "])
        dot.node(commit_id, message, **styles["commit"])
        if not parents:  # случай первого коммита
            head = "HEAD"  # добавляем указатель HEAD
            main = "main"  # и название главной ветки main
            dot.node(head, **styles["HEAD"])
            dot.node(main, **styles["main"])
            dot.edge("HEAD", "main")
            dot.edge("main", commit_id, label=message)
        for parent in parents:  # проходимся по коммитам-родителям
            parent = parent[:8]
            # создали ноду родительского коммита
            dot.node(parent, **styles["commit"])
            # добавили ребро между родительским и текущим коммитом
            dot.edge(parent, commit_id, label=message)
            # добавили ребро между деревом и коммитом
        dot.edge(commit_id, tree_id[:8], label="tree")
    # сохраняем граф
    # print(dot.source)
    dot.view()


if __name__ == '__main__':

    path_git = "C:\\Users\\Anna\\PycharmProjects\\config\\.git\\objects"
    # path_git = "C:\\Users\\Anna\\Desktop\\mypr\\.git\\objects"

    # создание графа
    dot = Digraph()

    # словари для хранения
    commits = dict()
    trees = dict()
    blobs = dict()

    # ......................... СЛОВАРИ ............................

    # словарь для хранения полученных данных
    database = {
        "commit": commits,
        "tree": trees,
        "blob": blobs
    }

    # словарь стилей дерева
    styles = {
        "HEAD": {"shape": "cds", "color": "#ADFF2F", "style": "filled"},
        "main": {"shape": "rectangle", "color": "#ADFF2F", "style": "rounded, filled"},
        "commit": {"shape": "box", "color": "#7FFFD4", "style": "rounded, filled"},
        "tree": {"shape": "folder", "color": "#00BFFF", "style": "rounded, filled"},
        "blob": {"shape": "box", "color": "#1E90FF", "style": "rounded, bold"}
    }

    parse(path_git)  # парсинг файлов
    graph_tree()  # генерируем граф файловых систем
    graph_commit()  # генерируем граф коммитов

