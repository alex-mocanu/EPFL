import logist.simulation.Vehicle;
import logist.agent.Agent;
import logist.behavior.ReactiveBehavior;
import logist.plan.Action;
import logist.task.Task;
import logist.task.TaskDistribution;
import logist.topology.Topology;

public class Reactive implements ReactiveBehavior {
	private int numActions;
	private Agent myAgent;
	private Policy policy; // determines the strategy of the agent

	@Override
	public void setup(Topology topology, TaskDistribution td, Agent agent) {
		this.policy = new Policy(topology, td, agent);
		this.numActions = 0;
		this.myAgent = agent;
	}

	@Override
	public Action act(Vehicle vehicle, Task availableTask) {
		if (numActions >= 1) {
			System.out.println(
				"The total profit after " + numActions + " actions is "
				+ myAgent.getTotalProfit() + " (average profit: "
				+ (myAgent.getTotalProfit() / (double)numActions) + ")"
			);
		}
		numActions++;
		
		return policy.getAction(vehicle, availableTask);
	}
}
