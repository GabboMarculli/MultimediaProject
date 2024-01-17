package it.unipi.mircv.SearchEngine.utilities;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;


import org.tartarus.snowball.ext.englishStemmer;
import org.tartarus.snowball.SnowballStemmer;



/**
 * This class is used in the project to implement pre-processing text elaboration.
 * It contains several methods for text cleaning, stemming and stop word removal.
 * It has the same exact implementation of TextProcessor used in Python during Indexing.
 * 
 * @author Davide and Gabriele
 *
 */
public class TextProcessor {
	
    private boolean useStemmingAndStopWords;
    private final Pattern regExpPunctuation = Pattern.compile("[^\\w\\s]|_");
    private final Pattern regExpHtmlTags = Pattern.compile("<[^>]+>");
    private final Pattern regExpHashtags = Pattern.compile("#\\w+");
    private final Pattern regExpUsernames = Pattern.compile("@\\w+");
    private final Pattern controlCharPattern = Pattern.compile("[^\\x00-\\x7F]+");
    private final Pattern regExpWebLinkPattern = Pattern.compile("https*://\\S+|www.\\S+");

    private SnowballStemmer stemmer;
    private Set<String> stopWords;

    
    /**
     * Constructor method:
     * 
     * @param useStemmingAndStopWordsRemoval -  true if stemming and stop word removal should be done, false otherwise
     * @param pathOfStopWords - the file path where to load the stop words
     */
    public TextProcessor(boolean useStemmingAndStopWordsRemoval,String pathOfStopWords) {
        
    	this.useStemmingAndStopWords = useStemmingAndStopWordsRemoval;
        this.stopWords = readWordsFromFile(pathOfStopWords);
        
        if (useStemmingAndStopWordsRemoval) {
        	 englishStemmer en= new englishStemmer();
             this.stemmer = (SnowballStemmer) en;
        }
    }
    
    /**
     * Process a text by cleaning, tokenizing, removing stopwords and stemming(optionally).
     * This is the main method called from outside, during the processing of all the queries.
     * 
     * @param text - The text to be processed.
     * @return
     */
    public String processText(String text) {
        
    	text = cleanText(text);

        if (text.isEmpty()) {
            return text;
        }

        List<String> wordTokens = tokenizeText(text);

        if (useStemmingAndStopWords) {
            wordTokens = removeStopWords(wordTokens);
            wordTokens = stemText(wordTokens);
        }

        return String.join(" ", wordTokens);
    }
    
    /**
     * Apply Stemming on a list of tokens using English language.
     * @param tokens - List of tokens to be stemmed.
     * @return - a list of strings where stemming is done.
     */
    public List<String> stemText(List<String> tokens) {
//        List<String> stemmedTokens = new ArrayList<>();
//        for (String token : tokens) {
//        	
//        	stemmer.setCurrent(token);
//			stemmer.stem();
//            stemmedTokens.add(stemmer.getCurrent());
//        }
//        return stemmedTokens;
    	// JAVA8
    	return tokens.stream()
                .map(token -> {
                    stemmer.setCurrent(token);
                    stemmer.stem();
                    return stemmer.getCurrent();
                })
                .collect(Collectors.toList());
    	
    	
    }

    /**
     * Remove stopwords from a list of stop words tokens in English language.
     * @param tokens - List of tokens to be processed.
     * @return
     */
    public List<String> removeStopWords(List<String> tokens) {
        List<String> filteredTokens = new ArrayList<>();
        for (String token : tokens) {
            if (!stopWords.contains(token)) {
                filteredTokens.add(token);
            }
        }
        return filteredTokens;
        
    	//Java 8
//        return tokens.stream()
//                .filter(token -> !stopWords.contains(token))
//                .collect(Collectors.toList());
        
    }
	/**
	 * Clean the text by converting to lowercase, replacing special characters.
	 * @param text - The text to be cleaned.
	 * @return The cleaned text
	 */
    public String cleanText(String text) {
        text = text.toLowerCase();
        text = controlCharPattern.matcher(text).replaceAll(" ");

        String combinedPattern = regExpHtmlTags.pattern() + "|" + regExpHashtags.pattern() + "|" +
                regExpPunctuation.pattern() + "|" + regExpUsernames.pattern() + "|" +
                regExpWebLinkPattern.pattern();
        Pattern combinedPatternCompiled = Pattern.compile(combinedPattern);
        text = combinedPatternCompiled.matcher(text).replaceAll(" ");

        text = text.replaceAll("\\s+", " ");

        return text.trim();
    }
    
    
    /**
     * Method to divide text in tokens.
     * @param text - the text to be divided
     * @return a list of strings representing the tokens
     */
    public List<String> tokenizeText(String text) {
        String[] words = text.split("\\s+");
        return Arrays.asList(words);
    }
    
	/**
	 * Utility method for loading a list of stop words from a textual file.
	 * @param filePath
	 * @return
	 */
    private Set<String> readWordsFromFile(String filePath) {
        Set<String> stopWordsList = new HashSet<>();
        try {
            Path path = Paths.get(filePath);
            stopWordsList.addAll(Files.readAllLines(path));
        } catch (IOException e) {
            System.err.println("Stopword file not imported");
        }
        return stopWordsList;
    }
}
