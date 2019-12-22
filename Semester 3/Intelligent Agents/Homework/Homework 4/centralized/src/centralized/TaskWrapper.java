package centralized;

import logist.task.Task;

/**
 * Wrapper class incorporating a Task object and the type of action to perform
 * with it
 */
public class TaskWrapper {
    public enum ActionType {
        PICKUP, DELIVER, NULL
    }

    private Task task;
    private ActionType action;

    public TaskWrapper(Task task, ActionType action) {
        this.task = task;
        this.action = action;
    }

    public Task getTask() {
        return task;
    }

    public ActionType getAction() {
        return action;
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof TaskWrapper))
            return false;
        
        TaskWrapper t = (TaskWrapper)obj;
        return this.task == t.task && this.action == t.action;
    }

    @Override
    public int hashCode() {
        int hash = task.id;
        if (action == ActionType.DELIVER)
            hash += 1 << 30;
        return hash;
    }
}