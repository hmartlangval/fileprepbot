import os
import time
import openai
import threading
from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv
from base_bot import BaseBot

load_dotenv()  # reads .env

openai.api_key = os.environ.get("OPENAI_API_KEY")
SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:3000")
BOT_ID = os.environ.get("BOT_ID", "map_bot")
BOT_NAME = os.environ.get("BOT_NAME", "Map Bot")
DEFAULT_CHANNEL = os.environ.get("DEFAULT_CHANNEL", "general")

DOWNLOADS_PATH = "D:/PlayWright/BaseBot/downloads"

class MapBot(BaseBot):
    def should_respond_to(self, message):
        """Use LLM to determine if @map_bot should respond to the message."""
        if not (isinstance(message, dict) and "content" in message):
            return False

        message_text = message["content"]
        if not openai.api_key:
            return False  # no GPT if no key

        # 1) Prompt for GPT decision
        prompt = f"""
        You are an intelligent chatbot. Determine if this message is directed to @map_bot:
        Message: "{message_text}"
        Conditions to respond:
        - If @map_bot is mentioned
        - If the message contains a request related to maps, locations, or coordinates
        - If a URL and address are detected
        Respond with "yes" if @map_bot should respond, or "no" otherwise.
        """
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        decision = response.choices[0].message.content.strip().lower()
        return (decision == "yes")
    
    def generate_response(self, message):
        """
        1) Immediately return "I see you have tagged me..."
        2) Spin off a thread that will do the automation and
           emit additional messages back to the chat.
        """
        if not (isinstance(message, dict) and "content" in message):
            return "⚠️ I couldn't understand the request."

        content = message["content"]
        url, address = self.extract_details_from_message(content)

        # Start a thread to run the next steps.
        t = threading.Thread(
            target=self.on_after_response,
            args=(url, address),
            daemon=True
        )
        t.start()

        # Immediately return the first message
        return "I see you have tagged me! I'll start the process..."

    def on_after_response(self, url, address):
        """
        Runs in a background thread to:
        1) Wait so user sees "I see you have tagged me..."
        2) Post "Automation started..."
        3) Run the automation
        4) If address not found => "The address you sent is not available."
        If success => "Automation successful!"
        """
        time.sleep(8)  # Delay for UI message visibility

        if not url or not address:
            self.post_message("⚠️ Could not find 'url:' or 'address:' in your request.")
            return

        self.post_message(f"Automation started for URL: {url}, address: {address}")

        try:
            success = self.run_map_automation(url, address)
        except Exception as e:
            self.post_message(f"❌ Automation error: {e}")
            return

        if success:
            self.post_message("✅ Automation successful!")  # ✅ Post success message
        else:
            self.post_message(f"❌ The address you sent ('{address}') is not available.")  # ❌ Post failure message


    def post_message(self, text):
        """
        Actually EMIT a message event to the chat server.
        We assume 'self.socket' is a socket.io client, and
        self.state["current_channel_id"] has the channel to post to.
        """
        if not hasattr(self, "socket"):
            print("❌ No socket reference found! Cannot emit chat message.")
            return

        channel_id = self.state.get("current_channel_id", DEFAULT_CHANNEL)
        payload = {
            "channelId": channel_id,
            "content": text
        }
        self.socket.emit("message", payload)

    ###########################################################################
    # Helper Methods
    ###########################################################################
    def extract_details_from_message(self, message_text):
        """
        Finds 'url:' and 'address:' in the message, then slices out
        whatever follows. Returns (url, address) or (None, None).
        """
        lower_text = message_text.lower()
        url_label = "url:"
        address_label = "address:"

        url, address = None, None
        url_index = lower_text.find(url_label)
        addr_index = lower_text.find(address_label)

        # Extract URL
        if url_index != -1:
            start_url = url_index + len(url_label)
            if addr_index != -1 and addr_index > url_index:
                url = message_text[start_url:addr_index].strip()
            else:
                url = message_text[start_url:].strip()
            # Strip trailing commas/spaces
            url = url.rstrip(", ")

        # Extract address
        if addr_index != -1:
            start_addr = addr_index + len(address_label)
            address = message_text[start_addr:].strip()

        return url, address

    def validate_with_ai(self, url, address):
        """
        Optional: use GPT to confirm 'url' is from netronline.com 
        and 'address' is plausible. Return True/False.
        """
        if not openai.api_key:
            return True  # skip if no key

        prompt = f"""
        We have a map automation request:
        URL: {url}
        Address: {address}

        Check:
        1) Does the URL belong to netronline.com?
        2) Is the address plausible?

        Respond 'yes' or 'no'.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )
            decision = response.choices[0].message.content.strip().lower()
            return decision == "yes"
        except:
            return True  # fallback

    ###########################################################################
    # MAP AUTOMATION
    ###########################################################################
    def run_map_automation(self, url, address):
        """
        Launches Playwright to capture screenshots of the property map.
        Returns True if the address is found and processed, False otherwise.
        """
        print(f"🔄 Starting map automation for: {address}")

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=False)
                page = browser.new_page()
                page.set_default_navigation_timeout(90000)

                page.goto(url)
                found = self.capture_property_map(page, address)
                browser.close()

                if found:
                    print(f"✅ Automation completed for '{address}'.")
                    return True  # ✅ Ensure successful processing returns True
                else:
                    print(f"❌ Address '{address}' not found in the dropdown.")
                    return False  # ❌ Ensure failure returns False
        except Exception as e:
            print(f"❌ Automation error: {e}")
            return False  # Ensure an exception does not trigger false success


    def capture_property_map(self, page: Page, address):
        """
        Selects the best address from the dropdown using LLM and captures the property map.
        If no valid match is found, return False. Otherwise, return True.
        """
        print(f"📍 Capturing property map for: {address}")
        search_value = address.strip()
        search_box_selector = "#react-select-4-input"
        dropdown_selector = "#react-select-4-listbox"

        try:
            print("⌨️ Typing search address...")
            search_box = page.locator(search_box_selector)
            search_box.fill(search_value[:5])  # Type first few chars
            time.sleep(3)
            print("🔽 Adjusting map view...")
            page.evaluate("window.scrollBy(0, document.body.scrollHeight * 0.13)")
            time.sleep(3)

            print("🔍 Waiting for dropdown options...")
            page.wait_for_selector(dropdown_selector, timeout=10000)

            # Wait for any "Loading..." text to disappear
            loading_selector = f"{dropdown_selector} div:has-text('Loading...')"
            while page.query_selector(loading_selector):
                print("Waiting for dropdown data to load... rechecking every 3 seconds")
                time.sleep(3)

            print("Dropdown data loaded, waiting 1 second for UI to render...")
            time.sleep(1)

            # Use GPT-based selection, but if it returns False, we stop.
            selection_successful = self.select_best_match_with_llm(
                page, dropdown_selector, search_value
            )
            if not selection_successful:
                print("❌ Address selection failed (no valid match).")
                return False  # Return False ONLY if selection fails

            # If we made it here, we selected something
            print("Clicking submit button... waiting 1 second")
            time.sleep(1)

            submit_button_selector = 'button.bg-primary:has-text("Submit")'
            submit_button = page.locator(submit_button_selector)
            if submit_button.count() > 0:
                print("Clicking submit button...")
                submit_button.click()
                print("Submit button clicked")
                self.do_countdown(8, "Waiting for map to load...")

                print("🔽 Adjusting map view...")
                page.evaluate("window.scrollBy(0, document.body.scrollHeight * 0.13)")
                time.sleep(3)

                downloads_dir = self.ensure_downloads_dir()
                for i, suffix in enumerate(["initial", "zoomed", "zoomed_2"]):
                    screenshot_path = os.path.join(
                        downloads_dir, 
                        f"map_{address.replace(' ', '_')}_{suffix}.png"
                    )
                    page.screenshot(path=screenshot_path)
                    print(f"📸 Screenshot saved: {screenshot_path}")

                    # Zoom in for next screenshot
                    if i < 2:
                        self.find_element_and_click(page, 'a.leaflet-control-zoom-in')
                        time.sleep(2)

                return True  # ✅ Return True if everything succeeds
            else:
                print("❌ Submit button not found.")
                return False  # Return False if submit button is missing

        except Exception as e:
            print(f"❌ Error during map capture: {e}")
            self.post_message(f"❌ Error during map capture: {e}")
            return False  # Return False on any exception



    def ensure_downloads_dir(self):
        """
        Ensures a single directory 'downloads/maps' exists for screenshots.
        """
        downloads_dir = os.path.join(DOWNLOADS_PATH, "maps")
        os.makedirs(downloads_dir, exist_ok=True)
        return downloads_dir

    def find_element_and_click(self, page, element_selector):
        element = page.query_selector(element_selector)
        if element:
            element.click()
        else:
            print(f"❌ Element not found: {element_selector}")

    def do_countdown(self, count, message="Waiting for "):
        print(message, end="", flush=True)
        for i in range(count, 0, -1):
            print(f"\r{message} {i} seconds remaining", end="", flush=True)
            time.sleep(1)
        print("\rCountdown complete!")

    ###########################################################################
    # LLM-based dropdown matching
    ###########################################################################
    def select_best_match_with_llm(self, page, dropdown_selector, address):
        """
        Uses GPT to find the best matching address from the dropdown options.
        If GPT can't find a match, return False. Otherwise, click the selected option.
        """
        try:
            options = []
            option_elements = []

            # Collect dropdown options
            for i in range(20):  # Assuming max 10 options
                option_selector = f'#react-select-4-option-{i}'
                option_element = page.query_selector(option_selector)
                if option_element:
                    option_text = option_element.text_content().strip()
                    options.append(option_text)
                    option_elements.append((option_selector, option_text))
                else:
                    break

            if not options:
                
                return False

            # Use GPT to find the best match
            best_match_index = self.get_best_match_from_llm(options, address)

            # Ensure a valid selection before clicking
            if 0 <= best_match_index < len(option_elements):
                best_selector, best_text = option_elements[best_match_index]
                print(f"✅ GPT selected: {best_text}")
                page.click(best_selector)
                time.sleep(2)
                return True  # Mark success to avoid incorrect "not found" message
            else:
                print("❌ No valid match found for the given address.")
                
                return False
        except Exception as e:
            print(f"❌ Error selecting best match: {e}")
            self.post_message(f"❌ Error selecting best match: {e}")
            return False



    def get_best_match_from_llm(self, options, address):
        """Uses GPT-4o to determine the best matching address from the dropdown options."""
        if not openai.api_key:
            print("❌ OpenAI API key not set. Using first option as fallback.")
            return 0  # Fallback if no API key

        try:
            prompt = f"""
            We are selecting the best matching address from a dropdown.
            The user is searching for: "{address}"

            Available options:
            {chr(10).join([f"{i}. {option}" for i, option in enumerate(options)])}

            Provide ONLY the index number (0-based) of the best match.
            If no suitable match is found, respond with -1.
            """

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )

            result = response.choices[0].message.content.strip()

            # Convert response to integer
            best_index = int(result) if result.isdigit() or result == "-1" else -1

            return best_index
        except Exception as e:
            
            return -1  # Indicate failure to find a match



# -------------------------------------
# Example usage (if you were to test):
# -------------------------------------
if __name__ == "__main__":
    bot = MapBot()
    bot.should_respond_to = MapBot.should_respond_to.__get__(bot, BaseBot)
    bot.generate_response = MapBot.generate_response.__get__(bot, BaseBot)

    # In your real setup, the framework might call bot.generate_response(message).
    # This just prevents the script from exiting if your BaseBot has a background thread:
    bot.input_thread.join()
