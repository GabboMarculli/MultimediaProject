package Test;

import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.utilities.Scoring;

import static org.junit.jupiter.api.Assertions.*;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;

class ScoringTest {

    // Replace these paths with your actual file paths
    String pathLexicon = "D:\\QueryProcessing\\SearchEngine\\lexicon.bin";
    String pathDocIndex = "D:\\QueryProcessing\\SearchEngine\\document_index.bin";
    CollectionStatistics collectionStatistics = new CollectionStatistics("D:\\QueryProcessing\\SearchEngine\\collection_statistics.txt");

    RandomAccessFile fileDocIndex = new RandomAccessFile(this.pathLexicon, "r");
    RandomAccessFile fileLexicon = new RandomAccessFile(this.pathDocIndex, "r");
    Scoring scoring = new Scoring(fileDocIndex, null,collectionStatistics);

    ScoringTest() throws FileNotFoundException {
    }

    @Test
    void testComputeBM25Term() throws IOException {
        try {
            assertEquals(scoring.computeBM25Term(1, 3, 5), 5.512563481050379);
            assertEquals(scoring.computeBM25Term(673243, 2, 2132), 2.889714707880195);
            assertEquals(scoring.computeBM25Term(67765, 4, 512), 9.316297714597517E-7);

            IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
                scoring.computeBM25Term(-1, 5, 3456);
            });
            assertEquals("docId and termFreq must be positive", exception.getMessage());

            assertEquals(scoring.computeTFIDF(1, 233), 4.579185962677002);
            assertEquals(scoring.computeTFIDF(3, 256), 6.7036222629002);
            assertEquals(scoring.computeTFIDF(2, 311), 5.794503461938128);

            assertEquals(scoring.computeTFIDF(-1, 5), 0);

        } finally {
            fileDocIndex.close();
            fileLexicon.close();
        }
    }
}

