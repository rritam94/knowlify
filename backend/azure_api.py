import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) 

def complete_api_request(prompt, pdf):
    data =  {
    "messages": [
        {
        "role": "system",
        "content": prompt,
        },

        {
        "role": "user",
        "content": pdf
        },
    ],

    "max_tokens": 4096,
    "temperature": 0.6,
    "top_p": 0.95,
    "top_k": 50,
    "best_of": 1,
    "presence_penalty": 0,
    "use_beam_search": "false",
    "use_cache": "true"
    }

    body = str.encode(json.dumps(data))

    url = 'https://Meta-Llama-3-1-70B-Instruct-yirc.eastus2.models.ai.azure.com/v1/chat/completions'

    api_key = 'ZuxRKCow74ealWvmI4Rgy0slMgx71Kow'

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")


    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        json_string = result.decode('utf-8')
        data = json.loads(json_string)
        message_content = data['choices'][0]['message']['content']
        return message_content
        
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

        return None