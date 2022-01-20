import json
import requests
import re

class Repository(object):
    def __init__(self, name):
        self.name = name
        self.cache = {}

    def get_download_url(self, branch, path):
        return f"https://raw.githubusercontent.com/{self.name}/{branch}/{path}"

    @property
    def repository_name(self):
        return self.name.split("/")[1]

    def get_tree(self, branch) -> dict:
        self.cache["tree"] = {}
        tmp_tree = {}
        request = requests.get(f"https://api.github.com/repos/{self.name}/git/trees/{branch}?recursive=true")
        if request.status_code == 200:
            r = request.json()
            self.__verify_request(r)
            for i in r["tree"]:
                tmp_tree[i["path"]] = i
            self.cache["tree"][branch] = tmp_tree
            return tmp_tree
        else:
            return None

    def get_size(self, branch):
        size = 0
        cacheres = self.get_cache("tree", branch)
        tree = cacheres if cacheres is not None else self.get_tree(branch)
        for i in tree.values():
            tmp_size = i.get("size")
            size += tmp_size if tmp_size is not None else 0
        return size  # Uncompressed

    def get_cache(self, *args):
        last_arg = None
        for counter, i in enumerate(args):
            getres = self.cache.get(i) if last_arg is None else last_arg.get(i)
            if type(getres) != dict or counter == len(args) - 1:
                return getres
            else:
                last_arg = getres

    def get_commit_info(self, commit):
        commit_info = requests.get(f"https://api.github.com/repos/{self.name}/commits/{commit}").json()
        self.__verify_request(commit_info)
        return commit_info

    def get_latest_commit_hash(self, branch):
        if (cacheres := self.get_cache("branches", branch)) is None:
            request = requests.get(f"https://api.github.com/repos/{self.name}/branches/{branch}")
            if request.status_code == 200:
                r = request.json()
                self.__verify_request(r)
                return r["commit"]["sha"]
            else:
                return None
        else:
            return cacheres["sha"]

    def __verify_request(self, r):
        if type(r) == dict and r.get("message") is not None:
            raise Exception(r.get("message"))

r = Repository("VKCOM/icons")
tree = r.get_tree("master")
tree

largo = {}

for k, v in tree.items():
    if k.startswith("src/svg") and k.count("/") >= 3:
        size = k.split("src/svg")[1].split("/")[1]
        if not largo.get(size): largo[size] = {}
        link = f"https://raw.githubusercontent.com/VKCOM/icons/master/{k}"
        html = requests.get(link).text
        name = k.split("/")[-1]
        largo[size][name] = {"link": link, "html": html, "link_cors": f"https://cors-anywhere.dimden.dev/{link}"}

with open("icons.json", "w") as f:
    # remove comments
    for v in largo.values():
        for value in v.values():
            value['html'] = re.sub("(<!--.*?-->)", "", value['html'])
    json.dump(largo, f, indent=4)