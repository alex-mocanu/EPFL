package template;

import logist.task.Task;
import logist.task.TaskSet;
import logist.topology.Topology.City;

public class State {
	private City currentCity;
	private TaskSet tasksToPickUp;
	private TaskSet tasksOnBoard;
	private int size;
	
	public State(City city, TaskSet pickUp, TaskSet onBoard) {
		this.currentCity = city;
		this.tasksToPickUp = pickUp;
		this.tasksOnBoard = onBoard;
		
		// Compute the size of the load on board
		this.size = 0;
		for (Task task : tasksOnBoard)
			this.size += task.weight;
	}
	
	public City getCurrentCity() {
		return currentCity;
	}
	
	public TaskSet getTasksToPickUp() {
		return tasksToPickUp;
	}
	
	public TaskSet getTasksOnBoard() {
		return tasksOnBoard;
	}
	
	public int getSize() {
		return size;
	}
	
	@Override
	public int hashCode() {
		int hashMult = 31;
		int hash = 17;
		hash = hashMult * hash + currentCity.id;
		
		for (Task t : tasksToPickUp)
			hash = hashMult * hash + t.id;
		for (Task t : tasksOnBoard)
			hash = hashMult * hash + t.id;
		
		return hash;
	}
	
	@Override
	public boolean equals(Object obj) {
		if (obj == this)
			return true;
		
		// Different object type
		if (!(obj instanceof State))
			return false;
		
		State compState = (State)obj;
		// Different city
		if (compState.currentCity != this.currentCity)
			return false;
		// Different tasks to pick up
		if (!compState.tasksToPickUp.equals(this.tasksToPickUp))
			return false;
		// Different tasks on board
		if (!compState.tasksOnBoard.equals(this.tasksOnBoard))
			return false;
		
		return true;
	}
	
	public boolean isInTasksToPickUp(Task task) {
		return tasksToPickUp.contains(task);
	}
	
	public boolean isInTasksOnBoard(Task task) {
		return tasksOnBoard.contains(task);
	}
	
	public boolean isStateFinal() {
		return tasksToPickUp.isEmpty() && tasksOnBoard.isEmpty();
	}
}
