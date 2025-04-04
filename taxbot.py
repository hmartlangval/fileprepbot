from dotenv import load_dotenv
import AbstractBot
import ctypes
import asyncio

load_dotenv()

def get_window_handle():
    user32 = ctypes.windll.user32
    handle = user32.GetForegroundWindow()
    return handle

class TaxBot(AbstractBot.FilePreparationParentBot):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

    async def generate_response(self, message):
        try:
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": 'Message is received, processing... >>>'
            })

            # ✅ Safely extract JSON
            json_data = super().extract_json_data(message)
            if not json_data:
                raise ValueError("No JSON data extracted from message.")

            # Optional validation
            if json_data.get('x_county') == 'nelvin':
                return "I reject because I cannot serve nelvin county"

            # ✅ Prepare LLM data
            [instructions, sensitive_data, extend_system_prompt] = await super().prepare_LLM_data(json_data, message)

            print(f"instructions: {instructions}")
            print(f"sensitive_data: {sensitive_data}")
            print(f"extend_system_prompt: {extend_system_prompt}")

            # ✅ Call LLM
            result = await self.call_agent(instructions, extend_system_message=extend_system_prompt, sensitive_data=sensitive_data)

            # ✅ Summarize response                                                             
            summary = await self.analyse_summary(result)
            # ✅ Notify MainBot of completion
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": "@fileprep task_complete from taxbot"
            })

            return f"I am Tax Bot. Tasks have been completed. {summary}"

        except Exception as e:
            error_msg = f"❌ TaxBot.generate_response error: {str(e)}"
            print(error_msg)

            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": error_msg
            })

            return error_msg

    async def analyse_summary(self, summary):
        prompt = f"""You are provided with summary of a task that has been completed.
    Please analyze the summary:
    {summary}

    And provide the result in short format using max 20 words."""

        result = await self.call(prompt)
        return result  # ⬅️ no `.content` here



# ✅ Initialize and run the bot
bot = TaxBot(options={
    "window_handle": get_window_handle(),
    "bot_type": "task_bot",
    "restart_command": "^c^cpython taxbot.py",
    "bot_id": "taxbot",
    "bot_name": "TaxBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "./prompts/tax_steps.txt",
    "system_prompt_path": "./prompts/tax_system.txt",
    "downloads_path": r"D:/browser_use_bot/fileprepbot/downloads"
})

bot.start()
bot.join()
bot.cleanup()
