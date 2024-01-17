package it.unipi.mircv.SearchEngine.handlers;

import java.io.IOException;
import java.io.RandomAccessFile;

import org.junit.platform.commons.util.LruCache;

import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.structures.LexiconRow;

/**
* Represents a Lexicon containing term information and provides methods for managing and accessing terms.
* This class includes functionalities such as term caching, adding terms, finding terms, and exposing
* Lexicon information through getter methods.
* @author Gabriele
*/
public class Lexicon {
	
	
	private boolean useCache;
    private int capacity;
    
	private CollectionStatistics collectionStatistics;
    private LruCache<String, LexiconRow> vocabulary;
   
    private RandomAccessFile fileLexicon;
    
    /**
     * Constructs a Lexicon with the specified capacity.
     * 
     * @param capacity - The maximum capacity of the Lexicon cache.
     * @param useCache - If using cache or not
     * @param fileLexicon - The RandomAccessFile representing the Lexicon file.
     * @param collectionStatistics - The statistics about the collection containing the terms.
     */
	public Lexicon(int capacity,boolean useCache,RandomAccessFile fileLexicon,CollectionStatistics collectionStatistics) {
        
		this.useCache=useCache;
		
		if (this.useCache) {
			if(capacity < 1)
	            this.capacity = 1024;
	        else
	        	this.capacity = capacity;
			this.vocabulary = new LruCache<>(this.capacity);
		}
		
        this.fileLexicon=fileLexicon;
        this.collectionStatistics=collectionStatistics;
        
    }
	
	/**
     * Adds a LexiconRow representing a term to the Lexicon cache.
     *
     * @param lexRow The LexiconRow representing the term to add.
     */
    public void addTerm(LexiconRow lexRow) {
        vocabulary.put(lexRow.getTerm(), lexRow);
    }
    
    /**
     * Retrieves a LexiconRow representing a term from the Lexicon cache.
     *
     * @param term The term to retrieve.
     * @return The LexiconRow representing the term or null if not found in the cache.
     */
    public LexiconRow getTerms(String term) {
        return vocabulary.getOrDefault(term, null);
    }

    /**
     * Finds a LexiconRow representing a term in the Lexicon file using binary search.
     *
     * @param term The term to find.
     * @return The LexiconRow representing the term or null if not found.
     * @throws IOException if an I/O error occurs during the search.
     */
    private LexiconRow findEntry(String term) throws IOException {
        LexiconRow lexiconRow = new LexiconRow();
        int start = 0;
        int end = collectionStatistics.getNumDistinctTerms() - 1;

        while (start <= end) {
            int mid = start + (end - start) / 2;

            // Get entry from disk
            lexiconRow.readLexiconRowOnDiskFromOpenedFile(this.fileLexicon, mid * LexiconRow.LEXICON_ROW_SIZE);
            
            String key = lexiconRow.getTerm().trim();

            // Check if the search was successful
            if (key.equals(term)) {
                return lexiconRow;
            }

            // Update search portion parameters
            if (term.compareTo(key) > 0) {
                start = mid + 1;
            } else {
                end = mid - 1;
            }
        }

        return null;
    }

    
    /**
     * Retrieves a LexiconRow representing a term, if cache enabled from the cache, or finds it in the Lexicon file.
     * If found in the file, the term is added to the cache.
     *
     * @param searchTerm The term to retrieve.
     * @return The LexiconRow representing the term or null if not found.
     * @throws IOException if an I/O error occurs during the retrieval.
     */
    public LexiconRow getLexiconRowTerm(String searchTerm) throws IOException {
        
    	LexiconRow lexiconRow = null;
    	
    	if (this.useCache) {
    		lexiconRow=getTerms(searchTerm);  // check if term is in cache
            if (lexiconRow != null)
                return lexiconRow;
    	}
    	
        lexiconRow = findEntry(searchTerm);
        
        if (this.useCache) {
	        if (lexiconRow != null) // add to cache
	            addTerm(lexiconRow);
        }

        return lexiconRow;
    }

    
    /** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
    
    public int getCapacity() {
		return capacity;
	}

	public CollectionStatistics getCollectionStatistics() {
		return collectionStatistics;
	}

	public LruCache<String, LexiconRow> getVocabulary() {
		return vocabulary;
	}

	public RandomAccessFile getFileLexicon() {
		return fileLexicon;
	}
    
	public boolean isUseCache() {
		return useCache;
	}
    
    
}
