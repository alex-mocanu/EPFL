package template;

import java.util.List;

import uchicago.src.collection.Pair;

public class PlanNode {
	private State state;
	private double reward;
	private List<Pair> plan;
	
	public PlanNode(State state, double reward, List<Pair> plan) {
		this.state = state;
		this.reward = reward;
		this.plan = plan;
	}
	
	public State getState() {
		return state;
	}
	
	public double getReward() {
		return reward;
	}
	
	public List<Pair> getPlan() {
		return plan;
	}
}
