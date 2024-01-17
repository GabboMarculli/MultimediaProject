package it.unipi.mircv.SearchEngine.handlers;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

import it.unipi.mircv.SearchEngine.algorithms.DAAT;
import it.unipi.mircv.SearchEngine.algorithms.MaxScore;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.utilities.TextProcessor;
import it.unipi.mircv.SearchEngine.utilities.Scoring.ObjScore;

public class QueryProcesser {
    
	private int kResults;
	private boolean useStemmingAndStopWordsRemoval;
	private boolean compressionMode;
	private boolean useCache;
	
	private TextProcessor textProcessor;
	private CollectionStatistics collectionStatistics=null;

    private RandomAccessFile fileDocIndex=null;
	private RandomAccessFile fileLexicon=null;
	
	private RandomAccessFile fileDocIds=null;
	private RandomAccessFile fileFreqs = null;
	private RandomAccessFile fileBlocks = null;
	
	private DocumentIndex documentIndex;
    
   
	private DAAT daat;
    private MaxScore maxScore;
    
	
    public QueryProcesser(
    		String pathDocIndex,
    		String pathLexicon,
    		String pathCollectionStatistics,
    		String pathDocIds,
    		String pathFreqs,
    		String pathBlocks,
    		String stopWordsPath,
    		boolean useStemmingAndStopWordsRemoval,
    		boolean compressionMode,
    		boolean useCache,
    		int kResults	
    		) throws Exception {
        
    	
    	if (!checkFilesForQueryProcessing(pathDocIndex,pathLexicon,pathCollectionStatistics,pathDocIds,pathFreqs,pathBlocks,stopWordsPath)) {
    		throw new Exception("File Not Found");
    	}
    	
    	this.documentIndex=new DocumentIndex();
    	
    	this.kResults=kResults;
    	this.useStemmingAndStopWordsRemoval=useStemmingAndStopWordsRemoval;
    	this.compressionMode=compressionMode;
    	this.useCache=useCache;
    	
    	this.textProcessor = new TextProcessor(this.useStemmingAndStopWordsRemoval,stopWordsPath);
        
    	this.fileLexicon= new RandomAccessFile(pathLexicon, "r");
		this.fileDocIds = new RandomAccessFile(pathDocIds, "r");
		this.fileFreqs = new RandomAccessFile(pathFreqs, "r");
		this.fileBlocks= new RandomAccessFile(pathBlocks, "r");
		
		this.fileDocIndex= new RandomAccessFile(pathDocIndex, "r");
    	
		this.collectionStatistics=new CollectionStatistics(pathCollectionStatistics);
		
		if (useCache) {
			long start=System.currentTimeMillis();
			this.documentIndex.initCache(pathDocIndex, this.collectionStatistics.getNumDocuments());
			long end=System.currentTimeMillis();
			System.out.println("Tempo speso per inizializzazione cache: "+(end-start));
		}
			
    	this.daat = new DAAT(this.kResults, this.fileLexicon, this.fileDocIndex, this.collectionStatistics, this.documentIndex, this.fileBlocks, this.fileFreqs, this.fileDocIds, this.compressionMode, this.useCache);
    	this.maxScore = new MaxScore(this.kResults,this.fileLexicon, this.collectionStatistics, this.documentIndex, this.fileBlocks, this.fileFreqs, this.fileDocIds,this.fileDocIndex,this.compressionMode, this.useCache);
    
    }

	/** This method checks if the paths contain effectively a files.
	 * 
	 * @param pathDocIndex
	 * @param pathLexicon
	 * @param pathCollectionStatistics
	 * @param pathDocIds
	 * @param pathFreqs
	 * @param pathBlocks
	 * @param stopWordsPath
	 * @return
	 */
    public boolean checkFilesForQueryProcessing(String pathDocIndex,
    		String pathLexicon,
    		String pathCollectionStatistics,
    		String pathDocIds,
    		String pathFreqs,
    		String pathBlocks,
    		String stopWordsPath) {
        
    	
    	Path documentIndexPath = Paths.get(pathDocIndex);
        Path collectionStatisticsPath = Paths.get(pathCollectionStatistics);
        Path docIdsPath = Paths.get(pathDocIds);
        Path freqPath = Paths.get(pathFreqs);
        Path blockPath= Paths.get(pathBlocks);
        Path lexiconPathFile = Paths.get(pathLexicon);
        Path stopWordFile=Paths.get(stopWordsPath);

        boolean ris=true;
        if (!Files.exists(documentIndexPath)) {
        	System.err.println("Document Index Path not valid: "+documentIndexPath.toString());
        	ris=false;
        }
        
        if (!Files.exists(lexiconPathFile)) {
        	System.err.println("Lexicon Path not valid: "+lexiconPathFile.toString());
        	ris=false;
        }
        
        if (!Files.exists(collectionStatisticsPath)) {
        	System.err.println("Collection Statistics Path not valid: "+collectionStatisticsPath.toString());
        	ris=false;
        }
        
        if (!Files.exists(docIdsPath)) {
        	System.err.println("Doc Ids Path not valid: "+docIdsPath.toString());
        	ris=false;
        }
        
        if (!Files.exists(freqPath)) {
        	System.err.println("Freqs Path not valid: "+freqPath.toString());
        	ris=false;
        }
        
        if (!Files.exists(blockPath)) {
        	System.err.println("Blocks Path not valid: "+blockPath.toString());
        	ris=false;
        }

        if (!Files.exists(stopWordFile)) {
        	System.err.println("StopWord file Path not valid: "+stopWordFile.toString());
        	ris=false;
        }
        
        return ris;
               
    }

    /**
     * This is the generic method to invoke the scoring functionality.
     * @param query
     * @param scoringFunction
     * @param algorithm
     * @param isConjunctive
     * @return
     * @throws IOException
     */
    public List<ObjScore> processQuery(String query, String scoringFunction, String algorithm, boolean isConjunctive) throws IOException {

        //System.out.println("Sono nel query processer con : " + query);
        if (query == null || query.isEmpty())
            return null;
        
        //long start=System.currentTimeMillis();
        
        List<String> tokens = this.textProcessor.tokenizeText(this.textProcessor.processText(query)); // process query
        Set<String> uniqueTokens = new HashSet<>(tokens); // remove duplicate
        
        //long end=System.currentTimeMillis();
        //System.out.println("PreProcess: "+(end-start));
        
        List<ObjScore> result = null;
        if ("daat".equals(algorithm)) {
            result = daat.scoreQuery(scoringFunction, new ArrayList<>(uniqueTokens) , isConjunctive);
        } else {
            result = maxScore.scoreQuery(scoringFunction, new ArrayList<>(uniqueTokens), isConjunctive);
        }
    	
        return result;
    }
    
    
    /**
     * This method care of closing all the file at the begin.
     */
    public void closeFiles() {
    	
    	if (this.fileLexicon!=null) {
    		try {
				this.fileLexicon.close();
			} catch (IOException e) {
			}
    	}
    	
    	if (this.fileDocIds!=null) {
    		try {
				this.fileDocIds.close();
			} catch (IOException e) {
			}
    	}
    	
    	if (this.fileFreqs!=null) {
    		try {
				this.fileFreqs.close();
			} catch (IOException e) {
			}
    	}
    	
    	if (this.fileBlocks!=null) {
    		try {
				this.fileBlocks.close();
			} catch (IOException e) {
			}
    	}
    	
    	if (this.fileDocIndex!=null) {
    		try {
				this.fileDocIndex.close();
			} catch (IOException e) {
			}
    	}
    }

    /** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
    

	public int getkResults() {
		return kResults;
	}


	public boolean isUseStemmingAndStopWordsRemoval() {
		return useStemmingAndStopWordsRemoval;
	}


	public boolean isCompressionMode() {
		return compressionMode;
	}


	public boolean isUseCache() {
		return useCache;
	}


	public TextProcessor getTextProcessor() {
		return textProcessor;
	}


	public CollectionStatistics getCollectionStatistics() {
		return collectionStatistics;
	}


	public RandomAccessFile getFileDocIndex() {
		return fileDocIndex;
	}


	public RandomAccessFile getFileLexicon() {
		return fileLexicon;
	}


	public RandomAccessFile getFileDocIds() {
		return fileDocIds;
	}


	public RandomAccessFile getFileFreqs() {
		return fileFreqs;
	}


	public RandomAccessFile getFileBlocks() {
		return fileBlocks;
	}


	public DocumentIndex getDocumentIndex() {
		return documentIndex;
	}


	public DAAT getDaat() {
		return daat;
	}



    

    
}
