package Test;


import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.algorithms.MaxScore;
import it.unipi.mircv.SearchEngine.handlers.Lexicon;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.utilities.Scoring.ObjScore;

import static org.junit.jupiter.api.Assertions.*;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.*;

public class MaxScoreTest {

    String pathLexicon = "D:\\QueryProcessing\\SearchEngine\\lexicon.bin";
    CollectionStatistics cs = new CollectionStatistics("D:\\QueryProcessing\\SearchEngine\\collection_statistics.txt");

    RandomAccessFile fileBlocks = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\block_descriptors.bin", "r");
    RandomAccessFile fileFreqs = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\freq.bin", "r");
    RandomAccessFile fileDocIds = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\doc_ids.bin", "r");
    RandomAccessFile fileDocIndex = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\document_index.bin", "r");
    RandomAccessFile filelexicon = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\lexicon.bin", "r");
    Lexicon lexicon = new Lexicon(512,false, filelexicon, cs);

    public MaxScoreTest() throws FileNotFoundException {
    }

    @Test
    void testScoreQuery() throws IOException {
        try {
            MaxScore maxScore = new MaxScore(5, filelexicon, cs,null, fileBlocks, fileFreqs, fileDocIds, fileDocIndex,false,false);
           
            assertTrue(maxScore.getPostingReaders().isEmpty());
            assertTrue(maxScore.getTopKdocuments().isEmpty());

            // #################### test initializeAndSortPostingLists
            List<String> stringList = new ArrayList<>();
            stringList.add("who");
            stringList.add("is");
            stringList.add("aziz");
            stringList.add("hashim");

            maxScore.initializeAndSortPostingLists(stringList, "tfidf", 4);

            List<Float> upperBound = new ArrayList<>();
            upperBound.add(lexicon.getLexiconRowTerm("who").getMaxTFIDF());
            upperBound.add(lexicon.getLexiconRowTerm("is").getMaxTFIDF());
            upperBound.add(lexicon.getLexiconRowTerm("aziz").getMaxTFIDF());
            upperBound.add(lexicon.getLexiconRowTerm("hashim").getMaxTFIDF());
            Collections.sort(upperBound);

            for (int i = 0; i < upperBound.size(); i++)
                assertEquals(upperBound.get(i), maxScore.getPostingReaders().get(i).getLexiconElem().getMaxTFIDF());

            stringList = new ArrayList<>();
            stringList.add("who");
            stringList.add("was");
            stringList.add("the");
            stringList.add("highest");
            stringList.add("career");
            stringList.add("passer");
            stringList.add("rating");
            stringList.add("in");
            stringList.add("the");
            stringList.add("nfl");

            maxScore.clearPostingReaders();
            maxScore.initializeAndSortPostingLists(stringList, "bm25", stringList.size());

            upperBound = new ArrayList<>();
            upperBound.add(lexicon.getLexiconRowTerm("who").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("was").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("the").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("highest").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("career").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("passer").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("rating").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("in").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("the").getMaxBM25());
            upperBound.add(lexicon.getLexiconRowTerm("nfl").getMaxBM25());
            Collections.sort(upperBound);

            for (int i = 0; i < upperBound.size(); i++)
                assertEquals(upperBound.get(i), maxScore.getPostingReaders().get(i).getLexiconElem().getMaxBM25());

            // ################# test for doc to process
            List<Integer> documentIds = new ArrayList<>();
            for (int i = 0; i < maxScore.getPostingReaders().size(); i++)
                if (maxScore.getPostingReaders().get(i).hasNext())
                    documentIds.add(maxScore.getPostingReaders().get(i).getCurrentPosting().getDocId());
            Collections.sort(documentIds);

            assertEquals(maxScore.docToProcess(false, 0).getCurrentPosting().getDocId(), documentIds.get(0)); // min docid
            assertEquals(maxScore.docToProcess(true, 0).getCurrentPosting().getDocId(), documentIds.get(documentIds.size() - 1)); // maxdocid

            // ############## test update heap
            for (int i = 100; i >= 1; i--) {
                double score = i; // You can use your own scoring logic here
                int current = i; // Replace with actual docId
                double currThreshold = maxScore.updateHeap(score, i, current);

                // Check that the size of topKdocuments remains at most k
                assertTrue(maxScore.getTopKdocuments().size() <= maxScore.getK());

                boolean order = true;
                for (ObjScore objScore : maxScore.getTopKdocuments())
                    if (objScore.getScore() < currThreshold) {
                        order = false;

                        // Check that the smallest element in topKdocuments is smaller than others
                        assertTrue(order);
                    }
            }
        }catch(IOException e){
            fail("Exception during test: " + e.getMessage());
        }
    }
}

