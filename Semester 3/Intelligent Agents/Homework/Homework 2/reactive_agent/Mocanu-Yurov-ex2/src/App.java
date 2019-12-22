import java.io.IOException;

import logist.LogistPlatform;

public class App {
	public static void main(String[] args) throws IOException {
		LogistPlatform.main(new String[]{"config/reactive.xml", "reactive-rla"});
	}
}
