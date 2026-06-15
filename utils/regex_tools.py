import re

def regex_python(text: str):
    matches = re.findall(r"<python>(.*?)</python>", text, re.DOTALL)
    if matches:
        match = matches[0].strip()
        return match
    else:
        return ""
    
def regex_json(text: str):
    matches = re.findall(r"<json>(.*?)</json>", text, re.DOTALL)
    if matches:
        match = matches[0].strip()
        return match
    else:
        return ""
    

def regex_workflow(text: str):
    matches = re.findall(r"<workflow>(.*?)</workflow>", text, re.DOTALL)
    if matches:
        match = matches[0].strip()
        return match
    else:
        return ""

def regex_general(keyword:str, text:str):
    matches = re.findall(r"<"+keyword+r">(.*?)</"+keyword+r">", text, re.DOTALL)
    if matches:
        match = matches[0].strip()
        return match
    else:
        return ""

def regex_json_doc(text):
    matches = re.findall(r"```json(.*?)```", text, re.DOTALL)
    if matches:
        match = matches[0].strip()
        return match
    else:
        return ""