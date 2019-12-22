import java.util.ArrayList;

import uchicago.src.sim.space.Object2DGrid;

/**
 * Class that implements the simulation space of the rabbits grass simulation.
 * @author 
 */

public class RabbitsGrassSimulationSpace {
	public enum GridCell {
		EMPTY(0), GRASS(1);
		
		private final int value;
		
		private GridCell(int value) {
			this.value = value;
		}
		
		public Integer getValue() {
			return value;
		}
	}
	
	private class GridCoords {
		public int x, y;
		
		public GridCoords(int x, int y) {
			this.x = x;
			this.y = y;
		}
	}
	
	// Environment and agent grids
	private Object2DGrid grassSpace;
	private Object2DGrid agentSpace;

	// Environment characteristics
	private int xSize, ySize;
	private int grassEnergy;
	
	// Cell counters
	private int totalCells;
	private int numFreeCells;
	private int numGrassCells;
	private int numRabbitCells;
	
	// Percentage of filled cells for which when choosing a random cell
	// we make a more careful selection
	private static final float RANDOMTHRESH = 25;
	
	public RabbitsGrassSimulationSpace(int xSize, int ySize, int grassEnergy) {
		grassSpace = new Object2DGrid(xSize, ySize);
		agentSpace = new Object2DGrid(xSize, ySize);
		this.xSize = xSize;
		this.ySize = ySize;
		this.grassEnergy = grassEnergy;
		
		for (int i = 0; i < xSize; ++i)
			for (int j = 0; j < ySize; ++j) {
				grassSpace.putObjectAt(i, j, GridCell.EMPTY.getValue());
				agentSpace.putObjectAt(i, j, null);
			}
		
		// Keep track of the number of cells of each type
		totalCells = xSize * ySize;
		numFreeCells = totalCells;
		numGrassCells = 0;
		numRabbitCells = 0;
	}
	
	public Object2DGrid getGrassSpace() {
		return grassSpace;
	}
	
	public Object2DGrid getAgentSpace() {
		return agentSpace;
	}
	
	/*
	 * Check if there is a rabbit at a given cell
	 * 
	 * @parameter x	x-coordinate of the cell to query
	 * @parameter y	y-coordinate of the cell to query
	 * @return rabbit object at the given coordinates or null if there
	 * is no rabbit
	 */
	public RabbitsGrassSimulationAgent getRabbitAt(int x, int y) {
		return (RabbitsGrassSimulationAgent)agentSpace.getObjectAt(x, y);
	}
	
	/*
	 * Tries to create maximum numGrass grass cells, being restricted
	 * by the number of free cells available
	 * 
	 * @parameter numGrass	number of grass cells to create  
	 */
	public void spreadGrass(int numGrass) {
		System.out.println("Num grass: " + numGrassCells + ", Num rabbits: " + numRabbitCells);
		
		while (numGrass > 0) {
			if (!createGrass())
				break;
			
			--numGrass;
		}
	}
	
	/*
	 * Tries to create maximum numRabbits rabbit cells, being restricted
	 * by the number of free cells available
	 * 
	 * @parameter numRabbits	number of rabbit cells to create
	 * @parameter rabbits		list of rabbits to put on grid
	 * @return the list of rabbits added  
	 */
	public ArrayList<RabbitsGrassSimulationAgent> spreadRabbits(int numRabbits, ArrayList<RabbitsGrassSimulationAgent> rabbits) {
		ArrayList<RabbitsGrassSimulationAgent> addedRabbits = new ArrayList<RabbitsGrassSimulationAgent>();
		while (numRabbits > 0) {
			if (!createRabbit(rabbits.get(numRabbits - 1)))
				break;
			
			addedRabbits.add(rabbits.get(numRabbits - 1));
			--numRabbits;
		}
		
		return addedRabbits;
	}
	
	/*
	 * Tries to create a grass cell if free cells are still available
	 * 
	 * @return true if a grass cell was created, false otherwise  
	 */
	public boolean createGrass() {
		GridCoords coords = getFreeCellCoords();
		if (coords == null)
			return false;

		// Add grass to the grid space
		grassSpace.putObjectAt(coords.x, coords.y, GridCell.GRASS.getValue());
		++numGrassCells;
		--numFreeCells;
		
		return true;
	}
	
	/*
	 * Tries to create a rabbit cell if free cells are still available
	 * 
	 * @parameter agent	rabbit agent to be placed in agent space
	 * @return true if a rabbit cell was created, false otherwise  
	 */
	public boolean createRabbit(RabbitsGrassSimulationAgent agent) {
		GridCoords coords = getFreeCellCoords();
		if (coords == null)
			return false;

		// Add the rabbit to the agent space
		agentSpace.putObjectAt(coords.x, coords.y, agent);
		agent.setCoords(coords.x, coords.y);
		agent.setSimSpace(this);
		
		++numRabbitCells;
		--numFreeCells;
		
		return true;
	}
	
	/*
	 * Tries to remove grass from a given cell if grass is present
	 * 
	 * @parameter x	x-coordinate of the cell
	 * @parameter y	y-coordinate of the cell
	 * @return true, if grass was found in the cell, false otherwise
	 */
	public boolean removeGrass(int x, int y) {
		if (grassSpace.getObjectAt(x, y) != GridCell.GRASS.getValue())
			return false;
		
		grassSpace.putObjectAt(x, y, GridCell.EMPTY.getValue());
		--numGrassCells;
		++numFreeCells;
		
		return true;
	}
	
	/*
	 * Tries to remove a rabbit from a given cell if a rabbit is present
	 * 
	 * @parameter x				x-coordinate of the cell
	 * @parameter y				y-coordinate of the cell
	 * @parameter deadRabbit	whether the rabbit consumed its energy
	 * @return true, if a rabbit was found in the cell, false otherwise
	 */
	public boolean removeRabbit(int x, int y, boolean deadRabbit) {
		if (getRabbitAt(x, y) == null)
			return false;
		
		agentSpace.putObjectAt(x, y, null);
		
		if (deadRabbit)
		{
			--numRabbitCells;
			++numFreeCells;
		}
		
		return true;
	}
	
	/*
	 * Return the energy from the cell at the given coordinates based
	 * on whether there is grass or not
	 * 
	 * @parameter x	x-coordinate of the cell to query
	 * @parameter y	y-coordinate of the cell to query
	 * @return the energy at the given cell
	 */
	public int takeEnergyAt(int x, int y) {
		// Remove grass from the cell
		return removeGrass(x, y) ? grassEnergy : 0;
	}
	
	/*
	 * Try moving an agent
	 * 
	 * @parameter x		old x-coordinate of the agent
	 * @parameter y		old y-coordinate of the agent
	 * @parameter newX	new x-coordinate of the agent
	 * @parameter newY	new y-coordinate of the agent
	 * @return true, if the move succeeded or not, false otherwise
	 */
	public boolean moveAgentAt(int x, int y, int newX, int newY) {		
		RabbitsGrassSimulationAgent rabbit = getRabbitAt(x, y);
		if (rabbit == null)
			return false;
		
		// Check if the move is valid
		if (Math.abs(x - newX) > 1 && Math.abs(x - newX) != xSize - 1)
			return false;
		if (Math.abs(y - newY) > 1 && Math.abs(y - newY) != ySize - 1)
			return false;
		
		// Check if there would occur a collision
		if (getRabbitAt(newX, newY) != null)
			return false;
		
		removeRabbit(x, y, false);
		rabbit.setCoords(newX, newY);
		agentSpace.putObjectAt(newX, newY, rabbit);
		
		return true;
	}
	
	public int getXSize() {
		return xSize;
	}
	
	public int getYSize() {
		return ySize;
	}
	
	 /* Find coordinates for a randomly chosen free cell, if one is available
	 * 
	 * @return	coordinates of a free cell, if one is available, null otherwise
	 */
	private GridCoords getFreeCellCoords() {
		GridCoords coords;
		if (100 * ((float)numFreeCells) / totalCells > RANDOMTHRESH)
			coords = simpleRandomChoice();
		else
			coords = guidedRandomChoice();
		
		return coords;
	}
	
	/*
	 * Find coordinates for a randomly chosen free cell, if one is available
	 * Both coordinates are searched completely at random
	 * 
	 * @return	coordinates of a free cell, if one is available, null otherwise
	 */
	private GridCoords simpleRandomChoice() {
		if (numFreeCells == 0)
			return null;
		
		while (true) {
			// Choose coordinates at random
			int x = (int)(Math.random() * xSize);
			int y = (int)(Math.random() * ySize);
			
			if (grassSpace.getObjectAt(x, y) == GridCell.EMPTY.getValue() && getRabbitAt(x, y) == null)
				return new GridCoords(x, y);
		}
	}
	
	/*
	 * Find coordinates for a randomly chosen free cell, if one is available
	 * The row coordinate is chosen completely at random, the column coordinate
	 * is chosen from the free cells on the previously chosen row
	 * 
	 * @return	coordinates of a free cell, if one is available, null otherwise
	 */
	private GridCoords guidedRandomChoice() {
		if (numFreeCells == 0)
			return null;
		
		while (true) {
			// Choose x-coordinate at random
			int x = (int)(Math.random() * xSize);
			
			// Look for free cells on row x
			ArrayList<Integer> freeCells = new ArrayList<Integer>();
			for (int y = 0; y < ySize; ++y)
				if (grassSpace.getObjectAt(x, y) == GridCell.EMPTY.getValue() && getRabbitAt(x, y) == null)
					freeCells.add(y);
			
			if (freeCells.size() == 0)
				continue;
			
			int y = freeCells.get((int)(Math.random() * freeCells.size()));
		
			return new GridCoords(x, y);
		}
	}
}
