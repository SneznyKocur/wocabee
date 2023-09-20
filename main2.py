from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time, json
from tqdm import tqdm

class wocabot:
    def __init__(self,username,password,args):
        self.word_dictionary = {}
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

        self.word_dictionary = self._dictionary_load()
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)

        print(f"{self.ok} Logging in...")
        self.login(self.username,self.password)
        if not self.is_loggedIn():
            print(f"{self.err} Failed to log in")
            self.driver.quit()
            return
        
        if self.args.getclasses:
            classes = self.get_classes()
            for id,Class in enumerate(classes):
                # class is dict of id:button
                
                print(id, Class[id].find_element(By.TAG_NAME,"span").text)
            return
        elif not self.args.classid:
            print(f"{self.err} Class is required to proceed!")
            return
        self.wocaclass = self.args.classid
        self.pick_class(self.wocaclass,self.get_classes())
        
        self.package = self.args.package
    
        if self.args.practice:
            self.package = 0
            self.pick_package(self.package,self.get_packages(self.PRACTICE))
            self.practice(self.args.target_points)

        elif self.args.do_package:
            packages = self.get_packages(self.DOPACKAGE)
            self.package = self.pick_package(int(self.args.package),packages)
            self.do_package()
        elif self.args.learn:
            self.learn()
        elif self.args.learnall:
            self.learnALL()
        elif self.args.quickclick:
            self.driver.find_element(By.CLASS_NAME,"btn-info").click()
            self.driver.find_element(By.ID,"oneAnswerGameStartBtn").click()
            self.quickclick(self.args.target_points)

        elif self.args.getpackages:
            for i,x in enumerate(self.get_packages(self.GETPACKAGE)):
                k,v = x
                print(f"Package: {i} = {k} Playable: {v}")
        elif self.args.leaderboard:
            first_place = self.get_leaderboard()[0]
            for x in self.get_leaderboard():
                print(f"#{x['place']}: {x['name']} with {x['points']} points (diff to #1 = {int(first_place['points'])-int(x['points'])})")
        else:
            print(f"{self.err} Nothing to do")
        self.driver.quit()

    def elem_type(self,by,elem,x):
        elem = self.driver.find_element(by,elem)
        elem.clear()
        elem.send_keys(x)
    
    def login(self,username,password):
        self.elem_type(By.ID,"login",username)
        self.elem_type(By.ID,"password",password)
        btn = self.driver.find_element(By.ID,"submitBtn")
        btn.click()
    def is_loggedIn(self):
        return self.exists_element(self.driver,By.ID,"logoutBtn")
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
            return self.driver.find_element(by,element).text
        else:
            return 0
    def get_elements_text(self,by,element):
        if self.exists_element(self.driver,by,element):
            return [x.text for x in self.get_elements(by,element)]
        else:
            return [0]
    def wait_for_element(self,timeout,by,element):
        WebDriverWait(self.driver,timeout).until(lambda x: self.driver.find_element(by,element).is_displayed())
        return self.driver.find_element(by,element)
    # class
    def get_classes(self) -> list:
        classesList = []
        classes = self.wait_for_element(5,By.ID,"listOfClasses")
        return [{i:button} for i,button in enumerate(classes.find_elements(By.TAG_NAME,"button"))]
    def pick_class(self,class_id,classes):
        class_id = int(class_id)
        classes[class_id][class_id].click()

    # leaderboard
    def get_leaderboard(self):
        leaderboard = []
        wrapper = self.wait_for_element(5,By.ID,"listOfStudentsWrapper")
        for i in range(len(wrapper.find_element(By.ID,"tbody").find_elements(By.TAG_NAME,"tr"))):
            elem = self.wait_for_element(5,By.ID,"tbody")
            elem2 = elem.find_elements(By.TAG_NAME,"tr")[i]
            try:
                leaderboard.append({"place":elem.find_element(By.CLASS_NAME,"place").text,"name":elem.find_element(By.CLASS_NAME,"name").text,"points":elem.find_elements(By.TAG_NAME,"td")[2].text})
            except:
                pass
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
                    button = self.get_element(elem,By.CLASS_NAME,"btn-primary")
                    packageslist.append({i:button})

        elif prac == self.DOPACKAGE:
            for i,elem in enumerate(self.get_elements(By.CLASS_NAME,"pTableRow")[:10]):
                if self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                    button = elem.find_element(By.CLASS_NAME,"package ").find_element(By.TAG_NAME,"a")
                    packageslist.append({i:button})
        elif prac == self.LEARN or prac == self.LEARNALL:
            for i,elem in enumerate(self.get_elements(By.CLASS_NAME,"pTableRow")):
                if self.exists_element(elem,By.TAG_NAME,"a"):
                    button = elem.find_element(By.TAG_NAME,"a")
                    packageslist.append({i:button})
        return packageslist
    def pick_package(self,package_id,packages):
        package_id = int(package_id)
        packages[package_id][package_id].click()


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

        levelToggle = self.get_element(By.ID,"levelToggle")
        levelToggle.click()

        # pbar = tqdm(total=self.calculate_words(difference))
        while wocapoints <= target_wocapoints:
            wocapoints = int(self.get_element_text(By.ID,"WocaPoints"))
            self.do_exercise()
            # pbar.update()

        if save:
            self.get_element(By.ID,"backBtn").click()

    # learning
    def learn(self,echo = False):
        while self.exists_element(self.driver,By.ID,"intro"):
            self.wait_for_element(10,By.ID,"word")

            word = self.get_element_text(By.ID,"word")
            translation = self.get_element_text(By.ID,"translation")
            self.dictionary_put(word, translation,self.package)

            try: 
                self.driver.find_element(By.ID,"rightArrow").click()
            except:
                print(f"{self.err} Failed to click right arrow")
                self.get_element(By.ID,"backBtn").click()
    def LearnALL(self):
        packagelist = self.get_packages(self.LEARNALL)
        for i in tqdm(range(len(packagelist)),colour="red"):
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
                self._outofmany(self)
            else:
                timeleft = self.get_element_text(By.ID, "oneAnswerGameSecondsLeft")
                time.sleep(int(timeleft))

    def find_missing_letters(self,missing,word):
        if not missing or not word:
            print(f"{self.err} no word")
            return
        end = ""
        for i,x in enumerate(missing):
            if x == "_":
                end+=word[i]
        return end

    # exercises
    def do_exercise(self):
        if self.exists_element(self.driver,By.ID,"pexeso"):
            self._idk()
        elif self.exists_element(self.driver,By.CLASS_NAME,"picture"):
            self._idk()
        elif self.exists_element(self.driver,By.ID,"describePicture"):
            self._idk()
        elif self.exists_element(self.driver,By.ID,"transcribeSkipBtn"):
            self.get_element(By.ID,"transcribeSkipBtn").click()
        elif self.exists_element(self.driver,By.ID,"translateWord"):
            word = self.get_element_text(By.ID,"q_word")
            translated = self.dictionary_get(word,self.package)[0]

            if not translated:
                translated = "omg"
            self._main(translated)
        elif self.exists_element(self.driver,By.ID,"tfw_word"):
            word = self.get_element_text(By.ID,"tfw_word")
            translated = self.dictionary_get(word,self.package)[0]
            if not translated:
                translated = "omg"
            self._tfw(translated)
        elif self.exists_element(self.driver,By.ID, "chooseWord"):
            self._ch_word()
        elif self.exists_element(self.driver,By.ID,"compreteWord"):
            self._complete_word()
        elif self.exists_element(self.driver,By.ID,"ontOutOfMany"):
            self._outofmany()
        elif self.exists_element(self.driver,By.ID,"findPair"):
            self._pariky()
        word = self.get_element_text(By.CLASS_NAME,"correctWordQuestion")
        translation = self.get_element_text(By.CLASS_NAME,"correctWordAnswer")
        self.dictionary_put(word,translation,self.package)
        self.get_element(By.ID,"incorrect-next-button").click()
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
        answers = self.get_elements_text(By.CLASS_NAME,"chooseWordAnswer")
        preklad = self.dictionary_get(word,self.package)
        for answer in answers:
            if answer in preklad:
                answer.click()
                break
    def _complete_word(self):
        word = self.get_element_text(By.ID,"completeWordQuestion")
        miss = self.get_element_text(By.ID,"completeWordAnswer")
        preklady = self.dictionary_get(word,self.package)
        preklad = ""
        if preklady:
            for x in preklad:
                if len(miss) == len(x):
                    preklad = x
        if not preklad:
            preklad = preklady[0]

        letters = self.get_elements_text(By.CLASS_NAME,"char")
        missing_letters = self.find_missing_letters(miss,preklad)
        for x in missing_letters:
            for letter in letters:
                if letter == x:
                    letter.click()
        self.get_element(By.ID,"completeWordSubmitBtn").click()
    def _pariky(self):
        questions = self.get_elements_text(By.ID,"q_words")
        answers = self.get_elements_text(By.ID,"a_words")

        for question in questions:
            for y in self.dictionary_get(question,self.package):
                if y in answers:
                    questions[question].click()
                    answers[y].click()
                    break
    def _outofmany(self):
        word = self.wait_for_element(10,By.ID,"ontOutOfManyQuestionWord")
        translations = self.get_elements_text(By.CLASS_NAME,"oneOutOfManyWord")
        preklad = self.dictionary_get(word.text)
        if not preklad:
            print(f"{self.err} Word not in dictionary")
            return
        for translation in translations:
            if translation in preklad:
                translation.click()
    
    def dictionary_get(self,word,*args,**kwargs):
        dictionary = self.word_dictionary[str(self.wocaclass)]
        words = []
        end = []
        if "," in word:
            for x in word.split(","):
                words.append(x.strip())
            words.append(word)
        else:
            words.append(word)
        for word in words:
            for x in dictionary:
                if word == x:
                    end.append(dictionary[x])
                elif word in dictionary[x]:
                    end.append(x)

    def dictionary_put(self,word,translation,*args,**kwargs):
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
            words.append(word)
            value = words
            key = translation
        elif "," in translation:
            translations = []
            for x in translation.split(","):
                translations.append(x.strip())
            translations.append(translation)
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
args = parser.parse_args()

Wocabot = wocabot(username=args.username,password=args.password,args=args)