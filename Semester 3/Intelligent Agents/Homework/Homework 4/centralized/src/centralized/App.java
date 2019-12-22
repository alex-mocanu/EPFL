package centralized;

import logist.LogistPlatform;

public class App {
	
	public static void main(String[] args) {
		LogistPlatform.main(new String[]{"config/centralized.xml", "centralized-main"});
	}
}
