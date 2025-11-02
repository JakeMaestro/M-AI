import asyncio, os, time, logging
import redis.asyncio as aioredis

log = logging.getLogger("leader")

class LeaderLock:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.key   = os.getenv("LOCK_KEY", "ari-leader")
        self.ttl   = int(os.getenv("LOCK_TTL", "15"))
        self.renew = int(os.getenv("LOCK_RENEW", "5"))
        self._is_leader = False
        self._stop = False
        self._task = None
        self._client = None

    async def start(self):
        self._client = aioredis.from_url(self.redis_url)
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._stop = True
        if self._task:
            self._task.cancel()
        if self._client:
            try:
                await self._client.close()
            except Exception:
                try:
                    await self._client.connection_pool.disconnect()
                except Exception:
                    pass

    async def _loop(self):
        while not self._stop:
            try:
                now = str(time.time())
                ok = await self._client.set(self.key, now, ex=self.ttl, nx=True)
                if ok:
                    if not self._is_leader:
                        log.info("Acquired leader lock")
                    self._is_leader = True
                elif self._is_leader:
                    ttl = await self._client.ttl(self.key)
                    if ttl and ttl < self.renew:
                        await self._client.expire(self.key, self.ttl)
                else:
                    self._is_leader = False
                await asyncio.sleep(self.renew)
            except Exception as e:
                log.warning(f"Leader loop error: {e}")
                await asyncio.sleep(3)

    @property
    def is_leader(self):
        return self._is_leader
