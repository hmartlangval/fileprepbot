from dotenv import load_dotenv

import AbstractBot
from langchain_openai import ChatOpenAI

load_dotenv()

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
        return f"I am Property Bot. Taks has been completed, and the summary is {summary}"
    
    def analyse_summary(self, summary):
        prompt = f""" You are provided with summary of task that has been completed.
        Please analyse the summary :
        {summary}
        **Analyze the summary for if automation was successful or not, if pdf was downloaded or not, if any errors occurred or not, and if image screeshot was downloaded or not.
        and provide the result in short format using max 20 words."""
        llm = ChatOpenAI(model="gpt-4-turbo")
        result = llm.invoke(prompt)
        return result.content
    
    def analyze_instructions(self, instructions):
        prompt = f""" You are provided with instructions for a task.
        Please check the instructions :
        {instructions}
        if the instruction is none then return "No instructions provided"
        if the instruction is not none then return "Able to load Instructions, proceeding with task"""

        llm = ChatOpenAI(model="gpt-4-turbo")
        result = llm.invoke(prompt)
        return result.content
    
bot = PropertyBot(options={
    "bot_type": "task_bot",
    "bot_id": "propertybot",
    "bot_name": "PropertyBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "./prompts/property_appraisal_steps.txt",
    "system_prompt_path": "./prompts/property_appraisal_system.txt",
    # "downloads_path": r"D:\ThoughtfocusRD\Phase_2_navigators_deo\Base_bot\fileprepbot\downloads"
})


bot.start()

bot.join()

bot.cleanup()

