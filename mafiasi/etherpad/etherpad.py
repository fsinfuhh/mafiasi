from etherpad_lite import EtherpadLiteClient, EtherpadException
import time
from django.conf import settings

class Etherpad(object):
    def __init__(self):
        self.api = EtherpadLiteClient(
                    api_version='1.2.1',
                    base_url="%s://%s/api/" % (
                        settings.ETHERPAD_PROTOCOLL,
                        settings.ETHERPAD_DOMAIN),
                    base_params={'apikey': settings.ETHERPAD_API_KEY}
                )

    def __get_ep_user(self, user):
        return self.api.createAuthorIfNotExistsFor(
                        authorMapper=user.id,
                        name="%s (%s)" % (user.username, user.account),
                        )['authorID']

    def create_group_pad(self, group_name, pad_name):
        """
        Creates a Pad for Group
        """
        try:
            self.api.createGroupPad(
                groupID=self.get_group_id(group_name),
                padName=pad_name
                )
        except EtherpadException as e:
            # test if pas was already created, when its ok
            if e.message == "padName does already exist":
                return
            raise

    def create_session(self, user, group_name):
        group = self.get_group_id(group_name)
        user_ep = self.__get_ep_user(user)
        # first we delete old sessions
        activ_sessions = self.api.listSessionsOfGroup(groupID=group)
        if activ_sessions:
            for sessionID, data in activ_sessions.items():
                if data['authorID'] == user_ep:
                    if data['validUntil'] > time.time() + 60*60*6:
                        # There is a valid session with over 6 hours
                        # remaining time
                        return
                    else:
                        # we delete the old Session so the user has not two
                        # on the same group. (technickal no problem,
                        # but the cookies will have more data
                        self.api.deleteSession(sessionID=sessionID)
        # we create a new session
        self.api.createSession(
                        groupID = group,
                        authorID = user_ep,
                        validUntil = time.time() + 60*60*12,
                        )

    def get_session_cookie(self, user):
        sessions = self.api.listSessionsOfAuthor(
                        authorID= self.__get_ep_user(user)
                        )
        sessions_cookie = ""
        for sessionID in sessions.keys():
            sessions_cookie += sessionID + ","
        return sessions_cookie[:-1]  # letztes , entfernen

    def get_group_id(self, group_name):
        return self.api.createGroupIfNotExistsFor(
                groupMapper=group_name
                )["groupID"]

    def get_group_pads(self, group_name):
        try:
            return self.api.listPads(groupID=self.get_group_id(group_name))['padIDs']
        except EtherpadException as e:
            if e.message == "groupID does not exist":
                # es wurde einfach noch kein Pad in dieser Gruppe angelegt
                return []
            raise



