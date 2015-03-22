import java.io.*;
import java.util.*;

public class Tokenizer {

	private static String[] reservedWords = { "abstract","continue","for","new","switch",
		"assert","default","goto","package","synchronized",
		"boolean","do","if","private","this",
		"break","double","implements","protected","throw",
		"byte","else","import","public","throws",
		"case","enum","instanceof","return","transient",
		"catch","extends","int","short","try",
		"char","final","interface","static","void",
		"class","finally","long","strictfp","volatile",
		"const","float","native","super","while" };

	private static String[] stopWords = {
		"apache", "exception", "iterator", "false", "get", "java", "javax", "listener", "null", "object", "set", "string", "throwable", "true", "util"
	};

	public static void main(String[] args) throws IOException {
		Reader r = new BufferedReader(new InputStreamReader(System.in));
		StreamTokenizer st = new StreamTokenizer(r);
		st.slashSlashComments(true);
		Set<String> tokens = new TreeSet<String>();
		while (st.nextToken() != StreamTokenizer.TT_EOF) {
			if (st.ttype == StreamTokenizer.TT_WORD) {
				for (String s : st.sval.split("\\.|-|_")) {
					for (String s0 : splitCamelCase(s).toLowerCase().split(" ")) {
						List<String> rw = Arrays.asList(reservedWords);
						List<String> sw = Arrays.asList(stopWords);
						if (rw.indexOf(s0) == -1 && sw.indexOf(s0) == -1) {
							tokens.add(s0);
						}
					}
				}
			}
		}
		System.out.println(tokens);
	}

	private static String splitCamelCase(String s) {
	   return s.replaceAll(
	      String.format("%s|%s|%s",
	         "(?<=[A-Z])(?=[A-Z][a-z])",
	         "(?<=[^A-Z])(?=[A-Z])",
	         "(?<=[A-Za-z])(?=[^A-Za-z])"
	      ),
	      " "
	   );
	}
}