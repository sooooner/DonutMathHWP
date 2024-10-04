import os
import time
import json
from openai import OpenAI

from .path import json_folder



class APIRequestManager:
    def __init__(self, api_key, temperature=0.0, model='gpt-4o-mini'):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.temperature = temperature
        self.model = model
        self.max_tokens = 2048

    def init_messages(self, content, systems):
        if not isinstance(content, str):
            content = str(content)
        messages = []
        for system in systems:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": content})

        return messages

    def send_request(self, messages):
        if self.model == 'gpt-4o-mini':
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
        else:
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

    def remove_none(self, d):
        if isinstance(d, dict):
            return {k: self.remove_none(v) for k, v in d.items() if v is not None}
        elif isinstance(d, list):
            return [self.remove_none(x) for x in d if x is not None]
        else:
            return d

    def retry_until_success(self, messages):
        success = False
        while not success:
            try:
                response = self.send_request(messages)
                success = True
            except Exception as e:
                print(f"Request failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)
        return response

    def save_response_as_json(self, response, file_name):
        if not os.path.exists(json_folder):
            os.makedirs(json_folder)

        json_path = os.path.join(json_folder, file_name) + '.json'
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(response.to_dict(), json_file, ensure_ascii=False)

    def generate_responses(self, pages, file_name, systems):
        for idx, page in enumerate(pages):
            cur_file_name = f"{file_name}_page_{idx}"
            messages = self.init_messages(page, systems)
            response = self.retry_until_success(messages)
            self.save_response_as_json(response, cur_file_name)