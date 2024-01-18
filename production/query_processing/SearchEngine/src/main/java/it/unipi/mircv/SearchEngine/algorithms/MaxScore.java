package it.unipi.mircv.SearchEngine.algorithms;


import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.*;
import java.util.stream.Collectors;

import it.unipi.mircv.SearchEngine.handlers.DocumentIndex;
import it.unipi.mircv.SearchEngine.handlers.Lexicon;
import it.unipi.mircv.SearchEngine.handlers.PostingListHandler;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.structures.LexiconRow;
import it.unipi.mircv.SearchEngine.structures.Posting;
import it.unipi.mircv.SearchEngine.utilities.Scoring;
import it.unipi.mircv.SearchEngine.utilities.Scoring.ObjScore;

/**
 * The MaxScore class is responsible for scoring and retrieving top-k documents based on the given scoring function and tokens.
 * 
 * @author Gabriele
 *
 */
public class MaxScore {

    private Scoring scorer;

    private Lexicon lexicon;
    private boolean compressionMode;

    // metti privato, è pubblico per debug
    private ArrayList<PostingListHandler> postingReaders = new ArrayList<>();

    private PriorityQueue<ObjScore> topKdocuments;

    private ArrayList<Float> upperBound;

    private CollectionStatistics collectionStatistics;

    private RandomAccessFile fileDocIds;

    private RandomAccessFile fileBlocks;

    private RandomAccessFile fileFreqs;

    private int k;

    /**
     * Constructor for the MaxScore class.
     *
     * @param filelexicon     - the file related to lexicon
	 * @param fileDocIndex    - the file related to documentIndex
	 * @param cs              - the Collection Statistic information
	 * @param documentIndex 
	 * @param fileBlocks      - the file related to BlockDescriptors
	 * @param fileFreqs       - the file related to Frequencies
	 * @param fileDocIds      - the file related to DocIds
	 * @param compressionMode - if using or not the decompression for interpreting
	 * @param useCache		  - if using cache or not
     * @throws IOException - if an I/O error occurs
     */
    public MaxScore(int k, RandomAccessFile filelexicon, CollectionStatistics cs, DocumentIndex documentIndex,RandomAccessFile fileBlocks, RandomAccessFile fileFreqs, RandomAccessFile fileDocIds, RandomAccessFile fileDocIndex,boolean compressionMode,boolean useCache) throws IOException {

    	this.collectionStatistics = cs;
    	this.lexicon = new Lexicon(512,useCache, filelexicon, this.collectionStatistics);
       
        this.scorer = new Scoring(fileDocIndex ,documentIndex, this.collectionStatistics);
        this.compressionMode = compressionMode;

        this.fileDocIds = fileDocIds;
        this.fileFreqs =fileFreqs;
        this.fileBlocks= fileBlocks;

        this.k = Math.max(k, 1);

        this.topKdocuments = new PriorityQueue<ObjScore>(this.k, Comparator.comparingDouble(ObjScore::getScore));
    }


    /**
     * Initializes the upper bound for scoring based on the scoring function.
     *
     * @param scoringFunction - the scoring function to use (e.g., "tfidf" or "bm25")
     * @param numberOfTokens  - the number of tokens
     */
    public void initializeUpperBound(String scoringFunction, int numberOfTokens)  {
        // Determine the actual number of tokens to process based on the minimum between the specified number and the size of postingReaders.
        int condition = Math.min(numberOfTokens, this.postingReaders.size());

        // Initialize the upperBound ArrayList with the determined condition.
        this.upperBound = new ArrayList<>(condition);
        // Add the initial value to upperBound based on the scoring function of the first postingReader.
        this.upperBound.add(0 , (scoringFunction.equals("tfidf") ?
                this.postingReaders.get(0).getLexiconElem().getMaxTFIDF() :
                this.postingReaders.get(0).getLexiconElem().getMaxBM25()));

        // Iterate from the second postingReader onwards to compute and add cumulative values to upperBound.
        for (int i = 1; i < condition; i++){
            if (scoringFunction.equals("tfidf"))
                // For tfidf scoring, add the cumulative value of MaxTFIDF to the previous value in upperBound.
                this.upperBound.add(this.postingReaders.get(i).getLexiconElem().getMaxTFIDF() + upperBound.get(i-1));
            else
                // For bm25 scoring, add the cumulative value of MaxBM25 to the previous value in upperBound.
                this.upperBound.add(this.postingReaders.get(i).getLexiconElem().getMaxBM25() + upperBound.get(i-1));
        }
    }

    /**
     * Initializes and sorts posting lists based on term upper bound.
     *
     * @param tokens          - the list of tokens to process
     * @param scoringFunction - the scoring function to use (e.g., "tfidf" or "bm25")
     * @param numberOfTokens  - the number of tokens in query
     * @throws IOException    - if an I/O error occurs
     */
    public void initializeAndSortPostingLists(List<String> tokens, String scoringFunction, int numberOfTokens) throws IOException {
        // Create a priority queue to store ObjScore objects with scores for sorting.
        PriorityQueue<ObjScore> priorityQueue = new PriorityQueue<>(numberOfTokens, Comparator.comparingDouble(ObjScore::getScore));

        // Iterate through each token to process its corresponding posting list.
        for (String token : tokens) {
            // Retrieve the LexiconRow for the current token from the cache.
            LexiconRow termLexiconRow = this.lexicon.getLexiconRowTerm(token);

            // Check if the token exists in the lexicon.
            if (termLexiconRow != null) {
                // Create a PostingListHandler for the current token's posting list.
                PostingListHandler reader = new PostingListHandler(termLexiconRow, this.compressionMode, this.fileDocIds, this.fileFreqs, this.fileBlocks);
                reader.next();

                // Determine the score based on the scoring function for the current token.
                double score = (scoringFunction.equals("bm25")) ?
                        reader.getLexiconElem().getMaxBM25() :
                        reader.getLexiconElem().getMaxTFIDF();

                // Create an ObjScore object with the computed score and the PostingListHandler.
                priorityQueue.offer(new ObjScore(score,0,reader));
            }
        }

        // Transfer posting readers from the priority queue to the postingReaders list, sorted by scores.
        while (!priorityQueue.isEmpty())
            this.postingReaders.add((PostingListHandler) priorityQueue.poll().getPayload());
    }

    /**
     * Initializes the structure by clearing topKdocuments, resetting postingReaders, and initializing the upper bound.
     *
     * @param tokens          - the list of tokens to process
     * @param scoringFunction - the scoring function to use (e.g., "tfidf" or "bm25")
     * @param numberOfTokens  - the number of tokens
     * @throws IOException    - if an I/O error occurs
     */
    public void initializeStructure(List<String> tokens, String scoringFunction, int numberOfTokens) throws IOException {
        this.topKdocuments.clear();
        this.postingReaders = new ArrayList<>(); // reset postings list readers
        this.initializeAndSortPostingLists(tokens, scoringFunction, numberOfTokens);
        this.initializeUpperBound(scoringFunction, tokens.size());
    }

    /**
     * Determines the document to process based on conjunction and pivot.
     *
     * @param isConjunctive - flag indicating whether conjunction is used
     * @param pivot         - the pivot index
     * @return the PostingListHandler for the document to process
     */
    public PostingListHandler docToProcess( boolean isConjunctive, int pivot) {
        // insert in this list only hanlder with non null "hasNext"
        List<PostingListHandler> validDocsEssential = postingReaders.subList(pivot, postingReaders.size())
                .stream()
                .filter(PostingListHandler::hasNext)
                .collect(Collectors.toList());

        if (validDocsEssential.isEmpty()) // if no hanlder was found, return
            return null;

        if (isConjunctive && validDocsEssential.size() != postingReaders.size() - pivot) {
            return null;
        }

        return isConjunctive ?
                validDocsEssential.stream().max(Comparator.comparingInt(docTuple -> docTuple.getCurrentPosting().getDocId())).orElse(null) :
                validDocsEssential.stream().min(Comparator.comparingInt(docTuple -> docTuple.getCurrentPosting().getDocId())).orElse(null);
    }

    /**
     * Calculates the score of non essential posting lists.
     *
     * @param pivot          - the pivot index
     * @param currThreshold  - the current threshold
     * @param current        - the current document ID
     * @param scoringFunction - the scoring function to use (e.g., "tfidf" or "bm25")
     * @return the calculated non-essential score
     * @throws IOException   - if an I/O error occurs
     */
    public double nonEssentialScore(int pivot, double currThreshold, int current, String scoringFunction, double essentialScore) throws IOException {
        // CONTROLLA DIFFERENZA PERFORMANCE SE INIZIALIZZO QUI SOTTO PARTIALSCORE = 0 OPPURE PARTIALSCORE = ESSENTIALSCORE
        double partialScore = 0;

        for(int i = pivot-1; i>=0 ; i--)
        {
            // if the sum of partial score and upper bound of the term is under the threshold, not process other posting list
            if(partialScore + this.upperBound.get(i) < currThreshold)
                break;

            PostingListHandler reader = this.postingReaders.get(i);
            reader.nextGEQ(current); // search for docId to process

            Posting posting = reader.getCurrentPosting();
            if(posting != null && posting.getDocId() == current) // if the docid is present in posting list, compute its score
                partialScore += this.scorer.chooseScoringFunction(scoringFunction, current, posting.getFrequency(), reader.getLexiconElem().getDft());
        }

        return partialScore;
    }

    /**
     * Updates the heap with a new entry. If the minheap is full, update threshold with minimum value in the queue.
     *
     * @param score         - the new score to update in the heap
     * @param currThreshold - the current threshold
     * @param current       - the current document ID to process
     * @return the updated current threshold after the heap update
     */
    public double updateHeap(double score, double currThreshold, int current){
        topKdocuments.offer(new ObjScore(score, current,null));

        if(topKdocuments.size() > k) {
            topKdocuments.poll(); // Remove the smallest element (element with the lowest score)
            return topKdocuments.peek().getScore(); // Update currThreshold to the new lowest score in the topKdocuments
        }

        return currThreshold;
    }

    /**
     * Scores the query based on the given scoring function.
     *
     * @param scoringFunction - the scoring function to use (e.g., "tfidf" or "bm25")
     * @param tokens          - the list of tokens to process
     * @param isConjunctive   - flag indicating whether conjunction is used
     * @return a list of ObjScore representing the top-k scored documents
     * @throws IOException    - if an I/O error occurs
     */
    public List<ObjScore> scoreQuery(String scoringFunction, List<String> tokens, boolean isConjunctive) throws IOException {
        int numberOfTokens = tokens.size(), pivot = 0; // pivot is the index of the first essential postings list

        this.initializeStructure(tokens, scoringFunction, numberOfTokens); // initialize structure used in the algorithm
        if (postingReaders.isEmpty())
            return Collections.emptyList();

        double currThreshold = 0; // initial threshold

        // Initialization of current threshold to enter the MinHeap of the results
        PostingListHandler postingListHandler = this.docToProcess(isConjunctive, pivot);
        int current = (postingListHandler == null) ? -1 : postingListHandler.getCurrentPosting().getDocId(); // first docId to process
        if (current == -1)
            return Collections.emptyList();

        int condition = Math.min(numberOfTokens, this.postingReaders.size()); // number of valid term to process

        while (pivot < condition && current != Integer.MAX_VALUE) {
                double score = 0;
                int next = Integer.MAX_VALUE; // next docid to process

                // process essential posting lists
                for (int i = pivot; i < this.postingReaders.size(); i++){
                    PostingListHandler reader = this.postingReaders.get(i);
                    if (reader.hasNext()) {
                        Posting posting = reader.getCurrentPosting();
                        if (posting != null ) {
                            int docId = posting.getDocId();
                            if(docId == current) {
                                score += this.scorer.chooseScoringFunction(scoringFunction, current, posting.getFrequency(), reader.getLexiconElem().getDft());
                                reader.next();
                            }

                            if(docId < next) // search for the minimum docid among essential posting list (the next to process)
                                next = docId;
                        }
                    }
                }

                // add the score of non essential postings lists
                score += this.nonEssentialScore(pivot, currThreshold, current, scoringFunction, score);

                // update the threshold
                currThreshold = this.updateHeap(score, currThreshold, current);

                // update pivot
                while(pivot < condition && this.upperBound.get(pivot) < currThreshold)
                    pivot++;

                current = next;
        }

        // sort from highest score to lowest and return <score, docid>
        List<ObjScore> sortedList = new ArrayList<>(topKdocuments);
        sortedList.sort(Comparator.comparingDouble(ObjScore::getScore).reversed());
        return sortedList;
    }

    public PriorityQueue<ObjScore> getTopKdocuments() {
        return topKdocuments;
    }

    public int getK() {
        return k;
    }

    public ArrayList<PostingListHandler> getPostingReaders() {
        return postingReaders;
    }

    public void clearPostingReaders(){
        this.postingReaders.clear();
    }


	public Scoring getScorer() {
		return scorer;
	}


	public Lexicon getLexicon() {
		return lexicon;
	}


	public boolean isCompressionMode() {
		return compressionMode;
	}


	public ArrayList<Float> getUpperBound() {
		return upperBound;
	}


	public CollectionStatistics getCollectionStatistics() {
		return collectionStatistics;
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
    
    
    
    
}



