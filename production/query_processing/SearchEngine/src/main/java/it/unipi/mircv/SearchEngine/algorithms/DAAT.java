package it.unipi.mircv.SearchEngine.algorithms;

import java.io.*;
import java.util.*;
import java.util.stream.Collectors;

import it.unipi.mircv.SearchEngine.handlers.DocumentIndex;
import it.unipi.mircv.SearchEngine.handlers.Lexicon;
import it.unipi.mircv.SearchEngine.handlers.PostingListHandler;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.structures.LexiconRow;
import it.unipi.mircv.SearchEngine.utilities.Scoring;
import it.unipi.mircv.SearchEngine.utilities.Scoring.ObjScore;

/**
 * This class represents a Query Processing technique to determine the most
 * relevant documents for a specific query.
 * 
 * @author Gabriele and Davide
 */
public class DAAT {

	// The maximum number of top scored documents.
	private int k;

	private Lexicon lexicon;
	private Scoring scorer;

	private RandomAccessFile fileDocIds;
	private RandomAccessFile fileBlocks;
	private RandomAccessFile fileFreqs;

	private boolean compressionMode;

	// For each different term in the query there is a posting list handler related
	private List<PostingListHandler> postingReaderList = new ArrayList<PostingListHandler>();

	// The container of the result of the top-k scored documents.
	private PriorityQueue<ObjScore> topKdocuments;

	/**
	 * Constructor method:
	 * 
	 * @param k               - the maximum number of the top document to be
	 *                        returned
	 * @param filelexicon     - the file related to lexicon
	 * @param fileDocIndex    - the file related to documentIndex
	 * @param cs              - the Collection Statistic information
	 * @param documentIndex 
	 * @param fileBlocks      - the file related to BlockDescriptors
	 * @param fileFreqs       - the file related to Frequencies
	 * @param fileDocIds      - the file related to DocIds
	 * @param compressionMode - if using or not the decompression for interpreting
	 * @param useCache		  - if using cache or not
	 *                        the posting list
	 * @throws IOException
	 */
	public DAAT(int k, RandomAccessFile filelexicon, RandomAccessFile fileDocIndex, CollectionStatistics cs,
			DocumentIndex documentIndex, RandomAccessFile fileBlocks, RandomAccessFile fileFreqs, RandomAccessFile fileDocIds,
			boolean compressionMode,boolean useCache) throws IOException {

		this.lexicon = new Lexicon(512,useCache, filelexicon, cs);
		this.scorer = new Scoring(fileDocIndex, useCache?documentIndex:null, cs);
		this.compressionMode = compressionMode;

		this.fileDocIds = fileDocIds;
		this.fileFreqs = fileFreqs;
		this.fileBlocks = fileBlocks;

		this.k = Math.max(k, 1);

		this.topKdocuments = new PriorityQueue<ObjScore>(this.k, Comparator.comparingDouble(ObjScore::getScore));
		
	}

	/**
	 * This method resets the posting list reader and the top-k documents in the
	 * results.
	 */
	public void resetLists() {
		// This list will contain pointers to the posting lists of all terms
		this.postingReaderList.clear();
		this.topKdocuments.clear();
	}

	/**
	 * This method aims to initialize the postingReaderList for each term in the
	 * query.
	 * 
	 * @param tokens
	 * @throws IOException
	 */
	public void initializePostingLists(List<String> tokens) throws IOException {

		for (String token : tokens) {

			// First a binary search is done to find the term information in the lexicon
			LexiconRow term_lexicon_row = lexicon.getLexiconRowTerm(token);

			if (term_lexicon_row != null) {

				PostingListHandler reader = new PostingListHandler(term_lexicon_row, this.compressionMode,
						this.fileDocIds, this.fileFreqs, this.fileBlocks);
				if (reader.hasNext())
					reader.next();
				
				postingReaderList.add(reader);
			}
		}
	}

	/**
	 * Function to find the indexes of the elements in the postingReaderList whose
	 * current posting element docId is minimum.
	 * 
	 * @return a list of position in which the min docId is present.
	 */
	public List<Integer> minDoc() {

		List<Integer> indexesOfMinDoc = new ArrayList<Integer>();

		int minDocId = -1;
		for (Iterator<PostingListHandler> iterator = this.postingReaderList.iterator(); iterator.hasNext();) {
			PostingListHandler reader = (PostingListHandler) iterator.next();

			if (reader.getCurrentPosting() != null) {
				if (minDocId == -1) {
					minDocId = reader.getCurrentPosting().getDocId();
				}
				if (reader.getCurrentPosting().getDocId() < minDocId) {
					minDocId = reader.getCurrentPosting().getDocId();
				}
			}
		}
		int i = 0;
		for (Iterator<PostingListHandler> iterator = this.postingReaderList.iterator(); iterator.hasNext(); i++) {
			PostingListHandler reader = (PostingListHandler) iterator.next();
			if (reader.getCurrentPosting() != null && reader.getCurrentPosting().getDocId() == minDocId) {
				indexesOfMinDoc.add(i);
			}
		}

		return indexesOfMinDoc;
	}

	/**
	 * Function to update topKdocuments structure: the current top-k best scored
	 * documents.
	 * 
	 * @param choice_function
	 * @param docToProcess
	 * @param docScore
	 * @throws IOException
	 */
	public void updateHeap(int docToProcess, double docScore) throws IOException {

		if (this.topKdocuments.size() == this.k) {
			if (docScore > this.topKdocuments.peek().getScore()) {
				this.topKdocuments.poll();
				this.topKdocuments.offer(new ObjScore(docScore, docToProcess,null));
			}
		} else {
			this.topKdocuments.offer(new ObjScore(docScore, docToProcess,null));
		}

	}

	/**
	 * This function aims to determine what are the top-k documents according to a specific function criteria.
	 * It also gives the possibility to execute a conjunctive/disjunctive search.
	 *  
	 * @param choiceFunction - The criteria to score a document (indicate bm25 or tfidf)
	 * @param tokens - The list of tokens of words to be considered during the scoring
	 * @param isConjunctive - The value to execute conjunctive search(true) otherwise disjunctive(false)
	 * @return a list of ObjScore in descending order of ObjScore.score
	 * @throws IOException
	 */
	public List<ObjScore> scoreQuery(String choiceFunction, List<String> tokens, boolean isConjunctive)
			throws IOException {

		this.resetLists();
		this.initializePostingLists(tokens);
//		int sommaTempi=0;
//		int sommaTempiFor=0;
//		int sommaTempiHeap=0;
		while (true) {
			
	
			List<Integer> indexesOfMinDocIds = minDoc();

			if (indexesOfMinDocIds != null && indexesOfMinDocIds.size() > 0) {

				if (isConjunctive) {
					// If the currentMinDoc is not present in all the token terms posting list, it
					// should be discarded.
					if (indexesOfMinDocIds.size() != tokens.size()) {
						for (Iterator<Integer> iterator = indexesOfMinDocIds.iterator(); iterator.hasNext();) {
							Integer index = (Integer) iterator.next();
							if (this.postingReaderList.get(index).hasNext()) {
								this.postingReaderList.get(index).next();
							}
						}
						continue;
					}
				}
				// Here I have the current minDocId and it is the same for all the indexes in indexesOfMinDocIds.
				int minDoc = this.postingReaderList.get(indexesOfMinDocIds.get(0)).getCurrentPosting().getDocId();
				
				//long start_1=System.currentTimeMillis();
				
				// Agglomerative score variable.
				double docScore = 0;
				for (Iterator<Integer> iterator = indexesOfMinDocIds.iterator(); iterator.hasNext();) {
					Integer index = (Integer) iterator.next();
					//long start=System.currentTimeMillis();
					docScore += scorer.chooseScoringFunction(choiceFunction, minDoc,
							this.postingReaderList.get(index).getCurrentPosting().getFrequency(),
							this.postingReaderList.get(index).getLexiconElem().getDft());
					//long end=System.currentTimeMillis();
					//sommaTempi+=(end-start);
					
					if (this.postingReaderList.get(index).hasNext()) {
						this.postingReaderList.get(index).next();
					} else {
						// System.out.println("Finito di scorrere posting di :"+this.postingReaderList.get(index).getLexiconElem().getTerm()+ " "+this.postingReaderList.get(index).getLexiconElem().getDft());
					}
				}
//				long end_1=System.currentTimeMillis();
//				sommaTempiFor+=(end_1-start_1);
				
				//long start_2=System.currentTimeMillis();
				updateHeap(minDoc, docScore);
				//long ends_2=System.currentTimeMillis();
				//sommaTempiHeap+=(ends_2-start_2);
				
			} else {
				// End condition: all the posting lists are read.
				break;
			}

		}
	
//		System.out.println("Somma tempi FOR: "+sommaTempiFor);
//		System.out.println("Somma tempi HEAP:"+sommaTempiHeap);
//		
//		
//		System.out.println("Somma tempi scoring (parte di FOR): "+sommaTempi);
		
		
		//System.out.println("Somma tempi HEAP: "+sommaTempiHeap);
		
		
		//scorer.somma_tempi=0;
		return topKdocuments.stream().sorted(Comparator.comparingDouble(ObjScore::getScore).reversed())
				.collect(Collectors.toList());
	}

	
	/** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
	
	public int getK() {
		return k;
	}

	public Lexicon getLexicon() {
		return lexicon;
	}

	public Scoring getScorer() {
		return scorer;
	}

	public RandomAccessFile getFileDocIds() {
		return fileDocIds;
	}

	public RandomAccessFile getFileBlocks() {
		return fileBlocks;
	}

	public RandomAccessFile getFileFreqs() {
		return fileFreqs;
	}

	public boolean isCompressionMode() {
		return compressionMode;
	}

	public List<PostingListHandler> getPostingReaderList() {
		return postingReaderList;
	}

	public PriorityQueue<ObjScore> getTopKdocuments() {
		return topKdocuments;
	}

}
