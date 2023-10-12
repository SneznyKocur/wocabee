from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import time, json, os, datetime
from tqdm import tqdm
import argparse

#TODO: GUI


class wocabot:
    def __init__(self,username,password,args):
        self.args = args
        self.username = username
        self.password = password

        self.word_dictionary = {}
        self.tracker_path = "../wocabee archive/track.json"
        self.dictionary_path = "../wocabee archive/8.A.json"
        self.url = "https://wocabee.app/app"

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

        self.word_dictionary = self._dictionary_Load()
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)
        self.class_names = []
        print(f"{self.ok} Logging in...")
        self.login(self.username,self.password)
        if not self.is_loggedIn():
            print(f"{self.err} Failed to log in")
            self.driver.quit()
            return
        self.name = self.get_elements_text(By.TAG_NAME,"b")[0]
        for id,Class in enumerate(self.get_classes()):
            self.class_names.append(Class[id].find_element(By.TAG_NAME,"span").text)
        print(self.class_names,len(self.class_names))
        if self.args.getclasses:
            classes = self.get_classes()
            for id,Class in enumerate(classes):
                # class is dict of id:button
                
                print(id, Class[id].find_element(By.TAG_NAME,"span").text)

            return
        elif not self.args.classid and not self.args.auto:
            print(f"{self.err} Class is required to proceed!")
            return
        if not self.args.auto:
            self.wocaclass = self.args.classid
            self.pick_class(self.wocaclass,self.get_classes())
        else:
            self.auto()
        self.package = self.args.package

        if self.args.practice:
            self.package = 0
            self.pick_package(self.package,self.get_packages(self.PRACTICE))
            self.practice(self.args.target_points)
        elif self.args.tracker:
            self.track()
        elif self.args.do_package:
            packages = self.get_packages(self.DOPACKAGE)
            self.package = self.pick_package(int(self.args.package),packages)
            self.do_package()
        elif self.args.learn:
            packages = self.get_packages(self.LEARN)
            self.pick_package(self.args.package,packages)
            self.learn()
        elif self.args.learnall:
            self.learnALL()
        elif self.args.quickclick:
            self.get_element(By.CLASS_NAME,"btn-info").click()
            self.get_element(By.ID,"oneAnswerGameStartBtn").click()
            self.quickclick(self.args.target_points)

        elif self.args.getpackages:
            for i,x in enumerate(self.get_packages(self.GETPACKAGE)):
                k,v = x
                print(f"Package: {i} = {k} Playable: {v}")
        elif self.args.leaderboard:
            leaderboard = self.get_leaderboard()
            first_place = leaderboard[0]
            for x in leaderboard:
                print(f"#{x['place']:<2}: {x['name']:<20} ({'🟢' if x['online'] else '🔴'}) {x['points']:<3} (diff to #1 = {int(first_place['points'])-int(x['points']):>4}) {x['packages']}")
        else:
            print(f"{self.err} Nothing to do")
        self.driver.quit()

    def elem_type(self,by,elem,x):
        #print("typing:",elem,x)
        elem = self.get_element(by,elem)
        
        elem.clear()
        elem.send_keys(x)
    
    def login(self,username,password):
        self.elem_type(By.ID,"login",username)
        self.elem_type(By.ID,"password",password)
        btn = self.get_element(By.ID,"submitBtn")
        btn.click()
    def is_loggedIn(self):
        return self.wait_for_element(2,By.ID,"logoutBtn")
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
        print(magic)
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


    def practice(self,target_wocapoints = None):
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
        for i in tqdm(range(len(packagelist)),colour="red"):
            packagelist = self.get_packages(self.LEARNALL)
            self.wait_for_element(10,By.CLASS_NAME,"pTableRow")
            
            package_id = list(packagelist[i].keys())[0]
            self.package = package_id
            self.pick_package(package_id,packagelist)
            self.learn()

    # quickclick
    def quickclick(self,target_points = None):
        if not target_points:
            target_points = int(input("points:"))
        elif not "+" in target_points:
            target_points = int(target_points)
        else:
            print(f"{self.err} Cant use {target_points} in quickclick")
            return
        while self.exists_element(self.driver,By.ID,"oneAnswerGameSecondsLeft"):
            curr_points = int(self.get_element_text(By.ID,"oneAnswerGameCounter"))
            if curr_points <= target_points:
                self._outofmany()
            else:
                timeleft = self.get_element_text(By.ID, "oneAnswerGameSecondsLeft")
                time.sleep(int(timeleft))

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
    
    def track(self):
        with open(self.tracker_path,"r",encoding="utf-8") as f:
            tracker = json.load(f)
        no = datetime.datetime.now()
        while True:
            leaderboard = self.get_leaderboard()
            os.system("clear")
            
            now = f"{no.day}.{no.month}.{no.year} {no.hour}:{no.minute}"
            names = []
            for x in leaderboard:
                
                name = x["name"]
                online = x["online"]
                if online:
                    names.append(name)
                    if "Jakub Huttman" in names:
                        names.remove("Jakub Huttman")
                tracker.update({now:names})
            print(f"{self.debug} (tracker) {now}: {names}")
            if datetime.datetime.now().minute == no.minute + 10:
                no = datetime.datetime.now()
                print(f"{self.debug} (tracker) dumping...")
                with open(self.tracker_path,"w",encoding="utf-8") as f:
                    json.dump(tracker,f,indent=2)


    def leave_class(self):
        self.get_element(By.CLASS_NAME,"home-breadcrumb").click()
        time.sleep(0.5) # wait for webpage to load
    def auto(self):
        now = datetime.datetime.now()
        offset = 0
        while True:
            if datetime.datetime.now().hour == now.hour+offset:
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
                offset = 3

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
        with open(self.dictionary_path,"r") as f:
            ext_dict = json.load(f)
        self.word_dictionary = ext_dict
        return ext_dict
    def _dictionary_Save(self):
        with open(self.dictionary_path,"w") as f:
            json.dump(self.word_dictionary,f,indent=2)
    

parser = argparse.ArgumentParser(
                    prog='WocaBot',
                    description='Multi-purpose bot for wocabee',
                    epilog='I am not responsible for your teachers getting angry :)')

parser.add_argument("-u","--user","--username",dest="username",required=False) # debug
parser.add_argument("-p","--pass","--password",dest="password",required=False) # debug
parser.add_argument("--practice",action='store_true',dest="practice",required=False)
parser.add_argument("--quickclick",action='store_true',dest="quickclick",required=False)
parser.add_argument("--points",dest="target_points",required=False)
parser.add_argument("--class",dest="classid",required=False)
parser.add_argument("--package",dest="package",required=False)
parser.add_argument("--do-package",action='store_true',dest="do_package",required=False)
parser.add_argument("--learn-all",action="store_true",dest="learnall",required=False)
parser.add_argument("--learn",action="store_true",dest="learn",required=False)
parser.add_argument("--get-classes","--classes",action="store_true",dest="getclasses",required=False)
parser.add_argument("--get-packages","--packages",action="store_true",dest="getpackages",required=False)
parser.add_argument("--get-leaderboard","--leaderboard",action="store_true",dest="leaderboard")
parser.add_argument("--track",action="store_true",dest="tracker",required=False)
parser.add_argument("--auto",action="store_true",dest="auto",required=False)
parser.add_argument("--leaderboard-pos",dest="leaderboardpos",required=False)
args = parser.parse_args()

Wocabot = wocabot(username=args.username,password=args.password,args=args)