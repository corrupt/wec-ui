import json

def default_profile(title):
    return json.dumps(
        {
            "url": "",
            "title": title,
            "visitpages": 50,
            "firstparty": [],
            "mustvisit": []
        }
    )