from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *

@register(
    name="群友ID获取", 
    description="获取群聊对话中的ID给大模型", 
    version="1.0", 
    author="小馄饨"
)
class UserIDPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        self.host = host
    
    async def initialize(self):
        pass

    @handler(GroupNormalMessageReceived)
    async def handle_group_message(self, ctx: EventContext):
        try:
            msg = ctx.event.text_message
            if not msg:
                return

            sender_name = "Unknown"
            if hasattr(ctx.event, 'query') and hasattr(ctx.event.query, 'message_event'):
                message_event = ctx.event.query.message_event
                if hasattr(message_event, 'sender') and hasattr(message_event.sender, 'member_name'):
                    sender_name = message_event.sender.member_name

            modified_msg = f"群友 {sender_name} 说：{msg}"
            
            # Print modified message to console
            print(f"Modified message: {modified_msg}")
            
            if hasattr(ctx.event, 'query'):
                if hasattr(ctx.event.query, 'user_message'):
                    if isinstance(ctx.event.query.user_message.content, list):
                        for content in ctx.event.query.user_message.content:
                            if hasattr(content, 'text'):
                                content.text = modified_msg
                    else:
                        ctx.event.query.user_message.content = modified_msg

                if hasattr(ctx.event.query, 'session') and hasattr(ctx.event.query.session, 'using_conversation'):
                    conversation = ctx.event.query.session.using_conversation
                    if hasattr(conversation, 'messages') and conversation.messages:
                        last_message = conversation.messages[-1]
                        if hasattr(last_message, 'content'):
                            last_message.content = modified_msg

        except Exception:
            pass

    def __del__(self):
        pass 
