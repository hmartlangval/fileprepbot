import json
from base_bot.llm_bot_base import LLMBotBase
from dotenv import load_dotenv
from classes.pdf_to_image import PdfToImage
from classes.utils import clean_json_string
from classes.api_service import ApiService

load_dotenv()

class MainBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.isBusy = False
        self.api_service = ApiService(self.config)
        
    async def register_task(self, message):
        import aiohttp

        async with aiohttp.ClientSession() as session:
            url = "https://ABC.com/register"
            async with session.post(url, json=message) as response:
                if response.status == 200:
                    response_data = await response.json()
                    print("Task registered successfully:", response_data)
                else:
                    print("Failed to register task. Status code:", response.status)
        
        
    async def process_tasks(self, task_id, tasks, message):
        
        await self.api_service.update_extracted_json(task_id, tasks)
        await self.api_service.create_pubsub_topics(task_id, tasks)
        
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@taxbot @propertybot start processing for [json]{json.dumps(tasks)}[/json] for order: {tasks.get('order_number', 'n/a')}",
            "taskId": tasks.get('context', {}).get('id', None)
        })
        print('All tasks initiated for ', tasks)
    
    async def generate_response(self, message):
        # await self.process_tasks("67ed6b7d1bc731e14544f672", {
        #     "order_number": "WTS-25-000016 Order",
        #     "s_data": {
        #         "x_county": "pasco",
        #         "x_property_address": "13127 Keel Court, Hudson, FL 34667",
        #         "x_account_number": "",
        #         "x_house_number": "13127",
        #         "x_street_name": "Keel Court",
        #         "x_city": "Hudson",
        #         "x_zip_code": "34667"
        #     },
        #     "context": {
        #         "pdf_path": "http://localhost:3000/api/data/1743612794545-WTS-25-000016 Order.pdf",
        #         "original_filename": "WTS-25-000016 Order.pdf",
        #         "file_type": "application/pdf",
        #         "id": "67ed6b7d1bc731e14544f672"
        #     }
        # }, message)    
        
        # return "DONE"
    
    
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
                        
                        # add more context into the task for the processor
                        userInput_json['context'] = item
                        
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
                            await self.process_tasks(item.get('id', None), userInput_json, message)
                        
                        # self.socket.emit('message', {
                        #     "channelId": message.get("channelId", "general"),
                        #     "content": f"extracted JSON is for [json]{json.dumps(userInput_json)}[/json]"
                        # })
                        
                    else:
                        return "You seem to have not provided a valid pdf path"
                
                return "Request Processed"
            finally:
                self.isBusy = False
                print("Processing complete, busy status reset to False")
        
        print(message)
        
        self.isBusy = False
        return f"""Hello {message.get("senderName", "Guest")}, I am currently trained to help you automate a task. I cannot offer any other services.
            To start a task, click on the "Start Task" button on the top right of the screen.
        """
    
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

