package Test;

import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.structures.LexiconRow;

import static org.junit.jupiter.api.Assertions.*;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;

class LexiconRowTest {
    RandomAccessFile lexiconFile = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\lexicon.bin", "r");

    LexiconRowTest() throws FileNotFoundException {
    }

    @Test
    void testReadLexiconRowOnDiskFromOpenedFile() throws IOException {
        LexiconRow readRow = new LexiconRow();
        readRow.readLexiconRowOnDiskFromOpenedFile(lexiconFile, 0); // "0" term in lexicon, 74 x 277297

        // Compare the original and read LexiconRow
        assertEquals("0", readRow.getTerm().trim());
        assertEquals(194228, readRow.getDft());
        assertEquals(1.658229947090149, readRow.getMaxTFIDF(), 0.01); // Add delta for floating-point comparison
        assertEquals(18.830875396728516, readRow.getMaxBM25(), 0.01); // Add delta for floating-point comparison
        assertEquals(0, readRow.getBlockOffset());
        assertEquals(63, readRow.getNumBlocks());
    }

}
