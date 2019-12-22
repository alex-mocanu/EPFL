import java.util.List;

import logist.agent.Agent;
import logist.plan.Action;
import logist.simulation.Vehicle;
import logist.task.Task;
import logist.task.TaskDistribution;
import logist.topology.Topology;
import logist.topology.Topology.City;

public class Policy {
  private final double defaultDiscount = 0.99;
  private final int maxNumIter = 1000;
  private final double changeThresh = 0.001;

  // Environment objects
  private TaskDistribution taskDist;
  private Agent agent;
  private double discount;
  List<City> cities;

  // Internal objects
  private double[][] reward;
  private double[][][] transition;
  private int numCities;
  private int numStates;
  private int numActions;
  private int numAvailableTasks;
  private int[] bestAction;

  public Policy(Topology topology, TaskDistribution td, Agent agent) {
    this.cities = topology.cities();
    this.taskDist = td;
    this.agent = agent;
    this.discount = agent.readProperty("discount-factor", Double.class, defaultDiscount);

    this.numCities = topology.size();
    // State -> (city, availableDelivery)
    // Action -> moveTo(city)/pickUp
    this.numAvailableTasks = numCities + 1;
    this.numStates = numCities * numAvailableTasks;
    this.numActions = numCities + 1;
    this.reward = new double[numStates][numActions];
    this.transition = new double[numStates][numActions][numStates];

    this.initEnvironment();
    bestAction = this.computeStrategy();
  }

  public Action getAction(Vehicle vehicle, Task availableTask) {
    int startCity = vehicle.getCurrentCity().id;
    int deliveryCity = numCities;
    if (availableTask != null)
      deliveryCity = availableTask.deliveryCity.id;
    
    int state = startCity * (numCities + 1) + deliveryCity;
    if (bestAction[state] < numCities)
      return new Action.Move(cities.get(bestAction[state]));
    return new Action.Pickup(availableTask);
  }

  private void initEnvironment() {
    int costPerKm = agent.vehicles().get(0).costPerKm();

    // Initialize the reward table
    for (int city = 0; city < numCities; ++city) {
      City cityObj = cities.get(city);
      for (int deliv = 0; deliv < numAvailableTasks; ++deliv) {
        int state = city * numAvailableTasks + deliv;
        // Move actions
        for (City nextCityObj : cityObj) {
          double delivCost = cityObj.distanceTo(nextCityObj) * costPerKm;
          int action = nextCityObj.id;
          reward[state][action] = -delivCost;
        }
          
        // Pick up action
        if (deliv < numCities) {
          City delivObj = cities.get(deliv);
          int delivReward = taskDist.reward(cityObj, delivObj);
          double delivCost = cityObj.distanceTo(delivObj) * costPerKm;
          int action = numCities;
          reward[state][action] = delivReward - delivCost;
        }
      }
    }
    
    // Initialize the transition table
    for (int currCity = 0; currCity < numCities; ++currCity)
      for (int currDeliv = 0; currDeliv < numAvailableTasks; ++currDeliv) {
        int currState = currCity * numAvailableTasks + currDeliv;
        // Move actions
        for (City nextCityObj : cities.get(currCity))
          for (int nextDeliv = 0; nextDeliv < numAvailableTasks; ++nextDeliv) {
            int nextState = nextCityObj.id * numAvailableTasks + nextDeliv;
            City nextDelivObj = (nextDeliv == numCities ? null : cities.get(nextDeliv));
            int action = nextCityObj.id;
            transition[currState][action][nextState] = taskDist.probability(nextCityObj, nextDelivObj);
          }
        
        // Pickup action
        if (currDeliv == numCities)
          continue;
        City nextCityObj = cities.get(currDeliv);
        for (int nextDeliv = 0; nextDeliv < numAvailableTasks; ++nextDeliv) {
          int nextState = currDeliv * numAvailableTasks + nextDeliv;     
          City nextDelivObj = (nextDeliv == numCities ? null : cities.get(nextDeliv));
          int action = numCities;
          transition[currState][action][nextState] = taskDist.probability(nextCityObj, nextDelivObj);
        }
      }
  }

  private int[] computeStrategy() {
    double[][] Q = new double[numStates][numActions];
    double[] V = new double[numStates];
    int[] bestAction = new int[numStates];

    for (int i = 0; i < maxNumIter; ++i) {
      boolean change = false;
      for (int state = 0; state < numStates; ++state) {
        double maxQ = -Double.MAX_VALUE;
        int bestAct = 0;
        for (int action = 0; action < numActions; ++action) {
          // Evaluate action only if it is valid
          if (!validAction(action, state))
            continue;

          double futureReturn = 0;
          for (int nextState = 0; nextState < numStates; ++nextState)
            futureReturn += transition[state][action][nextState] * V[nextState];
          Q[state][action] = reward[state][action] + discount * futureReturn;
          if (maxQ < Q[state][action]) {
            maxQ = Q[state][action];
            bestAct = action;
          }
        }
        double diff = Math.abs(maxQ - V[state]);
        V[state] = maxQ;
        bestAction[state] = bestAct;

        if (diff > changeThresh)
          change = true;
      }

      // If there was no significant change in the values, stop
      if (!change) {
        System.out.println("Value iteration converged after " + (i + 1) + " steps.");
        break;
      }
    }

    return bestAction;
  }

  private boolean validAction(int action, int state) {
    int city = state / numAvailableTasks;
    int deliv = state % numAvailableTasks;
    City cityObj = cities.get(city);

    // Pickup action
    if (action == numCities && (deliv == numCities || deliv == city))
      return false;
    // Move action
    if (action < numCities && !cityObj.hasNeighbor(cities.get(action)))
      return false;

    return true;
  }
}