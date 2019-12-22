package template;

import logist.plan.Plan;
import logist.task.TaskDistribution;
import logist.topology.Topology;

public class AStarPlanner extends Planner {
	public AStarPlanner(Topology topology, TaskDistribution td, int capacity, double costPerKm) {
		super(topology, td, capacity, costPerKm);
	}

	@Override
	public Plan generatePlan(State state) {
		// Not implemented
		throw new UnsupportedOperationException();
	}
}
