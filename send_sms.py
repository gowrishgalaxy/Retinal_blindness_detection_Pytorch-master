from twilio.rest import Client

#--------------------------------------------------------
# change values of account_sid, auth_token, to and from - all from twilio account
#-------------------------------------------------------
def send(value, classes):
    # Your Account SID from twilio.com/console
    #account_sid = "Twilio accountid"
    # Your Auth Token from twilio.com/console
    auth_token  = "89e49d18ce80ec211389a26f5fc92388"

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+919141785977",
        from_="+19892678904",
        body=f"Blindness detection system report! severity level is : {value} and class is {classes}")

    print('Message sent Succesfully !')
    #print(message.sid)
