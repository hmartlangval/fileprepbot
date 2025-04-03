import json
from base_bot.llm_bot_base import LLMBotBase
from dotenv import load_dotenv
from classes.pdf_to_image import PdfToImage
from classes.utils import clean_json_string

load_dotenv()

class MainBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.isBusy = False
        
    async def process_tasks(self, message, tasks):
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@taxbot start processing for [json]{json.dumps(tasks)}[/json]"
        })
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@propertybot start processing for [json]{json.dumps(tasks)}[/json]"
        })
        print('All tasks initiated for ', tasks)
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"All Tasks initiated for order: {tasks.get('order_number', 'n/a')}"
        })
    
    async def generate_response(self, message):
        if(self.isBusy):
            return "I am currently busy. Please wait for me to finish the task."
        
        def emit_start_message(message):
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": 'Message is received, processing... Allow me to finish the task first >>>'
            })
          
        json_data = super().extract_json_data(message)
        
        action = None
        if json_data:
            action = json_data.get("action", None)
          
        if action == "start_local_pdf":
            emit_start_message(message)
            self.isBusy = True
            try:
                data = json_data.get("data", [])
                
                for item in data:
                    userInput_json = None
                    pdf_path = item.get("pdf_path", None)
                    if pdf_path:
                        instructions = await self.quick_load_prompts("prompts/pdf_text_extraction.txt")
                        instructions = instructions.replace("[order_number]", PdfToImage.get_file_name_from_path(item.get("original_filename", "ai-do-not-fill")))
                        
                        text = PdfToImage.extract_text_from_pdf(pdf_path=pdf_path)
                        instructions = f"{instructions}. \n\n Text extracted from PDF: {text}"
                        # instructions = instructions.replace("[order_number]", PdfToImage.get_file_name_from_path(item.get("original_filename", "ai-do-not-fill")))
                        result = await self.call(instructions)
                        clean_parsed = clean_json_string(result)
                        userInput_json = json.loads(clean_parsed)
                        userInput = "PDF has been analyzed from URL {}. Result: [json]{}[/json]".format(pdf_path, clean_parsed)
                        
                        # if pdf_path.startswith("http"):
                        #     # extracted_data = PdfToImage.pdf_page_to_base64_from_url(pdf_path)
                        #     # result = await self.analyze_image(instructions, encoded_image_base64=extracted_data)
                        #     text = PdfToImage.extract_text_from_pdf(pdf_path=pdf_path)
                        #     instructions = f"{instructions}. \n\n Text extracted from PDF: {text}"
                        #     # instructions = instructions.replace("[order_number]", PdfToImage.get_file_name_from_path(item.get("original_filename", "ai-do-not-fill")))
                        #     result = await self.call(instructions)
                        #     clean_parsed = result.replace("```json", "").replace("```", "")
                        #     userInput_json = json.loads(clean_parsed)
                        #     userInput = "PDF has been analyzed from URL {}. Result: [json]{}[/json]".format(pdf_path, clean_parsed)
                        # else:
                        #     extracted_data = PdfToImage.pdf_page_to_base64_from_path(pdf_path)
                        #     result = await self.analyze_image(instructions, encoded_image_base64=extracted_data)
                        #     clean_parsed = result.replace("```json", "").replace("```", "")
                        #     userInput_json = json.loads(clean_parsed)
                        #     userInput = "PDF has been analyzed from local path {}. Result: [json]{}[/json]".format(pdf_path, clean_parsed)
                    
                        if userInput_json:
                            await self.process_tasks(message, userInput_json)
                        
                        self.socket.emit('message', {
                            "channelId": message.get("channelId", "general"),
                            "content": f"extracted JSON is for [json]{json.dumps(userInput_json)}[/json]"
                        })
                        
                    else:
                        return "You seem to have not provided a valid pdf path"
                
                return "Request Processed"
            finally:
                self.isBusy = False
                print("Processing complete, busy status reset to False")
        
        elif action == "start_task":
            data = json_data.get("data", {})
            
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": f"Request Accepted. Starting Tasks for the following [json] {json.dumps(data)} [/json]"
            })
            
            await self.process_tasks(message, data)
            
            return f"Tasks started!!"
     
        
        print(message)
        
        self.isBusy = False
        return f"""Hello {message.get("senderName", "Guest")}, I am currently trained to help you automate a task. I cannot offer any other services.
            To start a task, click on the "Start Task" button on the top right of the screen.
        """

        # elif action is not None:
        #     return "I am instructed to perform task i am not trained on. Task: " + json_data.get("action", "unknown")
        
        # return "I am a simple FilePrep Service Bot"
    
    
bot = MainBot(options={
    "bot_id": "fileprep",
    "bot_name": "Fileprep Service",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    # "prompts_path": "prompts/datacollection.txt",
})

bot.start()

bot.join()

bot.cleanup()

