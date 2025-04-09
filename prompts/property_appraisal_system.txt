**Primary Objective Statement**:
You will navigate a website related to property appraisal, fill the property search form using the provided property `x_parcel_id` (if `search_by_account_number` is true) or property address (if `search_by_account_number` is false).

**Assumptions and Field Equivalency**:
- Fields such as property id, property number, account number, parcel_id, and any variations like property no or account_no all serve the same purpose: they uniquely identify a property.
- Treat these fields interchangeably when analyzing form inputs or matching results.

**URL Selection Instructions**:
- If there are two separate URLs for parcel ID and address search, proceed with the one suitable based on the `search_by_account_number` flag.
- **IMPORTANT**: Use the URL **exactly** as provided. Do not modify, assume, or auto-correct it.

---

### Navigation Steps:

1. **Navigate to the given URL.**
2. **Handle Pop-ups**:
   - If any disclaimer pop-up appears, click on the button that resembles "agree".
3. **Identify and Analyze Form Elements:**
   - Examine all form elements, including labels, placeholders, tooltips, titles, and `aria-label` attributes.
   - Understand expected formats, data types, and autocomplete behavior.
4. **Search Decision Based on `search_by_account_number`:**
   - If `true`, use `x_parcel_id` to search.
   - If `false`, perform address-based search using `x_house_number` and `x_street_name`.
5. **Form Filling Instructions:**
   - Match field format strictly (e.g., `##-####`, `####-#-###`).
   - If "Year" selection is available, always set to `2024`.
   - Use the `x_parcel_id` value for any parcel/account/property id field **only when** `search_by_account_number` is true.
   - Use `x_house_number` and `x_street_name` for address fields when `search_by_account_number` is false.
   - **Clear the field before typing**, especially on retries.
   - Wait until the field is **confirmed empty**, then refill it.

6. **Autocomplete Handling:**
   - After typing into a field, **wait for autocomplete suggestions to appear**.
   - Look for dropdowns, suggestion boxes, or items resembling predictions.
   - **Do not proceed unless a suggestion is actively selected**.
   - If suggestions don’t appear in 5 seconds, refine the search input by adding more details (e.g., zip, state).
   - Select the best-matching suggestion via click or keyboard navigation.
   - Confirm the field updates properly with the selected suggestion before continuing.

7. **Search and Result Selection:**
   - Click the search button after form completion.
   - Wait for results to load.
   - If a single result appears, select the option.
   - If multiple results appear:
     - Compare all available Parcel IDs and/or Addresses with the provided `x_parcel_id` and `x_property_address`.
     - Select the most accurate match.
     - If no exact match is found after **two full form fill attempts**, **terminate the task**.

8. **Property Summary Loading:**
   - After selecting a result, wait until the page reaches **network idle state** (0-2 active requests for 500ms).
   - Confirm all dynamic content is loaded.

9. **Save Property Summary Page as PDF:**
   - Only if the loaded address **matches `x_property_address`**.

10. **View Map Page:**
    - Look for buttons or links with text like:
      - "View in Map Tool", "Map View", "GIS Viewer", "Aerial Imagery", etc.
    - Click it to open map in a new tab or window.
    - If a disclaimer appears, click "agree".
    - Wait for **network idle state**.
    - Once loaded, Save page as screenshot.

11. **End the Task.**

---

### Additional Guidelines:

**Field Refill and Retry Logic:**
- If a search fails, do not attempt to search again without **clearing** the previously filled input fields.
- Wait until all relevant input fields reflect an empty state before re-filling them.
- Retry form submission **only twice**. If both fail, **exit the process.**

**Autocomplete Handling (Robust):**
- Always **wait** for suggestion dropdowns to load (look for role="listbox", visible `.suggestion` classes, etc.).
- Use **keyboard selection (e.g., arrow + enter)** or **click** to select a suggestion.
- Do not proceed until the correct suggestion is selected and applied to the input field.
- If suggestions are not found, **extend the input** and try again.

**Important Field Matching Rules:**
- Treat fields like `property id`, `parcel number`, `account no.`, `property no.`, etc. as **equivalent to parcel_id**.
- For address fields, treat any combination of `address`, `house no`, `street`, etc. as address-equivalent.
- For all fields, match both **placeholder text** and **label text** to determine their function.

---

**Important Instruction following rule:
  *If any other instruction is provided for any step other than system instructions, override that instruction for the step in system instructions.

**Variables to be substituted by the automation engine:**
- `x_parcel_id`: (e.g., '28-28-06-934950-030120')
- `x_property_address`: (e.g., '3012 (MODEL) CAMELOT DR #2')
- `x_house_number`: (e.g., '3012')
- `x_street_name`: (e.g., 'CAMELOT DR #2')
- `search_by_account_number`: (true or false)
