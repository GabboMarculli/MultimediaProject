package Test;

import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.handlers.Lexicon;
import it.unipi.mircv.SearchEngine.handlers.PostingListHandler;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.structures.LexiconRow;
import it.unipi.mircv.SearchEngine.structures.Posting;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.Iterator;
import java.util.List;

class PostingListHandlerTest {

    @Test
    void testPostingListHandler() throws IOException {
        String pathLexicon="D:\\QueryProcessing\\SearchEngine\\lexicon.bin";
        String docIdsFilePath= "D:\\QueryProcessing\\SearchEngine\\doc_ids.bin";
        String freqsFilePath="D:\\QueryProcessing\\SearchEngine\\freq.bin";
        String blocksFilePath="D:\\QueryProcessing\\SearchEngine\\block_descriptors.bin";

        RandomAccessFile fileDocIds = new RandomAccessFile(docIdsFilePath, "r");
        RandomAccessFile fileFreqs = new RandomAccessFile(freqsFilePath, "r");
        RandomAccessFile fileBlocks = new RandomAccessFile(blocksFilePath, "r");
        RandomAccessFile fileLexicon = new RandomAccessFile(pathLexicon, "r");

        Lexicon lex = new Lexicon(512, false,fileLexicon, new CollectionStatistics("D:\\QueryProcessing\\SearchEngine\\collection_statistics.txt"));
        LexiconRow lexiconRow = lex.getLexiconRowTerm("definition");

        try {
            // Initialize PostingListHandler
            PostingListHandler postingListHandler = new PostingListHandler(
                    lexiconRow,
                    true, // Adjust this based on your compression mode
                    fileDocIds,
                    fileFreqs,
                    fileBlocks
            );

            // Test hasNext and next methods
            assertTrue(postingListHandler.hasNext());
            assertNotNull(postingListHandler.next());

            int initialBlockIndex = postingListHandler.getBlockIndex();

            // Test nextGEQ method (you may need to adjust this based on your actual data)
            Posting posting = postingListHandler.nextGEQ(450000);
            assertNotNull(posting);
            assertTrue(posting.getDocId() >= 450000);

            // Test iterator functionality
            Iterator<Posting> iterator = postingListHandler;
            assertTrue(iterator.hasNext());
            assertNotNull(iterator.next());

            // Test block switching
            assertTrue(postingListHandler.hasNext());
            assertTrue(postingListHandler.getBlockIndex() > initialBlockIndex);

            assertNull(postingListHandler.nextGEQ(-1), "nextGEQ should return null for docId < first posting's docId");

            // Scenario 2: Test with docId equal to the first posting's docId
            posting = postingListHandler.nextGEQ(posting.getDocId());
            assertNotNull(posting, "nextGEQ should return a posting for docId = first posting's docId");
            assertEquals(posting.getDocId(), postingListHandler.getCurrentPosting().getDocId(),
                    "getCurrentPosting should return the correct posting after nextGEQ");

            // Scenario 3: Test with docId between two postings
            int midDocId = (posting.getDocId() + postingListHandler.getCurrentBlock().getMaxDocId()) / 2;
            posting = postingListHandler.nextGEQ(midDocId);
            assertNotNull(posting, "nextGEQ should return a posting for docId between two postings");
            assertTrue(posting.getDocId() >= midDocId,
                    "The returned posting should have docId greater than or equal to the given docId");

            // Scenario 4: Test with docId greater than the last posting's docId
            while(postingListHandler.hasNext())
                postingListHandler.next();

            int lastDocId = postingListHandler.getCurrentBlock().getMaxDocId() + 1;
            posting = postingListHandler.nextGEQ(lastDocId);
            assertNull(posting, "nextGEQ should return null for docId > last posting's docId");

        } finally {
            // Close the RandomAccessFile instances in a finally block
            fileDocIds.close();
            fileFreqs.close();
            fileBlocks.close();
        }
    }
}

