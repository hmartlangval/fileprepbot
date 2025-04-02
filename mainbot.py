import json
import asyncio
from base_bot.llm_bot_base import LLMBotBase
from dotenv import load_dotenv
from classes.pdf_to_image import PdfToImage
from classes.utils import clean_json_string

load_dotenv()

class MainBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.isBusy = False
        self.propertybot_done_event = asyncio.Event()

        # Register event handler
        self.socket.on('message', lambda msg: asyncio.create_task(self.on_socket_message(msg)))

    async def on_socket_message(self, msg):
        content = msg.get("content", "")
        if "@fileprep task_complete from propertybot" in content.lower():
            print("✅ Received completion signal from propertybot.")
            self.propertybot_done_event.set()

    async def wait_for_propertybot(self, tasks, message):
        self.propertybot_done_event.clear()

        # Start propertybot
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@propertybot start processing for [json]{json.dumps(tasks)}[/json]"
        })
        print("📤 propertybot started... waiting for completion signal or timeout")

        try:
            await asyncio.wait_for(self.propertybot_done_event.wait(), timeout=120)  # Wait max 2 min
            print("✅ propertybot completed (signal received).")
        except asyncio.TimeoutError:
            print("⚠️ Timeout waiting for propertybot. Proceeding to taxbot anyway.")

    async def process_tasks(self, message, tasks):
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"🔁 Starting sequential bot tasks for order: {tasks.get('order_number', 'n/a')}"
        })

        # 1️⃣ Wait for propertybot to finish (or timeout)
        await self.wait_for_propertybot(tasks, message)

        # 2️⃣ Always start taxbot afterward
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@taxbot start processing for [json]{json.dumps(tasks)}[/json]"
        })
        print("📤 taxbot started")

    async def generate_response(self, message):
        if self.isBusy:
            return "⚠️ I am currently busy. Please wait for me to finish the task."

        def emit_start_message(msg):
            self.socket.emit('message', {
                "channelId": msg.get("channelId"),
                "content": "✅ Message received. Starting task..."
            })

        json_data = super().extract_json_data(message)
        action = json_data.get("action") if json_data else None

        if action == "start_local_pdf":
            emit_start_message(message)
            self.isBusy = True
            try:
                data = json_data.get("data", [])
                for item in data:
                    pdf_path = item.get("pdf_path")
                    if not pdf_path:
                        return "❌ No valid PDF path provided."

                    instructions = await self.quick_load_prompts("prompts/pdf_text_extraction.txt")
                    instructions = instructions.replace("[order_number]", PdfToImage.get_file_name_from_path(item.get("original_filename", "ai-do-not-fill")))
                    text = PdfToImage.extract_text_from_pdf(pdf_path=pdf_path)
                    instructions += f"\n\n Text extracted from PDF: {text}"

                    result = await self.call(instructions)
                    clean_parsed = clean_json_string(result)
                    parsed_json = json.loads(clean_parsed)

                    if parsed_json:
                        await self.process_tasks(message, parsed_json)

                    self.socket.emit('message', {
                        "channelId": message.get("channelId", "general"),
                        "content": f"✅ Extracted JSON: [json]{json.dumps(parsed_json)}[/json]"
                    })

                return "✅ PDF Task Processed"
            finally:
                self.isBusy = False
                print("✅ Finished, busy flag cleared.")

        elif action == "start_task":
            data = json_data.get("data", {})
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": f"📝 Request Accepted. Starting tasks for: [json]{json.dumps(data)}[/json]"
            })

            await self.process_tasks(message, data)

            return "✅ Task processing started!"

        self.isBusy = False
        return 

# Launch the bot
bot = MainBot(options={
    "bot_id": "fileprep",
    "bot_name": "Fileprep Service",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
})

bot.start()
bot.join()
bot.cleanup()
