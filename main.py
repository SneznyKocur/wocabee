import argparse
from selenium.webdriver.common.by import By
from time import sleep
import getpass
from wocabee import wocabee
import traceback
#TODO: GUI

"""
    track.json structure:
    { 
        time (d.m.y HH:MM): [
            names (str)
        ]
    }

    dict.json structure:
    {
    class1: [{word:translation}, {word2:translation2}, ...]
    class2...
    Pictures: [{picture path: meaning}]
    }

"""





def leaderboard():

    end = ""
    leaderboard = woca.get_leaderboard()
    #print(f"{woca.debug} {leaderboard}")
    first_place = leaderboard[0]
    for x in leaderboard:
        end+=(f"#{x['place']:<2}: {x['name']:<20} ({'🟢' if x['online'] else '🔴'}) {x['points']:<5} (diff to #1 = {int(first_place['points'])-int(x['points']):>5}) {x['packages']}\n")
    print(end)
    woca.quit()


def miesto(miesto:int):
    leaderboard = woca.get_leaderboard()
    nplace = leaderboard[miesto-1]
    ourpoints = [x["points"] for x in leaderboard if x["name"] == woca.name][0]
    if nplace["name"] != woca.name:
        if int(nplace["points"]) > int(ourpoints):
            target_points = int(nplace["points"]) - int(ourpoints)
            woca.pick_package(0,woca.get_packages(woca.PRACTICE))
            print(f"{woca.name} bude mať {nplace['points']} (#{miesto})")
            woca.get_points(f"+{target_points}")
            
def bodiky(body: int):
    woca.pick_package(0,woca.get_packages(woca.PRACTICE))
    print(f"robim {body} wocapoints pre {woca.name}")
    woca.get_points(f"+{body}")
    woca.quit()


def chybajuce_baliky(trieda: str,komu: str):
    packages = woca.get_packages(woca.GETPACKAGE)
    end = []
    for package in packages:
        items = package.items()
        for name,playable in items:         
            if playable:
                end.append(name)
    woca.quit()
    print(end)
    return end
                
    
def zrob_balik(package):
    woca.pick_package(package,woca.get_packages(woca.DOPACKAGE))
    while True:
        try:
            woca.do_package()
        except Exception as e:
            print(e)
        else:
            break

def nauc_balik(trieda: str,komu: str):
    pass

def vsetky_baliky():
    while woca.get_packages(woca.DOPACKAGE):
        woca.pick_package(0,woca.get_packages(woca.DOPACKAGE))
        while True:
            try:
                woca.do_package()
            except Exception as e:
                print(traceback.format_exception(e))
            else:
                break
        sleep(2)
        if woca.exists_element(woca.driver,By.ID,"continueBtn"):
            woca.get_element(By.ID,"continueBtn").click()
        try:
            woca.wait_for_element(5,By.ID,"backBtn")
            if woca.get_element_text(By.ID,"backBtn") == "Uložiť a odísť":
                woca.get_element(By.ID,"backBtn").click()
        except:
            exit(0)

parser = argparse.ArgumentParser(
                    prog='WocaBot',
                    description='Multi-purpose bot for wocabee',
                    epilog='I am not responsible for your teachers getting angry :)')

parser.add_argument("--practice",action='store_true',dest="practice",required=False)
parser.add_argument("--points",dest="target_points",required=False)
parser.add_argument("--class",dest="classid",required=False)
parser.add_argument("--package",dest="package",required=False)
parser.add_argument("--do-package",action='store_true',dest="do_package",required=False)
parser.add_argument("--learn-all",action="store_true",dest="learnall",required=False)
parser.add_argument("--get-classes","--classes",action="store_true",dest="getclasses",required=False)
parser.add_argument("--get-packages","--packages",action="store_true",dest="getpackages",required=False)
parser.add_argument("--get-leaderboard","--leaderboard",action="store_true",dest="leaderboard")
parser.add_argument("--auto",action="store_true",dest="auto",required=False)
parser.add_argument("--leaderboard-pos","--pos",action="store_true",dest="pos",required=False)
parser.add_argument("--learn", action="store_true",dest="learn",required=False)
args = parser.parse_args()


woca = wocabee(udaje=(input("Username:"),getpass.getpass()))
woca.init()
if args.getclasses:
    for i,x in enumerate(woca.get_classes()):
        print(i,x)
    woca.quit()
if args.getpackages:
    for i,x in enumerate(woca.get_packages(woca.GETPACKAGE)):
        print(i,x)
    woca.quit()
if not args.classid:
    print("you need to specify class id")
    exit(1)




woca.pick_class(args.classid,woca.get_classes())
if args.practice:
    if not args.target_points:
        args.target_points = input("points:")
    
    bodiky(args.target_points)
if args.do_package:
    if not args.package:
        print("you need to specify package (--packages).")
        exit(1)
if args.learnall:
    woca.learnALL()
if args.leaderboard:
    leaderboard()

if args.auto:
    vsetky_baliky()
    woca.quit()
    exit(0)

if args.pos:
    miesto(int(args.pos))
    woca.quit()
if args.learn:
    if not args.package:
        print("you need to specify package (--packages).")
        exit(1)
    woca.pick_package(args.package,woca.get_packages(woca.LEARN))
    woca.learn()