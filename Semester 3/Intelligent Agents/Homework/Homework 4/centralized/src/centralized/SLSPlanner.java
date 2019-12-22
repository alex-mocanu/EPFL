package centralized;

import java.util.List;
import java.util.Random;

import logist.plan.Plan;
import logist.simulation.Vehicle;
import logist.task.Task;
import logist.task.TaskSet;

/**
 * Class used for implementing the SLS planner
 */
public class SLSPlanner {
    private List<Vehicle> vehicles;
    private TaskSet tasks;
    private int maxIter;
    private final double greedyProb = 0.3;

    public SLSPlanner(List<Vehicle> vehicles, TaskSet tasks, int maxIter) {
        this.vehicles = vehicles;
        this.tasks = tasks;
        this.maxIter = maxIter;
    }

    public List<Plan> SLS() {
        SLSPlan plan = initialPlan();
        int iter = 0;

        // Search for a close to optimal plan
        SLSPlan bestPlan = plan;
        while(iter < maxIter) {
            List<SLSPlanChange> neighbors = plan.neighborPlans();
            SLSPlanChange bestPlanChange = localChoice(neighbors);
            double posChange = 0;
            // Test if the new plan is better than the previous one
            if (plan.evaluateChange(bestPlanChange) <= 0)
                if (Math.random() <= greedyProb) {
                    posChange += plan.evaluateChange(bestPlanChange);
                    posChange = Math.max(posChange, 0);
                    plan.executeChange(bestPlanChange);
                    if (posChange == 0)
                        bestPlan = plan;
                } else
                    posChange += plan.evaluateChange(bestPlanChange);
            ++iter;
        }

        // Generate the plans for each vehicle
        return bestPlan.generatePlans(vehicles);
    }

    private SLSPlan initialPlan() {
        SLSPlan initPlan = new SLSPlan();
        Vehicle largestVehicle = vehicles.get(0);

        // Initialize vehicles in plan
        initPlan.initVehicle(vehicles.get(0));
        // Find the largest vehicle
        for (int i = 1; i < vehicles.size(); ++i) {
            initPlan.initVehicle(vehicles.get(i));
            if (largestVehicle.capacity() < vehicles.get(i).capacity())
                largestVehicle = vehicles.get(i);
        }
        // Allocate all tasks to the largest vehicle
        for (Task t : tasks)
            if (!initPlan.addTaskToVehicle(largestVehicle, t))
                return null;

        return initPlan;
    }

    private SLSPlanChange localChoice(List<SLSPlanChange> plans) {
        Random rand = new Random();
        
        // Choose one element at random
        return plans.get(rand.nextInt(plans.size()));
    }
}