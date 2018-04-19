# TODO

'''
class LiveGuildMembersAudited(LiveGuildMembers):

    def __init__(self):
        self.audit_kick_stack = AuditStackKicks(self.client_bind, self.guild_id)
        self.audit_ban_add_stack = AuditStackBanAdd(self.client_bind, self.guild_id)
        self.invite_stack = InviteStack(self.client_bind, self.guild_id)
        self.queue_dispenser = QueueDispenser(('ADD', 'UPDATE', 'SELF-LEAVE', 'BAN', 'KICK'))


    async def on_guild_member_self_leave(self) -> typing.AsyncGenerator[GuildMember, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'SELF-LEAVE')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_update(self) -> typing.AsyncGenerator[GuildMember, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'UPDATE')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_kicked(self) -> typing.AsyncGenerator[typing.Tuple[GuildMember, AuditKick], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'KICK')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_banned(self) -> typing.AsyncGenerator[typing.Tuple[GuildMember, AuditBanAdd], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'BAN')
        while True:
            yield (await queue.get())[0]
'''