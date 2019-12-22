package template;

import java.util.Hashtable;

import logist.plan.Plan;
import logist.task.Task;
import logist.task.TaskDistribution;
import logist.topology.Topology;

abstract public class Planner {
	protected enum ActionType {PICKUP, DELIVER};
	
	protected Topology topology;
	protected TaskDistribution td;
	protected int capacity;
	protected Hashtable<State, Double> stateValue;
	protected double costPerKm;
	
	public Planner(Topology topology, TaskDistribution td, int capacity, double costPerKm) {
		this.topology = topology;
		this.td = td;
		this.stateValue = new Hashtable<State, Double>();
		this.capacity = capacity;
		this.costPerKm = costPerKm;
	}
	
	abstract public Plan generatePlan(State state);
	
	protected boolean isActionValid(State state, Task task, ActionType action) {
		// Deliver action
		if (action == ActionType.DELIVER)
			return state.isInTasksOnBoard(task);
		
		// Pick-up action
		return state.isInTasksToPickUp(task) && state.getSize() + task.weight <= capacity;
	}
}
