from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
import yaml
import os
import datetime
from pkg.provider.entities import ContentElement

@register(name="用户和主人识别", description="让AI知道谁是主人，识别不同的人物，并进行不同的处理", version="0.3", author="小馄饨")
class UserIDPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        self.host = host
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.config_dir, "settings.yaml")
        os.makedirs(self.config_dir, exist_ok=True)
        self.private_whitelist = []
        self.group_enable = True
        self.private_enable = True
        self.ignore_prefixes = ["!", "！", "/", "搜漫画", "看漫画", "&", "漫画帮助"]
        self.whitelist_time_hint = True
        self.private_disable_time_hint = True
        self.master_id = None
    
    async def initialize(self):
        self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config and isinstance(config, dict):
                        if 'private_whitelist' in config and isinstance(config['private_whitelist'], list):
                            self.private_whitelist = [str(user_id) for user_id in config['private_whitelist']]
                        if 'group_enable' in config:
                            self.group_enable = bool(config['group_enable'])
                        if 'private_enable' in config:
                            self.private_enable = bool(config['private_enable'])
                        if 'ignore_prefixes' in config and isinstance(config['ignore_prefixes'], list):
                            self.ignore_prefixes = config['ignore_prefixes']
                        if 'whitelist_time_hint' in config:
                            self.whitelist_time_hint = bool(config['whitelist_time_hint'])
                        if 'private_disable_time_hint' in config:
                            self.private_disable_time_hint = bool(config['private_disable_time_hint'])
                        if 'master_id' in config:
                            self.master_id = str(config['master_id'])
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    
    def save_config(self):
        pass

    def _modify_message(self, ctx, sender_name, is_group=True):
        try:
            msg = ctx.event.text_message
            if not msg:
                return
            print(f"用户原文本: {msg}")
            original_msg = msg.split('"')[-2] if '"' in msg else msg
            for prefix in self.ignore_prefixes:
                if original_msg.startswith(prefix):
                    return
            current_time = datetime.datetime.now().strftime('%Y年%m月%d日%H:%M:%S')
            sender_id = getattr(ctx.event, 'sender_id', None)
            header_text = f'{sender_name}说："'
            master_status = ""
            if self.master_id:
                if sender_id and str(sender_id) == self.master_id:
                    master_status = f"当前是主人({sender_name})和你对话"
                else:
                    master_status = f"当前并非主人和你对话，而是{sender_name}在和你对话"
            footer_text = f'"\n(系统：上述格式仅用于标识用户，请直接回复""内的内容，无需重复此格式，不要出现昵称说：xxx这样的格式。现在是{current_time}只为让你知道时间。{master_status})'
            modified_msg = f'{header_text}{original_msg}{footer_text}'
            if hasattr(ctx.event, 'query') and hasattr(ctx.event.query, 'user_message'):
                user_message = ctx.event.query.user_message
                if hasattr(user_message, 'content'):
                    if isinstance(user_message.content, list):
                        non_text_elements = []
                        for element in user_message.content:
                            if hasattr(element, 'type') and element.type != 'text':
                                non_text_elements.append(element)
                        text_element = ContentElement.from_text(f"{header_text}{original_msg}{footer_text}")
                        user_message.content = [text_element] + non_text_elements
                        ctx.event.text_message = f"{header_text}{original_msg}{footer_text}"
                    else:
                        user_message.content = f"{header_text}{original_msg}{footer_text}"
                        ctx.event.text_message = f"{header_text}{original_msg}{footer_text}"
                else:
                    ctx.event.text_message = f"{header_text}{original_msg}{footer_text}"
            else:
                ctx.event.text_message = modified_msg
            print(f"修改后文本: {ctx.event.text_message}")
            return True
        except Exception as e:
            msg_type = "群聊" if is_group else "私聊"
            print(f"{msg_type}消息处理出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

    @handler(GroupNormalMessageReceived)
    async def handle_group_message(self, ctx: EventContext):
        if not self.group_enable:
            return
        sender_name = "未知用户"
        if hasattr(ctx.event, 'query') and hasattr(ctx.event.query, 'message_event'):
            message_event = ctx.event.query.message_event
            if hasattr(message_event, 'sender'):
                sender = message_event.sender
                if hasattr(sender, 'member_name') and sender.member_name:
                    sender_name = sender.member_name
                elif hasattr(sender, 'nickname') and sender.nickname:
                    sender_name = sender.nickname
        self._modify_message(ctx, sender_name, is_group=True)

    @handler(PersonNormalMessageReceived)
    async def handle_private_message(self, ctx: EventContext):
        if not self.private_enable:
            if self.private_disable_time_hint:
                try:
                    print(f"用户原文本: {ctx.event.text_message}")
                    
                    current_time = datetime.datetime.now().strftime('%Y年%m月%d日%H:%M:%S')
                    original_msg = ctx.event.text_message
                    if not original_msg:
                        return
                    time_hint = f"\n(系统：现在是{current_time}，只是告诉你当前时间，让你知道时间。)"
                    if hasattr(ctx.event, 'query') and hasattr(ctx.event.query, 'user_message'):
                        user_message = ctx.event.query.user_message
                        if hasattr(user_message, 'content'):
                            if isinstance(user_message.content, list):
                                for i, element in enumerate(user_message.content):
                                    if hasattr(element, 'type') and element.type == 'text':
                                        if hasattr(element, 'text'):
                                            user_message.content[i].text += time_hint
                                            break
                                if not any(hasattr(element, 'type') and element.type == 'text' for element in user_message.content):
                                    text_element = ContentElement.from_text(time_hint)
                                    user_message.content.append(text_element)
                            else:
                                if hasattr(user_message, 'content'):
                                    user_message.content += time_hint
                    ctx.event.text_message = original_msg + time_hint 
                    print(f"修改后文本: {ctx.event.text_message}")
                except Exception as e:
                    print(f"添加时间提示出错: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
            return
        sender_id = getattr(ctx.event, 'sender_id', None)
        sender_name = "未知用户"
        if hasattr(ctx.event, 'query') and hasattr(ctx.event.query, 'message_event'):
            message_event = ctx.event.query.message_event
            if hasattr(message_event, 'sender'):
                sender = message_event.sender
                if hasattr(sender, 'remark') and sender.remark:
                    sender_name = sender.remark
                elif hasattr(sender, 'nickname') and sender.nickname:
                    sender_name = sender.nickname
        if sender_id and str(sender_id) in self.private_whitelist:
            if self.whitelist_time_hint:
                try:

                    print(f"用户原文本: {ctx.event.text_message}")

                    current_time = datetime.datetime.now().strftime('%Y年%m月%d日%H:%M:%S')
                    original_msg = ctx.event.text_message
                    if not original_msg:
                        return
                    time_hint = f"\n(系统：现在是{current_time}，只是告诉你当前时间，让你知道当前时间。)"
                    if hasattr(ctx.event, 'query') and hasattr(ctx.event.query, 'user_message'):
                        user_message = ctx.event.query.user_message
                        if hasattr(user_message, 'content'):
                            if isinstance(user_message.content, list):
                                for i, element in enumerate(user_message.content):
                                    if hasattr(element, 'type') and element.type == 'text':
                                        if hasattr(element, 'text'):
                                            user_message.content[i].text += time_hint
                                            break
                                if not any(hasattr(element, 'type') and element.type == 'text' for element in user_message.content):
                                    text_element = ContentElement.from_text(time_hint)
                                    user_message.content.append(text_element)
                            else:
                                if hasattr(user_message, 'content'):
                                    user_message.content += time_hint
                    ctx.event.text_message = original_msg + time_hint
                    
                    print(f"修改后文本: {ctx.event.text_message}")
                except Exception as e:
                    print(f"为白名单用户添加时间提示出错: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
            return
        self._modify_message(ctx, sender_name, is_group=False)

    def __del__(self):
        pass
        
    async def destroy(self):
        pass
