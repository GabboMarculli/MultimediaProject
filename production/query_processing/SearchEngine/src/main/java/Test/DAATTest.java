package Test;


import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.algorithms.DAAT;
import it.unipi.mircv.SearchEngine.handlers.Lexicon;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class DAATTest {
    String pathLexicon = "D:\\QueryProcessing\\SearchEngine\\lexicon.bin";
    CollectionStatistics cs = new CollectionStatistics("D:\\QueryProcessing\\SearchEngine\\collection_statistics.txt");

    RandomAccessFile fileBlocks = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\block_descriptors.bin", "r");
    RandomAccessFile fileFreqs = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\freq.bin", "r");
    RandomAccessFile fileDocIds = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\doc_ids.bin", "r");
    RandomAccessFile fileDocIndex = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\document_index.bin", "r");
    RandomAccessFile filelexicon = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\lexicon.bin", "r");
    Lexicon lexicon = new Lexicon(512, false,filelexicon, cs);

    public DAATTest() throws FileNotFoundException {
    }

    @Test
    void TestDAAT() throws IOException {
        DAAT daat = new DAAT(5, filelexicon,fileDocIndex, cs, null, fileBlocks, fileFreqs, fileDocIds, false, false);

        assertTrue(daat.getPostingReaderList().isEmpty());
        assertTrue(daat.getTopKdocuments().isEmpty());

        List<String> stringList = new ArrayList<>();
        stringList.add("who");
        stringList.add("is");
        stringList.add("aziz");
        stringList.add("hashim");

        daat.initializePostingLists(stringList);
        assertFalse(daat.getPostingReaderList().isEmpty());

        List<Integer> documentIds = new ArrayList<>();
        for (int i = 0; i < daat.getPostingReaderList().size(); i++)
            if (daat.getPostingReaderList().get(i).hasNext())
                documentIds.add(daat.getPostingReaderList().get(i).getCurrentPosting().getDocId());
        Collections.sort(documentIds);

        int indexOfMin = daat.minDoc().get(0);
        int minInCollection = documentIds.get(0);
        assertEquals(daat.getPostingReaderList().get(indexOfMin).getCurrentPosting().getDocId(), minInCollection);

        for (int i = 0; i < 100; i++) {
            // Simulate different document scores and IDs for testing
            double randomScore = Math.random() * 100;
            int randomDocId = i;

            daat.updateHeap(randomDocId, randomScore);

            // Check conditions after each update
            assert daat.getTopKdocuments().size() <= daat.getK() : "Heap size exceeds k";
            if (daat.getTopKdocuments().size() == daat.getK()) {
                double smallestScore = daat.getTopKdocuments().peek().getScore();
                assert daat.getTopKdocuments().stream().allMatch(objScore -> objScore.getScore() >= smallestScore)
                        : "Removed element has a smaller score than the current smallest element";
            }
        }
    }
}
