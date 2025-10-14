"""
Faculty Evaluation Automation Bot for MIST Student Portal
=========================================================
This script automates the faculty evaluation process by:
1. Logging into the student portal
2. Navigating to faculty evaluation page
3. Filling out evaluations with "Very Good" ratings
4. Submitting default comments
5. Moving to next faculty automatically

Requirements:
- pip install selenium python-dotenv
- Chrome browser installed
- ChromeDriver (managed automatically by selenium 4.6+)
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class FacultyEvaluationBot:
    """Automated bot for completing MIST faculty evaluations."""
    
    def __init__(self, headless=False):
        """
        Initialize the bot with Chrome WebDriver.
        
        Args:
            headless (bool): Run browser in headless mode (no UI)
        """
        self.student_id = os.getenv('STUDENT_ID')
        self.password = os.getenv('PASSWORD')
        
        # Validate credentials
        if not self.student_id or not self.password:
            raise ValueError("STUDENT_ID and PASSWORD must be set in .env file")
        
        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        
        # URLs
        self.login_url = "https://student.mist.ac.bd/login"
        self.evaluation_url = "https://student.mist.ac.bd/semester-evaluation/faculty-evaluation"
        
        # Default comments
        self.overall_comment = "Very good teaching experience. The course was well-structured and engaging."
        self.recommendation = "Continue maintaining this quality. Keep up the excellent work."
    
    def login(self):
        """Log into the student portal."""
        print("🔐 Logging into student portal...")
        self.driver.get(self.login_url)
        
        try:
            # Wait for page to load completely
            time.sleep(3)
            
            # Try multiple selectors for student ID field
            student_id_field = None
            selectors_to_try = [
                (By.NAME, "email"),  # Material-UI uses email field for student ID
                (By.ID, "mui-1"),
                (By.ID, "student_id"),  # Fallback to original
                (By.XPATH, "//input[@name='email']"),
                (By.XPATH, "//input[@type='text']"),
            ]
            
            for selector_type, selector_value in selectors_to_try:
                try:
                    student_id_field = self.wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    print(f"✅ Found student ID field using: {selector_type}='{selector_value}'")
                    break
                except TimeoutException:
                    continue
            
            if not student_id_field:
                raise Exception("Could not locate student ID field with any selector")
            
            # Fill student ID field
            student_id_field.clear()
            student_id_field.send_keys(self.student_id)
            print(f"✅ Entered student ID: {self.student_id}")
            
            # Try multiple selectors for password field
            password_field = None
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "mui-2"),
                (By.ID, "password"),
                (By.XPATH, "//input[@type='password']"),
            ]
            
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = self.driver.find_element(selector_type, selector_value)
                    print(f"✅ Found password field using: {selector_type}='{selector_value}'")
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Could not locate password field")
            
            # Fill password field
            password_field.clear()
            password_field.send_keys(self.password)
            print("✅ Entered password")
            
            # Wait a moment before clicking login
            time.sleep(1)
            
            # Try multiple selectors for login button
            login_button = None
            button_selectors = [
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
            ]
            
            for selector_type, selector_value in button_selectors:
                try:
                    login_button = self.driver.find_element(selector_type, selector_value)
                    print(f"✅ Found login button using: {selector_type}='{selector_value}'")
                    break
                except:
                    continue
            
            if not login_button:
                raise Exception("Could not locate login button")
            
            # Click login button
            print("🔄 Clicking login button...")
            login_button.click()
            
            # Wait for URL change or check for error messages
            try:
                # Wait for successful login (URL should change)
                self.wait.until(EC.url_changes(self.login_url))
                print("✅ Successfully logged in!")
                print(f"🔗 New URL: {self.driver.current_url}")
                time.sleep(2)  # Brief pause after login
                
            except TimeoutException:
                # Check if we're still on login page and look for error messages
                current_url = self.driver.current_url
                if "login" in current_url:
                    # Look for error messages
                    error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'invalid') or contains(text(), 'error') or contains(text(), 'token')]")
                    if error_elements:
                        error_text = error_elements[0].text
                        print(f"❌ Login error: {error_text}")
                        # Take screenshot for debugging
                        self.driver.save_screenshot("login_error.png")
                        print("📸 Login error screenshot saved as 'login_error.png'")
                    raise Exception(f"Login failed - still on login page. Current URL: {current_url}")
                else:
                    print("✅ Login appears successful (URL changed)")
            
        except TimeoutException:
            print("❌ Login failed: Timeout waiting for elements")
            self.driver.save_screenshot("login_timeout_error.png")
            print("📸 Timeout error screenshot saved")
            raise
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            raise
    
    def navigate_to_evaluations(self):
        """Navigate to the faculty evaluation page."""
        print("📍 Navigating to faculty evaluation page...")
        self.driver.get(self.evaluation_url)
        time.sleep(1)  # Reduced wait time
        print("✅ Reached evaluation page")
    
    def get_faculty_cards(self):
        """
        Get all faculty evaluation cards that still need evaluation.
        
        Returns:
            list: List of faculty evaluation button elements that need evaluation
        """
        try:
            # Wait for faculty cards to load
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button"))
            )
            
            # Find all faculty cards with "Evaluate" buttons (unevaluated)
            evaluate_buttons = self.driver.find_elements(
                By.XPATH, 
                "//button[contains(text(), 'Evaluate') and not(contains(text(), 'Evaluated'))]"
            )
            
            # Filter out disabled buttons
            active_buttons = [btn for btn in evaluate_buttons if btn.is_enabled() and btn.is_displayed()]
            
            print(f"📋 Found {len(active_buttons)} faculty with active 'Evaluate' buttons")
            
            # Debug: also check for other button states
            all_buttons = self.driver.find_elements(By.XPATH, "//button")
            button_texts = [btn.text for btn in all_buttons if btn.text.strip()]
            unique_texts = list(set(button_texts))
            print(f"🔍 All button texts found: {unique_texts[:10]}")  # Show first 10
            
            return active_buttons
            
        except TimeoutException:
            print("⚠️ No faculty cards found")
            return []
        except Exception as e:
            print(f"⚠️ Error getting faculty cards: {str(e)}")
            return []
    
    def fill_evaluation_form_direct(self):
        """
        Fill out the evaluation form directly (assumes we're already on the form page).
        """
        try:
            # Wait for the form to load with reduced timeout
            print("   ⏳ Waiting for evaluation form to load...")
            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "semesterEvaluation_answer_item__G6tGB"))
            )
            print("   ✓ Form loaded")
            
            # Short wait to ensure all elements are rendered
            time.sleep(1)
            
            # Find all "Very Good" answer options using the correct class
            very_good_options = self.driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'semesterEvaluation_answer_item__G6tGB')]//div[text()='Very Good']"
            )
            
            print(f"   📊 Found {len(very_good_options)} 'Very Good' options")
            
            if len(very_good_options) == 0:
                print("   ⚠️ No 'Very Good' options found, trying alternative selector...")
                # Alternative selector
                very_good_options = self.driver.find_elements(
                    By.XPATH, 
                    "//div[contains(text(), 'Very Good')]"
                )
                print(f"   📊 Found {len(very_good_options)} options with alternative selector")
            
            # Click each "Very Good" option
            questions_answered = 0
            for i, option in enumerate(very_good_options):
                try:
                    # Multiple click strategies for better success rate
                    success = False
                    click_strategies = [
                        ("JavaScript click", lambda elem: self.driver.execute_script("arguments[0].click();", elem)),
                        ("Scroll and click", lambda elem: (
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem),
                            time.sleep(0.2),
                            elem.click()
                        )),
                        ("Actions click", lambda elem: (
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", elem),
                            time.sleep(0.1),
                            self.driver.execute_script("arguments[0].click();", elem)
                        )),
                        ("Parent click", lambda elem: (
                            elem.find_element(By.XPATH, "./parent::div").click()
                        ))
                    ]
                    
                    for strategy_name, click_func in click_strategies:
                        try:
                            click_func(option)
                            questions_answered += 1
                            print(f"   ✓ Answered question {questions_answered}: Very Good ({strategy_name})")
                            success = True
                            break
                        except Exception as e:
                            continue
                    
                    if not success:
                        print(f"   ⚠️ Could not click option {i+1} with any strategy")
                    
                    # Brief pause between clicks
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"   ⚠️ Could not process option {i+1}: {str(e)[:50]}...")
                    continue
            
            print(f"   ✅ Successfully answered {questions_answered} evaluation questions")
            
            # Wait a moment for the form to update
            time.sleep(2)
            
            # Check if we answered enough questions (should be 10)
            if questions_answered < 10:
                print(f"   ⚠️ Only answered {questions_answered}/10 questions - form may not submit")
                
                # Try alternative approach - click by position or different selector
                print("   🔄 Trying alternative approach for remaining questions...")
                
                # Try clicking answer items by their container
                answer_containers = self.driver.find_elements(
                    By.XPATH, 
                    "//div[contains(@class, 'semesterEvaluation_answer_item__G6tGB')][.//div[text()='Very Good']]"
                )
                
                remaining_attempts = 10 - questions_answered
                for i, container in enumerate(answer_containers[:remaining_attempts]):
                    try:
                        self.driver.execute_script("arguments[0].click();", container)
                        questions_answered += 1
                        print(f"   ✓ Answered question {questions_answered}: Very Good (container click)")
                        time.sleep(0.3)
                    except:
                        continue
                
                print(f"   📊 Final count: {questions_answered}/10 questions answered")
            
            # Check if submit button is now enabled
            submit_buttons = self.driver.find_elements(
                By.XPATH, 
                "//button[contains(text(), 'Submit') and not(contains(@class, 'Mui-disabled'))]"
            )
            
            if submit_buttons:
                print("   ✅ Submit button is now enabled")
            else:
                print("   ⚠️ Submit button is still disabled - checking why...")
                
                # Check for any required fields or validation messages
                required_fields = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'required') or contains(text(), 'Required')]")
                if required_fields:
                    print(f"   ℹ️ Found {len(required_fields)} required field indicators")
                
                # Save debug HTML to check what happened
                try:
                    with open("form_after_filling_debug.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print("   📄 Saved debug HTML after filling")
                except:
                    pass
            
        except Exception as e:
            print(f"   ❌ Error filling evaluation form: {str(e)}")
    
    def fill_evaluation_form(self, faculty_index):
        """
        Fill out the evaluation form for a specific faculty.
        
        Args:
            faculty_index (int): Index of the faculty member (0-based)
        """
        try:
            # Get all evaluate buttons again (to avoid stale element references)
            evaluate_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Evaluate')]")
            
            if faculty_index >= len(evaluate_buttons):
                print(f"   ⚠️ Faculty index {faculty_index} out of range")
                return
            
            # Click the evaluate button for this faculty
            evaluate_button = evaluate_buttons[faculty_index]
            
            # Get faculty name from the button's parent container
            try:
                faculty_container = evaluate_button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'faculty_item')]")
                faculty_name_element = faculty_container.find_element(By.XPATH, ".//div[contains(@class, 'muiltr-kw6mk3')]")
                faculty_name = faculty_name_element.text
                print(f"   👤 Evaluating: {faculty_name}")
            except:
                print(f"   👤 Evaluating faculty #{faculty_index + 1}")
            
            # Scroll to button and click using ActionChains for better reliability
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", evaluate_button)
            time.sleep(1)
            
            # Try multiple click methods
            try:
                # Method 1: Regular click
                evaluate_button.click()
                print(f"   🔘 Clicked evaluate button (regular click)")
            except:
                try:
                    # Method 2: JavaScript click
                    self.driver.execute_script("arguments[0].click();", evaluate_button)
                    print(f"   🔘 Clicked evaluate button (JavaScript click)")
                except:
                    # Method 3: ActionChains click
                    actions.move_to_element(evaluate_button).click().perform()
                    print(f"   🔘 Clicked evaluate button (ActionChains click)")
            
            # Wait for loading screen to appear and then disappear
            print("   ⏳ Waiting for page to load...")
            
            # First, wait for the loading screen (UNIPLEX text)
            try:
                loading_screen = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "waviy"))
                )
                print("   📄 Loading screen appeared")
                
                # Then wait for loading screen to disappear and actual content to load
                WebDriverWait(self.driver, 30).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "waviy"))
                )
                print("   ✅ Loading screen disappeared, content should be ready")
                
            except TimeoutException:
                print("   ℹ️ No loading screen detected or already loaded")
            
            # Wait additional time for form to render
            time.sleep(3)
            
            # Look for evaluation form elements (these are clickable divs, not radio buttons!)
            print("   🔍 Looking for evaluation form elements...")
            
            # Wait for evaluation form to be present
            try:
                # Wait for the evaluation questions to appear
                WebDriverWait(self.driver, 10).until(
                    lambda driver: len(driver.find_elements(By.CLASS_NAME, "semesterEvaluation_answer_item__G6tGB")) > 0
                )
                print("   ✅ Evaluation form questions detected")
            except TimeoutException:
                print("   ⚠️ No evaluation questions found after waiting")
            
            # Find all "Very Good" options (these are clickable divs, not radio buttons)
            very_good_options = self.driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'semesterEvaluation_answer_item__G6tGB')]//div[text()='Very Good']/.."
            )
            
            print(f"   ✓ Found {len(very_good_options)} 'Very Good' options")
            
            if not very_good_options:
                print("   ⚠️ No 'Very Good' options found")
                # Try alternative selectors
                all_options = self.driver.find_elements(By.CLASS_NAME, "semesterEvaluation_answer_item__G6tGB")
                print(f"   ℹ️ Found {len(all_options)} total answer options")
                
                if not all_options:
                    # Save page source for debugging
                    with open(f"evaluation_form_debug_{faculty_index}.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print(f"   💾 Page source saved for debugging: evaluation_form_debug_{faculty_index}.html")
                    
                    # Take screenshot for debugging
                    self.driver.save_screenshot(f"evaluation_form_debug_{faculty_index}.png")
                    print(f"   📸 Screenshot saved: evaluation_form_debug_{faculty_index}.png")
                    return
                else:
                    # Use the first option (Very Good) from each question
                    print("   🔄 Trying to select first option from each question...")
                    very_good_options = []
                    questions = set()
                    for option in all_options:
                        try:
                            # Get the question number to avoid duplicates
                            question_elem = option.find_element(By.XPATH, "./ancestor::div[contains(@class, 'muiltr-1qm1lh')]//div[contains(@class, 'semesterEvaluation_question_number__34CKe')]")
                            question_num = question_elem.text.strip()
                            
                            if question_num not in questions:
                                option_text = option.text.strip()
                                if "Very Good" in option_text:
                                    very_good_options.append(option)
                                    questions.add(question_num)
                                    print(f"     ✓ Found Very Good option for {question_num}")
                        except:
                            continue
            
            # Click all "Very Good" options
            selected_count = 0
            for i, option in enumerate(very_good_options):
                try:
                    # Scroll into view and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                    time.sleep(0.5)
                    
                    # Click the option
                    option.click()
                    selected_count += 1
                    print(f"   ✓ Selected 'Very Good' for question {i+1}")
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"   ⚠️ Could not select question {i+1}: {str(e)}")
                    try:
                        # Try JavaScript click
                        self.driver.execute_script("arguments[0].click();", option)
                        selected_count += 1
                        print(f"   ✓ Selected 'Very Good' for question {i+1} (JavaScript click)")
                    except Exception as e2:
                        print(f"   ❌ Failed both click methods for question {i+1}: {str(e2)}")
            
            print(f"   ✅ Successfully selected {selected_count} 'Very Good' ratings")
            
            if selected_count > 0:
                time.sleep(2)  # Wait for form to update
                
                # Check if submit button is now enabled
                submit_buttons = self.driver.find_elements(
                    By.XPATH, 
                    "//button[contains(text(), 'Submit') and not(@disabled)]"
                )
                
                if submit_buttons:
                    print(f"   🎉 Submit button is now enabled!")
                else:
                    print(f"   ⚠️ Submit button is still disabled, may need more selections")
            else:
                print("   ❌ No options were successfully selected")
                return
            
        except Exception as e:
            print(f"   ⚠️ Error filling evaluation form: {str(e)}")
            # Take screenshot for debugging
            self.driver.save_screenshot(f"evaluation_error_faculty_{faculty_index}.png")
    
    def submit_evaluation(self):
        """Submit the evaluation with comments - optimized for speed."""
        try:
            # Quick dialog cleanup
            try:
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(0.3)
            except:
                pass
            
            # Find and click submit button
            submit_buttons = self.driver.find_elements(
                By.XPATH, 
                "//button[contains(text(), 'Submit') or contains(text(), 'SUBMIT')]"
            )
            
            if submit_buttons:
                submit_buttons[0].click()
                print("   📝 Clicked submit button...")
                
                # Fast modal detection and filling
                try:
                    # Quick wait for modal
                    wait = WebDriverWait(self.driver, 8)
                    
                    # Check for loading and wait briefly if needed
                    loading_elements = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Loading...')]")
                    if loading_elements and loading_elements[0].is_displayed():
                        print("   ⏳ Brief loading...")
                        try:
                            wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Loading...')]")))
                        except:
                            pass
                    
                    # Wait for textarea fields to appear (main indicator of modal)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                    print("   📝 Comment modal appeared!")
                    
                    # Save debug HTML
                    try:
                        with open("comment_modal_debug.html", "w", encoding="utf-8") as f:
                            f.write(self.driver.page_source)
                        print("   📄 Saved debug HTML")
                    except:
                        pass
                    
                    # Get all textareas - fast approach with specific targeting
                    try:
                        # Wait for modal to be fully loaded
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.NAME, "comments"))
                        )
                        print("   📝 Modal form fully loaded")
                    except:
                        print("   ⚠️ Modal form not fully loaded, continuing anyway...")
                    
                    # Fill "Overall Comments" field first (required)
                    comments_filled = False
                    try:
                        comments_field = self.driver.find_element(By.NAME, "comments")
                        comments_field.clear()
                        comments_field.send_keys("Good teaching methodology and helpful guidance throughout the course.")
                        print("   ✓ Filled comments field")
                        comments_filled = True
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"   ⚠️ Comments field error: {str(e)}")
                    
                    # Fill "Recommendations" field (required)  
                    recommendations_filled = False
                    try:
                        recommendations_field = self.driver.find_element(By.NAME, "recommendations")
                        recommendations_field.clear()
                        recommendations_field.send_keys("Continue the excellent work and keep inspiring students with innovative teaching methods.")
                        print("   ✓ Filled recommendations field")
                        recommendations_filled = True
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"   ⚠️ Recommendations field error: {str(e)}")
                    
                    # Fallback: try to fill any empty textareas
                    if not comments_filled or not recommendations_filled:
                        print("   🔄 Trying fallback approach for empty fields...")
                        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                        for i, textarea in enumerate(textareas):
                            try:
                                if textarea.get_attribute("value") == "":  # Empty field
                                    if i == 0 and not comments_filled:
                                        textarea.clear()
                                        textarea.send_keys("Good teaching methodology and helpful guidance.")
                                        print(f"   ✓ Filled comments via fallback")
                                        comments_filled = True
                                    elif i == 1 and not recommendations_filled:
                                        textarea.clear()
                                        textarea.send_keys("Continue the excellent work and keep inspiring students.")
                                        print(f"   ✓ Filled recommendations via fallback")
                                        recommendations_filled = True
                            except:
                                continue
                    
                    fields_filled = sum([comments_filled, recommendations_filled])
                    print(f"   📊 Successfully filled {fields_filled}/2 required fields")
                    
                    time.sleep(1)
                    
                    # Wait for submit button to be enabled (both fields must be filled)
                    print("   ⏳ Waiting for submit button to be enabled...")
                    try:
                        submit_enabled = WebDriverWait(self.driver, 8).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and not(contains(@class, 'Mui-disabled'))]"))
                        )
                        print("   ✅ Submit button is now enabled!")
                    except TimeoutException:
                        print("   ⚠️ Submit button still disabled, trying anyway...")
                    
                    # Fast submit button detection and click
                    submit_clicked = False
                    submit_selectors = [
                        "//button[@type='submit']",
                        "//button[contains(@class, 'MuiLoadingButton-root')]",
                        "//button[contains(text(), 'Submit')]",
                        "//button[@form='evaluate_form']"
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            submit_btns = self.driver.find_elements(By.XPATH, selector)
                            for submit_btn in submit_btns:
                                if submit_btn.is_displayed():
                                    # Try JavaScript click for better success rate
                                    self.driver.execute_script("arguments[0].click();", submit_btn)
                                    print(f"   ✅ Clicked final submit button!")
                                    submit_clicked = True
                                    break
                            if submit_clicked:
                                break
                        except Exception as e:
                            print(f"   ⚠️ Submit attempt failed: {str(e)[:50]}...")
                            continue
                    
                    if not submit_clicked:
                        # Fallback: click any visible enabled button
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            try:
                                if btn.is_displayed() and btn.is_enabled():
                                    btn.click()
                                    print("   ✓ Clicked fallback button")
                                    break
                            except:
                                continue
                    
                    time.sleep(1.5)
                    
                except TimeoutException:
                    print("   ⚠️ Modal timeout - may not have appeared")
                    # Save debug info
                    try:
                        with open("submit_timeout_debug.html", "w", encoding="utf-8") as f:
                            f.write(self.driver.page_source)
                    except:
                        pass
                
            else:
                print("   ⚠️ No submit button found")
                
        except Exception as e:
            print(f"   ❌ Submit error: {str(e)}")
    
    def process_all_evaluations(self):
        """Process all faculty evaluations on the page."""
        print("\n🎓 Starting faculty evaluations...\n")
        
        completed_evaluations = 0
        max_attempts = 15  # Reduced max attempts
        attempt = 0
        consecutive_failures = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Get current faculty evaluation buttons
            faculty_buttons = self.get_faculty_cards()
            
            if not faculty_buttons:
                print("✅ No more faculty evaluation cards found - all completed!")
                break
            
            current_faculty_count = len(faculty_buttons)
            print(f"📊 Found {current_faculty_count} remaining faculty members to evaluate")
            
            # Always process the first available faculty
            try:
                print(f"�‍🏫 Processing Faculty (Attempt {attempt})")
                
                # Click the first faculty button directly
                faculty_buttons[0].click()
                print(f"   ✓ Clicked on faculty evaluation")
                time.sleep(0.5)  # Reduced wait time
                
                # Fill and submit evaluation  
                self.fill_evaluation_form_direct()
                self.submit_evaluation()
                
                completed_evaluations += 1
                print(f"   ✅ Completed evaluation {completed_evaluations}")
                
                # Return to faculty list
                self.navigate_to_evaluations()
                time.sleep(0.5)  # Reduced wait time
                
            except Exception as e:
                print(f"   ❌ Error processing faculty: {str(e)}")
                # Try to return to evaluations page on error
                try:
                    self.navigate_to_evaluations()
                    time.sleep(1)
                except:
                    print("   ⚠️ Could not return to evaluations page")
                continue
                
        print(f"\n🎉 Completed {completed_evaluations} faculty evaluations!")
    
    def check_for_access_issues(self):
        """Check for access token or authentication issues."""
        try:
            # Look for common error messages
            error_indicators = [
                "invalid access token",
                "access denied",
                "session expired",
                "unauthorized",
                "authentication failed"
            ]
            
            page_text = self.driver.page_source.lower()
            for indicator in error_indicators:
                if indicator in page_text:
                    print(f"⚠️ Detected authentication issue: {indicator}")
                    return True
            
            # Check for redirect to login page
            current_url = self.driver.current_url
            if "login" in current_url and "evaluation" not in current_url:
                print("⚠️ Redirected back to login page - session may have expired")
                return True
                
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking for access issues: {e}")
            return False

    def run(self):
        """Main execution method."""
        try:
            # Step 1: Login
            self.login()
            
            # Check for access issues after login
            if self.check_for_access_issues():
                print("❌ Authentication issues detected. Please check your credentials or try again later.")
                self.driver.save_screenshot("auth_error.png")
                print("📸 Authentication error screenshot saved as 'auth_error.png'")
                return
            
            # Step 2: Navigate to evaluations
            self.navigate_to_evaluations()
            
            # Check again after navigation
            if self.check_for_access_issues():
                print("❌ Access issues detected when accessing evaluation page.")
                self.driver.save_screenshot("evaluation_access_error.png")
                print("📸 Evaluation access error screenshot saved")
                return
            
            # Step 3: Process all evaluations
            self.process_all_evaluations()
            
            print("\n✨ Bot execution completed!")
            
        except Exception as e:
            print(f"\n❌ Error during execution: {str(e)}")
            # Take screenshot on error for debugging
            self.driver.save_screenshot("error_screenshot.png")
            print("📸 Error screenshot saved as 'error_screenshot.png'")
            
            # Print current page info for debugging
            try:
                print(f"🔗 Current URL: {self.driver.current_url}")
                print(f"📄 Page title: {self.driver.title}")
            except:
                pass
                
            raise
        
        finally:
            # Keep browser open for 10 seconds to see results
            print("\n⏳ Keeping browser open for 10 seconds to inspect results...")
            time.sleep(10)
            self.driver.quit()


def main():
    """Main entry point for the script."""
    print("=" * 60)
    print("MIST Faculty Evaluation Automation Bot")
    print("=" * 60)
    print()
    
    # Create .env file example if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file template...")
        with open('.env', 'w') as f:
            f.write("STUDENT_ID=your_student_id_here\n")
            f.write("PASSWORD=your_password_here\n")
        print("⚠️ Please edit .env file with your credentials and run again.")
        return
    
    # Ask user about headless mode
    headless_input = input("Run in headless mode? (y/n, default: n): ").strip().lower()
    headless = headless_input == 'y'
    
    # Initialize and run bot
    bot = FacultyEvaluationBot(headless=headless)
    bot.run()


if __name__ == "__main__":
    main()