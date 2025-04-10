import json
from typing import Optional
from base_bot.browser_client_base_bot import BrowserClientBaseBot
from dotenv import load_dotenv
import os

from classes.bot_helper import ensure_downloads_folder
from classes.dynamic_script_executor import DynamicScriptExecutor

load_dotenv()

class FilePreparationParentBot(BrowserClientBaseBot):
    def __init__(self, options=None, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.variables = [
            "order_number", # non sensitive data, ok to be sent to LLM
            "x_county", # count is also OK to be sent to LLM
        ]
        
        self.script_executor = DynamicScriptExecutor(self, os.path.join(os.getcwd(), 'scripts'))
    
    def validate_data(self, message):
        
        botstates = self.get_bot_state()
        if any(task.status == "in_progress" for task in botstates.tasks):
            raise Exception("Task currently in progress. Please wait for it to complete.")
                
        json_data = super().extract_json_data(message)
        if json_data is None:
            raise Exception("JSON data is None")
        
        order_number = json_data.get('order_number', None)
        if not order_number:
            raise Exception("Order Number is None")
        
        context = json_data.get('context', None)
        if context is None:
            raise Exception("Context is None")
        
        database_id = context.get("id")
        
        self.new_task_started(database_id, f"order_number: {order_number}")
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": 'Message is received, processing... >>>'
        })
        
        return [json_data, order_number, context, database_id]
        
    def extract_sensitive_data(self, json_data):
        if json_data:
            s_data = json_data.get('s_data', {})
        else:
            s_data = {}
        return s_data
    
    async def prepare_LLM_data(self, json_data, message, v2_config: dict = None):
        if not v2_config:
            raise Exception("Your need V2 configuration for this bot.")
        
        sensitive_data = self.extract_sensitive_data(json_data)
        order_number = json_data.get('order_number', None)
        context = json_data.get('context', {})
        
        # verify if folder is already created, to check this we need to make API call to get the order details
        dl_f = await ensure_downloads_folder(self, context.get('id', None), order_number)
        self.config['custom_downloads_path'] = dl_f
        
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": f"Processing action {v2_config.get('name', '')}... >>>"
        })
        [instructions, extend_system_prompt] = await self.v2_prompt(v2_config)
            
        self.script_executor.set_session_data({
            'message': message,
            'json_data': json_data,
            'sensitive_data': sensitive_data,
            'instructions': instructions,
            'extend_system_prompt': extend_system_prompt
        })
        
        # after loading prompt, we can execute the script
        for script in v2_config.get('prompt_scripts', []):
            [file_name, function_name] = script.split(':')
            await self.script_executor.execute(file_name.strip(), function_name.strip())

        instructions = self.script_executor.SessionData.get('instructions', '')
        extend_system_prompt = self.script_executor.SessionData.get('extend_system_prompt', '')
        sensitive_data = self.script_executor.SessionData.get('sensitive_data', None)
        
        if json_data is not None:
            cleaned_message = message.get('content', '').replace(message.get('content', '').split('[json]')[1].split('[/json]')[0], '').replace('[json]', '').replace('[/json]', '')
        else:
            cleaned_message = message.get('content', '')
        
        if instructions is not None:
            instructions = instructions.replace('[user_intent]', cleaned_message)
            if json_data is not None:
                for variable in self.variables:
                    instructions = instructions.replace(f'[{variable}]', json_data.get(variable, ''))
            
        return [instructions, sensitive_data, extend_system_prompt]


