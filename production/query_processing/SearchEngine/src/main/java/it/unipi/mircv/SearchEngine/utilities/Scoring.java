package it.unipi.mircv.SearchEngine.utilities;



import java.io.IOException;
import java.io.RandomAccessFile;

import it.unipi.mircv.SearchEngine.handlers.DocumentIndex;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.structures.DocumentIndexRow;


/**
 * Todo
 * 
 * @author Gabriele
 *
 */
public class Scoring {
	
    private final double k1 = 1.6;
    private final double b = 0.75;
	
    private DocumentIndexRow docIndexRow;

    private CollectionStatistics collectionStatistics;
    private RandomAccessFile fileDocIndex;
    
    private DocumentIndex documentIndex;
    
    //public long somma_tempi=0;
    
    private float avgDL;

    public Scoring( RandomAccessFile fileDocIndex,DocumentIndex documentIndex, CollectionStatistics collectionStatistics) {
        
    	this.collectionStatistics = collectionStatistics;
        this.fileDocIndex=fileDocIndex;
        
        // Precomputed
        this.avgDL = this.collectionStatistics.getAverageDocumentLength();
        
        this.documentIndex=documentIndex;
        
        //Used as temp variable
        this.docIndexRow=new DocumentIndexRow(0, "0", "");
    }

    public double chooseScoringFunction(String choice, int docId, int termFreq, int dft) throws IOException {
        return (choice.equals("bm25")) ?  computeBM25Term(docId, termFreq, dft) : computeTFIDF(termFreq, dft);
    }

    
    public double computeBM25Term(int docId, int termFreq, int dft) throws IOException {
        if (docId < 0 || termFreq <= 0) {
            throw new IllegalArgumentException("docId and termFreq must be positive");
        }
       
        float idf = computeIDFT(dft);
        double logTF = (1 + Math.log10(termFreq));

        //long start=System.currentTimeMillis();
        
        int docLen=0;
        // If cache is enabled, look in memory to see the document length
        if (this.documentIndex!=null && this.documentIndex.getCacheDocumentIndex().get((long) docId)!=null) {
        	docLen=this.documentIndex.getCacheDocumentIndex().get((long) docId);
        }
        else {
        	docIndexRow.readDocIndexRowOnDisk(fileDocIndex, docId * DocumentIndexRow.SIZE_DOC_INDEX_ROW);
        	docLen=docIndexRow.getDocumentLength();
        }
        
       
        //long end=System.currentTimeMillis();
        double ris=(idf * logTF) / (logTF + k1 * ((1 - b) + b * (docLen / avgDL)));
        
        //somma_tempi+=(end-start);
        
        return ris;
    }

    private float computeIDFT(int dft) {
        if (dft <= 0) {
            throw new IllegalArgumentException("Invalid parameters.");
        }
        return (float) Math.log10((double) collectionStatistics.getNumDocuments() / dft);
    }

    
    public double computeTFIDF(int tf, int dft) {
        if (tf <= 0) {
            return 0;
        }
        return (1 + Math.log10(tf)) * computeIDFT(dft);
    }
 
    /**
     * This class is used as temp obj elem of Priority Queue, in order to handle the score obtained by each document.
     * The payload attribute is used during max-score to keep the posting list
     * @author Davide and Gabriele
     *
     */
    public static class ObjScore implements Comparable<ObjScore>{
		
		private double score;
		private int docId;
		
		//Used only in max-score
		private Object payload;
		
		public ObjScore(double score, int docId, Object payload) {
			super();
			this.score = score;
			this.docId = docId;
			this.payload=payload;
		}
		
		public double getScore() {
			return score;
		}
		public void setScore(double score) {
			this.score = score;
		}
		public int getDocId() {
			return docId;
		}
		public void setDocId(int docId) {
			this.docId = docId;
		}
		@Override
		public int compareTo(ObjScore o) {
			return Double.compare(this.score, o.score);
		}
		
		

		public Object getPayload() {
			return payload;
		}

		public void setPayload(Object payload) {
			this.payload = payload;
		}

		@Override
		public String toString() {
			return "ObjScore [score=" + score + ", docId=" + docId+ "]";
		}
		
	}
    
}




