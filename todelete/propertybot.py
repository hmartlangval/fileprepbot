from dotenv import load_dotenv
 
import AbstractBot
from langchain_openai import ChatOpenAI
 
load_dotenv()
import ctypes
 
def get_window_handle():
    user32 = ctypes.windll.user32
    handle = user32.GetForegroundWindow()
    return handle
 
class PropertyBot(AbstractBot.FilePreparationParentBot):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
   
    async def generate_response(self, message):
       
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": 'Message is received, processing... >>>'
        })
               
        json_data = super().extract_json_data(message)
 
        ## do validation if it should proceed or not based on json data ONLY IF REQUIRED
        if json_data.get('x_county') == 'nelvin':
            return "I reject because i cannot serve nelvin county"
       
        [instructions, sensitive_data, extend_system_prompt] = await super().prepare_LLM_data(json_data, message)
              
        
        instructions_result = self.analyze_instructions(instructions)
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": instructions_result
        })
        
        result  = await self.call_agent(instructions, extend_system_message=extend_system_prompt, sensitive_data=sensitive_data)
        summary = self.analyse_summary(result)

        summary = f"I am property bot. summary of downloading task: {summary}"

        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": summary
        })
       
        [is_success, final_summary] = self.check_success_or_failure(result)
        if is_success:
            return f"I am Property Bot. Tasks has been completed. {final_summary}"
        else:
            return f"I am Property Bot. Tasks has failed. Message: {final_summary}"
    
    def analyse_summary(self, summary):
        prompt = f""" You are provided with summary of task that has been completed.
        Please analyse the summary :
        {summary}
        ** if pdf was downloaded or not and if image screeshot was downloaded or not.
        ** Also give the download path where the files were downloaded.
        ** provide the result in short format using max 20 words.
        ** If the summary is not provided then return "No summary provided"
        """
        llm = ChatOpenAI(model="gpt-4-turbo")
        result = llm.invoke(prompt)
        return result.content
    
    def analyze_instructions(self, instructions):
        prompt = f""" You are provided with instructions for a task.
        Please check the instructions :
        {instructions} .
        **If the instruction is none then return "No instructions provided",
        **If the instruction is present then return "Able to load Instructions, proceeding with task.
        Strictly return only one of the above two options, don't any analysis or explanation"""

        llm = ChatOpenAI(model="gpt-4-turbo")
        result = llm.invoke(prompt)
        return result.content
   
    def analyze_instructions(self, instructions):
        prompt = f""" You are provided with instructions for a task.
        Please check the instructions :
        {instructions} .
        **If the instruction is none then return "No instructions provided",
        **If the instruction is present then return "Able to load Instructions, proceeding with task.
        Strictly return only one of the above two options, don't any analysis or explanation"""
 
        llm = ChatOpenAI(model="gpt-4-turbo")
        result = llm.invoke(prompt)
        return result.content
   
bot = PropertyBot(options={
    "window_handle": get_window_handle(),
    "bot_type": "task_bot",
    "bot_id": "propertybot",
    "bot_name": "PropertyBot",
    "bot_type":"task_bot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "./prompts/property_appraisal_steps.txt",
    "system_prompt_path": "./prompts/property_appraisal_system.txt"
})
 
 
bot.start()
 
bot.join()
 
bot.cleanup()
 
 
 