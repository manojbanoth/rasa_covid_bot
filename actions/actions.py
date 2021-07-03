# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Optional, Union
#
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet
from rasa_sdk.events import EventType,  UserUtteranceReverted, AllSlotsReset

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import requests
import json
import asyncio
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class ValidateUserForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_user_form"

    #def slot_mappings(self):
    #    return {
    #        "pin_code_confirmation": self.from_entity(entity="pin_code_confirmation", intent="corona_help"), "type": self.from_text()
    #        "pin_code_confirmation": self.from_entity(entity="pin_code_confirmation", intent="corona_help"),
    #        "type": self.from_text()
    #    }
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Optional[List[Text]]:

        #if tracker.slots.get("pin_code_confirmation") == True:
           # return ['pin_code_confirmation', 'category_confirmation']

        #else:
            #return ["pin_code", "category"]
        required_slots = []
        if tracker.latest_message["intent"].get("name") == "corona_help":
            required_slots = ["pin_code_confirmation",'category_confirmation']
            print('required_slots_pin')
        elif tracker.slots.get("category") == True:


            required_slots = ['pin_code_confirmation', 'category_confirmation']
            print('required_slots_slot')


            #if tracker.slots.get("pin_code_confirmation") is True:
               # required_slots = required_slots.append('category_confirmation')
            #return required_slots + slots_mapped_in_domain

        else:

            required_slots = ["pin_code", "category"]
            print('pin_code and cat')

        return required_slots


   #
   # async def extract_pin_code_confirmation(
   #         self,
   #         dispatcher: CollectingDispatcher,
   #         tracker: Tracker,
   #         domain: Dict
   # ) -> Dict[Text, Any]:
   #
   #     if not tracker.slots.get('requested_slot') == 'pin_code_confirmation':
   #         return {}
   #
   #     intent = tracker.latest_message['intent'].get('name')
   #     if intent == "corona_help":
   #         return {"pin_code_confirmation": None}
   #     else:
   #         return {}
   #
   #     entities = tracker.latest_message.get('entities')
   #     for entity in entities:
   #         if entity['entity'] == "pin_code_confirmation":
   #             return {"pin_code_confirmation": entity['value']}
   #     return {}
   #
   #
   # async def extract_category_confirmation(
   #         self,
   #         dispatcher: CollectingDispatcher,
   #         tracker: Tracker,
   #         domain: Dict
   # ) -> Dict[Text, Any]:
   #
   #     if not tracker.slots.get('requested_slot') == 'category_confirmation':
   #         return {}
   #
   #     intent = tracker.latest_message['intent'].get('name')
   #     if intent == "corona_help":
   #         return {"category_confirmation": None}
   #     else:
   #         return {}
   #
   #     entities = tracker.latest_message.get('entities')
   #     for entity in entities:
   #         if entity['entity'] == "category_confirmation":
   #             return {"category_confirmation": entity['value']}
   #     return {}

    async def validate_pin_code(self,
                          slot_value: Any,
                          dispatcher: CollectingDispatcher,
                          tracker: Tracker,
                          domain: DomainDict,
                          ) -> Dict[Text, Any]:



        res = requests.get(
            f'https://api.postalpincode.in/pincode/{slot_value}').json()
        status = res[0]["Status"]

        if status == "Error":
            dispatcher.utter_message(
                text="No records/Invalid pin found; Try with a valid pin")
            return {"pin_code": None}

        else:

            return {"pin_code": slot_value}

    async def validate_category(self,
                          slot_value: Any,
                          dispatcher: CollectingDispatcher,
                          tracker: Tracker,
                          domain: DomainDict,
                          ) -> Dict[Text, Any]:

        url = "http://ec2-3-23-130-174.us-east-2.compute.amazonaws.com:8000/categories"
        r = requests.get(url)
        data = json.loads(r.content)
        category_list = data["data"]
        if slot_value not in category_list:
            dispatcher.utter_message(text="This resource is currently not available. Please choose another.")
            return {"category": None}
        else:
            return {"category": slot_value}

    async def validate_pin_code_confirmation(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        print("validate confirm pin code")

        pin_code = tracker.get_slot("pin_code")

        if slot_value.lower() == 'no':
            return {"pin_code": None}
        else:
            return {"pin_code": pin_code}


    async def validate_category_confirmation(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        category = tracker.get_slot("category")
        print(category)
        if slot_value.lower() == "no":
             return {"category": None}
        else:
            return {"category": category}


class UserIntent(Action):
    def name(self) -> Text:
        return "user_Intent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message['intent'].get('name')
        print(intent)
        pin_code = tracker.get_slot("pin_code")
        print(pin_code)
        category = tracker.get_slot("category")

        if intent == "corona_help":
            dispatcher.utter_message(
                response="utter_ask_pin_code_confirmation")
            return {"pin_code_confirmation": None, "category_confirmation": None}


class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"




    def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:




        pin_code = tracker.get_slot("pin_code")
        category = tracker.get_slot("category")

        pin = requests.get(
            f'https://api.postalpincode.in/pincode/{pin_code}').json()
        city = pin[0]['PostOffice'][0]['District']

        data_city = requests.get(
            f"http://ec2-3-23-130-174.us-east-2.compute.amazonaws.com:8000/cities").json()
        cities = data_city['data']

        if city in cities:
            city = city.replace(" ", "%20")
            category = category.replace(" ", "%20")
            category_data = requests.get(
                f"http://ec2-3-23-130-174.us-east-2.compute.amazonaws.com:8000/resource?city={city}&category={category}").json()

            data = category_data['data']

            if not data:
                result = "No resources found."
                dispatcher.utter_message(response="utter_submit",
                                         pin_code=pin_code,
                                         category=category,
                                         contact=result,
                                         description=result,
                                         organisation=result,
                                         phone=result,
                                         state=result)
                return []

            contact = data[0]["contact"]
            description = data[0]["description"]
            organisation = data[0]["organisation"]
            phone = data[0]["phone"]
            state = data[0]["state"]

            category = category.replace("%20", " ")

            dispatcher.utter_message(response="utter_submit",
                                     pin_code=pin_code,
                                     category=category,
                                     contact=contact,
                                     description=description,
                                     organisation=organisation,
                                     phone=phone,
                                     state=state
                                     )

        else:
            result = "No resources found."
            dispatcher.utter_message(response="utter_submit",
                                     pin_code=pin_code,
                                     category=category,
                                     contact=result,
                                     description=result,
                                     organisation=result,
                                     phone=result,
                                     state=result)