package centralized;

import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;
import java.util.Random;

import centralized.SLSPlanChange.ChangeType;
import centralized.TaskWrapper.ActionType;
import logist.plan.Plan;
import logist.simulation.Vehicle;
import logist.task.Task;
import logist.topology.Topology.City;

/**
 * Class that manages the variables and is used for representing
 * a plan
 */
public class SLSPlan {
    private Hashtable<Vehicle, TaskWrapper> nextTaskV;
    private Hashtable<TaskWrapper, TaskWrapper> nextTaskT;
    private Hashtable<Vehicle, Integer> spaceV;
    private Hashtable<TaskWrapper, Integer> spaceT;
    private Hashtable<TaskWrapper, Integer> time;
    private Hashtable<TaskWrapper, Vehicle> vehicle;

    public SLSPlan() {
        nextTaskV = new Hashtable<Vehicle, TaskWrapper>();
        nextTaskT = new Hashtable<TaskWrapper, TaskWrapper>();
        spaceV = new Hashtable<Vehicle, Integer>();
        spaceT = new Hashtable<TaskWrapper, Integer>();
        time = new Hashtable<TaskWrapper, Integer>();
        vehicle = new Hashtable<TaskWrapper, Vehicle>();
    }

    public void initVehicle(Vehicle v) {
        nextTaskV.put(v, new TaskWrapper(null, ActionType.NULL));
        spaceV.put(v, v.capacity());
    }

    public boolean addTaskToVehicle(Vehicle v, Task t) {
        // Create PICKUP and DELIVERY subtasks
        TaskWrapper pickupTask = new TaskWrapper(t, ActionType.PICKUP);
        TaskWrapper deliverTask = new TaskWrapper(t, ActionType.DELIVER);

        // Prepare the link between pickup and deliver
        nextTaskT.put(pickupTask, deliverTask);
        nextTaskT.put(deliverTask, new TaskWrapper(null, ActionType.NULL));
        spaceT.put(pickupTask, spaceV.get(v) - t.weight);
        spaceT.put(deliverTask, spaceV.get(v));

        // Go to the end of the vehicle's list and add the subtasks
        if (nextTaskV.get(v).getAction() == ActionType.NULL) {
            // Can not add task to the vehicle if it is too large
            if (spaceV.get(v) < t.weight)
                return false;
            nextTaskV.put(v, pickupTask);
            time.put(pickupTask, 0);
            time.put(deliverTask, 1);
        } else {
            TaskWrapper endTask = nextTaskV.get(v);
            while (nextTaskT.get(endTask).getAction() != ActionType.NULL)
                endTask = nextTaskT.get(endTask);
            // Can not add task to the vehicle if it is too large
            if (spaceT.get(endTask) < t.weight)
                return false;
            nextTaskT.put(endTask, pickupTask);
            time.put(pickupTask, time.get(endTask) + 1);
            time.put(deliverTask, time.get(endTask) + 2);
        }
        // Associate the subtasks with the vehicle
        vehicle.put(pickupTask, v);
        vehicle.put(deliverTask, v);

        return true;
    }

    public List<SLSPlanChange> neighborPlans() {
        List<SLSPlanChange> plans = new ArrayList<SLSPlanChange>();
        Random rand = new Random();
        List<Vehicle> activeVehicles = new ArrayList<Vehicle>();

        // Choose one of the vehicles with tasks
        for (Vehicle v : nextTaskV.keySet())
            if (nextTaskV.get(v).getAction() != ActionType.NULL)
                activeVehicles.add(v);
        Vehicle v = activeVehicles.get(rand.nextInt(activeVehicles.size()));

        addMoveChanges(v, plans);
        addExchangeChanges(v, plans);

        return plans;
    }

    public double evaluateChange(SLSPlanChange change) {
        if (change.getType() == ChangeType.MOVE)
            return evaluateMove(change.getVehicles(), change.getMoveTask());
        return evaluateExchange(change.getTasks());
    }

    public void executeChange(SLSPlanChange change) {
        if (change.getType() == ChangeType.MOVE)
            executeMove(change.getVehicles(), change.getMoveTask());
        else
            executeExchange(change.getTasks());
    }

    public List<Plan> generatePlans(List<Vehicle> vehicles) {
        List<Plan> vehiclePlans = new ArrayList<Plan>();
        int cnt;
        // Generate the plan for each vehicle
        for (Vehicle v : vehicles) {
            cnt = 0;
            TaskWrapper task = nextTaskV.get(v);
            City currCity = v.getCurrentCity(), nextCity;
            Plan plan = new Plan(currCity);

            if (task.getAction() == ActionType.NULL)
                plan = Plan.EMPTY;
            // Go through all the tasks
            while (task.getAction() != ActionType.NULL) {
                if (task.getAction() == ActionType.PICKUP) {
                    ++cnt;
                    nextCity = task.getTask().pickupCity;
                    for (City city : currCity.pathTo(nextCity))
                        plan.appendMove(city);
                    plan.appendPickup(task.getTask());
                } else {
                    nextCity = task.getTask().deliveryCity;
                    for (City city : currCity.pathTo(nextCity))
                        plan.appendMove(city);
                    plan.appendDelivery(task.getTask());
                }
                currCity = nextCity;
                task = nextTaskT.get(task);
            }
            System.out.println(cnt);
            vehiclePlans.add(plan);
        }

        return vehiclePlans;
    }

    private void addMoveChanges(Vehicle v, List<SLSPlanChange> plans) {
        double bestCost = (plans.isEmpty() ? Double.MAX_VALUE : evaluateChange(plans.get(0)));

        for (Vehicle vToMove : nextTaskV.keySet()) {
            if (v.equals(vToMove))
                continue;
            // Look for pickup tasks
            TaskWrapper task = nextTaskV.get(v);
            while (task.getAction() != ActionType.NULL) {
                if (task.getAction() != ActionType.PICKUP) {
                    task = nextTaskT.get(task);
                    continue;    
                }
                // Check if move would be valid
                if (vToMove.capacity() < task.getTask().weight) {
                    task = nextTaskT.get(task);
                    continue;
                }
                
                SLSPlanChange change = new SLSPlanChange(v, vToMove, task);
                task = nextTaskT.get(task);
                // Add the plan if the list is empty
                if (plans.isEmpty()) {
                    bestCost = evaluateChange(change);
                    plans.add(change);
                    continue;
                }
                // Check if the change brings improvement
                double changeCost = evaluateChange(change);
                if (changeCost < bestCost) {
                    bestCost = changeCost;
                    plans.clear();
                }
                if (changeCost <= bestCost)
                    plans.add(change);
            }
        }
    }

    private void addExchangeChanges(Vehicle v, List<SLSPlanChange> plans) {
        double bestCost = (plans.isEmpty() ? Double.MAX_VALUE : evaluateChange(plans.get(0)));
        // Create the arraylist for the vehicle's plan
        TaskWrapper t = nextTaskV.get(v);
        List<TaskWrapper> tasks = new ArrayList<TaskWrapper>();
        while (t.getAction() != ActionType.NULL) {
            tasks.add(t);
            t = nextTaskT.get(t);
        }

        // Try exchanging every pair of tasks(
        for (int i = 0; i < tasks.size() - 1; ++i)
            for (int j = i + 1; j < tasks.size(); ++j) {
                TaskWrapper t1 = tasks.get(i), t2 = tasks.get(j);
                
                // Check if the exchange is valid
                if (t2.getAction() == ActionType.DELIVER) {
                    // Deliver would be before its corresponding pickup
                    if (time.get(new TaskWrapper(t2.getTask(), ActionType.PICKUP)) >= time.get(t1))
                        continue;
                }
                if (t1.getAction() == ActionType.PICKUP) {
                    // Deliver would be before its corresponding pickup
                    if (time.get(new TaskWrapper(t1.getTask(), ActionType.DELIVER)) <= time.get(t2))
                        continue;
                }
                // Space in the vehicle does not become negative
                int weightDiff = t2.getTask().weight * (t2.getAction() == ActionType.PICKUP ? -1 : 1) -
                    t1.getTask().weight * (t1.getAction() == ActionType.PICKUP ? -1 : 1);
                int space = spaceT.get(t1);
                t = t1;
                while (t.getAction() != ActionType.NULL) {
                    if (t.equals(t1))
                        space += weightDiff;
                    else if (t.equals(t2))
                        space -= weightDiff;
                    else
                        space += t.getTask().weight * (t.getAction() == ActionType.PICKUP ? -1 : 1);
                    if (space < 0)
                        break;
                    // Advance to the next task
                    t = nextTaskT.get(t);
                }
                if (t.getAction() != ActionType.NULL)
                    continue;
                
                SLSPlanChange change = new SLSPlanChange(t1, t2);
                // Add the plan if the list is empty
                if (plans.isEmpty()) {
                    bestCost = evaluateChange(change);
                    plans.add(change);
                    continue;
                }
                // Check if the change brings improvement
                double changeCost = evaluateChange(change);
                if (changeCost < bestCost) {
                    bestCost = changeCost;
                    plans.clear();
                }
                if (changeCost <= bestCost)
                    plans.add(change);
            }
    }

    private City getTaskCity(TaskWrapper task) {
        if (task.getAction() == ActionType.NULL)
            return null;
        return task.getAction() == ActionType.PICKUP ? task.getTask().pickupCity : task.getTask().deliveryCity;
    }

    private double evaluateMove(Vehicle[] vs, TaskWrapper moveTask) {
        double relativeChange = 0;
        Task task = moveTask.getTask();
        TaskWrapper taskPickup = new TaskWrapper(task, ActionType.PICKUP);
        TaskWrapper taskDeliver = new TaskWrapper(task, ActionType.DELIVER);

        // Find city before task pickup
        City prevTaskCity;
        if (time.get(moveTask) == 0)
            prevTaskCity = vs[0].getCurrentCity();
        else {
            TaskWrapper t = nextTaskV.get(vs[0]);
            while (!nextTaskT.get(t).equals(moveTask))
                t = nextTaskT.get(t);
            prevTaskCity = getTaskCity(t);
        }

        // + last task in v2 -> task pick
        TaskWrapper lastTaskV2 = nextTaskV.get(vs[1]);
        if (lastTaskV2.getAction() == ActionType.NULL)
            relativeChange += vs[1].getCurrentCity().distanceTo(task.pickupCity) * vs[1].costPerKm();
        else {
            while (nextTaskT.get(lastTaskV2).getAction() != ActionType.NULL)
                lastTaskV2 = nextTaskT.get(lastTaskV2);
            relativeChange += lastTaskV2.getTask().deliveryCity.distanceTo(task.pickupCity) * vs[1].costPerKm();
        }
        // - prev(task pick) -> task pick
        relativeChange -= prevTaskCity.distanceTo(task.pickupCity) * vs[0].costPerKm();

        // Pickup and delivery are one after the other for task
        if (nextTaskT.get(taskPickup).equals(taskDeliver)) {
            // - task cost in prev vehicle
            relativeChange -= task.pathLength() * vs[0].costPerKm();
            // + task cost in new vehicle
            relativeChange += task.pathLength() * vs[1].costPerKm();
            // + prev(task pick) -> next(task deliv)
            if (nextTaskT.get(taskDeliver).getAction() != ActionType.NULL)
                relativeChange += prevTaskCity.distanceTo(nextTaskT.get(taskDeliver).getTask().pickupCity) * vs[0].costPerKm();
        } else {
            // + task pick -> task deliv
            relativeChange += task.pathLength();
            // - task pick -> next(task pick)
            relativeChange -= task.pickupCity.distanceTo(nextTaskT.get(taskPickup).getTask().pickupCity) * vs[0].costPerKm();
            // + prev(task pick) -> next(task pick)
            relativeChange += prevTaskCity.distanceTo(nextTaskT.get(taskPickup).getTask().pickupCity) * vs[0].costPerKm();
            // - prev(task deliv) -> task deliv
            TaskWrapper prevDelivT = nextTaskT.get(taskPickup);
            while (!nextTaskT.get(prevDelivT).equals(taskDeliver))
                prevDelivT = nextTaskT.get(prevDelivT);
            City prevDelivTCity = getTaskCity(prevDelivT);
            relativeChange -= prevDelivTCity.distanceTo(task.deliveryCity) * vs[0].costPerKm();

            if (nextTaskT.get(taskDeliver).getAction() != ActionType.NULL) {
                City nextDelivTCity = getTaskCity(nextTaskT.get(taskDeliver));
                // - task deliv -> next(task deliv)
                relativeChange -= task.deliveryCity.distanceTo(nextDelivTCity) * vs[0].costPerKm();
                // + prev(task deliv) -> next(task deliv)
                relativeChange += prevDelivTCity.distanceTo(nextDelivTCity) * vs[0].costPerKm();
            }
        }

        return relativeChange;
    }

    private double evaluateExchange(TaskWrapper[] ts) {
        double relativeChange = 0;
        // Get tasks before task2 and after task1 and task2
        TaskWrapper prevT2 = ts[0];
        while (!nextTaskT.get(prevT2).equals(ts[1]))
            prevT2 = nextTaskT.get(prevT2);
        TaskWrapper nextT1 = nextTaskT.get(ts[0]);
        TaskWrapper nextT2 = nextTaskT.get(ts[1]);
        City t1City = getTaskCity(ts[0]);
        City t2City = getTaskCity(ts[1]);
        City prevT2City = getTaskCity(prevT2);
        City nextT1City = getTaskCity(nextT1);
        City nextT2City = getTaskCity(nextT2);
        Vehicle v = vehicle.get(ts[0]);

        // First task is the first in the list
        if (nextTaskV.get(v).equals(ts[0])) {
            // - v -> task1
            relativeChange -= v.getCurrentCity().distanceTo(t1City) * v.costPerKm();
            // + v -> task2
            relativeChange += v.getCurrentCity().distanceTo(t2City) * v.costPerKm();
        } else {
            // Get the task before task1
            TaskWrapper prevT1 = nextTaskV.get(v);
            while (!nextTaskT.get(prevT1).equals(ts[0]))
                prevT1 = nextTaskT.get(prevT1);
            City prevT1City = getTaskCity(prevT1);
            
            // - prev(task1) -> task1
            relativeChange -= prevT1City.distanceTo(t1City) * v.costPerKm();
            // + prev(task1) -> task2
            relativeChange += prevT1City.distanceTo(t2City) * v.costPerKm();
        }

        // The tasks are not one after the other
        if (!nextT1.equals(ts[1])) {
            // - prev(task2) -> task2
            relativeChange -= prevT2City.distanceTo(t2City) * v.costPerKm();
            // + prev(task2) -> task1
            relativeChange += prevT2City.distanceTo(t1City) * v.costPerKm();
            // - task1 -> next(task1)
            relativeChange -= t1City.distanceTo(nextT1City) * v.costPerKm();
            // + task2 -> next(task1)
            relativeChange += t2City.distanceTo(nextT1City) * v.costPerKm();
        }

        // If task2 has a next task
        if (nextT2City != null) {
            // - task2 -> next(task2)
            relativeChange -= t2City.distanceTo(nextT2City) * v.costPerKm();
            // + task1 -> next(task2)
            relativeChange += t1City.distanceTo(nextT2City) * v.costPerKm();
        }

        return relativeChange;
    }

    private void executeMove(Vehicle[] vs, TaskWrapper moveTask) {
        Task taskToMove = moveTask.getTask();
        TaskWrapper taskPickup = new TaskWrapper(taskToMove, ActionType.PICKUP);
        TaskWrapper taskDeliv = new TaskWrapper(taskToMove, ActionType.DELIVER);
        // Get the task after delivery
        TaskWrapper nextDeliv = nextTaskT.get(taskDeliv);
        // Get task before pickup
        TaskWrapper prevPickup = nextTaskV.get(vs[0]);
        if (time.get(moveTask) != 0)
            while (!nextTaskT.get(prevPickup).equals(moveTask))
                prevPickup = nextTaskT.get(prevPickup);

        // Delivery is after pickup
        if (nextTaskT.get(taskPickup).equals(taskDeliv)) {
            if (time.get(taskPickup) == 0)
                nextTaskV.put(vs[0], nextDeliv);
            else
                nextTaskT.put(prevPickup, nextDeliv);
        } else {
            if (time.get(taskPickup) == 0)
                nextTaskV.put(vs[0], nextTaskT.get(taskPickup));
            else
                nextTaskT.put(prevPickup, nextTaskT.get(taskPickup));
            // Get the task before deliver
            TaskWrapper prevDeliv = nextTaskT.get(taskPickup);
            while (!nextTaskT.get(prevDeliv).equals(taskDeliv))
                prevDeliv = nextTaskT.get(prevDeliv);
            nextTaskT.put(prevDeliv, nextDeliv);
        }

        // Put task in the other vehicle's list
        addTaskToVehicle(vs[1], taskToMove);

        // Update timestamps and space for the first vehicle
        TaskWrapper t = nextTaskV.get(vs[0]);
        int timestamp = 0, space = vs[0].capacity();
        while (t.getAction() != ActionType.NULL) {
            time.put(t, timestamp);
            space += t.getTask().weight * (t.getAction() == ActionType.PICKUP ? -1 : 1);
            spaceT.put(t, space);
            ++timestamp;
            t = nextTaskT.get(t);
        }
    }

    private void executeExchange(TaskWrapper[] ts) {
        Vehicle v = vehicle.get(ts[0]);
        // Get tasks before task2 and after task1 and task2
        TaskWrapper prevT2 = ts[0];
        while (!nextTaskT.get(prevT2).equals(ts[1]))
            prevT2 = nextTaskT.get(prevT2);
        TaskWrapper nextT1 = nextTaskT.get(ts[0]);
        TaskWrapper nextT2 = nextTaskT.get(ts[1]);

        // First task is at the list head
        if (nextTaskV.get(v).equals(ts[0]))
            nextTaskV.put(v, ts[1]);
        else {
            // Get task before task1
            TaskWrapper prevT1 = nextTaskV.get(v);
            while (!nextTaskT.get(prevT1).equals(ts[0]))
                prevT1 = nextTaskT.get(prevT1);
            nextTaskT.put(prevT1, ts[1]);
        }

        // Tasks are one after the other
        if (nextT1.equals(ts[1]))
            nextTaskT.put(ts[1], ts[0]);
        else {
            nextTaskT.put(ts[1], nextT1);
            nextTaskT.put(prevT2, ts[0]);
        }
        nextTaskT.put(ts[0], nextT2);

        // Exchange timestamps
        int timeT0 = time.get(ts[0]);
        time.put(ts[0], time.get(ts[1]));
        time.put(ts[1], timeT0);

        // Update space variables
        int space = spaceV.get(v);
        TaskWrapper t = nextTaskV.get(v);
        while (t.getAction() != ActionType.NULL) {
            space += t.getTask().weight * (t.getAction() == ActionType.PICKUP ? -1 : 1);
            spaceT.put(t, space);
            t = nextTaskT.get(t);
        }
    }
}