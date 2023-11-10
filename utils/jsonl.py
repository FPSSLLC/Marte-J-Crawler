from dotenv import load_dotenv
import time
import json

class Output:
    def __init__(self, config):
        
        self.file_path = f"{config['dirname']}/output/{config['domain']}_{int(time.time())}.jsonl"
        self.file = open(self.file_path, 'w')

    def write_listing(self, data):
        for url in data:
            json.dump({"url":url}, self.file,indent=4)
            self.file.write('\n')

    def write_products(self, data):
        json.dump(data, self.file,indent=4)
        self.file.write('\n')

    def close(self):
        self.file.close()
