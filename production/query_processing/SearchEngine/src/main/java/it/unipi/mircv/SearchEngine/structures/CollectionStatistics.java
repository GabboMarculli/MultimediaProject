package it.unipi.mircv.SearchEngine.structures;

import java.io.*;

/**
 * This class represents the information of the collection handle in the project.
 * @author Gabriele
 *
 */
public class CollectionStatistics {

	private final String filePath;
	
    private int numDocuments;
    private int numDistinctTerms;
    private int sumDocumentLengths;
    
    /**
     * Initializes an instance of Collection_statistics.
     * 
     * @param filePath - the location where the info are stored.
     * @throws FileNotFoundException
     */
    public CollectionStatistics(String filePath) throws FileNotFoundException {
 
        this.filePath = filePath;
        this.read_statistics();
    }

    /**
     * Load the statistics related to the collection from a file and populate the fields.
     */
    public void read_statistics() {
        try (BufferedReader br = new BufferedReader(new FileReader(this.filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                // Split della linea in chiave e valore
                String[] parts = line.split(":");
                if (parts.length == 2) {
                    String key = parts[0].trim();
                    String value = parts[1].trim();
                    //System.out.println(key + ": " + value);

                    if(key.equals("Document Index Size"))
                    	this.numDocuments=Integer.parseInt(value);
                    else if(key.equals("Vocabulary Size"))
                    	this.numDistinctTerms=Integer.parseInt(value);
                    else if(key.equals("Sum Document length"))
                    	this.sumDocumentLengths=Integer.parseInt(value);
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
    
    
	/**
	 * Compute the average document length among all the document in the collection.
	 * @return a float representing the average document length
	 */
    public float getAverageDocumentLength() {
        return (float) sumDocumentLengths / numDocuments;
    }

    /** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
    
    public int getNumDistinctTerms() {
        return numDistinctTerms;
    }

    public int getNumDocuments() {
        return numDocuments;
    }

    public int getSumDocumentLengths() {
        return sumDocumentLengths;
    }

   
}
