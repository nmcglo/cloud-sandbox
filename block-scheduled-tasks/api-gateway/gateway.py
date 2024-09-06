from fastapi import FastAPI, HTTPException
import redis
from redis import Redis
import json
import logging
import os

logger = logging.getLogger('uvicorn.error')
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

app = FastAPI()
redis_client = Redis(host='redis', port=6379, db=0)

class SchedulerAPI:
    def __init__(self, redis_client: Redis, num_processors: int):
        self.redis_client = redis_client
        self.num_processors = num_processors
        self._initialize_processors()

    def _initialize_processors(self):
        # Ensure scheduler:next_task_id exists in Redis
        if not self.redis_client.exists('scheduler:next_task_id'):
            self.redis_client.set('scheduler:next_task_id', 0)
        # Initialize sorted sets for each processor with an empty task
        for i in range(self.num_processors):
            key = f"scheduler:processor_queue:{i}"
            if not self.redis_client.exists(key):
                self.redis_client.zadd(key, {json.dumps({"task_id": -1, "start_time": 0, "end_time": 0}): 0})  # Initialize as an empty sorted set

    def _find_earliest_start(self, duration: int):
        best_start_time = float('inf')
        best_processor = None

        for i in range(self.num_processors):
            key = f"scheduler:processor_queue:{i}"
            busy_intervals = self.redis_client.zrange(key, 0, -1, withscores=True)
            last_end_time = 0
            for task_json, _ in busy_intervals:
                task = json.loads(task_json)
                start_time = task['start_time']
                end_time = task['end_time']
                # Check if there is a gap between the last busy interval and the current one
                if start_time - last_end_time >= duration:
                    logger.debug(f"Found candidate fitting gap on processor {i} in range [{last_end_time}, {start_time}), new best start time: {last_end_time}")
                    best_start_time = last_end_time
                    best_processor = i
                    break
                else:
                    logger.debug(f"Did not find fitting gap on processor {i} in range [{last_end_time}, {start_time}), best start time: {best_start_time}")
                last_end_time = end_time
            
            # Check if the processor is idle after the last busy interval
            if last_end_time < best_start_time:
                best_start_time = last_end_time
                best_processor = i
                logger.debug(f"Found candidate idle gap on processor {i} in range [{last_end_time}, {last_end_time + duration}), new best start time: {best_start_time}")
            else:
                logger.debug(f"Did not find idle gap on processor {i} in range [{last_end_time}, {last_end_time + duration}), best start time: {best_start_time}")

        return best_processor, best_start_time

    def schedule_task(self, duration: int):
        while True:
            with self.redis_client.pipeline() as pipeline:
                try:
                    pipeline.watch('scheduler:next_task_id') #watch next task ID, if it changes then we need to retry
                    task_id = int(self.redis_client.get('scheduler:next_task_id') or 0)
                    processor, start_time = self._find_earliest_start(duration)

                    if processor is None:
                        pipeline.unwatch()
                        raise HTTPException(status_code=400, detail="No available slot found")

                    task = {
                        "task_id": task_id,
                        "start_time": start_time,
                        "end_time": start_time + duration
                    }

                    key = f"scheduler:processor_queue:{processor}"

                    pipeline.multi()
                    pipeline.zadd(key, {json.dumps(task): task['start_time']})  # Score is the start time
                    pipeline.incr('scheduler:next_task_id')
                    pipeline.execute()

                    return task_id, processor, start_time
                except redis.WatchError:
                    continue

scheduler_api = SchedulerAPI(redis_client, num_processors=4)

@app.post("/schedule")
def schedule_task(duration: int):
    try:
        task_id, processor, start_time = scheduler_api.schedule_task(duration)
        return {"task_id": task_id, "processor": processor, "start_time": start_time}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
def reset_scheduler():
    redis_client.flushdb()
    scheduler_api._initialize_processors()
    return {"message": "Scheduler reset"}