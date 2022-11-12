import requests
import json

# Написать на выбранном вами языке программирования программу,
# которая принимает в качестве аргумента командной строки имя пакета,
# а возвращает граф его зависимостей в виде текста на языке Graphviz.

def get_req(package_name, level, parents_list):
    if level > 2: return []
    response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    information = json.loads(response.text)

    try:
        info_list = information['info']['requires_dist']
        info_list = set(map(lambda t: t.split()[0], info_list))
    except:
        return []

    result = []
    for val in info_list:
        pack = val.split()[0]
        if pack in parents_list:
            continue
        result.append(f'"{package_name}"->"{pack}";')
        result.extend(get_req(pack, level + 1, parents_list + [package_name]))
    return result


def writing(f):
    with open("output.txt", 'w') as out:
        out.write("digraph G {\n")
        out.write("\n".join(f))
        out.write("\n}")


# TensorFlow, NumPy, SciPy, Pandas, SciKit-Learn, PyTorch

print("Введите название пакета: ")
package = input()

result = get_req(package, 1, [])

writing(result)
