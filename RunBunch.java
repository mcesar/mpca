import java.io.*;
import java.lang.reflect.*;
import java.util.*;

import bunch.*;
import bunch.api.*;
import bunch.engine.*;

public class RunBunch {

	public static void main(String[] args) throws Exception {
		if (args.length != 2) {
			System.out.println("Usage: java RunBunch <file-name> <dest>");
			System.exit(1);
		}

		System.out.println(args[0]);

		BunchAPI api = new BunchAPI();
		BunchProperties bp = new BunchProperties();
		bp.setProperty(BunchProperties.MDG_INPUT_FILE_NAME, args[0]);
		//bp.setProperty(BunchProperties.OUTPUT_FORMAT, BunchProperties.DOT_OUTPUT_FORMAT);
		bp.setProperty(BunchProperties.OUTPUT_DIRECTORY, args[1]);
		//bp.setProperty(BunchProperties.MDG_OUTPUT_MODE, BunchProperties.OUTPUT_DETAILED);
		api.setProperties(bp);
		api.run();
		/*
		Hashtable results = api.getResults();
		System.out.println(results.get(BunchAPI.TOTAL_CLUSTER_LEVELS));
		for (Object ht : (Object[]) results.get(BunchAPI.RESULT_CLUSTER_OBJS)) {
			System.out.println(ht);
		}
		*/

		BunchEngine engine = null;
		Field field = api.getClass().getDeclaredField("engine");
		field.setAccessible(true);
		engine = (BunchEngine) field.get(api);

		GraphOutput graphOutput = new GraphOutputFactory().getOutput("Dotty");
		graphOutput.setBaseName(args[0]);
		graphOutput.setBasicName(args[0]);
		String outputFileName = graphOutput.getBaseName();
		String outputPath = args[1];
		if (outputPath != null) {
			File f = new File(graphOutput.getBaseName());
			String filename = f.getName();
			outputFileName = outputPath + filename;
		}
		graphOutput.setCurrentName(outputFileName);
		graphOutput.setOutputTechnique(3);
		graphOutput.setGraph(engine.getBestGraph());
		graphOutput.write();
	}
}