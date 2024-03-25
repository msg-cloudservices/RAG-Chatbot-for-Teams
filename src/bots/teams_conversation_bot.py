# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import TurnContext, MessageFactory
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from rag.rag_with_history import generate_answer
import logging

ADAPTIVECARDTEMPLATE = "resources/UserMentionCardTemplate.json"

class TeamsConversationBot(TeamsActivityHandler):
    def __init__(self, app_id: str, app_password: str):
        self._app_id = app_id
        self._app_password = app_password

    async def on_teams_members_added(  # pylint: disable=unused-argument
        self,
        teams_members_added: [TeamsChannelAccount],
        team_info: TeamInfo,
        turn_context: TurnContext,
    ):
        for member in teams_members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome to the team { member.given_name } { member.surname }. "
                )

    async def on_message_activity(self, turn_context: TurnContext):
        TurnContext.remove_recipient_mention(turn_context.activity)
        try:
            prompt = turn_context.activity.text.strip()
        except Exception as e:
            # No text attribute, e.g. if only emojis are sent
            # TODO: Emoji handling
            logging.warn(f"Could not read any text from received message. Error: {e}")
            await turn_context.send_activity(MessageFactory.text("Hallo, wie kann ich weiterhelfen?"))
            return

        conversation_id = turn_context.activity.conversation.id
        logging.info(f"Prompt is: {prompt}")
        
        response = generate_answer(prompt, conversation_id)
        await turn_context.send_activity(
            MessageFactory.text(response)
        )
        return