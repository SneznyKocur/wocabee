from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import time, json, os, datetime,threading

import discord
class wocabee:
    def __init__(self):
        self.url = "https://wocabee.app/app"
        self.dict_path = "./dict.json"
        self.data_path = "./data.json"
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
    def init(self,username,password):
        self.word_dictionary = self._dictionary_Load()
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        self.driver.get(self.url)
        self.class_names = []
        print(f"{self.ok} Logging in... {username} {password}")
        self.login(username,password)
        if not self.is_loggedIn():
            self.login(username,password)
            if not self.is_loggedIn():
                print("no login :sob:")
                self.driver.quit()
        self.name = self.get_elements_text(By.TAG_NAME,"b")[0]
        for id,Class in enumerate(self.get_classes()):
            self.class_names.append(Class[id].find_element(By.TAG_NAME,"span").text)
        print(f"finished init {self.class_names}")

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

    # leaderboard
    def get_leaderboard(self):
        leaderboard = []
        time.sleep(1)
        wrapper = self.wait_for_element(5,By.ID,"listOfStudentsWrapper")
        magic = len(self.get_packages(self.GETPACKAGE))
        for i in range(len(wrapper.find_elements(By.CLASS_NAME,"wb-tr"))):
            elem2 = self.wait_for_elements_in_element(5,wrapper,By.CLASS_NAME,"wb-tr")[i]
            try:
                
                elem3 = elem2.find_element(By.CLASS_NAME,"status-icon-wrapper")
                online = False
                if self.exists_element(elem3,By.CLASS_NAME,"status-online"):
                    online = True
                elif self.exists_element(elem3,By.CLASS_NAME,"status-offline"):
                    online = False
                name = ""
                place = 0
                points = 0
                z = [x.text for x in self.wait_for_elements_in_element(5,elem2,By.TAG_NAME,"td")[magic*4:]]
                names = z[i*4]
                name = names.split("\n")[2]
                place = names.split("\n")[0]
                points = z[i*4+2]
                packages = z[i*4+3]
            except Exception as e:
                print(e)
            leaderboard.append({"place":place,"name":name,"points":points,"online":online,"packages":packages})
        return leaderboard
    #packages
    def get_packages(self,prac):
        prac = int(prac)
        packageslist = []
        if prac == self.GETPACKAGE:
            for elem in self.get_elements(By.CLASS_NAME,"pTableRow"):
                name = elem.find_element(By.CLASS_NAME,"package-name").text
                playable = self.exists_element(elem,By.CLASS_NAME,"fa-play-circle")
                packageslist.append({name:playable})

        elif prac == self.PRACTICE:
            for i,elem in enumerate(self.get_elements(By.CLASS_NAME,"pTableRow")[:10]):
                if self.exists_element(elem,By.CLASS_NAME,"fa-gamepad"):
                    button = elem.find_element(By.CLASS_NAME,"btn-primary")
                    packageslist.append({i:button})

        elif prac == self.DOPACKAGE:
            for i,elem in enumerate(self.get_elements(By.CLASS_NAME,"pTableRow")[:10]):
                if self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                    button = elem.find_element(By.CLASS_NAME,"package ").find_element(By.TAG_NAME,"a")
                    id = len(packageslist)
                    packageslist.append({id:button})
        elif prac == self.LEARN or prac == self.LEARNALL:
            for i,elem in enumerate(self.get_elements(By.CLASS_NAME,"pTableRow")):
                if self.exists_element(elem,By.TAG_NAME,"a"):
                    button = elem.find_element(By.TAG_NAME,"a")
                    packageslist.append({i:button})
        return packageslist
    def pick_package(self,package_id,packages):
        package_id = int(package_id)
        print(packages,package_id)
        packages[package_id][package_id].click()
        self.package = package_id

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

        levelToggle = self.driver.find_element(By.ID,"levelToggle")
        #levelToggle.click()
        ActionChains(self.driver).move_to_element(levelToggle).click(levelToggle).perform()

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
                self.dictionary_put(os.path.basename(path)[::3],translation,Picture=True)
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
        if not missing or not word:
            print(f"{self.err} no word")
            return
        end = ""
        for i,x in enumerate(missing):
            print(i,x,missing,word,end)
            if x == "_":
                end+=word[i]
        return end

    # exercises
    # USPORIADANIE SLOV:
    # no one si zisti preklad
    # splitne po medzerach
    # zisti kde čo patry
    # zisti o kolko to ma posunut a kam
    # posunie
    # krok 3 znova
    # word-to-arrange
    # ende
    def do_exercise(self):
        if self.exists_element(self.driver,By.ID,"addMissingWord"):
            self._complete_veta()
        elif self.exists_element(self.driver,By.ID,"choosePicture"):
            # HACK
            try:
                self._choose_picture()
            except:
                self._idk()
        elif self.exists_element(self.driver,By.ID,"pexeso"):
            self._pexeso()
        elif self.exists_element(self.driver,By.CLASS_NAME,"picture"):
            self._idk()
        elif self.exists_element(self.driver,By.ID,"describePicture"):
            # HACK
            try:
                self._describe()
            except:
                self._idk()
        elif self.exists_element(self.driver,By.ID,"transcribeSkipBtn"):
            print(f"{self.debug} skip")
            self.get_element(By.ID,"transcribeSkipBtn").click()
        elif self.exists_element(self.driver,By.ID,"translateWord"):
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
        elif self.exists_element(self.driver,By.ID,"tfw_word"):
            print(f"{self.debug} tfw word")
            word = self.get_element_text(By.ID,"tfw_word")
            translated = self.dictionary_get(word,self.package)[0]
            if not translated:
                translated = "omg"
            self._tfw(translated)
        elif self.exists_element(self.driver,By.ID, "chooseWord"):
            print(f"{self.debug} choose word")
            self._ch_word()
        elif self.exists_element(self.driver,By.ID,"completeWord"):
            print(f"{self.debug} complete wodrd")
            self._complete_word()
        elif self.exists_element(self.driver,By.ID,"oneOutOfMany"):
            print(f"{self.debug} one out of many")
            self._outofmany()
        elif self.exists_element(self.driver,By.ID,"findPair"):
            print(f"{self.debug} pariky")
            self._pariky()
        elif self.exists_element(self.driver,By.ID,"incorrect-next-button"):
            word = self.get_element_text(By.CLASS_NAME,"correctWordQuestion")
            translation = self.get_element_text(By.CLASS_NAME,"correctWordAnswer")
            self.dictionary_put(word,translation,self.package)
            self.get_element(By.ID,"incorrect-next-button").click()
    
    def _choose_picture(self):
        while True:
            word = self.get_element_text(By.ID,"choosePictureWord")
            picture = self.get_element(By.CLASS_NAME,"slick-current").find_element(By.TAG_NAME,"img")
            if picture.get_attribute("word"):
                for x in self.dictionary_get(word):
                    print(x,picture.get_attribute("word"))
                    if x == picture.get_attribute("word"):
                        picture.click()
                        break
                    else:
                        print(x,picture.get_attribute("word"),x == picture.get_attribute("word"))
            self.get_element(By.CLASS_NAME,"slick-next").click()
    def _describe(self):
        image = self.get_element(By.ID,"describePictureImg")
        path = image.get_attribute("src")
        filename = os.path.basename(path)[::3]
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
        for answer in answers:
            if answer.text in preklad:
                answer.click()
                break
    def _complete_word(self):
        word = self.get_element_text(By.ID,"completeWordQuestion")
        miss = self.get_element_text(By.ID,"completeWordAnswer")
        preklady = self.dictionary_get(word,self.package)
        preklad = ""
        if preklady:
            for x in preklady:
                if len(miss) == len(x):
                    preklad = x
        print(preklad,word,miss)
        letters = [x for x in self.get_element(By.ID,"characters").find_elements(By.TAG_NAME,"span") if x.is_displayed()]
        for _ in self.find_missing_letters(miss,preklad):
            miss = self.get_element_text(By.ID,"completeWordAnswer")
            if "_" in miss:
                index = miss.index("_")
                
                print([x.text for x in letters])
                for x in letters:
                    if x.text == preklad[index]:
                        x.click()
                        letters.remove(x)
                    else:
                        print(x.text,preklad[index])
        try:
            self.wait_for_element(5,By.ID,"completeWordSubmitBtn").click()
        except:
            pass
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
        for translation in translations:
            if translation.text in preklad:
                translation.click()
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

                for x in answers:
                    x.click()
                    for y in x.find_elements(By.CLASS_NAME,"pexesoBack"):
                        answertexts.append(y.text)
                
                for x in questions:
                    x.click()
                    for y in x.find_elements(By.CLASS_NAME,"pexesoBack"):
                        questiontexts.append(y.text)
                time.sleep(0.2) # make this not a double click
                x.click() # hide the button
                for x in answertexts:
                    for y in self.dictionary_get(x):
                        if y in questiontexts:
                            elem = questions[questiontexts.index(y)]
                            elem.click()
                            elem.click()
                            elem2 = answers[answertexts.index(x)]
                            elem2.click()
                            elem2.click()
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
            a_sentence2 = a_sentence.split("_")[0].strip()
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
        ...
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
                    self.wait_for_element(10,By.ID, "introNext")
                    self.get_element(By.ID,"introNext").click()
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
    def get_package_completion(self,x):
        wrapper = self.get_elements(By.CLASS_NAME,"circles-wrapper")
        for _ in wrapper:
            elems = _.find_elements(By.CLASS_NAME,"custom-icon")
            print(x,_,len(elems))
        return 3

    def leave_class(self):
        self.get_element(By.CLASS_NAME,"home-breadcrumb").click()
        time.sleep(0.5) # wait for webpage to load
    def auto(self,offset):
        now = datetime.datetime.now()
        _offset = 0
        while True:
            if datetime.datetime.now().hour == now.hour+_offset:
                now = datetime.datetime.now()
                if not self.args.classid:
                    # check classes
                    classes = self.get_classes()
                    for id,clas in enumerate(classes):
                        try:
                            self.leave_class()
                        except Exception:
                            pass
                        classes = self.get_classes()
                        self.wocaclass = id
                        self.pick_class(id,classes)
                        # do packages in classes
                        packages = self.get_packages(self.DOPACKAGE)
                        while packages:
                            self.pick_package(0,packages)
                            self.do_package()
                            time.sleep(2) # animations
                            if self.exists_element(self.driver,By.ID,"continueBtn"):
                                self.wait_for_element(5,By.ID,"continueBtn").click()
                            while self.exists_element(self.driver,By.ID,"problem-words-next"):
                                self.wait_for_element(5,By.ID,"problem-words-next").click()
                            self.wait_for_element(5,By.ID,"backBtn").click()
                            packages = self.get_packages(self.DOPACKAGE)
                        # do the leaderboard stuff
                        if self.args.leaderboardpos:
                            pos = int(self.args.leaderboardpos)
                            leaderboard = self.get_leaderboard()
                            if leaderboard[pos-1]["name"] != self.name:
                                target_points = int(leaderboard[pos-1]["points"])+1
                                target_points = str(target_points)
                                if not leaderboard[pos-1]["online"]:
                                    self.package = 0
                                    self.pick_package(self.package,self.get_packages(self.PRACTICE))
                                    self.practice(target_points)
                            time.sleep(2) # wait for leaderboard to update
                    
                    self.leave_class()
                else:
                    self.wocaclass = int(self.args.classid)
                    classes = self.get_classes()
                    self.pick_class(self.wocaclass,classes)
                    # do packages in classes
                    packages = self.get_packages(self.DOPACKAGE)
                    while packages:
                        self.pick_package(0,packages)
                        self.do_package()
                        time.sleep(2) # animations
                        if self.exists_element(self.driver,By.ID,"continueBtn"):
                            self.wait_for_element(5,By.ID,"continueBtn").click()
                        while self.exists_element(self.driver,By.ID,"problem-words-next"):
                            self.wait_for_element(5,By.ID,"problem-words-next").click()
                        self.wait_for_element(5,By.ID,"backBtn").click()
                        packages = self.get_packages(self.DOPACKAGE)
                    # do the leaderboard stuff
                    if self.args.leaderboardpos:
                        pos = int(self.args.leaderboardpos)
                        leaderboard = self.get_leaderboard()
                        if leaderboard[pos-1]["name"] != self.name:
                            target_points = int(leaderboard[pos-1]["points"])+1
                            target_points = str(target_points)
                            if not leaderboard[pos-1]["online"]:
                                self.package = 0
                                self.pick_package(self.package,self.get_packages(self.PRACTICE))
                                self.practice(target_points)
                        time.sleep(2) # wait for leaderboard to update
            _offset = offset
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
woca = wocabee()
def get_classes_from_dict():
    
    with open(woca.dict_path,"r") as f:
        dictionary = json.loads(f.read())
    return dictionary.keys()

token = "MTE2MjA3OTU2MTU4OTIxNTMwMg.GT_S9T.Lt4tda-AgPAsGxrH2QoSn_WWMaD_fQcCL6QwCc"

bot = discord.Bot()

async def class_autocomplete(ctx: discord.AutocompleteContext):
    trieda = ctx.options['trieda']
    with open(woca.data_path,"r") as f:
        data = json.load(f)
    end = [x[0] for x in data[trieda] if x]
    print(end)
    return end

class MyView(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Výber balíku", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
        ],
        custom_id="package_select"
    )
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.send_message(f"robkam")
        print(select.values)
        for x in select.values:
            
            x = int(x)
            y = x
            if x != 0 and len(woca.get_packages(woca.DOPACKAGE)) < x:
                x -=1
            for _ in range(woca.get_package_completion(y)):
                print(_)
                woca.pick_package(x,woca.get_packages(woca.DOPACKAGE))
                woca.do_package() # why does this quit??
                time.sleep(2)
                if woca.exists_element(woca.driver,By.ID,"continueBtn"):
                    woca.get_element(By.ID,"continueBtn").click()
                if woca.exists_element(woca.driver,By.ID,"backBtn"):
                    print("yes")
                    if woca.get_element_text(By.ID,"backBtn") == "Uložiť a odísť":
                        woca.get_element(By.ID,"backBtn").click()
        woca.quit()

class LearnView(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Výber balíku", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 5, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
        ],
        custom_id="learn_select"
    )
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.defer()
        original = await interaction.original_response()
        for x in select.values:
            woca.pick_package(x,woca.get_packages(woca.LEARN)) #FIXME change to DOPACKAGE
            woca.learn()
        woca.quit()

        
        await original.channel.send_message("hotovo")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command()
async def hello(ctx):
    await ctx.respond("Hello!")


@bot.slash_command()
async def leaderboard(ctx,classroom: discord.Option(str,choices=get_classes_from_dict())):
    await ctx.defer()
    end = ""
    with open(woca.data_path,"r") as f:
        
        data = json.load(f)
    meno = data[classroom][0][0]
    heslo = data[classroom][0][1]
    woca.init(meno,heslo)
    index = woca.class_names.index(classroom)
    woca.pick_class(index,woca.get_classes())
    leaderboard = woca.get_leaderboard()
    first_place = leaderboard[0]
    for x in leaderboard:
        end+=(f"#{x['place']:<2}: {x['name']:<20} ({'🟢' if x['online'] else '🔴':>5}) {x['points']:<3} (diff to #1 = {int(first_place['points'])-int(x['points']):>4}) {x['packages']}\n")
    await ctx.respond(end)
    woca.quit()
@bot.slash_command()
async def zasielka(ctx,meno:str,trieda: discord.Option(str,choices=get_classes_from_dict()),wocabee_prihlasovacie: str,wocabee_heslo: str,baliky: int,body: int,cena: str):
    with open(woca.data_path,"r") as f:
        data = json.load(f)
    if not trieda in data:
        data.update({trieda:[]})
    data[trieda].append([wocabee_prihlasovacie,wocabee_heslo])
    with open(woca.data_path,"w") as f:
        json.dump(data,f)

    embed = discord.Embed(
        title="Nová zásielka",
        description="jeees keš many peniaze",
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
    embed.add_field(name="Meno:", value=meno)

    embed.add_field(name="Trieda:", value=trieda)
    embed.add_field(name="Woca meno", value=wocabee_prihlasovacie)
    embed.add_field(name="Woca heslo", value=wocabee_heslo)
    embed.add_field(name="baliky:",value=baliky)
    embed.add_field(name="body:",value=body)
    embed.add_field(name="zarobok:",value=str(cena) + "€")
    embed.set_footer(text="omg áno") # footers can have icons too
    
    with open("zasielky.txt","a") as f:
        f.write(f"{meno}: [{wocabee_prihlasovacie} {wocabee_heslo}] {baliky}b {body}bodov za {cena}€")

    channel = bot.get_channel(1160961783016734740)
    await channel.send(embed=embed)
    response = await ctx.respond("zaregistrovane")
    await response.delete_original_response()

@bot.slash_command()
async def miesto(ctx,trieda: discord.Option(str,choices=get_classes_from_dict()),
                 komu: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(class_autocomplete)),miesto:int):
    await ctx.defer()
    with open(woca.data_path,"r") as f:
        data = json.load(f)
        for x in data[trieda]:
            if x[0] == komu:
                udaje = x


        meno = udaje[0]
        heslo = udaje[1]
        woca.init(meno,heslo)
    woca.pick_class(woca.class_names.index(trieda),woca.get_classes())
    
    leaderboard = woca.get_leaderboard()
    nplace = leaderboard[miesto-1]
    ourpoints = [x["points"] for x in leaderboard if x["name"] == woca.name][0]
    if nplace["name"] != meno:
        if int(nplace["points"]) > int(ourpoints):
            target_points = int(nplace["points"]) - int(ourpoints)
            woca.pick_package(0,woca.get_packages(woca.PRACTICE))
            await ctx.respond(f"{komu} bude mať {nplace['points']} v {trieda} (#{miesto})")
            woca.get_points(f"+{target_points}")
            
@bot.slash_command()
async def bodiky(ctx,trieda: discord.Option(str,choices=get_classes_from_dict()),
                 komu: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(class_autocomplete)),
                 body: int):
    await ctx.defer()

    with open(woca.data_path,"r") as f:
        data = json.load(f)
        for x in data[trieda]:
            if x[0] == komu:
                udaje = x


        meno = udaje[0]
        heslo = udaje[1]
        print(udaje,meno,heslo,komu)
        woca.init(meno,heslo)
    woca.pick_class(woca.class_names.index(trieda),woca.get_classes())
    woca.pick_package(0,woca.get_packages(woca.PRACTICE))
    await ctx.respond(f"robim {body} wocapoints pre {komu} v {trieda}")
    woca.get_points(f"+{body}")
    woca.quit()

@bot.slash_command()
async def nove_baliky(ctx):
    await ctx.defer()
    trieda = get_classes_from_dict()
    embed = discord.Embed(
        title="baliky",
        description="omg ano",
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
    with open(woca.data_path,"r") as f:
        data = json.load(f)
    for y in [_ for _ in trieda if _ != "Picture"]: 
        for x in data[y]:
            udaje = x
            meno = udaje[0]
            heslo = udaje[1]
            print(meno,heslo)
            woca.init(meno,heslo)
            woca.pick_class(woca.class_names.index(y),woca.get_classes())
            packages = woca.get_packages(woca.GETPACKAGE)
            a = False
            for package in packages:
                items = package.items()
                for name,playable in items:         
                    if playable:
                        embed.add_field(name=meno,value=f"{name} {y}")
                        a = True
            woca.quit()
    if not a:
        await ctx.respond("žiadne nedokončene baliky :sob:")
    else:
        await ctx.respond(embed=embed)

@bot.slash_command()
async def chybajuce_baliky(ctx,trieda: discord.Option(str,choices=get_classes_from_dict()),
                 komu: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(class_autocomplete))):
    await ctx.defer()
    with open(woca.data_path,"r") as f:
        data = json.load(f)
        for x in data[trieda]:
            if x[0] == komu:
                udaje = x


        meno = udaje[0]
        heslo = udaje[1]
    woca.init(meno,heslo)
    woca.pick_class(woca.class_names.index(trieda),woca.get_classes())
    packages = woca.get_packages(woca.GETPACKAGE)
    end = []
    for package in packages:
        items = package.items()
        for name,playable in items:         
            if playable:
                end.append(name)
    woca.quit()
    await ctx.respond(end)
                
    
@bot.slash_command()
async def zrob_balik(ctx,trieda: discord.Option(str,choices=get_classes_from_dict()),
                 komu: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(class_autocomplete))
                 ):
    await ctx.defer()
    view = MyView()
    with open(woca.data_path,"r") as f:
        data = json.load(f)
        for x in data[trieda]:
            if x[0] == komu:
                udaje = x


        meno = udaje[0]
        heslo = udaje[1]
    woca.init(meno,heslo)
    woca.pick_class(woca.class_names.index(trieda),woca.get_classes())
    doablePackages = woca.get_packages(woca.DOPACKAGE)
    packages = woca.get_packages(woca.GETPACKAGE)
    if doablePackages:
        playablePackages = list()
        for package in packages:
            for name,playable in package.items():
                if playable:
                    playablePackages.append(name)
        for package in doablePackages:
            items = package.items()
            for id,button in items:         
                view.get_item("package_select").add_option(label=playablePackages[id],value=str(id),default=False)
        view.get_item("package_select").max_values = len(woca.get_packages(woca.DOPACKAGE))
        await ctx.respond(view=view)
    else:
        await ctx.respond("neni su baliky :sob:")

@bot.slash_command()
async def nauc_balik(ctx,trieda: discord.Option(str,choices=get_classes_from_dict()),
                        komu: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(class_autocomplete))):
    await ctx.defer()
    view = LearnView()
    with open(woca.data_path,"r") as f:
        data = json.load(f)
        for x in data[trieda]:
            if x[0] == komu:
                udaje = x


        meno = udaje[0]
        heslo = udaje[1]
    woca.init(meno,heslo)
    woca.pick_class(woca.class_names.index(trieda),woca.get_classes())
    doablePackages = woca.get_packages(woca.LEARN)
    packages = woca.get_packages(woca.GETPACKAGE)
    if doablePackages:
        playablePackages = list()
        for package in packages:
            for name,playable in package.items():    
                playablePackages.append(name)
        for package in doablePackages:
            items = package.items()
            for id,button in items:         
                view.get_item("learn_select").add_option(label=playablePackages[id],value=str(id),default=False)
        
        await ctx.followup.send(view=view)
    else:
        await ctx.followup.send("neni su baliky :sob:")
                        
bot.run(token)