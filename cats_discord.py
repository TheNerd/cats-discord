import select
from systemd import journal
from discord_webhook import DiscordWebhook
import datetime

# configuration 
botname = "" # give your bot a nice name so you know who it is
webhookurl = "" # got to Discord and set up a web hook for the channel you want to post to
avatar = "" # URL of an image to use as the avatar for the bot. This needs to be an public accessible location.
systemd_unit = "cats-igate.service" # leave this at cats-igate.service for use on a Raspberry Pi with a Hat - piwifhat


def bot_stop_err(err):
    stop_bot = DiscordWebhook(url=webhookurl, username=botname, content=datetime.datetime.now().time().strftime("%H:%M:%S")  + " - Bot has been stopped with following error: " + str(err), avatar_url=avatar)
    stop_bot.execute()
    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")  + " - Bot has been stopped with following error: " + str(err))

def bot_start():
    start_bot = DiscordWebhook(url=webhookurl, username=botname, content=datetime.datetime.now().time().strftime("%H:%M:%S")  + " - Bot has been started\n", avatar_url=avatar)
    start_bot.execute()
    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")  + " - Bot has been started\n")

def bot_send_message(message):
    send_message = DiscordWebhook(url=webhookurl, username=botname, content=message, avatar_url=avatar, rate_limit_retry=True)
    send_message.execute()
    print(message)

def main():

    j = journal.Reader()
    j.log_level(journal.LOG_INFO)

    j.add_match(_SYSTEMD_UNIT=systemd_unit) 
    j.seek_tail()
    j.get_previous()
    # j.get_next() # it seems this is not necessary.

    p = select.poll()
    p.register(j, j.get_events())

    message = ""

    try:

        bot_start() # message sent to server notifying we started

        while p.poll():

            if j.process() != journal.APPEND:
                continue

            # iterate over the entries from the journal to build the output. 
            for entry in j:
                if entry['MESSAGE'] != "":
                    message += str(entry['__REALTIME_TIMESTAMP'].strftime("%H:%M:%S")) + " - " + entry['MESSAGE'] + "\n"

            # add a divider for readability
            if message != "":
                message += "------------------------------------\n"
            
            #send the message to discord
            bot_send_message(message)
    
    # nothing fancy but lets you know if the bot craps out
    except Exception as e:
        bot_stop_err(e)


if __name__ == "__main__":
    main()
