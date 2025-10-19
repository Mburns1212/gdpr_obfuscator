def json_obfuscate(json, piis):
    if isinstance(json, dict):
        for k, v in json.items():
            if k in piis:
                json[k] = '***'
            else:
                json_obfuscate(v, piis)

    if isinstance(json, list):
        for item in json:
            json_obfuscate(item, piis)
