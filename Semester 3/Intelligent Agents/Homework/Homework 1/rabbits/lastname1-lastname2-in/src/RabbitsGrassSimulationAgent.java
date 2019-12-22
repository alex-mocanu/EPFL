import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.Hashtable;

import javax.imageio.ImageIO;

import uchicago.src.sim.gui.Drawable;
import uchicago.src.sim.gui.SimGraphics;


/**
 * Class that implements the simulation agent for the rabbits grass simulation.

 * @author
 */

public class RabbitsGrassSimulationAgent implements Drawable {
	private class LegalMove {
		public int x, y;
		
		public LegalMove(int x, int y) {
			this.x = x;
			this.y = y;
		}
	}
	
	private static final String rabbitImagePath = "resources/rabbit.png";
	private boolean rabbitImageFound = true;
	private BufferedImage rabbitImage;
	
	// References to the model and the space where the agent exists 
	private RabbitsGrassSimulationModel model;
	private RabbitsGrassSimulationSpace simSpace;
	
	// Agent characteristics
	private int x, y;
	private int vX, vY; // velocity
	private int energy;
	
	private Hashtable<Integer, LegalMove> legalMoves;
	
	public RabbitsGrassSimulationAgent(RabbitsGrassSimulationModel model) {
		x = -1;
		y = -1;
		this.model = model;
		this.energy = model.getInitialEnergy();
		
		// Define legal moves for the agent
		legalMoves = new Hashtable<Integer, LegalMove>();
		legalMoves.put(0, new LegalMove(0, -1));
		legalMoves.put(1, new LegalMove(0, 1));
		legalMoves.put(2, new LegalMove(-1, 0));
		legalMoves.put(3, new LegalMove(1, 0));
	}
	
	public void setCoords(int x, int y) {
		this.x = x;
		this.y = y;
	}
	
	public void setSimSpace(RabbitsGrassSimulationSpace simSpace) {
		this.simSpace = simSpace;
	}
	
	public void draw(SimGraphics graphics) {
		if (!rabbitImageFound) {
			// Rabbit image was not found, so we draw something simpler
			graphics.drawFastRoundRect(Color.gray);
		}
		else if (rabbitImage == null)
		{
			// Image was not yet loaded
			try {
				rabbitImage = ImageIO.read(new File(rabbitImagePath));
				graphics.drawImageToFit(rabbitImage);
				rabbitImageFound = true;
			} catch (IOException e) {
				System.out.println("Rabbit image " + rabbitImagePath + " not found");
				graphics.drawFastRoundRect(Color.gray);
			}
		}
		else
		{
			// Image was already read
			graphics.drawImageToFit(rabbitImage);
		}
	}

	public int getX() {
		return x;
	}

	public int getY() {
		return y;
	}

	/*
	 * Move the agent for the current timestep
	 */
	public void moveAgent() {
		if (!isRabbitSurrounded()) {
			int newX, newY;
			int xSize = simSpace.getXSize();
			int ySize = simSpace.getYSize();
			
			do {
				setVxVy();
				newX = (x + vX + xSize) % xSize;
				newY = (y + vY + ySize) % ySize;
			} while (!tryMove(newX, newY));
			
			energy += simSpace.takeEnergyAt(x, y);
		}
		
		energy -= model.getEnergyDecay();
		
		// Reproduces if it has enough energy
		if (energy >= model.getBirthThreshold()) {
			energy -= model.getReproductionEnergy();
			model.addNewAgent();
		}
	}
	
	public int getEnergy() {
		return energy;
	}
	
	/*
	 * Choose a random direction for the agent to move towards
	 */
	private void setVxVy() {
		int move = (int)(Math.random() * legalMoves.size());
		vX = legalMoves.get(move).x;
		vY = legalMoves.get(move).y;
	}
	
	/*
	 * Check if a move is valid
	 * 
	 * @parameter newX	x-coordinate to move the agent to
	 * @parameter newY	y-coordinate to move the agent to
	 * @return true, if the move succeeded, false otherwise 
	 */
	private boolean tryMove(int newX, int newY) {
		return simSpace.moveAgentAt(x, y, newX, newY);
	}
	
	/*
	 * Check if a rabbit can not move due to it having another rabbit
	 * in each of its neighboring cells
	 * 
	 * @parameter x	x-coordinate of the rabbit
	 * @parameter y	y-coordinate of the rabbit
	 * @return true, if the rabbit is surrounded, false otherwise
	 */
	private boolean isRabbitSurrounded() {
		boolean isSurrounded = true;
		for (int i = 0; i < legalMoves.size(); ++i) {
			int xSize = simSpace.getXSize();
			int ySize = simSpace.getYSize();
			int neighX = (x + legalMoves.get(i).x + xSize) % xSize;
			int neighY = (y + legalMoves.get(i).y + ySize) % ySize;
			isSurrounded &= (simSpace.getRabbitAt(neighX, neighY) != null);
		}
		
		return isSurrounded;
	}
}
