from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from getpass import getpass, getuser
import time
import json
import os

from tqdm import tqdm
# TODO: progress bar in package
class wocabot:
    def __init__(self,username,password):
        self.word_dictionary = {}
        self.dictionary_path = "dict.json"
        self.ok = "[+]"
        self.warn = "[!]"
        self.err = "[-]"
        self.info = "[#]"
        self.debug = "[D]"

        print(f"{self.ok} Loading dictionary from file")

        
        self._dictionary_Load()
        #print(f"{self.debug} {self.word_dictionary=}")

        self.username = username
        self.password = password
        
        self.url = "https://wocabee.app/app"

        self.driver = webdriver.Firefox()
        self.driver.get(self.url)

        print(f"{self.ok} Trying to login...")

        self.Woca_login(username, password)
        if self.is_loggedIn():
            print(f"{self.ok} Succesfully logged in...")

            classes = self.get_classes()
            for id,Class in enumerate(classes):
                # class is dict of id:button
                print(id, Class[id].find_element(By.TAG_NAME,"span").text)
                
            classid = input("ID:")
            self.wocaclass = str(classid)
            self.pick_class(classid, classes)
            time.sleep(1)

            prac = int(input("0: practice, 1: do package 2: learn words 3: Learn ALL words 4: quickclick :"))

            if prac < 3:
                packages = self.get_packages(prac)

                if len(packages) > 1:
                    for id,package in enumerate(packages):
                        print(id,self.driver.find_elements(By.CLASS_NAME,"pTableRow")[id].find_element(By.CLASS_NAME,"package-name").text)

                    self.package = self.pick_package(input("ID:"),packages)
                    if int(prac) == 0:
                        self.practice()
                    if int(prac) == 2:
                        self.learn() 
                else:
                    self.package = self.pick_package(0, packages)

                    if int(prac) == 0:
                        self.practice()
                    if int(prac) == 2:
                        self.learn()
                    if int(prac) == 3:
                        self.learnALL()

                if int(prac) == 1:
                    self.do_package()

            elif prac == 3:
                # learn all
                self.learnALL()

            elif prac == 4:
                # quickclick
                self.driver.find_element(By.CLASS_NAME,"btn-info").click()
                self.driver.find_element(By.ID,"oneAnswerGameStartBtn").click()
                self.quickclick()
            else:
                print(f"{self.err} Invalid Option")
        else:
            print(f"{self.err} Failed to log in.")
        self.driver.quit()

    def pkgID_to_name(self,pkgID:int):
        return self.driver.find_elements(By.CLASS_NAME,"pTableRow")[pkgID].find_element(By.CLASS_NAME,"package-name").text

    def elem_type(self,by,element,x):
        elem = self.driver.find_element(by,element)
        elem.clear()
        elem.send_keys(x)

    def Woca_login(self,username: str, password:str) -> int:
        # username
        self.elem_type(By.ID,"login",username)
        # password
        self.elem_type(By.ID,"password",password)
        # click login button
        elem = self.driver.find_element(By.ID,"submitBtn")
        elem.click()
    def exists_element(self,root,by,element):
        try:
            elem = root.find_element(by,element)
            return elem.is_displayed()
        except:
            # maybe not loaded yet?
            time.sleep(1)
            try:
                return root.find_element(by,element).is_displayed()
            except:
                return False
    def is_loggedIn(self):
        return self.exists_element(self.driver,By.ID,"logoutBtn")


    def fail_practice(self):
        WebDriverWait(self.driver, 10).until(lambda x: self.driver.find_element(By.ID, "tfw_word").is_displayed())
        self.elem_type(By.ID, "translateFallingWordAnswer", "omg")
        self.driver.find_element(By.ID,"translateFallingWordSubmitBtn").click()
        self.driver.find_element(By.ID,"incorrect-next-button").click()

    def calculate_words(self,diff_wocapoints):
        target_points = diff_wocapoints
        target_bonus = 5
        target_word_count = 0
        total = 0
        current_bonus = 0
        for i in range(diff_wocapoints):
            if i >= target_bonus:
                current_bonus += target_bonus
                target_bonus *= 2        

            total = i*2 + current_bonus
            #print(f"{self.debug} {i=} {current_bonus=} {total=} {target_points=} {target_word_count=}")
            if total < target_points:
                target_word_count+=1
            else:
                break
        return target_word_count-1

    def get_element(self,by, element):
        try:
            elem = self.driver.find_element(by,element)
        except:
            elem = 0
        if elem and elem != "":
            return elem
        else:
            return 0

    def get_element_text(self,by, element):
        try:
            elem = self.driver.find_element(by,element).text
        except:
            elem = 0
        if elem and elem != "":
            return elem
        else:
            return 0
    def get_classes(self):
        classeslist = []
        classes = self.driver.find_element(By.ID,"listOfClasses")
        i = 0
        for button in classes.find_elements(By.TAG_NAME,"button"):
            classeslist.append({i:button})
            i+=1
        return classeslist

    def pick_class(self,class_id,classes):
        class_id = int(class_id)
        classes[class_id][class_id].click()

    def get_packages(self, prac):
        i = 0
        prac = int(prac)
        if prac == 3: # learn all = learn
            prac = 2 
        packageslist = []
        for elem in self.driver.find_elements(By.CLASS_NAME,"pTableRow"):
            # check if package is still playable
            if prac == 1:
                if self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                    button = elem.find_element(By.CLASS_NAME,"package ").find_element(By.TAG_NAME,"a")
                    #print(button)
                    packageslist.append({i:button})
                    i+=1
            elif prac == 0:
                if self.exists_element(elem, By.CLASS_NAME, "fa-gamepad"):
                    button = elem.find_element(By.CLASS_NAME,"btn-primary")
                    packageslist.append({i:button})
                    i+=1
            elif prac == 2:
                if self.exists_element(elem, By.TAG_NAME, "a"):
                    button = elem.find_element(By.TAG_NAME, "a")
                    packageslist.append({i:button})
                    i+=1
        return packageslist
            #print(f'{elem.find_element(By.CLASS_NAME,"package-name").text}: {self.exists_element(elem, By.CLASS_NAME, "fa-play-circle")}')
    def pick_package(self,package_id,packages):
        #print(f"{self.debug} {package_id=} {packages=}")
        package_id = int(package_id)
        packages[package_id][package_id].click()
        return package_id
    def practice(self):

        save = True

        wocapoints = int(self.driver.find_element(By.ID,"WocaPoints").text)
        target_wocapoints = input("target wocapoints: ")

        if target_wocapoints.startswith("+"):
            target_wocapoints = wocapoints + int(target_wocapoints.replace("+", ""))
        else:
            target_wocapoints = int(target_wocapoints)


        difference = target_wocapoints - wocapoints
        
        print(f"{self.info} Doing {difference} wocapoints ({wocapoints} -> {target_wocapoints})")

        # switch to 2 wocapoint level
        levelToggle = self.driver.find_element(By.ID,"levelToggle")
        ActionChains(self.driver).move_to_element(levelToggle).click(levelToggle).perform()

        for i in tqdm(range(int(self.calculate_words(difference)))):
            pre_wocapoints = wocapoints # save 
            wocapoints = self.get_element_text(By.ID, "WocaPoints")
            if not wocapoints:
                wocapoints = pre_wocapoints
            else:
                wocapoints = int(wocapoints)
            
            if target_wocapoints - wocapoints == 1:
                ActionChains(self.driver).move_to_element(levelToggle).click(levelToggle).perform()


            # TODO: when in 1st level there may not be a falling word so this wont work    
            WebDriverWait(self.driver, 10).until(lambda x: self.driver.find_element(By.ID, "tfw_word").is_displayed())
            self.do_exercise()


        difference = target_wocapoints - wocapoints
        self.fail_practice()

        for i in tqdm(range(int(self.calculate_words(difference-2)))):
            pre_wocapoints = wocapoints # save 
            wocapoints = self.get_element_text(By.ID, "WocaPoints")
            if not wocapoints:
                wocapoints = pre_wocapoints
            else:
                wocapoints = int(wocapoints)
            
            if target_wocapoints - wocapoints == 1:
                ActionChains(self.driver).move_to_element(levelToggle).click(levelToggle).perform()
                self.do_exercise()
            else:
                WebDriverWait(self.driver, 10).until(lambda x: self.driver.find_element(By.ID, "tfw_word").is_displayed())
                self.do_exercise()
        
        
        if save:
            self.driver.find_element(By.ID,"backBtn").click()

    def learnALL(self):
        packagelist = self.get_packages(2)
        for i in tqdm(range(len(packagelist))):
            WebDriverWait(self.driver, 10,ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)).until(
                            lambda x: self.driver.find_element(By.CLASS_NAME, "pTableRow").is_displayed()) # wait until we can pick a package
            time.sleep(1)
            packagelist = self.get_packages(2)
            package = packagelist[i]
            package_ID = list(package.keys())[0]
            # package is dict of {id: button}
            self.package = package_ID
            self.pick_package(list(package.keys())[0], packagelist)
            self.learn(False)

    def learn(self,echo = False):
        while self.exists_element(self.driver, By.ID, "intro"):
            WebDriverWait(self.driver,10).until(lambda x: self.driver.find_element(By.ID,"word").is_displayed())
            word = self.driver.find_element(By.ID,"word").text
            translation = self.driver.find_element(By.ID,"translation").text
            self.dictionary_put(word, translation,self.package,echo)

            try: 
                self.driver.find_element(By.ID,"rightArrow").click()
            except:
                word = self.driver.find_element(By.ID,"word").text
                translation = self.driver.find_element(By.ID,"translation").text
                self.dictionary_put(word, translation,self.package,echo)
                # return to menu
                self.driver.find_element(By.ID,"backBtn").click()
                return



    def quickclick(self): # ja neviem čo toto je to som mal asi 20 promile
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        while self.exists_element(self.driver, By.ID, "oneAnswerGameSecondsLeft"):
            WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(
                            lambda x: self.driver.find_element(By.ID, "oneOutOfManyQuestionWord").is_displayed())
            word = self.driver.find_element(By.ID,"oneOutOfManyQuestionWord")
            translations = self.driver.find_elements(By.CLASS_NAME,"oneOutOfManyWord")
            preklad = self.dictionary_get(word.text)
            print(f"{preklad=} {word.text=}")
            if preklad:
                for translation in translations:
                    if preklad == translation.text:
                        translation.click()
            
            # what,
            else:
                print(f"{self.err} Word not in dictionary")
                if self.dictionary_get(translations[0].text):
                    translations[1].click()
                else:
                    translations[0].click()
                if self.exists_element(self.driver, By.ID, "incorrect-next-button"):
                    self.driver.find_element(By.ID,"incorrect-next-button").click()
    def find_missing_letters(self,missing,word):
        end = ""
        for i,x in enumerate(missing):
            if x == "_":
                end+=word[i]
        return end

    def do_exercise(self):
        # TODO: pictures


        # listening skip
        if self.exists_element(self.driver, By.ID, "transcribeSkipBtn"):
            self.driver.find_element(By.ID,"transcribeSkipBtn").click()

        # main translating
        if self.exists_element(self.driver, By.ID, "translateWord"):
            word = self.driver.find_element(By.ID,"q_word").text
            translated = self.dictionary_get(word,self.package)
            if translated:
                self.elem_type(By.ID, "translateWordAnswer", translated)
                self.driver.find_element(By.ID,"translateWordSubmitBtn").click()

            else:
                print(f"{self.warn} Word Not in dictionary {word}")
                self.elem_type(By.ID, "translateWordAnswer", "omg")
                self.driver.find_element(By.ID,"translateWordSubmitBtn").click()
                time.sleep(1)
                # add correct word to dictionary
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translation,self.package)
                self.driver.find_element(By.ID,"incorrect-next-button").click()

        # falling word (only in practice?)
        if self.exists_element(self.driver, By.ID, "tfw_word"):
            word = self.driver.find_element(By.ID,"tfw_word").text
            if self.dictionary_get(word,self.package):
                self.elem_type(By.ID, "translateFallingWordAnswer", self.dictionary_get(word,self.package))
                self.driver.find_element(By.ID,"translateFallingWordSubmitBtn").click()
            else:
                print(f"{self.warn} Word Not in dictionary {word}")
                self.elem_type(By.ID, "translateFallingWordAnswer", "omg")
                self.driver.find_element(By.ID,"translateFallingWordSubmitBtn").click()
                
                # add correct word to dictionary
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translation,self.package)
                self.driver.find_element(By.ID,"incorrect-next-button").click()
        # choose correct word
        if self.exists_element(self.driver,By.ID, "chooseWord"):
            word = self.driver.find_element(By.ID,"ch_word").text
            answers = self.driver.find_elements(By.CLASS_NAME,"chooseWordAnswer")

            correct = self.dictionary_get(word,self.package)
            if correct:
                for answer in answers:
                    if answer.text == correct:
                        answer.click()
            else:
                print(f"{self.err} Word not in dictionary")
                answers[0].click()
                time.sleep(1)
                # add correct word to dictionary
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translation,self.package)
                self.driver.find_element(By.ID,"incorrect-next-button").click()
        
        # dopln chybajuce pismena
        if self.exists_element(self.driver,By.ID, "completeWord"):
            word = self.driver.find_element(By.ID,"completeWordQuestion")
            translation = self.dictionary_get(word.text,self.package)
            miss = self.driver.find_element(By.ID, "completeWordAnswer")
            missing_letters = self.find_missing_letters(miss.text, translation)
            
            letters = self.driver.find_elements(By.CLASS_NAME,"char")
            if translation:
                for x in missing_letters:
                    for letter in letters:
                        if letter.text == x:
                            letter.click()
            else:
                print(f"{self.err} Word not in dictionary")
                # click letters:
                for i in range(miss.text.count("_")):
                    letters[i].click()

                time.sleep(1)
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translation,self.package)
                self.driver.find_element(By.ID,"incorrect-next-button").click()

        # pexeso
        while self.exists_element(self.driver,By.ID, "pexeso"):
            words = {}
            translations = {}
            wordbuttons = self.driver.find_elements(By.CLASS_NAME,"btn-info")
            translatebuttons = self.driver.find_elements(By.CLASS_NAME,"btn-primary")
            for word in wordbuttons:
                words.update({word.text,word})

            for translation in translatebuttons:
                translations.update({translation.text,translation})

            for x in words:
                if self.dictionary_get(x,self.package):
                    if self.dictionary_get(x) in translations:
                        for y in translations:
                            if self.dictionary_get(x,self.package) == y:
                                words[x].click()
                                words[x].click()
                                translations[y].click()
                                translations[y].click()
                            else:
                                continue
                    else:
                        continue 
                else:
                    words[0].click()
                    words[0].click()
                    translations[0].click()
                    translations[0].click()
                    print(f"{self.err} Word not in dictionary")
                    time.sleep(1)
                    word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                    translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                    self.dictionary_put(word,translation,self.package)
                    self.driver.find_element(By.ID,"incorrect-next-button").click()
    
        # zvol spravny preklad
        if self.exists_element(self.driver,By.ID,"oneOutOfMany"):
            word = self.driver.find_element(By.ID,"oneOutOfManyQuestionWord")
            translations = self.driver.find_elements(By.CLASS_NAME,"oneOutOfManyWord")
            if self.dictionary_get(word.text,self.package):
                for translation in translations:
                    if self.dictionary_get(word.text,self.package) == translation.text:
                        translation.click()
            else:
                translations[0].click()
                print(f"{self.err} Word not in dictionary")
                time.sleep(1)
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translation,self.package)
                self.driver.find_element(By.ID,"incorrect-next-button").click()
    
        else:
            self.driver.save_full_page_screenshot("unknown_exercise.png")
    def do_package(self):
        print(f"{self.ok} Doing Package...")
        time.sleep(2)
        if self.exists_element(self.driver, By.ID, "introRun"):
            print(f"{self.ok} New package Started...")
            self.driver.find_element(By.ID,"introRun").click()
            i = 0
            words = True
            while words:
                if self.exists_element(self.driver, By.ID, "introWord") and self.exists_element(self.driver, By.ID, "introTranslation"):
                    word = self.driver.find_element(By.ID,"introWord")
                    translation = self.driver.find_element(By.ID,"introTranslation")
                    self.dictionary_put(word.text,translation.text,self.package)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "introNext"))).click()
                    self.driver.find_element(By.ID,"introNext").click()
                else:
                    words = False
            while i<3:
                self.do_exercise()
            i+=1
        else:
            print(f"{self.warn} Package has been already started before, words may not be in dictionary!")
            while i<3:
                self.do_exercise()
            i+=1
    def dictionary_get(self,word:str,package = "") -> str | None:
        #print(f"{self.debug} {word=}, {package=}")
        if not package:
            for x in self.word_dictionary[self.wocaclass]:
                #print(x)
                dictionary = self.word_dictionary[self.wocaclass][x]

                if word in dictionary.keys():
                    return dictionary[word]
                elif word in dictionary.values():
                    return list(dictionary.keys())[
                        list(dictionary.values()).index(word)]
            return None
        package = str(package)
        dictionary = self.word_dictionary[self.wocaclass][package]

        if word in dictionary.keys():
            return dictionary[word]
        elif word in dictionary.values():
            return list(dictionary.keys())[
                list(dictionary.values()).index(word)]
        else:
            return None
    def dictionary_put(self,word:str,translation:str,package,echo = True) -> int:
        package = str(package)
        if not word or not translation:
            return
        if not self.wocaclass in self.word_dictionary.keys():
                self.word_dictionary.update({self.wocaclass:{}})
        if not package in self.word_dictionary[self.wocaclass].keys():
            self.word_dictionary[self.wocaclass].update({package:{}})
        
        if not word in self.word_dictionary[self.wocaclass][package]:
            if echo:
                print(f"{self.ok} Adding New word to dictionary: {word} = {translation}")
            
            self.word_dictionary[self.wocaclass][package].update({word:translation})
        elif echo:
            print(f"{self.warn} Word Already in dictionary!")
        self._dictionary_Save()
    def _dictionary_Load(self):
        with open(self.dictionary_path,"r") as f:
            ext_dict = json.load(f)
        self.word_dictionary = ext_dict
    def _dictionary_Save(self):
        with open(self.dictionary_path,"w") as f:
            json.dump(self.word_dictionary,f,indent=2)
Wocabot = wocabot(input("Username:"),getpass("Password:"))
# https://github.com/SneznyKocur/wocabot
