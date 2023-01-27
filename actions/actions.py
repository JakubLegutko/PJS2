# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


#This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import json

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime
from fuzzywuzzy import fuzz

menuFile = open("data/menu.json", 'r')
menu = json.load(menuFile)

current_receipt = []

def CheckOpen() -> bool:
    with open('data/opening_hours.json', 'r') as f:
        hours = json.load(f)
        test_time = False
        current_time = datetime.datetime.now()
        today = list(hours['items'].keys())[current_time.weekday()]
        time_string = int(str(current_time.time())[:2])
        if (not test_time):
            if (time_string > hours['items'][today]['close'] or time_string < hours['items'][today]['open']):
                return False
            else:
                return True
        else:
            return True

        
class ActionGetMenu(Action):
    menu = None
    hours = None
    def name(self) -> Text:
        return "action_get_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            dispatcher.utter_message(text="This is our menu, feel free to customize any item! ex. Tiramisu with vodka")
            for i in menu['items']:
                dispatcher.utter_message(text="{} for the price of {} dollars and a prep time of {} hours".format(i['name'],i['price'],i['preparation_time']))
            return []




class ActionGetOpeningHours(Action):
    menu = None

    def name(self) -> Text:
        return "action_get_opening_hours"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open('data/opening_hours.json', 'r') as f:
            hours = json.load(f)
        dispatcher.utter_message(text="We are open on these days:")
        for i in hours['items']:
            dispatcher.utter_message(text="{} Open : {}:00".format(i,hours['items'][i]['open']))
            dispatcher.utter_message(text="Close : {}:00".format(hours['items'][i]['close']))


        return []

class ActionGetOpeningOnDay(Action):
    menu = None

    def name(self) -> Text:
        return "action_get_opening_on_day"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open('data/opening_hours.json', 'r') as f:
            hours = json.load(f)
        dispatcher.utter_message(text="We are open on these days:")
        for i in hours['items']:
            dispatcher.utter_message(text="{} Open : {}:00".format(i,hours['items'][i]['open']))
            dispatcher.utter_message(text="Close : {}:00".format(hours['items'][i]['close']))


        return []

class ActionOrderDish(Action):
    def name(self) -> Text:
        return "action_get_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not CheckOpen():
            current_time = datetime.datetime.now()
            dispatcher.utter_message(text="Sorry, the restaurant is closed, as right now it's {} o'clock, try ordering between the following hours:".format(str(current_time.ctime())[:-5]))
            with open('data/opening_hours.json', 'r') as f:
                hours = json.load(f)
            for i in hours['items']:
                dispatcher.utter_message(text="{} Open : {}:00".format(i,hours['items'][i]['open']))
                dispatcher.utter_message(text="Close : {}:00".format(hours['items'][i]['close']))
            return []
        
        order_extra = tracker.get_slot("order_extra")
        order = tracker.get_slot("order")
        output_message = []
        
        if (not order) and (not order_extra):
            dispatcher.utter_message(text="This item is not in our menu, please pick something from the menu")
            return []
        
        
        if order:
            for item in order:
                for dish in menu["items"]:
                    if(fuzz.ratio(dish["name"].lower(), item.lower()) > 85 or fuzz.partial_ratio(dish["name"].lower(), item.lower()) > 85):
                        current_receipt.append(dish)   
            output_message.extend(order)
            
        if order_extra:
            for item in order_extra:
                for dish in menu["items"]:
                    if(fuzz.partial_ratio(dish["name"].lower(), item.lower()) > 85):
                        dish_extra = {
                            **dish,
                            "notes": item 
                        }
                        current_receipt.append(dish_extra)      
            output_message.extend(order_extra)
        
        if not len(current_receipt):
            dispatcher.utter_message(text="One of the items you mentioned doesn't match any menu entries. Please, try ordering again.")
            return [SlotSet("order", []), SlotSet("order_extra",[])]

        if not len(output_message) :
            dispatcher.utter_message(text="One of the items you mentioned doesn't match any menu entries. Please, try ordering again.")
            return [SlotSet("order", []), SlotSet("order_extra",[])]

        dispatcher.utter_message(text="I have added {} to your order. Anything else?".format(output_message))
        dispatcher.utter_message("If any of the ordered items do not match your desired order, please express the intent to clear the order and try again")
        return [SlotSet("order", []), SlotSet("order_extra",[])]

class ActionConfirmOrder(Action):
    def name(self) -> Text:
        return "action_confirm_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        total_names = []
        for dish in current_receipt:
            total_names.append(dish["name"])
        dispatcher.utter_message(text="Could you please confirm the order? {}".format(total_names))
        return []

class ActionShowOrder(Action):
    def name(self) -> Text:
        return "action_show_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Your order currently consists of ")
        if (not len(current_receipt)):
            dispatcher.utter_message(text="Nothing, please order something first")
        else:
            for dish in current_receipt:

                dispatcher.utter_message(text=" {} for the price of {} $ and prep time of {} minutes ".format(dish["name"],dish["price"],int(dish["preparation_time"]*60)))
            dispatcher.utter_message(text="Can I get you anything else?")    
        return []



class ActionClearOrder(Action):
    def name(self) -> Text:
        return "action_clear_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="This was your order {}".format(current_receipt))
        current_receipt.clear()
        dispatcher.utter_message(text="Order cleared")

        return []

class ActionSumUpTheOrder(Action):
    def name(self) -> Text:
        return "action_sum_up_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        time = 0
        money = 0
        for dish in current_receipt:
            money+=dish["price"]
            time+=dish["preparation_time"]

        dispatcher.utter_message(text="Thank You for ordering in our restaurant. We inform You that your shipment will be ready for transport in {} minutes. The total cost is {}$. Have a nice meal :-)".format(int(time*60), money))
        current_receipt.clear()
        return []