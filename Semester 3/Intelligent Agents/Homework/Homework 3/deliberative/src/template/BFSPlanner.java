package template;

import java.util.List;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Queue;

import logist.plan.Plan;
import logist.task.Task;
import logist.task.TaskDistribution;
import logist.task.TaskSet;
import logist.topology.Topology;
import logist.topology.Topology.City;
import uchicago.src.collection.Pair;

public class BFSPlanner extends Planner {
	public BFSPlanner(Topology topology, TaskDistribution td, int capacity, double costPerKm) {
		super(topology, td, capacity, costPerKm);
	}

	@Override
	public Plan generatePlan(State state) {
		stateValue.put(state, 0.0);
		Queue<PlanNode> stateQueue = new LinkedList<PlanNode>();
		Plan plan = new Plan(state.getCurrentCity());
		
		stateQueue.add(new PlanNode(state, 0, new ArrayList<Pair>()));
		ArrayList<PlanNode> optimalPlan = null;
		double bestReward = -Double.MAX_VALUE;
		while (!stateQueue.isEmpty()) {
			PlanNode node = stateQueue.poll();
			State currState = node.getState();
			double currReward = node.getReward();
			
			// Consider the pick-up actions
			for (Task task : currState.getTasksToPickUp()) {
				// Check if action is valid
				if (!isActionValid(currState, task, ActionType.PICKUP))
					continue;
				
				// Compute the cost of the move
				City nextCity = task.pickupCity;
				double moveCost = currState.getCurrentCity().distanceTo(nextCity) * costPerKm;
				double nextReward = currReward - moveCost;
				
				// Generate next state
				TaskSet nextTasksToPickUp = currState.getTasksToPickUp().clone();
				nextTasksToPickUp.remove(task);
				TaskSet nextTasksOnBoard = currState.getTasksOnBoard().clone();
				nextTasksOnBoard.add(task);
				State nextState = new State(nextCity, nextTasksToPickUp, nextTasksOnBoard);
				
				// Check if this state was visited
				if (stateValue.contains(nextState)) {
					// Check if the reward is improved
					if (stateValue.get(nextState) >= currReward)
						continue;
				}
				
				// Add a new node to the planning tree
				stateValue.put(nextState, nextReward);
				ArrayList<Pair> nextPlan = new ArrayList<Pair>(node.getPlan());
				nextPlan.add(new Pair(nextCity, ActionType.PICKUP));
				stateValue.put(nextState, nextReward);
				stateQueue.add(new PlanNode(nextState, nextReward, nextPlan));
			}
			
			// Consider the deliver actions
			for (Task task : currState.getTasksOnBoard()) {
				// Check if action is valid
				if (!isActionValid(currState, task, ActionType.PICKUP))
					continue;
				
				// Compute the cost of the move
				City nextCity = task.deliveryCity;
				double moveCost = currState.getCurrentCity().distanceTo(nextCity) * costPerKm;
				double nextReward = currReward + td.reward(task.pickupCity, nextCity) - moveCost;
				
				// Generate next state
				TaskSet nextTasksToPickUp = currState.getTasksToPickUp().clone();
				TaskSet nextTasksOnBoard = currState.getTasksOnBoard().clone();
				nextTasksOnBoard.remove(task);
				State nextState = new State(nextCity, nextTasksToPickUp, nextTasksOnBoard);
				
				// Check if this state was visited
				if (stateValue.contains(nextState)) {
					// Check if the reward is improved
					if (stateValue.get(nextState) >= currReward)
						continue;
				}
				
				// Add a new node to the planning tree
				stateValue.put(nextState, nextReward);
				ArrayList<Pair> nextPlan = new ArrayList<Pair>(node.getPlan());
				nextPlan.add(new Pair(nextCity, ActionType.DELIVER));
				stateValue.put(nextState, nextReward);
				stateQueue.add(new PlanNode(nextState, nextReward, nextPlan));
			}
		}
		
		return buildPlan(state.getCurrentCity(), optimalPlan);
	}
	
	private Plan buildPlan(City initCity, List<Pair> optimalPlan) {
		Plan plan = new Plan(initCity);
		
		for (Pair node : optimalPlan) {
			City nextCity = (City)node.first;
			ActionType action = (ActionType)node.second;
			
			
		}
		
		return plan;
	}
}
