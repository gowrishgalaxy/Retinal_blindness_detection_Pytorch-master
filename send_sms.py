from twilio.rest import Client

#--------------------------------------------------------
# change values of account_sid, auth_token, to and from - all from twilio account
#-------------------------------------------------------
def send(value, classes):
    # Your Account SID from twilio.com/console
    account_sid = "twilio sid"
    # Your Auth Token from twilio.com/console
    auth_token  = "twilio token number"

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="from nuber",
        from_="twilio number",
        body=f"Blindness detection system report! severity level is : {value} and class is {classes}")

    print('Message sent Succesfully !')
    print(message.sid)
