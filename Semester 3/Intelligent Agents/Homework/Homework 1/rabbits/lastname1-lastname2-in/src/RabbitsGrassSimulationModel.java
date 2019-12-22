import java.awt.Color;
import java.util.ArrayList;

import uchicago.src.sim.engine.BasicAction;
import uchicago.src.sim.engine.Schedule;
import uchicago.src.sim.engine.SimInit;
import uchicago.src.sim.engine.SimModelImpl;
import uchicago.src.sim.gui.ColorMap;
import uchicago.src.sim.gui.DisplaySurface;
import uchicago.src.sim.gui.Object2DDisplay;
import uchicago.src.sim.gui.Value2DDisplay;
import uchicago.src.sim.util.SimUtilities;

/**
 * Class that implements the simulation model for the rabbits grass
 * simulation.  This is the first class which needs to be setup in
 * order to run Repast simulation. It manages the entire RePast
 * environment and the simulation.
 *
 * @author 
 */


public class RabbitsGrassSimulationModel extends SimModelImpl {
	// Default parameter values
	private static final int GRIDSIZE = 20;
	private static final int NUMINITRABBITS = 10;
	private static final int NUMINITGRASS = 20;
	private static final int GRASSGROWTHRATE = 5;
	private static final int BIRTHTHRESHOLD = 20;
	private static final int GRASSENERGY = 10;
	private static final int INITIALENERGY = 10;
	private static final int ENERGYDECAY = 1;
	private static final int REPRODUCTIONENERGY = 15;
	
	// Schedule object
	private Schedule schedule;
	
	// Simulation parameters
	private int gridSize = GRIDSIZE;
	private int numInitRabbits = NUMINITRABBITS;
	private int numInitGrass = NUMINITGRASS;
	private int grassGrowthRate = GRASSGROWTHRATE;
	private int birthThreshold = BIRTHTHRESHOLD;
	private int grassEnergy = GRASSENERGY;
	private int initialEnergy = INITIALENERGY;
	private int energyDecay = ENERGYDECAY;
	private int reproductionEnergy = REPRODUCTIONENERGY;
	
	// Space object
	private RabbitsGrassSimulationSpace simSpace;
	private DisplaySurface displaySurf;
	
	// The list containing the agents
	private ArrayList<RabbitsGrassSimulationAgent> agentList;
	
	public static void main(String[] args) {
		SimInit init = new SimInit();
		RabbitsGrassSimulationModel model = new RabbitsGrassSimulationModel();
		// Do "not" modify the following lines of parsing arguments
		if (args.length == 0) // by default, you don't use parameter file nor batch mode 
			init.loadModel(model, "", false);
		else
			init.loadModel(model, args[0], Boolean.parseBoolean(args[1]));
	}
	
	public void setup() {
		System.out.println("setup");
		
		simSpace = null;
		agentList = new ArrayList<RabbitsGrassSimulationAgent>();
		schedule = new Schedule(1);
		
		if (displaySurf != null)
			displaySurf.dispose();
		displaySurf = new DisplaySurface(this, "Rabbit Grass Simulation Window");
		registerDisplaySurface("Rabbit Grass Simulation Window", displaySurf);
	}

	public void begin() {
		buildModel();
	    buildSchedule();
	    buildDisplay();
	    
	    // Display the simulation
	    displaySurf.display();
	}
	
	public void buildModel(){
		System.out.println("buildModel");
		
		// Create space and fill it with grass and rabbits
		simSpace = new RabbitsGrassSimulationSpace(gridSize, gridSize, grassEnergy);
		simSpace.spreadGrass(numInitGrass);
		ArrayList<RabbitsGrassSimulationAgent> rabbits = new ArrayList<RabbitsGrassSimulationAgent>();
		for (int i = 0; i < numInitRabbits; ++i)
			rabbits.add(new RabbitsGrassSimulationAgent(this));
		agentList = simSpace.spreadRabbits(numInitRabbits, rabbits);
	}

	public void buildSchedule(){
		System.out.println("buildSchedule");
		
		class RabbitsGrassSimulationStep extends BasicAction {
			public void execute() {
				SimUtilities.shuffle(agentList);
				for (int i = 0; i < agentList.size(); ++i)
					agentList.get(i).moveAgent();
				
				// Remove dead rabbits and add grass
				removeDeadRabbits();
				simSpace.spreadGrass(grassGrowthRate);
				
				// Redraw the grid
				displaySurf.updateDisplay();
			}
		}
		
		schedule.scheduleActionBeginning(0, new RabbitsGrassSimulationStep());
	}

	public void buildDisplay(){
		System.out.println("buildDisplay");
		
		ColorMap map = new ColorMap();

	    map.mapColor(0, Color.black);
	    map.mapColor(1, Color.green);

	    Value2DDisplay displayGrass = new Value2DDisplay(simSpace.getGrassSpace(), map);
	    Object2DDisplay displayRabbits = new Object2DDisplay(simSpace.getAgentSpace());

	    displaySurf.addDisplayable(displayGrass, "Grass");
	    displaySurf.addDisplayable(displayRabbits, "Rabbits");
	}

	public String[] getInitParam() {
		// Parameters to be set by users via the Repast UI slider bar
		// Do "not" modify the parameters names provided in the skeleton code, you can add more if you want 
		String[] params = { "GridSize", "NumInitRabbits", "NumInitGrass", "GrassGrowthRate", "BirthThreshold",
				"GrassEnergy", "InitialEnergy", "EnergyDecay", "ReproductionEnergy"};
		return params;
	}

	public String getName() {
		return "Rabbits Grass Simulation";
	}
	
	public void addNewAgent() {
		RabbitsGrassSimulationAgent agent = new RabbitsGrassSimulationAgent(this);
		
		// Only add agent to the list if it could be created
		if (simSpace.createRabbit(agent)) 
			agentList.add(agent);
	}

	public Schedule getSchedule() {
		return schedule;
	}
	
	public int getGridSize() {
		return gridSize;
	}
	
	public void setGridSize(int gridSize) {
		this.gridSize = gridSize;
	}

	public int getNumInitRabbits() {
		return numInitRabbits;
	}

	public void setNumInitRabbits(int numInitRabbits) {
		this.numInitRabbits = numInitRabbits;
	}

	public int getNumInitGrass() {
		return numInitGrass;
	}

	public void setNumInitGrass(int numInitGrass) {
		this.numInitGrass = numInitGrass;
	}

	public int getGrassGrowthRate() {
		return grassGrowthRate;
	}

	public void setGrassGrowthRate(int grassGrowthRate) {
		this.grassGrowthRate = grassGrowthRate;
	}

	public int getBirthThreshold() {
		return birthThreshold;
	}

	public void setBirthThreshold(int birthThreshold) {
		this.birthThreshold = birthThreshold;
	}

	public int getGrassEnergy() {
		return grassEnergy;
	}

	public void setGrassEnergy(int grassEnergy) {
		this.grassEnergy = grassEnergy;
	}

	public int getInitialEnergy() {
		return initialEnergy;
	}

	public void setInitialEnergy(int initialEnergy) {
		this.initialEnergy = initialEnergy;
	}

	public int getEnergyDecay() {
		return energyDecay;
	}

	public void setEnergyDecay(int energyDecay) {
		this.energyDecay = energyDecay;
	}

	public int getReproductionEnergy() {
		return reproductionEnergy;
	}

	public void setReproductionEnergy(int reproductionEnergy) {
		this.reproductionEnergy = reproductionEnergy;
	}
	
	/*
	 * Remove rabbits that have consumed their energy
	 */
	private void removeDeadRabbits() {
		for (int i = agentList.size() - 1; i >= 0; --i) {
			RabbitsGrassSimulationAgent rabbit = agentList.get(i);
			if (rabbit.getEnergy() <= 0) {
				simSpace.removeRabbit(rabbit.getX(), rabbit.getY(), true);
				agentList.remove(i);
			}
		}
	}
}
