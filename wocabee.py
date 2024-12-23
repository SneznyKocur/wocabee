import os
import json
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

class wocabee:
    def __init__(self, udaje: tuple):
        self.url = "https://wocabee.app/app"
        self.dict_path = "./dict.json"
        
        # Create dictionary file if it doesn't exist
        if not os.path.exists(self.dict_path):
            with open(self.dict_path, "w") as f:
                f.write("{}")
                
        self.word_dictionary = {}
        
        # Status indicators
        self.ok = "[+]"
        self.warn = "[!]" 
        self.err = "[-]"
        self.info = "[#]"
        self.debug = "[D]"

        # Exercise types
        self.PRACTICE = 0
        self.DOPACKAGE = 1 
        self.LEARN = 2
        self.LEARNALL = 3
        self.GETPACKAGE = 4

        self.udaje = udaje

        # Initialize headless Firefox driver with performance options
        options = Options()
        options.headless = True
        options.add_argument("--headless")
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", False)
        options.set_preference("browser.cache.offline.enable", False)
        options.set_preference("network.http.use-cache", False)
        
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(10)
        self.driver.implicitly_wait(1)  # Reduce implicit wait time
        
        self.driver.get(self.url)
        
        # Initialize thread pool for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=4)

    def init(self):
        """Initialize session by logging in and loading class data"""
        self.word_dictionary = self._dictionary_Load()
        self.class_names = []
        
        username, password = self.udaje
        print(f"{self.ok} Logging in... {username}")

        # Retry login up to 3 times (reduced from 5)
        attempts = 0
        logged_in = False
        while not logged_in and attempts < 3:
            try:
                self.login(username, password)
                if self.is_loggedIn():
                    logged_in = True
                else:
                    attempts += 1
            except:
                attempts += 1
                time.sleep(0.5)

        if not logged_in:
            print("Login failed")
            self.driver.quit()
            return

        # Get user name and class names in parallel
        self.name = self.get_elements_text(By.TAG_NAME, "b")[0]
        classes = self.get_classes()
        
        def get_class_name(class_item):
            id = list(class_item.keys())[0]
            return id, class_item[id].find_element(By.TAG_NAME, "span").text
            
        class_futures = [self.executor.submit(get_class_name, Class) for Class in classes]
        class_results = [f.result() for f in class_futures]
        self.class_names = [name for _, name in sorted(class_results)]
        
        print(f"Initialization complete. Classes: {self.class_names}")

    def quit(self):
        """Close browser and end session"""
        self.executor.shutdown()
        self.driver.quit()

    def elem_type(self, by, elem, x):
        """Type text into an element"""
        elem = self.get_element(by, elem)
        if elem:
            elem.clear()
            elem.send_keys(x)
    
    def login(self, username, password):
        """Log into Wocabee"""
        self.elem_type(By.ID, "login", username)
        self.elem_type(By.ID, "password", password)
        self.get_element(By.ID, "submitBtn").click()

    def is_loggedIn(self):
        """Check if logged in by looking for logout button"""
        try:
            return self.wait_for_element(1, By.ID, "logoutBtn")  # Reduced timeout
        except:
            return False    

    # Optimized element utilities
    def exists_element(self, root, by, element):
        """Check if element exists and is displayed"""
        try:
            return root.find_element(by, element).is_displayed()
        except:
            return False

    def get_element(self, by, element):
        """Get single element if it exists"""
        try:
            return self.driver.find_element(by, element) if self.exists_element(self.driver, by, element) else None
        except:
            return None

    def get_elements(self, by, element):
        """Get multiple elements if they exist"""
        try:
            return self.driver.find_elements(by, element) if self.exists_element(self.driver, by, element) else None
        except:
            return None

    def get_element_text(self, by, element):
        """Get text of single element"""
        elem = self.get_element(by, element)
        return elem.text if elem else 0

    def get_elements_text(self, by, element):
        """Get text of multiple elements"""
        elems = self.get_elements(by, element)
        return [x.text for x in elems] if elems else [0]

    def wait_for_element(self, timeout, by, element):
        """Wait for element to be displayed"""
        WebDriverWait(self.driver, timeout).until(
            lambda x: self.driver.find_element(by, element).is_displayed()
        )
        return self.get_element(by, element)

    # Optimized class management
    def get_classes(self) -> list:
        """Get list of available classes"""
        classes = self.wait_for_element(5, By.ID, "listOfClasses")
        return [{i: btn} for i, btn in enumerate(classes.find_elements(By.CLASS_NAME, "btn-wocagrey"))]

    def pick_class(self, class_id, classes):
        """Select a class to work with"""
        try:
            class_id = int(class_id)
            classes[class_id][class_id].click()
            self.wocaclass = class_id
        except Exception as e:
            print(f"Error selecting class: {e}")
        time.sleep(0.5)  # Reduced wait time

    # Optimized leaderboard
    def get_leaderboard(self):
        """Get class leaderboard data"""
        table_body = self.get_element(By.ID, "tbody")
        if not table_body:
            return []
            
        students = table_body.find_elements(By.CLASS_NAME, "wb-tr")
        
        def process_student(student):
            try:
                return {
                    "place": student.find_element(By.CLASS_NAME, "place").text,
                    "name": student.find_element(By.CLASS_NAME, "name").text,
                    "online": "status-online" in student.find_element(By.CLASS_NAME, "status-icon").get_attribute("class"),
                    "points": student.find_elements(By.TAG_NAME, "td")[2].text,
                    "packages": student.find_elements(By.TAG_NAME, "td")[3].text
                }
            except:
                return None
                
        # Process students in parallel
        futures = [self.executor.submit(process_student, student) for student in students]
        return [f.result() for f in futures if f.result()]

    # Optimized package management
    def get_packages(self, prac):
        """Get list of available packages based on practice type"""
        prac = int(prac)
        packages = []
        elements = self.get_elements(By.CLASS_NAME, "pTableRow")
        if not elements:
            return packages

        if prac == self.GETPACKAGE:
            def process_package(elem):
                try:
                    name = elem.find_element(By.CLASS_NAME, "package-name").text
                    playable = self.exists_element(elem, By.CLASS_NAME, "fa-play-circle")
                    return {name: playable}
                except:
                    return None
                    
            futures = [self.executor.submit(process_package, elem) for elem in elements]
            packages = [f.result() for f in futures if f.result()]

        elif prac == self.PRACTICE:
            elements = elements[:10]  # Only first 10 for practice
            for i, elem in enumerate(elements):
                if self.exists_element(elem, By.CLASS_NAME, "fa-gamepad"):
                    try:
                        button = elem.find_element(By.CLASS_NAME, "btn-primary")
                        packages.append({i: button})
                    except:
                        continue

        elif prac == self.DOPACKAGE:
            for i, elem in enumerate(elements):
                if self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                    try:
                        button = elem.find_element(By.CLASS_NAME, "package").find_element(By.TAG_NAME, "a")
                        packages.append({len(packages): button})
                    except:
                        continue

        elif prac in (self.LEARN, self.LEARNALL):
            for i, elem in enumerate(elements):
                if self.exists_element(elem, By.TAG_NAME, "a"):
                    try:
                        button = elem.find_element(By.TAG_NAME, "a")
                        packages.append({i: button})
                    except:
                        continue

        return packages

    def pick_package(self, package_id, packages):
        """Select a package to work with"""
        try:
            package_id = int(package_id)
            packages[package_id][package_id].click()
            self.package = package_id
        except Exception as e:
            print(f"Error selecting package: {e}")
        time.sleep(0.5)

    # Rest of the methods remain largely unchanged as they are already optimized
    # or require sequential execution due to website interaction requirements
    
    # Dictionary operations optimized with caching
    _dictionary_cache = {}
    
    def dictionary_get(self, word, *args, **kwargs):
        """Get translations for a word from dictionary with caching"""
        word = str(word)
        cache_key = f"{word}_{kwargs.get('Picture', False)}"
        
        if cache_key in self._dictionary_cache:
            return self._dictionary_cache[cache_key]
            
        if not self.word_dictionary:
            self.word_dictionary = self._dictionary_Load()
            
        if "Picture" in kwargs:
            dictionary = self.word_dictionary.get("Picture", {})
        else:
            dictionary = self.word_dictionary.get(self.class_names[int(self.wocaclass)], {})

        words = []
        translations = []
        
        if "," in word:
            words.extend(x.strip() for x in word.split(",") if len(x.strip()) > 2)
            words.append(word)
        else:
            words.append(word)

        for word in words:
            for dict_word, dict_translations in dictionary.items():
                if word == dict_word:
                    translations.extend(x for x in dict_translations if x not in translations)
                elif word in dict_translations:
                    if dict_word not in translations:
                        translations.append(dict_word)

        if translations and isinstance(translations[0], list):
            result = translations[0]
        else:
            result = translations
            
        self._dictionary_cache[cache_key] = result
        return result

    def dictionary_put(self, word, translation, *args, **kwargs):
        """Add word and translation to dictionary with cache invalidation"""
        if not word or not translation:
            return
            
        self.wocaclass = int(self.wocaclass)
        
        if "Picture" in kwargs:
            dict_key = "Picture"
        else:
            dict_key = self.class_names[self.wocaclass]
            
        if dict_key not in self.word_dictionary:
            self.word_dictionary[dict_key] = {}
            
        dictionary = self.word_dictionary[dict_key]
        word = str(word)
        translation = str(translation)

        if "," in translation:
            translations = []
            translations.extend(x.strip() for x in translation.split(","))
            translations.append(translation)
            value = translations
            key = word
        else:
            value = [translation]
            key = word

        if key not in dictionary:
            dictionary[key] = value
        else:
            dictionary[key].extend(x for x in value if x not in dictionary[key])

        # Invalidate cache for this word
        cache_key = f"{word}_{kwargs.get('Picture', False)}"
        if cache_key in self._dictionary_cache:
            del self._dictionary_cache[cache_key]

        self._dictionary_Save()

    def _dictionary_Load(self):
        """Load dictionary from file"""
        try:
            with open(self.dict_path, "r") as f:
                self.word_dictionary = json.load(f)
            return self.word_dictionary
        except:
            return {}

    def _dictionary_Save(self):
        """Save dictionary to file"""
        with open(self.dict_path, "w") as f:
            json.dump(self.word_dictionary, f, indent=2)
