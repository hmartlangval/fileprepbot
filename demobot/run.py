import json
import os
from dotenv import load_dotenv
import AbstractBot
from langchain_openai import ChatOpenAI
from classes.bot_helper import format_output
from classes.dynamic_script_executor import DynamicScriptExecutor
load_dotenv()

import ctypes

def get_window_handle():
    user32 = ctypes.windll.user32
    handle = user32.GetForegroundWindow()
    return handle

class DemoBot(AbstractBot.BrowserClientBaseBot):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.script_executor = DynamicScriptExecutor(self, os.path.join(os.getcwd(), 'scripts'))
   
    async def generate_response(self, message):
       
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": 'Message is received, processing... >>>'
        })
       
        ## only customization here
        json_data = super().extract_json_data(message)
       
        for action in await self.actions_in_config():
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": f"Processing action {action.get('name', '')}... >>>"
            })
            
            [instructions, extend_system_prompt] = await self.v2_prompt(action)
            
            if not instructions:
                self.socket.emit('message', {
                    "channelId": message.get("channelId"),
                    "content": f"Action '{action['name']}' has No instructions provided."
                })
                continue
            
            self.script_executor.set_session_data({
                'message': message,
                'json_data': json_data,
                # 'sensitive_data': sensitive_data,
                'instructions': instructions,
                'extend_system_prompt': extend_system_prompt
            })
            
            # after loading prompt, we can execute the script
            for script in action.get('prompt_scripts', []):
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
                            
                
                print(f"instructions:       {instructions}")
                print(f"sensitive_data:          {sensitive_data}")
                print(f"extend_system_prompt:  {extend_system_prompt}")
                
                if action.get('requires_browser', False):
                    result  = await self.call_agent(instructions, extend_system_message=extend_system_prompt, sensitive_data=sensitive_data,
                                                    session_config={
                                                        "original_json": json_data
                                                    })
                    [is_success, final_summary] = self.check_success_or_failure(result)
                    if is_success:
                        result_text = await format_output(self.script_executor, action, final_summary)
                    else:
                        result_text = f"Action '{action['name']}' has failed. Message: {final_summary}"
                else:
                    combined_instructions = f"""
                    {extend_system_prompt}
                    
                    {instructions}
                    """
                    result = await self.call(combined_instructions)
                    result_text = await format_output(self.script_executor, action, result)
                
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": result_text
            })

        return "Action executor exited."
    
    # async def analyse_summary(self, summary):

    #     prompt = f""" You are provided with summary of task that has been completed.
    #     Please analyse the summary :
    #     {summary}       
    #     **If pdf was downloaded or not, if any errors occurred or not.
    #     **Also give the download path where the files were downloaded.
    #     ** provide the result in short format using max 20 words.
    #     ** If the summary is not provided then return "No summary provided"
    #     """

    #     llm = ChatOpenAI(model="gpt-4-turbo")
    #     result = llm.invoke(prompt)
    #     return result.content
    
bot = DemoBot(options={
    "window_handle": get_window_handle(),
    "bot_type": "task_bot",
    "bot_id": "demobot",
    "bot_name": "Demo Bot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_directory": os.getenv("PROMPTS_DIR_PATH", "prompts"),
    # "prompts_directory": "prompts",
    # "prompts_path": "./prompts/taxbot/tax_steps.txt",
    # "system_prompt_path": "./prompts/tax_system.txt"
})
 
bot.start()

bot.join()
bot.cleanup()