from colorama import Fore, Style, init

DEBUG=False

class PriorityList:
    def __init__(self, key=lambda x: x):
        self._list = []
        self._key = key

    def insert(self, item):
        key = self._key(item)
        # Start at the end of the list and move backwards to find the correct position
        i = len(self._list) - 1
        while i >= 0 and self._key(self._list[i]) > key:
            i -= 1
        # Insert the item after the found position (or at the start if not found)
        self._list.insert(i + 1, item)

    def __repr__(self):
        return repr(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index):
        return self._list[index]

    def __iter__(self):
        return iter(self._list)

class OnlineScheduler:
    def __init__(self, num_processors):
        self.processors = [PriorityList(key=lambda x: x[1]) for _ in range(num_processors)]  # Each processor has a list of busy intervals
        self.next_task_id = 0
        self.task_to_processor_map = {}
    
    def _find_earliest_start(self, duration):
        cur_task_id = self.next_task_id
        if DEBUG:
            print(f"Scheduling task {cur_task_id} with duration {duration}")
        self.next_task_id += 1
        
        ## Find the earliest available time on any processor that can fit the task, fit in gaps if possible
        best_start_time = float('inf')
        best_processor = None
        for i in range(len(self.processors)):
            last_end_time = 0
            for task_id, start_time, end_time in self.processors[i]:
                if start_time - last_end_time >= duration:
                    if DEBUG:
                        print(f"Found fitting gap on processor {i} in range [{last_end_time}, {start_time})")
                    best_start_time = last_end_time
                    best_processor = i
                    break
                last_end_time = end_time
            if last_end_time < best_start_time:
                best_start_time = last_end_time
                best_processor = i
        
        self.task_to_processor_map[cur_task_id] = best_processor
        return cur_task_id, best_processor, best_start_time
    
    def schedule_task(self, duration, print_gantt=False):
        task_id, processor, start_time = self._find_earliest_start(duration)
        if processor is not None:
            self.processors[processor].insert((task_id, start_time, start_time + duration))
            if DEBUG or print_gantt:
                self.print_gantt_chart()
            return task_id, processor, start_time
        return None, None, None
    
    def complete_task_early(self, task_id, actual_duration, print_gantt=False):
        if DEBUG:
            print(f"Task {task_id} completed early with actual duration {actual_duration}")
        processor = self.task_to_processor_map[task_id]
        start_time = [st for tid, st, _ in self.processors[processor] if tid == task_id][0]
        actual_end_time = start_time + actual_duration
        
        # Find and update the task interval on the processor
        updated_intervals = PriorityList(key=lambda x: x[1])
        for interval in self.processors[processor]:
            if interval[0] == task_id:
                if DEBUG:
                    print(f"Updating interval {interval} to ({start_time}, {actual_end_time})")
                updated_intervals.insert((task_id, start_time, actual_end_time))
            else:
                if DEBUG:
                    print(f"Keeping interval {interval}")
                updated_intervals.insert(interval)
        self.processors[processor] = updated_intervals
        
        if DEBUG or print_gantt:
            self.print_gantt_chart()

    def print_gantt_chart(self):
        total_time = max(end for processor in self.processors for _, _, end in processor)
        print("--- Gantt Chart ---")
        for i in range(len(self.processors)):
            chart = [" "] * total_time
            for task_id, start, end in self.processors[i]:
                for j in range(start, end):
                    if j < total_time:
                        chart[j] = f"{task_id}"
            print(f"Processor {i}: {''.join(chart)}")


def run_tests():
    test_cases = [
        {
            "description": "Simple case with one resource",
            "resources": 1,
            "task_durations": [2, 3, 1, 2],
            "task_terminations": [],
            "new_task_duration": 1,
            "expected_new_task_start": 8
        },
        {
            "description": "Simple case with two resources",
            "resources": 2,
            "task_durations": [2, 3, 1, 2],
            "task_terminations": [],
            "new_task_duration": 1,
            "expected_new_task_start": 3
        },
        {
            "description": "Simple case with three resources",
            "resources": 3,
            "task_durations": [2, 3, 1, 2],
            "task_terminations": [],
            "new_task_duration": 1,
            "expected_new_task_start": 2
        },
        {
            "description": "Task can fill a gap on a single resource",
            "resources": 1,
            "task_durations": [2, 3, 1, 2],
            "task_terminations": [(1,1)],
            "new_task_duration": 1,
            "expected_new_task_start": 3
        },
        {
            "description": "Task can fill a gap on multiple resources",
            "resources": 3,
            "task_durations": [2, 3, 1, 2],
            "task_terminations": [(1,1)],
            "new_task_duration": 1,
            "expected_new_task_start": 1
        },
        {
            "description": "Task can't fill in a gap",
            "resources": 2,
            "task_durations": [2, 3, 6, 2],
            "task_terminations": [(1,1)],
            "new_task_duration": 6,
            "expected_new_task_start": 5
        }
    ]
    
    passed_tests = 0
    failed_tests = 0
    for test_case in test_cases:
        try:
            scheduler = OnlineScheduler(num_processors=test_case["resources"])
            for duration in test_case["task_durations"]:
                scheduler.schedule_task(duration)
            for task_id, actual_duration in test_case["task_terminations"]:
                scheduler.complete_task_early(task_id, actual_duration)
            
            task_id, processor, start_time = scheduler.schedule_task(test_case["new_task_duration"])
            assert start_time == test_case["expected_new_task_start"]
            print(f"{Fore.GREEN}Test case passed: {test_case['description']}{Style.RESET_ALL}")
            passed_tests += 1
        except AssertionError:
            print(f"{Fore.RED}Test case failed: {test_case['description']}, expected start time: {test_case['expected_new_task_start']}, got: {start_time}{Style.RESET_ALL}")
            failed_tests += 1
    
    print(f"Tests passed: {passed_tests}/{len(test_cases)}, Tests failed: {failed_tests}/{len(test_cases)}")
    if failed_tests == 0:
        print(f"{Fore.GREEN}All tests passed!{Style.RESET_ALL}")

if __name__ == "__main__":
    run_tests()
