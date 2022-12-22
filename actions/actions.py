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
        current_time = datetime.datetime.now()
        today = list(hours['items'].keys())[current_time.weekday()]
        #return current_time.hour > hours['items'][today]['open'] and current_time.hour < hours['items'][today]['close']
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
        #dispatcher.utter_message(text=json.dumps(menu['items'], indent=4))



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
        #dispatcher.utter_message(text=json.dumps(hours['items'], indent=4))

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
        #dispatcher.utter_message(text=json.dumps(hours['items'], indent=4))

        return []

class ActionOrderDish(Action):
    def name(self) -> Text:
        return "action_get_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not CheckOpen():
            dispatcher.utter_message(text="Sorry, currently we are closed. Our Opening hours are:")
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
        
        dish_found = False
        if order:
            for item in order:
                for dish in menu["items"]:
                    if(fuzz.ratio(dish["name"].lower(), item.lower()) > 85):
                        current_receipt.append(dish)
                        dish_found = True     
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
                        dish_found = True        
            output_message.extend(order_extra)
        
        if not dish_found:
            dispatcher.utter_message(text="I did not find one of your order dishes in our menu. Please, try ordering again.")
            return [SlotSet("order", []), SlotSet("order_extra",[])]

        if len(output_message) == 0 :
            dispatcher.utter_message(text="I did not find one of your order dishes in our menu. Please, try ordering again.")
            return [SlotSet("order", []), SlotSet("order_extra",[])]

        dispatcher.utter_message(text="I have added {} to your receipt sir/mam. Anything else?".format(output_message))
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
        dispatcher.utter_message(text="Can we confirm that this is everything you ordered? {}".format(total_names))
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
        total_time = 0
        total_spend = 0
        for dish in current_receipt:
            total_spend+=dish["price"]
            total_time+=dish["preparation_time"]

        dispatcher.utter_message(text="Thank You for ordering in our restaurant. We inform You that your shipment will be ready for transport in {} minutes. The total cost is {}$. Have a nice meal :-)".format(total_time*60, total_spend))
        current_receipt.clear()
        return []