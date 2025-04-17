import asyncio
import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from classes.bot_helper import ensure_downloads_folder
from base_bot.llm_bot_base import LLMBotBase

from classes.bot_helper import format_output
load_dotenv()

import ctypes

def get_window_handle():
    user32 = ctypes.windll.user32
    handle = user32.GetForegroundWindow()
    return handle

class AbstractLLMBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.on('new_message', self.handle_new_message)
        # self.on('connected', self.handle_connected)
        # self.on('disconnected', self.handle_disconnected)
        # self.on('channelStatus', self.handle_channel_status)
        # self.on('error', self.handle_error)
   
    def handle_new_message(self, message):
        print(f"ABSTRACT LLM BOT handle_new_message: {message}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.handle_new_message_async(message))
        loop.close()
    
    async def handle_new_message_async(self, message):
        json_data = self.extract_json_data(message)
        
        if not json_data:
            self.send_message("Currently I am trained to help you automate a task. I cannot offer any other services.")
            return
        
        requested_action = json_data.get("action", None)
        if requested_action == "start_task":
            id = json_data.get("id", None)
            order_number = json_data.get("order_number", None)
            # extracted_data = json_data.get("data", None)
            # if not extracted_data:
                # self.send_message("V2 request that extracted_data be included in the request.")
                # return
            
            await ensure_downloads_folder(self, id, order_number)
            # self.send_message(f"@taxbot @propertybot New task assigned for order: {json_result.get('order_number', 'n/a')} [json]{json.dumps(json_result)}[/json]")
            self.send_message(f"@taxbot @propertybot New task assigned for order: {order_number} [json]{json.dumps(json_data)}[/json]")
            # result_text = 
        # if json_data:
        #     requested_action = json_data.get("action", None)
        
        # # validates acceptance, busy state and retrieves data
        # # [json_data, order_number, context, database_id] = self.validate_data(message)
        # [json_data, sensitive_data] = await self.extract_message_data(self, message)
        
        # for action in await self.actions_in_config():
        #     try:
        #         [instructions, extend_system_prompt] = await self.v2_prompt(action)
        #     except Exception as e:
        #         self.send_message(f"Action '{action['name']}' Error reading instructions. Check instruction file.")
                
        #     self.script_executor.set_session_data({
        #         'message': message,
        #         'json_data': json_data,
        #         'sensitive_data': sensitive_data if sensitive_data else None,
        #         'instructions': instructions,
        #         'extend_system_prompt': extend_system_prompt
        #     })
            
        #      # after loading prompt, we can execute the script
        #     scripts = action.get('prompt_scripts', [])
        #     if scripts:
        #         for script in scripts:
        #             [file_name, function_name] = script.split(':')
        #             await self.script_executor.execute(file_name.strip(), function_name.strip())
            
        #     # after executing the script, we can get the data
       
        # instructions = self.script_executor.SessionData.get('instructions', '')
        # extend_system_prompt = self.script_executor.SessionData.get('extend_system_prompt', '')
        # sensitive_data = self.script_executor.SessionData.get('sensitive_data', None)
        
        # # CUSTOMIZED FOR MAINboT, TO UPDATE LATER
        # # we will have to use message que and not manually triggere the for each data loop as it is anti-pattern here
        # # this bot should check queue and start hitting ONE data per execution. and repeat until data is cleared.
        # try:
        #     requested_action = None
        #     if json_data:
        #         requested_action = json_data.get("action", None)
                
        #     if requested_action == "start_local_pdf":
        #         await ensure_downloads_folder(self, database_id, order_number)
                            
        #         result_text = await format_output(self.script_executor, action, userInput_json)
        #         # userInput_json = self.add_more_params_for_task_bots(userInput_json, json_data=json_data)
                
        #         self.socket.emit('message', {
        #             "channelId": message.get("channelId", "general"),
        #             "content": result_text
        #         })
        #         finally:
        #             self.isBusy = False
        #             print("Processing complete, busy status reset to False")
    
        #     else :
        #         self.isBusy = False
        #         return f"""Hello {message.get("senderName", "Guest")}, I am currently trained to help you automate a task. I cannot offer any other services.
        #             To start a task, click on the "Start Task" button on the top right of the screen.
        #         """
        # except Exception as e:
        #     self.socket.emit('message', {
        #         "channelId": message.get("channelId"),
        #         "content": f"Action '{action['name']}' Error processing data. Message: {e}"
        #     })
        # # CUSTOMIZATION ENDS HERE
        
             
        # self.task_ended(database_id)
        # return "Action executor exited."
    
# bot = AbstractLLMBot(options={
#     "window_handle": get_window_handle(),
#     "bot_type": "task_bot",
#     "bot_id": "taxbot",
#     "bot_name": "TaxBot",
#     "autojoin_channel": "general",
#     "model": "gpt-4o-mini",
#     "prompts_directory": os.getenv("PROMPTS_DIR_PATH", "prompts"),
# })
 
# bot.start()

# bot.join()
# bot.cleanup()