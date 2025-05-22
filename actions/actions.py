from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re
from rasa_sdk.events import SlotSet, FollowupAction

class ActionExtractLocation(Action):
    def name(self):
        return "action_extract_location"

    def run(self, dispatcher, tracker, domain):
        last_message = tracker.latest_message.get("text")
        match = re.search(r"(QC|KP)-\d{2},?\s*Room\s*(\d[A-Da-d]\d{2})", last_message, re.IGNORECASE)

        if match:
            hostel = match.group(1) + "-" + match.group(0).split('-')[1][:2]
            room = match.group(2)
            dispatcher.utter_message(text=f"✅ Got it! You are in {hostel}, Room {room}. Now tell me your good name?")
            return [SlotSet("hostel", hostel), SlotSet("room", room)]
        else:
            dispatcher.utter_message(text="⚠️ Sorry, I couldn’t understand that. Please enter in this format: QC-03, Room 1A32")
            return []

class ActionExtractName(Action):
    def name(self) -> Text:
        return "action_extract_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text = tracker.latest_message.get('text')
        name = None

        patterns = [
            r"my name is ([A-Z][a-z]+)",
            r"i am ([A-Z][a-z]+)",
            r"it's ([A-Z][a-z]+)",
            r"([A-Z][a-z]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).capitalize()
                break

        if name:
            dispatcher.utter_message(text=f"Thank you, {name} 😊. Are you facing any hostel-related issue? (yes/no)")
            return [SlotSet("user_name", name)]
        else:
            dispatcher.utter_message("Sorry, I didn't catch your name. Can you repeat it?")
            return []

class ActionAcknowledgeIssue(Action):
    def name(self) -> Text:
        return "action_acknowledge_issue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        issue = tracker.latest_message.get("text")
        user_name = tracker.get_slot("user_name")

        dispatcher.utter_message(
            text=f"Thank you for reporting the **{issue}** issue, {user_name} ✅.\n"
                 f"Please inform the hostel warden first.\nIf it continues, contact the hostel admin or your mentor.\n"
                 f"You can also email the CEO, Director, or Registrar if necessary.\nWould you like me to send a complaint form link? (want/no)"
        )

        return [SlotSet("issue_type", issue)]

class ActionSendFormLink(Action):
    def name(self) -> Text:
        return "action_send_form_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("user_name")
        dispatcher.utter_message(
            text=f"""If your problem is very serious and urgent, and you feel like no one is listening to you, please use this link to officially register your complaint:\n[Grievance Portal](https://kiit.ac.in/grievance/)\n
                    This is the best way to make sure your issue reaches the right authorities immediately.\n"""
                 f"Feel free to fill it. I’m always here to help you, {name}! 😊"
        )

        return []

class ActionHealthProblem(Action):
    def name(self) -> Text:
        return "action_health_problem"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        issue = tracker.latest_message.get("text", "").lower()
        user_name = tracker.get_slot("user_name") or "there"

        if "fever" in issue:
            dispatcher.utter_message(
                text=f"Hi {user_name}, it seems you have a fever 🤒.\n"
                     f"Please rest well, drink plenty of fluids, and monitor your temperature."
            )
            # Set slot and call next action
            return [SlotSet("health_issue", "fever"), FollowupAction("action_provide_health_tips")]

        elif "cold" in issue:
            dispatcher.utter_message(
                text=f"Hello {user_name}, you might be having a cold 🤧.\n"
                     f"Make sure to stay warm, drink warm fluids, and rest."
            )
            return [SlotSet("health_issue", "cold"), FollowupAction("action_provide_health_tips")]

        else:
            dispatcher.utter_message(
                text=f"Thanks for letting me know, {user_name}.\n"
                     f"Please take care of yourself and consult a doctor if needed."
            )
            return [SlotSet("health_issue", None)]

class ActionProvideHealthTips(Action):
    def name(self) -> Text:
        return "action_provide_health_tips"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        health_issue = tracker.get_slot("health_issue")

        if health_issue == "fever":
            dispatcher.utter_message(text="Remember to take fever reducers and see a doctor if it doesn't improve.")
        elif health_issue == "cold":
            dispatcher.utter_message(text="Stay hydrated and rest. Warm soups can help soothe cold symptoms.")
        else:
            dispatcher.utter_message(text="Stay healthy! If you have any symptoms, please consult a doctor.")

        return []
