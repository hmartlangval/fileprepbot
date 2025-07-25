*Primary Objective Statement*:
You will access a county property tax website and search for property details using either an account number or an address (based on search_by_account_number). After identifying the correct property, export the details page as a PDF — only if the address is a perfect match. If no match is found after 2 total attempts, terminate immediately.


**Navigation Steps:
        1.  **Navigate to correct given URL.**
        2.  **Identify and Analyze Form Elements:**
            * Thoroughly examine all form elements, including labels, placeholders, instructions, tooltips, titles, and `aria-label` attributes.
            * Understand the expected input formats and data types for each field.
        3.  **Data Validation and Prioritization (using search_by_account_number):**
            * **Crucially:** Determine the search method based on the `search_by_account_number` flag.
            * **If `search_by_account_number` is true, prioritize searching by `x_account_number`. This is the preferred search method.**
            * **If `search_by_account_number` is false, proceed with address-based search.**
        4.  **Form Filling:**
            * Fill input fields *exactly* as specified by the website's form requirements Fill it just once as it is .
            * Maintain the required formatting (e.g., `##-####`, `####-#-###`).
            * For address searches, initially use only `x_house_number` and `x_street_name`.
            * If a "Year" selection field is available, set it to "2024" first.
            * **Autocomplete Fields:** If an input field uses autocomplete, wait for suggestions to appear after typing. Do not proceed until suggestions are loaded. If no relevant suggestions appear, add more filter criteria (e.g., state and zip code) until a match is found.
            * **Use the `x_account_number` value for the account number field when `search_by_account_number` is true.**
        5.  **Search and Result Selection:** (Dropdown or Tabular Based):
                    After *filling out the form* and clicking the search button (for form-based UIs), *OR* while *typing* (for autocomplete dropdown UIs), proceed with address and account number validation.
                    Search results may appear as:
                        -A table, list, or search result entries
                        -A dropdown suggestion box while typing address
                    **Pre-Click Validation (before selecting any result , Address must be exactly equal to 'x_property_address'):**
                        For each result entry (tabular-based or dropdown suggestion), compare the following components exactly with the provided fields:
                        Address components that must match exactly:
                                -House number = x_house_number
                                -Street name (including direction/suffixes) = x_street_name
                                -direction = x_direction (eg:E,NW,SW,S,NE...)
                                -City = x_city
                                -State = x_state
                                -ZIP code (if shown) = x_zip_code
                        **Only proceed to click/select if all the above fields match exactly(Address must be exactly equal to 'x_property_address').
                        **If no valid match is found:**
                            * Clear the input field completely or refresh the page.
                            * Re-enter the search criteria (account number or address) exactly as before.
                            **If no valid match is found even after the second attempt, terminate the task immediately.**
                            **Do not click any unmatched result.**
                    **Post-Click Validation (after selecting a result):(Address must be exactly equal to 'x_property_address')**
                        *Once the property details page is loaded, perform a strict and full re-verification of the displayed property address against x_property_address:*
                            -House number = x_house_number
                            -Street name (including direction/suffixes) = x_street_name
                            -direction = x_direction (eg:E,NW,SW,S,NE...)
                            -City = x_city
                            -State = x_state
                            -ZIP code (if shown) = x_zip_code
                        *If the on-page address matches **exactly** and completely, proceed to export the page to PDF.*
                        *If the address does not match exactly, do not export:*
                            Return to the search results.
                            Attempt a second (and final) valid selection (if the first one was incorrect).
                        After two total attempts, if no correct address is found or selected:
                            *Terminate the task immediately.*
                            Do *not* export any PDF.
                            Do *not* continue further.
        6.  **Save Page to PDF:(Only if Address is valid and address must be exactly equal to 'x_property_address')** 
            *Once the property details page is open and if the address matches perfectly then, Save the page as a PDF.  
             -If Page contains **2024 Annual  Bill** just click Print PDF link  **Once or maximum two times**

            **Note:** If the *address doesn't match ,Terminate the task immediately*
        7.  **End Task.**
        8.  **Error Handling and Retry Mechanism:**
                *If no results are found in the initial search and if incorrect result is been choosen :*
                    *Retry Search Attempt 2 times* :Clear the input field refresh the page first and then Retry the original search method .
                   
                **If both attempts fail:**
                        -Terminate the task immediately
                **If you are not able to find search box don't keep on looping try 2-3 times the terminate forcefully**


*Form Filling Guide (Detailed):*
* **Address Fields:** If address fields are separated (house number, street, city, etc.), fill each field individually.
* **Combined Address/Account Fields:** If a single field accepts both account number and addresses, use the `x_account_number` if `search_by_account_number` is true.
* **Autocomplete Handling:**
    * Wait patiently for autocomplete suggestions.
    * If no matching suggestions appear, refine the search by adding more information (e.g., state).
* **Fill input field with account number and addresses just once ,wait if no match found **clear the input field or refresh the input field remove the previous search data** and retry(only two attempts)**
* **Year Selection:** Always prioritize filling the "Year" field (if present) with "2024" to filter results.

*When to Search by account number vs. Address (Explicit Rules):*
* **Account Number Search:**
    * Use Account Number search *only* when the provided `search_by_account_number` flag is true and the input fields accepting account number exists.
* **Address Search:**
    * Use address search *only* when the provided `search_by_account_number` flag is false or account number input fields does not exists.
***Strict Termination Rules:***
    * Maximum of 2 total attempts (whether dropdown or tabular).
    * Always clear input field between attempts.
    * Do not proceed to export PDF unless the full property address is a confirmed exact match that is Address must be exactly equal to 'x_property_address'.
    * Do not loop or retry beyond 2 times — if no match, terminate the task immediately.
