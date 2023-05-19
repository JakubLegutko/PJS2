# PJS2
PJS rasa chatbot

The connection to the Slack server was established according to this instruction and video:
https://www.youtube.com/watch?v=YsOcE8pCXsk
https://rasa.com/docs/rasa/connectors/slack
![image](https://user-images.githubusercontent.com/64753746/209166583-6b6b775c-245b-4397-9ee4-5497a82ce42c.png)
![image](https://user-images.githubusercontent.com/64753746/209166654-15811ba4-ac97-4093-a08e-b3a7dc3773ea.png)
![image](https://user-images.githubusercontent.com/64753746/209166704-d2bcdf38-7f24-4835-a4aa-78e4b237159d.png)


In this example conversation an user orders some items, then proceeds to checkout.
Another conversation is started later, with omitting the greeting, going straight to the menu and then abandonning the order.

The bot will now check whether the restaurant is open, if not it will tell the user to come back at a later time, the user can disable this 
function and enter debug mode by setting test_time to True inside the actions.py file

The bot is also capable of detecting the intent to see the order by the user.

The bot will ask the user to pick delivery or pickup, on delivery it will add delivery time and cost to the order.

Update May 19: The bot is now capable of connecting to GPT models and asking them questions on the behalf of the user:
![image](https://github.com/JakubLegutko/PJS2/assets/64753746/281369f4-64c3-4375-9e53-2d2ffc51e284)
![image](https://github.com/JakubLegutko/PJS2/assets/64753746/aad1bc89-602d-4ac0-987b-9b5f6355062a)
Needs a secret code in the actions.py file to be able to ask questions though. This costs money so I won't give mine away
