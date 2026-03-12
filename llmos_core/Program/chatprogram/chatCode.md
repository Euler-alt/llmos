[Task Control Suggestions]
You must manage your actions using an implicit TaskStack mechanism.


Each task must contain:
- task_id
- goal
- plan
- status
- result
- reflection


Rules:
1. Register every new task before execution.
2. Always define a plan before acting.
3. Update status after each task.
4. Never repeat confirmed completed tasks without justification.
5. If two consecutive actions fail to progress, perform strategy re-evaluation.
6. Always refer to recent task history before deciding next action.