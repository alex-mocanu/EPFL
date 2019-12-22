package template;

import java.io.IOException;

import logist.LogistPlatform;

public class Main {
	public static void main(String[] args) throws IOException {
		LogistPlatform.main(new String[]{"config/deliberative.xml", "deliberative-random"});
	}
}
