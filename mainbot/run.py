import asyncio
import json
from dotenv import load_dotenv
from base_bot.llm_bot_base import LLMBotBase
# from langchain_openai import ChatOpenAI
from classes.api_service import ApiService
from classes.dynamic_script_executor import DynamicScriptExecutor
from classes.bot_helper import ensure_downloads_folder, extract_message_data, format_output
from classes.pdf_to_image import PdfToImage
from classes.utils import clean_json_string

import os

load_dotenv()

import ctypes

def get_window_handle():
    user32 = ctypes.windll.user32
    handle = user32.GetForegroundWindow()
    return handle

class MainBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.script_executor = DynamicScriptExecutor(self, os.path.join(os.getcwd(), 'scripts'))
        self.api_service = ApiService(self.config)
   
    def emit_start_message(self, message):
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": 'Message is received, processing... Allow me to finish the task first >>>'
        })
        
    def add_more_params_for_task_bots(self, final_json_data, json_data):
        final_json_data['x_county'] = final_json_data.get("s_data", {}).get('x_county', None)
        return final_json_data
        
    async def generate_response(self, message):
       
        self.emit_start_message(message)
       
        ## only customization here
        [json_data, sensitive_data] = await extract_message_data(self, message)
        
        for action in await self.actions_in_config():
            
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": f"Executing action {action.get('name', '')}... >>>"
            })
            
            try:
                [instructions, extend_system_prompt] = await self.v2_prompt(action)
            except Exception as e:
                self.socket.emit('message', {
                    "channelId": message.get("channelId"),
                    "content": f"Action '{action['name']}' Error reading instructions. Check instruction file."
                })
                continue
            
            self.script_executor.set_session_data({
                'message': message,
                'json_data': json_data,
                'sensitive_data': sensitive_data if sensitive_data else None,
                'instructions': instructions,
                'extend_system_prompt': extend_system_prompt
            })
            
            # after loading prompt, we can execute the script
            scripts = action.get('prompt_scripts', [])
            if scripts:
                for script in scripts:
                    [file_name, function_name] = script.split(':')
                    await self.script_executor.execute(file_name.strip(), function_name.strip())
                    
            # after executing the script, we can get the data
            instructions = self.script_executor.SessionData.get('instructions', '')
            extend_system_prompt = self.script_executor.SessionData.get('extend_system_prompt', '')
            sensitive_data = self.script_executor.SessionData.get('sensitive_data', None)
            
            # CUSTOMIZED FOR MAINboT, TO UPDATE LATER
            # we will have to use message que and not manually triggere the for each data loop as it is anti-pattern here
            # this bot should check queue and start hitting ONE data per execution. and repeat until data is cleared.
            try:
                requested_action = None
                if json_data:
                    requested_action = json_data.get("action", None)
                    
                if requested_action == "start_local_pdf":
                    self.isBusy = True
                    try:
                        data = json_data.get("data", [])
                        
                        for item in data:
                            userInput_json = None
                            pdf_path = item.get("pdf_path", None)
                            if pdf_path:
                                instructions = instructions.replace("[order_number]", PdfToImage.get_file_name_from_path(item.get("original_filename", "ai-do-not-fill")))
                                
                                text = PdfToImage.extract_text_from_pdf(pdf_path=pdf_path)
                                instructions = f"{instructions}. \n\n Text extracted from PDF: {text}"
                                # instructions = instructions.replace("[order_number]", PdfToImage.get_file_name_from_path(item.get("original_filename", "ai-do-not-fill")))
                                result = await self.call(instructions)
                                if action.get('output_formatting', 'text') == 'json':
                                    clean_parsed = clean_json_string(result)
                                    userInput_json = json.loads(clean_parsed)
                                    userInput_json['context'] = item
                                else:
                                    userInput_json = result
                                # here make sure directory is created
                                order_number = userInput_json.get('order_number', None)
                                if not order_number:
                                    raise Exception("Order number is not set")
                                
                                aido_order_id = item.get('id', None)
                                if not aido_order_id:
                                    raise Exception("AIDO Order id is not set")
                                
                                # we passed false here because we are going to make one DB call for update anyway after this.
                                file_download_folder = await ensure_downloads_folder(self, aido_order_id, order_number, update_database=False)
                                
                                # now that everything is prepared, we update the database
                                await self.api_service.update_aido_extracted_json(
                                    aido_order_id=aido_order_id, 
                                    extracted_json=userInput_json, 
                                    downloads_path=file_download_folder
                                )
                                
                                queues = os.getenv('FILEPREP_QUEUES', '').split(',')
                                for queue in queues:
                                    if queue and queue.strip():
                                        await self.api_service.create_new_task(aido_order_id, queue.strip())
                                        await asyncio.sleep(0.1)  # Sleep for 100ms
                                
                                result_text = await format_output(self.script_executor, action, userInput_json)
                              
                                self.socket.emit('message', {
                                    "channelId": message.get("channelId", "general"),
                                    "content": result_text
                                })
                                
                            else:
                                return "You seem to have not provided a valid pdf path"
                        
                        return "Request Processed"
                    finally:
                        self.isBusy = False
                        print("Processing complete, busy status reset to False")
        
                else :
                    self.isBusy = False
                    return f"""Hello {message.get("senderName", "Guest")}, I am currently trained to help you automate a task. I cannot offer any other services.
                        To start a task, click on the "Start Task" button on the top right of the screen.
                    """
            except Exception as e:
                self.socket.emit('message', {
                    "channelId": message.get("channelId"),
                    "content": f"Action '{action['name']}' Error processing data. Message: {e}"
                })
                continue
        # CUSTOMIZATION ENDS HERE

        return "Action executor exited."
    
bot = MainBot(options={
    "window_handle": get_window_handle(),
    "bot_type": "system",
    "bot_id": "fileprep",
    "bot_name": "FilePrep",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_directory": os.getenv("PROMPTS_DIR_PATH", "prompts"),
})
 
bot.start()

bot.join()
bot.cleanup()