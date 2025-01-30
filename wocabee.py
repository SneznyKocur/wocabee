import os
import json
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common import actions
import time, json, os, datetime,threading
from selenium.webdriver.common.by import By
from selenium import webdriver
import traceback
from selenium.webdriver.firefox.options import Options
class wocabee:
    def __init__(self,udaje: tuple):
        self.url = "https://wocabee.app/app"
        self.dict_path = "./dict.json"
        if not os.path.exists(self.dict_path):
            with open(self.dict_path,"w") as f:
                f.write("{}")
        self.word_dictionary = {}
        self.ok = "[+]"
        self.warn = "[!]"
        self.err = "[-]"
        self.info = "[#]"
        self.debug = "[D]"

        self.PRACTICE = 0
        self.DOPACKAGE = 1
        self.LEARN = 2
        self.LEARNALL = 3
        self.GETPACKAGE = 4
        self.udaje = udaje
        #try:
        #    service = GeckoDriverManager().install()
        #    self.driver = webdriver.Firefox(service=FirefoxService(service))
        #except Exception as e:
        #    traceback.print_exception(e)
        options = Options()
        options.headless = True
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
    
        self.driver.get(self.url)
    def init(self):
        self.word_dictionary = self._dictionary_Load()
        self.class_names = []
        username,password = self.udaje
        print(f"{self.ok} Logging in... {username}")
        # HACK:
        attempts = 0
        logged_in = False
        while not logged_in and attempts < 5:
            try:
                self.login(username,password)
            except:
                pass
        
            if self.is_loggedIn():
                logged_in = True
            else:
                attempts+=1
        if not self.is_loggedIn():
            print("no login :sob:")
            self.driver.quit()
        self.name = self.get_elements_text(By.TAG_NAME,"b")[0]
        for id,Class in enumerate(self.get_classes()):
            self.class_names.append(Class[id].find_element(By.TAG_NAME,"span").text)
        print(f"finished init {self.class_names}")
        time.sleep(2)

    def quit(self):
        self.driver.quit()
    def elem_type(self,by,elem,x):
        #print("typing:",elem,x)
        elem = self.get_element(by,elem)
        
        elem.clear()
        elem.send_keys(x)
    
    def login(self,username,password):
        self.elem_type(By.ID,"login",username)
        self.elem_type(By.ID,"password",password)
        time.sleep(0.5)
        btn = self.get_element(By.ID,"submitBtn")
        btn.click()
    def is_loggedIn(self):
        try:
            return self.wait_for_element(2,By.ID,"logoutBtn")
        except:
            return False    
    # utilities
    def exists_element(self,root,by,element):
        try:
            return root.find_element(by,element).is_displayed()
        except:
            return False
    def get_element(self,by, element):
        if self.exists_element(self.driver,by,element):
            return self.driver.find_element(by,element)
        else:
            return None
    def get_elements(self,by,element):
        if self.exists_element(self.driver,by,element):
            return self.driver.find_elements(by,element)
        else:
            return None
    def get_element_text(self,by, element):
        if self.exists_element(self.driver,by,element):
            return self.get_element(by,element).text
        else:
            return 0
    def get_elements_text(self,by,element):
        if self.exists_element(self.driver,by,element):
            return [x.text for x in self.get_elements(by,element)]
        else:
            return [0]
    def wait_for_element(self,timeout,by,element):
        WebDriverWait(self.driver,timeout).until(lambda x: self.driver.find_element(by,element).is_displayed())
        return self.get_element(by,element)
    def wait_for_element_in_element(self,timeout,elem,by,element):
        WebDriverWait(self.driver,timeout).until(lambda x: elem.find_element(by,element).is_displayed())
        return self.get_element(by,element)
    def wait_for_elements_in_element(self,timeout,elem,by,element):
        WebDriverWait(self.driver,timeout).until(lambda x: elem.find_element(by,element).is_displayed())
        return self.get_elements(by,element)
    # class 
    def get_classes(self) -> list:
        classesList = []
        classes = self.wait_for_element(5,By.ID,"listOfClasses")
        classesList = [{i:button} for i,button in enumerate(classes.find_elements(By.CLASS_NAME,"btn-wocagrey"))]
        return classesList
    def pick_class(self,class_id,classes):
        print("PICKING",class_id)
        try:
            class_id = int(class_id)
            classes[class_id][class_id].click()
            self.wocaclass = class_id
        except Exception as e:
            print(class_id,classes,classes[class_id],len(classes),e)
        time.sleep(2) # loading times

    # leaderboard
    # TODO: FIX THIS
    def get_leaderboard(self):
        # self.wait_for_element(10,By.ID,"standardView")
        # leaderboard = []
        # magic = len(self.get_packages(self.GETPACKAGE))
        # for i in range(len(self.wait_for_element(5,By.ID,"listOfStudentsWrapper").find_elements(By.CLASS_NAME,"wb-tr"))):
        #     self.wait_for_element(10,By.ID,"standardView")
        #     try:
        #         online = False
        #         if self.exists_element(self.wait_for_elements_in_element(5,self.wait_for_element(5,By.ID,"listOfStudentsWrapper"),By.CLASS_NAME,"wb-tr")[i].find_element(By.CLASS_NAME,"status-icon-wrapper"),By.CLASS_NAME,"status-online"):
        #             online = True
        #         elif self.exists_element(self.wait_for_elements_in_element(5,self.wait_for_element(5,By.ID,"listOfStudentsWrapper"),By.CLASS_NAME,"wb-tr")[i].find_element(By.CLASS_NAME,"status-icon-wrapper"),By.CLASS_NAME,"status-offline"):
        #             online = False
        #         name = ""
        #         place = 0
        #         points = 0
        #         z = [x.text for x in self.wait_for_elements_in_element(5,self.wait_for_elements_in_element(5,self.wait_for_element(5,By.ID,"listOfStudentsWrapper"),By.CLASS_NAME,"wb-tr")[i],By.TAG_NAME,"td")[magic*4:]]
        #         names = z[i*4]
        #         name = names.split("\n")[2]
        #         place = names.split("\n")[0]
        #         points = z[i*4+2]
        #         packages = z[i*4+3]
        #     except Exception as e:
        #         self.driver.save_screenshot("screenshot.png")
        #         print(e)
        #     leaderboard.append({"place":place,"name":name,"points":points,"online":online,"packages":packages})
        # return leaderboard
        table_body = self.get_element(By.ID,"tbody")
        students = table_body.find_elements(By.CLASS_NAME,"wb-tr")
        leaderboard = []
        for student in students:
            place = student.find_element(By.CLASS_NAME,"place").text
            name = student.find_element(By.CLASS_NAME,"name").text
            online = "status-online" in student.find_element(By.CLASS_NAME,"status-icon").get_attribute("class")      
            points = student.find_elements(By.TAG_NAME,"td")[2].text
            packages = student.find_elements(By.TAG_NAME,"td")[3] .text
            leaderboard.append({"place":place,"name":name,"points":points,"online":online,"packages":packages})
        return leaderboard
    #packages
    def get_packages(self, prac):
        prac = int(prac)
        packageslist = []
        if self.exists_element(self.driver, By.ID, "showMorePackagesBtn"):
            self.get_element(By.ID, "showMorePackagesBtn").click()
        elements = self.get_elements(By.CLASS_NAME, "pTableRow")
        for i, elem in enumerate(elements):
            if prac == self.GETPACKAGE and self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                name = elem.find_element(By.CLASS_NAME, "package-name").text
                playable = True
            elif prac == self.PRACTICE and self.exists_element(elem, By.CLASS_NAME, "fa-gamepad"):
                button = elem.find_element(By.CLASS_NAME, "btn-primary")
                packageslist.append({i: button})
                continue
            elif prac == self.DOPACKAGE and self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                button = elem.find_element(By.CLASS_NAME, "package ").find_element(By.TAG_NAME, "a")
                id = len(packageslist)
                packageslist.append({id: button})
                continue
            elif prac == self.LEARN or prac == self.LEARNALL and self.exists_element(elem, By.TAG_NAME, "a"):
                button = elem.find_element(By.TAG_NAME, "a")
                packageslist.append({i: button})
                continue
            if prac == self.GETPACKAGE:
                packageslist.append({name: playable})
        return packageslist
    
    def pick_package(self,package_id,packages):
        package_id = int(package_id)
        print(packages,package_id)
        packages[package_id][package_id].click()
        self.package = package_id
        time.sleep(2)

    def get_points(self,target_wocapoints = None):
        save = True

        wocapoints = int(self.get_element_text(By.ID,"WocaPoints"))
        if not target_wocapoints:
            target_wocapoints = input("target wocapoints: ")

        if target_wocapoints.startswith("+"):
            target_wocapoints = wocapoints + int(target_wocapoints.replace("+", ""))
        else:
            target_wocapoints = int(target_wocapoints)


        difference = target_wocapoints - wocapoints
        
        print(f"{self.info} Doing {difference} wocapoints ({wocapoints} -> {target_wocapoints})")

        #levelToggle = self.driver.find_element(By.ID,"levelToggle")
        #levelToggle.click()
        #ActionChains(self.driver).move_to_element(levelToggle).click(levelToggle).perform()

        # pbar = tqdm(total=self.calculate_words(difference))
        #for _ in range(int(difference / 2)):
        while wocapoints < target_wocapoints:
            print(wocapoints,target_wocapoints)
            try:
                wocapoints = int(self.wait_for_element(5,By.ID,"WocaPoints").text)
            except Exception as e:
                print(e)
            self.do_exercise()
            # pbar.update()

        if save:
            self.get_element(By.ID,"backBtn").click()
    # learning
    def learn(self,echo = False):
        while self.exists_element(self.driver,By.ID,"intro"):
            word = self.wait_for_element(5,By.ID,"word").text
            translation = self.get_element_text(By.ID,"translation")
            if self.exists_element(self.driver,By.ID,"pictureThumbnail"):
                # picture
                picture = self.get_element(By.ID,"pictureThumbnail")
                path = picture.get_attribute("src")
                print(f"{self.debug} PUT {os.path.basename(path)[:-4]} as translation")
                self.dictionary_put(os.path.basename(path)[:-4],translation,Picture=True)
            print(f"{self.debug} PUT {word} as {translation}")
            self.dictionary_put(word, translation,self.package)

            try: 
                self.get_element(By.ID,"rightArrow").click()
            except:
                print(f"{self.err} Failed to click right arrow")
                self.get_element(By.ID,"backBtn").click()
    def learnALL(self):
        packagelist = self.get_packages(self.LEARNALL)
        for i in range(len(packagelist)):
            packagelist = self.get_packages(self.LEARNALL)
            self.wait_for_element(10,By.CLASS_NAME,"pTableRow")
            
            package_id = list(packagelist[i].keys())[0]
            self.package = package_id
            self.pick_package(package_id,packagelist)
            self.learn()

    def find_missing_letters(self,missing,word):
        missing = str(missing)
        word = str(word)
        if not missing or not word:
            print(f"{self.err} no word")
            return
        end = ""
        index = 0
        print(f"{self.debug} {missing.count("_")}")
        for _ in range(missing.count("_")+1):
            x = missing.find("_",index)
            print(f"{self.debug} {x} {_} {word[x]} {index}")
            end+=word[x]
            index = x+1

        return end

    def do_exercise(self):
        if self.exists_element(self.driver,By.ID,"addMissingWord"):
            self._complete_veta()
        if self.exists_element(self.driver,By.ID,"choosePicture"):
            # HACK
            try:
                self._choose_picture()
            except:
                self._idk()
        if self.exists_element(self.driver,By.ID,"pexeso"):
            self._pexeso()
        if self.exists_element(self.driver,By.CLASS_NAME,"picture"):
            self._idk()
        if self.exists_element(self.driver,By.ID,"describePicture"):
            # HACK
            try:
                self._describe()
            except:
                self._idk()
        if self.exists_element(self.driver,By.ID,"transcribeSkipBtn"):
            print(f"{self.debug} skip")
            self.get_element(By.ID,"transcribeSkipBtn").click()
        if self.exists_element(self.driver,By.ID,"translateWord"):
            print(f"{self.debug} translate word")
            word = self.wait_for_element(5,By.ID,"q_word").text
            try:
                translated = self.dictionary_get(word,self.package)[0]
            except Exception as e:
                print(word,e)
                translated = "omg"
            if not translated:
                translated = "omg"
            self._main(translated)
        if self.exists_element(self.driver,By.ID,"tfw_word"):
            print(f"{self.debug} tfw word")
            word = self.get_element_text(By.ID,"tfw_word")
            translated = self.dictionary_get(word,self.package)[0]
            if not translated:
                translated = "omg"
            self._tfw(translated)
        if self.exists_element(self.driver,By.ID, "chooseWord"):
            print(f"{self.debug} choose word")
            self._ch_word()
        if self.exists_element(self.driver,By.ID,"completeWord"):
            print(f"{self.debug} complete word")
            self._complete_word()
        if self.exists_element(self.driver,By.ID,"oneOutOfMany"):
            print(f"{self.debug} one out of many")
            self._outofmany()
        if self.exists_element(self.driver,By.ID,"findPair"):
            print(f"{self.debug} pariky")
            self._pariky()
        if self.exists_element(self.driver,By.ID,"sortableWords"):
            self._arrange_words()
        if self.exists_element(self.driver,By.ID,"incorrect-next-button"):
            word = self.get_element_text(By.CLASS_NAME,"correctWordQuestion")
            translation = self.get_element_text(By.CLASS_NAME,"correctWordAnswer")
            self.dictionary_put(word,translation)
            self.get_element(By.ID,"incorrect-next-button").click()
    def _choose_picture(self):
        while True:
            time.sleep(0.2)
            word_translation = self.get_element_text(By.ID,"choosePictureWord")
            picture = self.get_element(By.CLASS_NAME,"slick-current").find_element(By.TAG_NAME,"img")
            word = picture.get_attribute("word")
            if not self.dictionary_get(word):
                self.get_element(By.CLASS_NAME,"slick-next").click()
            elif word == word_translation: 
                print(word,word_translation,"CLICKING")
                picture.click()
                picture.click()
            elif word_translation in self.dictionary_get(word):
                print(word,word_translation,"CLICKING")
                picture.click()
                picture.click()
            else:
                self.get_element(By.CLASS_NAME,"slick-next").click()
        
    def _describe(self):
        
        image = self.get_element(By.ID,"describePictureImg")
        path = image.get_attribute("src")
        # split by / from right and discard file extension
        filename = path.split("pictures/")[1][:-4]
        description = self.dictionary_get(filename,Picture=True)
        print(description,filename,path)
        self.elem_type(By.ID,"describePictureAnswer",description)
        self.get_element(By.ID,"describePictureSubmitBtn").click()
        
        
    def _idk(self):
        print(f"{self.err} toto neviem ešte")
    def _main(self,translated):
        self.elem_type(By.ID,"translateWordAnswer",translated)
        self.get_element(By.ID,"translateWordSubmitBtn").click()
    def _tfw(self,translated):
        self.elem_type(By.ID,"translateFallingWordAnswer",translated)
        self.get_element(By.ID,"translateFallingWordSubmitBtn").click()
    def _ch_word(self):
        word = self.get_element_text(By.ID,"ch_word")
        answers = self.get_elements(By.CLASS_NAME,"chooseWordAnswer")
        preklad = self.dictionary_get(word,self.package)
        [answer.click() for answer in answers if answer.text in preklad]
    def _complete_word(self):
        word = self.get_element_text(By.ID,"completeWordQuestion")
        miss = self.get_element_text(By.ID,"completeWordAnswer")
        preklady = self.dictionary_get(word,self.package)
        print(preklady)
        if preklady:
            for x in preklady:
                if len(miss) == len(x):
                    preklad = x
        print(f"{self.debug} {preklad} {word} {miss}")
        self.get_element(By.ID,"completeWordAnswer").send_keys("".join(self.find_missing_letters(miss,preklad)))
        try:
            self.wait_for_element(5,By.ID,"completeWordSubmitBtn").click()
        except Exception as e:
            print(traceback.format_exception(e))
    def _pariky(self):
        questions = self.get_elements(By.CLASS_NAME,"fp_q") # btn-success
        questiontexts = [x.text for x in questions]

        answers = self.get_elements(By.CLASS_NAME,"fp_a") # btn-primary
        answertexts = [x.text for x in answers]
        questionanswers = [self.dictionary_get(x) for x in questiontexts]
        for x in questionanswers:
            for y in x:
                if y in answertexts:
                    for z in self.dictionary_get(y):
                        if z in questiontexts:
                            questions[questiontexts.index(z)].click()
                    answers[answertexts.index(y)].click()
    def _outofmany(self):
        word = self.wait_for_element(10,By.ID,"oneOutOfManyQuestionWord")
        translations = self.get_elements(By.CLASS_NAME,"oneOutOfManyWord")
        preklad = self.dictionary_get(word.text)
        if not preklad:
            print(f"{self.err} Word not in dictionary")
            return
        # for translation in translations:
        #     if translation.text in preklad:
        #         translation.click()
        [translation.click() for translation in translations if translation.text in preklad]
    def _pexeso(self):
        # pa_words
        # pq_words
        # pexesoCardWrapper
        # pexesoBack
        while self.exists_element(self.driver,By.ID,"pexeso"):
            try:
                answertexts = []
                questiontexts = []
                pa_words = self.get_element(By.ID,"pa_words")
                pq_words = self.get_element(By.ID,"pq_words")

                answers = pa_words.find_elements(By.CLASS_NAME,"pexesoCardWrapper")
                questions = pq_words.find_elements(By.CLASS_NAME,"pexesoCardWrapper")

                end = []
                for x in questions:
                    x.click()
                    text = x.find_elements(By.CLASS_NAME,"pexesoBack")[0].text
                    questiontexts.append(text)

                for i,x in enumerate(answers):
                    x.click()
                    text = x.find_elements(By.CLASS_NAME,"pexesoBack")[0].text
                    answertexts.append(text)
                    for z in self.dictionary_get(text):
                        if z in questiontexts:
                            end.append((x,questions[questiontexts.index(z)]))
                            break

                    
                
                
                time.sleep(0.2) # make this not a double click
                x.click() # hide the button
                # for x in answertexts:
                #     for y in self.dictionary_get(x):
                #         if y in questiontexts:
                #             elem = questions[questiontexts.index(y)]
                #             elem.click()
                #             elem.click()
                #             elem2 = answers[answertexts.index(x)]
                #             elem2.click()
                #             elem2.click()
                for x in end:
                    x[0].click()
                    x[0].click()
                    x[1].click()
                    x[1].click()
            except Exception as e:
                print(e)
    def _complete_veta(self):
        # addMissingWord
        # a_sentence
        # q_sentence
        # missingWordAnswer

        # missingWordAnswer = dict[q_sentence] - a_sentence
        a_sentence = self.get_element_text(By.ID,"a_sentence")
        q_sentence = self.get_element_text(By.ID,"q_sentence")
        try:
            index = a_sentence.index("_")
            last = len(a_sentence) - a_sentence[::-1].index("_")
            sentence = self.dictionary_get(q_sentence)
            for x in sentence:
                if len(x) == len(a_sentence):
                    self.elem_type(By.ID,"missingWordAnswer",x[index:last])
                    
        except Exception as e:
            pass
        if self.exists_element(self.driver,By.ID,"addMissingWordSubmitBtn"):
            self.get_element(By.ID,"addMissingWordSubmitBtn").click()
    def _arrange_words(self):
        word = self.get_element_text(By.ID,"def-lang-sentence")
        # FIXME: what if the translation is not the first word here
        translated = self.dictionary_get(word)[0]
        words = translated.split(" ")
        ponctuation = self.get_element_text(By.ID,"static-punctuation")
        end = list()
        for word in words:
            if word.endswith(ponctuation):
                end.append(word.strip(ponctuation))
            else:
                end.append(word)
        words = end
        for i,x in enumerate(words):
            sortable = self.get_elements(By.CLASS_NAME,"word-to-arrange")
            sortable_text = [x.text for x in sortable]
            if x != sortable_text[i]:
                print(f"Moving: {x} -> {sortable_text[i]}")
                ActionChains(self.driver).drag_and_drop(sortable[sortable_text.index(x)],sortable[i]).perform()
        self.get_element(By.ID,"arrangeWordsSubmitBtn").click()
    def do_package(self):
        print(f"{self.ok} Doing Package...")
        if self.exists_element(self.driver, By.ID, "introRun"):
            print(f"{self.ok} New package Started...")
            self.get_element(By.ID,"introRun").click()
            self.wait_for_element(10,By.ID, "introNext")
            while self.exists_element(self.driver, By.ID, "introNext"):
                    word = self.get_element(By.ID,"introWord")
                    translation = self.get_element(By.ID,"introTranslation")
                    if word and translation:
                        self.dictionary_put(word.text,translation.text)
                    picture = self.get_element(By.ID,"pictureThumbnail")
                    if picture:
                        # picture
                        path = picture.get_attribute("src")
                        print(f"{self.debug} PUT {os.path.basename(path)[:-4]} as translation")
                        self.dictionary_put(os.path.basename(path)[:-4],translation.text,Picture=True)
                    try:
                        self.wait_for_element(10,By.ID, "introNext")
                        self.get_element(By.ID,"introNext").click()
                    except Exception as e:
                        print(traceback.format_exception(e))
                        break
        else:
            print(f"{self.warn} Package has been already started before, words may not be in dictionary!")
        while self.get_element_text(By.ID, "backBtn") == "Späť":
            self.last = ""
            self.do_exercise()
            #print(self.last)
            time.sleep(1)
            if self.exists_element(self.driver,By.ID, "completeWordSubmitBtn"):
                self.get_element(By.ID,"completeWordSubmitBtn").click()
            if self.exists_element(self.driver, By.ID, "incorrect-next-button"):
                self.get_element(By.ID, "incorrect-next-button").click()
        else:
            print(f"{self.get_element_text(By.ID,'backBtn')} != 'Späť'")
            while self.exists_element(self.driver,By.ID,"continueBtn"):
                self.get_element(By.ID,"continueBtn").click()
            try:
                self.get_element(By.ID,"backBtn").click()
            except:
                pass

    def leave_class(self):
        self.get_element(By.CLASS_NAME,"home-breadcrumb").click()
        time.sleep(0.5) # wait for webpage to load
    def dictionary_get(self,word,*args,**kwargs):
        word = str(word)
        if not self.word_dictionary:
            self.word_dictionary = self._dictionary_Load()
        dictionary = self.word_dictionary[self.class_names[int(self.wocaclass)]]
        if "Picture" in kwargs.keys():
            dictionary = self.word_dictionary["Picture"]
        words = []
        end = []
        if "," in word:
            for x in word.split(","):
                if len(x.strip()) > 2:
                    words.append(x.strip())
            words.append(word)
        else:
            words.append(word)
        for word in words:
            for x in dictionary:
                if word == x:
                    for x in dictionary[x]:
                        print("BBBBBBB",x,word)
                        if not x in end:
                            end.append(x)
                elif word in dictionary[x]:
                    print("AAAAAAA",x,word,dictionary[x])
                    if not x in end:
                        end.append(x)
        
        if end:
            if isinstance(end[0],list):
                return end[0]
        #print(f"{self.debug} {word} is {end} maybe please")
        print(f"{self.debug} (GET) {word} is {end}")
        return end

    def dictionary_put(self,word,translation,*args,**kwargs):
        self.wocaclass = int(self.wocaclass)
        if not word or not translation:
            return
        if not "Picture" in kwargs.keys():
            if not self.class_names[self.wocaclass] in self.word_dictionary.keys():
                self.word_dictionary.update({self.class_names[self.wocaclass]:{}})
            dictionary = self.word_dictionary[self.class_names[self.wocaclass]]
        else:
            if not "Picture" in self.word_dictionary.keys():
                self.word_dictionary.update({"Picture":{}})
            dictionary = self.word_dictionary["Picture"]
        word = str(word)
        translation = str(translation)

        #if "," in word and "," in translation:
            #return
        """
        if "," in word:
            words = []
            for x in word.split(","):
                words.append(x.strip())
            words.append(word)
            value = words
            key = translation
        """
        if "," in translation:
            translations = []
            for x in translation.split(","):
                translations.append(x.strip())
            translations.append(translation)
            value = translations
            key = word
        else:
            value = [f"{translation}"]
            key = word

        if not key in dictionary:
            dictionary.update({key:value})
        else:
            for x in value:
                if not x in dictionary[key]:
                    dictionary[key].append(x)
       

        
        print(f"{self.debug} (PUT) {word} as {translation}")
        self._dictionary_Save()

    def _dictionary_Load(self):
        with open(self.dict_path,"r") as f:
            ext_dict = json.load(f)
        self.word_dictionary = ext_dict
        return ext_dict
    def _dictionary_Save(self):
        with open(self.dict_path,"w") as f:
            json.dump(self.word_dictionary,f,indent=2)

