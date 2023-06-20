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
import argparse
from tqdm import tqdm
import random
# TODO: progress bar in package
class wocabot:
    def __init__(self,username,password,args):
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
        self.args = args
        self.username = username
        self.password = password
        
        self.url = "https://wocabee.app/app"

        self.driver = webdriver.Firefox()
        self.driver.get(self.url)

        print(f"{self.ok} Trying to login...")

        self.Woca_login(username, password)
        if self.is_loggedIn():
            print(f"{self.ok} Succesfully logged in...")
            classid = args.classid

            self.wocaclass = str(classid)
            classes = self.get_classes()
            self.pick_class(classid, classes)

            if not self.args.do_package and not self.args.practice and not self.args.quickclick and not self.args.learn and not self.args.learnall:
                prac = int(input("0: practice, 1: do package 2: learn words 3: Learn ALL words 4: quickclick :"))
            else:
                if self.args.practice:
                    prac = 0
                elif self.args.do_package:
                    prac = 1
                elif self.args.learn:
                    prac = 2
                elif self.args.learnall:
                    prac = 3
                elif self.args.quickclick:
                    prac = 4
            
            if not self.args.package and self.args.practice:
                self.package = 0
            elif self.args.learnall:
                self.learnALL()
            elif not self.args.package and not self.args.quickclick:
                packages = self.get_packages(prac)

                if len(packages) > 1:
                    for id,package in enumerate(packages):
                        print(id,self.driver.find_elements(By.CLASS_NAME,"pTableRow")[id].find_element(By.CLASS_NAME,"package-name").text)

                    self.package = self.pick_package(input("ID:"),packages)
                else:
                    self.package = self.pick_package(0, packages)
            elif not self.args.quickclick:
                packages = self.get_packages(prac)
                print("calling pick package")
                self.package = self.pick_package(int(self.args.package),packages)
            
            if int(prac) == 0:
                # TODO: we shouldn't be needing to do this
                if not self.package:
                    packages = self.get_packages(prac)
                    self.package = self.pick_package(0,packages)
                self.practice(self.args.target_points)
            elif int(prac) == 1:
                self.do_package()
            elif int(prac) == 2:
                self.learn() 
            elif int(prac) == 4:
                # quickclick
                self.driver.find_element(By.CLASS_NAME,"btn-info").click()
                self.driver.find_element(By.ID,"oneAnswerGameStartBtn").click()
                self.quickclick(self.args.target_points)

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

        if prac == 1:
            for elem in self.driver.find_elements(By.CLASS_NAME,"pTableRow")[:10]:
                if self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                    button = elem.find_element(By.CLASS_NAME,"package ").find_element(By.TAG_NAME,"a")
                    print(i)
                    packageslist.append({i:button})
                    i+=1
                else:
                    print(f"what {i=} {packageslist=}")
        elif prac == 0:
            for elem in self.driver.find_elements(By.CLASS_NAME,"pTableRow")[:10]:
                if self.exists_element(elem, By.CLASS_NAME, "fa-gamepad"):
                    button = elem.find_element(By.CLASS_NAME,"btn-primary")
                    packageslist.append({i:button})
                    i+=1
        elif prac == 2:
            for elem in self.driver.find_elements(By.CLASS_NAME,"pTableRow"):
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
    def practice(self,target_wocapoints = None):

        save = True

        wocapoints = int(self.driver.find_element(By.ID,"WocaPoints").text)
        if not target_wocapoints:
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
        for i in tqdm(range(len(packagelist)),colour="red"):
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



    def quickclick(self,target_points = None): # ja neviem čo toto je to som mal asi 20 promile
        if not target_points:
            target_points = int(input("points:"))
        else:
            target_points = int(target_points)
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        while self.exists_element(self.driver, By.ID, "oneAnswerGameSecondsLeft"):
            current_points = int(self.get_element_text(By.ID, "oneAnswerGameCounter"))
            if current_points < target_points:
                WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(
                                lambda x: self.driver.find_element(By.ID, "oneOutOfManyQuestionWord").is_displayed())
                word = self.driver.find_element(By.ID,"oneOutOfManyQuestionWord")
                translations = self.driver.find_elements(By.CLASS_NAME,"oneOutOfManyWord")
                preklady = self.dictionary_get(word.text)
                print(f"{preklady=} {word.text=}")
                if preklady:
                    called = False
                    for translation in translations:
                        if translation.text in preklady:
                            called = True
                            try:
                                translation.click()
                            except:
                                print(f"{self.err} Manual intervention required")
                                time.sleep(2)
                    if not called:
                        print(f"{self.err} Manual intervention required")
                        time.sleep(2)
                # what,
                else:
                    print(f"{self.err} Word not in dictionary")
                    translations[random.randint(0, len(translations)-1)].click()
                    if self.exists_element(self.driver, By.ID, "incorrect-next-button"):
                        self.driver.find_element(By.ID,"incorrect-next-button").click()
            else:
                print(f"{current_points=}, {target_points=}")
                timeleft = self.get_element_text(By.ID, "oneAnswerGameSecondsLeft")
                time.sleep(int(timeleft))

            
            
            
    def find_missing_letters(self,missing,word):
        print(f"{missing=} {word=}")
        end = ""
        for i,x in enumerate(missing):
            if x == "_":
                end+=word[i]
        return end

    def do_exercise(self):
        # TODO: THIS DOESNT GET CALLED UNLESS THE PICTURE IS MANUALLY CLICKED
        if self.exists_element(self.driver,By.CLASS_NAME,"picture"):
            # answer = ""
            # question = self.get_element_text(By.ID,"choosePictureWord")
            # while True:
            #     answer = self.get_element(By.CLASS_NAME,"picture").get_attribute("word")
            #     print(answer,question)

            #     if answer != question:
            #         self.get_element(By.CLASS_NAME,"slick-next").click()
            #     else:
            #         self.get_element(By.CLASS_NAME,"picture").click()
            #         break
            print(f"{self.err} toto neviem help plsky")
            self.last = "fotecky"
        if self.exists_element(self.driver,By.ID,"describePicture"):
            print(f"{self.err} toto neviem help plsky")
            self.last = "opis fotecky"
        # listening skip
        if self.exists_element(self.driver, By.ID, "transcribeSkipBtn"):
            self.driver.find_element(By.ID,"transcribeSkipBtn").click()
            self.last = "skip"

        # main translating
        elif self.exists_element(self.driver, By.ID, "translateWord"):
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
            self.last = "main"

        # falling word (only in practice?)
        elif self.exists_element(self.driver, By.ID, "tfw_word"):
            word = self.driver.find_element(By.ID,"tfw_word").text
            if self.dictionary_get(word,self.package):
                translate = self.dictionary_get(word,self.package)
                self.elem_type(By.ID, "translateFallingWordAnswer", translate[0])
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
            self.last = "fall"

        # choose correct word
        elif self.exists_element(self.driver,By.ID, "chooseWord"):
            word = self.driver.find_element(By.ID,"ch_word").text
            answers = self.driver.find_elements(By.CLASS_NAME,"chooseWordAnswer")
            translations = self.dictionary_get(word,self.package)
            for answer in answers:
                if answer.text in translations:
                    answer.click()
                    break
            self.last = "chooseword"
            if self.exists_element(self.driver, By.ID, "incorrect-next-button"):
                print(f"{self.err} Word not in dictionary")
                answers[0].click()
                time.sleep(1)
                # add correct word to dictionary
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translation,self.package)
                self.driver.find_element(By.ID,"incorrect-next-button").click()
        
        # dopln chybajuce pismena
        elif self.exists_element(self.driver,By.ID, "completeWord"):
            word = self.driver.find_element(By.ID,"completeWordQuestion")
            translations = self.dictionary_get(word.text,self.package)
            miss = self.driver.find_element(By.ID, "completeWordAnswer")
            translation = ""
            if isinstance(translations, list):

                if len(translations) > 1:
                    for x in translations:
                        if len(miss.text) == len(x):
                            translation = x
                            break
                else:
                    translation = translations[0]
            else:
                translation = translations
            print(f"{self.debug} {translation=} {len(translations)=} {translations=} {word.text=}")
            
            
            letters = self.driver.find_elements(By.CLASS_NAME,"char")
            # TODO: this is too much nesting
            if translations:
                missing_letters = self.find_missing_letters(miss.text, translation)
                for translation in [x for x in translations if x]:
                    for x in missing_letters:
                        for letter in letters:
                            if letter.text == x:
                                try:
                                    letter.click()
                                except:
                                    break
                        break
                    break
                ActionChains(self.driver).move_to_element(self.driver.find_element(By.ID,"completeWordSubmitBtn")).click()
            else:
                print(f"{self.err} Word not in dictionary")
                # click letters:
                for i in range(miss.text.count("_")):
                    letters[i].click()

                time.sleep(1)
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translationa = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translationa,self.package)
                WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "incorrect-next-button")))
                
            self.last = "completeword"
        # pexeso
        elif self.exists_element(self.driver, By.ID, "pexeso"):
            # TODO: maybe loop through all of them, click and record the buttons and text in dict?
            print(f"{self.err} toto neviem plsky help")
            self.last = "pexeso"
        # zvol spravny preklad
        elif self.exists_element(self.driver,By.ID,"oneOutOfMany"):
            word = self.driver.find_element(By.ID,"oneOutOfManyQuestionWord")
            translations = self.driver.find_elements(By.CLASS_NAME,"oneOutOfManyWord")
            if self.dictionary_get(word.text,self.package):
                for translation in translations:
                    if translation.text in self.dictionary_get(word.text,self.package):
                        translation.click()

            else:
                translations[0].click()
                print(f"{self.err} Word not in dictionary")
                time.sleep(1)
                word = self.driver.find_element(By.CLASS_NAME,"correctWordQuestion").text
                translation = self.driver.find_element(By.CLASS_NAME,"correctWordAnswer").text
                self.dictionary_put(word,translation,self.package)
                self.driver.find_element(By.ID,"incorrect-next-button").click()
            self.last = "oneoutma"
        elif self.exists_element(self.driver, By.ID, "findPair"):
            questions = self.driver.find_element(By.ID,"q_words").find_elements(By.TAG_NAME,"button")
            answers = self.driver.find_element(By.ID,"a_words").find_elements(By.TAG_NAME,"button")
            
            answertexts = [x.text for x in answers]
            questiontexts = [x.text for x in questions]

            for x in questiontexts:
                for y in self.dictionary_get(x):
                    if y in answertexts:
                        questions[questiontexts.index(x)].click()
                        answers[answertexts.index(y)].click()
                        break
                    break
            self.last = "find pair"

    def do_package(self):
        print(f"{self.ok} Doing Package...")
        if self.exists_element(self.driver, By.ID, "introRun"):
            print(f"{self.ok} New package Started...")
            self.driver.find_element(By.ID,"introRun").click()
            WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "introNext")))
            while self.exists_element(self.driver, By.ID, "introNext"):
                    word = self.driver.find_element(By.ID,"introWord")
                    translation = self.driver.find_element(By.ID,"introTranslation")
                    print(f"{word.text=} {translation.text=} intro")
                    self.dictionary_put(word.text,translation.text,self.package)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "introNext")))
                    self.driver.find_element(By.ID,"introNext").click()
        else:
            print(f"{self.warn} Package has been already started before, words may not be in dictionary!")
        while self.get_element_text(By.ID, "backBtn") == "Späť":
            self.last = ""
            self.do_exercise()
            print(self.last)
            time.sleep(1)
            if self.exists_element(self.driver,By.ID, "completeWordSubmitBtn"):
                self.get_element(By.ID,"completeWordSubmitBtn").click()
            if self.exists_element(self.driver, By.ID, "incorrect-next-button"):
                self.get_element(By.ID, "incorrect-next-button").click()
        else:
            try:
                self.get_element(By.ID,"backBtn").click()
            except:
                time.sleep(10)

    def dictionary_get(self,word:str,*args,**kwargs) -> list:

        dictionary = self.word_dictionary[self.wocaclass]
        words = []
        if "," in word:
            for x in word.split(","):
                words.append(x.strip())
        else:
            words.append(word)

        for word in words:
            for x in dictionary:
                if word in x:
                    return dictionary[x]
                elif word in dictionary[x]:
                    return x
        if isinstance(x,list):
            return x
        else:
            return [f"{x}"]

        return None
    def dictionary_put(self,word:str,translation:str,echo = True,*args,**kwargs) -> int:
        # TODO: list cant be a key so put translation first if its not a list and word as a key  
        if not word or not translation:
            return
        if not self.wocaclass in self.word_dictionary.keys():
            self.word_dictionary.update({self.wocaclass:{}})
        

        if "," in word and "," in translation:
            return

        if "," in word:
            words = []
            for x in word.split(","):
                words.append(x.strip())
            value = words
            key = translation
        elif "," in translation:
            translations = []
            for x in translation.split(","):
                translations.append(x.strip())
            value = translations
            key = word
        else:
            value = [f"{translation}"]
            key = word

        if not key in self.word_dictionary[self.wocaclass]:
            self.word_dictionary[self.wocaclass].update({key:value})
        else:
            for x in value:
                if not x in self.word_dictionary[self.wocaclass][key]:
                    self.word_dictionary[self.wocaclass][key].append(x)
        

        
        
        self._dictionary_Save()
    def _dictionary_Load(self):
        with open(self.dictionary_path,"r") as f:
            ext_dict = json.load(f)
        self.word_dictionary = ext_dict
    def _dictionary_Save(self):
        with open(self.dictionary_path,"w") as f:
            json.dump(self.word_dictionary,f,indent=2)
parser = argparse.ArgumentParser(
                    prog='WocaBot',
                    description='Multi-purpose bot for wocabee',
                    epilog='I am not responsible for your teachers getting angry :)')

parser.add_argument("-u","--user","--username",dest="username",required=True)
parser.add_argument("-p","--pass","--password",dest="password",required=True)
parser.add_argument("--practice",action='store_true',dest="practice",required=False)
parser.add_argument("--quickclick",action='store_true',dest="quickclick",required=False)
parser.add_argument("--points",dest="target_points",required=False)
parser.add_argument("--class",dest="classid",required=True)
parser.add_argument("--package",dest="package",required=False)
parser.add_argument("--do-package",action='store_true',dest="do_package",required=False)
parser.add_argument("--learnall",action="store_true",dest="learnall",required=False)
parser.add_argument("--learn",action="store_true",dest="learn",required=False)
args = parser.parse_args()
Wocabot = wocabot(username=args.username,password=args.password,args=args)