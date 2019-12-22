package centralized;

import logist.simulation.Vehicle;

/**
 * Class used for representing a change in the plan, used
 * when looking for neighbor plans
 */
public class SLSPlanChange {
    public enum ChangeType {
        MOVE, EXCHANGE
    }

    private TaskWrapper t1, t2;
    private Vehicle v1, v2;
    private TaskWrapper moveTask;
    private ChangeType type;

    public SLSPlanChange(Vehicle v1, Vehicle v2, TaskWrapper moveTask) {
        this.v1 = v1;
        this.v2 = v2;
        this.moveTask = moveTask;
        this.type = ChangeType.MOVE;
    }

    public SLSPlanChange(TaskWrapper t1, TaskWrapper t2) {
        this.t1 = t1;
        this.t2 = t2;
        this.type = ChangeType.EXCHANGE;
    }

    public ChangeType getType() {
        return type;
    }

    public TaskWrapper[] getTasks() {
        return new TaskWrapper[]{t1, t2};
    }

    public Vehicle[] getVehicles() {
        return new Vehicle[]{v1, v2};
    }

    public TaskWrapper getMoveTask() {
        return moveTask;
    }
}